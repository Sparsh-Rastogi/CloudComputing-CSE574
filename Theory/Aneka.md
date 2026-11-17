# Aneka: Cloud Application Platform: Complete Exam Notes

*Source: Cloud_Computing_10 to 14 (Dr. Prasenjit Chanak, IIT BHU). Duplicate slides across files are merged.*

---

## 0. Contents

1. Introduction
2. Framework Overview
3. Anatomy of the Aneka Container
4. Platform Abstraction Layer (PAL)
5. Fabric Services
6. Foundation Services
7. Application Services
8. Building Aneka Clouds (Infrastructure & Logical Organization)
9. Deployment Modes (Private / Public / Hybrid)
10. Master Comparison Tables
11. Likely Exam Questions & Model Answers
12. Common Mistakes
13. Self-Test
14. One-Page Last-Minute Summary

---

## 1. Introduction

- **Aneka** = **Manjrasoft Pty. Ltd.'s** solution for **developing, deploying and managing** cloud applications.
- A **scalable cloud middleware** deployable on **heterogeneous** computing resources.
- Offers an **extensible collection of services** that:
  - coordinate application execution,
  - help administrators monitor the cloud,
  - integrate with existing cloud technologies.
- **Key advantage:** an **extensible set of APIs** for different **programming models** (**Task, Thread, MapReduce**), used for:
  - developing distributed applications,
  - integrating new capabilities into the cloud,
  - supporting **public, private and hybrid** deployment.

---

## 2. Framework Overview

### 2.1 What is Aneka?
- Software platform for developing cloud computing applications.
- Couples different computing resources into **one unique virtual domain: the Aneka Cloud**, where applications execute.
- According to the Cloud Computing Reference Model, Aneka is a **pure PaaS** solution.
- Deployable on: a **network of computers, a multicore server, datacenters, virtual cloud infrastructures, or a mixture**.
- Provides both **middleware** (managing and scaling distributed applications) and an **extensible set of APIs** (developing them).

### 2.2 Layered architecture (diagram recall)

| Layer | Contents |
|---|---|
| **Application Development & Management** | Management: Tools, Interfaces and APIs · Software Development Kit: APIs & Tools |
| **Middleware: Container** → **Application Services** | Distributed Threads · MapReduce · Bag of Tasks · PSM (Parameter Sweep) · Other models |
| → **Foundation Services** | Storage · Resource Reservation · Billing & Reporting · Licensing & Accounting |
| → **Fabric Services** | High-Availability · Resource Provisioning · Hardware Profiling · Membership |
| *(vertical arrow across all)* | **Persistence & Security** |
| **PAL: Platform Abstraction Layer** | Interface to OS/hardware |
| **Infrastructure** | Enterprise Desktop Grid · Data Centers · Clusters · Public Cloud |

### 2.3 Service-Oriented Architecture (SOA)
- Aneka implements **SOA**; **services are the fundamental components** of an Aneka Cloud.
- Services operate at **container level** and, **except for the PAL**, provide developers, users and administrators with all framework features.
- Services are the **extension and customization point**: new services can be integrated, or existing ones **replaced** with a different implementation.
- Framework includes basic services for: infrastructure & node management, application execution, accounting, system monitoring.
- Features can be added by **dynamically plugging new services into the container**.

### 2.4 Six key aspects (very likely exam question)

| Aspect | Meaning |
|---|---|
| **Elasticity & scaling** | **Dynamic provisioning service** upsizes/downsizes infrastructure for applications |
| **Runtime management** | Keeps infrastructure up and running; hosting environment for services. Represented by the **container** + services for **membership & lookup, infrastructure maintenance, profiling** |
| **Resource management** | Resources added/removed dynamically per application needs and user requirements; QoS-based execution via **dynamic provisioning + reserving nodes for exclusive use** |
| **Application management** | Services for **scheduling, execution, monitoring, storage management** |
| **User management** | **Multitenant** environment; extensible user system defining **users, groups, permissions**; builds the **security infrastructure**; fundamental for accounting |
| **QoS/SLA management & billing** | Application execution is **metered and billed**; services coordinate to track resource usage per application and bill the owner |

