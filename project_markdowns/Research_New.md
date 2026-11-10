# research_latest.md — Implementation-grade extraction of three workflow-scheduling papers

Source rule: everything below comes **only** from the three attached PDFs. Nothing is filled in from memory of similar algorithms.

**Labels**
- `[STATED]` is written explicitly in the paper.
- `[IMPLIED]` is not written, but follows from the text (reason given).
- `[MISSING]` is not given anywhere. No value is guessed silently. Any default is in Section F and marked **MY ASSUMPTION**.

**Page convention**
- WPSO uses printed IEEE pages 264–271 (PDF page 1 = p.264).
- IPSO-GWO uses journal pages 1–28.
- PACM uses printed pages 1247–1258.

**Quotes** are under 15 words and are used only for conflicts. Original notation is kept.

**Limits of this extraction**
- I read the text layer of the PDFs. **I could not read curve or bar values off plots**, so results given only as figures are described by the paper's own text.
- PACM Table II (VM speeds and prices) did **not** appear in the extracted text. See PACM B/D.

## 0. Overview and quick comparison

| | **WPSO** | **IPSO-GWO** | **PACM** |
|---|---|---|---|
| Venue / year | IEEE ICCCBDA 2025 | Sci. Reports 16:4359, 2026 | IEEE TCC 13(4), 2025 |
| Objective | min cost s.t. deadline | min weighted sum of makespan, energy, cost | min cost s.t. deadline |
| Deadline | yes (Eq. 9, 12) | **no** | yes (Eq. 10, 26) |
| Billing period (rounded up) | yes, BI = 1 h (Eq. 8) | **no** (price × busy time, Eq. 5) | yes, 1 h (Eq. 8) |
| Boot delay | not modeled | not modeled | not modeled |
| Energy | none | yes (Eq. 2–4; sim uses constant busy/idle power) | none |
| Type | PSO + heuristic decoder | IPSO then GWO hybrid | pure heuristic |
| Static / offline | yes [IMPLIED] | yes [IMPLIED] | yes [IMPLIED] |
| Code released | not stated | no (data "on request") | not stated |
| Faithful re-implementation | **partly** | **partly** (skeleton yes, numbers no) | **partly** |

---

# PAPER 1 — WPSO

## A. Screening (WPSO)

| Item | Content | Label / cite |
|---|---|---|
| Title | WPSO: A PSO-Based Algorithm for Cost-Effective and Deadline-Constrained Workflow Scheduling in Cloud Environments | [STATED] p.264 |
| Authors | Guichen Wang, Yongke Li, Gongxuan Zhang* (Nanjing Univ. of Sci. & Tech.) | [STATED] p.264 |
| Venue / year | 2025 10th Int. Conf. on Cloud Computing and Big Data Analytics (ICCCBDA), IEEE, pp. 264–271, DOI 10.1109/ICCCBDA64898.2025.11030507 | [STATED] p.264 |
| Code / dataset released | Not mentioned. Workflows are the four standard CyberShake, Epigenomics, LIGO and Montage (Sec. V-A, p.268). | [MISSING] (code); [STATED] (workflow names) |
| Problem | DAG workflow scheduling on IaaS with a deadline and a cost objective. Single objective (WEC) with constraint WET ≤ DDL (Eq. 9, p.267). No energy and no multi-objective. | [STATED] |
| Static or dynamic | Static/offline. The whole topologically sorted DAG is decoded at once (Alg. 2). Future work lists "dynamic workflows" (Sec. VI, p.271). | [IMPLIED] |
| Algorithm type | Metaheuristic (PSO) with a heuristic decoder (Alg. 1, Alg. 2, p.268) | [STATED] |
| Verdict | **Partly feasible.** See below. | |

**Verdict reasoning**
- Feasible because:
  - Eq. 1–12, Table I and the tuned parameters are explicit.
  - Alg. 2's decoding logic is described in prose.
- Not fully feasible because:
  - There is no explicit fitness for infeasible particles (see C.8).
  - The stopping rule conflicts between Sec. IV-A and Sec. V-B (see C.6).
  - Velocity initialization is missing, and "initialize to maximum value" would give a frozen swarm (see C.5).
  - The encoding range [0, m) makes `vm_m` unreachable under the literal reading (see C.4).
  - Lease start/end (LST/LET) computation is not defined.
  - Tie-breaking and the "least increase" rules in Alg. 2 are ambiguous.
  - The HEFT configuration used to set TL/TR is not given.

## B. System model (WPSO)

**Task model**
- DAG G = (T, E), T = {t1..tn}, edge e_ij = data flow t_i → t_j with a data size. A child cannot start before its parent completes. [STATED] Sec. III-A, p.266.
- Virtual `t_entry`, `t_exit` consume no computation. [STATED] p.266.
- Workload W_i (Eq. 1). The unit of W_i is not stated. [MISSING] It must be compatible with C_j in FLOPS. [IMPLIED]
- Data volume D_{t_i}^{t_j}. The unit is not stated. [MISSING] Bandwidth is "20 MBps" (p.268), so data is presumably in MB. [IMPLIED]

**VM model**
- A set of VM *types* VM = {vm1..vmm}. Unlimited instances of each type are available from one data center. [STATED] Sec. III-B, p.266.
- Speed C_j is in FLOPS. Higher speed means higher price. [STATED] p.266.
- Table I (p.269), nine types:

| | vm1 | vm2 | vm3 | vm4 | vm5 | vm6 | vm7 | vm8 | vm9 |
|---|---|---|---|---|---|---|---|---|---|
| C | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 |
| P (per BI) | 0.12 | 0.195 | 0.28 | 0.375 | 0.48 | 0.595 | 0.72 | 0.855 | 1.0 |

- The unit of C in Table I is not stated. [MISSING] The pairing of this catalog with the "FLOPS" claim is therefore unclear.
- Billing: BI = one hour (p.268). Cost per instance is P × ⌈(LET − LST)/BI⌉ (Eq. 8). [STATED]
- Boot/provisioning delay: not mentioned, so not modeled. [MISSING / not modeled]
- Performance variability: not mentioned. [MISSING / not modeled]
- VM count limit: unlimited. [STATED]
- LST and LET are the lease start and end times of instance v_i. How they derive from task times, and whether data transfer is included, is not defined. [MISSING]

**Network model**
- One bandwidth `bw` between VMs, "known in advance", average 20 MBps (Sec. V-A, p.268). [STATED]
- TT_{t_i}^{t_j} = D_{t_i}^{t_j}/bw if VM(t_i) ≠ VM(t_j), otherwise 0 (Eq. 2). [STATED]
- No data-transfer cost. [STATED] p.266.
- Contention and transfer blocking: not modeled. [IMPLIED]

**Energy model**
- None. Energy is named only as future work (Sec. VI, p.271). [STATED]

**Deadline model**
- DDL = TL + (TR − TL) × λ (Eq. 12, p.269). [STATED]
- TL = HEFT scheduling time on the **fastest** VM type. TR = HEFT scheduling time on the **slowest** VM type. [STATED]
- λ runs 0.005 to 0.05 in steps of 0.005, which is 10 values. [STATED]
- The number of instances used by HEFT for TL and TR is not stated. [MISSING]

**Assumptions my model may violate**
- Unlimited VMs.
- No boot delay.
- Single uniform bandwidth.
- No idle or busy power.
- LST/LET undefined.
- Instance availability time AT_{v_j} undefined (see C.2).

## C. Algorithm specification (WPSO)

### C.1 Equations needed (verbatim notation)

| Eq. | Content | Cite |
|---|---|---|
| (1) | ET_{t_i}^{vm_j} = W_i / C_j | p.266 |
| (2) | TT_{t_i}^{t_j} = D_{t_i}^{t_j}/bw if VM(t_i) ≠ VM(t_j); 0 otherwise | p.266 |
| (3) | ST_{t_i}^{v_j} = max(AT_{v_j}, EST_{t_i}) | p.267 |
| (4) | FT_{t_i}^{v_j} = ST_{t_i}^{v_j} + ET_{t_i}^{k_{v_j}}, where k_{v_j} is the type of instance v_j | p.267 |
| (5) | EST_{t_i} = 0 if t_i = t_entry; otherwise max over parents t_a of ( FT_{t_a} + TT_{t_a}^{t_i} ) | p.267 |
| (6) | WET = max over t_i ∈ T of FT_{t_i} | p.267 |
| (7) | LFT_{t_i} = DDL if t_i = t_exit; otherwise min over e_ij ∈ E of ( LFT_{t_j} − MET_{t_j} − TT_{t_i}^{t_j} ). MET_{t_j} is the execution time on the fastest VM type. | p.267 |
| (8) | WEC = Σ over v_i ∈ R of P_{v_i} × ⌈(LET_{v_i} − LST_{v_i}) / BI⌉ | p.267 |
| (9) | minimize WEC s.t. WET ≤ DDL | p.267 |
| (10) | v_ij(t+1) = ω v_ij(t) + c1 r1(t)[p_ij(t) − x_ij(t)] + c2 r2(t)[p_gj(t) − x_ij(t)] | p.267 |
| (11) | x_ij(t+1) = x_ij(t) + v_ij(t+1) | p.267 |
| (12) | DDL = TL + (TR − TL) × λ | p.269 |

- Solution S = (R, M, WEC, WET). R is the leased instances, each v_i = (k_{v_i}, LST_{v_i}, LET_{v_i}). M is the mappings m_i = (t_i, v_j, ST, FT). [STATED] p.267.
- **Eq. 7 caveat:** TT in Eq. 7 depends on VM(t_i) and VM(t_j), which are not known when LFT is precomputed. See F, W11.

### C.2 Step-by-step description (in the paper's order)

1. Resolve the workflow by topological sorting. Particles choose a VM **type** per task, and a heuristic decoder chooses the **instance**. (Sec. I, p.265; Sec. IV, p.267–268) [STATED]
2. Particle dimension = n, the number of tasks. Position values lie in [0, m). The VM type is floor(value). (Sec. IV-A, p.267) [STATED]
3. Initialize the swarm with all positions at the maximum value, "to ensure a high scheduling success rate first". (p.267) [STATED]
4. Loop. For each particle: update velocity and position (Eq. 10, 11), decode with Alg. 2, update the particle's local best. After all particles, update the global best. (Alg. 1)
5. Stop when the iteration limit is reached or there is no improvement for 50 rounds (p.268). See the conflict in C.6.
6. Return S of the global-best particle.

