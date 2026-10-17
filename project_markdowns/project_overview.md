# CloudBurst: Project Overview

**Course:** CSE-574 Cloud Computing
**Title:** CloudBurst: Deadline-Aware, Duplication-Enabled, HEFT-Seeded PSO for Cost and Energy Efficient Scientific Workflow Scheduling
**Author:** [Name] | [Roll Number] | [Branch]
**Status:** 1st Evaluation (design and literature stage). Implementation and results are planned for the 2nd Evaluation.

> **Note on the name:** "CloudBurst" is a project brand. The project schedules workflows on cloud VMs; it does not deal with hybrid-cloud overflow ("cloud bursting"). The subtitle defines the method.

**Paper key** (same numbering as the slides)
- [1] Genez et al., *Scheduling Scientific Workflows on Clouds Using a Task Duplication Approach* (IEEE/ACM UCC 2018)
- [2] Rodriguez and Buyya, *Deadline Based Resource Provisioning and Scheduling Algorithm for Scientific Workflows on Clouds* (IEEE TCC 2014)
- [3] Li et al., *Cost and Energy Aware Scheduling Algorithm for Scientific Workflows with Deadline Constraint in Clouds* (CEAS) (IEEE TSC 2018)

---

## 1. Background and Problem (Slide 2)

Scientific workflows such as Montage, CyberShake, Epigenomics and LIGO are directed acyclic graphs (DAGs) of dependent tasks. Running them on an IaaS cloud means deciding which VMs to use and which task runs where. Cloud features that make this hard:

- VMs are **heterogeneous** (different speed and price).
- VMs are **billed per time period** (for example hourly), so a partly used period is still paid for.
- VMs have a **boot delay** before they can run tasks.
- Data moving between dependent tasks on different VMs leaves VMs idle.

A poor schedule wastes money, energy and time. The problem is to map tasks to VMs so that the **deadline is met** while **cost and energy are minimized**.

## 2. Literature Summary and Research Gap (Slides 3 to 5)

| Paper | What it contributes | Main gaps |
|---|---|---|
| [1] Genez et al. | HEFT-TD and Lookahead-TD: duplicate a task's critical parent on a candidate VM, keep the copy only if finish time improves. About 9% (HEFT-TD) and 12% (Lookahead-TD) lower makespan on average. | No deadline or budget; cost-unaware (cost rose +10% to +45% for some workflows under HEFT-TD); uneven gains; about 10 to 100 times slower; no boot time or hourly billing. |
| [2] Rodriguez and Buyya | PSO that jointly decides provisioning and scheduling; one dimension per task, integer part is VM index; cost fitness under hourly billing; Deb's rules for the deadline; models boot time (97 s) and variability. | Slow and variable between runs; sensitive to the initial VM pool; no energy awareness; no duplication; static schedule; only two baselines. |
| [3] Li et al. (CEAS) | Five chained polynomial-time steps: deadline split into sub-makespans, cost-utility VM choice, sequence and parallel merging, VM reuse, DVFS slack reclamation. Lowest cost and energy among its baselines (shown in plots only). | Greedy, no optimality guarantee; no duplication; assumes tenants control CPU frequency (DVFS); models only dynamic CPU energy; no boot time or variability; narrow baselines. |

**Combined research gap.** No existing approach combines task duplication, deadline-aware cost minimization under billing periods, and energy awareness inside a global search. [1] ignores deadline and cost, [2] ignores energy and duplication, and [3] is greedy with no duplication.

## 3. Aim

To design and evaluate a scheduling algorithm that fills this combined gap: a single global-search scheduler that handles deadline, billing-period cost, energy and task duplication together.

## 4. Objectives

1. **Build a realistic cost model.** Include boot time and billing-period rounding, as in [2] and [3].
2. **Add a tenant-side energy model.** Use busy and idle power, so no DVFS control is needed (unlike [3]).
3. **Seed the search with HEFT.** Start PSO from a strong schedule so that it needs fewer wasted iterations and varies less between runs (the weakness noted in [2]).
4. **Use cost-aware duplication.** Duplicate a parent task only when it lowers the child's finish time and the extra cost and energy stay under a threshold, preferring slots inside already-paid billing time. This targets the cost increases seen in [1].
5. **Handle the deadline without a penalty weight.** Use Deb's feasibility rules, as in [2].
6. **Evaluate by simulation.** Compare against classical heuristics, the three papers' approaches where feasible, and recent (2025/2026) work.

## 5. Core Idea (Slides 6 to 9)

CloudBurst is **DD-HPSO** (Deadline-aware, Duplication-enabled, HEFT-seeded PSO). Pipeline (slide 8):

1. **Input:** DAG, VM catalog, deadline D.
2. **Deadline distribution:** give each task a sub-deadline.
3. **HEFT seeding:** the initial swarm has one HEFT particle plus N-1 perturbed copies.
4. **PSO search with selective duplication:** each particle is decoded into a schedule, duplication is applied, and the schedule is evaluated.
5. **Output:** best schedule with cost, energy, makespan and utilization.

### Building blocks

- **HEFT (slide 6).** Ranks tasks by upward rank, then assigns each to the VM with the earliest finish time. Used here as the seed and as a baseline. It optimizes only makespan.
- **PSO (slide 7).** Particles are full task-to-VM mappings. Velocity and position updates pull each particle toward its personal best and the swarm best. Inertia decreases over iterations (explore early, refine late).
- **Selective duplication (slide 8).** For each task in topological order, consider its critical parents on other VMs. Duplicate a parent onto the task's VM only if an idle slot fits, the task's finish time drops, and the extra cost and energy are below a threshold.

