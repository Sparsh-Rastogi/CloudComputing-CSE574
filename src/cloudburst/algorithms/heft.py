"""
Heterogeneous Earliest Finish Time (HEFT) list scheduling algorithm.
Used as baseline, normalization reference, and PSO seed.
(Topcuoglu et al., 2002; README Section 6.1)
"""
import time
from typing import List, Tuple, Optional
from ..model.workflow import Workflow
from ..model.vm import VMInstance
from ..model.schedule import Schedule
from ..builder import (
    build_schedule,
    compute_execution_time,
    find_earliest_slot,
    insert_slot,
    BOOT_DELAY,
    BANDWIDTH,
)


def schedule_heft(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: Optional[float] = None,
    et_matrix: Optional[List[List[float]]] = None,
) -> Tuple[Schedule, List[int]]:
    """
    Runs HEFT scheduling on the workflow and VM pool.
    Returns (Schedule, mapping_vector).
    """
    start_time = time.perf_counter()
    if et_matrix is None:
        et_matrix = compute_execution_time(wf, pool)

    order = wf.order
    k_vms = len(pool)
    mapping = [0] * wf.n

    # Fast simulation tracking for HEFT
    slots: List[List[Tuple[float, float]]] = [[] for _ in range(k_vms)]
    task_finish: List[float] = [0.0] * wf.n
    task_vm: List[int] = [0] * wf.n

    for t_i in order:
        best_vm = 0
        best_aft = float("inf")
        best_est = float("inf")

        for k in range(k_vms):
            et_ik = et_matrix[t_i][k]
            # DRT on VM k
            drt_ik = 0.0
            for p_idx, data_bytes in wf.parents[t_i]:
                p_vm = task_vm[p_idx]
                trans = 0.0 if p_vm == k else (data_bytes / BANDWIDTH)
                arr = task_finish[p_idx] + trans
                if arr > drt_ik:
                    drt_ik = arr

            est_ik = find_earliest_slot(slots[k], et_ik, drt_ik, BOOT_DELAY)
            aft_ik = est_ik + et_ik

            # Decision D26: Lowest AFT, tie-breaker: lowest VM index
            if aft_ik < best_aft - 1e-9:
                best_aft = aft_ik
                best_est = est_ik
                best_vm = k

        mapping[t_i] = best_vm
        task_vm[t_i] = best_vm
        task_finish[t_i] = best_aft
        insert_slot(slots[best_vm], best_est, best_aft)

    # Build final schedule with complete metric accounting
    sched = build_schedule(
        wf=wf,
        pool=pool,
        mapping=mapping,
        order=order,
        deadline=deadline,
        et_matrix=et_matrix,
        enable_duplication=False,
    )
    sched.runtime_s = time.perf_counter() - start_time
    return sched, mapping
