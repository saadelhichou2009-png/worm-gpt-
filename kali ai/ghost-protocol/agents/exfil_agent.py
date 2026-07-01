"""Exfil specialization."""

from .base_agent import BaseAgent

class ExfilAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__()
        self.name = "exfil"