### Mathematical model (slide 9)

| Quantity | Formula | Role |
|---|---|---|
| Execution time | `ET(i,k) = L_i / s_k` | Task length over VM speed |
| Transfer time | `TT(i,j) = d_ij / B` (0 on same VM) | Cost of data movement; duplication removes it |
| Finish time | `AFT(i) = EST(i) + ET(i,k)` | VM available only after boot time |
| Makespan | `M = AFT(t_exit)` | Compared with deadline D |
| Cost | `C = Σ ceil((T_end - T_start)/τ) · p_k` | Leased time (including boot) rounded up to billing periods |
| Energy | `E = Σ (P_busy·T_busy + P_idle·T_idle)` | Busy and idle power, no DVFS |
| Utilization | `U = busy time / leased time` | Reported metric |
| Sub-deadline | `SD_i = AFT_HEFT(i) · D / M_HEFT` | HEFT-based variant of the sub-makespan idea in [3] |

**Objective:**

```
min F = w1·(C / C_ref) + w2·(E / E_ref) + w3·(M / M_ref)
subject to  M <= D,  precedence satisfied,  w1 + w2 + w3 = 1
```

The reference values come from the HEFT schedule, so `F = 1.0` means "same as HEFT". Normalizing makes the three terms comparable so the weights work as intended.

**Deadline handling (Deb's rules, as in [2]).** With violation `V = max(0, M - D)`: a feasible solution beats an infeasible one; between two feasible ones the smaller F wins; between two infeasible ones the smaller V wins.

## 6. Expected Contributions (Slide 10)

These are **hypotheses to be tested**, not results.

- HEFT seeding should reduce PSO's slowness and run-to-run variability [2].
- Cost-, energy- and deadline-aware duplication should avoid the cost increases seen in [1].
- One objective balances cost, energy and makespan, without needing DVFS control [3].
- **Trade-off:** longer scheduling time than pure heuristics.

Feature comparison (from slide 10):

| Feature | HEFT / Min-Min / Max-Min | [1] | [2] | [3] | CloudBurst |
|---|---|---|---|---|---|
| Deadline-aware | No | No | Yes | Yes | Yes |
| Cost-aware | No | No (incidental) | Yes | Yes | Yes |
| Energy-aware | No | No | No | Yes (DVFS) | Yes (busy/idle) |
| Task duplication | No | Yes (finish-time driven) | No | No | Yes (cost and deadline aware) |
| Global search | No | No | Yes | No | Yes |
| Boot time and billing periods | No | No | Yes | Billing only | Yes |
| Heuristic-seeded start | n/a | n/a | No | n/a | Yes |

## 7. Implementation and Evaluation Plan (Slide 11)

Pipeline: workflow input, algorithm implementation, simulation, comparison and analysis.

- **Simulator:** WorkflowSim (built on CloudSim).
- **Workflows:** Pegasus Montage, CyberShake, Epigenomics and LIGO, at varying sizes.
- **Baselines:** HEFT, Min-Min, Max-Min, plain PSO, algorithms from [1] to [3] where feasible, and recent (2025/2026) papers.
- **Metrics:** makespan, cost, energy, utilization, deadline success rate.

## 8. Deliverables

| # | Deliverable | Stage |
|---|---|---|
| 1 | Literature review of three papers with gap analysis | 1st Evaluation (done) |
| 2 | Algorithm design: architecture, pseudocode, duplication rule | 1st Evaluation (done) |
| 3 | Mathematical model and objective function | 1st Evaluation (done) |
| 4 | Presentation (11 slides) | 1st Evaluation (done) |
| 5 | Implementation of CloudBurst (DD-HPSO) in WorkflowSim | 2nd Evaluation |
| 6 | Implementations or reuse of baselines for comparison | 2nd Evaluation |
| 7 | Experimental results: tables and plots for all metrics | 2nd Evaluation |
| 8 | Analysis of results, including scheduling-time overhead | 2nd Evaluation |
| 9 | Final report | [TO FILL] |

## 9. Open Items [TO FILL]

These are not fixed in the current documents and must be decided before implementation:

- Objective weights `w1`, `w2`, `w3` (for example equal weights, or a sweep).
- PSO parameters: swarm size N, iterations I, inertia range `w_min` to `w_max`, `c1`, `c2`.
- Duplication threshold for extra cost and energy.
- VM catalog: types, speeds, prices, billing period, power values, boot time.
- Deadline settings (how D is chosen relative to the HEFT makespan).
- Which recent (2025/2026) papers to use as baselines.

## 10. Risks and Limitations

- **Runtime:** duplication made [1] about 10 to 100 times slower and PSO is already slow, so the implementation may need to limit how often duplication runs.
- **Duplication novelty:** [1] already keeps a duplicate only if finish time improves. The difference here is that the decision also weighs cost, energy and deadline, inside a global search.
- **Sub-deadlines:** distributing the deadline is an idea from [3] (proportional to fastest runtime); CloudBurst scales HEFT finish times instead.
- **Static schedule:** like all three papers, the schedule is computed offline and does not adapt at runtime.
- **Simulation only:** results will come from simulation, not a real cloud.
- **Claims:** all improvements are expected outcomes until verified in the 2nd Evaluation.