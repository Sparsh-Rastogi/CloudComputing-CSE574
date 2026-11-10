# CloudBurst: DD-HPSO and Baseline Schedulers (Python)

**Course:** CSE-574 Cloud Computing
**Method:** DD-HPSO, a Deadline-aware, Duplication-enabled, HEFT-seeded Particle Swarm Optimization scheduler for cost- and energy-efficient scientific workflow scheduling on IaaS clouds.
**Status:** Design stage (1st Evaluation). Everything below is a **specification to implement**. No result in this file is measured; all performance statements are hypotheses until the 2nd Evaluation.
**Document version:** v2. All earlier open choices are now resolved in [Section 2 (Decision Log)](#2-decision-log). Where a choice was open, the rule used was: *pick whatever is simplest to implement and simplest to compare fairly.*

> "CloudBurst" is a project brand. The project schedules workflows on cloud VMs; it does not deal with hybrid-cloud overflow.

---

## Table of Contents

1. [Goal and scope](#1-goal-and-scope)
2. [Decision log](#2-decision-log)
3. [Repository layout and environment](#3-repository-layout-and-environment)
4. [System model and formulas](#4-system-model-and-formulas)
5. [Core interfaces and the shared schedule builder](#5-core-interfaces-and-the-shared-schedule-builder)
6. [Classical baselines](#6-classical-baselines)
7. [DD-HPSO (proposed method)](#7-dd-hpso-proposed-method)
8. [Re-implementing the three reference papers](#8-re-implementing-the-three-reference-papers)
9. [Recent (2025/2026) baselines](#9-recent-20252026-baselines)
10. [Experiment design](#10-experiment-design)
11. [Results format and dashboard](#11-results-format-and-dashboard)
12. [Parameter values](#12-parameter-values)
13. [Validation and testing](#13-validation-and-testing)
14. [Known risks and limitations](#14-known-risks-and-limitations)
15. [Remaining items that still need action](#15-remaining-items-that-still-need-action)
16. [References](#16-references)

---

## 1. Goal and scope

Map the tasks of a workflow DAG to heterogeneous cloud VMs so that:

- the **deadline** `D` is met (hard constraint),
- **cost** `C` and **energy** `E` are minimized, with makespan `M` as a third term,
- the schedule is **static** (computed offline, no runtime adaptation).

No existing approach combines task duplication, deadline-aware cost minimization under billing periods, and energy awareness inside a global search ([1] ignores deadline and cost, [2] ignores energy and duplication, [3] is greedy with no duplication). DD-HPSO targets that gap.

**Hypotheses to test (not results):**

- H1: HEFT seeding reduces PSO's slowness and run-to-run variability (weakness noted in [2]).
- H2: Cost-, energy- and deadline-aware duplication avoids the cost increases seen in [1].
- H3: One normalized objective balances cost, energy and makespan without DVFS control.
- Trade-off: longer scheduling time than pure heuristics.

---

## 2. Decision log

These decisions are **final for the project** unless this table is edited with a dated note. Each row records what was chosen, why, and what was rejected. Any change after experiments start must be reported in the final report.

| ID | Topic | Decision | Reason (simplicity / fair comparison) | Rejected alternative |
|---|---|---|---|---|
| D1 | Language and simulator | **Python 3.10+ only.** Own lightweight event-free simulator (the "builder", Section 5). No WorkflowSim, no Java. | One codebase for algorithms, experiments and dashboard. The custom model (boot, billing, energy, duplication) would need heavy WorkflowSim changes anyway. | WorkflowSim (Java) |
| D2 | Workflow data | Pegasus workflow files (Montage, CyberShake, Epigenomics, LIGO) parsed from DAX (XML) with `xml.etree`. Task length = Pegasus runtime in seconds on a reference machine of speed 1. Data sizes from file sizes. | Real, standard workflows, same as the papers use. | Synthetic generator (kept only as a fallback if files cannot be obtained) |
| D3 | Single exit assumption | Makespan `M = max over all tasks of AFT`, not "AFT of exit task". | Pegasus DAGs may have several exit tasks. | Adding a virtual exit node |
| D4 | VM pool | **One fixed pool shared by every algorithm.** 4 VM types, 5 instances per type (20 VMs) for workflows with at most 100 tasks, 10 per type (40 VMs) above that. Only VMs that actually run tasks are leased and billed. | All algorithms choose among the same VMs, so differences come from the algorithm, not provisioning. Simple encoding (VM index). | Each algorithm provisions its own pool (as [2] and [3] do) |
| D5 | Lease model | A VM is leased from `first_start - β` to the finish of its last task, **continuously** (idle gaps in between are still billed). No output-data transfer after the last task. | Simple and consistent for all algorithms. | Releasing and re-leasing VMs mid-run |
| D6 | Boot time | `β = 97 s` (value from [2]) for every VM. Every VM's first task cannot start before `β`. Boot time is billed and counted as **idle power**. | One number, no separate boot-power parameter. | A separate boot power |
| D7 | Billing | Period `τ = 3600 s`, rounded up per VM. | Hourly billing is the model in [2] and [3]. | Per-second billing |
| D8 | Network | One bandwidth `B = 100 MB/s` between any two different VMs; zero transfer on the same VM; **no contention**. Input data of entry tasks is ignored. | Simple, deterministic. | Per-link bandwidth, contention models |
| D9 | Performance variability | **Not modeled.** Execution times are deterministic. | Keeps results reproducible; [1] and [3] also ignore it. | Variability as in [2] |
| D10 | Energy | `E = Σ (P_busy·T_busy + P_idle·T_idle)` per leased VM; duplicates count as busy; no DVFS; no network energy. | Tenant-side model needing no DVFS control. | DVFS (as in [3]) |
| D11 | VM catalog | Four illustrative types (Section 12). Price proportional to speed; idle power = 60% of busy power. **These numbers are assumptions, not taken from the papers.** | Linear scaling is the simplest consistent catalog. Report them as assumptions. | Copying a real provider's price list |
| D12 | Task order in PSO | **Fixed** order = HEFT upward-rank order (topological). The particle encodes only the task-to-VM mapping. | Halves the search space, simpler decoder. | Encoding task priorities in the particle |
| D13 | Particle encoding | One real dimension per task, `x_i ∈ [0, K)`, VM index `floor(x_i)`, as in [2]. | Matches [2], easy to implement. | Permutation or discrete encodings |
| D14 | Sub-deadlines | `SD_i = AFT_HEFT(i) · D / M_HEFT` is used **only as a duplication trigger**: duplication is attempted for task `i` only if its un-duplicated finish time exceeds `SD_i`. It is not part of the fitness or of Deb's violation. Switch-off flag gives an ablation. | Cheap, uses the deadline distribution meaningfully, and cuts runtime by skipping tasks that are already on time. | Using `SD_i` as an extra violation term |
| D15 | Duplication depth | **One level**: only the critical parent of a task. | Bounded runtime, simplest rule. | Recursive duplication of ancestors |
| D16 | Duplication thresholds | `θ_C = 0` (a duplicate may never increase that VM's billed cost) and cumulative extra energy from duplicates `≤ θ_E = 5%` of `E_ref`. | Strictest cost rule, one tunable number only. Directly targets the cost increases seen in [1]. | Per-duplicate relative thresholds |
| D17 | Objective weights | Equal weights `w1 = w2 = w3 = 1/3` in the main grid. A small sensitivity check (Section 10.5) tests other weights. | One setting to compare. | A full weight sweep over the grid |
| D18 | Deadline handling | Deb's feasibility rules (as in [2]); no penalty weight. | Specified by the project. | Penalty functions |
| D19 | Search budget | Every PSO-based algorithm gets the **same fitness-evaluation budget**: swarm `N = 30`, iterations `I = 100` (3000 evaluations). If measured run time on the largest workflows is too high, `I` is reduced **for all PSO-based algorithms equally** and documented. | Equal budget is the simplest fair comparison. | Equal wall-clock time |
| D20 | Seeds and statistics | 10 seeds per stochastic algorithm per case. Wilcoxon signed-rank test (SciPy) over per-case mean results. | Standard, cheap. | 30 seeds, performance profiles (profiles kept optional) |
| D21 | Test grid | 4 workflows × 3 sizes (about 50, 100, 1000 tasks; nearest sizes available in the gallery) × 3 deadline factors (1.2, 1.5, 2.0 × `M_HEFT`) = 36 cases. Fixed before any run. | Matches the evaluation plan. | Dense/sparse custom categories |
| D22 | Reference [1] | Implement **HEFT-TD** first. Lookahead-TD is a stretch goal. | HEFT-TD is a small extension of HEFT. | Both from the start |
| D23 | Reference [2] | Implement as PSO with **cost-only fitness**, Deb's rules, random initialization, same encoding (D13) and same budget (D19). Details to be confirmed against the PDF. | Shares code with plain PSO. | Rebuilding its own VM provisioning |
| D24 | Reference [3] | Implement CEAS **steps 1 to 4**; **step 5 (DVFS) dropped**; labeled "CEAS without DVFS". Runs on the fixed pool (D4), "VM reuse" means choosing among pool instances. | DVFS is outside the tenant model (D10). | Modeling DVFS only for this baseline |
| D25 | Recent baselines | Target **2** papers, chosen by the screening checklist in Section 9. If fewer than 2 pass, use fewer. | Two well-reproduced baselines beat three shaky ones. | Always taking 3 |
| D26 | Tie-breaking | Lowest VM index, then lowest task id, for every deterministic algorithm. | Reproducibility. | Random ties |
| D27 | Dashboard | **Streamlit + Plotly**, reading `results/` only; built last. | Python only, no front-end build chain. | JS front end |
| D28 | Parallelism | `multiprocessing` over (case, algorithm, seed) jobs. No Numba or C extensions initially. | Simple. Optimize only after profiling. | Numba from the start |

---

## 3. Repository layout and environment

```
cloudburst/
├── README.md
├── requirements.txt          # numpy, scipy, pandas, matplotlib, networkx, streamlit, plotly, pytest
├── data/
│   ├── workflows/            # Pegasus DAX files
│   └── vm_catalog.json       # Section 12
├── src/cloudburst/
│   ├── model/
│   │   ├── workflow.py       # DAX parser, topological order, upward rank
│   │   ├── vm.py             # VM types, pool construction
│   │   └── schedule.py       # Placement, Schedule, metrics
│   ├── builder.py            # decode mapping -> timed schedule (Section 5)
│   ├── algorithms/
│   │   ├── heft.py
│   │   ├── minmin.py         # Min-Min and Max-Min
│   │   ├── pso_plain.py
│   │   ├── ddhpso.py         # proposed
│   │   ├── genez_heft_td.py  # [1]
│   │   ├── rodriguez_pso.py  # [2]
│   │   ├── ceas.py           # [3]
│   │   └── recent_*.py       # chosen 2025/2026 baselines
│   ├── experiments/
│   │   ├── grid.py           # 36-case grid, seeds (Decisions D19 to D21)
│   │   └── run_all.py        # writes results/*.json
│   └── stats/                # win/tie/loss, Wilcoxon, normalization
├── results/                  # JSON/CSV for the dashboard
├── dashboard/app.py          # Streamlit
└── tests/                    # pytest (Section 13)
```

**Rule:** every algorithm returns a `Schedule` through the same builder and the same metric code, so numbers are comparable by construction.

---

## 4. System model and formulas

### 4.1 Notation

| Symbol | Meaning |
|---|---|
| `G = (T, E)` | Workflow DAG; `T` tasks, `E` dependency edges |
| `t_i` | Task `i`; `L_i` its length (seconds on a speed-1 machine) |
| `d_ij` | Data transferred from `t_i` to `t_j` (bytes) |
| `V` | VM pool, `K = |V|` instances. Instance `k` has speed `s_k`, price `p_k` per period, busy power `P_busy,k`, idle power `P_idle,k` |
| `B` | Bandwidth between distinct VMs (100 MB/s) |
| `τ` | Billing period (3600 s) |
| `β` | Boot delay (97 s) |
| `D` | Deadline |

### 4.2 Time

```
ET(i,k)  = L_i / s_k                              execution time of t_i on VM k
TT(i,j)  = d_ij / B   if t_i, t_j on different VMs
         = 0          if on the same VM           transfer time

DRT(i,k) = max over parents p of t_i of:
             AFT(p)              if a copy of p runs on VM k
             AFT(p) + TT(p,i)    otherwise
           (0 if t_i has no parents)

EST(i,k) = earliest start >= max( β, DRT(i,k) ) in an idle slot of VM k that fits ET(i,k)
AFT(i)   = EST(i,k) + ET(i,k)
M        = max over all tasks of AFT(i)
```

If a task has several copies (duplicates), a child uses the copy that minimizes `AFT(p) + TT(p,i)`.

### 4.3 Cost

For each used VM `k`: `T_start,k = first_start,k - β`, `T_end,k` = finish of its last task.

```
C = Σ_k  ceil( (T_end,k - T_start,k) / τ ) · p_k
```

Unused VMs cost nothing. A partly used period is paid in full.

### 4.4 Energy (tenant-side, no DVFS)

```
E = Σ_k ( P_busy,k · T_busy,k + P_idle,k · T_idle,k )
T_busy,k = Σ ET of every task copy executed on k      (duplicates count as busy)
T_idle,k = (T_end,k - T_start,k) - T_busy,k            (includes boot time and gaps)
```

### 4.5 Utilization

```
U = Σ_k T_busy,k / Σ_k (T_end,k - T_start,k)
```

### 4.6 Objective (DD-HPSO)

```
min F = w1·(C / C_ref) + w2·(E / E_ref) + w3·(M / M_ref)
s.t.  M <= D,  precedence satisfied,  w1 + w2 + w3 = 1
```

`C_ref, E_ref, M_ref` are the HEFT values on the same pool and case, so `F = 1.0` means "same as HEFT". Default `w1 = w2 = w3 = 1/3`.

### 4.7 Deadline handling (Deb's feasibility rules, as in [2])

```
V = max(0, M - D)
```

For two solutions A and B:

1. Both feasible (`V = 0`): smaller `F` wins.
2. One feasible, one infeasible: the feasible one wins.
3. Both infeasible: smaller `V` wins.

Use the same rule to update `pbest` and `gbest`.

### 4.8 Sub-deadlines

```
SD_i = AFT_HEFT(i) · D / M_HEFT
```

A HEFT-based variant of the sub-makespan idea in [3]. Used only as the duplication trigger (Decision D14).

---

## 5. Core interfaces and the shared schedule builder

### 5.1 Data structures

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class VMType:
    name: str
    speed: float      # relative to reference machine (1.0)
    price: float      # per billing period
    p_busy: float     # watts
    p_idle: float     # watts

@dataclass
class Workflow:
    n: int
    length: list[float]                       # L_i
    parents: list[list[tuple[int, float]]]    # (parent_id, data_bytes)
    children: list[list[tuple[int, float]]]
    order: list[int]                          # a topological order

@dataclass
class Placement:
    task: int
    vm: int
    start: float
    finish: float
    is_dup: bool = False

@dataclass
class Schedule:
    placements: list[Placement]
    makespan: float
    cost: float
    energy: float
    utilization: float
    runtime_s: float = 0.0                    # scheduling time, filled by the runner
```

Every algorithm exposes the same function:

```python
def schedule(wf: Workflow, pool: list[VMType], deadline: float,
             rng: "random.Random", budget: dict) -> Schedule: ...
```

### 5.2 The builder

```
function BUILD(wf, pool, mapping, order, dup_policy):
    for each VM k: slots[k] = [] (sorted by start), first_start[k] = None
    for t_i in order:                          # topological order
        k = mapping[t_i]
        compute DRT(i,k); EST(i,k) with insertion into idle slots (and >= β)
        if dup_policy is on and AFT_old(i) > SD_i:
            try DUPLICATE(t_i, k)              # Section 7.4
        place t_i on k; update first_start[k]
    compute T_start, T_end per VM, then M, C, E, U
    return Schedule
```

Implementation notes:

- Keep each VM's slots in a sorted list; find a gap with `bisect` and a linear scan from the insertion point.
- Precompute `ET[i][k]` once per workflow and pool (a `list[list[float]]`).
- Keep the builder free of algorithm-specific logic. HEFT, Min-Min, [1], [2], [3] and DD-HPSO all call it (or the same low-level helpers `est()` and `place()`).
- Python speed matters at 1000 tasks. Avoid object creation inside the hot loop, use plain lists, and profile with `cProfile` before optimizing.

---

## 6. Classical baselines

All baselines run on the same pool (Decision D4).

### 6.1 HEFT (Topcuoglu et al. 2002)

Used as the PSO seed, as the normalization reference, and as a baseline. It optimizes only makespan.

```
rank_u(i) = w̄_i + max over successors j of ( c̄_ij + rank_u(j) )
rank_u(exit) = w̄_exit
w̄_i  = mean over pool VMs of ET(i,k)
c̄_ij = d_ij / B
```

```
1. Compute rank_u for all tasks.
2. Sort tasks by non-increasing rank_u (a valid topological order).
3. For each task in that order:
       for each VM k in the pool: compute EST and AFT with insertion
       assign the task to the VM with the smallest AFT (ties: lowest VM index)
```

### 6.2 Min-Min and Max-Min

Applied to DAGs on the set of **ready tasks** (all parents scheduled):

```
repeat until all tasks are scheduled:
    R = ready tasks
    for each t in R: best_k(t) = argmin_k AFT(t,k);  ct(t) = AFT(t, best_k(t))
    Min-Min: pick t with the smallest ct(t)
    Max-Min: pick t with the largest  ct(t)
    assign it to best_k(t)
```

### 6.3 Plain PSO (ablation baseline)

DD-HPSO's PSO (Section 7) with **random** initialization and **no** duplication. Same fitness `F`, same Deb's rules, same budget. It isolates the effect of seeding and duplication.

---

## 7. DD-HPSO (proposed method)

### 7.1 Pipeline

```
Input: DAG, pool, deadline D
  1. Run HEFT on the pool: AFT_HEFT, M_HEFT, C_ref, E_ref, M_ref, order
  2. Deadline distribution: SD_i
  3. HEFT seeding: swarm = 1 HEFT particle + (N-1) perturbed copies
  4. PSO loop: decode particle -> selective duplication -> evaluate -> update
  5. Output best schedule with cost, energy, makespan, utilization
```

### 7.2 Encoding and seeding

- Particle `x ∈ R^n`, `x_i ∈ [0, K)`; VM of task `i` is `floor(x_i)`.
- Execution order is the fixed HEFT order (D12).

```
particle 1:       x_i = vm_index_HEFT(i) + 0.5
particles 2..N:   copy particle 1; for each task, with probability p_mut = 0.1,
                  set x_i = Uniform(0, K)
velocities:       initialized to 0
```

### 7.3 PSO update

```
v_i(t+1) = ω(t)·v_i(t) + c1·r1·(pbest_i - x_i(t)) + c2·r2·(gbest - x_i(t))
x_i(t+1) = x_i(t) + v_i(t+1)
ω(t)     = ω_max - (ω_max - ω_min) · t / I
```

`r1, r2 ~ U(0,1)` drawn per dimension. After each update, clamp `x` to `[0, K - 1e-9]` and `|v|` to `v_max = K/4`.

### 7.4 Selective duplication

Applied inside the builder for each decoded particle, once per task, in topological order.

```
function DUPLICATE(t_i, k):
    if AFT_old(i) <= SD_i: return                     # task already on time (D14)
    p* = remote parent maximizing AFT(p) + TT(p,i)    # critical parent, on another VM
    s  = earliest start of p* on k (its own data available on k, VM ready)
    if an idle slot on k fits [s, s + ET(p*,k)] and ends before t_i would start:
        AFT_new(i) = AFT of t_i recomputed with the copy on k
        ΔC = cost_k(with copy) - cost_k(without copy)     # exact, single VM, t_i placed in both
        ΔE = (P_busy,k - P_idle,k) · ET(p*,k)             # slot was idle
        accept if  AFT_new(i) < AFT_old(i)
               and ΔC <= 0                                # θ_C = 0
               and (extra_energy_so_far + ΔE) <= 0.05 · E_ref
        if accepted: register the copy so later tasks can use it; extra_energy_so_far += ΔE
```

Notes:

- Since the copy fills an idle slot, it cannot delay any other task, so the deadline violation `V` cannot get worse. Assert this in tests.
- `ΔC` is computed with `t_i` placed in both cases; later tasks may extend the lease window equally in both cases, so this local check is an accepted approximation.
- If scheduling time is too high ([1] reports duplication slowing scheduling by about 10 to 100 times), the fallback is to run duplication only when evaluating a new `pbest` candidate. Record this in the final report if used.

### 7.5 Fitness evaluation

```
function EVALUATE(particle):
    mapping  = floor(x)
    schedule = BUILD(mapping, HEFT_order, dup_policy)
    return (F, V, schedule)       # compared with Deb's rules
```

### 7.6 Full pseudocode

```
Input: DAG, pool, D, N=30, I=100, ω_max=0.9, ω_min=0.4, c1=2.0, c2=2.0,
       p_mut=0.1, w1=w2=w3=1/3, θ_C=0, θ_E=0.05
1.  Run HEFT -> order, AFT_HEFT, M_HEFT, C_ref, E_ref, M_ref
2.  Compute SD_i
3.  Initialize swarm (7.2)
4.  for each particle: (F, V, S) = EVALUATE(x); pbest = x
5.  gbest = best pbest by Deb's rules
6.  for t = 1 .. I:
7.      for each particle:
8.          update v, x (7.3)
9.          (F, V, S) = EVALUATE(x)
10.         if better than pbest by Deb's rules: pbest = x
11.     update gbest by Deb's rules
12. return schedule of gbest
```

**Termination:** `I` iterations (no early stopping, to keep the evaluation budget equal, D19).

**Property to test:** HEFT is in the initial swarm and `gbest` only improves under Deb's rules, so DD-HPSO's result should never be worse than HEFT's. One caveat: HEFT's own schedule has no duplication while the decoded HEFT particle may get duplication, which can only improve it. Add this as a unit test.

### 7.7 Complexity (rough)

One evaluation costs about `O(|T|·deg + |T|·log slots)` for the builder (more with duplication checks); total is about `N · I` evaluations. Measure real run time on a 1000-task case early; do not rely on this estimate.

---

## 8. Re-implementing the three reference papers

Label each in the report as **"our implementation of the approach in [X], adapted to our cost and energy model."** The summaries below come from the project overview, not the PDFs. **Confirm every detail against the PDF** (extraction prompt) before coding.

### 8.1 [1] Genez et al.: HEFT-TD (Lookahead-TD stretch)

- HEFT with **task duplication**: for each task on each candidate VM, duplicate its critical parent on that VM; keep the copy only if the task's finish time improves.
- Reported (to verify): about 9% (HEFT-TD) and 12% (Lookahead-TD) lower makespan on average.
- Implementation: HEFT loop (Section 6.1) where, for each candidate VM, the EST/AFT calculation tries the critical-parent duplication with **only the finish-time rule** (no cost, energy or deadline conditions), then picks the VM with the smallest AFT.
- Adaptation: runs on the fixed pool with the shared builder; its cost and energy are side effects, which is exactly what the comparison should show.
- To confirm from the PDF: whether duplication is tried on every candidate VM, tie-breaking, and Lookahead-TD's lookahead depth.

### 8.2 [2] Rodriguez and Buyya: deadline-based PSO (D23)

- PSO with one dimension per task, integer part = VM index, **cost fitness** under hourly billing, Deb's rules for the deadline.
- Implementation: `pso_plain.py` with fitness = `C` only, random initialization, same budget.
- Adaptations: fixed pool instead of its own provisioning (D4); no performance variability (D9).
- To confirm from the PDF: initialization ranges, parameter values, scheduling order, and how it forms the VM pool.

### 8.3 [3] Li et al.: CEAS without DVFS (D24)

Original steps: (1) deadline split into sub-makespans, (2) cost-utility VM choice, (3) sequence and parallel merging, (4) VM reuse, (5) DVFS slack reclamation.

- Implement steps 1 to 4 on the fixed pool; drop step 5 and say so. Dropping it removes part of CEAS's original energy saving, so state that CEAS is evaluated here without its DVFS energy mechanism.
- Results in [3] appear only in plots, so only trends can be checked, not exact values.
- To confirm from the PDF: the cost-utility formula, merge ordering, and tie-breaking.

---

## 9. Recent (2025/2026) baselines

Not selected yet (D25). Target 2 papers that pass most of this screen:

- pseudocode and parameter values given,
- same problem class (workflow DAG, VMs, deadline, cost or energy),
- released code or dataset (ideal),
- few model changes needed to run in this simulator,
- no pretrained weights or unreproducible training (for learning-based methods).

Drop a paper that fails two or more. Record the chosen papers as [4] and [5]. For each, document adaptations and estimated parameters in a table (paper value or "my assumption", with the reason).

---

## 10. Experiment design

### 10.1 Test-case grid (fixed before running, D21)

| Dimension | Values |
|---|---|
| Workflow | Montage, CyberShake, Epigenomics, LIGO |
| Size | about 50, 100, 1000 tasks (nearest sizes available) |
| Deadline factor | 1.2, 1.5, 2.0 × `M_HEFT` |
| Seeds | 10 per stochastic algorithm |

36 cases. Keep and report all of them, including losses.

### 10.2 Algorithms compared

HEFT, Min-Min, Max-Min, Plain PSO, [1] HEFT-TD, [2] PSO, [3] CEAS (no DVFS), recent [4], [5], and DD-HPSO.

### 10.3 Fairness rules

- Same pool, catalog, deadlines, builder, seeds count and PSO evaluation budget (D19).
- Rank cost and energy **only among feasible schedules** (`M <= D`).
- Document every estimated parameter.

### 10.4 Metrics and aggregation

Makespan, cost, energy, utilization, deadline success rate, scheduling time.

- Normalize each metric by the HEFT value of the same case, then average.
- Win/tie/loss matrix of DD-HPSO versus each baseline across cases.
- Deadline success rate per algorithm.
- Box plots across seeds (tests H1).
- Wilcoxon signed-rank test over per-case means (D20).
- Scheduling-time table by algorithm and size.

### 10.5 Ablation and sensitivity

- Ablation: Plain PSO, HEFT-seeded PSO without duplication, duplication on HEFT only, full DD-HPSO, DD-HPSO with sub-deadline trigger off.
- Sensitivity on 3 representative cases (one per size class): weights `(1/3,1/3,1/3)`, `(0.6,0.2,0.2)`, `(0.2,0.6,0.2)`; `θ_E ∈ {0, 5%, 10%}`.

---

## 11. Results format and dashboard

The dashboard (Streamlit + Plotly) is a precomputed results explorer; it does not run algorithms. Build it only after DD-HPSO and the core baselines work.

One record per (case, algorithm, seed):

```json
{
  "workflow": "Montage",
  "size": 100,
  "deadline_factor": 1.5,
  "deadline": 1234.5,
  "algorithm": "DD-HPSO",
  "seed": 7,
  "makespan": 1100.2,
  "cost": 4.8,
  "energy": 15230.0,
  "utilization": 0.71,
  "deadline_met": true,
  "runtime_s": 38.4,
  "schedule": [
    {"task": 1, "vm": 3, "start": 100.0, "finish": 130.5, "is_dup": false}
  ]
}
```

Store `schedule` only for the median-`F` seed of each (case, algorithm) to keep files small.

Views: Summary tab (normalized averages, win/tie/loss, deadline success), one tab per workflow with size and deadline selectors, case detail (DAG via NetworkX layout, Gantt chart, bars with error bars), overhead tab.

---

## 12. Parameter values

### 12.1 VM catalog (assumptions, D11)

| Type | Speed `s` | Price per hour | `P_busy` (W) | `P_idle` (W) |
|---|---|---|---|---|
| small | 1 | 0.10 | 50 | 30 |
| medium | 2 | 0.20 | 90 | 54 |
| large | 4 | 0.40 | 160 | 96 |
| xlarge | 8 | 0.80 | 300 | 180 |

Price scales linearly with speed; `P_idle = 0.6 · P_busy`. These values are **assumptions chosen for simplicity**, not taken from the reference papers or any provider. State this in the report.

### 12.2 Other model constants

| Constant | Value |
|---|---|
| Boot delay `β` | 97 s |
| Billing period `τ` | 3600 s |
| Bandwidth `B` | 100 MB/s |
| Pool size | 5 per type (at most 100 tasks), 10 per type (above) |

### 12.3 Algorithm parameters (starting defaults)

| Parameter | Value | Note |
|---|---|---|
| Swarm size `N` | 30 | Same for all PSO-based algorithms |
| Iterations `I` | 100 | Reduce equally for all if the 1000-task runs are too slow |
| Inertia `ω_max → ω_min` | 0.9 → 0.4 | Common default; confirm against [2] |
| `c1, c2` | 2.0, 2.0 | Common default; confirm against [2] |
| `v_max` | `K/4` | |
| `p_mut` | 0.1 | |
| Weights `w1, w2, w3` | 1/3 each | |
| `θ_C` | 0 | |
| `θ_E` | 5% of `E_ref` | |
| Deadline factors | 1.2, 1.5, 2.0 | × `M_HEFT` |
| Seeds | 10 | |

PSO defaults are common starting points, not tuned values. Because every PSO-based algorithm gets the same parameters and budget, the comparison stays fair; do any tuning identically for all of them.

---

## 13. Validation and testing

Use `pytest`.

- **Hand-checked tiny DAG** (4 to 5 tasks, 2 VMs): compute `M`, `C`, `E` by hand and assert the builder matches.
- **Precedence:** no task starts before every parent's data arrives.
- **Billing:** cost equals `ceil` of lease time over `τ` times price, boot included.
- **Energy:** `T_busy + T_idle` equals lease time for each VM.
- **HEFT consistency:** the HEFT particle decoded without duplication reproduces HEFT's makespan.
- **Monotonicity:** DD-HPSO's best result is never worse than HEFT's under Deb's rules.
- **Duplication:** a duplicate never increases `ΔC`, never worsens `V`, and total extra energy stays within `θ_E`.
- **Reproducibility:** fixed seeds, logged in the results.
- **Baseline sanity:** compare trends with each paper's reported trends; a mismatch means "bug or overclaim", so investigate before reporting.

---

## 14. Known risks and limitations

- **Runtime:** pure Python with PSO and duplication may be slow at 1000 tasks. Measure one run first; apply the equal-budget reduction rule (D19) if needed; use `multiprocessing` (D28); only then consider Numba.
- **Hourly billing on short workflows:** Pegasus tasks can run for seconds, so a whole workflow may fit inside one billing period and cost differences may be small. This is a property of the model, not a bug; report it, and note that cost differences are largest on the big workflows.
- **Simplified model:** fixed pool, no contention, no variability, continuous leases, no output transfer (D4 to D9).
- **Illustrative catalog:** VM prices and powers are assumptions (D11).
- **Duplication novelty:** [1] already keeps a duplicate only if finish time improves. The difference here is the added cost, energy and deadline conditions inside a global search.
- **Static schedule:** like all three papers, no runtime adaptation.
- **Simulation only.**
- **Reproduction fidelity:** baselines are reconstructions under this model; differences from the original papers are expected and must be documented.
- **Claims:** all improvements are expected outcomes until verified.

---

## 15. Remaining items that still need action

These cannot be decided from the current documents:

1. **Extract details for [1], [2], [3]** from their PDFs and update Section 8 (parameters, initialization, tie-breaking, CEAS formulas).
2. **Select the recent papers** [4], [5] and add a section per paper in Section 9.
3. **Obtain the Pegasus workflow files** and confirm which sizes actually exist for each workflow (D21 uses the nearest available).
4. **Justify or replace the VM catalog values** if the evaluators expect real provider prices.
5. **Measure run time** of one 1000-task DD-HPSO run, then confirm or reduce `I` (D19).

---

## 16. References

- [1] Genez et al., *Scheduling Scientific Workflows on Clouds Using a Task Duplication Approach*, IEEE/ACM UCC 2018.
- [2] Rodriguez and Buyya, *Deadline Based Resource Provisioning and Scheduling Algorithm for Scientific Workflows on Clouds*, IEEE Transactions on Cloud Computing, 2014.
- [3] Li et al., *Cost and Energy Aware Scheduling Algorithm for Scientific Workflows with Deadline Constraint in Clouds* (CEAS), IEEE Transactions on Services Computing, 2018.
- [4], [5] Recent (2025/2026) papers: **to be selected** (Section 9).

Supporting references (verify bibliographic details before citing in the report):

- Topcuoglu, Hariri and Wu, *Performance-Effective and Low-Complexity Task Scheduling for Heterogeneous Computing*, IEEE TPDS, 2002 (HEFT).
- Kennedy and Eberhart, *Particle Swarm Optimization*, IEEE ICNN, 1995.
- Deb, *An Efficient Constraint Handling Method for Genetic Algorithms*, Computer Methods in Applied Mechanics and Engineering, 2000.
- Juve et al., *Characterizing and Profiling Scientific Workflows*, Future Generation Computer Systems, 2013 (Pegasus workflows).
- Dolan and Moré, *Benchmarking Optimization Software with Performance Profiles*, Mathematical Programming, 2002 (optional performance profiles).