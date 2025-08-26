import sqlite3
import time
import json
from typing import List, Dict, Any

class MemoryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database with memories table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    ts REAL NOT NULL,
                    tags TEXT
                )
            """)
            conn.commit()
    
    def add_memory(self, user_id: str, text: str, tags: List[str] = None):
        """Add a memory for a user"""
        if tags is None:
            tags = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memories (user_id, text, ts, tags) VALUES (?, ?, ?, ?)",
                (user_id, text, time.time(), json.dumps(tags))
            )
            conn.commit()
    
    def recall_memories(self, user_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """Recall the k most recent memories for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT text, ts, tags FROM memories WHERE user_id = ? ORDER BY ts DESC LIMIT ?",
                (user_id, k)
            )
            rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            text, ts, tags_json = row
            try:
                tags = json.loads(tags_json) if tags_json else []
            except json.JSONDecodeError:
                tags = []
            
            memories.append({
                "text": text,
                "ts": ts,
                "score": 0.7,  # Dummy score as requested
                "tags": tags
            })
        
        return memories
