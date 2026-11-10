"""
Shared Schedule Builder for CloudBurst.
Decodes task mappings into fully timed schedules and computes exact metrics:
Makespan, Cost, Energy, Utilization, and Deb's Feasibility.
"""
import math
from typing import List, Tuple, Dict, Optional, Any
from .model.vm import VMInstance
from .model.workflow import Workflow
from .model.schedule import Placement, Schedule

# System Model Constants (README Section 12.2)
BOOT_DELAY = 97.0          # beta = 97s
BILLING_PERIOD = 3600.0    # tau = 3600s
BANDWIDTH = 1.0e8          # B = 100 MB/s = 1e8 B/s


def compute_execution_time(wf: Workflow, pool: List[VMInstance]) -> List[List[float]]:
    """Precomputes ET[task][vm] = length[task] / speed[vm]."""
    return [[wf.length[i] / vm.vm_type.speed for vm in pool] for i in range(wf.n)]


def find_earliest_slot(
    slots: List[Tuple[float, float]],
    duration: float,
    ready_time: float,
    boot_delay: float = BOOT_DELAY,
) -> float:
    """
    Finds the earliest start time >= max(boot_delay, ready_time) in an idle slot
    of a VM that can fit `duration`.
    slots is a sorted list of (start, finish) intervals.
    """
    earliest_possible = max(boot_delay, ready_time)
    if not slots:
        return earliest_possible

    # Check gap before first task
    if slots[0][0] - earliest_possible >= duration:
        return earliest_possible

    # Check gaps between consecutive tasks
    for i in range(len(slots) - 1):
        gap_start = max(slots[i][1], earliest_possible)
        if slots[i + 1][0] - gap_start >= duration:
            return gap_start

    # After the last task
    return max(slots[-1][1], earliest_possible)


def insert_slot(slots: List[Tuple[float, float]], start: float, finish: float) -> None:
    """Inserts (start, finish) into slots list, keeping it sorted by start."""
    if not slots or start >= slots[-1][0]:
        slots.append((start, finish))
        return
    for i, (s, _) in enumerate(slots):
        if start < s:
            slots.insert(i, (start, finish))
            return
    slots.append((start, finish))


