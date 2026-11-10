"""
Prepares structured aggregated data for the IEEE Paper Dashboard.
Reads results/raw_results.json and creates dashboard/data.json.
"""
import os
import sys
import json
import math
from collections import defaultdict

sys.path.insert(0, os.path.abspath("."))
from src.cloudburst.stats.analysis import wilcoxon_signed_rank_test, compute_win_tie_loss

os.makedirs("dashboard", exist_ok=True)

with open("results/raw_results.json", "r", encoding="utf-8") as f:
    raw_results = json.load(f)

all_algos = ["HEFT", "Plain PSO", "HEFT-TD", "Rodriguez PSO", "CEAS", "WPSO", "IPSO-GWO", "PACM", "DD-HPSO"]
all_cases = sorted(list({(r["workflow"], r["deadline_factor"]) for r in raw_results}))

# Group by (case_key, algo)
grouped = defaultdict(list)
case_info = {}
for r in raw_results:
    ckey = f"{r['workflow']}|D{r['deadline_factor']:.1f}"
    grouped[(ckey, r["algorithm"])].append(r)
    if ckey not in case_info:
        case_info[ckey] = {
            "workflow": r["workflow"],
            "size": r["size"],
            "deadline_factor": r["deadline_factor"],
            "deadline": r["deadline"]
        }

# Reference HEFT per case
case_refs = {}
for ckey, info in case_info.items():
    heft_runs = grouped[(ckey, "HEFT")]
    if heft_runs:
        case_refs[ckey] = {
            "makespan": heft_runs[0]["makespan"],
            "cost": heft_runs[0]["cost"],
            "energy": heft_runs[0]["energy"],
            "deadline": info["deadline"]
        }

# Overall summary per algorithm
overall_summary = {}
for algo in all_algos:
    m_list, c_list, e_list, u_list, t_list, feas_list = [], [], [], [], [], []
    norm_m, norm_c, norm_e = [], [], []
    for (wf, df) in all_cases:
        ckey = f"{wf}|D{df:.1f}"
        runs = grouped[(ckey, algo)]
        ref = case_refs[ckey]
        for r in runs:
            m_list.append(r["makespan"])
            u_list.append(r["utilization"])
            t_list.append(r["runtime_s"])
            feas = 1.0 if r["deadline_met"] else 0.0
            feas_list.append(feas)
            norm_m.append(r["makespan"] / ref["makespan"])
            if r["deadline_met"]:
                c_list.append(r["cost"])
                e_list.append(r["energy"])
                norm_c.append(r["cost"] / ref["cost"])
                norm_e.append(r["energy"] / ref["energy"])

    overall_summary[algo] = {
        "makespan_mean": round(sum(m_list) / len(m_list), 2) if m_list else 0.0,
        "norm_makespan": round(sum(norm_m) / len(norm_m), 3) if norm_m else 1.0,
        "cost_mean": round(sum(c_list) / len(c_list), 2) if c_list else None,
        "norm_cost": round(sum(norm_c) / len(norm_c), 3) if norm_c else None,
        "energy_mean": round(sum(e_list) / len(e_list), 1) if e_list else None,
        "norm_energy": round(sum(norm_e) / len(norm_e), 3) if norm_e else None,
        "util_mean": round(sum(u_list) / len(u_list) * 100.0, 1) if u_list else 0.0,
        "success_rate": round(sum(feas_list) / len(feas_list) * 100.0, 1) if feas_list else 0.0,
        "runtime_mean": round(sum(t_list) / len(t_list), 4) if t_list else 0.0,
    }

