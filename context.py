
# core/context.py
"""Conversation context manager.

Creates a brand‑new JSON file for each chat session and never merges
previous sessions unless explicitly queried. Provides lightweight helpers
to list or search past logs on demand (query style) without polluting the
active conversation history.
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class ContextManager:
    def __init__(self, system_prompt: str, log_dir: str = "chat_logs", auto_save: bool = True) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_started = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_file = self.log_dir / f"chat_{self.session_started}.json"
        self.auto_save = auto_save
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        self._write_session()
        logging.info(f"[context] New session file created: {self.session_file}")

    # ---------------- Core API ----------------
    def add_message(self, role: str, content: str) -> None:
        timestamp = datetime.now().isoformat()
        self.messages.append({
            "role": role, 
            "content": content,
            "timestamp": timestamp
        })
        logging.info(f"[context] add_message role={role}; total={len(self.messages)}")
        if self.auto_save:
            self._write_session()

    def get_history(self) -> List[Dict[str, str]]:
        logging.debug(f"[context] get_history len={len(self.messages)}")
        return self.messages

    def clear_history(self, system_prompt: str) -> None:
        self.messages = [{"role": "system", "content": system_prompt}]
        logging.info("[context] History cleared (system prompt retained)")
        if self.auto_save:
            self._write_session()

    # ---------------- Persistence ----------------
    def _write_session(self) -> None:
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"[context] Failed writing session file: {e}")

    def save_snapshot(self) -> Path:
        """Explicit snapshot (alias kept for controller compatibility)."""
        self._write_session()
        logging.info(f"[context] Snapshot saved: {self.session_file}")
        return self.session_file

    # ---------------- Query Utilities (do NOT modify current history) ----------------
    def list_past_logs(self) -> List[Path]:
        files = sorted(self.log_dir.glob("chat_*.json"))
        # Exclude the current session file path from listing of 'past'
        return [p for p in files if p != self.session_file]

    def load_log(self, file_path: str | Path) -> Optional[List[Dict[str, str]]]:
        p = Path(file_path)
        if not p.exists():
            logging.warning(f"[context] load_log: file not found {p}")
            return None
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"[context] Failed to load log {p}: {e}")
            return None

    def search_past(self, term: str, limit: int = 5) -> List[Dict[str, str]]:
        """Search past logs for messages containing the term (case-insensitive)."""
        term_l = term.lower()
        results: List[Dict[str, str]] = []
        for log_file in reversed(self.list_past_logs()):  # newest first
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for msg in data:
                    if term_l in msg.get("content", "").lower():
                        results.append({"file": log_file.name, **msg})
                        if len(results) >= limit:
                            return results
            except Exception:
                continue
        return results

    def format_search_results_for_context(self, results: List[Dict[str, str]]) -> str:
        """Format search results into a readable string for LLM context."""
        if not results:
            return "No relevant past conversations found."
        
        formatted = "Relevant past conversations:\n\n"
        for i, msg in enumerate(results, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "unknown time")
            file = msg.get("file", "unknown session")
            
            formatted += f"{i}. [{timestamp}] {role}: {content}\n"
        
        return formatted

    def detect_memory_query(self, user_input: str) -> bool:
        """Detect if user is asking about past conversations."""
        memory_keywords = [
            "remember", "recall", "what did", "earlier", "before",
            "previous", "last time", "you said", "we talked about",
            "mentioned", "discussed", "conversation about"
        ]
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in memory_keywords)

    def search_and_format_memories(self, query: str, limit: int = 5) -> Optional[str]:
        """Search past conversations and format results for LLM context.
        
        Args:
            query: The search query (user's message)
            limit: Maximum number of results to return
            
        Returns:
            Formatted string of past conversations, or None if no results
        """
        # Extract key terms from the query (simple approach: use words longer than 3 chars)
        words = query.split()
        search_terms = [w.strip(".,!?") for w in words if len(w.strip(".,!?")) > 3]
        
        all_results = []
        for term in search_terms:
            results = self.search_past(term, limit=limit)
            for r in results:
                # Avoid duplicates
                if r not in all_results:
                    all_results.append(r)
            if len(all_results) >= limit:
                break
        
        if not all_results:
            return None
        
        return self.format_search_results_for_context(all_results[:limit])

__all__ = ["ContextManager"]
