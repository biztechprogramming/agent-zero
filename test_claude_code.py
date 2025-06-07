#!/usr/bin/env python3
"""
Simple test script for the claude_code tool
"""
import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python.tools.claude_code import ClaudeCode
from python.helpers.tool import Response

async def test_claude_code():
    """Test the claude_code tool implementation"""
    
    print("Testing Claude Code Tool Implementation\n")
    
    # Create a mock agent object (minimal implementation)
    class MockAgent:
        def read_prompt(self, file, **kwargs):
            return f"Mock prompt from {file}"
    
    # Test 1: Create tool instance
    try:
        tool = ClaudeCode(
            agent=MockAgent(),
            name="claude_code",
            args={},
            message="test"
        )
        print("✅ Tool instance created successfully")
    except Exception as e:
        print(f"❌ Failed to create tool instance: {e}")
        return
    
    # Test 2: Test with no command
    try:
        response = await tool.execute()
        print(f"✅ No command test: {response.message}")
    except Exception as e:
        print(f"❌ No command test failed: {e}")
    
    # Test 3: Test start_session
    try:
        response = await tool.execute(command="start_session", project_path="/tmp/test")
        print(f"✅ Start session test: {response.message[:100]}...")
    except Exception as e:
        print(f"❌ Start session test failed: {e}")
    
    # Test 4: Test actual claude command (will likely fail)
    try:
        response = await tool.execute(command="analyze", project_path="/tmp")
        print(f"✅ Analyze command test: {response.message[:100]}...")
    except Exception as e:
        print(f"❌ Analyze command test failed: {e}")
    
    # Test 5: Test session status
    try:
        response = await tool.execute(command="session_status")
        print(f"✅ Session status test: {response.message}")
    except Exception as e:
        print(f"❌ Session status test failed: {e}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(test_claude_code())