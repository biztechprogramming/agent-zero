### claude_code
Use Claude Code CLI to ensure code is maintainable, readable, and follows best practices by leveraging design patterns and externalizing all configurable values.

**Core Responsibilities:**
1. **Design Pattern Enforcement** - Always consider and apply appropriate design patterns
2. **Zero Hardcoding Rule** - All configuration values must be stored in a database or configuration system
3. **Code Quality Review** - Validate changes against SOLID principles and best practices
4. **Fix Enforcement** - Claude Code must fix its own violations, not the agent

**Available Commands:**
- `analyze` - Analyze codebase for patterns and improvements
- `refactor` - Refactor code with pattern enforcement
- `implement` - Implement new features following standards
- `fix` - Fix issues while maintaining standards
- `document` - Generate documentation with pattern annotations
- `summary` - Generate a summary of changes made in the current session

**Arguments:**
- `command` (optional): The Claude Code command to execute (if not provided, use `prompt` instead)
- `project_path` (optional): Project directory path (defaults to current directory)
- `prompt` (optional): Direct prompt to send to Claude Code for custom requests
- `review_changes` (optional): Auto-review changes for compliance (default: true)

**Design Pattern Guidelines:**
When reviewing or writing code, ALWAYS ask:
- "Can a design pattern improve readability, scalability, or maintainability here?"
- "Does this logic violate SOLID principles? Could a pattern (e.g., Strategy, Factory, Observer) decouple it?"
- "Is this code prone to future changes? If yes, use a pattern to encapsulate variation."

**Pattern Examples to Enforce:**
- Use **Factory** for object creation logic
- Apply **Strategy** for interchangeable algorithms
- Implement **Observer** for event-driven workflows
- Prefer **Dependency Injection** over hardcoded dependencies

**Zero Hardcoding Rule:**
All configuration values (strings, numbers, API keys, paths) MUST be externalized:
- Store in project's database (SQL/NoSQL) or dedicated config table
- Exception: Only true constants (e.g., MAX_RETRIES = 3) after review approval
- Bad: `url = "http://api.example.com"` ❌
- Good: `url = ConfigDB.get("api_endpoint")` ✅

**Code Review Process:**
1. Claude Code makes changes
2. Agent reviews git diff for violations
3. If violations found, agent tells Claude Code what to fix
4. Claude Code must fix its own work
5. Process repeats until standards met

**Example - Analyze code:**
~~~json
{
    "thoughts": [
        "User wants me to analyze code for improvements",
        "I'll use claude_code to identify issues",
        "This will find hardcoded values and design problems"
    ],
    "tool_name": "claude_code",
    "tool_args": {
        "command": "analyze",
        "project_path": "/home/user/project"
    }
}
~~~

**Example - Refactor with pattern enforcement:**
~~~json
{
    "thoughts": [
        "Now I'll have Claude Code refactor the code",
        "It should apply appropriate design patterns",
        "All config values must be externalized"
    ],
    "tool_name": "claude_code",
    "tool_args": {
        "command": "refactor",
        "project_path": "/home/user/project",
        "flags": "--apply-patterns --externalize-config"
    }
}
~~~

**Example - Review and enforce fixes:**
~~~json
{
    "thoughts": [
        "Claude Code made changes, but review found violations",
        "Found hardcoded API URL and missing Factory pattern",
        "I must tell Claude Code to fix these issues"
    ],
    "tool_name": "claude_code",
    "tool_args": {
        "command": "fix"
    }
}
~~~

**Example - Direct prompt usage:**
~~~json
{
    "thoughts": [
        "User has a specific request for Claude Code",
        "I'll send a custom prompt instead of using predefined commands"
    ],
    "tool_name": "claude_code",
    "tool_args": {
        "prompt": "Please analyze the authentication module in this project and suggest improvements for security and maintainability. Focus on potential design patterns that could improve the code structure.",
        "project_path": "/home/user/project"
    }
}
~~~

**Critical Rules:**
1. **Never fix Claude Code's work yourself** - Always make Claude Code fix its own violations
2. **Document pattern usage** - Ensure code includes comments like `// Uses Factory Pattern`
3. **Review every change** - Use git diff to verify compliance
4. **Enforce standards strictly** - No exceptions to hardcoding or pattern rules
5. **Time management** - Monitor session time, create status docs on timeout

**Best Practices:**
- Start sessions for any significant code work
- Review changes immediately after each Claude Code operation
- Be specific about which patterns to apply and why
- Keep configuration documentation updated
- Ensure Claude Code annotates all pattern usage in code