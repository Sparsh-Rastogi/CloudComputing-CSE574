# Virtualization — Study Notes

> Based on: *Virtualization*, Dr. Prasenjit Chanak, Dept. of CSE, IIT (BHU) Varanasi
> Topic: Cloud Computing — Unit 3

---

## Table of Contents
1. [What is Virtualization?](#1-what-is-virtualization)
2. [Benefits of Virtualization](#2-benefits-of-virtualization)
3. [The Virtualization Reference Model (Guest–Host–Virtualization Layer)](#3-the-virtualization-reference-model-guesthostvirtualization-layer)
4. [The Machine Stack: ISA, ABI, API & Privileged Instructions](#4-the-machine-stack-isa-abi-api--privileged-instructions)
5. [**How to Classify Types of Virtualization — the Big Picture**](#5-how-to-classify-types-of-virtualization--the-big-picture)
6. [Axis A — WHAT is Virtualized (Execution / Storage / Network)](#6-axis-a--what-is-virtualized-execution--storage--network)
7. [Axis B — WHERE in the Software Stack (Level of Execution Virtualization)](#7-axis-b--where-in-the-software-stack-level-of-execution-virtualization)
   - 7.1 [Application-Level Virtualization](#71-application-level-virtualization)
   - 7.2 [Programming Language-Level Virtualization](#72-programming-language-level-virtualization)
   - 7.3 [Operating System-Level Virtualization](#73-operating-system-level-virtualization)
   - 7.4 [Hardware-Level Virtualization](#74-hardware-level-virtualization)
8. [Axis C — HOW COMPLETE the Hardware Emulation Is](#8-axis-c--how-complete-the-hardware-emulation-is)
9. [Axis D — WHERE the Hypervisor Sits (Type I vs Type II)](#9-axis-d--where-the-hypervisor-sits-type-i-vs-type-ii)
10. [Hypervisor Internals: Reference Architecture & VMM Properties](#10-hypervisor-internals-reference-architecture--vmm-properties)
11. [Specialized / Purpose-Driven Virtualization (Desktop & App-Server)](#11-specialized--purpose-driven-virtualization-desktop--app-server)
12. [Managed Execution: Sharing, Aggregation, Emulation, Isolation](#12-managed-execution-sharing-aggregation-emulation-isolation)
13. [Virtualization and Cloud Computing (IaaS vs PaaS)](#13-virtualization-and-cloud-computing-iaas-vs-paas)
14. [VM Migration & Server Consolidation](#14-vm-migration--server-consolidation)
15. [Advantages & Disadvantages of Virtualization](#15-advantages--disadvantages-of-virtualization)
16. [Case Studies: VMware & Xen Architecture](#16-case-studies-vmware--xen-architecture)
17. [Quick Revision — Important Exam Questions](#17-quick-revision--important-exam-questions)

---

## 1. What is Virtualization?

- **Virtualization** is a technology that lets you create and manage multiple simulated environments (**Virtual Machines / VMs**) from a single physical hardware system.
- A **Virtual Machine (VM)** is a software-based computer that behaves like a physical one. Each VM has its own:
  - Virtual CPU, Virtual Memory, Virtual Disk, Virtual Network Interface, Guest Operating System
  - Every VM operates **independently** of the others.
- It provides a **secure, customizable, isolated execution environment** — even untrusted applications can run without affecting other users (e.g., a Windows guest VM running on top of a Linux host).
- It enables **elastic scalability** — provisioning extra capacity at minimum cost — and is a **fundamental building block of cloud computing** (especially IaaS).

**Renewed interest in virtualization is driven by:**
- Increased hardware performance/capacity · Underutilized resources · Lack of physical space · Rising administrative costs

> **Diagram:** VM1 (Windows Server), VM2 (Ubuntu), VM3 (CentOS) → run on a **Hypervisor** → which runs on **Physical Hardware** (CPU, RAM, Disk, NIC).

**❓ Exam Questions:** Define virtualization and VM · List the components of a VM · Why has interest in virtualization grown recently?

---

## 2. Benefits of Virtualization

| Benefit | Description | Real-world example |
|---|---|---|
| **Flexibility** | Quickly provision/manage resources on demand (compute, storage, network). | AWS EC2 spinning up a new VM instance in minutes when traffic spikes on an e-commerce site during a sale. |
| **Cost Efficiency** | Less physical hardware needed; better utilization → savings. | A company running 20 lightly-used physical servers consolidates them onto 4 well-utilized hosts via VMware. |
| **Isolation & Security** | Tenants stay isolated from each other → improved stability. | Two competing companies' workloads run as separate VMs on the same physical server in a public cloud (multi-tenancy) without seeing each other's data. |
| **Disaster Recovery** | Rapid replication/restoration of VMs and data. | A hospital's patient-record VM is snapshotted nightly and can be restored on a backup host within minutes after a hardware failure. |

**❓ Exam Question:** Explain any three benefits of virtualization in cloud computing.

---

## 3. The Virtualization Reference Model (Guest–Host–Virtualization Layer)

Every virtualized setup — regardless of type — is built from **three components**:

| Component | Role |
|---|---|
| **Guest** | The system component that interacts with the virtualization layer instead of the host directly. |
| **Host** | The original/physical environment where the guest is actually managed. |
| **Virtualization Layer (VMM)** | Recreates the environment (same or different) in which the guest operates. |

In hardware virtualization specifically: Guest = OS + apps, running on **virtual hardware**; Host = physical hardware (+OS); the layer = **hypervisor**; guests reach the network via a **virtual network** (e.g. VPN).

**❓ Exam Question:** Explain the virtualization reference model with a diagram; differentiate guest, host, and virtualization layer.

---

## 4. The Machine Stack: ISA, ABI, API & Privileged Instructions

Before classifying virtualization types, it helps to know **where** in the computer's layered stack each type inserts itself.

```
 Applications
     │  (API calls)
 Libraries
     │  (System calls)
 Operating System
     │
 Hardware
```

| Interface | Sits Between | Defines |
|---|---|---|
| **ISA** (Instruction Set Architecture) | Hardware ↔ Software | Instruction set, registers, memory, interrupts. |
| **ABI** (Application Binary Interface) | OS ↔ Applications/Libraries | Data types, alignment, calling conventions, executable format, system calls. |
| **API** (Application Programming Interface) | Applications ↔ Libraries/OS | Highest-level abstraction. |

**Privileged vs non-privileged instructions:**
- **Non-privileged**: don't touch shared resources — safe to run freely.
- **Privileged**: sensitive operations, executed under restriction.

> 💡 **Why this matters for classification:** a virtualization technique is defined largely by *which interface it recreates* — ISA (hardware virtualization), ABI (OS-level / process VMs), or API (application-level virtualization). Keep this in mind for Section 7.

**❓ Exam Questions:** Explain ISA, ABI, API with the machine reference model · Differentiate privileged and non-privileged instructions.

---

## 5. How to Classify Types of Virtualization — the Big Picture

Students often get confused because "types of virtualization" are actually sliced along **four independent axes**. A single real-world technology (e.g., Xen) can be described using *all four* axes at once. Use this table as your map:

| Axis | Question it answers | Possible Answers |
|---|---|---|
| **A. What is virtualized?** | Which resource is being abstracted? | Execution environment / Storage / Network *(+ specialized: Desktop, App server)* |
| **B. Where in the stack?** | At which software layer does the virtualization layer sit? | Application-level / Programming-language-level / OS-level / Hardware-level |
| **C. How complete is the emulation?** *(applies only to hardware-level)* | Does the guest need to be modified? Is the whole machine emulated? | Full / Para / Partial / Hardware-Assisted |
| **D. Where does the hypervisor run?** *(applies only to hardware-level)* | Does it run directly on hardware or on top of a host OS? | Type I (Native) / Type II (Hosted) |

So, for example: **Xen** = Execution virtualization (A) → Hardware-level (B) → Paravirtualization (C) → Type I hypervisor (D).

**❓ Exam Question:** "Classify virtualization techniques" — answer using this 4-axis framework rather than a flat list.

---

## 6. Axis A — WHAT is Virtualized (Execution / Storage / Network)

| Category | What it abstracts | Notes | Example |
|---|---|---|---|
| **Execution Virtualization** | An execution environment separate from the one hosting the virtualization layer | Oldest, most popular, most developed. Further split by Axis B (Section 7). | A Windows guest OS running inside a VM on a Linux host via VMware/Xen. |
| **Storage Virtualization** | Decouples the *physical* organization of storage hardware from its *logical* representation | Users access data via a logical path, unaware of physical location. Common technique: **SANs** (Storage Area Networks). | Amazon EBS or a NetApp SAN — you request a "500 GB volume" without knowing which physical disks actually hold it. |
| **Network Virtualization** | Combines hardware appliances + software to build/manage a virtual network | **External**: aggregates physical networks → a single logical network (typically a **VLAN**). **Internal**: gives network-like functionality inside a single OS partition. Guest connects via shared NIC+NAT, an emulated virtual NIC, or a private guest-only network. | External: a company's Finance and HR departments on separate VLANs though wired to the same physical switch. Internal: VirtualBox's "NAT" networking mode for a guest VM sharing the host's single physical NIC. |

**❓ Exam Questions:** Differentiate storage, network, and execution virtualization · Differentiate internal vs external network virtualization.

---

## 7. Axis B — WHERE in the Software Stack (Level of Execution Virtualization)

This is the classification students usually find hardest — four levels, ordered **bottom (closest to hardware) to top (closest to the application)**. Each level recreates a *different interface* from Section 4.

| Level | Interface Recreated | Needs a Hypervisor/VMM? | Guest = | Example | Everyday analogy |
|---|---|---|---|---|---|
| **Hardware-Level** | ISA | Yes — a hypervisor | A full OS | VMware, Xen, Hyper-V, KVM | Installing a whole new "house" (OS) on a plot of virtual land. |
| **OS-Level** | ABI (via OS kernel) | No separate hypervisor — the *host OS kernel itself* isolates instances | Isolated user-space instance (not a full OS) | Docker containers, FreeBSD Jails, Solaris Zones, OpenVZ | Separate, locked "apartments" inside the same building (kernel). |
| **Programming Language-Level** | Byte-code / an abstract ISA defined by the language | Yes — a "process VM" that interprets/JIT-compiles byte code | Compiled byte code | JVM (`.class`/`.jar` files), .NET CLR (`.dll`/`.exe` assemblies) | Same recipe (byte code) followed by any kitchen (any OS) that has the right "chef" (runtime) installed. |
| **Application-Level** | Partial API/library emulation | A thin compatibility layer, not a full VMM | A single application | Wine (running `notepad.exe` on Ubuntu), WABI, CrossOver (running MS Office on macOS) | A translator standing next to one guest, not renovating the whole house. |

> 💡 **Memory trick:** the lower the level, the *heavier* the virtualization (you get a whole OS) and the *stronger* the isolation; the higher the level, the *lighter* it is (you only virtualize what one app needs) and the more implementation-specific it is.

### 7.1 Application-Level Virtualization
- Lets an application run in a runtime that doesn't natively support features it needs — app is not really installed, but runs "as though" it were.
- Works via a **thin layer** that emulates partial file systems, libraries, or OS components.
- For binaries built for a different hardware architecture, this thin layer uses **interpretation** or **binary translation**.
- Useful when host libraries are missing (replacement library linked in, or calls remapped).
- **Lightest** VMM of all four levels — only partial runtime emulation.
- Examples: **Wine** (runs Windows apps on Unix-like OS), **WABI** (Win16 API on Solaris), **CrossOver** (Windows apps on macOS).

### 7.2 Programming Language-Level Virtualization
- A VM executes the **byte code** produced by compiling source code for an abstract architecture.
- History: 1966 — **BCPL** (ancestor of C); also **UCSD Pascal**, **Smalltalk**.
- **JVM**: originally for Java, later extended to Python, Pascal, Groovy, Ruby.
- **.NET / CLI**: supports multiple languages under one runtime.
- Both Java and CLI are **stack-based** VMs; **Parrot** is a **register-based** VM example (originally for Perl).
- Advantages: uniform execution across platforms ("compile once, run anywhere"); security via I/O filtering and sandboxing (pluggable security policies in Java/.NET).

### 7.3 Operating System-Level Virtualization
- Creates isolated execution environments for apps **within a single OS kernel** — **no hypervisor at all.**
- The kernel allows multiple isolated user-space instances and manages resource sharing/limits between them.
- Evolution of Unix's **chroot** mechanism (which changes the file-system root visible to a process and its children).
- Good for **server consolidation** where multiple app servers share the same OS/technology stack.
- Examples: **FreeBSD Jails, IBM LPAR, Solaris Zones/Containers, Parallels Virtuozzo, OpenVZ, FreeVPS**.
- Modern real-world parallel: **Docker containers** work on this same principle — multiple containers share one Linux kernel but see isolated filesystems/processes.

### 7.4 Hardware-Level Virtualization
- Provides an abstract execution environment in terms of computer *hardware*, on top of which a **guest OS** runs.
- Guest = OS; Host = physical hardware; VM = its emulation; VMM = **hypervisor**.
- Also called **system virtualization** — it exposes **ISA** to VMs (vs. process VMs above, which expose ABI/byte-code interfaces).
- This is the richest category — it has its *own* two further sub-classifications, covered in **Axis C** and **Axis D** below.

**❓ Exam Questions:** Order the four levels of execution virtualization from lightest to heaviest and explain why · What is OS-level virtualization and how does it differ from hardware virtualization? · What is application-level virtualization? Give examples · Differentiate stack-based and register-based programming-level VMs.

---

## 8. Axis C — How Complete the Hardware Emulation Is

*(This axis only applies once you're already inside "Hardware-Level Virtualization" from Section 7.4 — it answers: how much of the machine does the hypervisor actually emulate, and does the guest OS need changing?)*

| Type | Guest OS modified? | Emulation completeness | Trade-off | Example |
|---|---|---|---|---|
| **Full Virtualization** | ❌ No — runs unmodified | Complete emulation of the entire underlying hardware | Best isolation & compatibility, but naive full emulation of every instruction costs performance | Achieved efficiently only when combined with hardware-assisted virtualization. E.g., installing an unmodified copy of Windows 11 as a guest inside VMware Workstation or VirtualBox. |
| **Paravirtualization** | ✅ Yes — guest is modified | Partial — exposes a *slightly different* interface than the real host | Faster (performance-critical ops go straight to host) but **not transparent** — needs a specially ported guest | **Xen** (Linux guests ported to Xen); also VMware, Parallels, TRANGO, Wind River, XtratuM. E.g., a Xen-aware Linux kernel making a `hypercall` instead of a normal system call for disk I/O. |
| **Partial Virtualization** | Depends | Partial emulation — guest cannot run in complete isolation; not all OS features supported | Historically a stepping stone to full virtualization | Address-space virtualization in time-sharing systems; experimental **IBM M44/44X**. E.g., early Unix `chroot`-like environments where processes shared the same CPU/disk but had separate memory address spaces. |
| **Hardware-Assisted Virtualization** | ❌ No | Hardware itself gives architectural support to the VMM (so software doesn't have to emulate everything) | Removes most of the "full virtualization" performance penalty | **Intel VT**, **AMD-V** (originally pioneered on **IBM System/370**); used by KVM, VirtualBox, Xen, VMware, Hyper-V after 2006. E.g., a laptop's BIOS/UEFI setting called "Intel VT-x" that must be enabled before VirtualBox/WSL2 will run. |

> 💡 Full vs Para is really a **transparency vs performance** trade-off: Full virtualization keeps the guest untouched (transparent) but costs more to emulate; Paravirtualization sacrifices transparency (guest must be ported) to gain speed. Hardware-assisted virtualization is what let vendors get *both* — a mostly-transparent guest **and** good performance, by moving support into the CPU itself.

**❓ Exam Questions:** Differentiate full, para, and partial virtualization — specifically on *guest modification* and *emulation completeness* · Why was hardware-assisted virtualization introduced, and what problem does it solve? · Name the real x86 technologies that enable hardware-assisted virtualization.

---

## 9. Axis D — Where the Hypervisor Sits (Type I vs Type II)

*(This is a second, independent axis within "Hardware-Level Virtualization" — it answers: does the hypervisor talk to hardware directly, or through a host OS?)*

| Type | Also called | Runs on | Talks to hardware via | Example | Where you'd see it |
|---|---|---|---|---|---|
| **Type I** | Native / Bare-metal hypervisor | Directly on hardware — *takes the place of* the OS | **ISA** directly | VMware ESXi, Xen, Microsoft Hyper-V, KVM | A data-center server rack that boots straight into ESXi with no separate "host OS" — used by cloud providers like AWS, Azure, GCP. |
| **Type II** | Hosted hypervisor | On top of a host operating system | **ABI** (through the host OS), which in turn emulates ISA for the guest | VMware Workstation, Oracle VirtualBox, Parallels Desktop | A developer's laptop running Windows, with VirtualBox installed as a normal app, used to run an Ubuntu VM for testing. |

> 💡 Note how Axis D reuses the ISA/ABI vocabulary from Section 4: a **Type I** hypervisor stands where the OS normally would (talking ISA to the hardware); a **Type II** hypervisor stands where a normal application would (talking ABI to the host OS).

**❓ Exam Questions:** Differentiate Type I and Type II hypervisors with a diagram and real examples · Why is a Type I hypervisor generally faster than a Type II hypervisor?

---

## 10. Hypervisor Internals: Reference Architecture & VMM Properties

**Three modules of a hypervisor** coordinate to emulate the underlying hardware:

1. **Dispatcher** — entry point; reroutes instructions from the VM to the allocator or interpreter.
2. **Allocator** — decides what system resources are given to the VM (invoked by the dispatcher).
3. **Interpreter** — a set of routines triggered (via a trap) whenever the VM executes a **privileged instruction**.

**Three properties every VMM must satisfy:**
1. **Equivalence**
2. **Resource Control**
3. **Efficiency**

**❓ Exam Questions:** Explain the hypervisor reference architecture (dispatcher, allocator, interpreter) · List the three properties a VMM must satisfy.

---

## 11. Specialized / Purpose-Driven Virtualization (Desktop & App-Server)

These don't fit neatly into Axis A–D above — they're defined by their **business purpose** rather than the mechanism used:

| Type | Purpose | Description | Example |
|---|---|---|---|
| **Desktop Virtualization** | Remote access to a personal desktop | Abstracts a desktop environment for **client/server** access — the system is remote but appears local. Examples: Sun VDI, Parallels VDI, Citrix XenDesktop. | A bank employee logs into a thin client each morning; their actual "desktop" (files, apps, settings) is really running on a server in the data center and just streamed to the screen. |
| **Application Server Virtualization** | Quality of service, not emulation | Abstracts a *collection* of application servers into one virtual server, using **load balancing** + **high availability**. Same underlying goal as storage virtualization — QoS, not creating a different environment. | An online food-delivery app's backend has 10 identical application-server instances behind a load balancer (like NGINX or AWS ELB); users hitting the API never know (or care) which physical/virtual server actually answered. |

**❓ Exam Questions:** How does desktop virtualization differ in purpose from hardware virtualization even though the mechanism looks similar? · What is the goal of application server virtualization?

---

## 12. Managed Execution: Sharing, Aggregation, Emulation, Isolation

> **Diagram (Fig 3.2):** maps Physical Resources → Virtualization function → Virtual Resources.

| Function | What it does | Example |
|---|---|---|
| **Sharing** | Creates separate environments within the *same* host, fully exploiting a powerful guest's capacity. Key in data centers to cut active-server count and power use. | One powerful 64-core physical server hosts 15 separate customer VMs instead of buying 15 separate small servers. |
| **Aggregation** | The opposite of sharing — ties multiple *separate* hosts together and presents them to guests as a **single** virtual host (e.g., cluster management software). | A Hadoop/Spark cluster of 50 physical machines presented to a data-processing job as one giant "virtual computer." |
| **Emulation** | Lets guest programs run with characteristics not physically present on the host (e.g., emulating a SCSI device) — very useful for testing. | Running an Android emulator on a desktop PC to test a mobile app, even though the PC has no ARM chip or touchscreen. |
| **Isolation** | Gives each guest a completely separate environment so multiple guests don't interfere with each other. | Two VMs on the same host — one gets compromised by malware, but the other VM (and the host) remains completely unaffected. |

**❓ Exam Questions:** Explain sharing and aggregation as opposite functions of managed execution · What is emulation in managed execution, with an example · Why is isolation critical in virtualized environments?

---

## 13. Virtualization and Cloud Computing (IaaS vs PaaS)

- Virtualization gives the customization, security, isolation, and manageability needed to deliver IT services on demand.
- Mainly used to offer **configurable computing environments and storage**; network virtualization is comparatively a complementary feature.

| Cloud Layer | Enabled by | Why |
|---|---|---|
| **IaaS** | **Hardware virtualization** | Delivers customizable, sandboxed virtual machines directly to customers |
| **PaaS** | **Programming language virtualization** | Delivers a customizable, sandboxed *runtime* (e.g., JVM/.NET) rather than a full VM |

Both create an attractive business opportunity for large-infrastructure providers, and enable finer control → simplifying service leasing/accountability, and efficient design via **consolidation** (transparent to end users).

**❓ Exam Questions:** How does virtualization enable IaaS and PaaS? · Why is programming-language virtualization more relevant to PaaS than to IaaS?

---

## 14. VM Migration & Server Consolidation

- **Server consolidation**: reduce the number of active physical resources by aggregating VMs onto fewer, fully-utilized hosts — attractive when resources are underused.
- **VM Migration**: moving VM instances between physical hosts.
  - **Cold/offline migration** — stop execution, move data, resume.
  - **Live migration** — move the *running* instance with finer control; more complex, but more efficient (no disruption).
- Mainly used with **hardware virtualization**, though technically possible with programming-language virtualization too.

> **Diagram (Fig 3.10):** Before migration — VMs spread across Server A & B. After migration — all VMs consolidated on Server A; Server B becomes inactive.

**❓ Exam Questions:** What is live migration and how does it differ from cold migration? · Explain server consolidation with a diagram.

---

## 15. Advantages & Disadvantages of Virtualization

### ✅ Advantages
- **Managed execution & isolation** — secure, controllable, sandboxed environments; simplified resource allocation.
- **Portability** — VM instances = files, easily moved; "compile once, run everywhere" (Java); fewer physical hosts than VM instances → lower maintenance cost.
- **Efficient resource use**.

### ❌ Disadvantages

**a) Performance Degradation**
- The abstraction layer between guest and host adds latency: maintaining virtual-processor state, trapping/simulating privileged instructions, supporting paging within the VM and console functions.
- The VMM competes for host resources with other applications.
- Binary translation/interpretation slows programming-level VMs (JVM, .NET) — mitigated by native-code compilation.

**b) Inefficiency & Degraded User Experience**
- Host-specific features can become inaccessible through the abstraction layer (e.g., a generic default graphics card instead of the host's real GPU).
- Early Java had poor GUI support — later resolved with the **Swing** framework and **OpenGL** SDK integration.

**c) Security Holes & New Threats**
- Transparent emulation opens the door to new malware: **BluePill** (targets AMD, moves the installed OS into a VM) and **SubVirt** (infects the guest OS, takes control of the host on reboot).
- Intel VT and AMD Pacifica added hardware support to counter such threats.
- Similarly, a modified JVM/.NET runtime can spy on memory if malware gains admin access or exploits a host security hole.

**❓ Exam Questions:** Discuss the performance-related disadvantages of virtualization · Explain BluePill and SubVirt as virtualization-based security threats · How was the degraded-GUI issue in early Java VMs eventually solved?

---

## 16. Case Studies: VMware & Xen Architecture

### VMware Workstation — Type II (Hosted)
- User apps + VMware Workstation run atop the **Host OS**; a **VMware driver** talks to the **VMware Hypervisor (VMM)**.
- VMM directly accesses hardware, manages I/O/memory/networking for guests, saves/restores host CPU state.
- Guest OS + apps run inside the **Virtual Machine Instance**.

### VMware ESXi — Type I (Native/Bare-metal)
- The **VMkernel** runs directly on hardware.
- Includes Resource Scheduling, Device Drivers, Storage Stack, Network Stack, Distributed VM File System, Virtual Ethernet Adapter & Switch.
- Each VM gets its own **VMM**; managed via hostd, DCUI, syslog, SNMP, CIM Broker, etc.

### VMware Cloud Solution Stack
Layered top→bottom: **Zimbra** (Application Virtualization) → **vFabric** (Platform Virtualization) → **vCloud → vCenter → vSphere → ESXi/ESX → Server → Data Center → Cloud** (Infrastructure Virtualization).

### Xen — Type I hypervisor + Paravirtualization
Uses x86 protection rings (Ring 0 – Ring 3):
- **Xen Hypervisor (VMM)** — Ring 0: memory management, CPU state registers, device I/O; interacts with hardware via traps.
- **Domain 0 (Management Domain)** — privileged domain: VM management, HTTP interface, access to Xen hypervisor.
- **Domain U (User Domains)** — guest OS with a **modified codebase**, making **hypercalls** into the Xen VMM — this *is* paravirtualization in action.
- **User Application** — runs with an unmodified ABI on top of the guest OS.

**❓ Exam Questions:** Compare VMware Workstation (Type II) and ESXi (Type I) architectures · Explain Xen's paravirtualization using its ring-based architecture and the roles of Domain 0 / Domain U.

---

## 17. Quick Revision — Important Exam Questions

**Foundational**
1. Define virtualization and explain its role in cloud computing.
2. Explain the guest–host–virtualization-layer reference model.
3. Explain ISA, ABI, API and privileged vs non-privileged instructions.

**Classification (most commonly confused topic)**
4. Explain the four axes used to classify virtualization techniques.
5. What is virtualized — execution, storage, or network? Differentiate them.
6. Order the four *levels* of execution virtualization (application → programming language → OS → hardware) and explain the trend in isolation strength vs weight.
7. Differentiate full, para, and partial virtualization on the basis of guest modification and emulation completeness.
8. Differentiate Type I and Type II hypervisors.

**Mechanism / Internals**
9. Explain the hypervisor reference architecture (dispatcher, allocator, interpreter).
10. List the three properties a VMM must satisfy.
11. Explain managed execution's four functions: sharing, aggregation, emulation, isolation.

**Applied / Cloud Context**
12. How does virtualization enable IaaS vs PaaS?
13. Explain server consolidation and live migration.
14. List advantages and disadvantages of virtualization, with the three main disadvantage categories.
15. Explain BluePill and SubVirt as virtualization security threats.

**Case Studies**
16. Compare VMware Workstation and ESXi architectures.
17. Explain Xen's paravirtualization model using Domain 0/Domain U and hypercalls.

---

*Compiled from lecture slides on Virtualization by Dr. Prasenjit Chanak, IIT (BHU) Varanasi.*