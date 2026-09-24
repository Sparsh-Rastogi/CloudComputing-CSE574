# Cloud Scheduling Algorithms — Study Notes

> Based on: handwritten/class notes on Max-Min, Min-Min, Load Balancing, and Heuristic/Metaheuristic Workflow Scheduling in Cloud Computing

---

## Table of Contents
1. [Max-Min Scheduling](#1-max-min-scheduling)
2. [Min-Min Scheduling](#2-min-min-scheduling)
3. [Max-Min vs. Min-Min](#3-max-min-vs-min-min)
4. [Load Balancing Scheduling](#4-load-balancing-scheduling)
5. [Common Load-Balancing Algorithms](#5-common-load-balancing-algorithms)
6. [Static vs. Dynamic Load Balancing](#6-static-vs-dynamic-load-balancing)
7. [Workflow Scheduling in Cloud Computing](#7-workflow-scheduling-in-cloud-computing)
8. [Why Workflow Scheduling Is Difficult](#8-why-workflow-scheduling-is-difficult)
9. [Workflow Scheduling Objectives](#9-workflow-scheduling-objectives)
10. [Heuristic Algorithms](#10-heuristic-algorithms)
11. [Common Heuristic Workflow Scheduling Algorithms](#11-common-heuristic-workflow-scheduling-algorithms)
12. [Limitations of Heuristic Algorithms](#12-limitations-of-heuristic-algorithms)
13. [Metaheuristic Algorithms](#13-metaheuristic-algorithms)
14. [Heuristic vs. Metaheuristic](#14-heuristic-vs-metaheuristic)
15. [Hybrid Workflow Scheduling](#15-hybrid-workflow-scheduling)
16. [Example Classroom Problem](#16-example-classroom-problem)
17. [Key Takeaway](#17-key-takeaway)
18. [Quick Revision — Important Exam Questions](#18-quick-revision--important-exam-questions)

---

## 1. Max-Min Scheduling

**Max-Min Scheduling** is a task scheduling algorithm used in cloud computing to assign a set of tasks (cloudlets) to available virtual machines (VMs) or computing resources. It is particularly useful in **heterogeneous cloud environments**, where VMs have different processing capabilities.

### Basic Idea
The algorithm calculates the **Expected Completion Time (ECT)** of every task on every available VM.

For each task:
1. Calculate its expected execution/completion time on all VMs.
2. Find the **minimum completion time** for that task.
3. Among all tasks' minimum completion times, select the task having the **maximum** value.
4. Assign this task to the VM that provides its minimum completion time.
5. Update the availability/load of that VM.
6. Repeat until all tasks are scheduled.

Hence the name **Max-Min**: **Max**imum among the **Min**imum completion times.

### Example
Suppose there are **3 tasks** and **2 VMs**.

| Task | VM1 | VM2 | Minimum |
|---|---|---|---|
| T1 | 10 | 6 | **6** |
| T2 | 8 | 12 | **8** |
| T3 | 15 | 9 | **9** |

The minimum completion times are: T1 → 6, T2 → 8, T3 → 9.

The **maximum of these minimum values is 9**, so **T3 is scheduled first on VM2**. After assigning T3, the availability/load of VM2 is updated, and the process is repeated for T1 and T2.

**❓ Exam Questions:**
- Explain the Max-Min scheduling algorithm with its steps.
- Why is it called "Max-Min"?
- Solve a given task–VM completion-time table using Max-Min scheduling.

---

## 2. Min-Min Scheduling

**Min-Min algorithm:** For each task → find its minimum completion time → choose the task with the smallest minimum → assign it → update VM load → repeat.

### Example
Assume we have **3 tasks (T1, T2, T3)** and **2 Virtual Machines (VM1, VM2)**.

Execution times:

| Task | VM1 | VM2 |
|---|---|---|
| T1 | 8 | 4 |
| T2 | 6 | 10 |
| T3 | 12 | 7 |

**Step 1: Find the minimum time for each task**
- T1: min(8, 4) = **4** → VM2
- T2: min(6, 10) = **6** → VM1
- T3: min(12, 7) = **7** → VM2

| Task | Minimum Time | Selected VM |
|---|---|---|
| T1 | 4 | VM2 |
| T2 | 6 | VM1 |
| T3 | 7 | VM2 |

**Step 2: Select the minimum among them**
Minimum of 4, 6, 7 = **4** → **T1 is scheduled on VM2**. VM2 now has a load of **4**.

**Step 3: Recalculate for remaining tasks (T2, T3)**
VM2's previous load of 4 is added to its completion times:

| Task | VM1 | VM2* |
|---|---|---|
| T2 | 6 | 4 + 10 = 14 |
| T3 | 12 | 4 + 7 = 11 |

- T2 → min(6, 14) = **6** → VM1
- T3 → min(12, 11) = **11** → VM2

The minimum is **6**, so **T2 is scheduled on VM1**. VM1 now has a load of **6**.

**Step 4: Schedule the remaining task (T3)**

| Task | VM1 | VM2 |
|---|---|---|
| T3 | 6 + 12 = 18 | 4 + 7 = 11 |

**T3 is scheduled on VM2.**

### Final Schedule

| Order | Task | VM | Completion Time |
|---|---|---|---|
| 1 | T1 | VM2 | 4 |
| 2 | T2 | VM1 | 6 |
| 3 | T3 | VM2 | 11 |

- **VM1:** T2 → finishes at **6**
- **VM2:** T1 → T3 → finishes at **11**

**Makespan = max(6, 11) = 11 time units**

**❓ Exam Questions:**
- Explain the Min-Min scheduling algorithm with its steps.
- Solve a given task–VM completion-time table using Min-Min scheduling and find the makespan.

---

## 3. Max-Min vs. Min-Min

| Feature | Min-Min | Max-Min |
|---|---|---|
| **Selection** | Minimum of minimum completion times | Maximum of minimum completion times |
| **First preference** | Short tasks | Relatively longer tasks |
| **Main objective** | Quickly complete many small tasks | Avoid delaying large tasks |
| **Suitable for** | Workloads with many short tasks | Workloads containing long/heterogeneous tasks |
| **Risk** | Long tasks may starve | Small tasks may wait longer |

### Advantages (of Max-Min)
- Simple and easy to implement
- Works well with heterogeneous VMs
- Gives priority to relatively longer tasks, reducing the chance that they remain until the end
- Can improve load distribution compared with some simple scheduling strategies
- Useful for static task scheduling in cloud environments

### Disadvantages (of Max-Min)
- May increase the waiting time of short tasks
- Does not necessarily produce the globally optimal schedule
- Performance depends strongly on accurate execution-time estimates
- For highly dynamic clouds (VM failures, changing resource availability, continuously arriving tasks), more adaptive algorithms may be preferable

### Worked Example: Max-Min Scheduling
Assume 3 tasks (T1, T2, T3) and 2 VMs (VM1, VM2), same execution times as the Min-Min example:

| Task | VM1 | VM2 | Minimum | Selected VM |
|---|---|---|---|---|
| T1 | 8 | 4 | 4 | VM2 |
| T2 | 6 | 10 | 6 | VM1 |
| T3 | 12 | 7 | 7 | VM2 |

**Step 1:** Max-Min selects the **maximum among the minimum values**: max(4, 6, 7) = **7**. Therefore, **T3 is scheduled first on VM2**. VM2's current load becomes 7.

**Step 2:** Recalculate for T1 and T2 (VM2 already occupied for 7 units):

| Task | VM1 | VM2 | Minimum | Selected VM |
|---|---|---|---|---|
| T1 | 8 | 7+4=11 | 8 | VM1 |
| T2 | 6 | 7+10=17 | 6 | VM1 |

max(8, 6) = **8** → **T1 is scheduled on VM1**. VM1's load becomes 8.

**Step 3:** Only T2 remains:

| Task | VM1 | VM2 |
|---|---|---|
| T2 | 8+6=14 | 7+10=17 |

**T2 is scheduled on VM1.**

### Final Schedule (Max-Min)

| Order | Task | VM | Completion Time |
|---|---|---|---|
| 1 | T3 | VM2 | 7 |
| 2 | T1 | VM1 | 8 |
| 3 | T2 | VM1 | 14 |

- **VM1:** T1 → T2 → finishes at **14**
- **VM2:** T3 → finishes at **7**

**Makespan = max(14, 7) = 14**

### Key Difference
- **Min-Min:** Select the **smallest** value among the tasks' minimum completion times.
- **Max-Min:** Select the **largest** value among the tasks' minimum completion times.

In this example, Max-Min selects **T3 first** because its best possible completion time (7) is the largest among 4, 6, and 7. This gives the relatively longer task an early start and helps prevent it from becoming a bottleneck later.

**❓ Exam Questions:**
- Compare Min-Min and Max-Min on selection criterion, first preference, objective, suitability, and risk.
- Using the same task–VM table, compute schedules with both Min-Min and Max-Min and compare the resulting makespans.

---

## 4. Load Balancing Scheduling

**Load balancing scheduling** is a technique in cloud computing that distributes tasks or workloads among available Virtual Machines (VMs), servers, or cloud resources so that no single resource becomes heavily overloaded while others remain underutilized.

### Main Objective
- Balanced resource utilization
- Reduced response time
- Reduced execution time
- Improved throughput
- Avoidance of VM/server overload
- Better resource utilization
- Improved Quality of Service (QoS)

### Simple Example
Suppose a cloud has 3 VMs:

| VM | Processing Capacity |
|---|---|
| VM1 | 100 units |
| VM2 | 80 units |
| VM3 | 120 units |

Four tasks arrive:

| Task | Workload |
|---|---|
| T1 | 40 |
| T2 | 30 |
| T3 | 60 |
| T4 | 20 |

A simple scheduling approach might assign tasks as: T1 → VM1, T2 → VM2, T3 → VM3, T4 → VM2.

The scheduler continuously monitors the **current load** of each VM and assigns new tasks to an appropriate VM rather than sending all tasks to the same resource.

### Load Balancing Concept

**Before load balancing:**
| VM | Load |
|---|---|
| VM1 | 90% |
| VM2 | 30% |
| VM3 | 20% |

VM1 is overloaded while VM2 and VM3 are underutilized.

**After load balancing:**
| VM | Load |
|---|---|
| VM1 | 60% |
| VM2 | 50% |
| VM3 | 55% |

The workload is more evenly distributed.

**❓ Exam Questions:**
- What is load balancing scheduling? List its main objectives.
- Explain, with an example, how load balancing redistributes workload among VMs.

---

## 5. Common Load-Balancing Algorithms

### 1. Round Robin
Tasks are assigned sequentially: T1→VM1, T2→VM2, T3→VM3, T4→VM1, T5→VM2, ...
- **Advantage:** Very simple.
- **Limitation:** Does not consider VM capacity or current workload.

### 2. Weighted Round Robin
VMs receive tasks according to their processing capacity.

Example: VM1 = Weight 5, VM2 = Weight 3, VM3 = Weight 2 → VM1 receives more tasks because it has greater capacity.

### 3. Least-Loaded Scheduling
The scheduler assigns a new task to the VM with the **lowest current load**.

Example:

| VM | Current Load |
|---|---|
| VM1 | 70% |
| VM2 | **30%** |
| VM3 | 50% |

A new task is assigned to **VM2**.

### 4. Min-Min Scheduling
For every task, the scheduler finds the VM that provides the **minimum completion time**, and then selects the task with the smallest of these minimum completion times.
> Min-Min → Schedule the task that can finish earliest.

### 5. Max-Min Scheduling
For every task, the scheduler finds its minimum completion time and then selects the task having the **maximum** of these minimum values.
> Max-Min → Schedule the relatively longer task first.

### 6. Dynamic Load Balancing
Unlike static scheduling, the scheduler continuously monitors:
- CPU utilization
- Memory utilization
- Network traffic
- VM queue length
- Task execution time
- VM availability

...and dynamically moves or assigns workloads according to the current system state.

**❓ Exam Questions:**
- List and explain six common load-balancing scheduling algorithms.
- What is the key limitation of Round Robin scheduling?
- Differentiate Round Robin and Weighted Round Robin.

---

## 6. Static vs. Dynamic Load Balancing

| Feature | Static | Dynamic |
|---|---|---|
| **Load information** | Known in advance | Continuously monitored |
| **Adaptability** | Low | High |
| **Overhead** | Low | Higher |
| **Suitable for** | Predictable workloads | Dynamic cloud workloads |
| **Examples** | Round Robin | Least Loaded, adaptive scheduling |

### Key Idea
A good load-balancing scheduler tries to minimize the difference between the workloads of different VMs:

$$\text{Load Imbalance} = \max(L_i) - \min(L_i)$$

where $L_i$ represents the load of VM $i$.

**In short:** Load balancing scheduling = intelligently distributing cloud tasks among available resources so that workload is balanced, resources are efficiently utilized, and performance is improved.

**❓ Exam Questions:**
- Differentiate static and dynamic load balancing.
- Define the "Load Imbalance" metric used to evaluate a load-balancing scheduler.

---

## 7. Workflow Scheduling in Cloud Computing

A **workflow** is a collection of computational tasks connected by dependencies.

### Example
```
        T1
       /  \
      T2   T3
       \  /
        T4
        |
        T5
```
Here:
- T1 must finish before T2 and T3.
- T2 and T3 must finish before T4.
- T4 must finish before T5.

The workflow can be represented as a **DAG (Directed Acyclic Graph)**:

$$G = (T, E)$$

where:
- $T = \{T_1, T_2, \ldots, T_n\}$ = set of tasks
- $E$ = dependency edges between tasks

The scheduler has to decide: **Which task should execute on which cloud resource, and at what time?**

**❓ Exam Questions:**
- What is a workflow in cloud computing? How is it represented mathematically?
- Explain a DAG and its role in workflow scheduling.

---

## 8. Why Workflow Scheduling Is Difficult

Suppose we have:
- 10 tasks
- 5 virtual machines

Each task can potentially be assigned to one of 5 VMs. The number of possible task-to-VM assignments is:

$$5^{10} = 9{,}765{,}625$$

For larger workflows, the search space becomes extremely large. Therefore, finding the **globally optimal schedule** can be computationally expensive.

This is why we use:

| Approach | Description |
|---|---|
| **Exact Algorithms** | Find the optimal solution but may require very high computational time. |
| **Heuristic Algorithms** | Use problem-specific rules to quickly find a good solution. |
| **Metaheuristic Algorithms** | Use general optimization strategies to explore a very large search space and obtain near-optimal solutions. |

**❓ Exam Questions:**
- Why does workflow scheduling become computationally expensive as the number of tasks/VMs grows? Illustrate with the calculation $5^{10}$.
- Differentiate exact, heuristic, and metaheuristic algorithms for workflow scheduling.

---

## 9. Workflow Scheduling Objectives

A cloud workflow scheduler may optimize one or more objectives:

### A. Makespan
The total time required to complete the workflow.

$$Makespan = \max_i(F_i)$$

where $F_i$ is the finishing time of task $i$. **Goal:** min *Makespan*.

### B. Cost
Cloud resources are generally charged according to resource usage.

$$Cost = \sum_{j=1}^{m} Price_j \times Usage_j$$

**Goal:** min *Cost*.

### C. Resource Utilization
We want to avoid resources remaining idle.

$$Utilization = \frac{\text{Busy Time}}{\text{Available Time}} \times 100$$

**Goal:** max *Utilization*.

### D. Energy Consumption
For energy-aware cloud scheduling: **Goal:** min *Energy*.

### E. Multi-objective Scheduling
Usually, we need to optimize several objectives simultaneously:

$$\min (Makespan,\ Cost,\ Energy)$$

This creates a **multi-objective optimization problem**.

**❓ Exam Questions:**
- Define makespan, cost, and resource utilization with their formulas.
- What is multi-objective scheduling in cloud workflows?

---

## 10. Heuristic Algorithms

A **heuristic** is a problem-solving strategy that uses a specific rule or knowledge about the problem to obtain a good solution quickly. It does **not guarantee the optimal solution**.

```
Problem
  ↓
Apply problem-specific rule
  ↓
Generate schedule
  ↓
Evaluate schedule
  ↓
Good solution
```

**Example rule:** "Always assign the task with the highest priority to the VM that can complete it earliest." — This is a heuristic rule.

**❓ Exam Question:** Define a heuristic algorithm and explain its general workflow with an example rule.

---

## 11. Common Heuristic Workflow Scheduling Algorithms

### 11.1 HEFT (Heterogeneous Earliest Finish Time)
One of the most important heuristics for workflow scheduling. HEFT considers:
- Task computation cost
- Communication cost
- Task dependencies
- Heterogeneous resources

**Two major steps:**

**Step 1: Task Ranking** — Calculate the **upward rank**:

$$rank_u(n_i) = \overline{w_i} + \max_{n_j \in succ(n_i)} \left( \overline{c_{ij}} + rank_u(n_j) \right)$$

where:
- $\overline{w_i}$ = average computation cost
- $\overline{c_{ij}}$ = average communication cost
- $succ(n_i)$ = successors of task $i$

Tasks are then scheduled according to their rank.

**Step 2: Processor Selection** — For each task, select the processor that provides the **Earliest Finish Time (EFT)**.

```
Rank tasks
   ↓
Select highest-priority task
   ↓
Check all VMs
   ↓
Calculate EFT
   ↓
Select VM with minimum EFT
   ↓
Schedule task
```

**Advantages:** Simple · Fast · Effective for DAG workflows · Considers communication cost · Suitable for heterogeneous cloud resources.

**Limitation:** Can become trapped in a locally good scheduling decision.

### 11.2 Min-Min
1. Calculate completion time of every unscheduled task on every VM.
2. Select the task with the **minimum completion time**.
3. Assign it to the corresponding VM.
4. Repeat.

```
Calculate CT
   ↓
Find minimum CT
   ↓
Assign task to VM
   ↓
Remove task
   ↓
Repeat
```

### 11.3 Max-Min
Similar to Min-Min, but selects the task having the **maximum minimum completion time**. Useful when some tasks are significantly larger than others.

### 11.4 Sufferage
For each task:

$$Sufferage_i = C_{i,2nd} - C_{i,best}$$

where:
- $C_{i,best}$ = best completion time
- $C_{i,2nd}$ = second-best completion time

The task with the highest **sufferage value** gets priority.

**Intuition:** Schedule first the task that will "suffer the most" if it does not get its best resource.

**❓ Exam Questions:**
- Explain HEFT's two steps (task ranking and processor selection) with its rank formula.
- What is the "upward rank" in HEFT?
- Define the sufferage value and explain its scheduling intuition.
- What is a key limitation of HEFT?

---

## 12. Limitations of Heuristic Algorithms

Heuristics are generally: **Fast · Simple · Problem-specific**

But:
- They may produce poor solutions for complex instances.
- They generally do not escape local optima.
- They may not work well when the optimization objectives change.
- They provide limited global exploration.

This motivates **metaheuristic algorithms**.

**❓ Exam Question:** List the limitations of heuristic algorithms that motivate the use of metaheuristics.

---

## 13. Metaheuristic Algorithms

A **metaheuristic** is a higher-level optimization strategy designed to search a large solution space efficiently. Unlike a conventional heuristic, it is generally **problem-independent** and can be adapted to many optimization problems.

### Basic Concept
```
        Search Space
       /            \
Exploration      Exploitation
     ↓                 ↓
Search new areas   Improve current area
       \            /
        Good solution
```

**Two key concepts:**
- **Exploration:** Search previously unexplored regions.
- **Exploitation:** Improve the best solutions already found.

A good metaheuristic must balance both.

### 13.1 Genetic Algorithm (GA)
Inspired by **natural evolution**. A scheduling solution is represented as a **chromosome**.

Example:

| Tasks: | T1 | T2 | T3 | T4 | T5 |
|---|---|---|---|---|---|
| VM: | 2 | 1 | 3 | 2 | 1 |

This chromosome represents: $[T1 \rightarrow VM2,\ T2 \rightarrow VM1, \ldots]$

**GA Workflow:**
```
Generate Population → Calculate Fitness → Selection → Crossover
→ Mutation → New Population → Termination? (No → Repeat | Yes → Best Solution)
```

**GA Fitness Function**

For a makespan minimization problem:
$$Fitness = \frac{1}{Makespan}$$

For multiple objectives:
$$Fitness = w_1 \frac{1}{Makespan} + w_2 \frac{1}{Cost} + w_3 \cdot Utilization$$

where $w_1 + w_2 + w_3 = 1$.

### 13.2 Particle Swarm Optimization (PSO)
Inspired by the movement of **birds or fish**. Each particle represents a possible scheduling solution.

Each particle remembers:
- **Personal best:** $pbest$
- **Global best:** $gbest$

**Velocity equation:**
$$v_i(t+1) = w v_i(t) + c_1 r_1 (pbest_i - x_i) + c_2 r_2 (gbest - x_i)$$

**Position equation:**
$$x_i(t+1) = x_i(t) + v_i(t+1)$$

where:
- $w$ = inertia weight
- $c_1$ = cognitive coefficient
- $c_2$ = social coefficient
- $r_1, r_2$ = random values

**Intuition:**
```
Particle → "Where have I found a good solution?" → pbest
        → "Where has the swarm found a good solution?" → gbest
        → Update movement → New scheduling solution
```

Note: For workflow scheduling, a **discrete/binary PSO** or specialized encoding is normally required because task-to-VM assignment is a discrete problem.

### 13.3 Ant Colony Optimization (ACO)
Inspired by **ants searching for food**. Ants leave **pheromones** on good paths.

For workflow scheduling, an ant constructs a schedule (Task → VM1/VM2/VM3, etc.) based on:
- Pheromone information
- Heuristic information

**Probability of selecting resource $j$:**

$$P_{ij} = \frac{\tau_{ij}^\alpha \eta_{ij}^\beta}{\sum_k \tau_{ik}^\alpha \eta_{ik}^\beta}$$

where:
- $\tau_{ij}$ = pheromone
- $\eta_{ij}$ = heuristic information
- $\alpha$ = pheromone importance
- $\beta$ = heuristic importance

After schedules are evaluated, pheromone values are updated.

### 13.4 Simulated Annealing (SA)
Inspired by the **annealing process in metallurgy**. It allows the algorithm to occasionally accept a worse solution — **why?** To escape a **local optimum**.

**Acceptance probability:**
$$P = e^{-\Delta E / T}$$

where:
- $\Delta E$ = increase in objective value
- $T$ = temperature

- Initially: $T \rightarrow$ high → more exploration.
- Later: $T \rightarrow$ low → more exploitation.

**Key idea:** Sometimes accept a worse solution now to obtain a much better solution later.

**❓ Exam Questions:**
- What is a metaheuristic? How does it differ from a heuristic?
- Explain exploration vs. exploitation in metaheuristic search.
- Explain GA's workflow and its fitness function for single/multi-objective scheduling.
- Write and explain PSO's velocity and position update equations.
- Explain ACO's probability equation for resource selection.
- Why does Simulated Annealing sometimes accept a worse solution? Explain using the acceptance probability formula.

---

## 14. Heuristic vs. Metaheuristic

| Feature | Heuristic | Metaheuristic |
|---|---|---|
| **Strategy** | Problem-specific | General optimization strategy |
| **Speed** | Usually very fast | Usually slower |
| **Search** | Limited | Broad search |
| **Local optimum** | May get trapped | Designed to escape |
| **Complexity** | Lower | Higher |
| **Optimality** | No guarantee | No guarantee |
| **Examples** | HEFT, Min-Min, Max-Min | GA, PSO, ACO, SA |
| **Adaptability** | Lower | Higher |

**❓ Exam Question:** Tabulate the differences between heuristic and metaheuristic algorithms across strategy, speed, search, local optima, complexity, and adaptability.

---

## 15. Hybrid Workflow Scheduling

A very important research direction is **hybrid algorithms** — combining a heuristic with a metaheuristic.

**Example: HEFT + GA**
```
Workflow DAG → HEFT → Generate good initial population
→ Genetic Algorithm → Optimization → Final Schedule
```
**Why?** HEFT provides a good initial solution, while GA performs global optimization.

**Other examples:**
- HEFT + PSO
- Min-Min + GA
- ACO + PSO
- GA + Local Search
- PSO + SA
- RL + Metaheuristic

**❓ Exam Question:** Why is HEFT often combined with GA in hybrid workflow scheduling? Name other common hybrid combinations.

---

## 16. Example Classroom Problem

**Tasks:**

| Task | Execution Time |
|---|---|
| T1 | 10 |
| T2 | 20 |
| T3 | 15 |
| T4 | 25 |
| T5 | 10 |

**Dependencies:**
- $T1 \rightarrow T2$
- $T1 \rightarrow T3$
- $T2, T3 \rightarrow T4$
- $T4 \rightarrow T5$

**Cloud resources:**
- VM1: Fast CPU
- VM2: Medium CPU
- VM3: Slow CPU

**Discussion Questions:**
1. What is the DAG?
2. Which tasks can execute simultaneously?
3. How would Min-Min schedule the tasks?
4. How would HEFT schedule them?
5. How could GA improve the HEFT solution?
6. Which algorithm would you choose if the objective is: $\min(Makespan + Cost)$?

### Important Research Problem
> Develop a metaheuristic-based workflow scheduling algorithm for cloud computing that minimizes makespan and execution cost while maintaining high resource utilization.

### Suggested Student Workflow
```
Literature Review → Select Algorithm → Define Workflow → Define Cloud Resources
→ Develop Scheduling Algorithm → Simulation → Compare with HEFT/Min-Min/GA/PSO
→ Performance Analysis
```

### Performance Metrics to Compare
1. Makespan
2. Execution cost
3. Resource utilization
4. Energy consumption
5. Convergence time
6. Scheduling time
7. QoS / deadline violation

**❓ Exam Questions:**
- For the given DAG (T1→T2, T1→T3, T2,T3→T4, T4→T5), draw the graph and identify which tasks can run in parallel.
- Which performance metrics should be used to compare workflow scheduling algorithms?

---

## 17. Key Takeaway

> **Heuristics** use intelligent problem-specific rules to quickly construct a good schedule, whereas **metaheuristics** perform broader intelligent search to improve solutions and escape local optima.

**A typical progression is:**

$$HEFT \rightarrow GA/PSO/ACO \rightarrow \text{Hybrid Metaheuristic} \rightarrow \text{Multi-objective Optimization}$$

This topic is particularly suitable for a **Cloud Computing project**, because students can implement HEFT, Min-Min, GA, and PSO in Python and compare their performance on the same workflow and cloud-resource configuration.

---

## 18. Quick Revision — Important Exam Questions

**Task-Level Scheduling**
1. Explain Max-Min and Min-Min scheduling algorithms with worked examples.
2. Compare Max-Min and Min-Min on selection criterion, objective, suitability, and risk.
3. Compute the makespan for a given task–VM completion-time table using both algorithms.

**Load Balancing**
4. What is load balancing scheduling and what are its objectives?
5. List and explain six common load-balancing algorithms (Round Robin, Weighted Round Robin, Least-Loaded, Min-Min, Max-Min, Dynamic Load Balancing).
6. Differentiate static and dynamic load balancing.
7. Define the Load Imbalance metric.

**Workflow Scheduling**
8. What is a workflow? Represent it as a DAG.
9. Why is workflow scheduling computationally difficult? Illustrate with $5^{10}$.
10. Differentiate exact, heuristic, and metaheuristic algorithms.
11. Define makespan, cost, resource utilization, and energy consumption objectives with formulas.
12. What is multi-objective scheduling?

**Heuristics**
13. Explain HEFT's two steps and its rank formula.
14. Explain Min-Min, Max-Min, and Sufferage as heuristic algorithms.
15. What are the limitations of heuristic algorithms?

**Metaheuristics**
16. What is a metaheuristic? Explain exploration vs. exploitation.
17. Explain GA's chromosome representation, workflow, and fitness function.
18. Write PSO's velocity and position equations and explain each term.
19. Explain ACO's pheromone-based probability equation.
20. Explain Simulated Annealing's acceptance probability and the role of temperature.
21. Tabulate differences between heuristic and metaheuristic algorithms.
22. Why are hybrid algorithms (e.g., HEFT + GA) used in workflow scheduling?

---

*Compiled from class notes on Max-Min/Min-Min Scheduling, Load Balancing Scheduling, and Heuristic/Metaheuristic Workflow Scheduling in Cloud Computing.*