**Availability time:** AT_{v_j} is not defined. Append-only (no insertion into idle gaps) is the natural reading. [IMPLIED] The paper never mentions insertion-based scheduling.

### C.3 Pseudocode, cleaned and mapped

**Alg. 1: Framework of WPSO (p.268)**

| # | Step | Paper line |
|---|---|---|
| 1 | Set N, ω, c1, c2. | L1 |
| 2 | Initialize population with all positions at max value. | L2 |
| 3 | While end-of-iteration condition not met: | L3 |
| 4 | For each particle: update v, x by Eq. 10/11 | L4–5 |
| 5 | Decode via Alg. 2 | L6 |
| 6 | Update local best | L7 |
| 7 | End for. Update global best particle | L8–9 |
| 8 | End while. Return S of global best | L10–11 |

Note: the text refers to "lines 4-12" and "line 13", but the listing ends at line 11. [conflict, minor]

**Alg. 2: Solution Construction (p.268)**

| # | Step | Paper line |
|---|---|---|
| 1 | R ← ∅, M ← ∅ | L1 |
| 2 | For i = 1..p.size(), in topological order: t_i = i-th task, vm_j = floor(p(i)) | L2–3 |
| 3 | A ← ∅, B ← ∅ | L4 |
| 4 | For each existing instance in R of type vm_j (same type only): compute FT_{t_i} on it. If FT_{t_i} ≤ LFT_{t_i}, put it in A when parents of t_i are scheduled on it, otherwise in B. | L5–10 |
| 5 | C ← A if A ≠ ∅, else C ← B | L11 |
| 6 | If C ≠ ∅: prefer instances in C where scheduling t_i adds **no new billing interval**. If none, choose by least billing-interval increase ("traverse all virtual machines"). Schedule t_i there. | L12–13 |
| 7 | Else open a new instance of type vm_j and schedule t_i on it. | L14–15 |
| 8 | Update R, M. | L17 |
| 9 | After all tasks: compute WET (Eq. 6), WEC (Eq. 8). Return S = {R, M, WEC, WET}. | L19–20 |

**Notes on Alg. 2**
- A new instance is accepted **without a deadline check**. Feasibility is only revealed in WET ≤ DDL. [IMPLIED]
- If A is non-empty, B is ignored even if B would be cheaper. [IMPLIED]
- The parent test is "parent tasks of t_i are scheduled on this instance". Whether this means *any* or *all* parents is not stated. [MISSING]

### C.4 Encoding (WPSO)
- Particle position x_i ∈ [0, m)^n. A dimension's floor gives the VM type. [STATED] p.267.
- Fig. 2 example, 7 tasks: positions 2.5, 6.1, 3.4, 1.2, 8.3, 4.7, 5.9 give vm2, vm6, vm3, vm1, vm8, vm4, vm5. So floor(x) **is the type index**, with types numbered from 1. [STATED]
- **Conflict:** values in [0, m) have floor 0..m−1. That makes "vm0" non-existent and `vm_m` (the fastest) unreachable. Possible readings:
  - (a) The effective range is [1, m+1).
  - (b) A value in [0, 1) is clamped to vm1, and `vm_m` is reached only at the boundary.
  - (c) The text is loose, and the code clamps to [1, m].
- Fig. 2 supports floor = type index. Reading (a) or (c) is implied.

### C.5 Initialization
- All particle positions at "maximum value". [STATED] p.267. This is presumably vm_m on every task, the fastest type. [IMPLIED]
- Velocity initialization: not stated. [MISSING]
- Local-best initialization: not stated. [MISSING]
- **Consequence [IMPLIED]:** all particles start identical. With zero initial velocity and pbest = gbest = x, Eq. 10 gives zero velocity and the swarm never moves. Some non-zero or random initial velocity is therefore needed.

### C.6 Termination
- Sec. IV-A, p.268: stop at "the number of iterations" or when quality has not improved for 50 rounds. [STATED]
- Sec. V-B, p.269: the parameter MaxE is called "maximum number of evaluations". It "serves as the stopping criterion" and is 400. [STATED]
- **Conflict:** MaxE is called "evaluations", but with N = 200 that would be 2 generations. The 50-round stagnation rule also does not fit that.
  - Reading 1: MaxE = max iterations = 400, plus the 50-round stagnation rule, whichever first.
  - Reading 2: MaxE = fitness evaluations (implausibly small).
  - Reading 3: only MaxE applies.

### C.7 Constraint / deadline handling
- Deadline enters through the LFT_{t_i} filter in Alg. 2 line 7 (existing instances only). [STATED]
- Initialization at max type biases the swarm toward feasibility. [STATED]
- No penalty, repair or explicit feasibility rule is given. [MISSING]
- SR counts solutions that meet DDL. [STATED] p.269.

### C.8 Fitness
- "Fitness measure" is mentioned only generically. [STATED] p.267.
- Implied: fitness = WEC with the deadline constraint applied. Support: HGSA's fitness "was adjusted to be the same as WPSO" for the cost model with deadline constraints. (p.269)
- How infeasible particles (WET > DDL) rank against feasible ones is not given. [MISSING]

### C.9 Tie-breaking and edge cases
- Ties between several "no new billing interval" instances: not stated. [MISSING]
- Ties in pbest/gbest updates (strict vs non-strict): not stated. [MISSING]
- Behavior of position values outside [0, m): not stated. [MISSING]
- Velocity clamping: not stated. [MISSING]
- Per-dimension vs per-particle r1, r2: not stated. [MISSING]
- Virtual entry/exit in the particle: not stated. Dimension = number of tasks n. [IMPLIED: exclude them]
- Random seeds: not stated. [MISSING]

## D. Parameters (WPSO)

| Parameter | Symbol | Value | Label | Source |
|---|---|---|---|---|
| Swarm size | N | 200 | STATED (tuned) | Sec. V-B, p.269 |
| Inertia weight | ω | 0.5 | STATED (tuned) | p.269 |
| Learning factors | c1 = c2 | 1.6 | STATED (tuned) | p.269 |
| Max evaluations | MaxE | 400 | STATED (meaning unclear, see C.6) | p.269 |
| Stagnation limit | – | 50 rounds | STATED | p.268 |
| r1, r2 | r1(t), r2(t) | random, new each iteration | STATED (distribution unstated) | p.267 |
| Billing interval | BI | 1 hour | STATED | p.268 |
| Bandwidth | bw | 20 MBps | STATED | p.268 |
| VM catalog | C, P | Table I (nine types) | STATED | p.269 |
| Deadline factor | λ | 0.005 to 0.05, step 0.005 | STATED | p.269 |
| Runs per config | – | 10 | STATED | p.269 |
| Initial position | x_ij(0) | "maximum value" | STATED | p.267 |
| Initial velocity | v_ij(0) | – | **MISSING** | – |
| Velocity bounds | v_max | – | **MISSING** | – |
| Position clamp rule | – | – | **MISSING** | – |
| Random seeds | – | – | **MISSING** | – |
| Boot delay | – | not modeled | MISSING | – |
| Units of W_i, C, D | – | – | **MISSING** | – |
| HEFT config for TL/TR | – | – | **MISSING** | – |
| Baseline parameters (IC-PCP, PSO, HGSA) | – | "followed their respective reference literature" | MISSING | p.269 |

**Tuning (Taguchi L16(4³), Tables II and III, p.269)**
- Factor levels: N ∈ {50, 100, 150, 200}; ω ∈ {0.2, 0.5, 0.8, 1.1}; c1 ∈ {1.6, 1.8, 2.0, 2.2}.
- The response value is WPSO's normalized cost averaged over 120 instances (4 workflows × 3 scales × 10 deadline factors).
- Average RV per level:

| Level | N | ω | c1 |
|---|---|---|---|
| 1 | 52.3778 | 50.7937 | 47.2629 |
| 2 | 47.8050 | 43.5897 | 47.3114 |
| 3 | 45.4583 | 44.7785 | 47.3520 |
| 4 | 44.0002 | 50.4795 | 47.7151 |
| Delta | 8.3776 | 7.2040 | 0.4521 |

- The minimum level was chosen per parameter. N is most influential, then ω, then c1. [STATED]
- How RV treats infeasible runs (SR < 1) in the average is not stated. [MISSING]

## E. Experimental setup (WPSO)

- **Machine:** Intel i5-12600KF 3.70 GHz, Java, Windows 11. No named simulator is stated. [STATED / MISSING simulator]
- **Workflows:** CyberShake, Epigenomics, LIGO, Montage (Pegasus-style, Fig. 3). Sizes: small/medium/large = **50 / 100 / 1000** tasks. [STATED] Sec. V-A, p.268.
- **VM catalog:** nine types (Table I), cited from [19]. BI = 1 h. bw = 20 MBps (cited from [20]). Pricing is "similar to Amazon EC2".
- **Deadlines:** Eq. 12 with λ = 0.005..0.05.
- **Runs:** each algorithm run 10 times, averages reported.
- **Metrics:**
  - SR (success rate) = fraction of solutions meeting DDL.
  - NC (normalized cost) = WEC / CR, where CR is the cost of HEFT on the slowest VM type.
- **Baselines:** IC-PCP [5], PSO [23], HGSA [24]. Note that refs [3] and [23] are the same entry in the reference list.
- **Reported results** (Figs. 4 and 5; plots only, no tables):
  - WPSO had the highest success rate in all scenarios, especially at small λ. In CyberShake and Montage it approached SR = 1.0 quickly. Epigenomics SR was lower overall.
  - For NC, excluding cases with SR < 1, WPSO had the lowest cost in CyberShake and Montage.
  - In Epigenomics and LIGO, WPSO beat PSO and HGSA but "lagged behind IC-PCP". WPSO kept trending down at larger λ while IC-PCP had leveled off.
  - Axis ranges of Fig. 5 (tick labels only): CyberShake 0–300+, Epigenomics 2–7, LIGO 10–40, Montage 0–600.