> **Mnemonic:** **E**very **R**ed **R**obot **A**lways **U**ses **Q**uality → **E**lasticity, **R**untime, **R**esource, **A**pplication, **U**ser, **Q**oS.

### 2.5 SDK vs Management Kit
- All services expose interfaces/APIs on which the **SDK** and **management kit** are built.
- **SDK:** application **development and modeling**; APIs for existing programming models + an **object model for creating new models**.
- **Management kit:** interacting with **runtime services** to manage **infrastructure, users and applications**.

---

## 3. Anatomy of the Aneka Container

- The container = **building block** of Aneka Clouds and the **runtime machinery** for services and applications.
- It is the **unit of deployment**: a **lightweight software layer** hosting services and interacting with the underlying OS and hardware.
- Main role: lightweight environment to deploy services + basic capabilities such as **communication channels** to other nodes.
- **Almost all operations** in Aneka are performed by **services** managed by the container.
- Three service categories:
  1. **Fabric Services**
  2. **Foundation Services**
  3. **Application Services**
- The services stack sits **on top of the PAL**, giving a uniform view of the software/hardware environment.
- **Persistence and security traverse the whole stack** to provide a secure and reliable infrastructure.

---

## 4. Platform Abstraction Layer (PAL)

- Detects the **supported hosting environment** and provides the matching implementation to interact with it, supporting the container's activity.

**Features**
1. Uniform, platform-independent **interface for accessing the hosting platform**
2. Uniform access to **extended/additional properties** of the platform
3. Uniform, platform-independent access to **remote nodes**
4. Uniform, platform-independent **management interfaces**

**Composition:** a small software layer with
- a **detection engine** that **automatically configures the container at boot time**,
- platform-specific components for information access,
- implementations for **Windows, Linux and Mac OS X**.

---

## 5. Fabric Services

- The **lowest level** of the container's software stack.
- Provide access to the **resource-provisioning subsystem** and the **monitoring facilities**.
- **Resource-provisioning services:** dynamically provide **new nodes on demand** using **virtualization**.
- **Monitoring services:** **hardware profiling** + a basic monitoring infrastructure usable by all services in the container.

### 5.1 Profiling and Monitoring
Exposed mostly through **Heartbeat, Monitoring and Reporting Services**.
- **Heartbeat Service:** makes available information collected **through the PAL**.
- **Monitoring + Reporting:** a **generic infrastructure** for monitoring the activity of any service.

Built-in services that feed this channel:

| Service | What it reports |
|---|---|
| **Membership Catalogue** | Performance information of nodes |
| **Execution Service** | Several time intervals of job execution |
| **Scheduling Service** | State transitions of jobs |
| **Storage Service** | Data transfer info: upload/download times, filenames, sizes |
| **Resource Provisioning Service** | Provisioning and lifetime information of virtual nodes |

### 5.2 Resource Management
- Fundamental feature; covers **resource membership, resource reservation, resource provisioning**.
- Services: **Index Service (Membership Catalogue)**, **Reservation Service**, **Resource Provisioning Service**.
- **Membership Catalogue:** the fundamental component; tracks **basic node information for all nodes, connected or disconnected**.
- **Dynamic resource provisioning:** integrates and manages **virtual resources rented from IaaS providers** into the Aneka Cloud.
- Provisioning is designed to support **QoS-requirement-driven** execution.

---

## 6. Foundation Services

- **Fabric** = basic infrastructure management. **Foundation** = **logical management** of the distributed system built on that infrastructure + supporting services for application execution.
- All programming models can integrate with and use these services.
- Cover: **storage management, accounting/billing/resource pricing, resource reservation**.

### 6.1 Storage Management
Two facilities:

| | Centralized file storage | Distributed file system |
|---|---|---|
| Suited for | **Compute-intensive** applications | **Data-intensive** applications |
| Needs | Powerful processors; low storage demand | Large files (GB/TB); processing is **not** the bottleneck |
| Files | Small, easily moved between nodes | Large |
| Solution | Centralized storage node or **pool of storage nodes** | File system **coupling storage space of all nodes** in the cloud, more **scalable** |

