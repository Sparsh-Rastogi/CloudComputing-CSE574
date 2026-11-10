"""
Statistical analysis and reporting utilities for CloudBurst.
Computes Wilcoxon signed-rank test in pure Python, normalization relative to HEFT,
win/tie/loss matrices, and ASCII comparison graphs.
"""
import math
from typing import List, Dict, Tuple, Any, Optional


def wilcoxon_signed_rank_test(x: List[float], y: List[float]) -> Tuple[float, float]:
    """
    Computes Wilcoxon signed-rank test for paired samples (pure Python).
    Returns (statistic W, approximate p-value).
    """
    diffs = [a - b for a, b in zip(x, y)]
    # Filter zero differences
    non_zero_diffs = [d for d in diffs if abs(d) > 1e-9]
    n = len(non_zero_diffs)
    if n < 5:
        # Too few non-zero pairs for normal approximation
        w_pos = sum(1 for d in non_zero_diffs if d > 0)
        return float(w_pos), 1.0

    # Rank absolute differences
    abs_diffs = [(abs(d), i, d > 0) for i, d in enumerate(non_zero_diffs)]
    abs_diffs.sort(key=lambda item: item[0])

    # Assign ranks with tie handling
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and abs(abs_diffs[j][0] - abs_diffs[i][0]) < 1e-9:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    # W+ is sum of ranks for positive differences
    w_pos = sum(ranks[k] for k in range(n) if abs_diffs[k][2])
    w_neg = sum(ranks[k] for k in range(n) if not abs_diffs[k][2])
    w = min(w_pos, w_neg)

    # Normal approximation for p-value
    mean_w = n * (n + 1) / 4.0
    var_w = n * (n + 1) * (2 * n + 1) / 24.0
    std_w = math.sqrt(var_w) if var_w > 0 else 1.0

    z = (w - mean_w) / std_w
    # Two-tailed p-value using complementary error function
    p_val = math.erfc(abs(z) / math.sqrt(2.0))
    return w, p_val


def compute_win_tie_loss(
    target_values: List[float],
    baseline_values: List[float],
    lower_is_better: bool = True,
    tol: float = 1e-4,
) -> Tuple[int, int, int]:
    """Computes Win / Tie / Loss count across cases."""
    wins, ties, losses = 0, 0, 0
    for t_val, b_val in zip(target_values, baseline_values):
        diff = t_val - b_val
        if abs(diff) <= tol:
            ties += 1
        elif (diff < 0 and lower_is_better) or (diff > 0 and not lower_is_better):
            wins += 1
        else:
            losses += 1
    return wins, ties, losses


def generate_ascii_bar(val: float, max_val: float, width: int = 25) -> str:
    """Generates a text ASCII progress bar."""
    if max_val <= 0:
        return ""
    ratio = min(1.0, max(0.0, val / max_val))
    filled = int(round(ratio * width))
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {val:.2f}"
