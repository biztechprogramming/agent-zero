# Filewatcher Tool

The filewatcher tool allows you to monitor log files for errors and automatically investigate them.

## Available Methods:

### Create a File Watcher
`filewatcher:create`
- `name`: A descriptive name for the watcher
- `directory`: The directory to monitor
- `file_pattern`: Optional glob pattern (e.g., "*.log", "error-*.txt")
- `error_patterns`: List of regex patterns to match errors
- `prompt`: Custom investigation prompt for errors

### List Watchers
`filewatcher:list`
Shows all configured file watchers and their status.

### Update a Watcher
`filewatcher:update`
- `watcher_id`: ID of the watcher to update
- All create parameters are optional for updates

### Delete a Watcher
`filewatcher:delete`
- `watcher_id`: ID of the watcher to delete

### Start/Stop Watching
`filewatcher:start` / `filewatcher:stop`
- `watcher_id`: ID of the watcher to control

### List Investigations
`filewatcher:list_investigations`
- `watcher_id`: Optional - filter by specific watcher

### Update Investigation Status
`filewatcher:update_investigation`
- `investigation_id`: ID of the investigation
- `status`: New status (pending, investigating, completed, ignored)
- `result`: Optional investigation result/findings

## Usage Examples:

1. Create a watcher for application logs:
```
<filewatcher:create>
name: Application Error Monitor
directory: /var/log/myapp
file_pattern: app-*.log
error_patterns: ["ERROR", "FATAL", "Exception"]
prompt: Investigate this application error and determine the root cause. Check related log entries and suggest a fix.
</filewatcher:create>
```

2. List all watchers:
```
<filewatcher:list>
</filewatcher:list>
```

3. Check investigations:
```
<filewatcher:list_investigations>
</filewatcher:list_investigations>
```

## How It Works:

1. The filewatcher continuously monitors specified directories for files matching the pattern
2. When an error pattern is detected in a log file, it triggers an investigation
3. The agent receives the error context and the investigation prompt
4. Duplicate errors are tracked - if the same error occurs again before investigation completes, it increments a counter instead of creating a new investigation
5. Users can mark investigations as completed or ignored through the UI or tool commands

## Best Practices:

- Use specific file patterns to avoid monitoring unnecessary files
- Create focused error patterns to reduce false positives
- Provide detailed investigation prompts to guide the agent
- Regularly review and update investigation statuses
- Consider pausing watchers during system maintenance to avoid false alerts