### 6.2 Accounting, Billing and Resource Pricing
- **Accounting Services:** track the **status of applications**; give a detailed breakdown of infrastructure usage (application execution + storage + other utilization parameters, with full history).
- This information is **the foundation on which users are charged**.
- **Billing Service:** detailed info on **each user's resource usage with associated costs**.
- Each resource can be **priced differently** based on the services available in its container or the software installed on the node.

### 6.3 Resource Reservation
- Supports distributed application execution; reserves resources for **exclusive use** by specific applications.
- Built from **two services**:
  - **Resource Reservation Service:** tracks **all reserved time slots**, gives a **unified view** of the system.
  - **Allocation Service:** installed on **each node with execution services**; manages the **local database of allocated slots**.
- Applications with **deadlines** request a number of nodes for a timeframe. If feasible, the Reservation Service returns a **reservation identifier** (proof of booking).

**Implementations (differ in protocol or request parameters):**

| Type | Feature |
|---|---|
| **Basic Reservation** | Reserve execution slots on nodes; implements the **alternate offers protocol** (alternatives if the initial request can't be met) |
| **Libra Reservation** | Variation of Basic; **prices nodes differently by hardware capability** |
| **Relay Reservation** | Very thin; lets a **resource broker** reserve nodes and control the reservation logic; useful in **intercloud** integration |

**Why it matters (QoS)**
- Fundamental to ensuring **negotiated QoS**.
- Gives a **predictable environment**: applications finish **within deadline or are not executed at all**.
- Acceptance is based on **static allocation** onto the existing physical/virtual infrastructure, considering **current and future load**.
- **Weakness:** sensitive to **node failures**, which can make Aneka unable to honor the **SLA**.

---

## 7. Application Services

- Manage **application execution**; the layer **differs per programming model**.
- Number/type of services vary by model.
- Two activities common to all models → abstracted as the **reference model**:
  1. **Scheduling Service**
  2. **Execution Service**

### 7.1 Scheduling Services
- Plan execution of distributed applications and **allocate jobs to nodes**.
- **Integration point** with: Resource Provisioning, Reservation, Accounting and Reporting Services.
- Common tasks:
  1. **Job-to-node mapping**
  2. **Rescheduling of failed jobs**
  3. **Job status monitoring**
  4. **Application status monitoring**
- **No centralized scheduling engine:** each programming model has its **own scheduling service**, working with existing middleware services.

### 7.2 Execution Services
- Control execution of **single jobs** composing an application; set up the **runtime environment**.
- Common operations:
  1. **Unpack** jobs from the scheduler
  2. **Retrieve input files**
  3. **Sandboxed execution**
  4. **Submit output files**
  5. **Execution failure management** (capture context to identify the failure)
  6. **Performance monitoring**
  7. **Pack jobs and send back** to the scheduler

> **Flow to remember:** Scheduler → (job) → Execution: unpack → fetch inputs → run in sandbox → return outputs → pack → back to scheduler.

### 7.3 Programming Models

| Model | Description |
|---|---|
| **Task Model** | Independent **"bag of tasks"**; tasks independent of each other, executable in **any order** |
| **Thread Model** | Extends classical **multithreading to a distributed infrastructure**; the **Thread abstraction wraps a method executed remotely** |
| **MapReduce Model** | Implementation of **Google's MapReduce** on top of Aneka |
| **Parameter Sweep Model** | **Specialization of Task Model**; a **template task** whose instances are generated from **different parameter combinations** (each = a point in the domain of interest) |

---

## 8. Building Aneka Clouds

- Aneka is primarily a platform for **developing distributed applications**; as software, it needs infrastructure that must be **managed**.
- Cloud building is a primary **administrator** task; supports **public, private, hybrid**.

### 8.1 Infrastructure Organization

| Component | Role |
|---|---|
| **Administrative (Management) Console** | Performs **all management operations** |
| **Repository** | Stores **libraries** to lay out/install Aneka; = **software image for node manager and container**; served via **HTTP, FTP, file share**, etc. |
| **Node Manager** | Manages the node |
| **Aneka Container** | Deployment unit hosting services |

- Physical/virtual nodes are managed **uniformly** if there is an **Internet connection and remote administrative access**.
- **Dynamic provisioning** of virtual instances: from **prepackaged images** already containing Aneka; only need **configuration to join** a specific cloud.
- Alternatively install only the **container** or the **Aneka daemon**; the choice depends mostly on the **lifetime of the virtual resources**.

### 8.2 Logical Organization
- Depends on each container's configuration.
- Most common: **master-worker with separate storage nodes**.

**Master node**
- Defined by the **Index Service (Membership Catalogue) in master mode**.
- Services: **Index (master) · Heartbeat · Logging · Reservation · Resource Provisioning · Accounting · Reporting & Monitoring · Scheduling services** (all models).
- Uses an **RDBMS** to keep service state; all scheduling services share the **application store** (persisted in the RDBMS) → **fault tolerance**.
- Master configuration can be **replicated on several nodes** → **high availability via failover**.

**Worker nodes**
- The **workforce**; execute applications.
- Services: **Index (slave) · Heartbeat · Logging · Allocation · Monitoring · Execution services**.
- Pool can be **partitioned** with different execution services to balance load among programming models and reserve nodes for specific application classes.

**Storage nodes**
- Optimized for storage; have the **Storage Service**.
- Count depends on **predicted workload and storage consumption**; usually on machines with **large disk space**.
- Services: **Index · Heartbeat · Logging · Monitoring · Storage**.

---

## 9. Deployment Modes

### 9.1 Private Cloud
- **Local physical resources** + infrastructure management software providing a **local pool of nodes** (maybe virtualized).
- Built from a **heterogeneous pool: desktops, clusters, workstations**; can be **partitioned into groups**.
- Fits **predictable workloads**, where a **local VM manager** can handle excess demand.
- Mostly **physical, long-lived, static** nodes, rarely reconfigured.
- *Diagram:* Master node (Application Management & Scheduling, Resource Provisioning, Resource Reservation) → Workstations, Clusters, Desktop Machines, Virtual Clusters (**Eucalyptus**).

### 9.2 Public Cloud
- Aneka **master and workers installed on a fully virtualized infrastructure** of providers such as **Amazon EC2 or GoGrid**.
- **Static deployment:** nodes pre-provisioned, used like real machines; just replicates classic Aneka, **no dynamic provisioning**.
- **Dynamic deployment:** uses **IaaS elasticity** → completely dynamic cloud.
- Generally within the boundaries of **a single IaaS provider**.
- *Diagram:* Master (App Management & Scheduling, Resource Provisioning, Reporting/Billing/Accounting) on an EC2 instance → slave nodes as EC2 instances, all within "EC2 boundaries".

### 9.3 Hybrid Cloud
- **Most common** Aneka deployment.
- **Existing local infrastructure** = static deployment, **elastically scaled on demand** into public clouds.
- **Most complete**: uses all capabilities:
  1. **Dynamic Resource Provisioning**
  2. **Resource Reservation**
  3. **Workload Partitioning**
  4. **Accounting, Monitoring and Reporting**
- *Diagram:* Local infrastructure (master with Reporting/Billing/Accounting, Resource Reservation, App Management & Scheduling; desktops/workstations, clusters, virtual clusters via **Eucalyptus, Xen, VMware**) → **Provisioning Service** → public clouds (**Amazon Web Services, GoGrid**).

---

## 10. Master Comparison Tables

### 10.1 Three service layers of the container

| Layer | Purpose | Services |
|---|---|---|
| **Fabric** (lowest) | Basic infrastructure management | High-availability, Resource Provisioning, Hardware Profiling, Membership; Heartbeat/Monitoring/Reporting |
| **Foundation** | Logical management of the distributed system | Storage, Resource Reservation, Accounting/Billing/Pricing, Licensing |
| **Application** | Runtime for programming models | Scheduling + Execution for Task, Thread, MapReduce, Parameter Sweep |

### 10.2 Node types

| | Master | Worker | Storage |
|---|---|---|---|
| Index Service | Master | Slave | Slave |
| Scheduling | ✅ | ❌ | ❌ |
| Reservation / Provisioning / Accounting / Reporting | ✅ | ❌ | ❌ |
| Allocation | ❌ | ✅ | ❌ |
| Execution | ❌ | ✅ | ❌ |
| Storage Service | ❌ | ❌ | ✅ |
| Heartbeat + Logging | ✅ | ✅ | ✅ |

> **Mnemonic:** Master = **S**cheduling, **R**eservation, **P**rovisioning, **A**ccounting, **R**eporting. Worker = **E**xecution + **A**llocation. Storage = **S**torage.

### 10.3 Deployment modes

| Feature | Private | Public | Hybrid |
|---|---|---|---|
| Where | Local physical (maybe virtualized) | Virtualized IaaS (EC2, GoGrid) | Local + public IaaS |
| Node lifetime | Long, static | Static or dynamic | Static local + dynamic cloud |
| Elasticity | Limited | Full (dynamic style) | On-demand scale-out |
| Best for | Predictable workloads | Fully elastic needs | Variable load + existing infra |
| Features used | Basic | Provisioning, billing | **All** |
| Popularity | Specific cases | Less common | **Most common** |

### 10.4 Storage options

| | Centralized | Distributed FS |
|---|---|---|
| Application | Compute-intensive | Data-intensive |
| File size | Small | GB to TB |
| Scalability | Lower | Higher |

### 10.5 Reservation types

| Basic | Libra | Relay |
|---|---|---|
| Slots + alternate offers | Hardware-based pricing | Thin; broker-controlled; intercloud |

---

## 11. Likely Exam Questions & Model Answers

### Short answer (2 to 3 marks)

**Q1. What is Aneka?**
Manjrasoft's pure PaaS cloud middleware for developing, deploying and managing cloud applications on heterogeneous resources, with extensible APIs for Task, Thread and MapReduce models.

**Q2. Why is Aneka called a PaaS?**
It provides a middleware platform plus APIs for developing and running applications, instead of raw infrastructure (IaaS) or finished software (SaaS).

**Q3. What is the Aneka container?**
The unit of deployment: a lightweight software layer hosting services and interacting with the OS/hardware; it provides communication channels and hosts Fabric, Foundation and Application services.

**Q4. What is the PAL and why is it needed?**
A small layer with a detection engine that configures the container at boot and gives a uniform, platform-independent interface to Windows, Linux and Mac OS X (hosting platform, properties, remote nodes, management).

**Q5. What does the Membership Catalogue do?**
It tracks basic information for all nodes (connected or disconnected) and is the core of resource management; the Index Service in master mode defines the master node.

**Q6. Centralized storage vs distributed file system?**
Centralized suits compute-intensive apps with small files; a distributed file system suits data-intensive apps with huge files and scales better.

**Q7. How does Aneka charge users?**
The Accounting Service records application execution, storage and resource utilization history; the Billing Service turns this into per-user costs, with resources priced by installed services/software.

**Q8. Name the reservation implementations.**
Basic (alternate offers protocol), Libra (hardware-based pricing), Relay (thin, broker-controlled, intercloud).

**Q9. Why is reservation sensitive to node failures?**
Acceptance rests on static allocation to the current infrastructure; a failing node can make Aneka unable to meet the SLA.

**Q10. Does Aneka have a centralized scheduler?**
No. Each programming model has its own scheduling service that cooperates with the other middleware services.

**Q11. Task Model vs Parameter Sweep Model?**
Task = independent tasks in any order. Parameter Sweep specializes Task: one template task instantiated over parameter combinations.

**Q12. How is master failure handled?**
The master configuration is replicated across nodes (failover); state and the application store persist in an RDBMS.

**Q13. Why is hybrid the most common deployment?**
Existing infrastructure becomes the static base and scales into public clouds on demand, using every Aneka capability.

### Long answer (5 to 10 marks)

**Q14. Explain the layered architecture of Aneka with a diagram.**
Draw: Application Development & Management (SDK + management kit) → Container with Application / Foundation / Fabric Services (+ vertical Persistence & Security) → PAL → Infrastructure (desktop grid, data centers, clusters, public cloud). Briefly describe each layer's services.

**Q15. Describe the key aspects (services) of the Aneka framework.**
Elasticity & scaling, runtime, resource, application, user, QoS/SLA & billing management, each with one or two lines (see 2.4). Add SOA and extensibility.

**Q16. Explain the Foundation Services.**
Storage management (two facilities), accounting/billing/pricing, and resource reservation (services, implementations, QoS role, SLA weakness).

**Q17. Explain Application Services and programming models.**
Scheduling + Execution reference model, tasks of each, no centralized scheduler, then the four models.

**Q18. Explain how Aneka Clouds are built: infrastructure and logical organization.**
Console, repository, node manager/container, provisioning via prepackaged images → master/worker/storage with service lists, RDBMS and failover.

**Q19. Describe Private, Public and Hybrid deployment of Aneka.**
Definition, resources, characteristics and diagram for each; finish with the comparison table.

**Q20. Explain Profiling and Monitoring in Aneka.**
Heartbeat, Monitoring and Reporting services; the five built-in services that supply information and what each reports (see 5.1).

---

## 12. Common Mistakes

- Calling Aneka IaaS or SaaS. It is **PaaS**.
- Saying Aneka has a **centralized scheduler**. It does not.
- Mixing the **Reservation Service** (master, global view) with the **Allocation Service** (each execution node, local slots).
- Forgetting that **PAL is the exception**: it is not a service, but everything above it is.
- Confusing **Fabric** (infrastructure management) with **Foundation** (logical management).
- Saying private-cloud nodes are dynamically provisioned. They are mostly **long-lived physical** nodes.
- Public deployment is usually within **one** provider; the **hybrid** diagram shows multiple (AWS, GoGrid).
- Saying Parameter Sweep is independent of the Task Model. It is a **specialization** of it.

---

## 13. Self-Test

1. Which company develops Aneka?
2. Name the three service categories in the container.
3. Which component auto-configures the container at boot?
4. Which OSes does the PAL support?
5. Which service tracks job state transitions?
6. Which two services together make up resource reservation?
7. What does Libra Reservation add?
8. Name the four programming models.
9. What defines a master node?
10. Which node type has the Allocation Service?
11. Name two public IaaS providers in the slides.
12. Which deployment uses Workload Partitioning?

**Answers:** 1) Manjrasoft Pty. Ltd. 2) Fabric, Foundation, Application. 3) PAL's detection engine. 4) Windows, Linux, Mac OS X. 5) Scheduling Service. 6) Resource Reservation + Allocation Service. 7) Different pricing by hardware capability. 8) Task, Thread, MapReduce, Parameter Sweep. 9) Index Service in master mode. 10) Worker. 11) Amazon EC2, GoGrid. 12) Hybrid.

