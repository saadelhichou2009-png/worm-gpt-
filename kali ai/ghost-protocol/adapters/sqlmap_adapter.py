#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — SQLMAP ADAPTER
=====================================
SQL injection automation adapter.
"""

import os
import json
import subprocess
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.CRITICAL)

class SQLMapAdapter:
    """
    SQLMap automation adapter.
    
    Executes sqlmap with sensible defaults for automated testing.
    """
    
    @staticmethod
    def scan(url: str, data: Optional[str] = None,
             method: str = "GET", level: int = 3,
             risk: int = 2) -> Dict:
        """
        Execute SQL injection scan on target URL.
        
        Args:
            url: Target URL with injection point
            data: POST data if applicable
            method: HTTP method (GET/POST)
            level: Test level (1-5, higher = more thorough)
            risk: Risk level (1-3, higher = more dangerous)
        
        Returns:
            Scan results
        """
        
        cmd = [
            "sqlmap", "-u", url,
            "--batch",
            "--random-agent",
            f"--level={level}",
            f"--risk={risk}",
            "--threads=10",
            "--time-sec=15",
            "--output-dir=/tmp/sqlmap_results"
        ]
        
        if data:
            cmd.extend(["--data", data])
        
        if method == "POST":
            cmd.append("--method=POST")
        
        result = {"status": "started", "findings": []}
        
        try:
            output = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600
            )
            
            stdout = output.stdout.lower()
            
            # Parse results
            if "sqlmap identified the following injection" in stdout:
                result["status"] = "vulnerable"
                result["findings"].append({
                    "type": "sql_injection",
                    "detail": "SQL injection confirmed"
                })
            elif "all tested parameters appear to be not injectable" in stdout:
                result["status"] = "not_vulnerable"
            else:
                result["status"] = "completed"
            
            result["raw_output"] = output.stdout[:2000]
            
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "http://testphp.vulnweb.com/artists.php?artist=1"
    
    print(f"Testing {url}...")
    result = SQLMapAdapter.scan(url)
    print(f"Status: {result['status']}")