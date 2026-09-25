# Evolution of Computing & Types of Clouds — Summary Notes

> Combined from two lecture decks: *Evolution of Cloud, Parallel & Distributed Computing* and *Cloud Computing Architectural Model — Types of Clouds*, Dr. Prasenjit Chanak, IIT (BHU) Varanasi

---

## Table of Contents
1. [Eras of Computing](#1-eras-of-computing)
2. [Milestones to Cloud Computing](#2-milestones-to-cloud-computing)
3. [Parallel vs. Distributed Computing](#3-parallel-vs-distributed-computing)
4. [Parallel Processing & Hardware Architectures](#4-parallel-processing--hardware-architectures)
5. [Parallel Programming Approaches & Levels](#5-parallel-programming-approaches--levels)
6. [Distributed Computing & System Components](#6-distributed-computing--system-components)
7. [Common Properties of Distributed Systems](#7-common-properties-of-distributed-systems)
8. [Types of Clouds — Overview](#8-types-of-clouds--overview)
9. [Public Clouds](#9-public-clouds)
10. [Private Clouds](#10-private-clouds)
11. [Hybrid / Heterogeneous Clouds](#11-hybrid--heterogeneous-clouds)
12. [Quick Revision — Important Questions](#12-quick-revision--important-questions)

---

## 1. Eras of Computing

- Two fundamental, dominant models of computing: **sequential** and **parallel (and distributed)**.
  - **Sequential era** began in the 1940s; the **parallel/distributed era** followed within a decade.
- Four key elements developed across these eras: **Architecture, Compilers, Applications, Problem-solving environments**.
- Hardware architecture advances enabled system software (compilers, OS), which in turn supported application development.

---

## 2. Milestones to Cloud Computing

Three major milestones led to cloud computing's evolution:

| Milestone | Description |
|---|---|
| **Mainframes** | Large computational facilities using multiple processing units, but presented as a *single entity* to users — **not** distributed systems. |
| **Clusters** | Multiple interconnected nodes, typically in close physical proximity within the *same* administrative domain, working as a single system. |
| **Grids** | Pools resources from *multiple* administrative domains/locations to jointly solve a computational problem. |
| **Clouds** | Delivery of computing services (servers, storage, databases, networking, software) over the Internet — on-demand, scalable, no need to manage physical hardware. |

**Timeline of key events:** 1951 UNIVAC I (first mainframe) → 1960 Cray's first supercomputer → 1966 Flynn's Taxonomy (SISD/SIMD/MISD/MIMD) → 1969 ARPANET → 1970 DARPA's TCP/IP → 1975 Xerox PARC invents Ethernet → 1984 IEEE 802.3 Ethernet & LAN, DEC's VMScluster → 1989 TCP/IP (IETF RFC 1122) → 1990 WWW/HTTP/HTML (Lee–Calliau) → 1997 IEEE 802.11 (Wi-Fi) → 1999 Grid Computing → 2004 Web 2.0 → 2005 Amazon AWS (EC2, S3) → 2007 Manjrasoft Aneka → 2008 Google AppEngine → 2010 Microsoft Azure.

*(Visually: Mainframes → Clusters → Grids → Clouds, each building on the last, plotted against this timeline.)*

---

## 3. Parallel vs. Distributed Computing

- The terms are often used interchangeably but differ slightly:
  - **Parallel** implies a **tightly coupled** system.
  - **Distributed** refers to a **wider class** of systems, including tightly coupled ones.
- **Parallel computing**: computation divided among several processors **sharing the same memory** (single address space accessible to all processors); architecture is usually **homogeneous** (same processor type/capability). Execution units communicate via shared memory.
  - Over time this relaxed to include architectures with shared memory *emulated* via libraries/networking (e.g., a cluster with InfiniBand + distributed shared memory can count as "parallel").
- **Distributed computing**: computation broken into units executed concurrently on different computing elements (different nodes, different processors, or even different cores) — elements are often **heterogeneous** and geographically dispersed.
  - Classic examples: **Computing Grids, Internet Computing Systems**.

**Why parallel computing matters:** silicon processor chips are hitting physical limits (speed of light, thermodynamics limit transistor density) — connecting multiple processors is the viable path forward for "Grand Challenge" problems.

**Definitions of Distributed Systems:**
- **Tanenbaum:** "A distributed system is a collection of independent computers that appears to its users as a single coherent system."
- **Coulouris:** "A distributed system is one in which components located at networked computers communicate and coordinate their actions only by passing messages."

---

## 4. Parallel Processing & Hardware Architectures

**Parallel processing** = processing multiple tasks simultaneously on multiple processors. A task is divided into subtasks (divide-and-conquer) and each runs on a different CPU; this style of programming is **parallel programming**.

**Why it matters:** many applications need more power than sequential computers offer; parallel processing gives a cost-effective solution by adding CPUs + an efficient inter-CPU communication system.

**Influencing factors:** rising computational demand (life sciences, aerospace, GIS, mechanical design) · sequential CPUs hitting physical/speed limits (no more "vertical growth", so "horizontal growth" via multiple CPUs) · vector processing works well only for specific problems (matrix/graphics, not databases) · maturing parallel-processing tools/R&D and networking tech enabling heterogeneous computing.

### Flynn's Taxonomy — Hardware Architecture Classification

| Type | Full Form | Description |
|---|---|---|
| **SISD** | Single Instruction, Single Data | Instructions processed sequentially — the classic "sequential computer." |
| **SIMD** | Single Instruction, Multiple Data | Same instruction executed on all CPUs, each operating on different data. |
| **MISD** | Multiple Instruction, Single Data | Different instructions executed on different CPUs, all on the *same* dataset. |
| **MIMD** | Multiple Instruction, Multiple Data | Multiple instructions executed on multiple datasets — further split into **Shared Memory MIMD** and **Distributed Memory MIMD** machines. |

---

## 5. Parallel Programming Approaches & Levels

**Approaches to parallel programming:**
- **Data Parallelism** — divide-and-conquer used to split *data* into multiple sets.
- **Process Parallelism**
- **Farmer and Worker Model**

**Levels of parallelism** (by grain size — the "lump" of code that can run in parallel):
- **Large-grain** (task-level)
- **Medium-grain** (control-level)
- **Fine-grain** (data-level)
- **Very-fine-grain** (multiple instruction issue)

---

## 6. Distributed Computing & System Components

- **Distributed computing** (as a field): studies distributed systems and uses them to solve computational problems.
- **Distributed system**: several autonomous computational entities, each with its own local memory, communicating via **message passing** (e.g., over high-speed buses/networks). Real-world examples: **Web Services, E-commerce Platforms, Social Networks**.

### Components of a Distributed System (Layered View)
A distributed system emerges from several layers working together to give users the illusion of one coherent system:

```
Applications
     ↑
Middleware  (Frameworks for Distributed Programming, IPC primitives for control & data)
     ↑
Operating System  (IPC, process scheduling/management, resource management)
     ↑
Hardware  (computer + network hardware — the physical infrastructure)
```
- The **bottom two layers** (hardware + OS) form the platform on which specialized software turns networked computers into a distributed system.

**Key components found across distributed systems:** Nodes · Communication Infrastructure · Middleware · Data Management · Coordination & Synchronization · Fault Tolerance & Recovery · Security · Service Discovery & Load Balancing · Application Layer · Resource Management · Data Consistency Models.

---

## 7. Common Properties of Distributed Systems

| Property | Key Aspects |
|---|---|
| **Fault Tolerance** | Redundancy (duplicate critical components/data) · Recovery mechanisms (checkpointing, logging, failover) · Error detection & handling |
| **Transparency** | Location, Replication, Concurrency, and Failure transparency — users interact with the system without needing to know internal complexity |
| **Scalability** | Horizontal scaling (add more nodes) · Load balancing · Dynamic resource management |
| **Concurrency** | Parallelism (simultaneous task execution) · Synchronization (locks, semaphores) to prevent conflicts |
| **Consistency** | Data consistency (strong vs. eventual) · Consistency models (e.g., linearizability, causal consistency) |
| **Coordination** | Coordination services (e.g., Apache ZooKeeper) · Consensus algorithms (Paxos, Raft, Byzantine Fault Tolerance) |
| **Resource Management** | Allocation of CPU/memory/storage · Monitoring node/resource status |
| **Security** | Authentication & authorization · Data protection (encryption, secure channels) |
| **Communication** | Message passing (RPC, message queues) · Underlying networking protocols/topology |
| **Flexibility** | Adaptability to changing workload/resources · Modularity (independent development/deployment of components) |

---

## 8. Types of Clouds — Overview

Clouds are the primary outcome of cloud computing — a type of parallel/distributed system presenting physical and virtual computers as a unified resource, building the infrastructure on which services are delivered.

Classification by **administrative domain**:

| Type | Description |
|---|---|
| **Public Cloud** | Open to the wider public |
| **Private Cloud** | Implemented within an institution's private premises, accessible to its members |
| **Hybrid/Heterogeneous Cloud** | Combination of public + private — typically a private cloud enlarged with public-cloud resources |
| **Community Cloud** | Multi-administrative-domain cloud (mixing public/private/hybrid models) designed for a specific industry's needs |

---

## 9. Public Clouds

- The **first realization** of cloud computing: services available to anyone, anywhere, anytime via the Internet.
- Structurally a distributed system — usually one or more connected **datacenters**.
- Customers self-register (credentials + billing) and use services directly.
- **Benefits:** minimizes IT infrastructure cost; handles peak loads; lets small enterprises start without large up-front investment; **elastic** — customers can dynamically scale up/down.
- **Key characteristic: multitenancy** — serves many users simultaneously, each needing an isolated virtual environment. This drives heavy investment in **monitoring, billing, and usage-history (QoS/accountability)** infrastructure.
- Can offer **any service layer**: e.g., **Amazon EC2** (IaaS), **Google AppEngine** (PaaS), **SalesForce.com** (SaaS).
- Architected to **scale on demand** and sustain peak loads; often uses **geographically distributed datacenters** (e.g., AWS has regions like us-west-1, us-east-1, eu-west-1, each with its own pricing and further split into availability zones).

---

## 10. Private Clouds

- Address the **"loss of control"** critique of public clouds — provider controls infrastructure & potentially sensitive data; risk of breach or unfavorable jurisdiction (e.g., the **USA PATRIOT Act** gives US authorities broad access to data stored on US soil).
- Government/military and similarly regulated institutions often avoid public clouds for sensitive data for this reason.
- **Private cloud**: resource provisioning limited to within an organization's boundaries; internal users get dynamic provisioning over a **private infrastructure**; billing may be internal/departmental rather than pay-as-you-go.

**Key Advantages:**
- **Customer information protection** — easier to maintain in-house security than rely on unproven public assurances.
- **Infrastructure ensuring SLAs** — full control over clustering, failover, replication, monitoring, disaster recovery.
- **Compliance** with third-party/regulatory standards that a public cloud may not support.
- Better utilization of **existing IT investment**; cheaper environment to **test** applications before public deployment.

### Private Cloud Hardware/Software Stack
```
PaaS   → Platform-as-a-Service Solutions   (DataSynapse, Zimory Pools, Elastra CloudServer, Aneka, ...)
IaaS   → Infrastructure Management Software (Eucalyptus, OpenNebula, VMware vCloud, OpenPEX, InterGrid, ...)
IaaS(M)→ Virtual Machine Technology         (KVM, Xen, VMware, ...)
       → Physical Infrastructure            (Datacenters, Clusters, Desktop Grids)
```
- **DataSynapse** — flexible environment for building private clouds on datacenters.
- **Elastra Cloud Server** — platform for configuring/deploying distributed app infrastructures on clouds.
- **Zimory** — automates resource pools based on Xen/KVM/VMware; builds internal clouds from sparse private+public resources; supports migrating applications.
- **Aneka** — pluggable, service-oriented platform for deploying cloud infra on heterogeneous hardware (datacenters, clusters, desktop grids); supports multiple programming models (bag-of-tasks, MapReduce, etc.).

---

## 11. Hybrid / Heterogeneous Clouds

- Public clouds are huge but face **security/administrative** concerns; private clouds keep control but **can't scale on demand** for peak loads.
- **Hybrid cloud** = private cloud + integrated public-cloud services/resources ("heterogeneous cloud") — best of both worlds.
- Lets enterprises keep sensitive data in-house while growing/shrinking capacity via external (public) resources — leased temporarily and released when no longer needed. This practice is called **cloudbursting**.
- Security concerns are then limited only to the public portion handling less-sensitive workload.
- **Dynamic provisioning** is the fundamental enabling component — the ability to acquire/release VMs on demand to scale the system; requires a more advanced scheduler than pure private clouds, one that also **optimizes budget** spent renting public resources.

**Example systems:**
- **OpenNebula** — infra management software that can integrate public-cloud resources (e.g., Amazon EC2) as if they were local VM instances; can integrate advanced schedulers like **Haizea** for cost-based scheduling.
- **InterGrid** — a distributed scheduling engine managing VM allocation across a collection of peer networks (local cluster + public cloud gateway, or combinations); allocates requests based on user budget and peering arrangements.
- **Aneka** — provides a provisioning service that leverages multiple IaaS providers to scale infrastructure; works with a budget-aware scheduler to rent virtual nodes as needed while meeting application QoS.

*(Diagram: a Private Cloud — with its own IaaS(M)/PaaS layer over Datacenter/Cluster/Desktop Grids — connects via Dynamic Provisioning through the Internet out to one or more Public Clouds, forming the Hybrid/Heterogeneous Cloud.)*

---

## 12. Quick Revision — Important Questions

1. What are the four elements of computing that developed across the sequential and parallel/distributed eras?
2. Explain the three milestones (Mainframes → Clusters → Grids → Clouds) leading to cloud computing.
3. Differentiate parallel computing and distributed computing.
4. Why is parallel computing becoming increasingly important given physical limits of silicon processors?
5. Explain Flynn's taxonomy: SISD, SIMD, MISD, MIMD.
6. What are the levels of parallelism (grain sizes)?
7. State Tanenbaum's and Coulouris's definitions of a distributed system.
8. Describe the layered view of a distributed system's components.
9. Explain any four "common properties" of distributed systems (e.g., fault tolerance, transparency, scalability, consistency).
10. Classify clouds based on administrative domain (public, private, hybrid, community).
11. What is multitenancy, and why is it fundamental to public clouds?
12. Why might government/military institutions avoid public clouds? Mention the USA PATRIOT Act example.
13. List the key advantages of private clouds over public clouds.
14. Describe the private cloud hardware/software stack (PaaS/IaaS/IaaS(M)/Physical layers) with examples.
15. What is a hybrid cloud? Explain dynamic provisioning and cloudbursting.
16. Explain how OpenNebula, InterGrid, and Aneka support hybrid cloud scheduling.

---

*Compiled from lecture slides: "Evolution of Cloud Computing, Parallel Computing, and Distributed Computing" and "Cloud Computing Architectural Model — Types of Clouds," Dr. Prasenjit Chanak, IIT (BHU) Varanasi.*