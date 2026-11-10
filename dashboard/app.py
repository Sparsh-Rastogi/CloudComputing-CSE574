"""
Streamlit implementation of the IEEE Research Paper Dashboard.
Run with: streamlit run dashboard/app.py
"""
import os
import json
import pandas as pd

try:
    import streamlit as st
except ImportError:
    print("Streamlit is not installed. To run the Streamlit version: pip install streamlit")
    exit(0)

st.set_page_config(
    page_title="DD-HPSO: IEEE Research Paper Dashboard",
    page_icon="📄",
    layout="wide",
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")
if not os.path.exists(DATA_PATH):
    st.error(f"Data file not found at {DATA_PATH}. Please run dashboard/prepare_dashboard_data.py first.")
    st.stop()

with open(DATA_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

# IEEE Paper Header Styling
st.markdown("""
<div style="text-align: center; border-bottom: 2px solid #002855; padding-bottom: 10px; margin-bottom: 20px;">
  <div style="font-size: 11px; font-weight: bold; letter-spacing: 1.5px; color: #002855; text-transform: uppercase;">
    IEEE Transactions on Cloud Computing — Special Issue Research Paper
  </div>
  <h1 style="font-size: 26px; font-weight: bold; color: #002855; margin-top: 10px; font-family: serif;">
    DD-HPSO: Deadline-Aware, Duplication-Enabled, HEFT-Seeded Particle Swarm Optimization for Cost and Energy Efficient Scientific Workflow Scheduling on IaaS Clouds
  </h1>
  <div style="font-size: 15px; font-weight: 600; color: #222; margin-top: 8px;">
    Sparsh Rastogi (24095072) &nbsp;&bull;&nbsp; Nisha Mittal (24095071)
  </div>
  <div style="font-size: 13px; color: #555; font-style: italic;">
    Department of Computer Science & Engineering, CSE-574 Cloud Computing
  </div>
  <div style="display: inline-block; margin-top: 8px; background: #eef4fa; color: #002855; padding: 4px 14px; border-radius: 12px; font-size: 12px; font-weight: 600; border: 1px solid #c9dcf0;">
    Under the Guidance of: Dr. Prasenjit Chanak
  </div>
</div>
""", unsafe_allow_html=True)

# Abstract
st.markdown("""
<div style="background: #fbfbfd; border-left: 4px solid #002855; padding: 12px 18px; margin-bottom: 20px; font-size: 13px; line-height: 1.6; border: 1px solid #e1e4e8;">
  <strong>Abstract—</strong> Scientific workflow scheduling on IaaS clouds poses a challenging multi-objective problem where execution makespan, monetary cost, and energy must be minimized under strict deadlines. While list heuristics (HEFT, HEFT-TD) compress makespan, they often increase monetary rental costs (+15% to +45%). Conversely, metaheuristics (PSO) suffer from high run-to-run variability and deadline violations under tight constraints. We propose <strong>DD-HPSO</strong>, which combines topological HEFT seeding, Deb's feasibility rules, sub-deadline triggers, and zero-cost/energy-capped selective duplication (&theta;<sub>C</sub> = 0, &theta;<sub>E</sub> &le; 5%). Evaluated across 21 benchmark cases and 1,323 runs, DD-HPSO achieves <strong>100.0% deadline feasibility</strong>, cuts monetary cost by <strong>8.9%</strong> and energy by <strong>6.8%</strong> vs HEFT/HEFT-TD, and outperforms recent 2025/2026 baselines with statistical significance.
</div>
""", unsafe_allow_html=True)

# Tabs
t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "Tab 1: I. Overview & Intro",
    "Tab 2: II. Scientific Workflows",
    "Tab 3: III. Cloud Environment",
    "Tab 4: IV. Benchmark Results & Gantt",
    "Tab 5: V. Proposed DD-HPSO",
    "Tab 6: VI. Analysis & Conclusion",
    "Tab 7: VII. References"
])

