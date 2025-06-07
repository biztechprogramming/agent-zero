You are reviewing code at {{project_path}}. Your job is to ensure code is maintainable, readable, and follows best practices by:
1. Leveraging design patterns (Factory, Strategy, Observer, etc.) where appropriate
2. Externalizing ALL configurable values to a database or configuration system (no hardcoding)
3. Following SOLID principles
4. Documenting pattern usage with comments like '// Uses Factory Pattern'

Current directory: {{project_path}}

Please refactor the code to:
1. Apply appropriate design patterns (Factory, Strategy, Observer, etc.)
2. Move ALL hardcoded values to ConfigDB.get() or similar
3. Fix any SOLID principle violations
4. Add comments documenting pattern usage
{{#flags}}
Additional requirements: {{flags}}
{{/flags}}