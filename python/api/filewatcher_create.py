from python.helpers.api import ApiHandler
from python.tools.filewatcher import FilewatcherManager, FileWatcher


class FilewatcherCreate(ApiHandler):
    async def process(self, data, request):
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
            
            # Log the data we're trying to create
            print(f"Creating watcher: name={name}, directory={directory}, patterns={error_patterns}")
            
            watcher = FileWatcher(
                name=name,
                directory=directory,
                file_pattern=file_pattern,
                error_patterns=error_patterns,
                prompt=prompt
            )
            
            manager.add_watcher(watcher)
            
            # Don't start watching automatically - let the manager handle it
            # when it's properly initialized with an agent context
            
            return {
                "success": True,
                "watcher": watcher.model_dump(mode='json')
            }
            
        except Exception as e:
            import traceback
            print(f"Error creating watcher: {str(e)}")
            print(traceback.format_exc())
            return {"error": str(e)}