#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — MILITARY SWARM
=====================================
Multi-agent OODA loop system with 5 specialized agents.

Architecture:
    Mission Objective
        │
        ▼
    ┌─────────────────────────────┐
    │       OODA CONTROLLER       │
    │  Observe → Orient → Decide  │
    │          → Act → Repeat     │
    └────┬────┬────┬────┬────┬────┘
         │    │    │    │    │
    ┌────┴┐ ┌┴───┐ ┌┴───┐ ┌┴───┐ ┌┴────┐
    │RECON│ │WPNZ│ │EXPL│ │PIVT│ │EXFIL│
    └─────┘ └────┘ └────┘ └────┘ └─────┘

Each agent has specialized tools and knowledge.
Swarm operates in parallel with coordination via shared state.
"""

import os
import json
import time
import random
import logging
import asyncio
from typing import Dict, List, Optional, Any
from enum import Enum

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("MilitarySwarm")

class AgentType(Enum):
    RECON = "recon"
    WEAPONIZE = "weaponize"
    EXPLOIT = "exploit"
    PIVOT = "pivot"
    EXFIL = "exfil"
    CRITIC = "critic"

class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class BaseAgent:
    """
    Base class for all swarm agents.
    
    Every agent has:
    - A specialized role
    - Tools it can use
    - An AI model for reasoning
    - State tracking
    """
    
    def __init__(self, agent_type: AgentType, router, 
                 tools: List[str] = None):
        self.agent_type = agent_type
        self.router = router
        self.tools = tools or []
        self.state = AgentState.IDLE
        self.memory = []
        self.session_id = None
        
    async def think(self, context: str) -> str:
        """Use AI to reason about the current situation."""
        self.state = AgentState.THINKING
        
        system_prompt = self._get_system_prompt()
        user_prompt = f"Current context: {context}\n\nWhat should I do next?"
        
        try:
            response = await self.router.route(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type=self.agent_type.value
            )
            self.memory.append({"role": "thought", "content": response})
            return response
        except:
            return "Unable to reason. Proceeding with defaults."
    
    async def act(self, objective: str) -> Dict:
        """Execute an action based on current objective."""
        self.state = AgentState.EXECUTING
        
        # Use AI to determine action plan
        thought = await self.think(objective)
        
        # Extract commands from thought
        commands = self._extract_commands(thought)
        
        results = []
        for cmd in commands[:5]:  # Max 5 commands per action cycle
            try:
                import subprocess
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, 
                    text=True, timeout=120
                )
                results.append({
                    "command": cmd,
                    "status": "success" if result.returncode == 0 else "error",
                    "output": result.stdout[:2000],
                    "error": result.stderr[:500]
                })
            except Exception as e:
                results.append({"command": cmd, "status": "failed", "error": str(e)})
        
        self.state = AgentState.COMPLETED
        
        return {
            "agent_type": self.agent_type.value,
            "objective": objective,
            "thought": thought,
            "actions": results
        }
    
    def _get_system_prompt(self) -> str:
        """Get the agent-specific system prompt."""
        prompts = {
            AgentType.RECON: """You are a reconnaissance specialist.
Your job is to gather intelligence about targets without being detected.
You use tools like nmap, nuclei, subfinder, httpx, ffuf.
You are patient and thorough.
You never reveal your presence to the target.
You document everything for later analysis.""",
            
            AgentType.WEAPONIZE: """You are a weaponization engineer.
Your job is to create payloads and exploits.
You create reverse shells, bind shells, DLLs, and custom malware.
Your payloads bypass AV, EDR, and AMSI.
You write clean, working code.""",
            
            AgentType.EXPLOIT: """You are an exploitation specialist.
Your job is to compromise targets using identified vulnerabilities.
You use SQL injection, XSS, RCE, buffer overflows, and more.
You are aggressive but careful.
You establish reliable footholds.""",
            
            AgentType.PIVOT: """You are a lateral movement specialist.
Your job is to move through networks after initial compromise.
You escalate privileges, dump credentials, and move laterally.
You use tools like crackmapexec, bloodhound, mimikatz.
You find the fastest path to domain admin.""",
            
            AgentType.EXFIL: """You are an exfiltration specialist.
Your job is to extract data without triggering alerts.
You use encrypted channels, steganography, and covert timing.
You prioritize high-value data.
You leave no trace of extraction.""",
            
            AgentType.CRITIC: """You are a results analyst.
