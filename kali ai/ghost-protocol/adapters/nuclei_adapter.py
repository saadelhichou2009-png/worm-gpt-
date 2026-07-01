#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — NUCLEI ADAPTER
=====================================
Vulnerability scanning with Nuclei.
"""

import os
import json
import subprocess
import logging
from typing import Dict, List

logging.basicConfig(level=logging.CRITICAL)

class NucleiAdapter:
    """
    Nuclei vulnerability scanner adapter.
    Updates templates automatically.
    """
    
    @staticmethod
    def update_templates():
        """Update nuclei templates."""
        subprocess.run(["nuclei", "-update-templates"], 
                      capture_output=True, timeout=60)
    
    @staticmethod
    def scan(target: str, severity: str = "critical,high",
             tags: str = "") -> Dict:
        """
        Scan target with nuclei.
        
        Args:
            target: URL or IP
            severity: Comma-separated severity levels
            tags: Optional template tags to filter
        
        Returns:
            Scan results grouped by severity
        """
        
        cmd = ["nuclei", "-u", target, "-severity", severity,
               "-json", "-silent"]
        
        if tags:
            cmd.extend(["-tags", tags])
        
        result = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": [],
            "total": 0
        }
        
        try:
            output = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )
            
            for line in output.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    finding = json.loads(line)
                    sev = finding.get('info', {}).get('severity', 'info').lower()
                    if sev in result:
                        result[sev].append(finding)
                except json.JSONDecodeError:
                    pass
            
            result["total"] = sum(len(v) for v in result.values())
            
        except subprocess.TimeoutExpired:
            result["error"] = "Nuclei scan timed out"
        except Exception as e:
            result["error"] = str(e)
        
        return result


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    
    print(f"Scanning {target}...")
    results = NucleiAdapter.scan(target)
    
    print(f"Findings: {results['total']}")
    for sev in ["critical", "high", "medium"]:
        if results[sev]:
            print(f"  {sev.upper()}: {len(results[sev])}")