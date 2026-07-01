"""Recon specialization."""

from .base_agent import BaseAgent

class ReconAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__()
        self.name = "recon"
