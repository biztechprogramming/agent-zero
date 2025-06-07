#!/usr/bin/env python3
"""
Simple syntax and logic test for claude_code tool
"""
import subprocess
import os

def test_claude_command():
    """Test if 'claude' command exists"""
    print("Testing if 'claude' command exists...")
    
    try:
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Claude command found at: {result.stdout.strip()}")
            return True
        else:
            print("❌ Claude command NOT found in PATH")
            print("   This means the tool will fail when trying to execute claude commands")
            return False
            
    except Exception as e:
        print(f"❌ Error checking for claude command: {e}")
        return False

def test_git_commands():
    """Test if git commands work"""
    print("\nTesting git commands...")
    
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Git is available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Git command failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running git: {e}")
        return False

def check_syntax():
    """Basic syntax check of the claude_code.py file"""
    print("\nChecking claude_code.py syntax...")
    
    try:
        with open("python/tools/claude_code.py", "r") as f:
            code = f.read()
            
        # Try to compile the code
        compile(code, "claude_code.py", "exec")
        print("✅ Python syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in claude_code.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking syntax: {e}")
        return False

def main():
    print("=== Claude Code Tool Basic Tests ===\n")
    
    # Run tests
    claude_exists = test_claude_command()
    git_exists = test_git_commands()
    syntax_ok = check_syntax()
    
    print("\n=== Summary ===")
    if not claude_exists:
        print("\n⚠️  The main issue: 'claude' CLI command doesn't exist!")
        print("   The tool assumes there's a 'claude' command available in the system.")
        print("   This needs to be either:")
        print("   1. Installed separately, or")
        print("   2. The tool needs to be reimplemented to work differently")
        
    if not git_exists:
        print("\n⚠️  Git is not available, which the tool needs for tracking changes")
        
    if syntax_ok and git_exists and not claude_exists:
        print("\n📌 The code itself is fine, but it's trying to run a 'claude' command that doesn't exist.")

if __name__ == "__main__":
    main()