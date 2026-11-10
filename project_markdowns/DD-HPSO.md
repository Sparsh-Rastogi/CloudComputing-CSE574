# Deadline-Driven Hybrid Particle Swarm Optimization (DD-HPSO)
### Mathematical Formulation, System Model, Constraints, and Python Implementation

**Course:** CSE-574: Cloud Computing  
**Authors:** Sparsh Rastogi (Roll No: 24095072) & Nisha Mittal (Roll No: 24095071)  
**Project Guide:** Dr. Prasenjit Chanak  
**Repository Module:** `src/cloudburst/algorithms/ddhpso.py`  
**Shared Simulator:** `src/cloudburst/builder.py`

---

## Table of Contents
1. [Executive Summary & Core Philosophy](#1-executive-summary--core-philosophy)
2. [Target Cloud System Model & Formal Constraints](#2-target-cloud-system-model--formal-constraints)
   - 2.1 [Workflow DAG & Communication Model](#21-workflow-dag--communication-model)
   - 2.2 [Heterogeneous VM Pool & Provisioning](#22-heterogeneous-vm-pool--provisioning)
   - 2.3 [VM Boot Delay & Continuous Lease Window](#23-vm-boot-delay--continuous-lease-window)
   - 2.4 [Hourly Quantum Billing Model](#24-hourly-quantum-billing-model)
   - 2.5 [Tenant-Side Power & Energy Model](#25-tenant-side-power--energy-model)
3. [Optimization Objectives & Fitness Formulation](#3-optimization-objectives--fitness-formulation)
   - 3.1 [Tri-Objective Normalized Fitness Function ($F$)](#31-tri-objective-normalized-fitness-function-f)
   - 3.2 [Normalization Baselines ($M_{ref}, C_{ref}, E_{ref}$)](#32-normalization-baselines-m_ref-c_ref-e_ref)
   - 3.3 [Objective Weights ($w_1, w_2, w_3$)](#33-objective-weights-w_1-w_2-w_3)
   - 3.4 [Constraint Handling via Deb's Feasibility Rules](#34-constraint-handling-via-debs-feasibility-rules)
4. [Step-by-Step Algorithmic Pipeline](#4-step-by-step-algorithmic-pipeline)
   - 4.1 [Step 1: Deterministic Baseline & Order Initialization](#41-step-1-deterministic-baseline--order-initialization)
   - 4.2 [Step 2: Proportional Sub-Deadline Assignment ($SD_i$)](#42-step-2-proportional-sub-deadline-assignment-sd_i)
   - 4.3 [Step 3: Continuous Particle Encoding & HEFT Swarm Seeding](#43-step-3-continuous-particle-encoding--heft-swarm-seeding)
   - 4.4 [Step 4: Swarm Evolution & Velocity Dynamics](#44-step-4-swarm-evolution--velocity-dynamics)
   - 4.5 [Step 5: Sub-Deadline Triggered, Dual-Constrained Critical Parent Duplication](#45-step-5-sub-deadline-triggered-dual-constrained-critical-parent-duplication)
5. [Complete Mathematical Specification](#5-complete-mathematical-specification)
6. [Line-by-Line Code Walkthrough](#6-line-by-line-code-walkthrough)
   - 6.1 [Sub-Deadlines and Swarm Initialization (`ddhpso.py`)](#61-sub-deadlines-and-swarm-initialization-ddhpsopy)
   - 6.2 [Particle Dynamics & Bounds Clamping (`ddhpso.py`)](#62-particle-dynamics--bounds-clamping-ddhpsopy)
   - 6.3 [Idle-Slot Search & Insertion (`builder.py`)](#63-idle-slot-search--insertion-builderpy)
   - 6.4 [Duplication Logic with Zero-Cost and Energy Thresholds (`builder.py`)](#64-duplication-logic-with-zero-cost-and-energy-thresholds-builderpy)
   - 6.5 [Deb's Feasibility Comparator (`builder.py`)](#65-debs-feasibility-comparator-builderpy)
7. [Hyperparameter Summary](#7-hyperparameter-summary)
8. [Theoretical & Empirical Insights](#8-theoretical--empirical-insights)

---

## 1. Executive Summary & Core Philosophy

Scientific workflow scheduling in Infrastructure-as-a-Service (IaaS) clouds is an **NP-hard** multi-objective combinatorial optimization problem. Traditional approaches suffer from distinct structural limitations:
- **Heuristic List Schedulers (e.g., HEFT)** are greedy and myopic; they optimize makespan without accounting for cloud leasing quanta (hourly billing cycles) or cumulative tenant energy dissipation.
- **Classic Duplication Schedulers (e.g., Genez et al. HEFT-TD)** duplicate critical parent tasks aggressively to eliminate edge transfer delays, but inadvertently produce severe monetary cost inflation and energy wastage by unnecessarily prolonging VM leasing cycles.
- **Unseeded Metaheuristics (e.g., Plain PSO, Rodriguez PSO, Awad et al. IPSO-GWO)** initialize particles randomly across high-dimensional search spaces, resulting in unacceptably high deadline violation rates under tight deadlines ($D = 1.2 \times M_{HEFT}$).

**Deadline-Driven Hybrid Particle Swarm Optimization (DD-HPSO)** resolves these conflicts through a hybrid four-pillar design:
1. **Deterministic Seeding (HEFT Anchor):** Embeds the deterministic HEFT solution directly into Particle 1 and creates controlled mutations for the remaining particles ($p_{mut} = 0.1$), guaranteeing initial feasibility under strict deadlines.
2. **Fixed Topological Ordering:** Freezes task priorities to the HEFT upward rank ($\text{rank}_u$) topological order, halving the search space so particles only encode task-to-VM assignments ($x_i \in [0, K)$).
3. **Sub-Deadline Duplication Trigger ($SD_i$):** Computes task-level proportional sub-deadlines based on HEFT finish times. Duplication is evaluated *only* for lagging tasks ($AFT_{old} > SD_i$), preventing search overhead and unnecessary VM bloat on non-critical tasks.
4. **Dual-Constrained Zero-Cost Duplication ($\theta_C = 0, \theta_E \le 5\%$):** Restricts critical parent duplication strictly to existing idle gaps in already-billed hourly integer billing periods ($\Delta C \le 0$), bounded by a cumulative 5% energy cap.

---

## 2. Target Cloud System Model & Formal Constraints

### 2.1 Workflow DAG & Communication Model
A scientific application is modeled as a Directed Acyclic Graph (DAG) $G = (V_{tasks}, E)$:
- $V_{tasks} = \{t_1, t_2, \dots, t_n\}$ represents $n$ computational tasks. Each task $t_i$ has a base workload length $L_i$ in Million Instructions (or execution seconds on a reference compute unit of speed $s = 1.0$).
- $E = \{(t_i, t_j)\}$ represents data dependency edges where task $t_j$ cannot commence until parent task $t_i$ completes and transfers $d_{ij}$ bytes of output data.
- Communication bandwidth between any two distinct VMs is fixed at $B = 100\text{ MB/s} = 10^8\text{ B/s}$. Intramachine data transfer (when parent and child run on the same VM) incurs zero transfer delay ($TT = 0$).

$$\text{TT}(t_i, t_j) = \begin{cases} 
0, & \text{if } \text{VM}(t_i) = \text{VM}(t_j) \\ 
\frac{d_{ij}}{B}, & \text{if } \text{VM}(t_i) \ne \text{VM}(t_j) 
\end{cases}$$

### 2.2 Heterogeneous VM Pool & Provisioning
Scheduling chooses from a pre-provisioned pool of heterogeneous VMs $V = \{v_1, v_2, \dots, v_K\}$ ($K=20$ instances for workflows $n \le 100$; $K=40$ for $n > 100$), divided evenly across four standardized VM tiers:

| VM Type | Speed Factor ($s_k$) | Hourly Price ($p_k$) | Active Power ($P_{busy,k}$) | Idle Power ($P_{idle,k}$) |
| :--- | :---: | :---: | :---: | :---: |
| **Small** | 1.0 | \$0.08 / hr | 100 W | 60 W |
| **Medium** | 2.0 | \$0.16 / hr | 150 W | 90 W |
| **Large** | 4.0 | \$0.32 / hr | 250 W | 150 W |
| **Extra Large** | 8.0 | \$0.64 / hr | 400 W | 240 W |

The deterministic execution time of task $t_i$ on VM instance $k$ is:
$$\text{ET}(i, k) = \frac{L_i}{s_k}$$

### 2.3 VM Boot Delay & Continuous Lease Window
- **Boot Delay ($\beta$):** Every leased VM incurs a hardware initialization and operating system boot latency of $\beta = 97.0\text{ seconds}$. No task may execute on VM $k$ before time $t = \beta$. Boot time is billed at full instance cost and dissipates idle power ($P_{idle,k}$).
- **Continuous Lease Model:** A VM is leased continuously from $\beta$ seconds prior to the start time of its first allocated task until the exact completion time of its final allocated task:
$$T_{start,k} = \min_{t_i \in \text{tasks}(k)} (\text{EST}(i, k)) - \beta$$
$$T_{end,k} = \max_{t_i \in \text{tasks}(k)} (\text{AFT}(i, k))$$
$$T_{leased,k} = \max(0, T_{end,k} - T_{start,k})$$

Intermediate idle gaps between tasks on VM $k$ are retained and paid for; VMs are not released and re-booted mid-workflow.

### 2.4 Hourly Quantum Billing Model
Commercial IaaS providers bill compute instances in discrete time quanta $\tau = 3600.0\text{ seconds}$ (1 hour). Any partial fraction of an hour is rounded up to the nearest integer billing period:

$$\text{Periods}_k = \left\lceil \frac{T_{leased,k}}{\tau} \right\rceil = \left\lceil \frac{T_{end,k} - T_{start,k}}{3600} \right\rceil$$

The total financial cost $C$ across the cluster is:
$$C = \sum_{k=1}^{K} \text{Periods}_k \cdot p_k$$
*(Unused VMs where $\text{tasks}(k) = \emptyset$ incur zero cost).*

### 2.5 Tenant-Side Power & Energy Model
Energy dissipation accounts for the active compute intervals of assigned tasks (and duplicates) and the idle intervals (including boot time and inter-task scheduling gaps):

$$T_{busy,k} = \sum_{t_i \in \text{tasks}(k)} \text{ET}(i, k)$$
$$T_{idle,k} = T_{leased,k} - T_{busy,k}$$
$$E_k = \left( P_{busy,k} \cdot T_{busy,k} \right) + \left( P_{idle,k} \cdot T_{idle,k} \right)$$
$$E = \sum_{k=1}^{K} E_k \quad \text{[Joules]}$$

---

## 3. Optimization Objectives & Fitness Formulation

### 3.1 Tri-Objective Normalized Fitness Function ($F$)
To eliminate scale disparity across monetary dollars (\$1 to \$50), energy Joules ($10^4$ to $10^7\text{ J}$), and execution time seconds ($10^2$ to $10^4\text{ s}$), DD-HPSO minimizes a dimensionless, normalized multi-objective objective:

$$F(\mathcal{S}) = w_1 \cdot \left( \frac{C(\mathcal{S})}{C_{ref}} \right) + w_2 \cdot \left( \frac{E(\mathcal{S})}{E_{ref}} \right) + w_3 \cdot \left( \frac{M(\mathcal{S})}{M_{ref}} \right)$$

subject to:
$$M(\mathcal{S}) \le D, \quad \text{Precedence Constraints Satisfied}$$

### 3.2 Normalization Baselines ($M_{ref}, C_{ref}, E_{ref}$)
The reference metrics $M_{ref}, C_{ref}, E_{ref}$ are determined **a priori** by executing the deterministic HEFT algorithm on the exact same workflow DAG and VM pool instance:
$$M_{ref} = M_{HEFT}, \quad C_{ref} = C_{HEFT}, \quad E_{ref} = E_{HEFT}$$
Under this formulation:
- $F = 1.0$ represents performance identical to HEFT.
- $F < 1.0$ signifies a Pareto-improving schedule that reduces cost and energy relative to HEFT.

### 3.3 Objective Weights ($w_1, w_2, w_3$)
In our canonical implementation, equal importance is assigned to each primary tenant concern:
$$w_1 = \frac{1}{3} \approx 0.3333 \quad \text{(Monetary Cost)}$$
$$w_2 = \frac{1}{3} \approx 0.3333 \quad \text{(Tenant Energy)}$$
$$w_3 = \frac{1}{3} \approx 0.3333 \quad \text{(Schedule Makespan)}$$
$$\sum_{m=1}^{3} w_m = 1.0$$

### 3.4 Constraint Handling via Deb's Feasibility Rules
Rather than using fragile, hyperparameter-sensitive penalty multipliers ($\lambda \cdot (M - D)^2$) that distort search gradients, DD-HPSO enforces the workflow deadline $D$ using **Deb's Feasibility Comparison Rules**.

The constraint violation function is defined as:
$$V(\mathcal{S}) = \max(0, M(\mathcal{S}) - D)$$

Given two candidate schedules $\mathcal{S}_A$ and $\mathcal{S}_B$, schedule $\mathcal{S}_A$ strictly dominates $\mathcal{S}_B$ ($\mathcal{S}_A \prec \mathcal{S}_B$) if and only if:
1. **Both Feasible ($V_A = 0$ and $V_B = 0$):**  
   $$\mathcal{S}_A \prec \mathcal{S}_B \iff F(\mathcal{S}_A) < F(\mathcal{S}_B)$$
2. **One Feasible, One Infeasible ($V_A = 0$ and $V_B > 0$):**  
   $$\mathcal{S}_A \prec \mathcal{S}_B \quad \text{(The feasible schedule always wins)}$$
3. **Both Infeasible ($V_A > 0$ and $V_B > 0$):**  
   $$\mathcal{S}_A \prec \mathcal{S}_B \iff V(\mathcal{S}_A) < V(\mathcal{S}_B)$$
   *(If $V_A = V_B$, the schedule with lower $F$ breaks the tie).*

Deb's rules guide the swarm toward the feasible design space before optimizing cost and energy.

---

## 4. Step-by-Step Algorithmic Pipeline

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Input: Workflow DAG G=(V,E), VM Pool, Deadline D           │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Phase 1: Deterministic Baseline & Order Resolution         │
  │  - Compute upward rank rank_u(t_i) for all tasks            │
  │  - Execute HEFT -> M_HEFT, C_ref, E_ref, AFT_HEFT, Order    │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Phase 2: Sub-Deadline Assignment                           │
  │  - SD_i = AFT_HEFT(t_i) * (D / M_HEFT)                      │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Phase 3: Hybrid Swarm Seeding                              │
  │  - Particle 1 = x_HEFT + 0.5 (HEFT seed)                    │
  │  - Particles 2..N = Mutated copies of P1 (p_mut = 0.1)      │
  │  - Initialize pbest_i and gbest using Deb's rules           │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Phase 4: PSO Swarm Evolution Loop (Iter t = 1 .. I)        │
  │  - Inertia decay: w(t) = w_max - (w_max - w_min)*(t/I)      │
  │  - Update v_id and x_id with clamping: |v| <= K/4, x in [0,K)│
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Phase 5: Schedule Decoding & Duplication                   │
  │  - For task t_i in fixed topological Order:                 │
  │    * Map to VM k = floor(x_i)                               │
  │    * If AFT(t_i) > SD_i:                                    │
  │        Identify critical parent p* on remote VM             │
  │        Test idle slot insertion for p* on VM k              │
  │        Accept duplicate iff:                                │
  │          1. AFT_new(t_i) < AFT_old(t_i)                     │
  │          2. Delta_C <= 0 (theta_C = 0, no extra period)     │
  │          3. Extra_Energy <= 0.05 * E_ref (theta_E = 5%)     │
  │  - Compute makespan, cost, energy, utilization              │
  │  - Update pbest and gbest using Deb's Feasibility Rules     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Output: Optimal Feasible Schedule S_gbest                  │
  └─────────────────────────────────────────────────────────────┘
```

### 4.1 Step 1: Deterministic Baseline & Order Initialization
1. Compute the **HEFT upward rank** ($\text{rank}_u$) recursively from the exit tasks up to the entry tasks:
   $$\overline{w}_i = \frac{1}{K} \sum_{k=1}^{K} \text{ET}(i, k)$$
   $$\overline{c}_{ij} = \frac{d_{ij}}{B}$$
   $$\text{rank}_u(i) = \overline{w}_i + \max_{t_j \in \text{succ}(t_i)} \left( \overline{c}_{ij} + \text{rank}_u(j) \right)$$
   For terminal exit tasks with no successors:
   $$\text{rank}_u(t_{exit}) = \overline{w}_{exit}$$
2. Sort tasks by descending $\text{rank}_u$. This produces a strict topological order:
   $$\mathcal{O} = \langle t_{(1)}, t_{(2)}, \dots, t_{(n)} \rangle$$
3. Run standard HEFT using insertion-based slot scheduling on $\mathcal{O}$ to obtain the baseline schedule $\mathcal{S}_{HEFT}$, saving:
   - Makespan: $M_{ref} = M_{HEFT}$
   - Cost: $C_{ref} = C_{HEFT}$
   - Energy: $E_{ref} = E_{HEFT}$
   - Task completion timestamps: $\text{AFT}_{HEFT}(i)$ for each $t_i$.

### 4.2 Step 2: Proportional Sub-Deadline Assignment ($SD_i$)
To guide localized duplication decisions without distorting the global objective function, a proportional sub-deadline $SD_i$ is computed for every task $t_i$:

$$SD_i = \text{AFT}_{HEFT}(i) \cdot \frac{D}{M_{HEFT}}$$

**Properties of $SD_i$:**
- If $D = M_{HEFT}$, then $SD_i = \text{AFT}_{HEFT}(i)$.
- If $D = 1.5 \times M_{HEFT}$, each task's milestone is scaled out by $1.5\times$.
- $SD_i$ acts as a **gatekeeper**: if task $t_i$ finishes before $SD_i$, it is progressing on schedule and duplication is skipped entirely.

### 4.3 Step 3: Continuous Particle Encoding & HEFT Swarm Seeding
- **Particle Representation:** Each particle $\vec{x}_p \in \mathbb{R}^n$ is an $n$-dimensional continuous position vector, where dimension $d \in \{0, \dots, n-1\}$ corresponds to task $t_d$.
- **Mapping Decoder:** Task $t_d$ is assigned to VM index:
  $$k = \lfloor x_{p,d} \rfloor, \quad k \in \{0, 1, \dots, K-1\}$$
- **HEFT Seeding:**
  - **Particle 1 (The Anchor):** Seeded directly from HEFT's mapping:
    $$x_{1, d} = \text{VM}_{HEFT}(d) + 0.5$$
    Adding $0.5$ centers the continuous position within the integer bucket $[k, k+1)$, providing stability against early small velocity fluctuations.
  - **Particles $2 \dots N$ (Mutated Ensemble):** Created by copying Particle 1 and applying uniform random mutations with mutation probability $p_{mut} = 0.1$:
    $$x_{p, d} = \begin{cases} 
    \mathcal{U}(0, K - 10^{-6}), & \text{if } \text{rand}() < p_{mut} \\ 
    x_{1, d}, & \text{otherwise} 
    \end{cases}$$
  - **Initial Velocities:** $\vec{v}_p = \vec{0}$ for all $p \in \{1, \dots, N\}$.

### 4.4 Step 4: Swarm Evolution & Velocity Dynamics
For iteration $t = 1, \dots, I$:
1. **Dynamic Inertia Weight:** Decays linearly from $\omega_{max} = 0.9$ (global exploration) to $\omega_{min} = 0.4$ (local exploitation):
   $$\omega(t) = \omega_{max} - \left( \frac{\omega_{max} - \omega_{min}}{I} \right) \cdot t$$
2. **Velocity Update:**
   $$v_{p,d}(t+1) = \omega(t) \cdot v_{p,d}(t) + c_1 r_1 \left( pbest_{p,d} - x_{p,d}(t) \right) + c_2 r_2 \left( gbest_d - x_{p,d}(t) \right)$$
   where $c_1 = 2.0$, $c_2 = 2.0$, and $r_1, r_2 \sim \mathcal{U}(0, 1)$.
3. **Velocity Clamping:**
   $$V_{max} = \frac{K}{4.0}$$
   $$v_{p,d}(t+1) = \max\left(-V_{max}, \min\left(V_{max}, v_{p,d}(t+1)\right)\right)$$
4. **Position Update & Boundary Clamping:**
   $$x_{p,d}(t+1) = x_{p,d}(t) + v_{p,d}(t+1)$$
   $$x_{p,d}(t+1) = \max\left(0.0, \min\left(K - 10^{-6}, x_{p,d}(t+1)\right)\right)$$

### 4.5 Step 5: Sub-Deadline Triggered, Dual-Constrained Critical Parent Duplication
When decoding a particle's mapping into a concrete schedule, tasks are processed strictly in topological order $\mathcal{O}$. For each task $t_i$ assigned to VM $k = \lfloor x_{p,i} \rfloor$:

1. **Data Ready Time (DRT):**
   $$\text{DRT}(i, k) = \max_{p \in \text{parents}(t_i)} \left( \min_{copy \in \text{copies}(p)} \left( \text{AFT}(copy) + \text{TT}(copy, k) \right) \right)$$
2. **Earliest Start Time (EST) & Finish Time:**
   Search sorted idle gaps on VM $k$ for an available slot satisfying:
   $$\text{gap\_start} \ge \max(\beta, \text{DRT}(i, k)) \quad \text{and} \quad \text{gap\_end} - \text{gap\_start} \ge \text{ET}(i, k)$$
   $$\text{AFT}_{old}(i) = \text{EST}(i, k) + \text{ET}(i, k)$$
3. **Duplication Trigger:** Duplication is evaluated **if and only if**:
   $$\text{AFT}_{old}(i) > SD_i$$
4. **Critical Remote Parent Identification:**
   Find the remote parent $p^*$ that determines the critical path arrival time:
   $$p^* = \arg\max_{p \in \text{parents}(t_i), \text{VM}(p) \ne k} \left( \min_{copy \in \text{copies}(p)} (\text{AFT}(copy)) + \frac{d_{p, i}}{B} \right)$$
5. **Idle-Slot Feasibility on Target VM $k$:**
   Determine whether parent $p^*$ can be scheduled on VM $k$ inside an idle slot without delaying task $t_i$:
   $$\text{EST}(p^*, k) = \text{find\_earliest\_slot}(\text{slots}_k, \text{ET}(p^*, k), \text{DRT}(p^*, k), \beta)$$
   $$\text{AFT}(p^*, k) = \text{EST}(p^*, k) + \text{ET}(p^*, k)$$
   **Feasibility condition:** $\text{AFT}(p^*, k) \le \text{EST}(t_i, k)$.
6. **Dual Acceptance Check:**
   If $p^*$ fits, recalculate tentative new times $\text{EST}_{new}(t_i, k)$ and $\text{AFT}_{new}(t_i, k)$ with $p^*$ local. The duplicate is committed if and only if **all three** conditions hold:
   - **Performance Gain:** $\text{AFT}_{new}(t_i) < \text{AFT}_{old}(t_i)$
   - **Zero-Cost Constraint ($\theta_C = 0$):**
     $$\Delta \text{Periods}_k = \left\lceil \frac{T_{leased,k}^{with\_dup}}{\tau} \right\rceil - \left\lceil \frac{T_{leased,k}^{without\_dup}}{\tau} \right\rceil \le 0$$
   - **Energy Threshold Constraint ($\theta_E \le 5\%$):**
     $$\Delta E = (P_{busy,k} - P_{idle,k}) \cdot \text{ET}(p^*, k)$$
     $$E_{cumulative\_dup} + \Delta E \le 0.05 \cdot E_{ref}$$

---

## 5. Complete Mathematical Specification

$$\begin{aligned}
& \underset{\vec{x}}{\text{minimize}}
& & F(\mathcal{S}(\vec{x})) = \frac{1}{3} \left( \frac{C(\mathcal{S})}{C_{ref}} \right) + \frac{1}{3} \left( \frac{E(\mathcal{S})}{E_{ref}} \right) + \frac{1}{3} \left( \frac{M(\mathcal{S})}{M_{ref}} \right) \\
& \text{subject to}
& & M(\mathcal{S}) \le D \\
& & & \text{EST}(i, k) \ge \max\left(\beta, \text{DRT}(i, k)\right), \quad \forall t_i \in V_{tasks} \\
& & & \text{AFT}(i, k) = \text{EST}(i, k) + \frac{L_i}{s_k} \\
& & & \text{Intervals}(t_i, t_j) \cap \text{Intervals}(t_a, t_b) = \emptyset, \quad \forall t_i \ne t_a \text{ on same VM } k \\
& & & \Delta C_{dup} \le 0 \quad (\theta_C = 0) \\
& & & \sum_{dup} \Delta E_{dup} \le 0.05 \cdot E_{ref} \quad (\theta_E = 0.05)
\end{aligned}$$

---

## 6. Line-by-Line Code Walkthrough

### 6.1 Sub-Deadlines and Swarm Initialization (`ddhpso.py`)

In [`src/cloudburst/algorithms/ddhpso.py`](file:///c:/Users/Spidey/Downloads/coding/CloudComputing-CSE574/src/cloudburst/algorithms/ddhpso.py#L56-L105):

```python
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

# Step 3: Swarm Seeding
swarm_x: List[List[float]] = []
swarm_v: List[List[float]] = []

# Particle 1: HEFT particle (+0.5 centers within the VM bucket)
p1 = [heft_mapping[i] + 0.5 for i in range(n_tasks)]
v1 = [0.0 for _ in range(n_tasks)]
mapping1 = [int(val) for val in p1]

# Evaluate particle 1 with duplication enabled
s1 = build_schedule(
    wf=wf, pool=pool, mapping=mapping1, order=order,
    deadline=deadline, et_matrix=et_matrix,
    enable_duplication=True, sub_deadlines=sub_deadlines,
    e_ref=e_ref, theta_e=theta_e,
)
f1 = compute_objective_f(s1, c_ref, e_ref, m_ref, w1, w2, w3)

swarm_x.append(p1)
swarm_v.append(v1)

# Particles 2..N: perturbed copies of Particle 1
for _ in range(1, pop_size):
    px = list(p1)
    pv = [0.0 for _ in range(n_tasks)]
    for d in range(n_tasks):
        if rng.random() < p_mut:
            px[d] = rng.uniform(0.0, k_vms - 1e-6)
    mapping = [int(val) for val in px]
    s = build_schedule(...)
    # append to swarm...
```

### 6.2 Particle Dynamics & Bounds Clamping (`ddhpso.py`)

In [`src/cloudburst/algorithms/ddhpso.py`](file:///c:/Users/Spidey/Downloads/coding/CloudComputing-CSE574/src/cloudburst/algorithms/ddhpso.py#L144-L182):

```python
# Step 4: PSO Loop
for t in range(iterations):
    omega = omega_max - (omega_max - omega_min) * (t / float(iterations))
    for i in range(pop_size):
        for d in range(n_tasks):
            r1 = rng.random()
            r2 = rng.random()
            # Standard PSO velocity update with inertia, cognitive, and social components
            swarm_v[i][d] = (
                omega * swarm_v[i][d]
                + c1 * r1 * (pbest_x[i][d] - swarm_x[i][d])
                + c2 * r2 * (gbest_x[d] - swarm_x[i][d])
            )
            # Velocity clamping to [-V_max, V_max] where V_max = K / 4.0
            if swarm_v[i][d] > v_max:
                swarm_v[i][d] = v_max
            elif swarm_v[i][d] < -v_max:
                swarm_v[i][d] = -v_max

            # Position update and boundary clamping to valid VM index space
            swarm_x[i][d] += swarm_v[i][d]
            if swarm_x[i][d] < 0.0:
                swarm_x[i][d] = 0.0
            elif swarm_x[i][d] >= k_vms:
                swarm_x[i][d] = k_vms - 1e-6

        # Decode particle positions into discrete integer VM assignments
        mapping = [int(val) for val in swarm_x[i]]
        sched = build_schedule(...)
        f_val = compute_objective_f(sched, c_ref, e_ref, m_ref, w1, w2, w3)

        # Update personal best and global best using Deb's rules
        if compare_schedules_deb(sched, pbest_sched[i], f_val, pbest_f[i]) < 0:
            pbest_x[i] = list(swarm_x[i])
            pbest_sched[i] = sched
            pbest_f[i] = f_val

            if compare_schedules_deb(sched, gbest_sched, f_val, gbest_f) < 0:
                gbest_x = list(swarm_x[i])
                gbest_sched = sched
                gbest_f = f_val
```

### 6.3 Idle-Slot Search & Insertion (`builder.py`)

In [`src/cloudburst/builder.py`](file:///c:/Users/Spidey/Downloads/coding/CloudComputing-CSE574/src/cloudburst/builder.py#L23-L62):

```python
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
```

### 6.4 Duplication Logic with Zero-Cost and Energy Thresholds (`builder.py`)

In [`src/cloudburst/builder.py`](file:///c:/Users/Spidey/Downloads/coding/CloudComputing-CSE574/src/cloudburst/builder.py#L117-L213):

```python
# Duplication check (if enabled)
if enable_duplication:
    # Trigger only if task finish exceeds proportional sub-deadline
    trigger = (aft_ik > sub_deadlines[t_i]) if sub_deadlines is not None else True

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
            # ... compute DRT for parent on vm_k ...
            est_pk = find_earliest_slot(slots[vm_k], et_pk, drt_pk, BOOT_DELAY)
            aft_pk = est_pk + et_pk

            # Must finish before task t_i starts to avoid delaying it
            if aft_pk <= est_ik:
                # Recompute t_i times with parent local
                # ...
                if new_aft < aft_ik:
                    # Check energy budget
                    vm_obj = pool[vm_k]
                    delta_e = (vm_obj.vm_type.p_busy - vm_obj.vm_type.p_idle) * et_pk
                    energy_ok = (extra_energy_so_far + delta_e) <= energy_budget

                    # Cost check: does adding duplicate increase billed hourly periods?
                    old_first_start = slots[vm_k][0][0] if slots[vm_k] else est_ik
                    old_last_finish = max(slots[vm_k][-1][1] if slots[vm_k] else aft_ik, aft_ik)
                    old_t_start = old_first_start - BOOT_DELAY
                    old_periods = math.ceil(max(0.0, old_last_finish - old_t_start) / BILLING_PERIOD)

                    new_first_start = min(old_first_start, est_pk, new_est)
                    new_last_finish = max(old_last_finish, aft_pk, new_aft)
                    new_t_start = new_first_start - BOOT_DELAY
                    new_periods = math.ceil(max(0.0, new_last_finish - new_t_start) / BILLING_PERIOD)

                    cost_ok = (new_periods <= old_periods) # theta_C = 0

                    if cost_ok and energy_ok:
                        # Commit duplicate placement
                        dup_p = Placement(task=crit_parent, vm=vm_k, start=est_pk, finish=aft_pk, is_dup=True)
                        insert_slot(slots[vm_k], est_pk, aft_pk)
                        placements.append(dup_p)
                        task_copies[crit_parent].append(dup_p)
                        extra_energy_so_far += delta_e
                        est_ik = new_est
                        aft_ik = new_aft
```

### 6.5 Deb's Feasibility Comparator (`builder.py`)

In [`src/cloudburst/builder.py`](file:///c:/Users/Spidey/Downloads/coding/CloudComputing-CSE574/src/cloudburst/builder.py#L266-L307):

```python
def compare_schedules_deb(
    sched_a: Schedule,
    sched_b: Schedule,
    f_a: float,
    f_b: float,
) -> int:
    """
    Deb's feasibility comparison rules.
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

    # Case 2: One feasible, one infeasible -> feasible wins unconditionally
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
```

---

## 7. Hyperparameter Summary

| Hyperparameter | Symbol | Value | Rationale |
| :--- | :---: | :---: | :--- |
| **Swarm Size** | $N$ | 30 particles | Balances population diversity and evaluation runtime |
| **Iterations** | $I$ | 100 generations | Total budget: $30 \times 100 = 3,000$ evaluations |
| **Inertia Weight Range** | $[\omega_{min}, \omega_{max}]$ | $[0.4, 0.9]$ | Standard linear decay from global exploration to exploitation |
| **Cognitive Acceleration** | $c_1$ | 2.0 | Weights trajectory toward personal best position |
| **Social Acceleration** | $c_2$ | 2.0 | Weights trajectory toward swarm global best position |
| **Mutation Probability** | $p_{mut}$ | 0.1 | Mutates seeded particles to avoid premature stagnation |
| **Velocity Cap** | $V_{max}$ | $K / 4.0$ | Clamps step size to prevent overshooting VM instance boundaries |
| **Cost Duplication Threshold** | $\theta_C$ | 0 | Strict zero-cost condition ($\Delta \text{Periods} \le 0$) |
| **Energy Duplication Cap** | $\theta_E$ | 5% ($0.05 \cdot E_{ref}$) | Upper bound on additional Joules consumed by duplicates |
| **Multi-Objective Weights** | $w_1, w_2, w_3$ | $\frac{1}{3}, \frac{1}{3}, \frac{1}{3}$ | Equal weighting for monetary cost, tenant energy, and makespan |
| **Boot Delay** | $\beta$ | 97.0 s | Realistic cloud VM startup latency |
| **Billing Quantum** | $\tau$ | 3600.0 s | Hourly discrete billing periods |
| **Network Bandwidth** | $B$ | $100\text{ MB/s}$ | Inter-VM data transfer bandwidth |

---

## 8. Theoretical & Empirical Insights

### Where DD-HPSO Wins
1. **Tight Deadline Scenarios ($D = 1.2 \times M_{HEFT}$):**
   - DD-HPSO achieves **100.0% feasibility** across all workflows.
   - Unseeded metaheuristics fail frequently because random initial swarms drift into infeasible regions: Plain PSO (73.8% success), WPSO (75.7%), IPSO-GWO (68.6%), and Rodriguez PSO (61.4%).
2. **High Communication-to-Computation Ratio (CCR) Workflows:**
   - In Montage and CyberShake workflows, large inter-task data transfers create idle gaps on receiving VMs. DD-HPSO selectively fills these gaps with critical parent duplicates, cutting transfer latency to zero without paying for additional billing hours.
3. **Makespan and Energy Conservation:**
   - Matches HEFT's makespan within 2.3% while cutting financial cost by **8.9%** and energy consumption by **6.8%**. In contrast, HEFT-TD increases cost (+0.4%) and energy (+0.9%).

### Where DD-HPSO Concedes (Trade-offs)
1. **Relaxed Deadlines ($D = 2.0 \times M_{HEFT}$):**
   - When deadlines are loose, pure cost-optimizing schedulers (e.g., Rodriguez PSO, WPSO, PACM) downscale tasks onto cheaper Small instances (\$0.08/hr), tolerating extended runtimes. Because DD-HPSO weights makespan equally ($w_3 = \frac{1}{3}$), it retains faster Large and Extra Large instances to maintain makespan efficiency, resulting in higher monetary cost than pure cost-minimization algorithms.
2. **Compute-Intensive, Low-CCR Workflows (Epigenomics):**
   - In workflows where tasks spend minimal time communicating, idle gaps are tiny. The zero-cost duplication constraint ($\theta_C = 0, \text{AFT}_{p^*} \le \text{EST}_i$) rarely triggers, causing DD-HPSO to perform essentially identically to seeded PSO without duplication.
