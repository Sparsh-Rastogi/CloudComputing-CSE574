"""Schedule and Placement data structures."""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Placement:
    task: int
    vm: int
    start: float
    finish: float
    is_dup: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "vm": self.vm,
            "start": round(self.start, 2),
            "finish": round(self.finish, 2),
            "is_dup": self.is_dup,
        }


@dataclass
class Schedule:
    placements: List[Placement]
    makespan: float
    cost: float
    energy: float
    utilization: float
    runtime_s: float = 0.0
    deadline_met: bool = True
    violation: float = 0.0

    def to_dict(self, include_placements: bool = True) -> Dict[str, Any]:
        res = {
            "makespan": round(self.makespan, 2),
            "cost": round(self.cost, 4),
            "energy": round(self.energy, 2),
            "utilization": round(self.utilization, 4),
            "runtime_s": round(self.runtime_s, 4),
            "deadline_met": self.deadline_met,
            "violation": round(self.violation, 2),
        }
        if include_placements:
            res["schedule"] = [p.to_dict() for p in self.placements]
        return res