def build_schedule(
    wf: Workflow,
    pool: List[VMInstance],
    mapping: List[int],
    order: Optional[List[int]] = None,
    deadline: Optional[float] = None,
    et_matrix: Optional[List[List[float]]] = None,
    enable_duplication: bool = False,
    sub_deadlines: Optional[List[float]] = None,
    e_ref: Optional[float] = None,
    theta_e: float = 0.05,
    is_heft_td: bool = False,
) -> Schedule:
    """
    Decodes a task-to-VM mapping into a Schedule.
    Supports both standard decoding and duplication policies (DD-HPSO and HEFT-TD).
    """
    if order is None:
        order = wf.order
    if et_matrix is None:
        et_matrix = compute_execution_time(wf, pool)

    k_vms = len(pool)
    slots: List[List[Tuple[float, float]]] = [[] for _ in range(k_vms)]
    placements: List[Placement] = []

    # Map task -> list of placements (to support multiple copies if duplicated)
    task_copies: Dict[int, List[Placement]] = {i: [] for i in range(wf.n)}

    extra_energy_so_far = 0.0
    energy_budget = (theta_e * e_ref) if (e_ref is not None) else float("inf")

    for t_i in order:
        vm_k = mapping[t_i]
        et_ik = et_matrix[t_i][vm_k]

        # 1. Compute Data Ready Time DRT(t_i, vm_k)
        drt_ik = 0.0
        for p_idx, data_bytes in wf.parents[t_i]:
            best_parent_arr = float("inf")
            for copy in task_copies[p_idx]:
                trans = 0.0 if copy.vm == vm_k else (data_bytes / BANDWIDTH)
                arr = copy.finish + trans
                if arr < best_parent_arr:
                    best_parent_arr = arr
            if best_parent_arr > drt_ik:
                drt_ik = best_parent_arr

        # 2. Compute EST and AFT
        est_ik = find_earliest_slot(slots[vm_k], et_ik, drt_ik, BOOT_DELAY)
        aft_ik = est_ik + et_ik

        # 3. Duplication check (if enabled)
        duplicated = False
        if enable_duplication:
            # For DD-HPSO: check sub-deadline trigger
            trigger = True
            if not is_heft_td and sub_deadlines is not None:
                trigger = (aft_ik > sub_deadlines[t_i])

            if trigger:
                # Identify critical remote parent
                crit_parent = None
                crit_arr = -1.0
                for p_idx, data_bytes in wf.parents[t_i]:
                    has_local_copy = any(c.vm == vm_k for c in task_copies[p_idx])
                    if not has_local_copy and task_copies[p_idx]:
                        best_copy = min(task_copies[p_idx], key=lambda c: c.finish)
                        arr = best_copy.finish + (data_bytes / BANDWIDTH)
                        if arr > crit_arr:
                            crit_arr = arr
                            crit_parent = p_idx

                if crit_parent is not None:
                    et_pk = et_matrix[crit_parent][vm_k]
                    # Compute DRT for critical parent on vm_k
                    drt_pk = 0.0
                    for gp_idx, gp_data in wf.parents[crit_parent]:
                        best_gp_arr = float("inf")
                        for gp_copy in task_copies[gp_idx]:
                            trans = 0.0 if gp_copy.vm == vm_k else (gp_data / BANDWIDTH)
                            arr = gp_copy.finish + trans
                            if arr < best_gp_arr:
                                best_gp_arr = arr
                        if best_gp_arr > drt_pk:
                            drt_pk = best_gp_arr

                    # Can parent fit in an idle slot on vm_k before t_i would start?
                    est_pk = find_earliest_slot(slots[vm_k], et_pk, drt_pk, BOOT_DELAY)
                    aft_pk = est_pk + et_pk

                    if aft_pk <= est_ik:
                        # Recompute t_i's DRT and EST assuming p* runs on vm_k
                        new_drt = 0.0
                        for p_idx, data_bytes in wf.parents[t_i]:
                            if p_idx == crit_parent:
                                arr = aft_pk  # on same VM
                            else:
                                arr = float("inf")
                                for copy in task_copies[p_idx]:
                                    trans = 0.0 if copy.vm == vm_k else (data_bytes / BANDWIDTH)
                                    if copy.finish + trans < arr:
                                        arr = copy.finish + trans
                            if arr > new_drt:
                                new_drt = arr

                        # Slots with parent added temporarily
                        temp_slots = list(slots[vm_k])
                        insert_slot(temp_slots, est_pk, aft_pk)
                        new_est = find_earliest_slot(temp_slots, et_ik, new_drt, BOOT_DELAY)
                        new_aft = new_est + et_ik

                        if new_aft < aft_ik:
                            accept = False
                            if is_heft_td:
                                # HEFT-TD only checks EFT improvement
                                accept = True
                            else:
                                # DD-HPSO checks theta_C = 0 and theta_E
                                vm_obj = pool[vm_k]
                                delta_e = (vm_obj.vm_type.p_busy - vm_obj.vm_type.p_idle) * et_pk
                                energy_ok = (extra_energy_so_far + delta_e) <= energy_budget

                                # Cost check: does adding the duplicate increase billed periods on vm_k?
                                old_first_start = slots[vm_k][0][0] if slots[vm_k] else est_ik
                                old_last_finish = max(slots[vm_k][-1][1] if slots[vm_k] else aft_ik, aft_ik)
                                old_t_start = old_first_start - BOOT_DELAY
                                old_periods = math.ceil(max(0.0, old_last_finish - old_t_start) / BILLING_PERIOD)

                                new_first_start = min(old_first_start, est_pk, new_est)
                                new_last_finish = max(old_last_finish, aft_pk, new_aft)
                                new_t_start = new_first_start - BOOT_DELAY
                                new_periods = math.ceil(max(0.0, new_last_finish - new_t_start) / BILLING_PERIOD)

                                cost_ok = (new_periods <= old_periods)
                                if cost_ok and energy_ok:
                                    accept = True
                                    extra_energy_so_far += delta_e

                            if accept:
                                # Register duplicate
                                dup_p = Placement(task=crit_parent, vm=vm_k, start=est_pk, finish=aft_pk, is_dup=True)
                                insert_slot(slots[vm_k], est_pk, aft_pk)
                                placements.append(dup_p)
                                task_copies[crit_parent].append(dup_p)

                                est_ik = new_est
                                aft_ik = new_aft
                                duplicated = True

        # 4. Finalize placement of t_i
        insert_slot(slots[vm_k], est_ik, aft_ik)
        p_obj = Placement(task=t_i, vm=vm_k, start=est_ik, finish=aft_ik, is_dup=False)
        placements.append(p_obj)
        task_copies[t_i].append(p_obj)

    # 5. Compute aggregate metrics
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

    return Schedule(
        placements=placements,
        makespan=makespan,
        cost=total_cost,
        energy=total_energy,
        utilization=utilization,
        deadline_met=deadline_met,
        violation=violation,
    )


def compare_schedules_deb(
    sched_a: Schedule,
    sched_b: Schedule,
    f_a: float,
    f_b: float,
) -> int:
    """
    Deb's feasibility comparison rules (README Section 4.7).
    Returns:
       -1 if sched_a beats sched_b
       +1 if sched_b beats sched_a
        0 if tied
    """
    feas_a = sched_a.deadline_met
    feas_b = sched_b.deadline_met

    # Case 1: Both feasible -> smaller F wins
    if feas_a and feas_b:
        if f_a < f_b - 1e-9:
            return -1
        elif f_b < f_a - 1e-9:
            return 1
        return 0

    # Case 2: One feasible, one infeasible -> feasible wins
    if feas_a and not feas_b:
        return -1
    if not feas_a and feas_b:
        return 1

    # Case 3: Both infeasible -> smaller violation V wins
    if sched_a.violation < sched_b.violation - 1e-9:
        return -1
    elif sched_b.violation < sched_a.violation - 1e-9:
        return 1

    # Violation tie -> smaller F
    if f_a < f_b - 1e-9:
        return -1
    elif f_b < f_a - 1e-9:
        return 1
    return 0
