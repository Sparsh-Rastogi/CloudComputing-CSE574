"""Workflow DAG model and Pegasus DAX XML parser."""
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict, Set


@dataclass
class Workflow:
    name: str
    n: int
    length: List[float]                       # L_i (seconds on speed 1.0)
    parents: List[List[Tuple[int, float]]]    # parents[i] = [(parent_idx, data_bytes), ...]
    children: List[List[Tuple[int, float]]]   # children[i] = [(child_idx, data_bytes), ...]
    order: List[int] = field(default_factory=list)      # topological order (by descending upward rank)
    task_names: List[str] = field(default_factory=list) # original job IDs (e.g., "ID00000")

    def compute_upward_ranks(self, avg_speed: float = 3.75, bandwidth: float = 1e8) -> List[float]:
        """
        Computes HEFT upward rank (rank_u) for all tasks.
        Default avg_speed is mean of catalog speeds (1+2+4+8)/4 = 3.75.
        rank_u(i) = avg_comp(i) + max_{j in succ(i)} (comm_time(i, j) + rank_u(j))
        """
        ranks = [0.0] * self.n

        # Find in-degrees / topological reverse traversal
        # A task's children must be computed before the task
        out_degree = [len(self.children[i]) for i in range(self.n)]
        ready = [i for i in range(self.n) if out_degree[i] == 0]

        # Queue-based backward traversal
        parent_out_count = list(out_degree)
        while ready:
            curr = ready.pop(0)
            avg_comp = self.length[curr] / avg_speed
            max_succ = 0.0
            for child_idx, data_bytes in self.children[curr]:
                comm = data_bytes / bandwidth
                val = comm + ranks[child_idx]
                if val > max_succ:
                    max_succ = val
            ranks[curr] = avg_comp + max_succ

            for p_idx, _ in self.parents[curr]:
                parent_out_count[p_idx] -= 1
                if parent_out_count[p_idx] == 0:
                    ready.append(p_idx)

        return ranks

    def compute_heft_order(self, avg_speed: float = 3.75, bandwidth: float = 1e8) -> List[int]:
        """
        Computes HEFT scheduling order: sorted by non-increasing rank_u.
        Ties broken by lowest task index (Decision D26).
        """
        ranks = self.compute_upward_ranks(avg_speed, bandwidth)
        # Sort descending by rank, ascending by task index
        indexed_ranks = [(ranks[i], -i, i) for i in range(self.n)]
        indexed_ranks.sort(reverse=True)
        return [item[2] for item in indexed_ranks]


def parse_dax_xml(xml_path: str, avg_speed: float = 3.75, bandwidth: float = 1e8) -> Workflow:
    """
    Parses a Pegasus DAX XML file into a Workflow instance.
    Handles exact file matching as well as parent output file fallback.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # Check for DAX namespace
    ns = ""
    if "}" in root.tag:
        ns = root.tag.split("}")[0] + "}"

    jobs = root.findall(f"{ns}job")
    n = len(jobs)

    job_id_to_idx: Dict[str, int] = {}
    task_names: List[str] = []
    lengths: List[float] = [0.0] * n
    job_outputs: Dict[str, Dict[str, float]] = {}
    job_inputs: Dict[str, Dict[str, float]] = {}

    for idx, job in enumerate(jobs):
        jid = job.get("id")
        job_id_to_idx[jid] = idx
        task_names.append(jid)
        runtime = float(job.get("runtime", 0.0))
        lengths[idx] = max(0.001, runtime)

        # Uses tags
        inputs = {}
        outputs = {}
        for use in job.findall(f"{ns}uses"):
            fname = use.get("file")
            link = use.get("link")
            size = float(use.get("size", 0.0))
            if link == "input":
                inputs[fname] = size
            elif link == "output":
                outputs[fname] = size

        job_inputs[jid] = inputs
        job_outputs[jid] = outputs

    parents: List[List[Tuple[int, float]]] = [[] for _ in range(n)]
    children: List[List[Tuple[int, float]]] = [[] for _ in range(n)]

    # Parse dependencies
    for child in root.findall(f"{ns}child"):
        cid = child.get("ref")
        if cid not in job_id_to_idx:
            continue
        c_idx = job_id_to_idx[cid]

        for p in child.findall(f"{ns}parent"):
            pid = p.get("ref")
            if pid not in job_id_to_idx:
                continue
            p_idx = job_id_to_idx[pid]

            # Calculate data bytes transferred
            shared_files = set(job_outputs[pid].keys()) & set(job_inputs[cid].keys())
            if shared_files:
                data_bytes = sum(job_outputs[pid][f] for f in shared_files)
            else:
                # Fallback: total parent output size if non-empty, else total child input size
                p_out = sum(job_outputs[pid].values())
                data_bytes = p_out

            parents[c_idx].append((p_idx, data_bytes))
            children[p_idx].append((c_idx, data_bytes))

    import os
    wf_name = os.path.splitext(os.path.basename(xml_path))[0]
    wf = Workflow(
        name=wf_name,
        n=n,
        length=lengths,
        parents=parents,
        children=children,
        task_names=task_names
    )
    wf.order = wf.compute_heft_order(avg_speed=avg_speed, bandwidth=bandwidth)
    return wf
