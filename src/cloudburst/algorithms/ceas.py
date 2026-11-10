"""
CEAS: Cost and Energy Aware Scheduling (Li et al., IEEE TSC 2018).
Implements Steps 1 to 4 on the shared VM pool (Step 5 DVFS omitted, Decision D24).
(README Section 8.3; Reference Paper 3)
"""
import time
import math
from typing import List, Tuple, Optional, Dict, Set
from ..model.workflow import Workflow
from ..model.vm import VMInstance
from ..model.schedule import Schedule
from ..builder import (
    build_schedule,
    compute_execution_time,
    find_earliest_slot,
    insert_slot,
    BOOT_DELAY,
    BILLING_PERIOD,
    BANDWIDTH,
)


def schedule_ceas(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: float,
    et_matrix: Optional[List[List[float]]] = None,
) -> Schedule:
    """
    CEAS heuristic without DVFS (Steps 1-4).
    1. Sub-makespan division & cost-utility VM selection.
    2. Sequential task merging.
    3. Parallel task merging.
    4. VM reuse and schedule construction.
    """
    start_time = time.perf_counter()
    if et_matrix is None:
        et_matrix = compute_execution_time(wf, pool)

    n_tasks = wf.n
    k_vms = len(pool)
    order = wf.order

    # Group pool by VM type
    type_to_vms: Dict[int, List[int]] = {}
    for vm in pool:
        tid = vm.vm_type.type_id
        if tid not in type_to_vms:
            type_to_vms[tid] = []
        type_to_vms[tid].append(vm.instance_id)

    # Step 1: Sub-makespan distribution
    # Fastest execution time per task
    min_et = [min(et_matrix[i]) for i in range(n_tasks)]
    sum_min_et = sum(min_et) if sum(min_et) > 0 else 1.0
    sub_makespans = [(deadline * (min_et[i] / sum_min_et)) for i in range(n_tasks)]

    # Cost-utility VM type selection
    # Prefer cheaper VM types that satisfy sub_makespan
    assigned_type: List[int] = [0] * n_tasks
    for i in range(n_tasks):
        best_tid = 0
        best_price = float("inf")
        # Check VM types
        for tid in sorted(type_to_vms.keys()):
            sample_vm = type_to_vms[tid][0]
            dur = et_matrix[i][sample_vm]
            if dur <= sub_makespans[i]:
                price = pool[sample_vm].vm_type.price
                if price < best_price:
                    best_price = price
                    best_tid = tid

        # If none fit within sub-makespan, select the fastest VM type (tid with highest speed)
        if best_price == float("inf"):
            best_tid = max(type_to_vms.keys(), key=lambda t: pool[type_to_vms[t][0]].vm_type.speed)
        assigned_type[i] = best_tid

    # Step 2: Sequential Task Merging
    # If parent p has exactly 1 child c, and child c has exactly 1 parent p:
    # Merge them to run on the same VM type (the faster of the two)
    seq_groups: Dict[int, int] = {i: i for i in range(n_tasks)}
    for p in range(n_tasks):
        if len(wf.children[p]) == 1:
            c = wf.children[p][0][0]
            if len(wf.parents[c]) == 1:
                # Merge p and c
                faster_tid = max(assigned_type[p], assigned_type[c])
                assigned_type[p] = faster_tid
                assigned_type[c] = faster_tid

    # Step 3: Parallel Task Merging
    # Sibling tasks with identical parents and children are assigned to same VM type
    parents_signature = [tuple(sorted(p[0] for p in wf.parents[i])) for i in range(n_tasks)]
    children_signature = [tuple(sorted(c[0] for c in wf.children[i])) for i in range(n_tasks)]
    for i in range(n_tasks):
        for j in range(i + 1, n_tasks):
            if parents_signature[i] and parents_signature[i] == parents_signature[j]:
                if children_signature[i] and children_signature[i] == children_signature[j]:
                    common_tid = max(assigned_type[i], assigned_type[j])
                    assigned_type[i] = common_tid
                    assigned_type[j] = common_tid

    # Step 4: VM Reuse and Schedule Construction
    # Place tasks in topological order. For each task, check instances of its assigned type:
    # Prefer an already active instance of assigned_type where it fits in an idle slot
    # without opening a new billing period. Otherwise open a new instance of that type.
    slots: List[List[Tuple[float, float]]] = [[] for _ in range(k_vms)]
    mapping = [0] * n_tasks
    task_finish = [0.0] * n_tasks

    for t_i in order:
        target_tid = assigned_type[t_i]
        candidate_vms = type_to_vms[target_tid]

        best_vm = candidate_vms[0]
        best_aft = float("inf")
        best_est = float("inf")
        best_new_period = True

        for vm_k in candidate_vms:
            et_ik = et_matrix[t_i][vm_k]
            drt_ik = 0.0
            for p_idx, data_bytes in wf.parents[t_i]:
                p_vm = mapping[p_idx]
                trans = 0.0 if p_vm == vm_k else (data_bytes / BANDWIDTH)
                arr = task_finish[p_idx] + trans
                if arr > drt_ik:
                    drt_ik = arr

            est_ik = find_earliest_slot(slots[vm_k], et_ik, drt_ik, BOOT_DELAY)
            aft_ik = est_ik + et_ik

            # Check if this placement opens a new billing period
            opens_new_period = True
            if slots[vm_k]:
                t_start = slots[vm_k][0][0] - BOOT_DELAY
                current_end = slots[vm_k][-1][1]
                current_periods = math.ceil(max(0.0, current_end - t_start) / BILLING_PERIOD)

                new_end = max(current_end, aft_ik)
                new_periods = math.ceil(max(0.0, new_end - t_start) / BILLING_PERIOD)
                opens_new_period = (new_periods > current_periods)

            # Preference: reuse without new period > earlier AFT > lowest VM index
            if not opens_new_period and best_new_period:
                best_vm = vm_k
                best_aft = aft_ik
                best_est = est_ik
                best_new_period = False
            elif opens_new_period == best_new_period:
                if aft_ik < best_aft - 1e-9:
                    best_vm = vm_k
                    best_aft = aft_ik
                    best_est = est_ik

        mapping[t_i] = best_vm
        task_finish[t_i] = best_aft
        insert_slot(slots[best_vm], best_est, best_aft)

    sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)
    sched.runtime_s = time.perf_counter() - start_time
    return sched