# Head-to-head WTL and Wilcoxon
wtl = {}
wilcoxon = {}
for algo in all_algos:
    if algo == "DD-HPSO":
        continue
    dd_m, ot_m = [], []
    dd_c, ot_c = [], []
    dd_e, ot_e = [], []
    for (wf, df) in all_cases:
        ckey = f"{wf}|D{df:.1f}"
        runs_dd = grouped[(ckey, "DD-HPSO")]
        runs_ot = grouped[(ckey, algo)]
        dd_m.append(sum(r["makespan"] for r in runs_dd) / len(runs_dd))
        ot_m.append(sum(r["makespan"] for r in runs_ot) / len(runs_ot))

        dd_f = [r for r in runs_dd if r["deadline_met"]]
        ot_f = [r for r in runs_ot if r["deadline_met"]]
        if dd_f and ot_f:
            dd_c.append(sum(r["cost"] for r in dd_f) / len(dd_f))
            ot_c.append(sum(r["cost"] for r in ot_f) / len(ot_f))
            dd_e.append(sum(r["energy"] for r in dd_f) / len(dd_f))
            ot_e.append(sum(r["energy"] for r in ot_f) / len(ot_f))

    wm, tm, lm = compute_win_tie_loss(dd_m, ot_m, lower_is_better=True)
    wc, tc, lc = compute_win_tie_loss(dd_c, ot_c, lower_is_better=True) if dd_c else (0, 0, 0)
    we, te, le = compute_win_tie_loss(dd_e, ot_e, lower_is_better=True) if dd_e else (0, 0, 0)

    wtl[algo] = {
        "makespan": f"{wm}/{tm}/{lm}",
        "cost": f"{wc}/{tc}/{lc}",
        "energy": f"{we}/{te}/{le}"
    }
    w_m, p_m = wilcoxon_signed_rank_test(dd_m, ot_m)
    wilcoxon[algo] = {"p_makespan": round(p_m, 4)}

# Cases breakdown
cases_dict = {}
for (wf, df) in all_cases:
    ckey = f"{wf}|D{df:.1f}"
    info = case_info[ckey]
    case_entry = {
        "case_id": ckey,
        "workflow": wf,
        "size": info["size"],
        "deadline_factor": df,
        "deadline": info["deadline"],
        "algorithms": {}
    }

    for algo in all_algos:
        runs = grouped[(ckey, algo)]
        if not runs:
            continue
        feas_runs = [r for r in runs if r["deadline_met"]]
        sched = []
        # Find schedule from median run
        for r in runs:
            if "schedule" in r and r["schedule"]:
                sched = r["schedule"]
                break

        case_entry["algorithms"][algo] = {
            "makespan": round(sum(r["makespan"] for r in runs) / len(runs), 2),
            "cost": round(sum(r["cost"] for r in feas_runs) / len(feas_runs), 2) if feas_runs else None,
            "energy": round(sum(r["energy"] for r in feas_runs) / len(feas_runs), 1) if feas_runs else None,
            "utilization": round(sum(r["utilization"] for r in runs) / len(runs) * 100.0, 1),
            "deadline_met_pct": round(len(feas_runs) / len(runs) * 100.0, 1),
            "runtime_s": round(sum(r["runtime_s"] for r in runs) / len(runs), 4),
            "schedule": sched
        }
    cases_dict[ckey] = case_entry

final_payload = {
    "metadata": {
        "title": "DD-HPSO: Deadline-Aware, Duplication-Enabled, HEFT-Seeded Particle Swarm Optimization for Cost and Energy Efficient Scientific Workflow Scheduling on IaaS Clouds",
        "authors": ["Sparsh Rastogi", "Nisha Mittal"],
        "advisor": "Dr. Prasenjit Chanak",
        "course": "CSE-574 Cloud Computing",
        "total_cases": len(all_cases),
        "total_runs": len(raw_results),
        "algorithms": all_algos,
    },
    "overall_summary": overall_summary,
    "wtl": wtl,
    "wilcoxon": wilcoxon,
    "cases": cases_dict,
}

with open("dashboard/data.json", "w", encoding="utf-8") as f:
    json.dump(final_payload, f, indent=2)

print("Saved dashboard/data.json successfully. Size:", os.path.getsize("dashboard/data.json"), "bytes")
