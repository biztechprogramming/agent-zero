#\!/bin/bash

# Create necessary directories
mkdir -p docker/run/agent-zero/python/tools
mkdir -p docker/run/agent-zero/python/api
mkdir -p docker/run/agent-zero/webui/js
mkdir -p docker/run/agent-zero/prompts/default

# Copy Python files
cp python/tools/filewatcher.py docker/run/agent-zero/python/tools/
cp python/api/filewatcher_*.py docker/run/agent-zero/python/api/

# Copy JavaScript files
cp webui/js/filewatcher.js docker/run/agent-zero/webui/js/

# Copy prompt files
cp prompts/default/agent.system.tool.filewatcher.md docker/run/agent-zero/prompts/default/

# Copy modified files
cp webui/index.html docker/run/agent-zero/webui/
cp webui/js/settings.js docker/run/agent-zero/webui/js/
cp prompts/default/agent.system.tools.md docker/run/agent-zero/prompts/default/

echo "All filewatcher files copied successfully\!"
echo ""
echo "New files copied:"
echo "- python/tools/filewatcher.py"
echo "- python/api/filewatcher_create.py"
echo "- python/api/filewatcher_list.py"
echo "- python/api/filewatcher_update.py"
echo "- python/api/filewatcher_delete.py"
echo "- python/api/filewatcher_investigations.py"
echo "- python/api/filewatcher_update_investigation.py"
echo "- webui/js/filewatcher.js"
echo "- prompts/default/agent.system.tool.filewatcher.md"
echo ""
echo "Modified files copied:"
echo "- webui/index.html"
echo "- webui/js/settings.js"
echo "- prompts/default/agent.system.tools.md"
