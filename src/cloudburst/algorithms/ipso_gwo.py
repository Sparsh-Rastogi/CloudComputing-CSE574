"""
IPSO-GWO: Hybrid Improved PSO and Grey Wolf Optimizer for Workflow Scheduling.
(Samar Awad et al., Scientific Reports 16:4359, Jan 2026; Recent Paper 2)
Our implementation adapted to the shared model and fixed pool.
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
from .pso_plain import compute_objective_f


def schedule_ipso_gwo(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: float,
    c_ref: float,
    e_ref: float,
    m_ref: float,
    rng: Optional[random.Random] = None,
    pop_size: int = 25,
    iterations: int = 100,
    c1: float = 2.0,
    c2: float = 2.0,
    w_begin: float = 0.8,
    w_end: float = 0.3,
    et_matrix: Optional[List[List[float]]] = None,
) -> Schedule:
    """
    Runs hybrid IPSO-GWO: Phase 1 (IPSO) runs for maxIter/2, Phase 2 (GWO) runs for remaining.
    """
    start_time = time.perf_counter()
    if rng is None:
        rng = random.Random(42)
    if et_matrix is None:
        et_matrix = compute_execution_time(wf, pool)

    n_tasks = wf.n
    k_vms = len(pool)
    v_max = (k_vms - 1) / 2.0
    order = wf.order

    half_iter = iterations // 2

    # --- Phase 1: IPSO Initialization ---
    pop_x: List[List[float]] = []
    pop_v: List[List[float]] = []
    pbest_x: List[List[float]] = []
    pbest_sched: List[Schedule] = []
    pbest_f: List[float] = []

    for _ in range(pop_size):
        x = [rng.uniform(0.0, k_vms - 1e-6) for _ in range(n_tasks)]
        v = [rng.uniform(-v_max, v_max) for _ in range(n_tasks)]
        mapping = [int(val) for val in x]
        sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)
        f_val = compute_objective_f(sched, c_ref, e_ref, m_ref)

        pop_x.append(x)
        pop_v.append(v)
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

    # --- Phase 1: IPSO Loop (1 to half_iter) ---
    for t in range(half_iter):
        # LDIW inertia weight (Eq. 11)
        w = w_end + (w_begin - w_end) * ((iterations - t) / float(iterations))
        for i in range(pop_size):
            for d in range(n_tasks):
                r1 = rng.random()
                r2 = rng.random()
                pop_v[i][d] = (
                    w * pop_v[i][d]
                    + c1 * r1 * (pbest_x[i][d] - pop_x[i][d])
                    + c2 * r2 * (gbest_x[d] - pop_x[i][d])
                )
                pop_v[i][d] = max(-v_max, min(v_max, pop_v[i][d]))
                pop_x[i][d] += pop_v[i][d]
                pop_x[i][d] = max(0.0, min(k_vms - 1e-6, pop_x[i][d]))

            mapping = [int(val) for val in pop_x[i]]
            sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)
            f_val = compute_objective_f(sched, c_ref, e_ref, m_ref)

            if compare_schedules_deb(sched, pbest_sched[i], f_val, pbest_f[i]) < 0:
                pbest_x[i] = list(pop_x[i])
                pbest_sched[i] = sched
                pbest_f[i] = f_val

                if compare_schedules_deb(sched, gbest_sched, f_val, gbest_f) < 0:
                    gbest_x = list(pop_x[i])
                    gbest_sched = sched
                    gbest_f = f_val

    # --- Switch to Phase 2: GWO Initialization ---
    # Alpha wolf = gbest
    # Other wolves: slightly perturbed versions around gbest and random pbests (I6)
    wolves: List[List[float]] = [list(gbest_x)]
    wolf_sched: List[Schedule] = [gbest_sched]
    wolf_f: List[float] = [gbest_f]

    for i in range(1, pop_size):
        source = gbest_x if rng.random() < 0.5 else pbest_x[i]
        mutated = list(source)
        for d in range(n_tasks):
            if rng.random() < 0.1:
                mutated[d] = rng.uniform(0.0, k_vms - 1e-6)
        mapping = [int(val) for val in mutated]
        sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)
        f_val = compute_objective_f(sched, c_ref, e_ref, m_ref)

        wolves.append(mutated)
        wolf_sched.append(sched)
        wolf_f.append(f_val)

    # --- Phase 2: GWO Loop (half_iter to iterations) ---
    for t in range(half_iter, iterations):
        # Sort wolves to find alpha, beta, delta
        indices = list(range(pop_size))
        # Custom comparator using Deb's rules
        from functools import cmp_to_key
        def deb_cmp(idx1, idx2):
            return compare_schedules_deb(wolf_sched[idx1], wolf_sched[idx2], wolf_f[idx1], wolf_f[idx2])

        indices.sort(key=cmp_to_key(deb_cmp))
        alpha_idx, beta_idx, delta_idx = indices[0], indices[1], indices[2]

        alpha_x = wolves[alpha_idx]
        beta_x = wolves[beta_idx]
        delta_x = wolves[delta_idx]

        # a linearly decreases from 2 to 0 over Phase 2
        phase2_t = t - half_iter
        phase2_total = max(1, iterations - half_iter)
        a = 2.0 - 2.0 * (phase2_t / float(phase2_total))

        for i in range(pop_size):
            new_x = [0.0] * n_tasks
            for d in range(n_tasks):
                # Alpha encircling
                r1, r2 = rng.random(), rng.random()
                A1 = 2.0 * a * r1 - a
                C1 = 2.0 * r2
                D_alpha = abs(C1 * alpha_x[d] - wolves[i][d])
                X1 = alpha_x[d] - A1 * D_alpha

                # Beta encircling
                r1, r2 = rng.random(), rng.random()
                A2 = 2.0 * a * r1 - a
                C2 = 2.0 * r2
                D_beta = abs(C2 * beta_x[d] - wolves[i][d])
                X2 = beta_x[d] - A2 * D_beta

                # Delta encircling
                r1, r2 = rng.random(), rng.random()
                A3 = 2.0 * a * r1 - a
                C3 = 2.0 * r2
                D_delta = abs(C3 * delta_x[d] - wolves[i][d])
                X3 = delta_x[d] - A3 * D_delta

                # Average position (Eq. 17)
                pos = (X1 + X2 + X3) / 3.0
                new_x[d] = max(0.0, min(k_vms - 1e-6, pos))

            wolves[i] = new_x
            mapping = [int(val) for val in new_x]
            sched = build_schedule(wf, pool, mapping, order=order, deadline=deadline, et_matrix=et_matrix)
            f_val = compute_objective_f(sched, c_ref, e_ref, m_ref)
            wolf_sched[i] = sched
            wolf_f[i] = f_val

            # Check overall gbest
            if compare_schedules_deb(sched, gbest_sched, f_val, gbest_f) < 0:
                gbest_sched = sched
                gbest_f = f_val

    gbest_sched.runtime_s = time.perf_counter() - start_time
    return gbest_sched
