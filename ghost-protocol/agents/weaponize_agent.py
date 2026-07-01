"""Weaponize specialization."""

from .base_agent import BaseAgent

class WeaponizeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__()
        self.name = "weaponize"
