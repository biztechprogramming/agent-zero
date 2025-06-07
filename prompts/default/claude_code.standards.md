# Claude Code Standards Enforcement

When working with Claude Code, enforce these standards strictly:

## 1. Design Pattern Requirements

### Must Apply Patterns When:
- Creating objects dynamically → **Factory Pattern**
- Multiple algorithms for same purpose → **Strategy Pattern**
- Event-driven communication needed → **Observer Pattern**
- Complex object construction → **Builder Pattern**
- Single instance needed → **Singleton Pattern** (use sparingly)
- Decoupling abstraction from implementation → **Bridge Pattern**

### SOLID Principles Check:
- **S**ingle Responsibility: Each class/function does ONE thing
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes must be substitutable
- **I**nterface Segregation: Many specific interfaces > one general
- **D**ependency Inversion: Depend on abstractions, not concretions

## 2. Configuration Externalization

### Must Externalize:
- API endpoints and URLs
- Timeout values
- Port numbers
- File paths
- Feature flags
- Environment-specific values
- API keys and secrets
- Rate limits
- Cache TTLs

### Acceptable Hardcoding (with review):
- Mathematical constants (π, e)
- Algorithm constants (MAX_ITERATIONS = 1000)
- Enum values
- Error messages (consider i18n needs)

### Implementation Pattern:
```python
# ❌ Bad
timeout = 30
api_url = "https://api.example.com"

# ✅ Good
timeout = ConfigDB.get("request_timeout_seconds", default=30)
api_url = ConfigDB.get("external_api_endpoint")
```

## 3. Code Documentation

### Required Comments:
- Design pattern usage: `// Factory Pattern: Creates appropriate handler`
- Complex algorithms: Explain the "why"
- Configuration keys: Document in CONFIG_README.md
- Non-obvious decisions: Explain trade-offs

### Pattern Annotation Examples:
```python
# Strategy Pattern: Allows swapping validation algorithms
class ValidationStrategy:
    pass

# Factory Pattern: Creates validators based on data type  
class ValidatorFactory:
    pass

# Observer Pattern: Notifies listeners of state changes
class EventManager:
    pass
```

## 4. Review Checklist

Before approving Claude Code changes:
- [ ] No hardcoded configuration values
- [ ] Appropriate design patterns applied
- [ ] SOLID principles followed
- [ ] Pattern usage documented in code
- [ ] Configuration keys documented
- [ ] Unit tests updated/added
- [ ] No code duplication
- [ ] Clear separation of concerns