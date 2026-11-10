"""
Plain PSO Workflow Scheduler (Ablation Baseline).
Multi-objective PSO with random initialization, no duplication, Deb's feasibility rules.
(README Section 6.3)
"""
import time
import random
from typing import List, Tuple, Optional
from ..model.workflow import Workflow
from ..model.vm import VMInstance
from ..model.schedule import Schedule
from ..builder import (
    build_schedule,
    compute_execution_time,
    compare_schedules_deb,
)


def compute_objective_f(
    sched: Schedule,
    c_ref: float,
    e_ref: float,
    m_ref: float,
    w1: float = 1.0 / 3.0,
    w2: float = 1.0 / 3.0,
    w3: float = 1.0 / 3.0,
) -> float:
    """Computes normalized fitness F = w1*(C/C_ref) + w2*(E/E_ref) + w3*(M/M_ref)."""
    c_term = (sched.cost / c_ref) if c_ref > 0 else 1.0
    e_term = (sched.energy / e_ref) if e_ref > 0 else 1.0
    m_term = (sched.makespan / m_ref) if m_ref > 0 else 1.0
    return w1 * c_term + w2 * e_term + w3 * m_term


def schedule_pso_plain(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: float,
    c_ref: float,
    e_ref: float,
    m_ref: float,
    rng: Optional[random.Random] = None,
    pop_size: int = 30,
    iterations: int = 100,
    c1: float = 2.0,
    c2: float = 2.0,
    omega_max: float = 0.9,
    omega_min: float = 0.4,
    w1: float = 1.0 / 3.0,
    w2: float = 1.0 / 3.0,
    w3: float = 1.0 / 3.0,
    et_matrix: Optional[List[List[float]]] = None,
) -> Schedule:
    """
    Runs Plain PSO with random initialization and no duplication.
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

    swarm_x: List[List[float]] = []
    swarm_v: List[List[float]] = []
    pbest_x: List[List[float]] = []
    pbest_sched: List[Schedule] = []
    pbest_f: List[float] = []

    for _ in range(pop_size):
        x = [rng.uniform(0.0, k_vms - 1e-6) for _ in range(n_tasks)]
        v = [rng.uniform(-v_max, v_max) for _ in range(n_tasks)]
        mapping = [int(val) for val in x]
        sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)
        f_val = compute_objective_f(sched, c_ref, e_ref, m_ref, w1, w2, w3)

        swarm_x.append(x)
        swarm_v.append(v)
        pbest_x.append(list(x))
        pbest_sched.append(sched)
        pbest_f.append(f_val)

    # Initial gbest
    gbest_idx = 0
    for i in range(1, pop_size):
        if compare_schedules_deb(pbest_sched[i], pbest_sched[gbest_idx], pbest_f[i], pbest_f[gbest_idx]) < 0:
            gbest_idx = i

    gbest_x = list(pbest_x[gbest_idx])
    gbest_sched = pbest_sched[gbest_idx]
    gbest_f = pbest_f[gbest_idx]

    # Optimization loop
    for t in range(iterations):
        omega = omega_max - (omega_max - omega_min) * (t / float(iterations))
        for i in range(pop_size):
            for d in range(n_tasks):
                r1 = rng.random()
                r2 = rng.random()
                swarm_v[i][d] = (
                    omega * swarm_v[i][d]
                    + c1 * r1 * (pbest_x[i][d] - swarm_x[i][d])
                    + c2 * r2 * (gbest_x[d] - swarm_x[i][d])
                )
                if swarm_v[i][d] > v_max:
                    swarm_v[i][d] = v_max
                elif swarm_v[i][d] < -v_max:
                    swarm_v[i][d] = -v_max

                swarm_x[i][d] += swarm_v[i][d]
                if swarm_x[i][d] < 0.0:
                    swarm_x[i][d] = 0.0
                elif swarm_x[i][d] >= k_vms:
                    swarm_x[i][d] = k_vms - 1e-6

            mapping = [int(val) for val in swarm_x[i]]
            sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)
            f_val = compute_objective_f(sched, c_ref, e_ref, m_ref, w1, w2, w3)

            if compare_schedules_deb(sched, pbest_sched[i], f_val, pbest_f[i]) < 0:
                pbest_x[i] = list(swarm_x[i])
                pbest_sched[i] = sched
                pbest_f[i] = f_val

                if compare_schedules_deb(sched, gbest_sched, f_val, gbest_f) < 0:
                    gbest_x = list(swarm_x[i])
                    gbest_sched = sched
                    gbest_f = f_val

    gbest_sched.runtime_s = time.perf_counter() - start_time
    return gbest_sched
