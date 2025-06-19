from python.helpers.api import ApiHandler
from python.tools.filewatcher import FilewatcherManager


class FilewatcherDelete(ApiHandler):
    async def process(self, data, request):
        # Extract parameters
        watcher_id = data.get("watcher_id", "").strip()
        
        if not watcher_id:
            return {"error": "Watcher ID is required"}
        
        # Get manager instance
        manager = await FilewatcherManager.get()
        
        # Delete watcher
        if manager.delete_watcher(watcher_id):
            return {"success": True}
        else:
            return {"error": f"Watcher with ID '{watcher_id}' not found"}