- **Sanity checks [IMPLIED]:**
  - Eq. 12 puts DDL within 0.5%–5% of the (TR − TL) range above TL, so deadlines are very tight and need many parallel instances.
  - Large NC values (tens to hundreds at small λ) are expected, since each extra instance pays at least one BI.
  - NC falls as λ rises.
  - The all-fastest-type schedule is the SR = 1 fallback.

## F. Gaps and adaptation report (WPSO)

### F.1 Numbered gaps with suggested defaults (all **MY ASSUMPTION**)

| # | Gap | Suggested default (MY ASSUMPTION) | Why reasonable | Impact |
|---|---|---|---|---|
| W1 | Fitness for infeasible particles | Feasible-first: if WET ≤ DDL, fit = WEC. Else fit = BIG + (WET − DDL) (or compare by violation first, then cost) | Matches the paper's "success first, cost second" intent (p.267) | **High** |
| W2 | v(0) and pbest(0) | v_ij(0) ~ U(−v_max, v_max), pbest = x(0) | Identical particles with v = 0 never move (C.5) | **High** |
| W3 | Out-of-range positions | Clamp to the valid range, velocity clamp v_max = (range)/2 | Keeps floor() valid | Medium |
| W4 | Type-index range | Position range [1, m+1), type = floor(x); init at m+1−ε (all fastest) | Makes vm1 and vm_m reachable, consistent with Fig. 2 | Medium |
| W5 | Termination | MaxE = 400 iterations AND stop after 50 non-improving rounds, whichever first | Both are stated; "evaluations" would give 2 generations at N = 200 | **High** |
| W6 | LST/LET | LST = first task start on the instance. LET = last task finish. Option: include data receive and send (as PACM Eq. 6–7 does) | Cost rounding in Eq. 8 depends on it | **High** |
| W7 | AT_{v_j} and insertion | AT = FT of the last task on the instance. Append-only | Nothing in the paper mentions gap filling | Medium |
| W8 | Ties among no-new-interval instances | Choose lowest FT, then lowest instance index | Deterministic, favors earlier finish | Medium |
| W9 | "Least increase in billing intervals" scope | Evaluate over C (the filtered candidates), tie → lower FT | "Traverse all VMs" most plausibly means all of C | Medium |
| W10 | A membership | Instance ∈ A if **any** parent is on it | Weakest reading, more candidates in A | Low–Med |
| W11 | LFT precompute (Eq. 7) | Use TT = D/bw for every edge (no co-location) | Placement is unknown at precompute time | Medium |
| W12 | pbest/gbest ties | Update only on strict improvement | Common practice | Low |
| W13 | r1, r2 | Fresh U(0,1) per particle per dimension per iteration | Common practice | Low |
| W14 | HEFT configuration for TL/TR | TL: HEFT on unlimited instances of the fastest type. TR: HEFT on one instance of the slowest type. (PACM, in your attachments, states the same setup in its Sec. V-B.) | Gives a sensible D range | Medium |
| W15 | Virtual entry/exit in the particle | Exclude from the particle (n real tasks) | They use no resource | Low |
| W16 | RV treatment of infeasible runs in tuning | Penalized cost value | Not stated | Low |
| W17 | Random seed policy | One fixed master seed per run, 10 runs | Reproducibility | Low |

### F.2 Where WPSO differs from MY MODEL, and the minimal change

| Aspect | WPSO | My model | Minimal change |
|---|---|---|---|
| Boot delay | none | boot delay b before a VM can run tasks | New instance: AT = lease start + b. LST is the lease start, billing includes boot (decide per your provider). LFT gate and decoder unchanged. |
| Billing | ⌈(LET − LST)/BI⌉ × P | fixed period rounded up | Compatible. Define LST/LET (W6). |
| Energy | none | busy power × busy time + idle power × idle time | Post-hoc from R and M. Report only. To optimize, add a weighted term to fitness. |
| Heterogeneity | speed and price | same | Compatible |
| Deadline | DDL via Eq. 12 | deadline D | Plug in your D |
| Network | uniform bw, 0 on same instance | assumed compatible | None |
| Static DAG | yes | yes | None |
| Metrics | WET, WEC, SR, NC | makespan, cost, energy, utilization, deadline success | Add utilization = Σ busy / Σ billed time |

### F.3 What changes results noticeably vs slightly
- **Noticeably:** W1, W2, W5, W6, W8, W9, W11, W14, and the boot-delay adaptation.
- **Slightly:** W10, W12, W13, W15, W17.

### F.4 Questions to resolve before coding
1. Does MaxE mean iterations or evaluations?
2. How exactly are LST/LET defined (data transfer included or not)?
3. What is the fitness rule for deadline-violating particles?
4. What are the initial velocities?
5. What is the effective position range, and is vm_m reachable?
6. How are ties broken in Alg. 2?
7. Is the TL/TR HEFT run on unlimited or single instances?

## G. Implementation checklist (WPSO)

1. **Preprocess.**
   - Build the topological order (exclude virtual entry/exit).
   - Compute MET_i = W_i / C_max.
   - Compute LFT by reverse topological order using Eq. 7, with TT = D/bw (W11).
   - Run HEFT for TL and TR, then set DDL = TL + (TR − TL) × λ.
2. **Parameters.** N = 200, ω = 0.5, c1 = c2 = 1.6, MaxE = 400 (as iterations), stagnation = 50, BI = 1 h, bw = 20 MBps, VM catalog from Table I.
3. **Initialize.** x_ij = max (vm_m on every task). v_ij random (W2). pbest = x, gbest = best.
4. **Loop** until MaxE iterations or 50 rounds without gbest improvement. For each particle:
   1. Update v (Eq. 10) and x (Eq. 11), then clamp.
   2. **Decode:**
      1. R = ∅, M = ∅.
      2. For each task t_i in topological order: type = floor(x_i).
      3. For each instance of that type in R: compute EST (Eq. 5), ST (Eq. 3) and FT (Eq. 4).
      4. If FT ≤ LFT_{t_i}, add to A (if a parent is on it) or B.
      5. C = A if A ≠ ∅, else B.
      6. If C is empty, open a new instance.
      7. Otherwise prefer an instance whose billed intervals do not increase. Else take the one with the least increase. Ties → W8.
      8. Update R, M.
   3. WET = max FT, WEC = Σ P × ⌈(LET − LST)/BI⌉.
   4. Fitness by W1. Update pbest.
5. Update gbest. Return S of the global best.
6. **Report** WET, WEC, SR (WET ≤ DDL), NC = WEC / CR, plus your utilization and energy (post-hoc).

---

# PAPER 2 — IPSO-GWO (fog-cloud)

## A. Screening (IPSO-GWO)

| Item | Content | Label / cite |
|---|---|---|
| Title | Efficient workflow scheduling in fog-cloud collaboration using a hybrid IPSO-GWO algorithm | [STATED] p.1 |
| Authors | Samar Awad, Marwa Gamal, Khaled Abd El Salam, Rehab F. Abdel-Kader | [STATED] p.1 |
| Venue / year | Scientific Reports 16:4359 (2026), DOI 10.1038/s41598-025-34462-w. Received 5 Jul 2025, accepted 29 Dec 2025, published 30 Jan 2026. Open access, CC BY 4.0. | [STATED] p.1, p.26, p.28 |
| Code / dataset | Code not mentioned. Datasets "available from the corresponding author on reasonable request". | [MISSING] code; [STATED] data (p.25) |
| Problem | Workflow scheduling over IoT–Fog–Cloud (IFC). Single objective formed as a weighted sum of makespan MS, total energy TE and total cost TC (Eq. 8, p.8). **No deadline.** | [STATED] |
| Static or dynamic | Static: a whole mapping vector is optimized. Dynamic migration is mentioned only as a benefit of VMs at the edge. | [IMPLIED] |
| Algorithm type | Hybrid metaheuristic. IPSO (linearly decreasing inertia weight) for the first maxIter/2 iterations, then GWO. | [STATED] Alg. 1, p.13 |
| Verdict | **Partly feasible: skeleton yes, reproducing numbers no.** | |

**Verdict reasoning**
- The skeleton is clear: two phases, Eq. 9–11 and Eq. 12–17, and Table 3 parameters.
- Fitness evaluation is delegated to the FogWorkflowSim framework and not specified:
  - how tasks are ordered on a VM,
  - how transfer times are computed,
  - how makespan arises.
- Continuous-to-integer rounding and the wolf-seeding perturbation are not specified.
- Several formula and table inconsistencies exist (see C.7).
- Results depend on the simulator, so numbers are not reproducible without it.

## B. System model (IPSO-GWO)

**Task model**
- DAG G = (T, E), E ∋ d_{i,j} = ⟨t_i, t_j⟩ with data output size d_{i,j}. A child starts only after the parent finishes. [STATED] p.6.
- Workflows are from the Pegasus family: Montage, Epigenomics, CyberShake, SIPHT, LIGO, with 100, 500 and 1000 tasks. [STATED] p.13–15.
- Task length unit (MI or similar): not stated. [MISSING]
- The data size unit: not stated. [MISSING]

**VM / resource model (Table 2, p.14, "environment parameter setting")**

| Parameter | EDs | FDs | CDs |
|---|---|---|---|
| Number of servers/devices | 5 | 5 | 5 |
| Processing rate (MIPS) | 1000 each | 1200, 1300, 1400, 1500, 1600 | 1600, 1700, 1800, 1900, 2000 |
| Task execution cost ($) | 0 | 0.1, 0.2, 0.3, 0.4, 0.5 | 0.5, 0.6, 0.7, 0.8, 0.9 |
| Communication cost ($) | 0 | 0.01 | 0.02 |
| Working power (labeled "MW") | 700 | 800 | 1600 |
| Idle power (labeled "MW") | 30 | 40 | 1300 |
| Uplink bandwidth (Mbps) | 20 | 10 | 1 |
| Downlink bandwidth (Mbps) | 40 | 10 | 10 |

