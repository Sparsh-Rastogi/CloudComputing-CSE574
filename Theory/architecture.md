# Cloud Computing Architectural Model — Study Notes

> Based on: *Cloud Computing Architectural Model*, Dr. Prasenjit Chanak, Dept. of CSE, IIT (BHU) Varanasi

---

## Table of Contents
1. [Everything as a Service (XaaS)](#1-everything-as-a-service-xaas)
2. [Cloud Computing Services Classification](#2-cloud-computing-services-classification)
3. [Infrastructure-as-a-Service (IaaS / HaaS)](#3-infrastructure-as-a-service-iaas--haas)
4. [Resource Scheduling in the Cloud](#4-resource-scheduling-in-the-cloud)
5. [Characteristics & Phases of Scheduling](#5-characteristics--phases-of-scheduling)
6. [Scheduling Approaches](#6-scheduling-approaches)
7. [Taxonomy of Cloud Resource Scheduling Algorithms](#7-taxonomy-of-cloud-resource-scheduling-algorithms)
8. [VM-Based Scheduling Algorithms](#8-vm-based-scheduling-algorithms)
9. [QoS Parameter(s)-Based Scheduling Algorithms](#9-qos-parameters-based-scheduling-algorithms)
10. [Platform-as-a-Service (PaaS)](#10-platform-as-a-service-paas)
11. [Quick Revision — Important Exam Questions](#11-quick-revision--important-exam-questions)

---

## 1. Everything as a Service (XaaS)

- Cloud services from different providers can be **combined** to provide a completely integrated solution covering the entire computing stack of a system.
- **IaaS providers** can offer bare metal in terms of virtual machines on which **PaaS** solutions are deployed. When no PaaS layer is needed, the virtual infrastructure can be directly customized with the software stack needed to run applications.
- Example: **virtual Web farms** — a distributed system of Web servers, database servers, and load balancers, on top of which prepackaged software is installed to run Web applications.
- This flexibility makes cloud computing attractive for **startups**, reducing capital investment in IT and allowing them to commercialize ideas quickly and scale according to revenue.

**❓ Exam Question:** What is XaaS? How does combining IaaS and PaaS benefit startups?

---

## 2. Cloud Computing Services Classification

| Category | Characteristics | Product Type | Vendors and Products |
|---|---|---|---|
| **SaaS** | Customers are provided with applications accessible anytime, from anywhere | Web applications and services (Web 2.0) | SalesForce.com (CRM), Clarizen.com (project management), Google Apps |
| **PaaS** | Customers are provided with a platform for developing applications hosted in the cloud | Programming APIs and frameworks, Deployment systems | Google AppEngine, Microsoft Azure, Manjrasoft Aneka, Data Synapse |
| **IaaS/HaaS** | Customers are provided with virtualized hardware and storage on top of which they build their infrastructure | Virtual machine management infrastructure, Storage management, Network management | Amazon EC2 and S3, GoGrid, Nirvanix |

*(Table 4.1 — Cloud Computing Services Classification)*

**❓ Exam Question:** Classify cloud computing services into SaaS, PaaS, and IaaS/HaaS with their characteristics and examples.

---

## 3. Infrastructure-as-a-Service (IaaS / HaaS)

### Overview
- The **most popular and developed** market segment of cloud computing.
- Key characteristics:
  - Customizable infrastructure on demand
  - On-demand computing resources
  - No up-front commitment
  - Start small and grow as required
  - Pay for what you use
  - No maintenance
  - Measured service
  - Scalability
  - Reliability

### Three Principal Layers

> **Diagram — IaaS/HaaS Reference Architecture:**
> `Web-Based Management Interface (Web Services, Portals, REST API)` → `Infrastructure Management Software` → `Physical Infrastructure` (+ optional `Third-Party IaaS Cloud`)

1. **User Interface (top layer)**
   - Provides access to services exposed by the software management infrastructure.
   - Based on **Web 2.0** technologies: Web services, **RESTful APIs**, and mash-ups.
   - Web services/RESTful APIs let programs interact with the service without human intervention, enabling complete integration within a software system.

2. **Infrastructure Management Software (core layer)**
   - Core features of an IaaS solution live here. Components include:

   | Component | Role |
   |---|---|
   | **Scheduler** | Central component; allocates execution of virtual machine instances |
   | **Pricing / Billing** | Tracks the cost of executing each VM instance; maintains data for charging users |
   | **Monitoring** | Tracks execution of each VM instance; maintains data for reporting & performance analysis |
   | **Reservation** | Stores information on all VM instances executed or to be executed in future |
   | **QoS/SLA Management** | Maintains a repository of all SLAs made with users; works with Monitoring to ensure desired quality of service |
   | **VM Image Repository** | Catalog of VM images users can use to create virtual instances |
   | **VM Pool Manager** | Keeps track of all live VM instances |
   | **Provisioning** | Interacts with the scheduler to provide a VM instance external to the local physical infrastructure |

3. **Physical Infrastructure (bottom layer)**
   - A service provider typically uses a massive **datacenter** with hundreds/thousands of nodes.
   - Can also be a **heterogeneous environment** aggregating PCs, workstations, and clusters.
   - Includes **virtual resources rented from external IaaS providers** (third-party IaaS cloud).
   - **Public cloud vendors**: Amazon, GoGrid, Joyent, Rightscale, Terremark, Rackspace, ElasticHosts, Flexiscale — own large datacenters, give IaaS access to their infrastructure.
   - **Private/self-managed IaaS software**: Enomaly, Elastra, Eucalyptus, OpenNebula, and IaaS(M) solutions from VMware, IBM, Microsoft.

**❓ Exam Questions:**
- Describe the three-layer architecture of IaaS/HaaS with a diagram.
- Explain the role of the scheduler, pricing/billing, monitoring, and reservation components in IaaS.
- Differentiate between public IaaS vendors and private IaaS management software, with examples.

---

## 4. Resource Scheduling in the Cloud

- **Scheduling problem**: allocating resources to jobs to attain an objective function within specified resource constraints.
- **Classical scheduling**: sequence for allocating jobs on (fixed) resources must be defined.
- **Online scheduling**: no need for future knowledge at allocation time; in cloud computing, providers can add/release resources as per application demand.

### Two Types of Scheduling in Cloud Computing
| Side | Mapping |
|---|---|
| **Client side** | Mapping of tasks to VMs |
| **Provider side** | Mapping of virtual machines to physical machines |

### Key Terminology

| Term | Definition |
|---|---|
| **Task** | A computation unit that runs in the cloud environment; defined per application requirement; can be independent or dependent; cannot be divided further |
| **Job** | Combination of different tasks with different processing capabilities; each job may have different resource requirements |
| **Workflow** | A series of activities that need to be performed to execute the application |
| **Provisioning** | The formal allocation of resources |
| **Scheduling** | The exact mapping of a job to an ingredient resource, aiming for an optimal solution |
| **Application** | Designed to solve a large-scale problem; consists of many jobs requiring computation at different levels; can be "monolithic" (assigned a complete computational node) |
| **Resource** | A computational unit used to complete an application's requirements (CPU, memory, network, etc.); has parameters like processing capability, data speed, storage space, workload |
| **Scheduler** | A process that decides which task/process should be accessed and run, and when, by the available resources — categorized as **local**, **global**, or **enterprise** scheduler based on frequency of operation |

**❓ Exam Questions:**
- Differentiate between task, job, workflow, and application in the context of cloud scheduling.
- Differentiate client-side and provider-side scheduling.
- Differentiate provisioning and scheduling.

---

## 5. Characteristics & Phases of Scheduling

### Characteristics of Cloud Scheduling
- Huge infrastructure
- Scalable nature of clouds
- Resource heterogeneity
- Highly diversified applications
- Diversity in resource connectivity techniques
- Decentralized resource ownership

### Phases of Scheduling
| Phase | Description |
|---|---|
| **Resource Provisioning** | Formal allocation of resources in the cloud domain; considers application profiling and analogical benchmarking to produce an appropriate schedule; allocation as per user specification |
| **Scheduling** | Mapping of tasks to appropriate resources for completing application execution |

**❓ Exam Question:** List the characteristics of cloud scheduling and explain its two main phases.

---

## 6. Scheduling Approaches

| Approach Pair | Description |
|---|---|
| **Local vs. Global** | *Local*: selects the process residing on a single CPU. *Global*: uses resource information to allocate processes across different processors for an optimal solution. |
| **Static vs. Dynamic** | *Static*: resource/task information is available at scheduling time. *Dynamic*: information is not available beforehand; resource upgrade/degradation info is kept posted. |
| **Centralized vs. Decentralized** | *Centralized*: the cloud scheduler has complete control over resources (faces issues like scalability, load balancing, fault tolerance). *Decentralized*: no centralized control — monitoring is done by the local scheduler. |
| **Co-operative vs. Non-cooperative** | *Co-operative*: each scheduler manages its own tasks per a designed policy to achieve the target. *Non-cooperative*: each scheduler makes independent decisions, acting as an autonomous entity. |
| **Immediate vs. Batch** | *Immediate*: jobs are scheduled as soon as they enter the system. *Batch*: tasks are grouped together before being scheduled for execution. |
| **Approximation vs. Heuristics** | *Approximation*: provides solutions close to optimal, with a guarantee on closeness (both in time and quality) — but too slow for large/dynamic cloud scenarios. *Heuristics*: practical rules-of-thumb for a "good enough" solution quickly; considered the de-facto standard for large-scale, dynamic, distributed scheduling (grid/cloud). |

**❓ Exam Questions:**
- Differentiate centralized and decentralized scheduling approaches.
- Why are heuristic algorithms preferred over approximation algorithms in cloud resource scheduling?
- Explain co-operative vs. non-cooperative scheduling.

---

## 7. Taxonomy of Cloud Resource Scheduling Algorithms

> **Diagram:**
> ```
> Resource Scheduling Algorithms
>        │
>   ┌────────────┬────────────────┬───────────────────────┬──────────────┐
> VM based RSA  Heuristic based RSA  Resource Allocation based RSA   QoS Based RSA
>   │                                                             │
>   ├── Dynamic VM placement                                  ├── Cost
>   ├── Network aware VM placement                            ├── Time
>   └── Energy aware VM placement                             ├── Reliability
>                                                               ├── Energy
>                                                               └── Security
> ```

Resource Scheduling Algorithms (RSA) branch into four categories:
1. **VM-based RSA**
2. **Heuristic-based RSA**
3. **Resource Allocation-based RSA**
4. **QoS-based RSA**

**❓ Exam Question:** Draw and explain the taxonomy of cloud resource scheduling algorithms.

---

## 8. VM-Based Scheduling Algorithms

- In VM scheduling, the cloud provider schedules VMs on physical machines whenever a user requests resources. In the VM placement problem, the static part of physical resources is shared among users.

| Type | Description |
|---|---|
| **Dynamic VM Placement** | Allocation/re-allocation of a VM is done dynamically; aims to utilize resources efficiently; important for system maintenance. **Live migration** is used to schedule resources across data centers, improving fault management and load balancing. Enables **elasticity** — a key cloud characteristic. |
| **Energy-Aware VM Placement** | Energy consumption is a major issue for providers. Reduced through **server consolidation**, optimizing physical-machine operations, and **dynamic voltage scaling** processors. |
| **Network-Aware VM Placement** | Growing numbers of users increase network traffic; bandwidth must be shared without hurting VM QoS. VMs access a physical machine's (PM's) network interface to communicate with other application/system components. |

### Hypervisors and Network Resources
- Hypervisors typically treat a PM's resources (network interfaces, switch links) as **unmanaged resources**.
- Hypervisors do **not** guarantee allocation to individual VMs.
- They rely on **statistical multiplexing**, assuming VMs are unlikely to simultaneously max out their nominally assigned bandwidth.
- Consequence: VMs can potentially affect each other's performance due to **contention** for network interface resources.

**❓ Exam Questions:**
- Explain dynamic VM placement and its relation to live migration and elasticity.
- How is energy-aware VM placement achieved?
- Why don't hypervisors guarantee network bandwidth allocation to VMs?

---

## 9. QoS Parameter(s)-Based Scheduling Algorithms

- Focus: not just reducing real-life factors (cost, time) but aiding scheduling decisions in cloud resource management systems, while satisfying an application's quality requirements.
- Providers want to maximize profit via proper resource utilization while minimizing unnecessary-execution costs; high-performance operation increases energy consumption (risk of system failure); users expect minimum response time/cost while their SLA requirements and security are met.

| Type | Description |
|---|---|
| **Cost-based** | Plays an important role since clouds work on the **pay-as-you-go** principle and offer resources on-demand. |
| **Time-based** | E.g., Yuan et al. (2017c) proposed a time-aware task scheduling algorithm for green data centers, combining **particle swarm optimization** and **simulated annealing** (a meta-heuristic) to investigate temporal variations and consider delay bounds. |
| **Energy-based** | Extracts total energy consumed for processing an application depending on the resource used; important to reduce energy consumption in data centers, since idle power wastage increases as data grows. |
| **Reliability-based** | E.g., Malik et al. (2012) designed a reliability-assessment model for cloud infrastructure; the fault-tolerance parameter is handled by checking node reliability during scheduling. |
| **Security-based** | Security is a major constraint the scheduling algorithm must satisfy; the VM scheduler's responsibility is to provide security while minimizing application response time simultaneously. |

**❓ Exam Questions:**
- What is QoS-parameter based scheduling? Name its five sub-types.
- Explain cost-based and energy-based scheduling algorithms with their motivations.
- Why is security-based scheduling important in cloud environments?

---

## 10. Platform-as-a-Service (PaaS)

### Overview
- PaaS provides a **development and deployment platform** for running applications in the cloud — the **middleware** on top of which applications are built.
- **Application management** is the core middleware functionality.
- PaaS implementations provide a **runtime environment** but do **not** expose services for managing the underlying infrastructure.
- Automates: deploying applications, configuring application components, provisioning/configuring supporting technologies (load balancers, databases), and managing system change per user-set policies.
- Developers design systems in terms of **applications** — not concerned with hardware (physical/virtual), OS, or other low-level services.
- Core middleware manages resources and scales applications on demand/automatically, per user commitments.
- Exposed via a **Web-based interface** or **programming APIs/libraries**.

### PaaS Reference Model

> **Diagram — PaaS Reference Architecture:**
> `Web-Based Interface (Web Services, Portals, REST API)` + `Programming API/Libraries` → **PaaS Core Middleware** (Elasticity & Scaling, Resources Management, Runtime, Application Management, User Management, QoS/SLA Management & Billing) → `Physical Infrastructure` + `IaaS Providers`

### Delivery Models
- PaaS can offer middleware **together with infrastructure**, or simply provide software installed on user premises.
- The PaaS provider also owns large datacenters where applications execute.
- **Pure PaaS**: middleware constitutes the core value of the offering.
- Some vendors deliver both middleware and infrastructure, and ship only the middleware for private installations.

### PaaS Offering Classification (Table 4.2)

| Category | Description | Product Type | Vendors/Products |
|---|---|---|---|
| **PaaS-I** | Runtime environment with Web-hosted application development platform; rapid application prototyping | Middleware + Infrastructure | Force.com, Longjump |
| **PaaS-II** | Runtime environment for scaling Web applications; runtime may be enhanced with additional scaling components | Middleware + Infrastructure / Middleware only | Google AppEngine, AppScale, Heroku, Engine Yard, Joyent Smart Platform, GigaSpaces XAP |
| **PaaS-III** | Middleware and programming model for developing distributed applications in the cloud | Middleware + Infrastructure / Middleware only | Microsoft Azure, DataSynapse, Cloud IQ, Manjrasoft Aneka, Apprenda SaaSGrid, GigaSpaces DataGrid |

### The Three Categories in Detail

1. **Fully Cloud-Native Development & Deployment (PaaS-I)**
   - Completely follows the cloud computing style for application development and deployment.
   - Offers an **integrated development environment hosted within the Web browser**, where apps are designed, developed, composed, and deployed.
   - Example: **Force.com**, **Longjump** — both deliver middleware + infrastructure combined.

2. **Scalable Web Application Infrastructure**
   - Focused on providing scalable infrastructure for Web applications (mostly websites).
   - Developers use the providers' APIs, built on top of industrial runtimes.
   - **Google AppEngine**: most popular; scalable runtime based on Java & Python (modified for a secure runtime, enriched with additional APIs/components for scalability).
   - **AppScale**: open-source, interface-compatible implementation of AppEngine, installed on physical infrastructure.
   - **Joyent Smart Platform**: similar approach to AppEngine.
   - **Heroku** and **Engine Yard**: scalability support for Ruby and Ruby on Rails websites — developers build apps traditionally, then deploy by uploading to the provider's platform.

3. **General-Purpose Cloud Programming Platforms**
   - Support any kind of application, not just Web applications.
   - **Microsoft Windows Azure**: most popular; comprehensive framework for building service-oriented cloud applications on top of **.NET** technology, hosted on Microsoft datacenters.
   - Others: **Manjrasoft Aneka, Apprenda SaaSGrid, Appistry Cloud IQ Platform, DataSynapse, GigaSpaces DataGrid** — provide middleware with different services.

### Common Criteria Across PaaS Implementations

| Criterion | Description |
|---|---|
| **Run-time Framework** | The "software stack" of the PaaS model; executes end-user code per policies set by user and provider. |
| **Abstraction** | Higher-level abstraction than IaaS. IaaS focuses on "raw" access to virtual/physical infrastructure; PaaS focuses on the *applications* the cloud must support — deploying/managing applications rather than raw VMs. |
| **Automation** | PaaS automates deployment to infrastructure and scaling (provisioning additional resources when needed), per the SLA between customer and provider — a feature not normally native to IaaS. |
| **Cloud Services** | PaaS provides developers/architects with services & APIs to simplify creation/delivery of elastic, highly-available cloud applications — key differentiators among competing PaaS solutions (app monitoring, management, reporting components). |
| **Integration** | Ability to integrate third-party cloud services from other vendors via **service-oriented architecture**, through standard interfaces/protocols — makes app development more agile and able to evolve with customer/user needs. |

### PaaS — Financial & Business Perspective
- IaaS shifts capital cost into operational cost via outsourcing.
- **PaaS** can cut costs across **development, deployment, and management** of applications.
- Reduces the risk of ever-changing technologies by offloading the cost of technology upgrades to the PaaS provider — happening transparently for the consumer.
- PaaS bundled with underlying IaaS helps even small startups quickly offer integrated solutions on a hosted platform at minimal cost — making PaaS a viable option targeting different market segments.

**❓ Exam Questions:**
- Explain the PaaS reference model with a diagram.
- Differentiate the three categories of PaaS implementations with examples.
- List and explain the five common criteria expected in any PaaS implementation.
- How does PaaS differ from IaaS in terms of abstraction and automation?
- Explain the financial advantages of PaaS over IaaS.

---

## 11. Quick Revision — Important Exam Questions

**Foundational**
1. What is XaaS (Everything as a Service)? How are IaaS and PaaS combined in practice?
2. Classify cloud computing services (SaaS, PaaS, IaaS/HaaS) with characteristics and examples.

**IaaS/HaaS**
3. Explain the three-layer architecture of IaaS/HaaS.
4. Explain the roles of scheduler, pricing/billing, monitoring, reservation, QoS/SLA management, VM image repository, VM pool manager, and provisioning components.
5. Differentiate public IaaS vendors vs. private IaaS management software.

**Scheduling**
6. Differentiate task, job, workflow, and application.
7. Differentiate provisioning and scheduling.
8. Differentiate client-side vs. provider-side scheduling.
9. Explain the characteristics and phases of cloud scheduling.
10. Explain the six pairs of scheduling approaches (local/global, static/dynamic, centralized/decentralized, co-operative/non-cooperative, immediate/batch, approximation/heuristics).
11. Draw and explain the taxonomy of cloud resource scheduling algorithms.
12. Explain VM-based scheduling: dynamic, energy-aware, and network-aware VM placement.
13. Why don't hypervisors guarantee bandwidth allocation to individual VMs?
14. Explain QoS-parameter-based scheduling and its five sub-types (cost, time, energy, reliability, security).

**PaaS**
15. Explain the PaaS reference model.
16. Differentiate the three categories of PaaS with examples (Force.com/Longjump; Google AppEngine/Heroku; Windows Azure/Aneka).
17. List and explain the common criteria of PaaS (runtime framework, abstraction, automation, cloud services, integration).
18. Compare PaaS and IaaS from an abstraction and financial standpoint.

---

*Compiled from lecture slides on Cloud Computing Architectural Model by Dr. Prasenjit Chanak, IIT (BHU) Varanasi.*