from python.helpers.api import ApiHandler
from python.tools.filewatcher import FilewatcherManager, FileWatcher


class FilewatcherCreate(ApiHandler):
    async def process(self, data, ws, connection_id):
        # Extract parameters
        name = data.get("name", "").strip()
        directory = data.get("directory", "").strip()
        file_pattern = data.get("file_pattern", "").strip() or None
        error_patterns = data.get("error_patterns", [])
        prompt = data.get("prompt", "").strip()
        
        # Validate required fields
        if not name:
            return {"error": "Name is required"}
        if not directory:
            return {"error": "Directory is required"}
        
        # Get manager instance
        manager = await FilewatcherManager.get()
        
        # Create watcher
        try:
            # Default error patterns if none provided
            if not error_patterns:
                error_patterns = [
                    r"(?i)\berror\b",
                    r"(?i)\bexception\b",
                    r"(?i)\bfailed\b",
                    r"(?i)\bcrash",
                    r"(?i)\bcritical\b"
                ]
            
            # Default prompt if none provided
            if not prompt:
                prompt = "Investigate the error found in the log file and determine its root cause."
            
            watcher = FileWatcher(
                name=name,
                directory=directory,
                file_pattern=file_pattern,
                error_patterns=error_patterns,
                prompt=prompt
            )
            
            manager.add_watcher(watcher)
            
            # Start watching automatically
            from python.tools.filewatcher import FilewatcherTool
            tool = FilewatcherTool(agent=None, name="filewatcher", args={}, message="")
            await tool._start_watch_task(manager, watcher)
            
            return {
                "success": True,
                "watcher": watcher.model_dump(mode='json')
            }
            
        except Exception as e:
            return {"error": str(e)}