- The table is attributed to ref [38]. [STATED]
- The power unit "MW" is as printed and is probably wrong. Fig. 9 etc. report energy in J. [MISSING: real unit]
- The unit of execution cost (per second? per MI?): not stated. [MISSING]
- Number of VMs: Table 2 lists 15 devices. Fig. 5's example uses 3 cloud + 2 fog + 1 ED VM. VMs per device is not stated. If one VM per device, V = 15. [MISSING / IMPLIED]
- Heterogeneity is by tier (ED, FD, CD), speed, price and power. [STATED]
- Billing period: **none**. Cost = price × (FT − ST), not rounded (Eq. 5). [STATED] p.8. Boot delay and performance variability: not mentioned.

**Network model**
- Tier-dependent uplink and downlink bandwidths (Table 2). [STATED]
- The formula for data transfer *time* is not given in the paper. [MISSING] It is delegated to FogWorkflowSim.
- Communication *cost* is CC_{i,j} = trc_{i,j} · d_{i,j}, and trc = 0 on the same resource (Eq. 6). [STATED]
- Same-VM transfer *time* is not stated. [MISSING]

**Energy model**
- Formal model (p.7), DVFS-style:
  - Eq. 2: E_idle = Σ_{j=1}^{m} Σ_{idle_{i,k} ∈ IDLE_{i,k}} α · f_{min j} · V²_{min j} · L_{j,k}
  - Eq. 3: E_active = Σ_{i=1}^{n} α · f_i · V_i² · (FT_{t_i} − ST_{t_i})
  - Eq. 4: TE = E_active + E_idle
- **Actual simulation model (p.16):** the paper states the simulator "does not dynamically model voltage and frequency scaling". It uses predefined constant busy and idle power per device. [STATED]
  - This matches your tenant-side form, busy power × busy time + idle power × idle time, with no DVFS. [IMPLIED]
- α, f, V values: not given. [MISSING]
- The idle-slot horizon (from time 0, from first task, or over the lease) is not defined. [MISSING]

**Deadline model**
- None. [STATED by absence]

**Assumptions my model might violate**
- No deadline and no billing period.
- No boot delay.
- Cost includes communication cost.
- A three-tier network with asymmetric bandwidths.
- Raw weighted sum of unlike units (see C.5).

## C. Algorithm specification (IPSO-GWO)

### C.1 Equations (verbatim notation)

| Eq. | Content | Cite |
|---|---|---|
| (1) | MS = max FT_{t_i} − min ST_{t_i}, t_i ∈ T | p.7 |
| (2)–(4) | Energy (above) | p.7–8 |
| (5) | CE_i^r = p_r · (FT_{t_i} − ST_{t_i}) | p.8 |
| (6) | CC_{i,j} = trc_{i,j} · d_{i,j}; trc_{i,j} = 0 on the same resource | p.8 |
| (7) | TC = Σ_i Σ_j CC_{i,j} + Σ_r Σ_j CE_i^r (index use is loose) | p.8 |
| (8) | F(p) = w1·MS + w2·TE + w3·TC | p.8 |
| (9) | V_i(t+1) = w_i·V_i(t) + C1·r1·(pbest − X_i(t)) + C2·r2·(gbest − X_i(t)) | p.8 |
| (10) | X_i(t+1) = X_i(t) + V_i(t+1) | p.8 |
| (11) | w^t = w_end + (w_begin − w_end) × (maxIter − Iter)/maxIter | p.9 |
| (12) | X1 = Xα − A1·Dα; X2 = Xβ − A2·Dβ; X3 = Xδ − A·Dδ | p.9 |
| (13) | Dα = \|C1·Xα − X(t)\|; Dβ = \|C2·Xβ − X(t)\|; Dδ = \|C3·Xδ − X(t)\| | p.9 |
| (14) | C = 2 × r2 | p.9 |
| (15) | A = 2 × a × r1 − a | p.9 |
| (16) | a(t) = 2 − 2×t / I_max | p.10 |
| (17) | X_{i-GWO}(t+1) = (X1(t) + X2(t) + X3(t)) / 3 | p.10 |

### C.2 Encoding
- An M-dimensional integer vector, one gene per task. The gene's index is the task's "sequence number". Its value k ∈ [1, VMs] is the VM chosen for that task. [STATED] p.11.
- "The K numbers are taken from the suitable VMs within the corresponding architecture layer". It is unclear whether that restricts the range per task. [AMBIGUOUS]
- Fig. 5 example, 9 tasks: P = (5, 2, 1, 4, 3, 6, 1, 6, 4). Resulting mapping: VM1 {3, 7}, VM2 {2}, VM3 {5}, VM4 {4, 9}, VM5 {1}, VM6 {6, 8}. [STATED] The example text is consistent with the vector.
- The same vector is used by particles and wolves. Only the "representation shifts" from particle to wolf. [STATED] p.12.
- Whether the gene order is a valid topological order, and how tasks on the same VM are ordered in simulation: not stated. [MISSING]

### C.3 Step-by-step (paper's order)

**Phase 1: IPSO** (Alg. 1, p.13; flowchart Fig. 6, p.12)
1. Initialize the IPSO population (N = popSize = 25) with random task-to-VM mappings. (L1)
2. Set w_begin, w_end, c1, c2, maxIter. (L2)
3. For iteration = 1 to maxIter/2: (L3)
   1. Compute the inertia weight (Eq. 11).
   2. For each particle: (i) evaluate F(P) (Eq. 8); (ii) update velocity (Eq. 9); (iii) update position (Eq. 10); (iv) update pbest and gbest.

**Phase 2: GWO**
4. Initialize the GWO population with gbest as the α wolf. (L5)
   - Other wolves are "slightly perturbed" versions of the IPSO solutions, "around the best particle and randomly selected particles". (p.12) The perturbation operator and size are not given. [MISSING]
5. For iteration = maxIter/2 + 1 to maxIter: (L6)
   1. Update positions by GWO encircling and hunting (Eq. 12–17).
   2. Evaluate F(P).
   3. Update α, β, δ by fitness.
6. Return the α wolf as the "task-to-VM" mapping. (L7)

**Notes**
- The pseudocode lists "Return α-wolf" as step 7 and an extra "End For" as step 8, so loop nesting is garbled. [conflict, minor]
- In step 3, evaluation precedes the velocity/position update. pbest/gbest are updated after the move. Standard PSO evaluates *after* moving. Possible readings: (a) evaluation of the new position is meant (standard); (b) literally evaluate the old position, then update using the new fitness (incoherent). Reading (a) is the usable one. [AMBIGUOUS]

### C.4 Initialization
- IPSO: "Randomly generate initial velocity and position" (Fig. 3 flowchart, p.9). Ranges are not given. [MISSING]
- GWO: α = IPSO gbest. The others are perturbed copies (C.3 step 4). [MISSING details]
- Real-to-integer handling: the update equations produce continuous values, but genes are integers in [1, VMs]. Rounding, clamping, discretization: not stated. [MISSING]

### C.5 Fitness and constraints
- F(p) = 0.2·MS + 0.2·TE + 0.2·TC. Weights w1 = w2 = w3 = 0.2 (p.8, p.15). [STATED]
- No normalization of the three terms. [MISSING]
- **Insight [IMPLIED]:** since the weights are equal, the factor 0.2 only scales the fitness and does not change the ranking. The effective objective is MS + TE + TC.
- Units differ (seconds, joules, dollars), so the larger-scale term dominates. The scales vary by case: Epigenomics (Table 6) has MS, TE and TC within about 1.5–3× of each other, while SIPHT at 100 tasks (Table 8) has TE (332) roughly ten times smaller than MS (3379) and TC (3666).
- No deadline and no constraint handling. [STATED by absence]

### C.6 Termination, tie-breaking, edge cases
- Termination: fixed iteration count maxIter = 100 ("set to 100", p.11). IPSO runs 1..50 and GWO runs 51..100. [STATED]
- Tie-breaking: not stated. [MISSING]
- Edge cases, parent-before-child enforcement in the evaluator: handled by the simulator's workflow engine, not by the algorithm. [STATED] p.6.

### C.7 Contradictions and ambiguities

| # | Conflict | Quotes (<15 words) | Readings |
|---|---|---|---|
| 1 | maxIter in Eq. 11 | Eq. 11 uses maxIter; IPSO runs only maxIter/2 | (a) maxIter = 100: w goes 0.8 → 0.55 over the IPSO phase. (b) maxIter = 50: w goes 0.8 → 0.3. |
| 2 | a(t) in Eq. 16 | "linearly decreased throughout iterations from 2 to 0" | (a) t counts from GWO start with I_max = 50: a = 2 → 0. (b) t is the global counter 51..100, I_max = 100: a = ~1 → 0. |
| 3 | r1, r2 in GWO | "r1, r2 are constant numbers in the interval (0, 1)" vs Table 3 "r1, r2 [0,1]" | Eq. 14–15 only make sense with random draws. |
| 4 | GWO A and C in Table 3 | Table 3 lists "A 0", "C 0" | Contradicts Eq. 14–15. Likely table formatting. |
| 5 | Eq. 12 third line | uses "A" where A3 is expected | Typo for A3 |
| 6 | VM counts | Table 2: 5+5+5 devices; Fig. 5 example: 3+2+1 | Different examples; algorithm size is VMs |
| 7 | Energy | Eq. 3 uses per-task f_i, V_i; sim uses constant power | Use the simulator's constant model (p.16) |
| 8 | "IPSO improvements" | "These improvements typically include:" three items | Only LDIW is used in Alg. 1 and Table 3 (fixed C1 = C2 = 2). Others are generic. |
| 9 | Results claims | Abstract/Conclusion claim consistent superiority | ANOVA Tables 5–8 show GWO best for CyberShake MS and TE, and GSA best for LIGO and SIPHT cost |
| 10 | Table 4 (Montage ANOVA) | 1000-task makespan mean 1473.9, equal to the 500-task cost mean | Smaller than the 500-task makespan mean 1545.9, which conflicts with Fig. 8. Likely a typo. |
| 11 | "Mean value" in Tables 4–8 | column header only | Mean over all algorithms, or IPSO-GWO's mean? The text for Epigenomics treats it as IPSO-GWO's. |
| 12 | Eq. 7 indices | Σ_i Σ_j CC_{i,j} + Σ_r Σ_j CE_i^r | Index i appears free in the second term. Read as a sum over tasks of the cost on the assigned resource. |

## D. Parameters (IPSO-GWO)

