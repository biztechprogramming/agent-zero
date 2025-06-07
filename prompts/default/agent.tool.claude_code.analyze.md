Analyze the code in {{project_path}} and provide a detailed code review report.

Focus on:
1. **Hardcoded Values**: List ALL hardcoded strings, URLs, paths, timeouts, ports, or configuration values that should be externalized
2. **Design Patterns**: Identify specific places where patterns (Factory, Strategy, Observer, etc.) would improve the code
3. **SOLID Violations**: Find methods/classes that do too much or have poor separation of concerns
4. **Code Smells**: Duplicate code, long methods, poor naming, missing error handling

For each issue found, provide:
- File path and line number
- The problematic code snippet
- Why it's an issue
- Specific fix recommendation

Be thorough but concise. Start your analysis now.
{{#flags}}
Additional focus: {{flags}}
{{/flags}}