from python.helpers.api import ApiHandler
from python.tools.filewatcher import FilewatcherManager


class FilewatcherInvestigations(ApiHandler):
    async def process(self, data, request):
        # Get manager instance
        manager = await FilewatcherManager.get()
        
        # Optional watcher filter
        watcher_id = data.get("watcher_id", "").strip()
        
        if watcher_id:
            investigations = manager.get_investigations_for_watcher(watcher_id)
        else:
            investigations = list(manager.investigations.values())
        
        # Convert to JSON-serializable format
        investigations_data = []
        for inv in investigations:
            inv_dict = inv.model_dump(mode='json')
            
            # Add watcher name
            if inv.watcher_id in manager.watchers:
                inv_dict['watcher_name'] = manager.watchers[inv.watcher_id].name
            else:
                inv_dict['watcher_name'] = "Unknown"
            
            investigations_data.append(inv_dict)
        
        # Sort by last_seen descending
        investigations_data.sort(key=lambda x: x['last_seen'], reverse=True)
        
        return {
            "investigations": investigations_data
        }