| Parameter | Symbol | Value | Label | Source |
|---|---|---|---|---|
| IPSO particles | N | 25 | STATED | Table 3, p.14 |
| Cognitive/social | C1, C2 | 2 | STATED | Table 3 |
| Inertia (start) | w_begin | 0.8 | STATED | Table 3 |
| Inertia (end) | w_end | 0.3 | STATED | Table 3 |
| r1, r2 | – | [0, 1] | STATED | Table 3 |
| Standard PSO baseline | N, C1 = C2, w | 25, 2, 1 | STATED | Table 3 |
| GWO wolves | popSize | 25 | STATED | Table 3 |
| GWO a | a | 2 → 0 (Eq. 16) | STATED | Table 3, p.10 |
| GWO A, C (Table 3) | A, C | "0", "0" | conflicts with Eq. 14–15 | Table 3 |
| GSA (baseline) | popSize, G0, α_GSA | 25, 1, 20 | STATED | Table 3 |
| Total iterations | maxIter | 100 | STATED | p.11 |
| Phase switch | – | maxIter/2 | STATED | p.11–13 |
| Objective weights | w1 = w2 = w3 | 0.2 | STATED | p.8, p.15 |
| Runs per config | – | 100 | STATED | p.14, p.15 |
| Hybrid's own parameters | – | "set to match those of the baseline algorithms" | IMPLIED: use the IPSO and GWO rows | p.15 |
| Environment | – | Table 2 (see B) | STATED | p.14 |
| Velocity init range / v_max | – | – | **MISSING** | |
| Real-to-integer mapping | – | – | **MISSING** | |
| Wolf perturbation (operator, rate) | – | – | **MISSING** | |
| VMs per device | – | – | **MISSING** | |
| Task length / data size units | – | – | **MISSING** | |
| α, f, V (Eq. 2–3) | – | – | **MISSING** (not used by the simulator) | |
| Power and price units | – | – | **MISSING / unclear** | |
| Seeds | – | – | **MISSING** | |

## E. Experimental setup (IPSO-GWO)

- **Simulator:** FogWorkflowSim (extends WorkflowSim and iFogSim), Eclipse Java IDE. Machine: Intel i7 M640 2.80 GHz, 6 GB RAM, Windows 10. [STATED] p.14.
- **Workflows:** Montage, Epigenomics, CyberShake, SIPHT, LIGO, each at 100, 500 and 1000 tasks (Pegasus). [STATED]
- **Runs:** 100 per algorithm per workflow and size. [STATED]
- **Baselines:** PSO [17, 29], IPSO [31], GWO [35], GSA [63]. All with the same population size (25). [STATED]
- **Statistics:** one-way ANOVA per workflow, size and metric (Tables 4–8, p.22–23).
- **Reported results.** The text gives percentage changes of IPSO-GWO relative to each baseline (plots in Figs. 8–22, no data tables). **Positive = IPSO-GWO better**, 100 / 500 / 1000 tasks.

**Montage (Figs. 8–10)**

| Metric | vs PSO | vs IPSO | vs GWO | vs GSA |
|---|---|---|---|---|
| MS | 21.51 / 17.32 / 32 | 15.68 / 6.04 / 24.62 | 0.99 / 17.89 / 5.76 | 11.24 / 28.77 / 24.62 |
| TE | 22.28 / 16.81 / 9.10 | 5.50 / 0.16 / 0.20 | 21.50 / 19.55 / 12.98 | 43.56 / 35.72 / 18.51 |
| TC | 15.61 / 14.92 / 10.64 | 4 / 3.36 / 8.41 | 13.42 / 25.15 / 9.64 | 1.78 / 11.46 / 10.21 |

**CyberShake (Figs. 11–13).** Negative = IPSO-GWO worse.

| Metric | vs PSO | vs IPSO | vs GWO | vs GSA |
|---|---|---|---|---|
| MS | 12.05 / 14.64 / 10.48 | 11.83 / 1.43 / 12.95 | −15.29 / −3.90 / −16.90 | −11.49 / −6.94* / −6.32 |
| TE | 21.74 / 33.42 / 25.99 | 9.79 / 0.50 / 6.56 | −9.78 / −16.43 / −7.49 | 31.84 / 23.33 / 33.34 |
| TC | 38.85 / 27.05 / 17.72 | 1.34 / 2.81 / 15.47 | 55.92 / 48.75 / 36.44 | 59.24 / 41.43 / 44.79 |

\*The text says the 500-task case "reduces MS than GSA by -6.94%". The sign is ambiguous.

**Epigenomics (Figs. 14–16)**

| Metric | vs PSO | vs IPSO | vs GWO | vs GSA |
|---|---|---|---|---|
| MS | 8.21 / 5.42 / 3.88 | 1.22 / 1.25 / 4.22 | 16.89 / 0.17 / 11.61 | 29.98 / 30.61 / 45.06 |
| TE | 42.13 / 31.03 / 21.79 | 9.75 / 0.26 / 1.79 | 76.85 / 35.87 / 27.68 | 79.56 / 49.44 / 38.12 |
| TC | 5.55 / 11.16 / 12.51 | 3.22 / 6.60 / 6.25 | 2.78 / 7.68 / 8.70 | 7.06 / 4.07 / 7.85 |

**LIGO (Figs. 17–19)**

| Metric | vs PSO | vs IPSO | vs GWO | vs GSA |
|---|---|---|---|---|
| MS | 11.31 / 11.01 / 5.26 | 0.70 / 0.40 / 0.55 | 17.11 / 16.41 / 10.78 | 25.87 / 50.64 / 49.01 |
| TE | 28.91 / 5.44 / 13.74 | 6.75 / 0.12 / 10.31 | 50.68 / 7.04 / 17.42 | 56.87 / 20.28 / 25.45 |
| TC | PSO better by 0.78 / 2.42 / 4.03 | +0.79 / +1.69 / −1.73 | + at 100; −5.16 / −5.50 | GSA better by 10.95 / 11.45 / 9.45 |

**SIPHT (Figs. 20–22)**

| Metric | vs PSO | vs IPSO | vs GWO | vs GSA |
|---|---|---|---|---|
| MS | 0.28 / 15.89 / 11.63 | 10.33 / 13.93 / 15.96 | 20.86 / 17.98 / 19.53 | 18.81 / 40.89 / 49.79 |
| TE | 4.94 / 26.60 / 32.36 | 0.62 / 23.40 / 27.71 | 15.46 / 30.81 / 43.61 | 23.88 / 42.25 / 43.79 |
| TC | 12.72 (100); 0.36 / 0.72 (500 / 1000) | 2.63 (100); −4.57 / −5.53 | 9.46 (100); −8.44 / −11.96 | 2.72 (100); −13.88 / −15.22 |

