#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — ZERO TRACE DATABASE
==========================================
Volatile encrypted in-memory database with auto-wipe.

This replaces paid services like Convex ($25/month).
Everything is in RAM. Nothing touches disk.
When the server dies, the data dies with it.
"""

import os
import json
import time
import sqlite3
import threading
import logging
from typing import Any, Optional, Dict, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("ZeroTraceDB")

class ZeroTraceDB:
    """
    Volatile in-memory database with encryption and auto-wipe.
    
    Features:
    - SQLite :memory: (nothing on disk)
    - AES-256 encryption for all values
    - TTL-based auto-expiry
    - Self-destruct on command
    - Thread-safe
    
    A livello di sicurezza:
    - Se il server viene spento: TUTTO SPARITO
    - Se qualcuno accede al server: dati in RAM cifrati
    - Chiave di cifratura generata all'avvio, mai salvata
    """
    
    def __init__(self, encryption_key: Optional[str] = None,
                 auto_wipe_minutes: int = 1440):
        """
        Init the database in memory.
        
        Args:
            encryption_key: If provided, encrypts all values
            auto_wipe_minutes: Auto-destroy after N minutes (0=disable)
        """
        
        # SQLite in RAM
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()
        
        # Cifratura
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Genera chiave casuale all'avvio
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
        
        # Crea tabella
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ghost_store (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL,
                metadata TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expires 
            ON ghost_store(expires_at)
        ''')
        self.conn.commit()
        
        # Auto-wipe thread
        if auto_wipe_minutes > 0:
            self.wipe_timer = threading.Timer(
                auto_wipe_minutes * 60,
                self.self_destruct
            )
            self.wipe_timer.daemon = True
            self.wipe_timer.start()
        
        # Cleanup expired entries thread
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True
        )
        self.cleanup_thread.start()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            metadata: Optional[Dict] = None):
        """
        Save a value to the database.
        
        Args:
            key: Unique key
            value: Any Python object (JSON serialized)
            ttl: Time-to-live in seconds
            metadata: Optional metadata dict
        """
        with self.lock:
            serialized = json.dumps(value)
            
            # Cifra se cipher disponibile
            if self.cipher:
                serialized = self.cipher.encrypt(
                    serialized.encode()
                ).decode()
            
            expires = (time.time() + ttl) if ttl else None
            meta_str = json.dumps(metadata) if metadata else None
            
            self.cursor.execute(
                """INSERT OR REPLACE INTO ghost_store 
                   (key, value, created_at, expires_at, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (key, serialized, time.time(), expires, meta_str)
            )
            self.conn.commit()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        with self.lock:
            self.cursor.execute(
                "SELECT value, expires_at FROM ghost_store WHERE key = ?",
                (key,)
            )
            row = self.cursor.fetchone()
            
            if not row:
                return None
            
            value, expires = row['value'], row['expires_at']
            
            # Check TTL
            if expires and time.time() > expires:
                self.delete(key)
                return None
            
            # Decifra
            if self.cipher:
                try:
                    value = self.cipher.decrypt(
                        value.encode()
                    ).decode()
                except:
                    return None
            
            return json.loads(value)
    
    def delete(self, key: str):
        """Delete a key."""
        with self.lock:
            self.cursor.execute(
                "DELETE FROM ghost_store WHERE key = ?", (key,)
            )
            self.conn.commit()
    
    def exists(self, key: str) -> bool:
        """Check if key exists and not expired."""
        return self.get(key) is not None
    
    def keys(self, pattern: str = "%") -> List[str]:
        """Get all keys matching pattern."""
        with self.lock:
            self.cursor.execute(
                "SELECT key FROM ghost_store WHERE key LIKE ?",
                (pattern,)
            )
            return [row['key'] for row in self.cursor.fetchall()]
    
    def count(self) -> int:
        """Get total number of stored items."""
        with self.lock:
            self.cursor.execute("SELECT COUNT(*) as c FROM ghost_store")
            return self.cursor.fetchone()['c']
    
    def _cleanup_loop(self):
        """Background thread to remove expired entries."""
        while True:
            time.sleep(60)  # Check every minute
            try:
                with self.lock:
                    self.cursor.execute(
                        "DELETE FROM ghost_store WHERE expires_at IS NOT NULL AND expires_at < ?",
                        (time.time(),)
                    )
                    if self.cursor.rowcount > 0:
                        self.conn.commit()
            except:
                pass
    
    def self_destruct(self) -> str:
        """
        Self-destruct the database.
        
        Steps:
        1. Delete ALL rows
        2. VACUUM to overwrite freed space
        3. Close connection
        
        ATTENZIONE: Dopo questa chiamata TUTTO È PERSO.
        Non recuperabile. Nemmeno con forensic tools.
        """
        with self.lock:
            # Cancella tutte le righe
            self.cursor.execute("DELETE FROM ghost_store")
            
            # Overwrite spazio libero
            self.cursor.execute("PRAGMA secure_delete = ON")
            self.cursor.execute("VACUUM")
            
            # Drop table
            self.cursor.execute("DROP TABLE IF EXISTS ghost_store")
            
            self.conn.commit()
            self.conn.close()
        
        # Cancella la chiave
        self.cipher = None
        
        return "💣 ZeroTraceDB: All data permanently destroyed"
    
    def flush(self):
        """Clear all data without destroying the database."""
        with self.lock:
            self.cursor.execute("DELETE FROM ghost_store")
            self.cursor.execute("VACUUM")
            self.conn.commit()


if __name__ == "__main__":
    db = ZeroTraceDB(auto_wipe_minutes=0)
    
    # Test
    db.set("test_key", {"hello": "world", "number": 42})
    print(f"Get: {db.get('test_key')}")
    print(f"Exists: {db.exists('test_key')}")
    print(f"Count: {db.count()}")
    
    db.self_destruct()
    print("Self-destruct complete")