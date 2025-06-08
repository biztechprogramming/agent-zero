from python.helpers.api import ApiHandler
from python.tools.filewatcher import FilewatcherManager, WatcherState


class FilewatcherUpdate(ApiHandler):
    async def process(self, data, ws, connection_id):
        # Extract parameters
        watcher_id = data.get("watcher_id", "").strip()
        
        if not watcher_id:
            return {"error": "Watcher ID is required"}
        
        # Get manager instance
        manager = await FilewatcherManager.get()
        
        # Check if watcher exists
        watcher = manager.get_watcher(watcher_id)
        if not watcher:
            return {"error": f"Watcher with ID '{watcher_id}' not found"}
        
        # Extract update fields
        updates = {}
        
        if "name" in data:
            updates["name"] = data["name"].strip()
        
        if "directory" in data:
            updates["directory"] = data["directory"].strip()
        
        if "file_pattern" in data:
            updates["file_pattern"] = data["file_pattern"].strip() or None
        
        if "error_patterns" in data:
            updates["error_patterns"] = data["error_patterns"]
        
        if "prompt" in data:
            updates["prompt"] = data["prompt"].strip()
        
        if "state" in data:
            state_value = data["state"].upper()
            if state_value in [s.value.upper() for s in WatcherState]:
                updates["state"] = WatcherState(state_value.lower())
        
        # Update watcher
        try:
            updated_watcher = manager.update_watcher(watcher_id, updates)
            
            # Handle state changes
            if "state" in updates:
                from python.tools.filewatcher import FilewatcherTool
                tool = FilewatcherTool(agent=None, name="filewatcher", args={}, message="")
                
                if updates["state"] == WatcherState.ACTIVE and watcher_id not in manager.watch_tasks:
                    # Start watching
                    await tool._start_watch_task(manager, updated_watcher)
                elif updates["state"] in [WatcherState.PAUSED, WatcherState.STOPPED] and watcher_id in manager.watch_tasks:
                    # Stop watching
                    manager.watch_tasks[watcher_id].cancel()
                    del manager.watch_tasks[watcher_id]
            
            return {
                "success": True,
                "watcher": updated_watcher.model_dump(mode='json')
            }
            
        except Exception as e:
            return {"error": str(e)}