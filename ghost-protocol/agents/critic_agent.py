"""Critic specialization."""

from .base_agent import BaseAgent

class CriticAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__()
        self.name = "critic"
