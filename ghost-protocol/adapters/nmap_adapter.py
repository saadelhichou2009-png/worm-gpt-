#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — NMAP ADAPTER
===================================
Wraps nmap with proxy support and result parsing.
"""

import os
import json
import subprocess
import re
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("NmapAdapter")

class NmapAdapter:
    """
    Nmap wrapper with result parsing and proxy support.
    """
    
    @staticmethod
    def scan(target: str, ports: str = "--top-ports 1000",
             flags: str = "-sV -T4") -> Dict:
        """
        Execute nmap scan with parsing.
        
        Args:
            target: IP or hostname
            ports: Port specification (e.g., "--top-ports 1000", "-p 80,443")
            flags: Additional nmap flags
        
        Returns:
            Parsed scan results
        """
        
        cmd = f"nmap {flags} {ports} {target}"
        
        try:
            result = subprocess.run(
                cmd.split(), capture_output=True, text=True, timeout=300
            )
            output = result.stdout
        except Exception as e:
            return {"error": str(e), "status": "failed"}
        
        # Parse results
        parsed = NmapAdapter.parse(output)
        parsed["command"] = cmd
        parsed["target"] = target
        
        return parsed
    
    @staticmethod
    def parse(output: str) -> Dict:
        """Parse nmap output into structured format."""
        
        result = {
            "status": "completed",
            "hosts": [],
            "open_ports": [],
            "services": []
        }
        
        # Extract host status
        host_match = re.search(r'Nmap scan report for (.+)', output)
        if host_match:
            result["hosts"].append(host_match.group(1))
        
        # Extract open ports
        port_pattern = r'(\d+)/tcp\s+open\s+(\S+)\s+(.+)'
        for match in re.finditer(port_pattern, output):
            port_info = {
                "port": int(match.group(1)),
                "protocol": "tcp",
                "service": match.group(2),
                "version": match.group(3).strip()
            }
            result["open_ports"].append(port_info)
            result["services"].append(match.group(2))
        
        # Extract OS info
        os_match = re.search(r'OS details: (.+)', output)
        if os_match:
            result["os"] = os_match.group(1).strip()
        
        # Extract hop count
        hop_match = re.search(r'Device type: (.+)', output)
        if hop_match:
            result["device_type"] = hop_match.group(1).strip()
        
        return result

    @staticmethod
    def quick_scan(target: str) -> Dict:
        """Quick scan of top 100 ports."""
        return NmapAdapter.scan(target, "--top-ports 100", "-sV -T4 --min-rate 2000")
    
    @staticmethod
    def full_scan(target: str) -> Dict:
        """Full scan of all ports (may take long)."""
        return NmapAdapter.scan(target, "-p-", "-sV -sC -T4")
    
    @staticmethod
    def service_scan(target: str, ports: str = "-p 80,443,22,3306,8080") -> Dict:
        """Targeted service version scan."""
        return NmapAdapter.scan(target, ports, "-sV --version-intensity 9")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "scanme.nmap.org"
    
    print(f"Scanning {target}...")
    result = NmapAdapter.quick_scan(target)
    
    print(f"Open ports: {len(result.get('open_ports', []))}")
    for port in result.get('open_ports', [])[:10]:
        print(f"  {port['port']}/tcp - {port['service']} {port['version']}")