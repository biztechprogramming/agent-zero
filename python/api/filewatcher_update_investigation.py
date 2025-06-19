from python.helpers.api import ApiHandler
from python.tools.filewatcher import FilewatcherManager


class FilewatcherUpdateInvestigation(ApiHandler):
    async def process(self, data, request):
        # Extract parameters
        investigation_id = data.get("investigation_id", "").strip()
        
        if not investigation_id:
            return {"error": "Investigation ID is required"}
        
        # Get manager instance
        manager = await FilewatcherManager.get()
        
        # Check if investigation exists
        if investigation_id not in manager.investigations:
            return {"error": f"Investigation with ID '{investigation_id}' not found"}
        
        # Extract update fields
        updates = {}
        
        if "status" in data:
            updates["investigation_status"] = data["status"]
        
        if "result" in data:
            updates["investigation_result"] = data["result"]
        
        # Update investigation
        try:
            updated_inv = manager.update_investigation(investigation_id, updates)
            
            return {
                "success": True,
                "investigation": updated_inv.model_dump(mode='json')
            }
            
        except Exception as e:
            return {"error": str(e)}