"""
Rodriguez & Buyya (IEEE TCC 2014) PSO Workflow Scheduler.
Cost-minimizing PSO under hourly billing with Deb's rules for deadline constraint.
(README Section 8.2, Decision D23; Reference Paper 2)
"""
import time
import random
import math
from typing import List, Tuple, Optional
from ..model.workflow import Workflow
from ..model.vm import VMInstance
from ..model.schedule import Schedule
from ..builder import (
    build_schedule,
    compute_execution_time,
    compare_schedules_deb,
)


def schedule_rodriguez_pso(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: float,
    rng: Optional[random.Random] = None,
    pop_size: int = 30,
    iterations: int = 100,
    c1: float = 2.0,
    c2: float = 2.0,
    omega: float = 0.5,
    et_matrix: Optional[List[List[float]]] = None,
) -> Schedule:
    """
    Runs Rodriguez & Buyya PSO with cost-only fitness and Deb's constraint handling.
    """
    start_time = time.perf_counter()
    if rng is None:
        rng = random.Random(42)
    if et_matrix is None:
        et_matrix = compute_execution_time(wf, pool)

    n_tasks = wf.n
    k_vms = len(pool)
    v_max = k_vms / 4.0
    order = wf.order

    # Initialize swarm randomly
    swarm_x: List[List[float]] = []
    swarm_v: List[List[float]] = []
    pbest_x: List[List[float]] = []
    pbest_sched: List[Schedule] = []
    pbest_cost: List[float] = []

    for _ in range(pop_size):
        x = [rng.uniform(0.0, k_vms - 1e-6) for _ in range(n_tasks)]
        v = [rng.uniform(-v_max, v_max) for _ in range(n_tasks)]
        mapping = [int(val) for val in x]
        sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)

        swarm_x.append(x)
        swarm_v.append(v)
        pbest_x.append(list(x))
        pbest_sched.append(sched)
        pbest_cost.append(sched.cost)

    # Find initial gbest using Deb's rules (smaller cost wins among feasible)
    gbest_idx = 0
    for i in range(1, pop_size):
        # In compare_schedules_deb, f is cost
        cmp = compare_schedules_deb(pbest_sched[i], pbest_sched[gbest_idx], pbest_cost[i], pbest_cost[gbest_idx])
        if cmp < 0:
            gbest_idx = i

    gbest_x = list(pbest_x[gbest_idx])
    gbest_sched = pbest_sched[gbest_idx]
    gbest_cost = pbest_cost[gbest_idx]

    # PSO Optimization Loop
    for t in range(iterations):
        for i in range(pop_size):
            # Update velocity and position
            for d in range(n_tasks):
                r1 = rng.random()
                r2 = rng.random()
                swarm_v[i][d] = (
                    omega * swarm_v[i][d]
                    + c1 * r1 * (pbest_x[i][d] - swarm_x[i][d])
                    + c2 * r2 * (gbest_x[d] - swarm_x[i][d])
                )
                # Clamp velocity
                if swarm_v[i][d] > v_max:
                    swarm_v[i][d] = v_max
                elif swarm_v[i][d] < -v_max:
                    swarm_v[i][d] = -v_max

                swarm_x[i][d] += swarm_v[i][d]
                # Clamp position
                if swarm_x[i][d] < 0.0:
                    swarm_x[i][d] = 0.0
                elif swarm_x[i][d] >= k_vms:
                    swarm_x[i][d] = k_vms - 1e-6

            # Evaluate
            mapping = [int(val) for val in swarm_x[i]]
            sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)
            cost = sched.cost

            # Update pbest by Deb's rules
            cmp_p = compare_schedules_deb(sched, pbest_sched[i], cost, pbest_cost[i])
            if cmp_p < 0:
                pbest_x[i] = list(swarm_x[i])
                pbest_sched[i] = sched
                pbest_cost[i] = cost

                # Check gbest
                cmp_g = compare_schedules_deb(sched, gbest_sched, cost, gbest_cost)
                if cmp_g < 0:
                    gbest_x = list(swarm_x[i])
                    gbest_sched = sched
                    gbest_cost = cost

    gbest_sched.runtime_s = time.perf_counter() - start_time
    return gbest_sched
