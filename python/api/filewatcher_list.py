from python.helpers.api import ApiHandler
from python.tools.filewatcher import FilewatcherManager


class FilewatcherList(ApiHandler):
    async def process(self, data, ws, connection_id):
        # Get manager instance
        manager = await FilewatcherManager.get()
        
        # Get all watchers
        watchers = manager.list_watchers()
        
        # Add runtime status
        watchers_data = []
        for watcher in watchers:
            watcher_dict = watcher.model_dump(mode='json')
            watcher_dict['is_running'] = watcher.id in manager.watch_tasks
            
            # Add investigation count
            watcher_dict['investigation_count'] = len(watcher.investigations)
            
            # Add recent investigations
            recent_investigations = []
            for inv_id in watcher.investigations[-5:]:  # Last 5 investigations
                if inv_id in manager.investigations:
                    inv = manager.investigations[inv_id]
                    recent_investigations.append({
                        "id": inv.id,
                        "error_pattern": inv.error_pattern[:100] + "..." if len(inv.error_pattern) > 100 else inv.error_pattern,
                        "status": inv.investigation_status,
                        "occurrences": inv.occurrences,
                        "last_seen": inv.last_seen.isoformat()
                    })
            watcher_dict['recent_investigations'] = recent_investigations
            
            watchers_data.append(watcher_dict)
        
        return {
            "watchers": watchers_data
        }