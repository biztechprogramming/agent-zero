from python.helpers.tool import Tool, Response
from python.helpers import files
from python.helpers.print_style import PrintStyle
import subprocess
import os
import json
import time
import asyncio
from datetime import datetime, timedelta

class ClaudeCode(Tool):
    """
    Tool for using Claude Code CLI to ensure code quality,
    design patterns, and configuration best practices
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_path = None
        self.git_baseline = None
    
    async def execute(self, command="", project_path="", prompt="", review_changes=True, mock_mode=False, **kwargs):
        """
        Execute Claude Code commands
        
        Args:
            command: The claude command to run (analyze, refactor, implement, fix, document, or direct prompt)
            project_path: Path to the project directory
            prompt: Direct prompt to send to Claude Code (used when command is not predefined)
            review_changes: Whether to review changes against standards (default: True)
            mock_mode: For testing without Claude CLI
        """
        
        # Convert all arguments to strings to avoid PrintStyle issues
        command = str(command) if command else ""
        project_path = str(project_path) if project_path else ""
        prompt = str(prompt) if prompt else ""
        
        # Set project path
        if project_path:
            self.project_path = project_path
        elif not self.project_path:
            self.project_path = os.getcwd()
        
        # Handle summary command first
        if command == "summary":
            summary = await self._generate_session_summary()
            return Response(
                message=summary,
                break_loop=True
            )
        
        # Get git baseline before Claude Code makes changes
        if review_changes and command in ["refactor", "implement", "fix"]:
            self.git_baseline = await self._capture_git_state()
        
        # Build the prompt based on command or use direct prompt
        if command and not prompt:
            prompt = self._build_prompt(command, self.project_path, kwargs.get('flags', ''))
            if not prompt:
                # Get the actual error from _build_prompt
                prompt_file = f"agent.tool.claude_code.{command}.md"
                return Response(
                    message=f"Error: Failed to load prompt for command '{command}'. Check if {prompt_file} exists in prompts directory.",
                    break_loop=True
                )
        elif not prompt:
            return Response(
                message="Error: No command or prompt specified for Claude Code",
                break_loop=False
            )
        
        PrintStyle(font_color="#85C1E9").print(f"Command: {command or 'direct prompt'}")
        PrintStyle(font_color="#85C1E9").print(f"Project path: {self.project_path}")
        
        # Mock mode for testing
        if mock_mode:
            PrintStyle(font_color="#FFCC00").print("MOCK MODE: Simulating Claude response")
            message = f"MOCK: Claude analyzed {self.project_path} and found:\n- Hardcoded values detected\n- Factory pattern could be applied\n- SOLID violations found"
            
            return Response(
                message=message,
                break_loop=False
            )
        
        try:
            # Check if claude CLI exists first
            check_claude = subprocess.run(
                ["which", "claude"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if check_claude.returncode != 0:
                return Response(
                    message="Error: Claude CLI not found. Please ensure it's installed and in PATH.\n\nTo test without Claude CLI, the agent can use mock_mode=True",
                    break_loop=True
                )
            
            # Execute claude interactively with streaming output
            message = await self._run_claude_interactive(prompt)
            
            # Review changes if requested
            if review_changes and command in ["refactor", "implement", "fix"]:
                review_result = await self._review_changes()
                if review_result and "violations" in review_result.lower():
                    # If violations found, tell Claude to fix them
                    fix_prompt = self._build_fix_prompt(review_result)
                    message += f"\n\n{review_result}\n\nRequesting Claude to fix violations..."
                    
                    fix_message = await self._run_claude_interactive(fix_prompt)
                    message += f"\n\nClaude's fix response:\n{fix_message}"
                elif review_result:
                    message += f"\n\n{review_result}"
                    
        except FileNotFoundError:
            message = "Error: Claude Code CLI not found. Please ensure it's installed and in PATH."
        except Exception as e:
            PrintStyle.error(f"Error executing Claude Code: {str(e)}")
            message = f"Error executing Claude Code: {str(e)}"
        
        # Determine whether to break the loop based on command type
        # Errors should break, work commands should continue
        should_break = "Error:" in message or command == "summary"
        
        return Response(
            message=message,
            break_loop=should_break
        )
    
    async def _run_claude_interactive(self, prompt):
        """Run Claude Code in non-interactive mode and capture output"""
        
        PrintStyle(font_color="#85C1E9").print("Executing Claude Code...")
        
        # Create a temporary file to store the prompt
        import tempfile
        temp_file = None
        
        try:
            # Write prompt to temporary file to avoid shell escaping issues
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write(prompt)
                temp_file = tmp.name
            
            # Set environment to force non-interactive mode
            env = os.environ.copy()
            env['TERM'] = 'dumb'  # Signal non-interactive terminal
            env['CI'] = 'true'    # Many CLIs check this to disable interactive features
            env['NO_COLOR'] = '1' # Disable color output
            env['FORCE_COLOR'] = '0' # Another way to disable color
            
            # Run claude with the prompt file as stdin
            process = await asyncio.create_subprocess_shell(
                f'claude < "{temp_file}"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_path,
                env=env
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=300  # 5 minute timeout
                )
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                return "Error: Claude Code timed out after 5 minutes"
            
            if process.returncode == 0:
                output = stdout.decode()
                # Clean up any ANSI escape codes
                import re
                output = re.sub(r'\x1b\[[0-9;]*m', '', output)
                return output.strip()
            else:
                error = stderr.decode() or "Unknown error"
                # Also include stdout in case error info is there
                if stdout:
                    error += f"\nOutput: {stdout.decode()}"
                return f"Claude Code error (return code {process.returncode}):\n{error}"
                
        except Exception as e:
            return f"Error running Claude Code: {str(e)}"
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def _build_prompt(self, command, project_path, flags):
        """Build appropriate prompt based on command"""
        try:
            # Read prompt from file
            prompt_file = f"agent.tool.claude_code.{command}.md"
            # Build kwargs, only include flags if it has a value
            kwargs = {"project_path": project_path}
            if flags:
                kwargs["flags"] = flags
            
            prompt = self.agent.read_prompt(prompt_file, **kwargs)
            return prompt
        except Exception as e:
            PrintStyle(font_color="red").print(f"Error reading prompt file for command '{command}': {str(e)}")
            # Return None if prompt file not found
            return None
    
    def _build_fix_prompt(self, review_result):
        """Build prompt to fix violations"""
        try:
            prompt = self.agent.read_prompt("agent.tool.claude_code.fix_violations.md", 
                review_result=review_result
            )
            return prompt
        except:
            # Fallback if prompt file not found
            return f"Fix these violations: {review_result}"
    
    async def _capture_git_state(self):
        """Capture current git state"""
        try:
            # Get current commit hash
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_path
            )
            
            if commit_result.returncode == 0:
                return commit_result.stdout.strip()
        except:
            pass
        
        return None
    
    async def _review_changes(self):
        """Review changes made by Claude Code against standards"""
        if not self.git_baseline:
            return None
        
        try:
            # Get git diff
            diff_result = subprocess.run(
                ["git", "diff", self.git_baseline],
                capture_output=True,
                text=True,
                cwd=self.project_path
            )
            
            if diff_result.returncode != 0:
                return None
            
            diff_output = diff_result.stdout
            
            # Analyze diff for violations
            violations = []
            improvements = []
            
            # Check for hardcoded values
            if self._check_hardcoded_values(diff_output):
                violations.append("Hardcoded configuration values detected")
                improvements.append("Move all configuration values to database or config system")
            
            # Check for design pattern opportunities
            pattern_suggestions = self._analyze_design_patterns(diff_output)
            if pattern_suggestions:
                improvements.extend(pattern_suggestions)
            
            # Generate review message
            if violations or improvements:
                review = "## Code Review Results\n\n"
                
                if violations:
                    review += "### ❌ Violations Found:\n"
                    for v in violations:
                        review += f"- {v}\n"
                    review += "\n"
                
                if improvements:
                    review += "### 💡 Improvement Suggestions:\n"
                    for i in improvements:
                        review += f"- {i}\n"
                    review += "\n"
                
                review += "**Action Required**: Claude Code must fix these issues before proceeding."
                return review
            else:
                return "✅ Code changes meet all quality standards."
                
        except Exception as e:
            return f"Error reviewing changes: {str(e)}"
    
    def _check_hardcoded_values(self, diff):
        """Check for hardcoded configuration values in diff"""
        # Simple heuristic checks for common hardcoded patterns
        hardcoded_patterns = [
            r'["\']https?://[^"\']+["\']',  # URLs
            r'["\'][\w\-]+\.[\w\-]+["\']',   # Domain names
            r'["\'][A-Za-z0-9]{20,}["\']',   # API keys
            r'timeout\s*=\s*\d+',             # Timeout values
            r'port\s*=\s*\d+',                # Port numbers
            r'["\']\/\w+\/\w+["\']',          # File paths
        ]
        
        import re
        for pattern in hardcoded_patterns:
            if re.search(pattern, diff):
                return True
        return False
    
    def _analyze_design_patterns(self, diff):
        """Analyze code for design pattern opportunities"""
        suggestions = []
        
        # Simple heuristics for pattern detection
        if "if isinstance" in diff or "type(" in diff:
            suggestions.append("Consider using Factory pattern for object creation")
        
        if diff.count("if ") > 5:
            suggestions.append("Consider Strategy pattern for complex conditional logic")
        
        if "global " in diff:
            suggestions.append("Use Dependency Injection instead of global variables")
        
        if diff.count("class ") > 3:
            suggestions.append("Ensure classes follow Single Responsibility Principle")
        
        return suggestions
    
    async def _generate_session_summary(self):
        """Generate a summary of the Claude Code session"""
        try:
            # Get git log for session
            if self.git_baseline:
                log_result = subprocess.run(
                    ["git", "log", f"{self.git_baseline}..HEAD", "--oneline"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path
                )
                
                commits = log_result.stdout if log_result.returncode == 0 else "No commits"
                
                # Get files changed
                files_result = subprocess.run(
                    ["git", "diff", "--name-only", self.git_baseline],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path
                )
                
                files_changed = files_result.stdout if files_result.returncode == 0 else "No files"
                
                summary = f"""## Claude Code Session Summary

**Project**: {self.project_path}

### Changes Made:
{commits}

### Files Modified:
{files_changed}

### Next Steps:
- Review all changes for design pattern compliance
- Ensure all configuration values are externalized
- Run tests to verify functionality
- Document any new patterns used"""
            else:
                summary = "Session summary unavailable (no git baseline)"
                
        except:
            summary = "Error generating session summary"
        
        return summary