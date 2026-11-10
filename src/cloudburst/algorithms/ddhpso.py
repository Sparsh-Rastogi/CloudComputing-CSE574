"""
DD-HPSO: Deadline-Aware, Duplication-Enabled, HEFT-Seeded Particle Swarm Optimization.
Proposed scheduler combining HEFT seeding, sub-deadline duplication triggers,
cost threshold theta_C=0, energy threshold theta_E=5%, and Deb's feasibility rules.
(README Section 7)
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
from .heft import schedule_heft
from .pso_plain import compute_objective_f


def schedule_ddhpso(
    wf: Workflow,
    pool: List[VMInstance],
    deadline: float,
    heft_sched: Optional[Schedule] = None,
    heft_mapping: Optional[List[int]] = None,
    rng: Optional[random.Random] = None,
    pop_size: int = 30,
    iterations: int = 100,
    c1: float = 2.0,
    c2: float = 2.0,
    omega_max: float = 0.9,
    omega_min: float = 0.4,
    p_mut: float = 0.1,
    theta_e: float = 0.05,
    w1: float = 1.0 / 3.0,
    w2: float = 1.0 / 3.0,
    w3: float = 1.0 / 3.0,
    et_matrix: Optional[List[List[float]]] = None,
) -> Schedule:
    """
    Runs DD-HPSO scheduling algorithm.
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

    # Step 1: Run HEFT if not passed
    if heft_sched is None or heft_mapping is None:
        heft_sched, heft_mapping = schedule_heft(wf, pool, deadline=deadline, et_matrix=et_matrix)

    m_heft = max(1e-6, heft_sched.makespan)
    c_ref = max(1e-6, heft_sched.cost)
    e_ref = max(1e-6, heft_sched.energy)
    m_ref = m_heft

    # Step 2: Sub-deadlines (SD_i = AFT_HEFT(i) * D / M_HEFT)
    task_heft_finish = [0.0] * n_tasks
    for p in heft_sched.placements:
        if not p.is_dup:
            task_heft_finish[p.task] = p.finish

    sub_deadlines = [(task_heft_finish[i] * deadline / m_heft) for i in range(n_tasks)]

    # Step 3: Swarm Seeding (README Section 7.2)
    swarm_x: List[List[float]] = []
    swarm_v: List[List[float]] = []
    pbest_x: List[List[float]] = []
    pbest_sched: List[Schedule] = []
    pbest_f: List[float] = []

    # Particle 1: HEFT particle
    p1 = [heft_mapping[i] + 0.5 for i in range(n_tasks)]
    v1 = [0.0 for _ in range(n_tasks)]
    mapping1 = [int(val) for val in p1]

    # Evaluate particle 1 with duplication enabled
    s1 = build_schedule(
        wf=wf,
        pool=pool,
        mapping=mapping1,
        order=order,
        deadline=deadline,
        et_matrix=et_matrix,
        enable_duplication=True,
        sub_deadlines=sub_deadlines,
        e_ref=e_ref,
        theta_e=theta_e,
    )
    f1 = compute_objective_f(s1, c_ref, e_ref, m_ref, w1, w2, w3)

    swarm_x.append(p1)
    swarm_v.append(v1)
    pbest_x.append(list(p1))
    pbest_sched.append(s1)
    pbest_f.append(f1)

    # Particles 2..N: perturbed copies of Particle 1
    for _ in range(1, pop_size):
        px = list(p1)
        pv = [0.0 for _ in range(n_tasks)]
        for d in range(n_tasks):
            if rng.random() < p_mut:
                px[d] = rng.uniform(0.0, k_vms - 1e-6)
        mapping = [int(val) for val in px]
        s = build_schedule(
            wf=wf,
            pool=pool,
            mapping=mapping,
            order=order,
            deadline=deadline,
            et_matrix=et_matrix,
            enable_duplication=True,
            sub_deadlines=sub_deadlines,
            e_ref=e_ref,
            theta_e=theta_e,
        )
        f = compute_objective_f(s, c_ref, e_ref, m_ref, w1, w2, w3)

        swarm_x.append(px)
        swarm_v.append(pv)
        pbest_x.append(list(px))
        pbest_sched.append(s)
        pbest_f.append(f)

    # Initial gbest by Deb's rules
    gbest_idx = 0
    for i in range(1, pop_size):
        if compare_schedules_deb(pbest_sched[i], pbest_sched[gbest_idx], pbest_f[i], pbest_f[gbest_idx]) < 0:
            gbest_idx = i

    gbest_x = list(pbest_x[gbest_idx])
    gbest_sched = pbest_sched[gbest_idx]
    gbest_f = pbest_f[gbest_idx]

    # Step 4: PSO Loop
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
            sched = build_schedule(
                wf=wf,
                pool=pool,
                mapping=mapping,
                order=order,
                deadline=deadline,
                et_matrix=et_matrix,
                enable_duplication=True,
                sub_deadlines=sub_deadlines,
                e_ref=e_ref,
                theta_e=theta_e,
            )
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
