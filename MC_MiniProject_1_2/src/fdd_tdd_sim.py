"""
Mobile Communications Mini Project 1.2
Comparing FDD and TDD Resource Utilization Under Traffic Asymmetry

Author: <your names>
Course: Mobile Communications — Unit 1 Lab
Reference: MC-MP_Unit1.pdf, Mini Project 1.2, Section 1.8

Implements:
  * FDD model: two fixed paired channels, symmetric per-direction capacity.
  * TDD model: one channel, time-divided into slots, guard-period overhead,
    DL/UL slot ratio configurable per scenario.
  * Three asymmetry scenarios (50:50, 70:30, 90:10).
  * Guard-period sensitivity sweep for TDD.
  * Comparison charts: utilization, throughput, guard sensitivity.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, asdict
from typing import List, Tuple

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
B_TOTAL_MHZ = 100.0          # total system bandwidth for BOTH schemes
SLOTS_PER_FRAME = 20         # TDD frame structure
GUARD_SLOTS_DEFAULT = 1      # default guard overhead
REFERENCE_BPS_PER_HZ = 1.0   # spectral efficiency assumption (Shannon-agnostic)


# ---------------------------------------------------------------------------
# Scenario definition
# ---------------------------------------------------------------------------

@dataclass
class AsymmetryScenario:
    label: str
    dl_fraction: float       # e.g. 0.80 for 80:20 DL:UL volume ratio

    @property
    def ul_fraction(self) -> float:
        return 1.0 - self.dl_fraction


SCENARIOS = [
    AsymmetryScenario("50:50 symmetric",   0.50),
    AsymmetryScenario("70:30 downlink",    0.70),
    AsymmetryScenario("90:10 downlink",    0.90),
]


# ---------------------------------------------------------------------------
# FDD model
# ---------------------------------------------------------------------------

@dataclass
class FDDResult:
    dl_capacity_mbps: float
    ul_capacity_mbps: float
    dl_demand_mbps: float
    ul_demand_mbps: float
    dl_throughput_mbps: float
    ul_throughput_mbps: float
    utilization: float


def run_fdd(scenario: AsymmetryScenario,
            b_total_mhz: float = B_TOTAL_MHZ,
            demand_total_mbps: float = None) -> FDDResult:
    """
    FDD with equal split of total bandwidth between UL and DL channels.

    Each direction is continuously available. If demand in a direction is
    below capacity, the surplus is wasted (cannot be reallocated).
    """
    b_per_direction = b_total_mhz / 2.0
    cap_per_direction = b_per_direction * REFERENCE_BPS_PER_HZ  # Mbit/s

    # Total offered demand, split by the scenario ratio.
    if demand_total_mbps is None:
        # Reference: total demand = total FDD capacity, so utilisation is
        # meaningful as a fraction of installed capacity.
        demand_total_mbps = b_total_mhz * REFERENCE_BPS_PER_HZ

    dl_demand = scenario.dl_fraction * demand_total_mbps
    ul_demand = scenario.ul_fraction * demand_total_mbps

    dl_tp = min(dl_demand, cap_per_direction)
    ul_tp = min(ul_demand, cap_per_direction)

    utilization = (dl_tp + ul_tp) / b_total_mhz

    return FDDResult(
        dl_capacity_mbps=cap_per_direction,
        ul_capacity_mbps=cap_per_direction,
        dl_demand_mbps=dl_demand,
        ul_demand_mbps=ul_demand,
        dl_throughput_mbps=dl_tp,
        ul_throughput_mbps=ul_tp,
        utilization=utilization,
    )


# ---------------------------------------------------------------------------
# TDD model
# ---------------------------------------------------------------------------

@dataclass
class TDDResult:
    dl_capacity_mbps: float
    ul_capacity_mbps: float
    dl_demand_mbps: float
    ul_demand_mbps: float
    dl_throughput_mbps: float
    ul_throughput_mbps: float
    utilization: float
    dl_slots: int
    ul_slots: int
    guard_slots: int


def _best_slot_split(scenario: AsymmetryScenario,
                     n_traffic_slots: int) -> Tuple[int, int]:
    """
    Given the traffic-slot budget (after guard slots), return the (DL, UL)
    slot split that best matches the DL/UL volume ratio.
    """
    dl_slots = int(round(n_traffic_slots * scenario.dl_fraction))
    dl_slots = max(0, min(n_traffic_slots, dl_slots))
    return dl_slots, n_traffic_slots - dl_slots


def run_tdd(scenario: AsymmetryScenario,
            b_total_mhz: float = B_TOTAL_MHZ,
            slots_per_frame: int = SLOTS_PER_FRAME,
            guard_slots: int = GUARD_SLOTS_DEFAULT,
            demand_total_mbps: float = None) -> TDDResult:
    """
    TDD with one shared channel. Frame = slots_per_frame slots. Guard
    slots carry no traffic. Remaining slots are split DL/UL to match the
    scenario ratio as closely as the discrete slot budget allows.

    Capacity per direction = (slots allocated / slots_per_frame) *
    b_total * spectral_efficiency.
    """
    if demand_total_mbps is None:
        demand_total_mbps = b_total_mhz * REFERENCE_BPS_PER_HZ

    traffic_slots = slots_per_frame - guard_slots
    dl_slots, ul_slots = _best_slot_split(scenario, traffic_slots)

    slot_bw = b_total_mhz / slots_per_frame
    dl_cap = dl_slots * slot_bw * REFERENCE_BPS_PER_HZ
    ul_cap = ul_slots * slot_bw * REFERENCE_BPS_PER_HZ

    dl_demand = scenario.dl_fraction * demand_total_mbps
    ul_demand = scenario.ul_fraction * demand_total_mbps

    dl_tp = min(dl_demand, dl_cap)
    ul_tp = min(ul_demand, ul_cap)

    utilization = (dl_tp + ul_tp) / b_total_mhz

    return TDDResult(
        dl_capacity_mbps=dl_cap,
        ul_capacity_mbps=ul_cap,
        dl_demand_mbps=dl_demand,
        ul_demand_mbps=ul_demand,
        dl_throughput_mbps=dl_tp,
        ul_throughput_mbps=ul_tp,
        utilization=utilization,
        dl_slots=dl_slots,
        ul_slots=ul_slots,
        guard_slots=guard_slots,
    )


# ---------------------------------------------------------------------------
# Driver — runs scenarios and produces tables + plots
# ---------------------------------------------------------------------------

def _fmt_row(name: str, r, scheme: str) -> dict:
    return {
        "scheme": scheme,
        "scenario": name,
        "dl_capacity_mbps": r.dl_capacity_mbps,
        "ul_capacity_mbps": r.ul_capacity_mbps,
        "dl_throughput_mbps": r.dl_throughput_mbps,
        "ul_throughput_mbps": r.ul_throughput_mbps,
        "utilization_pct": 100.0 * r.utilization,
    }


def write_csv(path: str, rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        return
    fields: List[str] = []
    seen = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                fields.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def plot_utilization(rows: List[dict], out_path: str) -> None:
    scenarios = sorted({r["scenario"] for r in rows})
    fdd = [next(r["utilization_pct"] for r in rows
                if r["scheme"] == "FDD" and r["scenario"] == s) for s in scenarios]
    tdd = [next(r["utilization_pct"] for r in rows
                if r["scheme"] == "TDD" and r["scenario"] == s) for s in scenarios]

    x = np.arange(len(scenarios))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w/2, fdd, w, label="FDD", color="tab:blue", edgecolor="black")
    ax.bar(x + w/2, tdd, w, label="TDD", color="tab:orange", edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios)
    ax.set_ylabel("Utilization (%)")
    ax.set_title("Effective utilization — FDD vs TDD across asymmetry scenarios")
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_throughput(rows: List[dict], out_path: str) -> None:
    scenarios = sorted({r["scenario"] for r in rows})
    x = np.arange(len(scenarios))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    for scheme, color, shift in [("FDD", "tab:blue", -w/2),
                                 ("TDD", "tab:orange", +w/2)]:
        dl = [next(r["dl_throughput_mbps"] for r in rows
                   if r["scheme"] == scheme and r["scenario"] == s)
              for s in scenarios]
        ul = [next(r["ul_throughput_mbps"] for r in rows
                   if r["scheme"] == scheme and r["scenario"] == s)
              for s in scenarios]
        ax.bar(x + shift, dl, w, label=f"{scheme} DL",
               color=color, edgecolor="black", alpha=0.85)
        ax.bar(x + shift, ul, w, bottom=dl, label=f"{scheme} UL",
               color=color, edgecolor="black", alpha=0.45, hatch="//")
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios)
    ax.set_ylabel("Effective throughput (Mbit/s)")
    ax.set_title("Delivered DL+UL throughput — FDD vs TDD")
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax.legend(ncol=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_guard_sensitivity(rows: List[dict], out_path: str) -> None:
    scenarios = sorted({r["scenario"] for r in rows})
    guard_fracs = sorted({r["guard_fraction"] for r in rows})
    x = np.arange(len(guard_fracs))
    w = 0.25
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["tab:green", "tab:orange", "tab:red"]
    for i, s in enumerate(scenarios):
        ys = [next(r["utilization_pct"] for r in rows
                   if r["scenario"] == s and r["guard_fraction"] == g)
              for g in guard_fracs]
        ax.bar(x + (i - 1) * w, ys, w, label=s,
               color=colors[i % len(colors)], edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{g:.2f}" for g in guard_fracs])
    ax.set_xlabel("Guard fraction (guard slots / frame)")
    ax.set_ylabel("TDD utilization (%)")
    ax.set_title("TDD utilization vs. guard-period overhead, per scenario")
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    plots_dir = os.path.join(root, "plots")
    results_dir = os.path.join(root, "results")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    scenario_rows: List[dict] = []

    print("=" * 72)
    print("SCENARIO COMPARISON — FDD vs TDD  (B_total = 100 MHz, "
          "TDD frame = 20 slots, 1 guard slot)")
    print("=" * 72)

    for s in SCENARIOS:
        fdd = run_fdd(s)
        tdd = run_tdd(s)
        scenario_rows.append(_fmt_row(s.label, fdd, "FDD"))
        scenario_rows.append(_fmt_row(s.label, tdd, "TDD"))
        print()
        print(f"  {s.label}  (DL:UL = {s.dl_fraction*100:.0f}:"
              f"{s.ul_fraction*100:.0f})")
        print(f"    FDD: DL cap {fdd.dl_capacity_mbps:6.1f}  "
              f"UL cap {fdd.ul_capacity_mbps:6.1f}  |  "
              f"DL tp {fdd.dl_throughput_mbps:6.1f}  "
              f"UL tp {fdd.ul_throughput_mbps:6.1f}  |  "
              f"util {100*fdd.utilization:5.2f}%")
        print(f"    TDD: DL cap {tdd.dl_capacity_mbps:6.1f}  "
              f"UL cap {tdd.ul_capacity_mbps:6.1f}  |  "
              f"DL tp {tdd.dl_throughput_mbps:6.1f}  "
              f"UL tp {tdd.ul_throughput_mbps:6.1f}  |  "
              f"util {100*tdd.utilization:5.2f}%  "
              f"(slots {tdd.dl_slots}DL/{tdd.ul_slots}UL/{tdd.guard_slots}G)")

    write_csv(os.path.join(results_dir, "scenario_summary.csv"), scenario_rows)

    plot_utilization(scenario_rows,
                     os.path.join(plots_dir, "utilization_comparison.png"))
    plot_throughput(scenario_rows,
                    os.path.join(plots_dir, "throughput_comparison.png"))

    # ---- Guard-period sensitivity sweep for TDD ----
    print()
    print("=" * 72)
    print("GUARD-PERIOD SENSITIVITY (TDD only)")
    print("=" * 72)

    guard_rows: List[dict] = []
    for s in SCENARIOS:
        for guard_slots in (1, 2, 4):
            tdd = run_tdd(s, guard_slots=guard_slots)
            guard_frac = guard_slots / SLOTS_PER_FRAME
            guard_rows.append({
                "scenario": s.label,
                "guard_slots": guard_slots,
                "guard_fraction": guard_frac,
                "dl_throughput_mbps": tdd.dl_throughput_mbps,
                "ul_throughput_mbps": tdd.ul_throughput_mbps,
                "utilization_pct": 100.0 * tdd.utilization,
            })
    for s in SCENARIOS:
        row_set = [r for r in guard_rows if r["scenario"] == s.label]
        print(f"\n  {s.label}")
        for r in row_set:
            print(f"    guard {r['guard_slots']}/20 "
                  f"({r['guard_fraction']*100:4.1f}%): "
                  f"util {r['utilization_pct']:5.2f}%  "
                  f"(DL {r['dl_throughput_mbps']:.1f} + "
                  f"UL {r['ul_throughput_mbps']:.1f} Mbit/s)")

    write_csv(os.path.join(results_dir, "guard_sensitivity.csv"), guard_rows)
    plot_guard_sensitivity(guard_rows,
                           os.path.join(plots_dir, "guard_sensitivity.png"))

    print()
    print("Plots:", plots_dir)
    print("CSVs :", results_dir)
    print("Done.")


if __name__ == "__main__":
    main()