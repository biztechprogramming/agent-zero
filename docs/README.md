# Agent Zero - Documentation Index

Welcome to the Agent Zero documentation! This collection of documents will help you understand, modify, and extend the Agent Zero framework.

## 📚 Documentation Overview

### 🎯 [Code Overview](./code-overview.md)
**Start here for a high-level understanding**
- What Agent Zero is and how it works
- Core architecture components
- Key design principles
- Customization points

### 🛠️ [Developer Cheatsheet](./developer-cheatsheet.md)
**Quick reference for development**
- Command reference and directory structure
- Tool development patterns
- API creation guide
- Configuration options
- Debugging tips and common patterns

### 📊 [Architecture Diagrams](./architecture-diagrams.md)
**Visual understanding of the system**
- System architecture overview
- Agent execution flow
- Tool architecture
- Multi-agent hierarchy
- Prompt system structure
- Web UI architecture
- Extension system
- Data flow diagrams

### 📖 [Essential Code Files](./essential-code-files.md)
**Guided tour of the most important code**
- Core system files with line-by-line guidance
- Tool implementation examples
- Prompt system files
- API and web interface code
- Recommended reading order

### 🔒 [Security and Non-Root Setup](./security-and-non-root-setup.md)
**Security considerations and non-root configuration**
- Current security model analysis
- Running Agent Zero as non-root user
- Implementation challenges and solutions
- Production security recommendations
- Docker security configurations

## � Quick Start Guide

### For Understanding the System
1. Read [Code Overview](./code-overview.md) for the big picture
2. Examine [Architecture Diagrams](./architecture-diagrams.md) for visual understanding
3. Follow [Essential Code Files](./essential-code-files.md) reading guide
4. Use [Developer Cheatsheet](./developer-cheatsheet.md) as reference

### For Development
1. Set up the environment using the main [README](../README.md)
2. Reference [Developer Cheatsheet](./developer-cheatsheet.md) for patterns
3. Study tool examples in [Essential Code Files](./essential-code-files.md)
4. Use [Architecture Diagrams](./architecture-diagrams.md) to understand component relationships

## 🎯 Key Concepts

### Agent Zero Philosophy
- **Transparency**: Everything is readable and modifiable
- **Modularity**: Components are loosely coupled
- **Extensibility**: Easy to add new capabilities
- **Flexibility**: No hard-coded limitations

### Core Components
- **Agents**: The thinking entities that process tasks
- **Tools**: Capabilities that agents can use (code execution, web browsing, etc.)
- **Prompts**: Text templates that define agent behavior
- **Extensions**: Hooks for adding custom functionality

### Development Patterns
- **Tool Creation**: Inherit from `Tool` base class
- **Prompt Modification**: Edit markdown files in `prompts/`
- **API Extension**: Add handlers in `python/api/`
- **UI Customization**: Modify files in `webui/`

## 🔧 Common Tasks

### Creating a New Tool
```python
# python/tools/my_tool.py
from python.helpers.tool import Tool, Response

class MyTool(Tool):
    async def execute(self, param="", **kwargs):
        result = f"Processed: {param}"
        return Response(message=result, break_loop=False)
```

### Modifying Agent Behavior
Edit prompt files in `prompts/default/`:
- `agent.system.main.role.md` - Core personality
- `agent.system.main.communication.md` - Communication style
- `agent.system.main.solving.md` - Problem-solving approach

### Adding API Endpoints
```python
# python/api/my_endpoint.py
from python.helpers.api import ApiHandler

class MyEndpoint(ApiHandler):
    async def handle_request(self, request):
        return {"status": "success"}
```

### Creating Extensions
```python
# python/extensions/monologue_start/my_extension.py
async def execute(agent, **kwargs):
    print(f"Agent {agent.number} starting task")
```

## 🔍 Debugging and Troubleshooting

### Common Issues
- **Tool not working**: Check tool implementation and prompt instructions
- **Agent behavior unexpected**: Review system prompts in `prompts/`
- **API errors**: Check authentication and endpoint configuration
- **UI problems**: Examine browser console and network requests

### Debug Resources
- **Logs**: Check `logs/` directory for HTML session logs
- **Memory**: Examine `memory/` for persistent agent memories
- **Configuration**: Review `.env` file for settings
- **Console Output**: Watch terminal for real-time debugging info

## 📈 Advanced Topics

### Multi-Agent Systems
- Agents can create subordinate agents for complex tasks
- Each agent maintains its own context and capabilities
- Hierarchical communication and task delegation

### Memory System
- Persistent memory using vector databases
- Automatic memory formation and retrieval
- Context-aware memory search

### Browser Automation
- AI-powered browser interaction
- Visual element recognition and interaction
- Web scraping and automation capabilities

### Extension System
- Lifecycle hooks for custom functionality
- Plugin-like architecture for adding features
- Event-driven extension execution

## 🤝 Contributing

### Code Contributions
1. Understand the architecture using these docs
2. Follow existing patterns and conventions
3. Test thoroughly with different scenarios
4. Document new features and changes

### Documentation Improvements
- Update these docs when adding new features
- Add examples for complex concepts
- Improve clarity and organization

## 🔗 Additional Resources

- **Main Repository**: [Agent Zero GitHub](https://github.com/frdel/agent-zero)
- **Installation Guide**: [Installation Documentation](../docs/installation.md)
- **Usage Examples**: [Usage Documentation](../docs/usage.md)
- **Community**: [Discord Server](https://discord.gg/B8KZKNsPpj)

---

This documentation is designed to be your comprehensive guide to understanding and working with Agent Zero. Start with the overview, use the diagrams for visual understanding, follow the code guide for hands-on learning, and reference the cheatsheet for quick answers.

Happy coding! 🚀