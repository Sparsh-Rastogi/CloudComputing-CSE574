"""
WPSO: A PSO-Based Algorithm for Cost-Effective and Deadline-Constrained Workflow Scheduling.
(Guichen Wang, Yongke Li, Gongxuan Zhang, IEEE ICCCBDA 2025; Recent Paper 1)
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
    compare_schedules_deb,
    find_earliest_slot,
    insert_slot,
    BOOT_DELAY,
    BILLING_PERIOD,
    BANDWIDTH,
)


def compute_lft(wf: Workflow, deadline: float, et_matrix: List[List[float]]) -> List[float]:
    """
    Computes Latest Finish Time (LFT) via backward topological traversal (Eq. 7).
    Uses execution time on fastest VM type.
    """
    n = wf.n
    min_et = [min(et_matrix[i]) for i in range(n)]
    lft = [deadline] * n

    # Backward traversal
    in_degree = [len(wf.children[i]) for i in range(n)]
    queue = [i for i in range(n) if in_degree[i] == 0]

    parent_child_count = list(in_degree)
    while queue:
        curr = queue.pop(0)
        curr_lft = lft[curr]
        for p_idx, data_bytes in wf.parents[curr]:
            comm = data_bytes / BANDWIDTH
            val = curr_lft - min_et[curr] - comm
            if val < lft[p_idx]:
                lft[p_idx] = val
            parent_child_count[p_idx] -= 1
            if parent_child_count[p_idx] == 0:
                queue.append(p_idx)

    return lft


def decode_wpso_solution(
    wf: Workflow,
    pool: List[VMInstance],
    type_mapping: List[int],
    lft: List[float],
    deadline: float,
    et_matrix: List[List[float]],
) -> Schedule:
    """
    Alg. 2: Solution Construction from WPSO particle.
    Filters candidate instances by LFT, parent co-location, and billing interval reuse.
    """
    n = wf.n
    k_vms = len(pool)
    order = wf.order

    # Group pool instances by type
    type_to_vms: Dict[int, List[int]] = {}
    for vm in pool:
        tid = vm.vm_type.type_id
        if tid not in type_to_vms:
            type_to_vms[tid] = []
        type_to_vms[tid].append(vm.instance_id)

    # Active instances in R
    active_instances: Set[int] = set()
    slots: List[List[Tuple[float, float]]] = [[] for _ in range(k_vms)]
    mapping = [0] * n
    task_finish = [0.0] * n

    for t_i in order:
        target_tid = type_mapping[t_i]
        all_instances_of_type = type_to_vms[target_tid]
        active_of_type = [v for v in all_instances_of_type if v in active_instances]

        # Candidates meeting LFT
        cand_a: List[Tuple[int, float, float, bool]] = [] # with parent
        cand_b: List[Tuple[int, float, float, bool]] = [] # without parent

        parents_of_ti = {p[0] for p in wf.parents[t_i]}

        for v in active_of_type:
            et_iv = et_matrix[t_i][v]
            drt_iv = 0.0
            has_parent = False
            for p_idx, data_bytes in wf.parents[t_i]:
                p_vm = mapping[p_idx]
                if p_vm == v:
                    has_parent = True
                trans = 0.0 if p_vm == v else (data_bytes / BANDWIDTH)
                arr = task_finish[p_idx] + trans
                if arr > drt_iv:
                    drt_iv = arr

            est_iv = find_earliest_slot(slots[v], et_iv, drt_iv, BOOT_DELAY)
            aft_iv = est_iv + et_iv

            # Check LFT filter (Alg. 2 Line 7)
            if aft_iv <= lft[t_i] + 1e-6:
                # Check billing interval expansion
                t_start = slots[v][0][0] - BOOT_DELAY
                curr_end = slots[v][-1][1]
                curr_bi = math.ceil(max(0.0, curr_end - t_start) / BILLING_PERIOD)
                new_end = max(curr_end, aft_iv)
                new_bi = math.ceil(max(0.0, new_end - t_start) / BILLING_PERIOD)
                no_new_interval = (new_bi == curr_bi)

                item = (v, est_iv, aft_iv, no_new_interval)
                if has_parent:
                    cand_a.append(item)
                else:
                    cand_b.append(item)

        candidates = cand_a if cand_a else cand_b

        selected_vm = -1
        selected_est = 0.0
        selected_aft = 0.0

        if candidates:
            # Prefer candidates that add no new billing interval
            no_new = [c for c in candidates if c[3]]
            pool_choices = no_new if no_new else candidates
            # Pick lowest finish time (W8)
            pool_choices.sort(key=lambda c: (c[2], c[0]))
            selected_vm, selected_est, selected_aft, _ = pool_choices[0]
        else:
            # Open a new instance of target_tid
            unused = [v for v in all_instances_of_type if v not in active_instances]
            if unused:
                selected_vm = unused[0]
            else:
                # If all instances in pool are already active, use the one that gives earliest finish
                best_aft = float("inf")
                selected_vm = all_instances_of_type[0]
                for v in all_instances_of_type:
                    et_iv = et_matrix[t_i][v]
                    drt_iv = 0.0
                    for p_idx, data_bytes in wf.parents[t_i]:
                        trans = 0.0 if mapping[p_idx] == v else (data_bytes / BANDWIDTH)
                        arr = task_finish[p_idx] + trans
                        if arr > drt_iv:
                            drt_iv = arr
                    est_iv = find_earliest_slot(slots[v], et_iv, drt_iv, BOOT_DELAY)
                    if est_iv + et_iv < best_aft:
                        best_aft = est_iv + et_iv
                        selected_vm = v

            et_iv = et_matrix[t_i][selected_vm]
            drt_iv = 0.0
            for p_idx, data_bytes in wf.parents[t_i]:
                trans = 0.0 if mapping[p_idx] == selected_vm else (data_bytes / BANDWIDTH)
                arr = task_finish[p_idx] + trans
                if arr > drt_iv:
                    drt_iv = arr
            selected_est = find_earliest_slot(slots[selected_vm], et_iv, drt_iv, BOOT_DELAY)
            selected_aft = selected_est + et_iv

        active_instances.add(selected_vm)
        mapping[t_i] = selected_vm
        task_finish[t_i] = selected_aft
        insert_slot(slots[selected_vm], selected_est, selected_aft)

    return build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)


def schedule_wpso(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: float,
    rng: Optional[random.Random] = None,
    pop_size: int = 30,
    iterations: int = 100,
    c1: float = 1.6,
    c2: float = 1.6,
    omega: float = 0.5,
    et_matrix: Optional[List[List[float]]] = None,
) -> Schedule:
    """Runs WPSO algorithm on the workflow and VM pool."""
    start_time = time.perf_counter()
    if rng is None:
        rng = random.Random(42)
    if et_matrix is None:
        et_matrix = compute_execution_time(wf, pool)

    n_tasks = wf.n
    n_types = 4  # small, medium, large, xlarge
    lft = compute_lft(wf, deadline, et_matrix)

    swarm_x: List[List[float]] = []
    swarm_v: List[List[float]] = []
    pbest_x: List[List[float]] = []
    pbest_sched: List[Schedule] = []

    # Particle 0: initialized to maximum speed type (fastest) as per paper
    # Other particles: random initialization
    for p_i in range(pop_size):
        if p_i == 0:
            x = [3.99 for _ in range(n_tasks)]
        else:
            x = [rng.uniform(0.0, 3.999) for _ in range(n_tasks)]
        v = [rng.uniform(-1.0, 1.0) for _ in range(n_tasks)]
        type_mapping = [int(val) for val in x]
        sched = decode_wpso_solution(wf, pool, type_mapping, lft, deadline, et_matrix)

        swarm_x.append(x)
        swarm_v.append(v)
        pbest_x.append(list(x))
        pbest_sched.append(sched)

    # Initial gbest by Deb's rules on cost
    gbest_idx = 0
    for i in range(1, pop_size):
        if compare_schedules_deb(pbest_sched[i], pbest_sched[gbest_idx], pbest_sched[i].cost, pbest_sched[gbest_idx].cost) < 0:
            gbest_idx = i

    gbest_x = list(pbest_x[gbest_idx])
    gbest_sched = pbest_sched[gbest_idx]

    # Optimization loop
    for _ in range(iterations):
        for i in range(pop_size):
            for d in range(n_tasks):
                r1 = rng.random()
                r2 = rng.random()
                swarm_v[i][d] = (
                    omega * swarm_v[i][d]
                    + c1 * r1 * (pbest_x[i][d] - swarm_x[i][d])
                    + c2 * r2 * (gbest_x[d] - swarm_x[i][d])
                )
                swarm_v[i][d] = max(-2.0, min(2.0, swarm_v[i][d]))
                swarm_x[i][d] += swarm_v[i][d]
                swarm_x[i][d] = max(0.0, min(3.999, swarm_x[i][d]))

            type_mapping = [int(val) for val in swarm_x[i]]
            sched = decode_wpso_solution(wf, pool, type_mapping, lft, deadline, et_matrix)

            if compare_schedules_deb(sched, pbest_sched[i], sched.cost, pbest_sched[i].cost) < 0:
                pbest_x[i] = list(swarm_x[i])
                pbest_sched[i] = sched

                if compare_schedules_deb(sched, gbest_sched, sched.cost, gbest_sched.cost) < 0:
                    gbest_x = list(swarm_x[i])
                    gbest_sched = sched

    gbest_sched.runtime_s = time.perf_counter() - start_time
    return gbest_sched
