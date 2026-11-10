"""
HEFT-TD: HEFT with Task Duplication.
(Genez et al., IEEE/ACM UCC 2018; README Section 8.1; Reference Paper 1)
Our implementation adapted to the shared model.
"""
import time
from typing import List, Tuple, Optional, Dict
from ..model.workflow import Workflow
from ..model.vm import VMInstance
from ..model.schedule import Schedule, Placement
from ..builder import (
    build_schedule,
    compute_execution_time,
    find_earliest_slot,
    insert_slot,
    BOOT_DELAY,
    BILLING_PERIOD,
    BANDWIDTH,
)
import math


def schedule_heft_td(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: Optional[float] = None,
    et_matrix: Optional[List[List[float]]] = None,
) -> Schedule:
    """
    HEFT-TD schedules tasks using finish-time driven critical parent duplication.
    """
    start_time = time.perf_counter()
    if et_matrix is None:
        et_matrix = compute_execution_time(wf, pool)

    order = wf.order
    k_vms = len(pool)
    slots: List[List[Tuple[float, float]]] = [[] for _ in range(k_vms)]
    placements: List[Placement] = []
    task_copies: Dict[int, List[Placement]] = {i: [] for i in range(wf.n)}

    for t_i in order:
        best_vm = 0
        best_aft = float("inf")
        best_est = float("inf")
        best_dup_info = None  # (crit_parent, est_pk, aft_pk)

        for k in range(k_vms):
            et_ik = et_matrix[t_i][k]
            # Standard DRT
            drt_ik = 0.0
            crit_parent = None
            crit_arr = -1.0
            for p_idx, data_bytes in wf.parents[t_i]:
                best_parent_arr = float("inf")
                has_copy_on_k = any(c.vm == k for c in task_copies[p_idx])
                for copy in task_copies[p_idx]:
                    trans = 0.0 if copy.vm == k else (data_bytes / BANDWIDTH)
                    arr = copy.finish + trans
                    if arr < best_parent_arr:
                        best_parent_arr = arr
                if best_parent_arr > drt_ik:
                    drt_ik = best_parent_arr
                if not has_copy_on_k and task_copies[p_idx]:
                    if best_parent_arr > crit_arr:
                        crit_arr = best_parent_arr
                        crit_parent = p_idx

            est_ik = find_earliest_slot(slots[k], et_ik, drt_ik, BOOT_DELAY)
            aft_ik = est_ik + et_ik
            dup_info = None

            # Attempt critical parent duplication on candidate VM k
            if crit_parent is not None:
                et_pk = et_matrix[crit_parent][k]
                drt_pk = 0.0
                for gp_idx, gp_data in wf.parents[crit_parent]:
                    best_gp_arr = float("inf")
                    for gp_copy in task_copies[gp_idx]:
                        trans = 0.0 if gp_copy.vm == k else (gp_data / BANDWIDTH)
                        arr = gp_copy.finish + trans
                        if arr < best_gp_arr:
                            best_gp_arr = arr
                    if best_gp_arr > drt_pk:
                        drt_pk = best_gp_arr

                est_pk = find_earliest_slot(slots[k], et_pk, drt_pk, BOOT_DELAY)
                aft_pk = est_pk + et_pk

                if aft_pk <= est_ik:
                    # New DRT for t_i with parent on VM k
                    new_drt = 0.0
                    for p_idx, data_bytes in wf.parents[t_i]:
                        if p_idx == crit_parent:
                            arr = aft_pk
                        else:
                            arr = float("inf")
                            for copy in task_copies[p_idx]:
                                trans = 0.0 if copy.vm == k else (data_bytes / BANDWIDTH)
                                if copy.finish + trans < arr:
                                    arr = copy.finish + trans
                        if arr > new_drt:
                            new_drt = arr

                    temp_slots = list(slots[k])
                    insert_slot(temp_slots, est_pk, aft_pk)
                    new_est = find_earliest_slot(temp_slots, et_ik, new_drt, BOOT_DELAY)
                    new_aft = new_est + et_ik

                    if new_aft < aft_ik:
                        est_ik = new_est
                        aft_ik = new_aft
                        dup_info = (crit_parent, est_pk, aft_pk)

            if aft_ik < best_aft - 1e-9:
                best_aft = aft_ik
                best_est = est_ik
                best_vm = k
                best_dup_info = dup_info

        # Commit winning placement
        if best_dup_info is not None:
            p_crit, s_crit, f_crit = best_dup_info
            dup_p = Placement(task=p_crit, vm=best_vm, start=s_crit, finish=f_crit, is_dup=True)
            insert_slot(slots[best_vm], s_crit, f_crit)
            placements.append(dup_p)
            task_copies[p_crit].append(dup_p)

        insert_slot(slots[best_vm], best_est, best_aft)
        p_obj = Placement(task=t_i, vm=best_vm, start=best_est, finish=best_aft, is_dup=False)
        placements.append(p_obj)
        task_copies[t_i].append(p_obj)

    # Compute complete metrics
    makespan = max((p.finish for p in placements), default=0.0)
    total_cost = 0.0
    total_energy = 0.0
    total_busy_time = 0.0
    total_leased_time = 0.0

    for k in range(k_vms):
        vm_slots = slots[k]
        if not vm_slots:
            continue
        vmt = pool[k].vm_type
        first_start = vm_slots[0][0]
        last_finish = vm_slots[-1][1]
        t_start = first_start - BOOT_DELAY
        t_end = last_finish
        leased_time = max(0.0, t_end - t_start)

        periods = math.ceil(leased_time / BILLING_PERIOD)
        cost_k = periods * vmt.price

        busy_k = sum(f - s for s, f in vm_slots)
        idle_k = max(0.0, leased_time - busy_k)
        energy_k = (vmt.p_busy * busy_k) + (vmt.p_idle * idle_k)

        total_cost += cost_k
        total_energy += energy_k
        total_busy_time += busy_k
        total_leased_time += leased_time

    utilization = (total_busy_time / total_leased_time) if total_leased_time > 0 else 0.0
    violation = max(0.0, makespan - deadline) if (deadline is not None) else 0.0
    deadline_met = (violation <= 1e-6)

    sched = Schedule(
        placements=placements,
        makespan=makespan,
        cost=total_cost,
        energy=total_energy,
        utilization=utilization,
        deadline_met=deadline_met,
        violation=violation,
        runtime_s=time.perf_counter() - start_time,
    )
    return sched
