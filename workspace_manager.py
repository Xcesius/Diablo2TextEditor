import json
import threading
import os
from typing import Dict, Any


class WorkspaceManager:
    """Simple JSON-backed storage for editor workspaces.

    Stores named snapshots containing window geometry/state, open files, and view settings.
    """

    def __init__(self, path: str = "workspaces.json") -> None:
        self.path = path
        self._lock = threading.Lock()

    def _load_unlocked(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"version": 1, "workspaces": {}}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {"version": 1, "workspaces": {}}
        data.setdefault("version", 1)
        data.setdefault("workspaces", {})
        return data

    def _save_unlocked(self, data: Dict[str, Any]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, self.path)

    def list_names(self):
        with self._lock:
            return sorted(self._load_unlocked().get("workspaces", {}).keys())

    def get(self, name: str) -> Dict[str, Any] | None:
        with self._lock:
            return self._load_unlocked().get("workspaces", {}).get(name)

    def save(self, name: str, snapshot: Dict[str, Any]) -> None:
        with self._lock:
            data = self._load_unlocked()
            data.setdefault("workspaces", {})[name] = snapshot
            self._save_unlocked(data)

    def delete(self, name: str) -> bool:
        with self._lock:
            data = self._load_unlocked()
            ws = data.get("workspaces", {})
            if name in ws:
                del ws[name]
                self._save_unlocked(data)
                return True
            return False

