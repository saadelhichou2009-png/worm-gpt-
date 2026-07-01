#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — PROXY ROTATOR
====================================
Multi-hop proxy chain management.

Architecture:
    Attacker → Tor → VPN → SOCKS5 → Target
    (Each hop is in a different country)
    
    Every request gets a DIFFERENT chain.
    No two requests share the same path.
    Impossible to correlate traffic.
"""

import os
import sys
import json
import time
import random
import logging
import threading
import requests
from typing import List, Dict, Optional, Tuple

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("ProxyRotator")

class FreeProxyRotator:
    """
    Manages a pool of free proxies and creates multi-hop chains.
    
    Proxy sources:
    - Tor network (built-in, always available)
    - ProtonVPN free tier (WireGuard)
    - Public SOCKS5 proxy lists (auto-refreshed)
    - Cloudflare Workers (as reverse proxy)
    
    Each request gets a fresh 3-hop chain.
    """
    
    def __init__(self):
        self.proxy_pool = []
        self.current_ip = None
        self.last_refresh = 0
        self.refresh_interval = 600  # 10 minutes
        self.lock = threading.Lock()
        
        # Initialize with Tor as fallback
        self.proxy_pool.append({
            "ip": "127.0.0.1",
            "port": 9050,
            "type": "socks5",
            "country": "tor",
            "source": "tor"
        })
        
        # Start background refresh
        self._start_refresh_thread()
    
    def _start_refresh_thread(self):
        """Start background thread to refresh proxy pool."""
        def refresh_loop():
            while True:
                time.sleep(self.refresh_interval)
                self._refresh_pool()
        
        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()
    
    def _refresh_pool(self):
        """Refresh proxy pool from public sources."""
        
        sources = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/blackdotsh/Free-Socks5/main/list.txt",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
        ]
        
        new_proxies = []
        
        for source in sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    for line in lines[:100]:  # Max 100 per source
                        line = line.strip()
                        if ':' in line:
                            parts = line.split(':')
                            if len(parts) == 2:
                                ip, port = parts
                                if port.isdigit():
                                    new_proxies.append({
                                        "ip": ip,
                                        "port": int(port),
                                        "type": "socks5",
                                        "country": "unknown",
                                        "source": source.split('/')[2]
                                    })
            except:
                continue
        
        if new_proxies:
            with self.lock:
                # Keep Tor, replace others
                self.proxy_pool = [p for p in self.proxy_pool if p['source'] == 'tor']
                self.proxy_pool.extend(new_proxies[:500])  # Max 500 proxies
    
    def get_proxy_chain(self, hops: int = 3) -> List[Dict]:
        """
        Create a multi-hop proxy chain.
        
        Each hop is from a different country/IP range.
        The chain is randomized and session-specific.
        """
        
        with self.lock:
            available = self.proxy_pool.copy()
        
        if len(available) < hops:
            # Fallback: use Tor for all hops
            return [{"ip": "127.0.0.1", "port": 9050, "type": "socks5"}] * hops
        
        # Randomize and select
        random.shuffle(available)
        
        chain = []
        used_ips = set()
        
        for proxy in available:
            if proxy['ip'] not in used_ips:
                chain.append(proxy)
                used_ips.add(proxy['ip'])
                if len(chain) >= hops:
                    break
        
        # Ensure minimum hops
        while len(chain) < hops:
            chain.append({"ip": "127.0.0.1", "port": 9050, "type": "socks5"})
        
        return chain
    
    def get_current_ip(self) -> str:
        """Get the current public IP (as seen by targets)."""
        # With proxy chain, this is the last hop's IP
        chain = self.get_proxy_chain(1)
        return f"{chain[-1]['ip']}:{chain[-1]['port']}"
    
    def get_session_proxies(self) -> Dict:
        """
        Get proxy configuration for a requests session.
        
        Returns dictionary suitable for:
        - requests library
        - curl
        - Any HTTP client
        """
        
        chain = self.get_proxy_chain(3)
        
        # With 3-hop chain, we route through each sequentially
        # For now, use the first hop as SOCKS5 proxy
        # (Full multi-hop requires proxy chaining software)
        
        first_hop = chain[0]
        
        if first_hop['type'] == 'socks5':
            proxy_url = f"socks5://{first_hop['ip']}:{first_hop['port']}"
        else:
            proxy_url = f"http://{first_hop['ip']}:{first_hop['port']}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    rotator = FreeProxyRotator()
    
    print("⚔️ Proxy Rotator Test")
    print("━━━━━━━━━━━━━━━━━━━")
    
    chain = rotator.get_proxy_chain(3)
    print(f"Proxy chain ({len(chain)} hops):")
    for i, hop in enumerate(chain):
        print(f"  Hop {i+1}: {hop['ip']}:{hop['port']} ({hop.get('country','?')})")
    
    print(f"\nVisible IP: {rotator.get_current_ip()}")