---

## 14. One-Page Last-Minute Summary

- **Aneka** = Manjrasoft's **PaaS middleware**; builds an **Aneka Cloud** (one virtual domain) from heterogeneous resources.
- **SOA**: services are the extension point; plug in new ones dynamically.
- **6 aspects:** Elasticity, Runtime, Resource, Application, User, QoS/SLA & billing.
- **SDK** = develop apps; **Management kit** = manage infra, users, apps.
- **Container** = unit of deployment. Stack: **Application → Foundation → Fabric → PAL**, with **Persistence & Security** across all.
- **PAL**: detection engine, Windows/Linux/Mac OS X, uniform interfaces.
- **Fabric:** provisioning, hardware profiling, membership, monitoring (Heartbeat/Monitoring/Reporting).
- **Foundation:** storage (centralized vs distributed FS), accounting & billing, reservation (Reservation + Allocation; Basic/Libra/Relay).
- **Application:** Scheduling + Execution; models: **Task, Thread, MapReduce, Parameter Sweep**.
- **Infrastructure:** Console + Repository (HTTP/FTP/share) + Node manager + Container.
- **Logical:** Master (Index master, scheduling, reservation, provisioning, accounting, reporting; RDBMS; failover) · Worker (execution, allocation) · Storage (storage service).
- **Deployment:** Private (local, predictable) · Public (EC2/GoGrid, static or dynamic) · **Hybrid (most common, uses everything)**.