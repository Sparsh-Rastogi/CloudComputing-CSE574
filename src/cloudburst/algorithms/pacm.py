"""
PACM: Path-Aware Scheduling Algorithm for Cost Optimization of Deadline-Constrained Scientific Workflows.
(Lin Cheng, Jing Wu, Yu Gan, Ziyu Chen, Wei Hu, IEEE TCC 13(4), Oct-Dec 2025; Recent Paper 3)
Our implementation adapted to the shared model and fixed pool.
"""
import time
import random
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


def compute_probabilistic_mr(
    wf: Workflow,
    fastest_speed: float,
    rng: random.Random,
    theta: float = 1.5,
) -> List[float]:
    """Computes probabilistic upward rank mr(t_i) (Eq. 11-13)."""
    n = wf.n
    mr = [0.0] * n
    et_f = [wf.length[i] / fastest_speed for i in range(n)]

    out_deg = [len(wf.children[i]) for i in range(n)]
    queue = [i for i in range(n) if out_deg[i] == 0]
    parent_child_count = list(out_deg)

    while queue:
        curr = queue.pop(0)
        max_succ = 0.0
        for c_idx, data_bytes in wf.children[curr]:
            tt = max(1e-6, data_bytes / BANDWIDTH)
            tau_j = et_f[curr] / tt
            prob = 1.0 - (theta ** (-tau_j))
            gamma_j = 0.0 if prob < rng.random() else 1.0
            val = mr[c_idx] + gamma_j * tt
            if val > max_succ:
                max_succ = val

        mr[curr] = et_f[curr] + max_succ
        for p_idx, _ in wf.parents[curr]:
            parent_child_count[p_idx] -= 1
            if parent_child_count[p_idx] == 0:
                queue.append(p_idx)

    return mr