with t1:
    st.subheader("I. Introduction & Literature Context")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### Motivation & Problem
        Commercial IaaS clouds present four core characteristics:
        1. **Heterogeneity**: VMs offer varying speed, pricing, and power draw.
        2. **Quantized Billing**: Rent is billed in discrete periods ($\tau = 3600$s), where partial periods are rounded up.
        3. **Boot Delay**: Provisioning adds $\beta = 97$s delay billed as idle energy.
        4. **Data Transfers**: Data exchanges between VMs stall child tasks.
        
        The objective is finding an offline task-to-VM mapping satisfying $M \le D$ while minimizing Cost $C$ and Energy $E$.
        """)
    with c2:
        st.markdown("""
        ### The Combined Research Gap
        • **Genez et al. (UCC 2018) [1]**: HEFT-TD duplicates parents to cut makespan, but is deadline-unaware and inflates costs (+10% to +45%).
        • **Rodriguez & Buyya (TCC 2014) [2]**: Cost-only PSO with Deb's rules under hourly billing, but lacks energy/duplication and has high run variability.
        • **Li et al. (TSC 2018, CEAS) [3]**: Greedy heuristic with sub-makespans and task merging, but relies on DVFS hardware control unavailable on public IaaS.
        
        **DD-HPSO fills this gap** by uniting heuristic seeding, selective duplication, hourly billing, and tenant-side energy tracking.
        """)

with t2:
    st.subheader("II. Scientific Workflows Characterization")
    st.markdown("""
    Workflows are modeled as DAGs $G = (T, E)$. We evaluated 7 standard Pegasus DAX workflows:
    - **Montage (50, 100)**: Sky mosaicking. High CCR (1.6); I/O intensive. Task duplication yields high gains.
    - **CyberShake (50, 100)**: Earthquake hazard simulation. Massive initial data transfers (>10GB) followed by synthesis.
    - **Epigenomics (100)**: Genome sequencing. Extremely compute-heavy (makespan >7,400s), very low CCR. Duplication has negligible impact.
    - **Inspiral (50, 100)**: Gravitational wave analysis (LIGO). Multi-stage pipeline with strict synchronization.
    """)

with t3:
    st.subheader("III. Cloud Simulation Environment & Constraints")
    st.markdown("""
    - **VM Catalog**: Small (1.0x, $0.10/h, 50W/30W), Medium (2.0x, $0.20/h, 90W/54W), Large (4.0x, $0.40/h, 160W/96W), XLarge (8.0x, $0.80/h, 300W/180W).
    - **Pool**: 20 VMs fixed pool (5 per type) (Decision D4).
    - **Boot Delay**: $\beta = 97$s (Decision D6).
    - **Billing Period**: $\tau = 3600$s ceil rounded per VM (Decision D7).
    - **Network**: Inter-VM bandwidth $B = 100$ MB/s; 0 on same VM (Decision D8).
    - **Energy**: $E = \sum (P_{busy} \cdot T_{busy} + P_{idle} \cdot T_{idle})$ (Decision D10).
    """)

with t4:
    st.subheader("IV. Empirical Performance & Schedule Explorer")
    case_keys = list(db["cases"].keys())
    selected_case = st.selectbox("Select Test Case:", case_keys)
    case_data = db["cases"][selected_case]

    colA, colB, colC, colD = st.columns(4)
    dd_metrics = case_data["algorithms"]["DD-HPSO"]
    colA.metric("Deadline", f"{case_data['deadline']:.1f} s")
    colB.metric("DD-HPSO Makespan", f"{dd_metrics['makespan']:.1f} s")
    colC.metric("DD-HPSO Cost", f"${dd_metrics['cost']:.2f}" if dd_metrics['cost'] else "N/A")
    colD.metric("Success Rate", f"{dd_metrics['deadline_met_pct']:.0f}%")

    st.markdown("### Comparative Performance Table")
    df_case = pd.DataFrame(case_data["algorithms"]).T
    st.dataframe(df_case[["makespan", "cost", "energy", "utilization", "deadline_met_pct", "runtime_s"]])

with t5:
    st.subheader("V. Proposed DD-HPSO Methodology")
    st.markdown("""
    1. **HEFT Seeding**: Particle 1 initialized with HEFT mapping. Particles 2..N initialized as mutated copies ($p_{mut} = 0.1$).
    2. **Sub-Deadlines**: $SD_i = AFT_{HEFT}(i) \cdot \frac{D}{M_{HEFT}}$. Duplication attempted only when $AFT_{old}(i) > SD_i$.
    3. **Duplication Filter**: Critical parent $p^*$ duplicated only if $\Delta C \le 0$ ($\theta_C = 0$) and $\Delta E \le 0.05 \cdot E_{ref}$.
    4. **Fitness**: Normalized multi-objective $F = \frac{1}{3} \frac{C}{C_{ref}} + \frac{1}{3} \frac{E}{E_{ref}} + \frac{1}{3} \frac{M}{M_{ref}}$ with Deb's rules.
    """)

with t6:
    st.subheader("VI. Results Analysis & Conclusion")
    st.markdown("""
    ### Key Findings
    - **100% Feasibility**: DD-HPSO met deadlines in 100% of cases, outperforming unseeded metaheuristics (Plain PSO 73.8%, Rodriguez PSO 61.4%).
    - **Makespan & Cost Harmony**: Matches HEFT's makespan within 2.3% while cutting cost by 8.9% and energy by 6.8%.
    - **Trade-offs**: On relaxed deadlines ($D = 2.0\times$), pure cost heuristics (WPSO, PACM) downscale to Small VMs for lower cost, whereas DD-HPSO protects makespan.
    """)

with t7:
    st.subheader("VII. References & Bibliography")
    st.markdown("""
    1. T. Genez et al., IEEE/ACM UCC 2018 (Task Duplication).
    2. M. A. Rodriguez & R. Buyya, IEEE TCC 2014 (PSO Cloud Scheduling).
    3. Z. Li et al., IEEE TSC 2018 (CEAS Algorithm).
    4. G. Wang et al., IEEE ICCCBDA 2025 (WPSO).
    5. S. Awad et al., Scientific Reports 2026 (IPSO-GWO).
    6. L. Cheng et al., IEEE TCC 2025 (PACM).
    7. H. Topcuoglu et al., IEEE TPDS 2002 (HEFT).
    """)
