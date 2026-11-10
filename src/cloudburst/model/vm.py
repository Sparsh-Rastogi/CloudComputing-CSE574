"""VM model and catalog definitions."""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class VMType:
    type_id: int          # 0..3
    name: str             # "small", "medium", "large", "xlarge"
    speed: float          # relative speed (1.0, 2.0, 4.0, 8.0)
    price: float          # price per billing period ($0.10, $0.20, $0.40, $0.80)
    p_busy: float         # Watts (50, 90, 160, 300)
    p_idle: float         # Watts (30, 54, 96, 180)


def get_default_catalog() -> List[VMType]:
    """Returns the four standard VM types defined in README Section 12.1."""
    return [
        VMType(0, "small", 1.0, 0.10, 50.0, 30.0),
        VMType(1, "medium", 2.0, 0.20, 90.0, 54.0),
        VMType(2, "large", 4.0, 0.40, 160.0, 96.0),
        VMType(3, "xlarge", 8.0, 0.80, 300.0, 180.0),
    ]


@dataclass(frozen=True)
class VMInstance:
    instance_id: int      # 0..K-1
    vm_type: VMType
    name: str             # e.g., "small-0", "medium-1"


def build_vm_pool(catalog: List[VMType] = None, task_count: int = 100) -> List[VMInstance]:
    """
    Builds the fixed VM pool (Decision D4).
    5 instances per type (20 VMs) for <= 100 tasks; 10 per type (40 VMs) above that.
    """
    if catalog is None:
        catalog = get_default_catalog()
    count_per_type = 5 if task_count <= 100 else 10
    pool: List[VMInstance] = []
    idx = 0
    for vmt in catalog:
        for i in range(count_per_type):
            pool.append(VMInstance(instance_id=idx, vm_type=vmt, name=f"{vmt.name}-{i}"))
            idx += 1
    return pool
