"""Pivot specialization."""

from .base_agent import BaseAgent

class PivotAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__()
        self.name = "pivot"
