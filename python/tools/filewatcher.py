import asyncio
import os
import re
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field

from python.helpers.tool import Tool, Response
from python.helpers import files
from python.helpers.print_style import PrintStyle


class WatcherState(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


class ErrorInvestigation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    error_pattern: str
    error_hash: str
    first_seen: datetime
    last_seen: datetime
    occurrences: int = 1
    investigation_status: str = "pending"  # pending, investigating, completed, ignored
    investigation_result: Optional[str] = None
    file_path: str
    watcher_id: str


class FileWatcher(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    directory: str
    file_pattern: Optional[str] = None
    error_patterns: List[str] = Field(default_factory=list)
    prompt: str
    state: WatcherState = WatcherState.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_positions: Dict[str, int] = Field(default_factory=dict)
    investigations: List[str] = Field(default_factory=list)  # Investigation IDs


class FilewatcherManager:
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.watchers: Dict[str, FileWatcher] = {}
        self.investigations: Dict[str, ErrorInvestigation] = {}
        self.watch_tasks: Dict[str, asyncio.Task] = {}
        self.data_dir = files.get_abs_path("tmp/filewatcher")
        self.watchers_file = os.path.join(self.data_dir, "watchers.json")
        self.investigations_file = os.path.join(self.data_dir, "investigations.json")
        self._ensure_data_dir()
        self._load_data()

    @classmethod
    async def get(cls):
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def _ensure_data_dir(self):
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

    def _load_data(self):
        # Load watchers
        if os.path.exists(self.watchers_file):
            try:
                data = json.loads(files.read_file(self.watchers_file))
                for watcher_data in data:
                    watcher = FileWatcher(**watcher_data)
                    self.watchers[watcher.id] = watcher
            except Exception as e:
                PrintStyle.error(f"Failed to load watchers: {e}")

        # Load investigations
        if os.path.exists(self.investigations_file):
            try:
                data = json.loads(files.read_file(self.investigations_file))
                for inv_data in data:
                    inv = ErrorInvestigation(**inv_data)
                    self.investigations[inv.id] = inv
            except Exception as e:
                PrintStyle.error(f"Failed to load investigations: {e}")

    def _save_watchers(self):
        data = [w.model_dump(mode='json') for w in self.watchers.values()]
        files.write_file(self.watchers_file, json.dumps(data, indent=2, default=str))

    def _save_investigations(self):
        data = [i.model_dump(mode='json') for i in self.investigations.values()]
        files.write_file(self.investigations_file, json.dumps(data, indent=2, default=str))

    def add_watcher(self, watcher: FileWatcher) -> FileWatcher:
        self.watchers[watcher.id] = watcher
        self._save_watchers()
        return watcher

    def update_watcher(self, watcher_id: str, updates: dict) -> Optional[FileWatcher]:
        if watcher_id in self.watchers:
            watcher = self.watchers[watcher_id]
            for key, value in updates.items():
                if hasattr(watcher, key):
                    setattr(watcher, key, value)
            watcher.updated_at = datetime.now()
            self._save_watchers()
            return watcher
        return None

    def delete_watcher(self, watcher_id: str) -> bool:
        if watcher_id in self.watchers:
            # Stop watching task if running
            if watcher_id in self.watch_tasks:
                self.watch_tasks[watcher_id].cancel()
                del self.watch_tasks[watcher_id]
            del self.watchers[watcher_id]
            self._save_watchers()
            return True
        return False

    def get_watcher(self, watcher_id: str) -> Optional[FileWatcher]:
        return self.watchers.get(watcher_id)

    def list_watchers(self) -> List[FileWatcher]:
        return list(self.watchers.values())

    def add_investigation(self, investigation: ErrorInvestigation) -> ErrorInvestigation:
        self.investigations[investigation.id] = investigation
        if investigation.watcher_id in self.watchers:
            self.watchers[investigation.watcher_id].investigations.append(investigation.id)
            self._save_watchers()
        self._save_investigations()
        return investigation

    def update_investigation(self, inv_id: str, updates: dict) -> Optional[ErrorInvestigation]:
        if inv_id in self.investigations:
            inv = self.investigations[inv_id]
            for key, value in updates.items():
                if hasattr(inv, key):
                    setattr(inv, key, value)
            self._save_investigations()
            return inv
        return None

    def get_investigations_for_watcher(self, watcher_id: str) -> List[ErrorInvestigation]:
        return [inv for inv in self.investigations.values() if inv.watcher_id == watcher_id]

    def find_existing_investigation(self, watcher_id: str, error_hash: str) -> Optional[ErrorInvestigation]:
        for inv in self.investigations.values():
            if inv.watcher_id == watcher_id and inv.error_hash == error_hash and inv.investigation_status != "ignored":
                return inv
        return None


class FilewatcherTool(Tool):
    async def execute(self, **kwargs):
        if self.method == "create":
            return await self.create_watcher(**kwargs)
        elif self.method == "list":
            return await self.list_watchers(**kwargs)
        elif self.method == "update":
            return await self.update_watcher(**kwargs)
        elif self.method == "delete":
            return await self.delete_watcher(**kwargs)
        elif self.method == "start":
            return await self.start_watching(**kwargs)
        elif self.method == "stop":
            return await self.stop_watching(**kwargs)
        elif self.method == "investigate":
            return await self.trigger_investigation(**kwargs)
        elif self.method == "update_investigation":
            return await self.update_investigation(**kwargs)
        elif self.method == "list_investigations":
            return await self.list_investigations(**kwargs)
        else:
            return Response(
                message=f"Unknown method '{self.name}:{self.method}'",
                break_loop=False
            )

    async def create_watcher(self, name: str, directory: str, file_pattern: str = None, 
                           error_patterns: List[str] = None, prompt: str = None, **kwargs):
        manager = await FilewatcherManager.get()
        
        # Validate directory path
        # If the path doesn't start with /, assume it's relative and make it absolute
        if not directory.startswith('/'):
            directory = '/' + directory
            
        if not os.path.exists(directory):
            # Try to create the directory if it doesn't exist
            try:
                os.makedirs(directory, exist_ok=True)
                message = f"Created directory '{directory}' and set up file watcher '{name}'"
            except Exception as e:
                return Response(
                    message=f"Directory '{directory}' does not exist and could not be created: {str(e)}",
                    break_loop=False
                )
        else:
            message = f"Created file watcher '{name}' for directory '{directory}'"
        
        # Default prompt if not provided
        if not prompt:
            prompt = "Investigate the error found in the log file and determine its root cause."
        
        # Default error patterns if not provided
        if not error_patterns:
            error_patterns = [
                r"(?i)\berror\b",
                r"(?i)\bexception\b",
                r"(?i)\bfailed\b",
                r"(?i)\bcrash",
                r"(?i)\bcritical\b"
            ]
        
        watcher = FileWatcher(
            name=name,
            directory=directory,
            file_pattern=file_pattern,
            error_patterns=error_patterns,
            prompt=prompt
        )
        
        manager.add_watcher(watcher)
        
        # Start watching immediately
        await self._start_watch_task(manager, watcher)
        
        return Response(
            message=message,
            break_loop=False
        )

    async def list_watchers(self, **kwargs):
        manager = await FilewatcherManager.get()
        watchers = manager.list_watchers()
        
        if not watchers:
            return Response(
                message="No file watchers configured",
                break_loop=False
            )
        
        output = []
        for watcher in watchers:
            status = "watching" if watcher.id in manager.watch_tasks else watcher.state.value
            output.append(
                f"- {watcher.name} (ID: {watcher.id})\n"
                f"  Directory: {watcher.directory}\n"
                f"  Pattern: {watcher.file_pattern or '*'}\n"
                f"  Status: {status}\n"
                f"  Investigations: {len(watcher.investigations)}"
            )
        
        return Response(
            message="File watchers:\n" + "\n".join(output),
            break_loop=False
        )

    async def update_watcher(self, watcher_id: str, **kwargs):
        manager = await FilewatcherManager.get()
        
        # Extract valid update fields
        updates = {}
        for field in ['name', 'directory', 'file_pattern', 'error_patterns', 'prompt', 'state']:
            if field in kwargs:
                updates[field] = kwargs[field]
        
        watcher = manager.update_watcher(watcher_id, updates)
        if not watcher:
            return Response(
                message=f"File watcher with ID '{watcher_id}' not found",
                break_loop=False
            )
        
        # Restart watching if it was active
        if watcher.state == WatcherState.ACTIVE and watcher_id in manager.watch_tasks:
            manager.watch_tasks[watcher_id].cancel()
            await self._start_watch_task(manager, watcher)
        
        return Response(
            message=f"Updated file watcher '{watcher.name}'",
            break_loop=False
        )

    async def delete_watcher(self, watcher_id: str, **kwargs):
        manager = await FilewatcherManager.get()
        
        if manager.delete_watcher(watcher_id):
            return Response(
                message=f"Deleted file watcher with ID '{watcher_id}'",
                break_loop=False
            )
        else:
            return Response(
                message=f"File watcher with ID '{watcher_id}' not found",
                break_loop=False
            )

    async def start_watching(self, watcher_id: str, **kwargs):
        manager = await FilewatcherManager.get()
        watcher = manager.get_watcher(watcher_id)
        
        if not watcher:
            return Response(
                message=f"File watcher with ID '{watcher_id}' not found",
                break_loop=False
            )
        
        if watcher_id in manager.watch_tasks:
            return Response(
                message=f"File watcher '{watcher.name}' is already running",
                break_loop=False
            )
        
        watcher.state = WatcherState.ACTIVE
        manager.update_watcher(watcher_id, {"state": WatcherState.ACTIVE})
        await self._start_watch_task(manager, watcher)
        
        return Response(
            message=f"Started watching '{watcher.name}'",
            break_loop=False
        )

    async def stop_watching(self, watcher_id: str, **kwargs):
        manager = await FilewatcherManager.get()
        watcher = manager.get_watcher(watcher_id)
        
        if not watcher:
            return Response(
                message=f"File watcher with ID '{watcher_id}' not found",
                break_loop=False
            )
        
        if watcher_id in manager.watch_tasks:
            manager.watch_tasks[watcher_id].cancel()
            del manager.watch_tasks[watcher_id]
        
        manager.update_watcher(watcher_id, {"state": WatcherState.STOPPED})
        
        return Response(
            message=f"Stopped watching '{watcher.name}'",
            break_loop=False
        )

    async def trigger_investigation(self, watcher_id: str, error_text: str, file_path: str, **kwargs):
        manager = await FilewatcherManager.get()
        watcher = manager.get_watcher(watcher_id)
        
        if not watcher:
            return Response(
                message=f"File watcher with ID '{watcher_id}' not found",
                break_loop=False
            )
        
        # Generate error hash for deduplication
        error_hash = self._generate_error_hash(error_text)
        
        # Check for existing investigation
        existing = manager.find_existing_investigation(watcher_id, error_hash)
        if existing:
            existing.occurrences += 1
            existing.last_seen = datetime.now()
            manager.update_investigation(existing.id, {
                "occurrences": existing.occurrences,
                "last_seen": existing.last_seen
            })
            
            if existing.investigation_status == "completed":
                return Response(
                    message=f"Error already investigated (ID: {existing.id}). Occurrences: {existing.occurrences}",
                    break_loop=False
                )
            elif existing.investigation_status == "investigating":
                return Response(
                    message=f"Error is currently being investigated (ID: {existing.id}). Occurrences: {existing.occurrences}",
                    break_loop=False
                )
        
        # Create new investigation
        investigation = ErrorInvestigation(
            error_pattern=error_text[:200],  # First 200 chars as pattern
            error_hash=error_hash,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            file_path=file_path,
            watcher_id=watcher_id
        )
        
        manager.add_investigation(investigation)
        
        # Trigger investigation with the agent
        investigation_prompt = f"{watcher.prompt}\n\nError found in {file_path}:\n{error_text}\n\nInvestigation ID: {investigation.id}"
        
        # Update investigation status
        manager.update_investigation(investigation.id, {"investigation_status": "investigating"})
        
        # Send the investigation prompt to the agent
        self.agent.set_data("filewatcher_investigation", {
            "id": investigation.id,
            "watcher_id": watcher_id,
            "prompt": investigation_prompt
        })
        
        return Response(
            message=f"Investigation triggered for error in {file_path} (ID: {investigation.id})\n\n{investigation_prompt}",
            break_loop=True  # Break the loop to let agent investigate
        )

    async def update_investigation(self, investigation_id: str, status: str = None, result: str = None, **kwargs):
        manager = await FilewatcherManager.get()
        
        updates = {}
        if status:
            updates["investigation_status"] = status
        if result:
            updates["investigation_result"] = result
        
        investigation = manager.update_investigation(investigation_id, updates)
        if not investigation:
            return Response(
                message=f"Investigation with ID '{investigation_id}' not found",
                break_loop=False
            )
        
        return Response(
            message=f"Updated investigation {investigation_id}. Status: {investigation.investigation_status}",
            break_loop=False
        )

    async def list_investigations(self, watcher_id: str = None, **kwargs):
        manager = await FilewatcherManager.get()
        
        if watcher_id:
            investigations = manager.get_investigations_for_watcher(watcher_id)
            title = f"Investigations for watcher {watcher_id}"
        else:
            investigations = list(manager.investigations.values())
            title = "All investigations"
        
        if not investigations:
            return Response(
                message=f"No investigations found",
                break_loop=False
            )
        
        output = [title + ":"]
        for inv in investigations:
            output.append(
                f"- ID: {inv.id}\n"
                f"  Error: {inv.error_pattern[:100]}...\n"
                f"  File: {inv.file_path}\n"
                f"  Status: {inv.investigation_status}\n"
                f"  Occurrences: {inv.occurrences}\n"
                f"  First seen: {inv.first_seen}\n"
                f"  Last seen: {inv.last_seen}"
            )
        
        return Response(
            message="\n".join(output),
            break_loop=False
        )

    async def _start_watch_task(self, manager: FilewatcherManager, watcher: FileWatcher):
        """Start the async task to watch files"""
        task = asyncio.create_task(self._watch_files(manager, watcher))
        manager.watch_tasks[watcher.id] = task

    async def _watch_files(self, manager: FilewatcherManager, watcher: FileWatcher):
        """Main file watching loop"""
        while watcher.state == WatcherState.ACTIVE:
            try:
                # Get files to watch
                files_to_watch = self._get_files_to_watch(watcher)
                
                for file_path in files_to_watch:
                    await self._check_file_for_errors(manager, watcher, file_path)
                
                # Sleep before next check
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                PrintStyle.error(f"Error in file watcher {watcher.name}: {e}")
                await asyncio.sleep(5)

    def _get_files_to_watch(self, watcher: FileWatcher) -> List[str]:
        """Get list of files to watch based on pattern"""
        files_to_watch = []
        
        try:
            for root, _, files in os.walk(watcher.directory):
                for file in files:
                    if watcher.file_pattern:
                        # Use glob pattern matching
                        if Path(file).match(watcher.file_pattern):
                            files_to_watch.append(os.path.join(root, file))
                    else:
                        # Watch all files if no pattern specified
                        files_to_watch.append(os.path.join(root, file))
        except Exception as e:
            PrintStyle.error(f"Error scanning directory {watcher.directory}: {e}")
        
        return files_to_watch

    async def _check_file_for_errors(self, manager: FilewatcherManager, watcher: FileWatcher, file_path: str):
        """Check a specific file for errors"""
        try:
            # Get last read position
            last_pos = watcher.last_positions.get(file_path, 0)
            
            # Read file from last position
            with open(file_path, 'r') as f:
                f.seek(last_pos)
                new_content = f.read()
                new_pos = f.tell()
            
            if new_content:
                # Update last position
                watcher.last_positions[file_path] = new_pos
                manager.update_watcher(watcher.id, {"last_positions": watcher.last_positions})
                
                # Check for errors
                for line in new_content.split('\n'):
                    if line.strip():
                        for pattern in watcher.error_patterns:
                            if re.search(pattern, line):
                                # Found an error, trigger investigation
                                await self.trigger_investigation(
                                    watcher_id=watcher.id,
                                    error_text=line,
                                    file_path=file_path
                                )
                                break
        
        except Exception as e:
            # File might be deleted or inaccessible
            if file_path in watcher.last_positions:
                del watcher.last_positions[file_path]
                manager.update_watcher(watcher.id, {"last_positions": watcher.last_positions})

    def _generate_error_hash(self, error_text: str) -> str:
        """Generate a hash for error deduplication"""
        # Remove timestamps and specific values to group similar errors
        cleaned = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', '', error_text)
        cleaned = re.sub(r'\b\d+\b', 'N', cleaned)  # Replace numbers with N
        cleaned = re.sub(r'[a-fA-F0-9]{8,}', 'HASH', cleaned)  # Replace hashes
        
        # Simple hash using Python's hash function
        return str(hash(cleaned))