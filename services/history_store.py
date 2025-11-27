"""
Almacenamiento persistente de historial de chat basado en JSONL por sesión.
Cada línea: {"session_id": str, "role": "user"|"assistant", "content": str, "timestamp": float}
"""
from __future__ import annotations
import os
import json
import threading
from time import time
from typing import List, Dict, Any, Optional

from config import HISTORY_DIR, HISTORY_FILE
from models import ChatTurn


class HistoryStore:
    """Gestor de historial de chat persistente y en memoria (caché simple)."""

    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file or HISTORY_FILE
        self._lock = threading.Lock()
        self._index: Dict[str, List[ChatTurn]] = {}
        self._ensure_paths()
        # Carga perezosa bajo demanda para sesiones; no precarga completa para no bloquear.

    def _ensure_paths(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        # Crear archivo si no existe
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", encoding="utf-8") as f:
                pass

    def append(self, session_id: str, role: str, content: str, timestamp: Optional[float] = None) -> None:
        if not session_id or not role or content is None:
            return
        ts = float(timestamp if timestamp is not None else time())
        turn = {"session_id": session_id, "role": role, "content": content, "timestamp": ts}
        line = json.dumps(turn, ensure_ascii=False)
        with self._lock:
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            # cache en memoria
            lst = self._index.setdefault(session_id, [])
            lst.append(ChatTurn(role=role, content=content, timestamp=ts))

    def _load_session_from_disk(self, session_id: str) -> List[ChatTurn]:
        turns: List[ChatTurn] = []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        rec = json.loads(line)
                        if rec.get("session_id") == session_id:
                            turns.append(ChatTurn(
                                role=rec.get("role", "user"),
                                content=rec.get("content", ""),
                                timestamp=float(rec.get("timestamp", time()))
                            ))
                    except Exception:
                        continue
        except FileNotFoundError:
            pass
        return turns

    def get_recent(self, session_id: Optional[str], limit: int = 8) -> List[ChatTurn]:
        if not session_id:
            return []
        with self._lock:
            if session_id not in self._index:
                self._index[session_id] = self._load_session_from_disk(session_id)
            turns = self._index.get(session_id, [])
            return turns[-limit:] if limit and limit > 0 else list(turns)

    def clear(self, session_id: Optional[str]) -> int:
        """Borra historial de una sesión (en memoria y reescribiendo archivo sin esa sesión).
        Retorna número de turnos eliminados.
        """
        if not session_id:
            return 0
        with self._lock:
            removed = len(self._index.get(session_id, []))
            self._index.pop(session_id, None)
            # Reescribir archivo filtrando sesión
            try:
                tmp_path = self.history_file + ".tmp"
                with open(self.history_file, "r", encoding="utf-8") as src, open(tmp_path, "w", encoding="utf-8") as dst:
                    for line in src:
                        if not line.strip():
                            continue
                        try:
                            rec = json.loads(line)
                            if rec.get("session_id") != session_id:
                                dst.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        except Exception:
                            # Conservar líneas corruptas por seguridad
                            dst.write(line)
                os.replace(tmp_path, self.history_file)
            except FileNotFoundError:
                pass
            return removed

    def stats(self) -> Dict[str, Any]:
        try:
            size = os.path.getsize(self.history_file)
        except Exception:
            size = 0
        return {"sessions_cached": len(self._index), "file": self.history_file, "size_bytes": size}