def schedule_pacm(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: float,
    rng: Optional[random.Random] = None,
    theta: float = 1.5,
    et_matrix: Optional[List[List[float]]] = None,
) -> Schedule:
    """Runs PACM algorithm on the workflow and VM pool."""
    start_time = time.perf_counter()
    if rng is None:
        rng = random.Random(42)
    if et_matrix is None:
        et_matrix = compute_execution_time(wf, pool)

    n = wf.n
    k_vms = len(pool)

    # Fastest VM speed
    fastest_speed = max(vm.vm_type.speed for vm in pool)
    avg_speed = sum(vm.vm_type.speed for vm in pool) / k_vms
    avg_et = [wf.length[i] / avg_speed for i in range(n)]

    # Step 1: Priority Ranking
    mr = compute_probabilistic_mr(wf, fastest_speed, rng, theta=theta)
    # Sort descending by mr, ascending by task id
    indexed_mr = [(mr[i], -i, i) for i in range(n)]
    indexed_mr.sort(reverse=True)
    pl = [item[2] for item in indexed_mr]

    # Step 2: Critical Path Length (CPL)
    cpl_u = [0.0] * n
    out_deg = [len(wf.children[i]) for i in range(n)]
    q_u = [i for i in range(n) if out_deg[i] == 0]
    pcc = list(out_deg)
    while q_u:
        curr = q_u.pop(0)
        max_succ = 0.0
        for c_idx, data_bytes in wf.children[curr]:
            val = (data_bytes / BANDWIDTH) + cpl_u[c_idx]
            if val > max_succ:
                max_succ = val
        cpl_u[curr] = avg_et[curr] + max_succ
        for p_idx, _ in wf.parents[curr]:
            pcc[p_idx] -= 1
            if pcc[p_idx] == 0:
                q_u.append(p_idx)

    cpl_d = [0.0] * n
    in_deg = [len(wf.parents[i]) for i in range(n)]
    q_d = [i for i in range(n) if in_deg[i] == 0]
    ccc = list(in_deg)
    while q_d:
        curr = q_d.pop(0)
        max_pred = 0.0
        for p_idx, data_bytes in wf.parents[curr]:
            val = (data_bytes / BANDWIDTH) + cpl_d[p_idx] + avg_et[p_idx]
            if val > max_pred:
                max_pred = val
        cpl_d[curr] = max_pred
        for c_idx, _ in wf.children[curr]:
            ccc[c_idx] -= 1
            if ccc[c_idx] == 0:
                q_d.append(c_idx)

    cpl = [cpl_u[i] + cpl_d[i] for i in range(n)]
    max_cpl = max(cpl) if cpl else 1.0
    cf = [1 if abs(cpl[i] - max_cpl) < 1e-4 else 0 for i in range(n)]

    # Step 3: Sub-deadlines
    et_f = [wf.length[i] / fastest_speed for i in range(n)]
    lft = [deadline] * n
    q_lft = [i for i in range(n) if out_deg[i] == 0]
    pcc_lft = list(out_deg)
    while q_lft:
        curr = q_lft.pop(0)
        for p_idx, data_bytes in wf.parents[curr]:
            val = lft[curr] - et_f[curr] - (data_bytes / BANDWIDTH)
            if val < lft[p_idx]:
                lft[p_idx] = val
            pcc_lft[p_idx] -= 1
            if pcc_lft[p_idx] == 0:
                q_lft.append(p_idx)

    # In-degree statistics for DAF
    in_degrees = [len(wf.parents[i]) for i in range(n)]
    max_in = max(in_degrees) if in_degrees else 1
    mean_in = sum(in_degrees) / float(n) if n > 0 else 1.0
    var_in = sum((x - mean_in) ** 2 for x in in_degrees) / float(n) if n > 0 else 1.0
    std_in = math.sqrt(var_in) if var_in > 1e-6 else 1.0
    daf = max_in / std_in
    sum_ie = max(1, sum(in_degrees))

    mr_entry = max(mr) if mr else 1.0
    sub_d = [0.0] * n
    for i in range(n):
        if cf[i] == 1:
            # Critical path sub-deadline (Eq. 24)
            dit = (sum(d[1] / BANDWIDTH for d in wf.parents[i]) / mr_entry)
            sub_d[i] = max(0.0, min(deadline, lft[i] - dit * (mr_entry - mr[i])))
        else:
            # Non-critical sub-deadline (Eq. 22)
            ratio = (mr_entry - mr[i] + et_f[i] + daf * (in_degrees[i] / sum_ie)) / mr_entry
            sub_d[i] = max(0.0, min(deadline, ratio * deadline))

    # Step 4: VM Mapping
    slots: List[List[Tuple[float, float]]] = [[] for _ in range(k_vms)]
    mapping = [0] * n
    task_finish = [0.0] * n

    for t_i in pl:
        is_crit = (cf[t_i] == 1)
        target_subd = sub_d[t_i]

        best_vm = -1
        best_aft = float("inf")
        best_est = float("inf")
        best_inc_cost = float("inf")

        # Evaluate all candidate VMs in pool
        for k in range(k_vms):
            et_ik = et_matrix[t_i][k]
            drt_ik = 0.0
            for p_idx, data_bytes in wf.parents[t_i]:
                p_vm = mapping[p_idx]
                trans = 0.0 if p_vm == k else (data_bytes / BANDWIDTH)
                arr = task_finish[p_idx] + trans
                if arr > drt_ik:
                    drt_ik = arr

            est_ik = find_earliest_slot(slots[k], et_ik, drt_ik, BOOT_DELAY)
            aft_ik = est_ik + et_ik

            # Compute incremental cost
            vmt = pool[k].vm_type
            if slots[k]:
                t_start = slots[k][0][0] - BOOT_DELAY
                curr_end = slots[k][-1][1]
                curr_periods = math.ceil(max(0.0, curr_end - t_start) / BILLING_PERIOD)
                new_end = max(curr_end, aft_ik)
                new_periods = math.ceil(max(0.0, new_end - t_start) / BILLING_PERIOD)
                inc_cost = (new_periods - curr_periods) * vmt.price
            else:
                inc_cost = vmt.price  # opening 1 new period

            meets_subd = (aft_ik <= target_subd + 1e-6)

            if is_crit:
                # Critical: earliest finish time meeting sub-deadline
                if meets_subd:
                    if aft_ik < best_aft - 1e-9:
                        best_aft = aft_ik
                        best_est = est_ik
                        best_vm = k
            else:
                # Non-critical: minimal incremental cost meeting sub-deadline
                if meets_subd:
                    if inc_cost < best_inc_cost - 1e-9:
                        best_inc_cost = inc_cost
                        best_aft = aft_ik
                        best_est = est_ik
                        best_vm = k
                    elif abs(inc_cost - best_inc_cost) <= 1e-9:
                        if aft_ik < best_aft - 1e-9:
                            best_aft = aft_ik
                            best_est = est_ik
                            best_vm = k

        # Fallback: if no VM meets sub-deadline, pick the one with earliest finish time
        if best_vm == -1:
            best_aft = float("inf")
            for k in range(k_vms):
                et_ik = et_matrix[t_i][k]
                drt_ik = 0.0
                for p_idx, data_bytes in wf.parents[t_i]:
                    p_vm = mapping[p_idx]
                    trans = 0.0 if p_vm == k else (data_bytes / BANDWIDTH)
                    arr = task_finish[p_idx] + trans
                    if arr > drt_ik:
                        drt_ik = arr
                est_ik = find_earliest_slot(slots[k], et_ik, drt_ik, BOOT_DELAY)
                aft_ik = est_ik + et_ik
                if aft_ik < best_aft - 1e-9:
                    best_aft = aft_ik
                    best_est = est_ik
                    best_vm = k

        mapping[t_i] = best_vm
        task_finish[t_i] = best_aft
        insert_slot(slots[best_vm], best_est, best_aft)

    sched = build_schedule(wf, pool, mapping, order=wf.order, deadline=deadline, et_matrix=et_matrix)
    sched.runtime_s = time.perf_counter() - start_time
    return sched
