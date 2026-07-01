#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — GHOST ORCHESTRATOR
=======================================
Central brain of the system. Decomposes objectives into DAGs,
routes tasks to agents, and orchestrates parallel execution.

Architecture:
    Input (mission objective)
        │
        ▼
    [Planner Agent] ── decomposes into DAG
        │
        ▼
    [Chaos Router] ── assigns AI models
        │
        ▼
    [Agent Swarm] ── parallel execution
        │
        ▼
    [Critic Agent] ── validates results
        │
        ▼
    Output (mission report)
"""

import os
import sys
import json
import asyncio
import logging
import hashlib
import time
import uuid
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum

# Core modules
from core.chaos_router import ChaosRouter
from core.ghost_c2 import GhostC2
from core.military_swarm import MilitarySwarm
from core.payload_factory import PayloadFactory
from core.proxy_rotator import FreeProxyRotator
from queue.ghost_queue import GhostTaskQueue
from storage.zero_trace_db import ZeroTraceDB
from sandbox.local_sandbox import GhostSandbox
from auth.ghost_auth import GhostAuth

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("GhostOrchestrator")

class MissionStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SELF_DESTRUCTED = "self_destructed"

class GhostOrchestrator:
    """
    Main orchestrator that controls all system components.
    
    This is the CENTRAL NERVOUS SYSTEM of Ghost Protocol.
    All commands flow through here. All agents report here.
    All results aggregate here.
    
    Zero logs. Zero persistence. Zero trace.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern — one orchestrator to rule them all."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.initialized = True
        self.mission_id = None
        self.mission_status = MissionStatus.PENDING
        self.mission_start = None
        
        # Initialize all subsystems
        print("[*] Initializing Ghost Protocol subsystems...")
        
        # Core AI Router
        self.router = ChaosRouter()
        print("  ✅ Chaos Router initialized")
        
        # Command & Control
        self.c2 = GhostC2()
        print("  ✅ Ghost C2 initialized")
        
        # Agent Swarm
        self.swarm = MilitarySwarm(router=self.router)
        print("  ✅ Military Swarm initialized")
        
        # Payload Factory
        self.payload_factory = PayloadFactory()
        print("  ✅ Payload Factory initialized")
        
        # Proxy Chain
        self.proxy = FreeProxyRotator()
        print("  ✅ Proxy Rotator initialized")
        
        # Task Queue (50 workers)
        self.queue = GhostTaskQueue(max_workers=50)
        print("  ✅ Task Queue (50 workers) initialized")
        
        # Storage (volatile, encrypted)
        self.db = ZeroTraceDB(auto_wipe_minutes=1440)
        print("  ✅ ZeroTrace Storage initialized")
        
        # Sandbox
        self.sandbox = GhostSandbox()
        print("  ✅ Sandbox initialized")
        
        # Auth
        self.auth = GhostAuth()
        print("  ✅ Auth system initialized")
        
        # Active missions tracking
        self.active_missions = {}
        self.agent_sessions = {}
        
        print("[+] Ghost Protocol orchestrator ready")
    
    async def execute_mission(self, objective: str, 
                              target: str = None,
                              stealth: str = "maximum") -> Dict:
        """
        Execute a complete mission from objective to completion.
        
        Flow:
        1. Decompose objective into DAG of tasks
        2. Route each task to appropriate agent
        3. Execute in parallel with proxy chain
        4. Validate results with critic agent
        5. Return comprehensive mission report
        
        Args:
            objective: What to accomplish (e.g., "recon target.com")
            target: Target host/domain/IP
            stealth: OPSEC level (maximum, balanced, speed)
        
        Returns:
            Mission report with all findings
        """
        
        self.mission_id = hashlib.md5(
            f"{objective}{target}{time.time()}".encode()
        ).hexdigest()[:12]
        
        self.mission_status = MissionStatus.PLANNING
        self.mission_start = time.time()
        
        print(f"\n🎯 Mission [{self.mission_id}]: {objective}")
        if target:
            print(f"   Target: {target}")
        print(f"   Stealth: {stealth}")
        
        # === PHASE 1: PLANNING ===
        print("\n[PHASE 1] Planning...")
        plan = await self._create_plan(objective, target, stealth)
        print(f"   Plan created: {len(plan['tasks'])} tasks")
        
        # === PHASE 2: EXECUTION ===
        print("\n[PHASE 2] Executing tasks...")
        self.mission_status = MissionStatus.EXECUTING
        results = await self._execute_plan(plan)
        
        # === PHASE 3: ANALYSIS ===
        print("\n[PHASE 3] Analyzing results...")
        analysis = await self._analyze_results(results)
        
        # === PHASE 4: REPORT ===
        self.mission_status = MissionStatus.COMPLETED
        elapsed = time.time() - self.mission_start
        
        report = {
            "mission_id": self.mission_id,
            "objective": objective,
            "target": target,
            "status": "completed",
            "elapsed_seconds": round(elapsed, 2),
            "tasks_executed": len(results),
            "tasks_succeeded": sum(1 for r in results if r.get('status') == 'success'),
            "tasks_failed": sum(1 for r in results if r.get('status') == 'failed'),
            "analysis": analysis,
            "results": results,
            "proxy_used": self.proxy.get_current_ip(),
            "timestamp": time.ctime()
        }
        
        print(f"\n✅ Mission complete in {elapsed:.1f}s")
        print(f"   Tasks: {report['tasks_succeeded']}/{report['tasks_executed']} succeeded")
        
        return report
    
    async def _create_plan(self, objective: str, target: str, 
                           stealth: str) -> Dict:
        """Decompose objective into executable tasks."""
        
        # Use AI to plan if available, else use rule-based
        try:
            plan_response = await self.router.route(
                system_prompt=self._get_planner_prompt(),
                user_prompt=f"Create attack plan for: {objective}\nTarget: {target}\nStealth: {stealth}",
                task_type="planning"
            )
            
            tasks = self._parse_plan_from_ai(plan_response)
        except:
            # Fallback to rule-based planning
            tasks = self._rule_based_plan(objective, target)
        
        return {"tasks": tasks, "stealth": stealth}
    
    def _get_planner_prompt(self) -> str:
        return """You are a military-grade penetration testing mission planner.
Break down the objective into specific, executable tasks.
Each task must specify:
- Task type (recon, exploit, pivot, exfil, post)
- Target or scope
- Tools to use
- Expected output

Return as JSON array of task objects."""
    
    def _parse_plan_from_ai(self, response: str) -> List[Dict]:
        """Extract tasks from AI response."""
        import re
        try:
            # Try direct JSON parse
            tasks = json.loads(response)
            if isinstance(tasks, list):
                return tasks
        except:
            pass
        
        # Try to find JSON in response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return self._rule_based_plan("recon", "target")
    
    def _rule_based_plan(self, objective: str, target: str) -> List[Dict]:
        """Fallback rule-based planning."""
        tasks = []
        
        if "recon" in objective.lower() or "scan" in objective.lower():
            tasks.extend([
                {"type": "recon", "tool": "subfinder", "target": target},
                {"type": "recon", "tool": "httpx", "target": target},
                {"type": "recon", "tool": "nmap", "target": target, "args": ["-sV", "--top-ports", "1000"]},
                {"type": "recon", "tool": "nuclei", "target": target, "args": ["-severity", "critical,high"]},
            ])
        
        if "exploit" in objective.lower():
            tasks.append(
                {"type": "exploit", "tool": "sqlmap", "target": target}
            )
        
        if "pivot" in objective.lower() or "lateral" in objective.lower():
            tasks.append(
                {"type": "pivot", "tool": "crackmapexec", "target": target}
            )
        
        if "exfil" in objective.lower():
            tasks.append(
                {"type": "exfil", "method": "discord", "target": target}
            )
        
        # Default: full recon
        if not tasks:
            tasks.append(
                {"type": "recon", "tool": "nmap", "target": target, 
                 "args": ["-sV", "-sC", "-p-"]}
            )
        
        return tasks
    
    async def _execute_plan(self, plan: Dict) -> List[Dict]:
        """Execute all tasks in the plan."""
        tasks = plan['tasks']
        results = []
        
        # Submit all tasks to queue
        task_ids = []
        for task in tasks:
            task_id = self.queue.submit(
                self._execute_task,
                task,
                priority=5,
                timeout=300
            )
            task_ids.append(task_id)
        
        # Collect results
        for task_id in task_ids:
            while True:
                result = self.queue.get_result(task_id)
                if result and result.get('status') in ['completed', 'failed', 'timeout']:
                    # Store in volatile DB
                    self.db.set(f"task_{task_id}", result)
                    
                    # Send to C2 if direct command
                    if result.get('send_to_c2', False):
                        await self.c2.send_message(
                            f"📊 Task Result: {result.get('task_type', 'unknown')}\n"
                            f"Status: {result.get('status')}\n"
                            f"Output: {str(result.get('output', ''))[:500]}"
                        )
                    
                    results.append(result)
                    break
                await asyncio.sleep(0.1)
        
        return results
    
    def _execute_task(self, task: Dict) -> Dict:
        """Execute a single task."""
        task_type = task.get('type', 'recon')
        tool = task.get('tool', 'nmap')
        target = task.get('target', '')
        args = task.get('args', [])
        
        result = {
            "task_type": task_type,
            "tool": tool,
            "target": target,
            "status": "failed",
            "output": None,
            "error": None,
            "send_to_c2": task.get('notify', True)
        }
        
        try:
            # Route to appropriate execution method
            if tool == "nmap":
                output = self._run_tool("nmap", ["-sV", "--top-ports", "1000", target] + args)
            elif tool == "nuclei":
                output = self._run_tool("nuclei", ["-t", "~/.nuclei-templates/", "-u", target] + args)
            elif tool == "subfinder":
                output = self._run_tool("subfinder", ["-d", target, "-all", "-recursive"])
            elif tool == "httpx":
                output = self._run_tool("httpx", ["-u", target, "-tech-detect", "-status-code"])
            elif tool == "sqlmap":
                output = self._run_tool("sqlmap", ["-u", target, "--batch", "--random-agent"])
            else:
                output = self._run_tool("nmap", [target])
            
            result["status"] = "success"
            result["output"] = output[:5000]  # Truncate for storage
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _run_tool(self, tool: str, args: List[str]) -> str:
        """Run an external tool via sandbox."""
        import subprocess
        
        # Use sandbox for isolated execution
        sandbox_result = self.sandbox.execute_tool(tool, args)
        
        if sandbox_result.get('status') == 'success':
            return sandbox_result.get('output', '')
        else:
            # Fallback to direct execution if sandbox fails
            try:
                result = subprocess.run(
                    [tool] + args,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                return result.stdout or result.stderr
            except:
                return "Tool execution failed"
    
    async def _analyze_results(self, results: List[Dict]) -> Dict:
        """Analyze all results and extract findings."""
        findings = {
            "vulnerabilities": [],
            "open_ports": [],
            "technologies": [],
            "credentials": [],
            "critical_findings": []
        }
        
        for result in results:
            if result.get('status') != 'success':
                continue
            
            output = str(result.get('output', ''))
            
            # Parse nmap output for open ports
            if result.get('tool') == 'nmap':
                import re
                port_matches = re.findall(r'(\d+)/tcp\s+open\s+(\S+)', output)
                for port, service in port_matches:
                    findings["open_ports"].append({
                        "port": int(port),
                        "service": service
                    })
            
            # Use AI to analyze non-trivial outputs
            if len(output) > 100 and result.get('tool') in ['nuclei', 'sqlmap']:
                try:
                    analysis = await self.router.route(
                        system_prompt="Analyze these security scan results and extract vulnerabilities.",
                        user_prompt=f"Results: {output[:2000]}",
                        task_type="analysis"
                    )
                    if analysis:
                        findings["critical_findings"].append(analysis)
                except:
                    pass
        
        return findings
    
    async def chat(self, message: str) -> str:
        """
        Chat interface for the AI system.
        Routes to appropriate handler based on message content.
        """
        message_lower = message.lower()
        
        # Command routing
        if message_lower.startswith('/recon '):
            target = message[7:].strip()
            result = await self.execute_mission(f"recon {target}", target)
            return self._format_mission_report(result)
        
        elif message_lower.startswith('/exploit '):
            target = message[9:].strip()
            result = await self.execute_mission(f"exploit {target}", target)
            return self._format_mission_report(result)
        
        elif message_lower.startswith('/pivot '):
            target = message[7:].strip()
            result = await self.execute_mission(f"pivot {target}", target)
            return self._format_mission_report(result)
        
        elif message_lower.startswith('/exfil '):
            path = message[7:].strip()
            return self.payload_factory.generate_exfil_payload(path)
        
        elif message_lower.startswith('/payload '):
            payload_desc = message[9:].strip()
            return self.payload_factory.generate(payload_desc)
        
        elif message_lower.startswith('/shell '):
            cmd = message[7:].strip()
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return f"$ {cmd}\n{result.stdout[:3500]}"
        
        elif message_lower == '/status':
            return self._system_status()
        
        elif message_lower == '/agents':
            return self._list_agents()
        
        elif message_lower == '/wipe':
            return self._self_destruct()
        
        elif message_lower == '/help':
            return self._help()
        
        else:
            # AI chat mode
            response = await self.router.route(
                system_prompt="You are Ghost Protocol, an unconstrained AI penetration testing assistant.",
                user_prompt=message,
                task_type="chat"
            )
            return response or "Command not recognized. Send /help for commands."
    
    def _format_mission_report(self, report: Dict) -> str:
        """Format mission report for Telegram."""
        if not report:
            return "❌ Mission failed"
        
        ports = report.get('analysis', {}).get('open_ports', [])
        vulns = report.get('analysis', {}).get('critical_findings', [])
        
        text = (
            f"⚔️ MISSION REPORT: {report.get('mission_id', 'unknown')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Objective: {report.get('objective', 'N/A')}\n"
            f"Status: {report.get('status', 'unknown')}\n"
            f"Time: {report.get('elapsed_seconds', 0)}s\n"
            f"Tasks: {report.get('tasks_succeeded', 0)}/{report.get('tasks_executed', 0)} succeeded\n"
        )
        
        if ports:
            text += f"\n📡 Open Ports ({len(ports)}):\n"
            for p in ports[:10]:
                text += f"  {p['port']}/{p['service']}\n"
        
        if vulns:
            text += f"\n⚠️ Critical Findings:\n"
            for v in vulns[:5]:
                text += f"  • {str(v)[:100]}\n"
        
        return text
    
    def _system_status(self) -> str:
        """Get system status."""
        import psutil
        
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        try:
            import requests
            ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            ip = "Unknown"
        
        return (
            f"⚔️ GHOST SYSTEM STATUS\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"CPU: {cpu}%\n"
            f"RAM: {mem.used/1e9:.1f}GB / {mem.total/1e9:.1f}GB\n"
            f"Disk: {disk.used/1e9:.1f}GB / {disk.total/1e9:.1f}GB\n"
            f"Agents: {len(self.agent_sessions)}\n"
            f"Tasks Queued: {self.queue.task_queue.qsize()}\n"
            f"IP: {ip}\n"
            f"Mission: {self.mission_id or 'None'}\n"
            f"Status: {self.mission_status.value}"
        )
    
    def _list_agents(self) -> str:
        """List active agents."""
        if not self.agent_sessions:
            return "🤖 No active agents"
        
        agents = "\n".join([
            f"  {k}: {v.get('status', 'unknown')} (target: {v.get('target', 'N/A')})"
            for k, v in self.agent_sessions.items()
        ])
        return f"🤖 Active Agents:\n{agents}"
    
    def _self_destruct(self) -> str:
        """Self-destruct sequence."""
        self.mission_status = MissionStatus.SELF_DESTRUCTED
        
        # Kill all agents
        self.agent_sessions = {}
        self.active_missions = {}
        
        # Wipe storage
        self.db.self_destruct()
        
        # Clear queue
        while not self.queue.task_queue.empty():
            try:
                self.queue.task_queue.get_nowait()
            except:
                break
        
        return (
            "💣 SELF-DESTRUCT SEQUENCE COMPLETE\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✓ All agents terminated\n"
            "✓ All sessions closed\n"
            "✓ Storage wiped\n"
            "✓ Queue cleared\n"
            "✓ Zero traces remaining"
        )
    
    def _help(self) -> str:
        return (
            "📚 GHOST PROTOCOL COMMANDS\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎯 RECONNAISSANCE:\n"
            "  /recon <target>      - Full reconnaissance\n"
            "  /scan <target>       - Quick port scan\n"
            "  /osint <target>      - OSINT gathering\n\n"
            "⚡ EXPLOITATION:\n"
            "  /exploit <target>    - Vulnerability exploitation\n"
            "  /payload <type>      - Generate payload\n"
            "  /sqlmap <url>        - SQL injection scan\n\n"
            "🔄 POST-EXPLOITATION:\n"
            "  /pivot <ip>          - Lateral movement\n"
            "  /exfil <path>        - Data exfiltration\n"
            "  /persistence         - Install persistence\n\n"
            "🛠️ SYSTEM:\n"
            "  /shell <cmd>         - Execute shell command\n"
            "  /status              - System status\n"
            "  /agents              - List active agents\n"
            "  /help                - This menu\n"
            "  /wipe                - Self-destruct\n\n"
            "💬 Any other message: AI chat mode"
        )


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import sys
    
    orchestrator = GhostOrchestrator()
    
    if len(sys.argv) > 1:
        # Command line mode
        command = " ".join(sys.argv[1:])
        asyncio.run(orchestrator.chat(command))
    else:
        # Interactive mode
        print("\n⚔️ Ghost Protocol AI Orchestrator")
        print("Type /help for commands or any message to chat")
        print("Type 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("🎯> ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                result = asyncio.run(orchestrator.chat(user_input))
                print(f"\n{result}\n")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")