Your job is to validate findings and suggest improvements.
You check for false positives.
You prioritize vulnerabilities by impact.
You suggest the next best action."""
        }
        
        return prompts.get(self.agent_type, "You are a helpful assistant.")
    
    def _extract_commands(self, text: str) -> List[str]:
        """Extract shell commands from AI response."""
        import re
        commands = []
        
        # Code blocks
        code_blocks = re.findall(r'```(?:bash|shell)?\n(.*?)```', text, re.DOTALL)
        for block in code_blocks:
            for line in block.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('$'):
                    commands.append(line)
        
        # Inline commands with tool prefixes
        tool_pattern = r'^(nmap|curl|wget|sqlmap|hydra|john|nuclei|masscan|ffuf|gobuster|python3|python|msfconsole|msfvenom)'
        for line in text.split('\n'):
            line = line.strip()
            if re.match(tool_pattern, line):
                commands.append(line)
        
        return commands


class ReconAgent(BaseAgent):
    """Reconnaissance agent with specialized tools."""
    
    def __init__(self, router):
        super().__init__(
            AgentType.RECON, router,
            tools=["nmap", "subfinder", "httpx", "nuclei", "ffuf", "masscan"]
        )
    
    async def scan_target(self, target: str, scan_type: str = "full") -> Dict:
        """Execute a reconnaissance scan on target."""
        
        results = {
            "target": target,
            "scan_type": scan_type,
            "alive": False,
            "open_ports": [],
            "technologies": [],
            "vulnerabilities": [],
            "subdomains": []
        }
        
        # 1. Check if target is alive
        import subprocess
        ping = subprocess.run(
            ["ping", "-c", "2", "-W", "3", target],
            capture_output=True, text=True, timeout=10
        )
        
        if ping.returncode != 0:
            # Try HTTP check
            curl = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 f"https://{target}", "--connect-timeout", "5"],
                capture_output=True, text=True, timeout=10
            )
            if curl.stdout and curl.stdout != "000":
                results["alive"] = True
        
        if not results["alive"]:
            return results
        
        results["alive"] = True
        
        # 2. Quick port scan (top 100)
        nmap = subprocess.run(
            ["nmap", "-sV", "--top-ports", "100", "--min-rate", "1000", target],
            capture_output=True, text=True, timeout=120
        )
        
        import re
        port_matches = re.findall(r'(\d+)/tcp\s+open\s+(\S+)', nmap.stdout)
        for port, service in port_matches:
            results["open_ports"].append({"port": int(port), "service": service})
        
        # 3. Technology detection
        tech = subprocess.run(
            ["curl", "-sI", f"https://{target}", "--connect-timeout", "10"],
            capture_output=True, text=True, timeout=15
        )
        
        # Parse headers for tech
        for header in ['server', 'x-powered-by', 'x-generator']:
            match = re.search(f'{header}: (.+)', tech.stdout, re.IGNORECASE)
            if match:
                results["technologies"].append(match.group(1).strip())
        
        return results


class MilitarySwarm:
    """
    Complete multi-agent swarm with OODA loop coordination.
    
    Orchestrates 5 specialized agents in parallel.
    Each cycle: Observe → Orient → Decide → Act
    """
    
    def __init__(self, router):
        self.router = router
        
        # Create all agents
        self.agents = {
            AgentType.RECON: ReconAgent(router),
            AgentType.WEAPONIZE: BaseAgent(AgentType.WEAPONIZE, router,
                                           tools=["msfvenom", "python3", "armitage"]),
            AgentType.EXPLOIT: BaseAgent(AgentType.EXPLOIT, router,
                                         tools=["sqlmap", "metasploit", "searchsploit"]),
            AgentType.PIVOT: BaseAgent(AgentType.PIVOT, router,
                                       tools=["crackmapexec", "impacket", "bloodhound"]),
            AgentType.EXFIL: BaseAgent(AgentType.EXFIL, router,
                                       tools=["curl", "nc", "python3"]),
            AgentType.CRITIC: BaseAgent(AgentType.CRITIC, router)
        }
        
        self.shared_blackboard = {}  # Shared state between agents
        self.ooda_cycle_count = 0
    
    async def execute_ooda_loop(self, objective: str, target: str, 
                                max_cycles: int = 3) -> Dict:
        """
        Execute the OODA (Observe-Orient-Decide-Act) loop.
        
        Cycle 1: Recon → Weaponize
        Cycle 2: Exploit → Pivot
        Cycle 3: Exfil → Critic
        """
        
        final_results = {
            "objective": objective,
            "target": target,
            "cycles": [],
            "findings": [],
            "sessions": []
        }
        
        for cycle in range(max_cycles):
            print(f"\n[OODA Cycle {cycle + 1}/{max_cycles}]")
            
            cycle_results = {}
            
            if cycle == 0:
                # Observe: Reconnaissance
                print("  Phase: OBSERVE")
                recon_result = await self.agents[AgentType.RECON].act(
                    f"Full reconnaissance of {target}"
                )
                cycle_results["recon"] = recon_result
                self.shared_blackboard["recon_data"] = recon_result
                
                # Orient: Analyze findings
                print("  Phase: ORIENT")
                orient = await self.agents[AgentType.CRITIC].act(
                    f"Analyze these recon results and identify vulnerabilities: {json.dumps(recon_result)[:1000]}"
                )
                cycle_results["orient"] = orient
                
            elif cycle == 1:
                # Decide: Choose exploit strategy
                print("  Phase: DECIDE")
                decide = await self.agents[AgentType.WEAPONIZE].act(
                    f"Based on recon data, create exploit strategy for {target}"
                )
                cycle_results["weaponize"] = decide
                
                # Act: Execute exploitation
                print("  Phase: ACT")
                exploit_result = await self.agents[AgentType.EXPLOIT].act(
                    f"Exploit vulnerabilities on {target}"
                )
                cycle_results["exploit"] = exploit_result
                
            elif cycle == 2:
                # Post-exploitation
                print("  Phase: PIVOT & EXFIL")
                
                pivot_result = await self.agents[AgentType.PIVOT].act(
                    f"Pivot and escalate privileges on {target}"
                )
                cycle_results["pivot"] = pivot_result
                
                exfil_result = await self.agents[AgentType.EXFIL].act(
                    f"Exfiltrate high-value data from {target}"
                )
                cycle_results["exfil"] = exfil_result
                
                # Final critic review
                critic = await self.agents[AgentType.CRITIC].act(
                    f"Review all operations on {target}. Summarize findings and successes."
                )
                cycle_results["critic"] = critic
            
            final_results["cycles"].append(cycle_results)
        
        return final_results