**Sanity-check numbers from the ANOVA tables.** "Mean value" is of unclear scope (C.7 #11).

| Workflow | 100 tasks (MS / TE / TC) | 500 | 1000 |
|---|---|---|---|
| Montage (Table 4) | 568.52 / 194.01 / 525.08 | 1545.9 / 1063.5 / 1473.9 | MS 1473.9 (suspect) / 2322.4 / 3206.6 |
| CyberShake (Table 5) | 60,529 / 2438 / 16,148 | 68,202 / 4601.4 / 38,266 | 1.0152e5 / 8337.9 / 77,035 |
| Epigenomics (Table 6) | 60,310 / 19,783 / 98,880 | 1.2586e5 / 1.6296e5 / 3.031e5 | 1.3171e5 / 2.5733e5 / 3.5169e5 |
| LIGO (Table 7) | 2412 / 2037.5 / 4811.4 | 7417.2 / 21,497 / 23,128 | 15,415 / 41,764 / 46,178 |
| SIPHT (Table 8) | 3378.6 / 332.36 / 3666 | 7423.7 / 12,752 / 19,328 | 12,926 / 23,901 / 39,308 |

- ANOVA significance and best algorithm:
  - Makespan and cost are not significant for Montage.
  - CyberShake: GWO best on MS and TE; IPSO-GWO best on cost, not significant.
  - Epigenomics: IPSO-GWO best and significant on everything.
  - LIGO and SIPHT: IPSO-GWO best on MS and TE, and GSA best on cost, except SIPHT at 100 tasks.
- Your re-implementation will not reproduce these without FogWorkflowSim and its Table 2 settings. Use them only for order-of-magnitude checks.

## F. Gaps and adaptation report (IPSO-GWO)

### F.1 Numbered gaps with suggested defaults (all **MY ASSUMPTION**)

| # | Gap | Suggested default (MY ASSUMPTION) | Why reasonable | Impact |
|---|---|---|---|---|
| I1 | Continuous → integer genes | round to nearest integer, clamp to [1, V] | Simplest mapping consistent with integer VM IDs | Medium |
| I2 | v(0) range, v_max | v ~ U(−(V−1)/2, (V−1)/2); clamp to ±(V−1)/2 | Prevents huge jumps | Medium |
| I3 | maxIter in Eq. 11 | Literal reading (maxIter = 100 total) | The equation says maxIter; alternative (b) in C.7 #1 is a variant to test | Low–Med |
| I4 | a(t) in Eq. 16 | Use phase-local t with I_max = maxIter/2 so a goes 2 → 0 | Gives the standard full exploration-to-exploitation sweep | Medium |
| I5 | r1, r2 in GWO | Fresh U(0,1) per wolf per dimension per iteration | Eq. 14–15 need randomness | Medium |
| I6 | Wolf seeding | α = gbest. For each other wolf, copy gbest or a random pbest, then mutate each gene to a random VM with probability 0.1 | "Slightly perturbed" is unquantified | Medium |
| I7 | Normalization | Keep raw terms for fidelity. For your model also run a normalized variant (each term divided by a reference such as a baseline schedule's value). | Raw terms let the largest-scale term dominate | **High** |
| I8 | Evaluator / scheduling semantics | Process tasks in topological order (e.g. by upward rank); each task runs on its assigned VM at max(VM available, parents' data ready); append-only per VM | The paper leaves this to FogWorkflowSim | **High** |
| I9 | Idle-energy horizon | Idle = lease span (first start to last finish, or billed span) − busy time | Matches your tenant-side model | Medium |
| I10 | VMs per device | One VM per device, so V = 15 (Table 2) | Consistent with "VMs" as the encoding range | Medium |
| I11 | Evaluation/update order | Move first, evaluate the new position, then update pbest/gbest | Standard PSO | Low |
| I12 | Layer restriction | No per-task layer restriction | The sentence is vague | Low–Med |
| I13 | Seeds | Fixed master seed, 100 runs | Reproducibility | Low |
| I14 | Transfer-time formula | time = d / min(uplink of source tier, downlink of target tier), 0 on same VM | Table 2 gives per-tier up/down bandwidth only | Medium |

### F.2 Where IPSO-GWO differs from MY MODEL

| Aspect | IPSO-GWO | My model | Minimal change |
|---|---|---|---|
| Deadline | none | deadline D | Add a penalty to F: F' = F + Λ·max(0, MS − D)/D, or feasible-first comparison |
| Billing | price × (FT − ST), no rounding | fixed period, rounded up | Replace Eq. 5 with ⌈lease span/BI⌉ × price per VM |
| Boot delay | none | yes | Add b to VM availability for first use. Include in lease. |
| Energy | Eq. 2–4 (but the sim uses constant power) | busy + idle power, no DVFS | Use the simulator's constant-power form: E = Σ_v (P_busy × busy_time + P_idle × idle_time). Drop α, f, V. |
| Cost | execution + communication | only VM billing | Drop CC (set trc = 0) |
| Network | per-tier up/down bandwidth | assumed single | Use a single bandwidth, or keep per-tier |
| Objective | weighted sum | min cost s.t. deadline (probably) | Pick the objective for the baseline role. Keep the weighted sum for fidelity. |
| Metrics | MS, TE, TC | + utilization, deadline success | Compute post-hoc |

### F.3 What changes results noticeably vs slightly
- **Noticeably:** I4, I6, I7, I8, I9, I10, the deadline and billing adaptations.
- **Slightly:** I3, I11, I13.

### F.4 Questions to resolve before coding
1. Which objective do you want: the paper's weighted sum, or cost with a deadline?
2. Normalized or raw terms?
3. How many VMs per device?
4. What are the real units for power and prices?
5. Which a(t) variant (C.7 #2)?
6. How are the wolves perturbed?
7. How are real values converted to integer VM IDs?

## G. Implementation checklist (IPSO-GWO)

1. **Setup.** V VMs (Table 2 → 15 if one VM per device). maxIter = 100, popSize = 25, w_begin = 0.8, w_end = 0.3, C1 = C2 = 2, weights 0.2.
2. **Evaluator** (your own, per I8): given mapping vector P, build the schedule in topological order, compute MS, TE, TC → F(P) = 0.2·MS + 0.2·TE + 0.2·TC (or your normalized or deadline-penalized variant).
3. **Phase 1.**
   1. Init particles with random integer VM IDs and random velocities.
   2. For iter = 1..50: w = w_end + (w_begin − w_end)(maxIter − iter)/maxIter.
   3. For each particle: update V (Eq. 9) and X (Eq. 10), round and clamp (I1), evaluate, update pbest and gbest.
4. **Switch.**
   1. α = gbest.
   2. Create popSize − 1 other wolves by perturbing gbest and random pbests (I6).
5. **Phase 2.** For iter = 51..100:
   1. Sort wolves by F. α, β, δ = best three.
   2. a = 2 − 2t/I_max (I4).
   3. For each wolf and dimension: A_k = 2a·r1 − a, C_k = 2·r2. D_k = |C_k·X_k − X|, X_k' = X_k − A_k·D_k for k = α, β, δ. New X = (X1 + X2 + X3)/3. Round and clamp.
   4. Evaluate.
6. Return the α wolf.
7. **Report** MS, cost, TE, utilization and deadline success (post-hoc). Compare at 100/500/1000 tasks with ANOVA if desired.

---

# PAPER 3 — PACM (Path-Aware Cost Minimization)

## A. Screening (PACM)

| Item | Content | Label / cite |
|---|---|---|
| Title | Path-Aware Scheduling Algorithm for Cost Optimization of Deadline-Constrained Scientific Workflows in Cloud Environments | [STATED] p.1247 |
| Authors | Lin Cheng, Jing Wu, Yu Gan, Ziyu Chen, Wei Hu (Wuhan Univ. of Sci. & Tech.) | [STATED] p.1247 |
| Venue / year | IEEE Transactions on Cloud Computing, vol. 13, no. 4, Oct–Dec 2025, pp. 1247–1258, DOI 10.1109/TCC.2025.3612584. Received 15 Jun 2025, accepted 17 Sep 2025. | [STATED] p.1247 |
| Code / dataset | No code mentioned. Workflows come from the Pegasus workflow generator (footnote 1, p.1253), DAX format. | [MISSING] code; [STATED] generator |
| Problem | DAG scheduling on IaaS. Minimize total cost (Eq. 9) s.t. FT(t_exit) ≤ D (Eq. 10). Single objective. No energy. | [STATED] p.1250 |
| Static or dynamic | Static plan per workflow. Alg. 1 line 1 triggers on "New Workflow arrives", but each workflow is planned once. Multi-workflow is future work. | [IMPLIED] |
| Algorithm type | Heuristic: probabilistic upward rank → sub-deadline division (CF/DAF/DIT) → VM mapping | [STATED] |
| Verdict | **Partly feasible** | |

**Verdict reasoning**
- Feasible because:
  - It is deterministic apart from the γ_j draws, and all steps are given as formulas (Eq. 1–27) plus Alg. 1.
- Not fully feasible because:
  - Table II (VM speeds and prices) is not in the text I have.
  - DAF (Eq. 20) is undefined for std = 0 and does not depend on task i.
  - Eq. 22 adds a dimensionless term to a time (see C.6).
  - The "upgrade" loop (Alg. 1 L24–26) and the fallback rule conflict with the prose.
  - The success-rate definition differs from the constraint in Eq. 10.
  - Several text/equation conflicts exist (see C.6).

## B. System model (PACM)

**Task model**
- DAG W: vertex set T = {t1..tn}, edges E = e_{i,j} with data_{i,j} (Table I). A task starts only after all parents finish and transfer data. [STATED] Sec. III-A, p.1249.
- ω_i = computational load in "CPU cycles". [STATED] p.1250. Virtual t_entry and t_exit exist (Fig. 1, Alg. 1). They are not discussed as zero-cost. [IMPLIED]
- The data size unit is not stated. [MISSING]

**VM model**
- Instance type defined by the tuple {ET(t_i, v_l), Cost_l}. ET(t_i, v_l) = ω_i / Speed_l (Eq. 2). [STATED] p.1250.
- Nine VM types, "Table II lists the nine types" (p.1254). **The Table II values are not available in the extracted text.** [MISSING in this extraction]. Read p.1254 of the PDF directly.
- Billing: one-hour interval. Used time is rounded up: Cost(v_l) = ⌈(VLFT(v_l) − VLST(v_l)) / interval⌉ × Cost_l (Eq. 8). [STATED] p.1250.
  - The text defines the lease time as "start time (VLFT) … end time (VLST)", with the two labels swapped. This is a typo. [conflict, minor]
- Lease start VLST (Eq. 6) = ST(t_i, v_l) − max over t_p ∈ pred(t_i) of TT_{e_{p,i}}, for the first task t_s on the instance. That is, the lease starts when data begins arriving. [STATED]
- Lease finish VLFT (Eq. 7) = FT(t_i, v_l) + max over t_m ∈ succ(t_i) of TT_{e_{i,m}}, for the last task t_e. That is, the lease ends when output transfer finishes. [STATED]
- Boot delay and performance variability: not mentioned. [MISSING / not modeled]
- VM count limit: not stated. For the HEFT reference on the fastest type, instances are unlimited (p.1254). [IMPLIED unlimited]
- The paper notes EC2's per-second billing, but adopts hourly billing "to enable direct and fair comparisons" (p.1247). It says PACM is agnostic to billing granularity (p.1250). [STATED]

**Network model**
- One average bandwidth β between VMs in the same data center. TT_{e_{i,j}} = data_{i,j}/β (Eq. 1). It is 0 if parent and child are on the same VM. [STATED] p.1250.
- β = 20 Mbps (p.1254). The unit relation between data and Mbps is not stated. [MISSING]
- No storage or transfer fees. [STATED]

**Energy model**
- None. [STATED by absence]

**Deadline model**
- D = M_f + (M_s − M_f) × λ (Eq. 26, p.1254). [STATED]
  - M_f: HEFT makespan using only the fastest VMs, with no instance limit. Cost C_f.
  - M_s: HEFT makespan on **a single instance** of the slowest VM. Cost C_s.
- λ from 0.01 to 0.1 in steps of 0.01. [STATED] p.1254.
- NC = Cost(W) / C_s (Eq. 27). [STATED] p.1254.

**Assumptions my model may violate**
- No boot delay.
- No energy.
- VLST/VLFT include data transfer, so the lease span starts before the first task.
- A single uniform bandwidth.
- No VM-count limit.

## C. Algorithm specification (PACM)

### C.1 Equations needed

| Eq. | Content | Cite |
|---|---|---|
| (1) | TT_{e_{i,j}} = data_{i,j} / β (0 if same VM) | p.1250 |
| (2) | ET(t_i, v_l) = ω_i / Speed_l | p.1250 |
| (3) | ST(t_i, v_l) = max{ Avail(v_l), max over t_p ∈ pred(t_i) of [ FT(t_p, v_k) + TT_{e_{p,i}} ] } | p.1250 |
| (4) | FT(t_i, v_l) = ST(t_i, v_l) + ET(t_i, v_l) | p.1250 |
| (5) | EFT(t_i) = min over v_l ∈ V of FT(t_i, v_l) | p.1250 |
| (6) | VLST(v_l) = ST(t_i, v_l) − max over t_p ∈ pred(t_i) of TT_{e_{p,i}} | p.1250 |
| (7) | VLFT(v_l) = FT(t_i, v_l) + max over t_m ∈ succ(t_i) of TT_{e_{i,m}} | p.1250 |
| (8) | Cost(v_l) = ⌈(VLFT − VLST) / interval⌉ × Cost_l | p.1250 |
| (9) | Minimize Cost(W) = Σ_{l=1}^{V} Cost(v_l) | p.1250 |
| (10) | Subject to FT(t_exit) ≤ D | p.1250 |
| (11) | mr(t_i) = max over t_j ∈ succ(t_i) of ( mr(t_j) + γ_j × TT_{e_{i,j}} ) + ET(t_i, v_f) | p.1251 |
| (12) | γ_j = 0 if 1 − θ^{−τ_j} < rand(); 1 otherwise | p.1251 |
| (13) | τ_j = ET(t_i, v_f) / TT_{e_{i,j}} | p.1251 |
| (14) | CPL_u(t_i) = ET(t_i) + max over t_j ∈ succ(t_i) of { TT_{e_{i,j}} + CPL_u(t_j) } | p.1251 |
| (15) | CPL_d(t_i) = max over t_p ∈ pre(t_i) of { TT_{e_{p,i}} + CPL_d(t_p) + ET(t_p) } | p.1251 |
| (16) | CPL(t_i) = CPL_u(t_i) + CPL_d(t_i) | p.1251 |
| (17) | CF = 1 if the task is on the critical path; 0 otherwise | p.1251 |
| (18) | LFT(t_i) = D if t_i = t_exit; otherwise min over t_j ∈ succ(t_i) of { LFT(t_j) − ET(t_j, v_f) − TT_{e_{i,j}} } | p.1251 |
| (19) | SubD(t_i) = ( mr(t_entry) − mr(t_i) + ET(t_i, v_f) ) / mr(t_entry) × D (general form; grouping inferred from the extraction) | p.1251 |
| (20) | DAF(t_i) = maxInEdge / stdInEdge | p.1251 |
| (21) | stdInEdge = sqrt( (1/n) Σ_{i=1}^{n} ( InE(t_i) − (1/n) Σ_{j=1}^{n} InE(t_j) )² ) | p.1252 |
| (22) | CF = 0: SubD(t_i) = ( mr(t_entry) − mr(t_i) + ET(t_i, v_f) + DAF × InE/SumIE ) / mr(t_entry) × D | p.1252 |
| (23) | DIT(t_i) = ( Σ_{h=entry}^{i} TT_{e_{h,h+1}} ) / mr(t_entry) | p.1252 |
| (24) | CF = 1: SubD(t_i) = LFT(t_i) − DIT(t_i) × ( mr(t_entry) − mr(t_i) ) | p.1252 |
| (25) | inCost(t_i, v_l) = Cost_now − Cost_old | p.1253 |
| (26) | D = M_f + (M_s − M_f) × λ | p.1254 |
| (27) | NC = Cost(W) / C_s | p.1254 |

- Definitions: InE = in-degree of a task; SumIE = sum of in-degrees of all tasks; maxInEdge = maximum in-degree; stdInEdge = standard deviation of in-degrees (Eq. 21). In Eq. 14–15, ET(t_i) is "the average execution time of task t_i on all processors" (p.1251).

### C.2 Step-by-step (paper's order)

**Step 1: Priority ranking (Sec. IV-A, Alg. 1 L1–4).** Compute mr(t_i) for all tasks (Eq. 11–13) and sort the list `pl` by descending mr.
- mr is the "probabilistic upward rank" from ref [22]. v_f is the fastest VM type.
- γ_j (Eq. 12) randomly decides whether the transfer time TT is included.
- θ = 1.5, greater than 1. [STATED] p.1254.
- mr of t_exit is not defined (zero is the natural base). [IMPLIED]
- Whether γ_j is drawn once per edge or on each use: not stated. [MISSING]

**Step 2: Critical path (Alg. 1 L5–12).**
- For each task, compute CPL (Eq. 14–16). Set CF = 1 if CPL(t_i) == CPL(t_entry), else CF = 0 (Alg. 1 L7).
- A floating-point tolerance for "==" is not stated. [MISSING]

**Step 3: Sub-deadlines (Alg. 1 L13–23).**
- If CF = 1: SubD from Eq. 24, which needs LFT (Eq. 18) and DIT (Eq. 23).
- If CF = 0: SubD from Eq. 22 (with DAF, InE, SumIE).

**Step 4: VM mapping (Alg. 1 L13–31), for each task in `pl` order:**
1. CF = 1: v_l ← the instance with earliest finish time that meets SubD(t_i). (L16)
2. CF = 0: v_l ← the instance with minimal inCost(t_i, v_l) that meets SubD(t_i). (L19)
   - If v_l is null: v_l ← the instance with earliest finish time that meets SubD(t_i). (L20–22)
3. While SubD(t_i) is not met and v_l is not the fastest type: upgrade the type of v_l to a faster type. (L24–26)
4. If v_l ∉ V: V ← V ∪ {v_l}. (L27–29)
5. R ← R ∪ {t_i, v_l, FT(t_i, v_l)}. (L30)
6. After the loop: return S = {V, R, Cost(W), FT(t_exit)}. (L32)

- Prose (Sec. IV-C, p.1252–1253):
  - The primary cost goal is the instance with the lowest *incremental* cost.
  - "Traverse all available VM instances": the candidate set is not defined further. [MISSING]
  - "If there is still no available VM at the end, the task is assigned on the instance with the smallest EFT", and the sub-deadline is disregarded.

### C.3 Initialization
- V = ∅, R = ∅ (Alg. 1 input line). [STATED]
- No random initialization except the γ_j draws. [IMPLIED]

### C.4 Termination
- One pass over all tasks in `pl`. [IMPLIED]

### C.5 Constraint / deadline handling
- The deadline is handled only through sub-deadlines. Task-level SubD tests decide VM choice. Overall feasibility FT(t_exit) ≤ D is required by Eq. 10 but is not enforced by a separate repair. [IMPLIED]
- Fallback: choose the smallest EFT and disregard SubD (prose, p.1253).
- Success rate (Fig. 9) is defined as "the ratio of the number of workflows satisfying all task sub-deadlines" to attempts (p.1256). [STATED]
  - This differs from the constraint in Eq. 10. See C.6 #9.

### C.6 Contradictions and ambiguities

| # | Issue | Quotes (<15 words) | Readings |
|---|---|---|---|
| 1 | τ_j definition vs Eq. 13 | Text: "ratio of communication time to computation time"; Eq. 13 = ET/TT | (a) Use Eq. 13 as written (computation/communication). (b) Use the prose (communication/computation), the inverse. The prose also says small τ_j makes γ_j = 0 more likely, which is true under Eq. 12 either way. Pick one and record it. |
| 2 | Critical path definition | "Critical path is the shortest path that determines the completion time" vs "the longest path from the start task to the end task" | Longest path is the only sensible reading. Treat "shortest" as a typo. |
| 3 | Eq. 22 dimensions | DAF · InE/SumIE added to mr (time) | A dimensionless term is added to times. Reading (a): add literally (a tiny effect if times are in seconds). Reading (b): the term was meant to be scaled by time. |
| 4 | Eq. 22 can exceed D for t_exit | For t_exit the base ratio equals 1 and the DAF term is added | SubD(t_exit) may exceed D. Cap at LFT or D. |
| 5 | DAF | Eq. 20 is DAF(t_i) but maxInEdge and stdInEdge are graph-level | DAF is the same for all tasks. Undefined when std = 0. |
| 6 | Fallback rule | Alg. L21: "…and meets SubD(t_i)"; prose: sub-deadline "will be disregarded" | (a) EFT among instances meeting SubD (can still be empty). (b) EFT with SubD ignored (prose). |
| 7 | CF = 1 constraint | Prose: satisfy "the overall deadline constraint"; Alg. L16: "meets SubD(t_i)" | Overall deadline D vs per-task SubD |
| 8 | Upgrade loop | L24–26: upgrade v_l type | Applies to a fresh instance only? An instance already holding tasks cannot change type without changing earlier tasks. |
| 9 | Success rate | Fig. 9 text: sub-deadlines; Eq. 10: FT(t_exit) ≤ D | Count by FT(t_exit) ≤ D for a strict constraint check. |
| 10 | Number of workflows | Sec. V-A: "two different scientific workflow applications"; Conclusion: "three typical" | Figures show CyberShake and Montage only. |
| 11 | Duplicated numbers | 1000 tasks: "20.5% lower than ProLis and 20.7% lower than CSDW" | Same numbers as the 500-task case. Likely copy-paste. |
| 12 | Rank equation refs | Sec. IV-A: "according to (1) and (2) by the probabilistic upward rank" | Equation numbers refer to TT and ET. mr is Eq. 11. |
| 13 | NC label | "gap … to the optimal scheduling cost" | NC divides by C_s (HEFT on a single slowest VM), not an optimum. |
| 14 | Eq. 7 and the placement unknown | VLFT adds max TT to successors | At assignment time successor placement is unknown. See F, P15. |
| 15 | Eq. 19 grouping | Extraction shows "mr(t_entry) − mr(t_i) + ET(t_i, v_f) / mr(t_entry) × D" | Fraction grouping read as ( … ) / mr(t_entry) × D. Check against the PDF p.1251. |

## D. Parameters (PACM)

| Parameter | Symbol | Value | Label | Source |
|---|---|---|---|---|
| Rank randomness | θ | 1.5 (> 1) | STATED | p.1254 |
| Billing interval | interval | 1 hour | STATED | p.1250, 1254 |
| Bandwidth | β | 20 Mbps | STATED | p.1254 |
| Deadline factor | λ | 0.01 to 0.1 step 0.01 | STATED | p.1254 |
| Workflow sizes | – | 50, 100, 500, 1000 | STATED | p.1254 |
| VM types | Speed_l, Cost_l | nine types, Table II | **MISSING in extracted text** | p.1254 |
| Workflow generator | – | Pegasus (Bharathi et al.) | STATED | p.1253 |
| Runs per configuration | – | – | **MISSING** | – |
| Seeds for γ_j | – | – | **MISSING** | – |
| CF equality tolerance | – | – | **MISSING** | – |
| Candidate-set definition | – | – | **MISSING** | – |
| Units of ω_i, Speed, data | – | – | **MISSING** | – |
| Boot delay | – | not modeled | MISSING | – |
| Simulator name | – | not named; platform: Intel i7 3.2 GHz, 8 GB, Windows 11, JDK 1.8.0 | MISSING (name) | p.1253 |

## E. Experimental setup (PACM)

- **Workflows:** CyberShake and Montage (Fig. 4, Sec. V-A). Sizes 50 / 100 / 500 / 1000. Generated by the Pegasus generator in DAX format. [STATED]
- **VMs:** nine types (Table II). bandwidth 20 Mbps, interval 1 h.
- **Deadline:** Eq. 26, λ = 0.01..0.1.
- **Baselines:** IC-PCP, CSDW, ProLiS (Sec. V).
- **Metrics:** NC (Eq. 27); success rate (Fig. 9, sub-deadline definition).
- **Number of runs:** not stated. [MISSING]
- **Results (Figs. 5–9, plots only; text numbers below):**
  - 50 tasks, CyberShake: NC lower by 16.7% vs ProLiS and 14.6% vs CSDW. Montage: "substantial" improvement, no number.
  - 100 tasks, CyberShake: 23.0% vs ProLiS and 20.6% vs CSDW. Montage: the benefit shrinks at relaxed deadlines. EFT-based mapping may miss sub-deadlines and add overhead.
  - 500 tasks, CyberShake: 20.5% vs ProLiS and 20.7% vs CSDW.
  - 1000 tasks, CyberShake: the same two numbers are repeated (see C.6 #11).
  - Cost falls as λ rises for all algorithms.
  - Success rate (Fig. 9): IC-PCP is clearly lower for λ ≤ 0.03. PACM, ProLiS and CSDW saturate for λ ≥ 0.05.
- **Sanity checks [IMPLIED]:**
  - At λ = 1, D = M_s, and a single slowest VM would meet it. A good scheduler should reach NC ≲ 1 there.
  - At λ = 0, D = M_f, and only the fastest-type parallel schedule is feasible.
  - λ ≤ 0.1 means deadlines are tight (within 10% of the M_f–M_s gap).

## F. Gaps and adaptation report (PACM)

### F.1 Numbered gaps with suggested defaults (all **MY ASSUMPTION**)

| # | Gap | Suggested default (MY ASSUMPTION) | Why reasonable | Impact |
|---|---|---|---|---|
| P1 | Table II values | Use your own VM catalog (speed, price) | Your model has its own catalog | Medium |
| P2 | DAF undefined for std = 0 | If std = 0, set DAF = maxInEdge (equivalent to std := 1). Cap DAF at maxInEdge. Count n over real tasks only. | Avoids division by zero. Keeps the term bounded. | Low |
| P3 | Eq. 22 dimensions / SubD > D | Add the DAF term literally, then clamp SubD(t_i) ≤ LFT(t_i) | A sub-deadline beyond LFT could break D. The term is tiny anyway (InE/SumIE ≈ 1/E). | Low |
| P4 | γ_j and τ_j | Draw γ_j once per edge at the start with a fixed seed. Use Eq. 13 as written (ET/TT). | Deterministic, reproducible ranking | Low–Med |
| P5 | CF tolerance and ET(t_i) | CF = 1 if CPL(t_i) ≥ CPL(t_entry)·(1 − 1e−9). ET(t_i) = arithmetic mean of ω_i/Speed over all VM types. | "Average on all processors" taken over VM types | **Medium** |
| P6 | DIT path | DIT(t_i) = sum of D/β along the critical-path chain from t_entry to t_i (no co-location assumption); for ties use the smallest sum | Eq. 23 needs a single ordered path | Medium |
| P7 | Candidate set for mapping | Existing instances in V plus one fresh instance of each type | Alg. 1 L27 adds new instances to V, so fresh ones must be candidates | **High** |
| P8 | Fallback rule | If no candidate meets SubD(t_i): take the smallest EFT, disregarding SubD (prose rule) | Prose is explicit on this | **High** |
| P9 | Upgrade loop | Apply only to fresh instances, equivalent to evaluating fresh instances of faster types in turn; stop at the fastest | An instance with tasks cannot change type retroactively | Medium |
| P10 | Ties | EFT ties → lower price, then lower index. inCost ties → earlier finish, then existing before fresh. | Deterministic | Medium |
| P11 | Success rate | Report SR as FT(t_exit) ≤ D (Eq. 10). Also report sub-deadline satisfaction separately. | Your model measures deadline success | Medium |
| P12 | Virtual nodes | Exclude from `pl`. ET = 0, edge data = 0. | They use no resource | Low |
| P13 | Avail(v_l) | FT of the last task on the instance (append-only) | Insertion is not mentioned | Medium |
| P14 | mr(t_exit) | 0 | Base case | Low |
| P15 | VLFT before successors are placed | While mapping, compute inCost with the worst-case outgoing transfer (max D/β over successors). Recompute the final cost with actual placement (0 if on the same VM). | Placement unknown at decision time | Medium–High |
| P16 | Units | Choose consistent units (e.g. data in MB, β in MB/s) | Paper leaves them open | Low |
| P17 | Runs and seeds | Single deterministic run per λ with a fixed seed for γ_j (optionally repeat with several seeds) | Not stated | Low |

### F.2 Where PACM differs from MY MODEL, and the minimal change

| Aspect | PACM | My model | Minimal change |
|---|---|---|---|
| Boot delay | none | boot delay b | Fresh instance: Avail = lease start + b. Choose the lease start so that boot finishes by the first task's ST. Keep the boot period billed. Adjust Eq. 6 (VLST) accordingly. |
| Billing | ⌈lease/interval⌉ × Cost_l, with the lease including data transfer | fixed period, rounded up | Same. Decide whether transfers are in the lease (P15). |
| Energy | none | busy power × busy time + idle power × idle time | Post-hoc: busy = Σ ET on the VM, idle = lease span − busy. Report only. |
| Heterogeneity | speed and price | same | Compatible |
| Deadline | D = Eq. 26 | deadline D | Plug in your D |
| Network | uniform β | assumed compatible | None |
| Static DAG | yes | yes | None |
| Metrics | cost, NC, SR | makespan, cost, energy, utilization, deadline success | Add utilization = Σ busy / Σ billed |

### F.3 What changes results noticeably vs slightly
- **Noticeably:** P5, P6, P7, P8, P9, P10, P11, P13, P15, and the boot-delay adaptation.
- **Slightly:** P2, P3, P4, P12, P14, P16, P17.

### F.4 Questions to resolve before coding
1. What are the Table II values (read p.1254)?
2. Are fresh instances part of the candidate set?
3. Should the fallback ignore SubD (prose) or keep it (L21)?
4. Is the upgrade loop restricted to fresh instances?
5. Do leases include data transfers (Eq. 6–7)?
6. How is "average ET over all processors" defined?
7. Success rate by sub-deadlines or by Eq. 10?

## G. Implementation checklist (PACM)

1. **Inputs.** DAG with ω_i and data_{i,j}, VM catalog (Speed_l, Cost_l), β, interval = 1 h, θ = 1.5, D (Eq. 26).
2. **Precompute.**
   1. v_f = fastest type. ET(t_i, v_f) = ω_i/Speed_f. Average ET(t_i) over types (P5).
   2. TT_{e_{i,j}} = data_{i,j}/β.
   3. Draw γ_j per edge (P4). mr in reverse topological order (Eq. 11–13). `pl` = tasks by descending mr.
   4. CPL_u, CPL_d, CPL (Eq. 14–16). CF = 1 where CPL ≈ CPL(t_entry).
   5. LFT (Eq. 18).
   6. InE per task, SumIE, maxInEdge, stdInEdge, DAF (P2).
   7. DIT along the critical path (Eq. 23, P6).
3. **Main loop**, for t_i in `pl`:
   1. SubD = Eq. 24 if CF = 1, else Eq. 22 (clamp, P3).
   2. Candidates = existing instances plus one fresh instance per type (P7). Compute ST (Eq. 3) and FT (Eq. 4) for each.
   3. Feasible = candidates with FT ≤ SubD.
   4. CF = 1: choose the feasible candidate with the smallest FT.
   5. CF = 0: choose the feasible candidate with the smallest inCost (Eq. 25); if none, the smallest-FT feasible one.
   6. If still none: choose the smallest-FT candidate, ignoring SubD (P8).
   7. Apply the upgrade rule only for fresh instances (P9). Break ties (P10).
   8. Record the assignment. Update V, R, Avail.
4. **Final.** Cost(W) = Σ Cost(v_l) (Eq. 8, with the lease from Eq. 6–7, P15). FT(t_exit) = max FT.
5. **Report** NC = Cost/C_s, success (FT(t_exit) ≤ D), plus your makespan, utilization, and post-hoc energy.

---

# Cross-paper notes

1. **Best baseline candidates for your model** (deadline, cost, per-period billing): PACM and WPSO. IPSO-GWO has no deadline or rounded-up billing, so its use as a deadline baseline needs the most adaptation.
2. **Shared adaptations** for all three:
   - Add boot delay b to new-instance availability.
   - Compute tenant energy post-hoc: Σ_v (P_busy · busy + P_idle · idle).
   - Compute utilization = Σ busy / Σ billed time.
   - Use one definition of lease span across all three so costs are comparable.
3. **Deadline definitions are not shared.**
   - WPSO: λ = 0.005–0.05 on [TL, TR].
   - PACM: λ = 0.01–0.1 on [M_f, M_s], where M_s is a *single* slowest instance.
   - If you compare them, generate D once and feed it to all.
4. **Normalization is not shared.**
   - WPSO NC = WEC / CR, where CR is HEFT cost on the slowest type.
   - PACM NC = Cost / C_s, where C_s is HEFT cost on a single slowest instance.
   - Use one reference for any cross-paper comparison.
5. **Data inconsistencies noticed while extracting:** WPSO MaxE vs stagnation, and the reachability of vm_m. IPSO-GWO Table 3 A = 0, C = 0, Table 4 makespan mean for 1000 tasks, and the ANOVA-vs-abstract claims. PACM's repeated 1000-task numbers and "two vs three workflows".
6. **Not extractable from the text layer:** curve values from plots (WPSO Figs. 4–5, PACM Figs. 5–9, IPSO-GWO bar heights) and PACM Table II. Open those pages if you need exact numbers.