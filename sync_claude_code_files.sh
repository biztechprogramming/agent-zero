#!/bin/bash

# Script to sync claude_code tool files to docker/run/agent-zero directory

echo "Syncing Claude Code tool files to docker/run/agent-zero..."

# Set source and destination directories
SOURCE_DIR="/mnt/c/dev/ai/agent-zero"
DEST_DIR="/mnt/c/dev/ai/agent-zero/docker/run/agent-zero"

# Create directories if they don't exist
mkdir -p "$DEST_DIR/python/tools"
mkdir -p "$DEST_DIR/prompts/default"

# Copy the tool implementation
echo "Copying claude_code.py..."
cp -v "$SOURCE_DIR/python/tools/claude_code.py" "$DEST_DIR/python/tools/"

# Copy the prompt files
echo "Copying prompt files..."
cp -v "$SOURCE_DIR/prompts/default/agent.system.tool.claude_code.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/agent.system.tools.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/fw.claude_code_review.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/fw.claude_code_timeout.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/claude_code.standards.md" "$DEST_DIR/prompts/default/"

# Copy the claude_code action-specific prompts
echo "Copying claude_code action prompts..."
cp -v "$SOURCE_DIR/prompts/default/agent.tool.claude_code.analyze.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/agent.tool.claude_code.document.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/agent.tool.claude_code.fix.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/agent.tool.claude_code.fix_violations.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/agent.tool.claude_code.implement.md" "$DEST_DIR/prompts/default/"
cp -v "$SOURCE_DIR/prompts/default/agent.tool.claude_code.refactor.md" "$DEST_DIR/prompts/default/"

# Copy the documentation
echo "Copying documentation..."
cp -v "$SOURCE_DIR/docs/adding-tools-and-prompts.md" "$DEST_DIR/docs/" 2>/dev/null || echo "Docs directory might not exist in docker/run"

# Verify the files were copied
echo -e "\nVerifying copied files:"
if [ -f "$DEST_DIR/python/tools/claude_code.py" ]; then
    echo "✅ claude_code.py copied successfully"
else
    echo "❌ claude_code.py copy failed"
fi

if [ -f "$DEST_DIR/prompts/default/agent.system.tool.claude_code.md" ]; then
    echo "✅ claude_code prompt copied successfully"
else
    echo "❌ claude_code prompt copy failed"
fi

echo -e "\nSync complete! You may need to restart the Docker container for changes to take effect."