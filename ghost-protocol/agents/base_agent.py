#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — BASE AGENT
=================================
Abstract base class for all swarm agents.
"""

import os
import json
import time
import logging
import subprocess
from typing import Dict, List, Optional, Any
from enum import Enum

logging.basicConfig(level=logging.CRITICAL)

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
    Base class for all agents.
    
    Each agent has:
    - A type (role)
    - Tools it can use
    - AI model for reasoning
    - State machine
    - Command execution capability
    """
    
    def __init__(self, agent_type: AgentType, router,
                 tools: List[str] = None,
                 system_prompt: str = ""):
        self.agent_type = agent_type
        self.router = router
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.state = AgentState.IDLE
        self.memory = []
        self.session_id = None
        self.last_result = None
    
    async def think(self, context: str) -> str:
        """Use AI to reason about current situation."""
        self.state = AgentState.THINKING
        
        prompt = self.system_prompt or f"You are a {self.agent_type.value} specialist."
        full_prompt = f"{context}"
        
        try:
            response = await self.router.route(
                system_prompt=prompt,
                user_prompt=full_prompt,
                task_type=self.agent_type.value
            )
            self.memory.append({"role": "thought", "content": response})
            return response
        except:
            return ""
    
    async def act(self, objective: str) -> Dict:
        """Execute action based on objective."""
        self.state = AgentState.EXECUTING
        
        # Think first
        thought = await self.think(objective)
        
        # Extract and execute commands
        commands = self._extract_commands(thought)
        results = []
        
        for cmd in commands[:3]:
            try:
                r = subprocess.run(
                    cmd, shell=True, capture_output=True,
                    text=True, timeout=120
                )
                results.append({
                    "command": cmd,
                    "status": "success" if r.returncode == 0 else "error",
                    "output": r.stdout[:1000]
                })
            except Exception as e:
                results.append({"command": cmd, "status": "failed", "error": str(e)})
        
        self.state = AgentState.COMPLETED
        self.last_result = {
            "agent": self.agent_type.value,
            "thought": thought,
            "actions": results
        }
        
        return self.last_result
    
    def _extract_commands(self, text: str) -> List[str]:
        """Extract shell commands from AI text."""
        import re
        commands = []
        
        code_blocks = re.findall(r'```(?:bash|shell)?\n(.*?)```', text, re.DOTALL)
        for block in code_blocks:
            for line in block.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('$'):
                    commands.append(line)
        
        return commands