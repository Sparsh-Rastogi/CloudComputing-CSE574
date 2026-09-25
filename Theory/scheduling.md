# Cloud Scheduling Algorithms — Study Notes

> Based on: class notes on Cloud Computing Scheduling Algorithms — covering the basic scheduling model, classical algorithms (FCFS, SJF, Round Robin, Priority), Max-Min/Min-Min, Load Balancing, Workflow Scheduling (DAGs), Heuristic & Metaheuristic algorithms, and AI/RL-based scheduling.

---

## Table of Contents
1. [Introduction to Cloud Scheduling](#1-introduction-to-cloud-scheduling)
2. [Why Scheduling Is Important](#2-why-scheduling-is-important)
3. [Types of Cloud Scheduling](#3-types-of-cloud-scheduling)
4. [Static vs. Dynamic Scheduling](#4-static-vs-dynamic-scheduling)
5. [Important Performance Metrics](#5-important-performance-metrics)
6. [Classical Scheduling Algorithms: FCFS, SJF, Round Robin, Priority](#6-classical-scheduling-algorithms-fcfs-sjf-round-robin-priority)
7. [Min-Min Scheduling](#7-min-min-scheduling)
8. [Max-Min Scheduling](#8-max-min-scheduling)
9. [FCFS vs. Min-Min vs. Max-Min](#9-fcfs-vs-min-min-vs-max-min)
10. [Load Balancing Scheduling](#10-load-balancing-scheduling)
11. [Common Load-Balancing Algorithms](#11-common-load-balancing-algorithms)
12. [Static vs. Dynamic Load Balancing](#12-static-vs-dynamic-load-balancing)
13. [Workflow Scheduling in Cloud Computing](#13-workflow-scheduling-in-cloud-computing)
14. [Why Workflow Scheduling Is Difficult](#14-why-workflow-scheduling-is-difficult)
15. [Workflow Scheduling Objectives](#15-workflow-scheduling-objectives)
16. [Heuristic Algorithms](#16-heuristic-algorithms)
17. [Common Heuristic Workflow Scheduling Algorithms](#17-common-heuristic-workflow-scheduling-algorithms)
18. [Limitations of Heuristic Algorithms](#18-limitations-of-heuristic-algorithms)
19. [Metaheuristic Algorithms](#19-metaheuristic-algorithms)
20. [Heuristic vs. Metaheuristic](#20-heuristic-vs-metaheuristic)
21. [AI-Based and Reinforcement-Learning-Based Scheduling](#21-ai-based-and-reinforcement-learning-based-scheduling)
22. [Multi-Objective Scheduling](#22-multi-objective-scheduling)
23. [Cost-Aware Scheduling](#23-cost-aware-scheduling)
24. [Energy-Aware Scheduling](#24-energy-aware-scheduling)
25. [Deadline-Aware Scheduling](#25-deadline-aware-scheduling)
26. [Hybrid Workflow Scheduling](#26-hybrid-workflow-scheduling)
27. [Comparison of Scheduling Algorithms](#27-comparison-of-scheduling-algorithms)
28. [Example Classroom Problems](#28-example-classroom-problems)
29. [Key Takeaways](#29-key-takeaways)
30. [Quick Revision — Important Exam Questions](#30-quick-revision--important-exam-questions)

---

## 1. Introduction to Cloud Scheduling

In cloud computing, **scheduling** is the process of assigning user tasks, jobs, or virtual machines (VMs) to available cloud resources such as CPUs, VMs, containers, or physical hosts.

The main objective is to use cloud resources efficiently while satisfying user requirements such as:
- Minimum execution time
- Minimum cost
- Maximum resource utilization
- Meeting deadlines
- Energy efficiency
- Load balancing
- Quality of Service (QoS)

### Basic Scheduling Model
```
User → Cloud Broker/Scheduler → Virtual Machines → Physical Hosts
```

**Example:** A user submits 100 tasks → Scheduler analyzes tasks → Tasks are assigned to appropriate VMs → VMs execute tasks.

**❓ Exam Questions:**
- Define scheduling in the context of cloud computing.
- Explain the basic scheduling model with an example.

---

## 2. Why Scheduling Is Important

Cloud environments have:
- Large numbers of users
- Heterogeneous resources
- Dynamic workloads
- Different VM configurations
- Variable resource availability
- Different pricing models

Therefore, simply assigning tasks to the first available VM may result in:
- Poor resource utilization
- Long execution time
- Increased cost
- VM overload
- SLA violations
- Higher energy consumption

**Scheduling algorithms attempt to find a better task-resource mapping.**

**❓ Exam Question:** What problems can arise if a cloud provider does not use a proper scheduling algorithm?

---

## 3. Types of Cloud Scheduling

Scheduling can be classified according to different criteria:

**Based on scheduling level**
1. Task Scheduling
2. VM Scheduling
3. Resource Scheduling
4. Workflow Scheduling

**Based on decision-making**
1. Static Scheduling
2. Dynamic Scheduling

**Based on optimization technique**
1. Traditional algorithms
2. Heuristic algorithms
3. Metaheuristic algorithms
4. AI/ML-based algorithms
5. Reinforcement Learning-based algorithms

**❓ Exam Question:** Classify cloud scheduling based on scheduling level, decision-making, and optimization technique.

---

## 4. Static vs. Dynamic Scheduling

### Static Scheduling
In static scheduling, information about tasks and resources is known before execution.

**Example:** Suppose we have 10 tasks, 3 VMs, and known execution time of every task. The scheduler creates a schedule *before* execution starts.

| | |
|---|---|
| **Advantages** | Simple · Predictable · Low scheduling overhead |
| **Disadvantages** | Not suitable for highly dynamic cloud environments · Cannot easily handle VM failures · Cannot react to changing workloads |

### Dynamic Scheduling
In dynamic scheduling, scheduling decisions are made *during* execution.

**Example:** VM1 becomes overloaded → Scheduler detects overload → Some tasks are moved to VM2.

| | |
|---|---|
| **Advantages** | Adaptable · Suitable for cloud environments · Handles changing workloads · Can respond to failures |
| **Disadvantages** | Higher scheduling overhead · More complex |

**❓ Exam Questions:**
- Differentiate static and dynamic scheduling with examples.
- Why is dynamic scheduling generally preferred in real cloud environments despite its higher overhead?

---

## 5. Important Performance Metrics

When evaluating a scheduling algorithm, several metrics are used:

| Metric | Description | Goal |
|---|---|---|
| **1. Makespan** | The total time required to complete all tasks: $Makespan = \max_i(F_i)$, where $F_i$ is the completion time of task $i$. | Lower makespan is better |
| **2. Execution Time** | Time required by a task to complete. | — |
| **3. Resource Utilization** | Measures how effectively resources are being used. | Higher utilization is generally desirable |
| **4. Cost** | Cloud providers charge users based on resource consumption: $Cost = \sum Price \times Usage$. | A good scheduler minimizes cost while satisfying QoS requirements |
| **5. Deadline Violation** | A task violates its deadline if its completion time exceeds the deadline. | Minimize the number of deadline violations |
| **6. Energy Consumption** | Energy-aware scheduling attempts to minimize energy use — particularly important in large cloud data centers. | Minimize energy |

**❓ Exam Questions:**
- List and define the important performance metrics used to evaluate cloud scheduling algorithms.
- Why is minimizing cost alone not sufficient — what constraint must also be satisfied?

---

## 6. Classical Scheduling Algorithms: FCFS, SJF, Round Robin, Priority

### 6.1 First-Come, First-Served (FCFS)
FCFS schedules tasks according to their arrival order.

**Example:**

| Task | Execution Time |
|---|---|
| T1 | 5 |
| T2 | 3 |
| T3 | 2 |
| T4 | 4 |

Arrival order: T1 → T2 → T3 → T4. The scheduler executes tasks in exactly this order.

| | |
|---|---|
| **Advantages** | Very simple · Easy to implement · Low scheduling overhead |
| **Disadvantages** | May produce high waiting time · Does not consider task priority · May lead to poor resource utilization |

### 6.2 Shortest Job First (SJF)
The task with the shortest execution time is selected first.

For the same example, execution order becomes: **T3 → T2 → T4 → T1** (2 → 3 → 4 → 5).

| | |
|---|---|
| **Advantage** | Generally reduces average waiting time |
| **Disadvantage** | Long tasks may suffer from **starvation** |

### 6.3 Round Robin Scheduling
Round Robin assigns each task a fixed **time quantum**.

**Example:** Time quantum = 2 seconds; Tasks = T1, T2, T3.
Execution: T1 → T2 → T3 → T1 → T2 → T3 → ... until all tasks finish.

| | |
|---|---|
| **Advantages** | Fair allocation · Prevents starvation · Suitable for time-sharing environments |
| **Disadvantages** | Performance depends on time quantum · Too small → high context-switching overhead · Too large → behaves similarly to FCFS |

### 6.4 Priority Scheduling
Each task receives a priority value.

**Example** (smaller number = higher priority):

| Task | Priority |
|---|---|
| T1 | 2 |
| T2 | 1 |
| T3 | 3 |

Execution order: **T2 → T1 → T3**

Priority can be based on: user importance, deadline, cost, SLA, task type, business importance.

**❓ Exam Questions:**
- Explain FCFS, SJF, Round Robin, and Priority scheduling with examples.
- Why can SJF cause starvation of long tasks?
- What happens to Round Robin's behavior if the time quantum is too large or too small?
- List the criteria on which task priority can be based.

---

## 7. Min-Min Scheduling

**Min-Min algorithm** — a popular heuristic for cloud task scheduling.

**Basic idea:** For every unscheduled task:
1. Calculate its completion time on every available VM.
2. Find the minimum completion time for each task.
3. Select the task having the **overall minimum completion time**.
4. Assign it to the corresponding VM.
5. Repeat.

### Example A — 3 Tasks, 3 VMs

| Task | VM1 | VM2 | VM3 |
|---|---|---|---|
| T1 | 8 | 5 | 7 |
| T2 | 6 | 9 | 4 |
| T3 | 10 | 3 | 8 |

Minimum for each task: T1 → 5 on VM2, T2 → 4 on VM3, T3 → 3 on VM2.
**Overall minimum = 3** → **T3 is scheduled on VM2**. The process is then repeated for the remaining tasks.

| | |
|---|---|
| **Advantages** | Simple · Often provides good makespan · Effective for independent tasks |
| **Disadvantage** | May favor short tasks and delay long tasks |

### Example B — 3 Tasks, 2 VMs (Detailed Walkthrough)

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

**Step 2: Select the minimum among them** → minimum of 4, 6, 7 = **4** → **T1 scheduled on VM2**. VM2's load becomes 4.

**Step 3: Recalculate for remaining tasks (T2, T3)** — VM2's previous load of 4 is added:

| Task | VM1 | VM2* |
|---|---|---|
| T2 | 6 | 4 + 10 = 14 |
| T3 | 12 | 4 + 7 = 11 |

- T2 → min(6, 14) = **6** → VM1
- T3 → min(12, 11) = **11** → VM2

Minimum is **6** → **T2 scheduled on VM1**. VM1's load becomes 6.

**Step 4: Schedule the remaining task (T3)** → T3 is scheduled on VM2 (completion time 11).

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

## 8. Max-Min Scheduling

Max-Min is similar to Min-Min. **The difference:** after calculating the minimum completion time for every task, the scheduler selects the task having the **maximum** of these minimum completion times.

**Why?** It attempts to give longer tasks an opportunity to execute earlier — this prevents them from becoming a bottleneck later.

### Comparison of Selection Rule

| Algorithm | Selection |
|---|---|
| Min-Min | Smallest minimum completion time |
| Max-Min | Largest minimum completion time |

### Worked Example (same data as Min-Min Example B)

| Task | VM1 | VM2 | Minimum | Selected VM |
|---|---|---|---|---|
| T1 | 8 | 4 | 4 | VM2 |
| T2 | 6 | 10 | 6 | VM1 |
| T3 | 12 | 7 | 7 | VM2 |

**Step 1:** max(4, 6, 7) = **7** → **T3 scheduled first on VM2**. VM2's load becomes 7.

**Step 2:** Recalculate for T1 and T2 (VM2 already occupied for 7 units):

| Task | VM1 | VM2 | Minimum | Selected VM |
|---|---|---|---|---|
| T1 | 8 | 7+4=11 | 8 | VM1 |
| T2 | 6 | 7+10=17 | 6 | VM1 |

max(8, 6) = **8** → **T1 scheduled on VM1**. VM1's load becomes 8.

**Step 3:** Only T2 remains → **T2 scheduled on VM1** (completion time 14).

### Final Schedule

| Order | Task | VM | Completion Time |
|---|---|---|---|
| 1 | T3 | VM2 | 7 |
| 2 | T1 | VM1 | 8 |
| 3 | T2 | VM1 | 14 |

- **VM1:** T1 → T2 → finishes at **14**
- **VM2:** T3 → finishes at **7**

**Makespan = max(14, 7) = 14**

**❓ Exam Questions:**
- Explain the Max-Min scheduling algorithm with its steps. Why is it called "Max-Min"?
- Using the same task–VM table, compute schedules with both Min-Min and Max-Min and compare the resulting makespans.

---

## 9. FCFS vs. Min-Min vs. Max-Min

| Feature | FCFS | Min-Min | Max-Min |
|---|---|---|---|
| **Complexity** | Low | Medium | Medium |
| **Task execution time considered** | No | Yes | Yes |
| **Resource capability considered** | Limited | Yes | Yes |
| **Makespan** | Usually high | Often lower | Often lower |
| **Starvation possibility** | Low | Possible (for long tasks) | Possible (for short tasks) |
| **Suitable for complex cloud workloads** | Limited | Better | Better |

**❓ Exam Question:** Compare FCFS, Min-Min, and Max-Min across complexity, makespan, and starvation risk.

---

## 10. Load Balancing Scheduling

**Load balancing scheduling** is a technique in cloud computing that distributes tasks or workloads among available Virtual Machines (VMs), servers, or cloud resources so that no single resource becomes heavily overloaded while others remain underutilized.

**Example:** VM1 = 90% utilization, VM2 = 20%, VM3 = 30%. A load-balancing scheduler may move some tasks from VM1 to VM2/VM3.

### Objective
Minimize the difference between the loads of different resources — i.e., minimize $\max(L_i) - \min(L_i)$, where $L_i$ represents the load of resource $i$.

### Benefits
- Better resource utilization
- Reduced response time
- Avoids VM overload
- Improves system performance
- Reduced execution time
- Improved throughput
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

A simple scheduling approach might assign: T1→VM1, T2→VM2, T3→VM3, T4→VM2. The scheduler continuously monitors the **current load** of each VM and assigns new tasks to an appropriate VM rather than sending all tasks to the same resource.

**Before load balancing:** VM1: 90%, VM2: 30%, VM3: 20% — VM1 is overloaded while VM2 and VM3 are underutilized.
**After load balancing:** VM1: 60%, VM2: 50%, VM3: 55% — the workload is more evenly distributed.

**❓ Exam Questions:**
- What is load balancing scheduling? List its main objectives and benefits.
- Explain, with an example, how load balancing redistributes workload among VMs.
- Define the Load Imbalance metric used to evaluate a load-balancing scheduler.

---

## 11. Common Load-Balancing Algorithms

1. **Round Robin** — Tasks assigned sequentially (T1→VM1, T2→VM2, T3→VM3, T4→VM1, ...). *Advantage:* very simple. *Limitation:* does not consider VM capacity or current workload.

2. **Weighted Round Robin** — VMs receive tasks according to their processing capacity. Example: VM1 = Weight 5, VM2 = Weight 3, VM3 = Weight 2 → VM1 receives more tasks because it has greater capacity.

3. **Least-Loaded Scheduling** — The scheduler assigns a new task to the VM with the lowest current load. Example: VM1=70%, VM2=**30%**, VM3=50% → new task assigned to VM2.

4. **Min-Min Scheduling** — Schedule the task that can finish earliest.

5. **Max-Min Scheduling** — Schedule the relatively longer task first.

6. **Dynamic Load Balancing** — The scheduler continuously monitors CPU utilization, memory utilization, network traffic, VM queue length, task execution time, and VM availability, then dynamically moves or assigns workloads according to the current system state.

**❓ Exam Questions:**
- List and explain six common load-balancing scheduling algorithms.
- What is the key limitation of Round Robin scheduling?
- Differentiate Round Robin and Weighted Round Robin.

---

## 12. Static vs. Dynamic Load Balancing

| Feature | Static | Dynamic |
|---|---|---|
| **Load information** | Known in advance | Continuously monitored |
| **Adaptability** | Low | High |
| **Overhead** | Low | Higher |
| **Suitable for** | Predictable workloads | Dynamic cloud workloads |
| **Examples** | Round Robin | Least Loaded, adaptive scheduling |

**In short:** Load balancing scheduling = intelligently distributing cloud tasks among available resources so that workload is balanced, resources are efficiently utilized, and performance is improved.

**❓ Exam Question:** Differentiate static and dynamic load balancing.

---

## 13. Workflow Scheduling in Cloud Computing

Many cloud applications consist of **dependent tasks** rather than independent tasks.

**Example pipeline:** Data Collection → Preprocessing → ML Training → Prediction → Report.

This can be represented as a **Directed Acyclic Graph (DAG)**: $G = (T, E)$, where $T = \{T_1, \ldots, T_n\}$ is the set of tasks and $E$ is the set of dependency edges. Each node represents a task and each edge represents a dependency (e.g., an edge T1→T2 means T2 cannot start until T1 finishes).

The scheduler has to decide: **Which task should execute on which cloud resource, and at what time?**

### Example: Real-World Workflow DAG (Airflow-style pipeline)
A typical automated data pipeline DAG:
```
Validate file exists (Cloud Storage) → Start Dataflow pipeline (Cloud Dataflow)
→ Execute BigQuery SQL job to validate processed data (BigQuery)
→ Delete Cloud Storage bucket (Cloud Storage)
   ↳ On task failure at any step → Send pipeline-failure Slack notification
```
This illustrates how a real cloud workflow chains together managed services (Cloud Storage, Dataflow, BigQuery) with dependency and failure-handling edges — exactly the kind of DAG a workflow scheduler must map onto resources.

### Workflow Scheduling System Architecture
A typical workflow scheduling pipeline used in cloud systems:
```
Input Events → Input Queue Manager → Input Queue → Workflow Manager → Workflow Task Queue
→ Task Scheduler (+ Load Balancer) → Node Executor → Compute Nodes
```
Supporting **Metadata Services** track: Workflow Metadata (via Workflow Metadata Service), Task Allocation (via Task Allocation Service + task-allocation store), and Task Assignment (via Task Assignment Service, which also retrieves "all tasks for a given node").

### Cloud Workflow Management System — Reference Architecture
A more complete reference architecture for cloud workflow management includes:
- **User-facing layer:** Workflow Management Interface, Workflow Modeling and Definition Tools, Cloud Resource Interface and Monitoring (all accessed by Users).
- **Workflow Engine** (the core): Workflow Parser, a Scheduler (containing a Service Analyser, an Energy-Aware/other-objectives Designer, and a Service Scheduler), Resource Provisioning, Data Management, and a Task Dispatcher.
- **Administration and Monitoring Tools:** Workflow Monitor, Resource Monitor, VM Management — backed by a Historical Data store.
- **Cloud Information Services:** VM Types, Storage Types, Cloud Providers — backed by a Cloud Resource Registry.
- All of the above connect through **Cloud Service Provisioning APIs** down to the **Cloud Datacenter**, which is organized as Virtual Machines (via a Virtualization layer) running on top of physical Servers.

**❓ Exam Questions:**
- What is a workflow in cloud computing? How is it represented mathematically as a DAG?
- Describe a real-world example of a DAG-based cloud workflow (e.g., a data pipeline) and explain its failure-handling edge.
- Explain the components of a cloud workflow management system's reference architecture.

---

## 14. Why Workflow Scheduling Is Difficult

Suppose we have 10 tasks and 5 virtual machines. Each task can potentially be assigned to one of 5 VMs, so the number of possible task-to-VM assignments is:

$$5^{10} = 9{,}765{,}625$$

For larger workflows, the search space becomes extremely large, so finding the **globally optimal schedule** can be computationally expensive. In fact, cloud scheduling is often an **NP-hard optimization problem** — this is exactly why metaheuristic and AI-based algorithms (Sections 19 & 21) are frequently used.

This is why we use:

| Approach | Description |
|---|---|
| **Exact Algorithms** | Find the optimal solution but may require very high computational time. |
| **Heuristic Algorithms** | Use problem-specific rules to quickly find a good solution. |
| **Metaheuristic Algorithms** | Use general optimization strategies to explore a very large search space and obtain near-optimal solutions. |

**❓ Exam Questions:**
- Why does workflow scheduling become computationally expensive as the number of tasks/VMs grows? Illustrate with $5^{10}$.
- Why is cloud scheduling often classified as an NP-hard problem?

---

## 15. Workflow Scheduling Objectives

### A. Makespan

$$Makespan = \max_i (F_i)$$

**Goal:** minimize Makespan.

### B. Cost

$$Cost = \sum_{j=1}^{m} Price_j \times Usage_j$$

**Goal:** minimize Cost.

### C. Resource Utilization

$$Utilization = \frac{\text{Busy Time}}{\text{Available Time}} \times 100$$

**Goal:** maximize Utilization.

### D. Energy Consumption
For energy-aware cloud scheduling, the **goal** is to minimize Energy.

### E. Multi-objective Scheduling

$$\min (Makespan,\ Cost,\ Energy)$$

This creates a **multi-objective optimization problem** (expanded in Section 22).

**❓ Exam Question:** Define makespan, cost, and resource utilization with their formulas.

---

## 16. Heuristic Algorithms

A **heuristic** is a problem-solving strategy that uses a specific rule or knowledge about the problem to obtain a good solution quickly. It does **not guarantee the optimal solution**.

```
Problem → Apply problem-specific rule → Generate schedule → Evaluate schedule → Good solution
```

**Example rule:** "Always assign the task with the highest priority to the VM that can complete it earliest."

**❓ Exam Question:** Define a heuristic algorithm and explain its general workflow with an example rule.

---

## 17. Common Heuristic Workflow Scheduling Algorithms

### 17.1 HEFT (Heterogeneous Earliest Finish Time)
HEFT is widely used for scheduling workflow applications on heterogeneous resources. It considers:
- Task dependencies · Communication cost · Execution time · Different processor capabilities

**Two major steps:**

**Step 1: Task Prioritization** — Calculate the **upward rank**:
$$rank_u(n_i) = \overline{w_i} + \max_{n_j \in succ(n_i)} \left( \overline{c_{ij}} + rank_u(n_j) \right)$$
where $\overline{w_i}$ = average computation cost, $\overline{c_{ij}}$ = average communication cost, $succ(n_i)$ = successors of task $i$. Tasks are then scheduled according to their rank.

**Step 2: Processor Selection** — For each task, select the processor that provides the **Earliest Finish Time (EFT)**.
```
Rank tasks → Select highest-priority task → Check all VMs → Calculate EFT
→ Select VM with minimum EFT → Schedule task
```
**Objective:** Minimize workflow makespan.

**Advantages:** Simple · Fast · Effective for DAG workflows · Considers communication cost · Suitable for heterogeneous cloud resources.
**Limitation:** Can become trapped in a locally good scheduling decision.

### 17.2 Min-Min
1. Calculate completion time of every unscheduled task on every VM. 2. Select the task with the minimum completion time. 3. Assign it to the corresponding VM. 4. Repeat.

### 17.3 Max-Min
Similar to Min-Min, but selects the task having the **maximum** minimum completion time. Useful when some tasks are significantly larger than others.

### 17.4 Sufferage
$$Sufferage_i = C_{i,2nd} - C_{i,best}$$
The task with the highest sufferage value gets priority. **Intuition:** Schedule first the task that will "suffer the most" if it does not get its best resource.

**❓ Exam Questions:**
- Explain HEFT's two steps (task ranking and processor selection) with its rank formula.
- Define the sufferage value and explain its scheduling intuition.

---

## 18. Limitations of Heuristic Algorithms

Heuristics are generally **fast, simple, and problem-specific**, but:
- They may produce poor solutions for complex instances.
- They generally do not escape local optima.
- They may not work well when the optimization objectives change.
- They provide limited global exploration.

This motivates **metaheuristic algorithms**.

**❓ Exam Question:** List the limitations of heuristic algorithms that motivate the use of metaheuristics.

---

## 19. Metaheuristic Algorithms

Cloud scheduling is often an **NP-hard optimization problem**; therefore, metaheuristic algorithms are frequently used. A **metaheuristic** is a higher-level, generally **problem-independent** optimization strategy designed to search a large solution space efficiently.

**Basic concept — balancing exploration and exploitation:**
```
        Search Space
       /            \
Exploration      Exploitation
     ↓                 ↓
Search new areas   Improve current area
       \            /
        Good solution
```

**Common metaheuristics used in cloud scheduling:**
- **Genetic Algorithm (GA)**
- **Particle Swarm Optimization (PSO)**
- **Ant Colony Optimization (ACO)**
- **Artificial Bee Colony (ABC)**
- **Grey Wolf Optimization (GWO)**
- **Whale Optimization Algorithm (WOA)**
- **Simulated Annealing (SA)**

### 19.1 Genetic Algorithm (GA)
Inspired by **biological evolution**. A scheduling solution is represented as a **chromosome**, e.g.:

| Tasks: | T1 | T2 | T3 | T4 | T5 |
|---|---|---|---|---|---|
| VM: | 2 | 1 | 3 | 2 | 1 |

This represents $[T1 \rightarrow VM2,\ T2 \rightarrow VM1, \ldots]$.

**GA workflow:**
```
Initial Population → Fitness Evaluation → Selection → Crossover → Mutation
→ New Population → Termination? (No → Repeat | Yes → best-fitness solution selected)
```

**Fitness function** — for makespan minimization: $Fitness = \frac{1}{Makespan}$. For multiple objectives: $Fitness = w_1 \frac{1}{Makespan} + w_2 \frac{1}{Cost} + w_3 \cdot Utilization$, where $w_1+w_2+w_3=1$ and the weights determine the importance of each objective (application-dependent).

### 19.2 Particle Swarm Optimization (PSO)
Inspired by the movement of **birds or fish**. Each particle represents a possible scheduling solution and remembers its **personal best ($pbest$)** and the **global best ($gbest$)** found by the swarm. Particles change position based on a velocity equation combining inertia, cognitive (pbest-based), and social (gbest-based) components. PSO is popular because of its relatively simple implementation. For workflow scheduling, a discrete/binary PSO or specialized encoding is normally required, since task-to-VM assignment is a discrete problem.

### 19.3 Ant Colony Optimization (ACO)
Inspired by **ants searching for food**, which leave **pheromones** on good paths. An ant constructs a schedule (Task→VM) based on pheromone information ($\tau_{ij}$) and heuristic information ($\eta_{ij}$), with importance weights $\alpha$ and $\beta$ respectively. After schedules are evaluated, pheromone values are updated.

### 19.4 Simulated Annealing (SA)
Inspired by the **annealing process in metallurgy**. It allows the algorithm to occasionally accept a worse solution (to escape a local optimum), with acceptance probability $P = e^{-\Delta E/T}$. High temperature $T$ → more exploration; low $T$ → more exploitation.

**❓ Exam Questions:**
- What is a metaheuristic? How does it differ from a heuristic?
- Name the common metaheuristic algorithms used in cloud scheduling.
- Explain GA's chromosome representation, workflow, and fitness function for single/multi-objective scheduling.
- Explain PSO's pbest/gbest concept and why discrete PSO is needed for task scheduling.
- Explain ACO's pheromone-based scheduling approach.
- Why does Simulated Annealing sometimes accept a worse solution?

---

## 20. Heuristic vs. Metaheuristic

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

**❓ Exam Question:** Tabulate the differences between heuristic and metaheuristic algorithms.

---

## 21. AI-Based and Reinforcement-Learning-Based Scheduling

### AI-Based Scheduling
Modern cloud scheduling increasingly uses: **Machine Learning · Deep Learning · Reinforcement Learning · Deep Reinforcement Learning (DRL)**. Instead of using only predefined rules, an AI-based scheduler can **learn scheduling policies** from system states and historical observations.

### Reinforcement Learning-Based Scheduling
In Reinforcement Learning (RL), the cloud scheduling problem maps as:

| RL Concept | Cloud Scheduling Equivalent |
|---|---|
| **Agent** | Cloud scheduler |
| **Environment** | Cloud infrastructure |
| **State** | Current resource/workload information |
| **Action** | Assign task to a VM/resource |
| **Reward** | Performance achieved |

#### RL-Based Scheduling Architecture
```
Cloud Environment → State Observer → State Features (Queue Length, Resource Utilization, Task Properties)
→ State Space → RL Agent (Q-Network + Experience Buffer, Policy Network) → Action Space
→ Actions (Task Assignment, Resource Scaling) → Resource Allocator → Reward Calculator → back to Cloud Environment
```

#### Example: DQN (Deep Q-Network) Scheduler
```
Users → Task Queue → DQN Scheduler → Resource Pool (Edge Nodes, Cloud Types)
→ Output
         ↑                                    │
         └── Reward Feedback ── Performance Evaluator (Energy/Cost Monitor) ←──┘
```
The scheduler also follows a general decision loop combining **exploration** (search new areas via an exploration algorithm) and **exploitation** (improve the current strategy) inside a **Decision Maker**, using state updates from the environment and long-term/real-time feedback via a replay storage buffer.

#### Reward Function
A possible (simplified) reward function for cloud RL scheduling is a **negative weighted sum** of the quantities to be minimized:
$$Reward = -\big(w_1 \cdot \text{ExecutionTime} + w_2 \cdot \text{Cost} + w_3 \cdot \text{Energy} + w_4 \cdot \text{DeadlineViolation}\big)$$
The **negative sign** encourages the agent to minimize these quantities (since RL agents maximize cumulative reward).

**❓ Exam Questions:**
- Map the five core RL concepts (Agent, Environment, State, Action, Reward) onto cloud scheduling.
- Explain the architecture of an RL-based cloud scheduler (state observer, RL agent, action space, reward calculator).
- Why does the reward function use a negative sign for execution time, cost, energy, and deadline violation?
- What is DRL (Deep Reinforcement Learning) and how does it relate to RL-based scheduling?

---

## 22. Multi-Objective Scheduling

Real cloud scheduling problems generally have **multiple objectives** simultaneously (e.g., minimizing makespan **while** minimizing cost **and** minimizing energy). This is called **multi-objective scheduling**.

There may **not be one solution that is best for all objectives** — instead, we typically obtain a set of **Pareto-optimal solutions**: a set of solutions where improving one objective would require worsening another, and no solution in the set strictly dominates another.

**❓ Exam Questions:**
- What is multi-objective scheduling? Why can't a single "best" solution always be found?
- What is a Pareto-optimal solution?

---

## 23. Cost-Aware Scheduling

Cloud providers may charge differently for different resources.

**Example:**

| VM | CPU | Cost/hour |
|---|---|---|
| VM1 | 2 cores | ₹X |
| VM2 | 4 cores | ₹Y |
| VM3 | 8 cores | ₹Z |

The scheduler must determine whether **faster execution on an expensive VM is worth the additional cost** — i.e., it optimizes a trade-off between execution speed and price rather than picking the cheapest or fastest VM blindly.

**❓ Exam Question:** What trade-off must a cost-aware scheduler evaluate? Illustrate with a VM pricing example.

---

## 24. Energy-Aware Scheduling

Cloud data centers consume enormous amounts of energy. Scheduling can reduce energy consumption by:
- **Consolidating workloads** (packing tasks onto fewer active servers)
- **Switching idle servers to sleep mode**
- **DVFS — Dynamic Voltage and Frequency Scaling**
- **Avoiding unnecessary VM activation**

A simple optimization objective is to minimize energy consumption **subject to QoS constraints** (i.e., energy savings should not come at the cost of violating service-quality requirements).

**❓ Exam Questions:**
- List four techniques used to reduce energy consumption in cloud data centers.
- What is DVFS?
- Why must energy minimization be constrained by QoS requirements?

---

## 25. Deadline-Aware Scheduling

A deadline-aware scheduler gives greater priority to tasks whose deadlines are approaching.

**Example:**

| Task | Execution Time | Deadline |
|---|---|---|
| T1 | 5 s | 8 s |
| T2 | 3 s | 10 s |
| T3 | 6 s | 7 s |

A useful concept is **slack time** (deadline − execution time, roughly how much delay a task can tolerate): **smaller slack generally means higher urgency**. In the example, T3 (slack = 7−6 = 1s) is more urgent than T1 (slack = 8−5 = 3s) or T2 (slack = 10−3 = 7s).

### Example: Multi-Objective Cloud Scheduling (Putting It Together)
Suppose there are 5 VMs and 20 tasks with different execution times, different deadlines, and different VM costs. The scheduler tries to optimize makespan, cost, energy, and deadline satisfaction *simultaneously* — the weights used in the objective function reflect the application's requirements (e.g., a latency-sensitive application weighs makespan/deadlines more heavily; a budget-constrained batch job weighs cost more heavily).

**❓ Exam Questions:**
- What is slack time, and how does it relate to task urgency?
- Given a table of tasks with execution times and deadlines, identify which task is most urgent.
- In a multi-objective scheduling scenario with 5 VMs and 20 tasks, what factors determine the weight given to each objective?

---

## 26. Hybrid Workflow Scheduling

A very important research direction is **hybrid algorithms** — combining a heuristic with a metaheuristic.

**Example: HEFT + GA**
```
Workflow DAG → HEFT → Generate good initial population
→ Genetic Algorithm → Optimization → Final Schedule
```
**Why?** HEFT provides a good initial solution, while GA performs global optimization.

**Other examples:** HEFT + PSO · Min-Min + GA · ACO + PSO · GA + Local Search · PSO + SA · RL + Metaheuristic.

**❓ Exam Question:** Why is HEFT often combined with GA in hybrid workflow scheduling?

---

## 27. Comparison of Scheduling Algorithms

| Algorithm | Main Objective | Complexity | Typical Application |
|---|---|---|---|
| **FCFS** | Fair/simple ordering | Low | Basic workloads |
| **SJF** | Reduce waiting time | Low | Short independent tasks |
| **Round Robin** | Fairness | Low | Time sharing |
| **Priority** | Task importance | Low | SLA/priority workloads |
| **Min-Min** | Completion time | Medium | Independent tasks |
| **Max-Min** | Balance short/long tasks | Medium | Independent tasks |
| **HEFT** | Workflow makespan | Medium | DAG workflows |
| **GA** | Optimization | High | Complex scheduling |
| **PSO** | Optimization | High | Resource/task mapping |
| **RL** | Adaptive decision-making | High | Dynamic cloud |
| **DRL** | Complex adaptive scheduling | Very high | Large-scale dynamic systems |

**❓ Exam Question:** Compare all major scheduling algorithms in terms of main objective, complexity, and typical application (use the table above as a reference answer).

---

## 28. Example Classroom Problems

### Problem 1: Task–VM Assignment (3 VMs, 4 Tasks)

There are three VMs (VM1, VM2, VM3) and four tasks (T1–T4). Suppose execution times are:

| Task | VM1 | VM2 | VM3 |
|---|---|---|---|
| T1 | 8 | 6 | 10 |
| T2 | 5 | 4 | 7 |
| T3 | 9 | 3 | 6 |
| T4 | 4 | 8 | 5 |

**Ask students:**
1. Which VM should execute T1?
2. Which VM should execute T2?
3. Which VM should execute T3?
4. Which VM should execute T4?
5. What is the expected makespan?
6. How would Min-Min scheduling differ from FCFS?
7. How would the answer change if VM costs were different?

*This example can be used to introduce students to task-resource mapping.*

### Problem 2: Workflow DAG Scheduling (5 Tasks, 3 VMs)

**Tasks:**

| Task | Execution Time |
|---|---|
| T1 | 10 |
| T2 | 20 |
| T3 | 15 |
| T4 | 25 |
| T5 | 10 |

**Dependencies:** $T1 \rightarrow T2$, $T1 \rightarrow T3$, $T2, T3 \rightarrow T4$, $T4 \rightarrow T5$

**Cloud resources:** VM1: Fast CPU, VM2: Medium CPU, VM3: Slow CPU

**Discussion Questions:**
1. What is the DAG?
2. Which tasks can execute simultaneously?
3. How would Min-Min schedule the tasks?
4. How would HEFT schedule them?
5. How could GA improve the HEFT solution?
6. Which algorithm would you choose if the objective is $\min(Makespan + Cost)$?

**❓ Exam Questions:**
- For each classroom problem, apply Min-Min and Max-Min manually and compare the resulting makespans.
- For the DAG (T1→T2, T1→T3, T2,T3→T4, T4→T5), identify which tasks can run in parallel.

---

## 29. Key Takeaways

Students should remember these points:
1. **Scheduling = assigning tasks to cloud resources.**
2. The primary objective is often **minimizing makespan**.
3. Cloud scheduling may involve multiple objectives.
4. **FCFS** is simple but not necessarily efficient.
5. **Min-Min** favors tasks with small completion times.
6. **Max-Min** gives more opportunity to longer tasks.
7. **HEFT** is useful for workflow/DAG scheduling.
8. **GA/PSO/ACO** are metaheuristic approaches.
9. **RL/DRL** can learn scheduling policies dynamically.
10. Modern cloud scheduling often considers **cost + energy + deadline + performance** simultaneously.

### Short Question for Students
**Q: Why is cloud scheduling considered an optimization problem?**
**A:** Because the scheduler must find an effective mapping of tasks to resources while optimizing one or more objectives such as makespan, cost, energy consumption, resource utilization, and deadline satisfaction — under resource and QoS constraints.

### Overall Progression
$$HEFT \rightarrow GA/PSO/ACO \rightarrow \text{Hybrid Metaheuristic} \rightarrow \text{Multi-objective Optimization} \rightarrow \text{RL/DRL}$$

This topic is particularly suitable for a **Cloud Computing project**: students can implement FCFS, Min-Min, Max-Min, HEFT, GA, and PSO in Python and compare their performance on the same workflow and cloud-resource configuration.

---

## 30. Quick Revision — Important Exam Questions

**Foundations**
1. Define cloud scheduling and explain the basic scheduling model.
2. Why is scheduling important? What problems arise without it?
3. Classify cloud scheduling by level, decision-making, and optimization technique.
4. Differentiate static and dynamic scheduling.
5. List and define the important performance metrics (makespan, execution time, resource utilization, cost, deadline violation, energy consumption).

**Classical Algorithms**
6. Explain FCFS, SJF, Round Robin, and Priority scheduling with examples.
7. Why can SJF and Round Robin (with poor quantum choice) cause problems?

**Task-Level Heuristics**
8. Explain Min-Min and Max-Min scheduling algorithms with worked examples and compute makespan.
9. Compare FCFS, Min-Min, and Max-Min on complexity, makespan, and starvation risk.

**Load Balancing**
10. What is load balancing scheduling and what are its objectives?
11. List and explain six common load-balancing algorithms.
12. Differentiate static and dynamic load balancing.

**Workflow Scheduling**
13. What is a workflow? Represent it as a DAG and give a real-world pipeline example.
14. Describe the architecture of a cloud workflow management system.
15. Why is workflow scheduling computationally difficult ($5^{10}$ example)? Why is it NP-hard?
16. Define makespan, cost, resource utilization, and energy objectives with formulas.

**Heuristics & Metaheuristics**
17. Explain HEFT's two steps and rank formula. Explain Sufferage.
18. What are the limitations of heuristic algorithms?
19. List the common metaheuristics used in cloud scheduling (GA, PSO, ACO, ABC, GWO, WOA, SA).
20. Explain GA's chromosome representation, workflow, and fitness function.
21. Tabulate differences between heuristic and metaheuristic algorithms.
22. Why are hybrid algorithms (e.g., HEFT + GA) used?

**AI/RL-Based Scheduling**
23. Map the RL concepts (Agent, Environment, State, Action, Reward) to cloud scheduling.
24. Explain the architecture of an RL/DQN-based cloud scheduler.
25. Why does the RL reward function use a negative weighted sum?

**Advanced Objectives**
26. What is multi-objective scheduling? What is a Pareto-optimal solution?
27. Explain cost-aware scheduling with a VM pricing example.
28. List techniques for energy-aware scheduling (consolidation, sleep mode, DVFS, avoiding unnecessary VM activation).
29. What is slack time in deadline-aware scheduling, and how does it indicate urgency?

**Comparison**
30. Compare all major scheduling algorithms (FCFS, SJF, RR, Priority, Min-Min, Max-Min, HEFT, GA, PSO, RL, DRL) by objective, complexity, and application.

---

*Compiled from class notes/lecture slides on Cloud Computing Scheduling Algorithms.*