"""
Mobile Communications Mini Project 1.1
Simulating Link Budgets and Coverage Range with Python

Author: <your names>
Course: Mobile Communications — Unit 1 Lab
Reference: MC-MP_Unit1.pdf, Mini Project 1.1, Section 1.10

FIX-1  distance sweep extended to 1000 km so both bands have finite
       maximum-range values instead of hitting the 100 km cap.

FIX-2  an extra band "28 GHz + 30 dB excess loss" is included in the
       base scenario to represent a realistic mmWave link.

FIX-3  Lab Task 5 no longer cross-references band names from the base
       scenario. It defines its own baseline band set and runs all three
       variants (baseline / double-P_TX / double-bandwidth) within it, so
       no dictionary lookup can miss and return None.
"""

from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass
from typing import Optional, Dict, List

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# 1. Free-space path loss (Section 1.10 formula)
# ---------------------------------------------------------------------------

def fspl_db(d_km, f_mhz):
    """
    Free-space path loss in dB:

        L = 20 log10(d_km) + 20 log10(f_MHz) + 32.44
    """
    d_km = np.asarray(d_km, dtype=float)
    return 20.0 * np.log10(d_km) + 20.0 * np.log10(f_mhz) + 32.44


# ---------------------------------------------------------------------------
# 2. Link budget (Section 1.10 formula)
# ---------------------------------------------------------------------------

def link_budget_dbm(p_tx_dbm, g_tx_dbi, l_path_db, g_rx_dbi, l_other_db):
    """
    P_RX = P_TX + G_TX - L_path + G_RX - L_other   [dBm]
    """
    return (np.asarray(p_tx_dbm) + np.asarray(g_tx_dbi)
            - np.asarray(l_path_db) + np.asarray(g_rx_dbi)
            - np.asarray(l_other_db))


# ---------------------------------------------------------------------------
# 3. Scenario / band types
# ---------------------------------------------------------------------------

@dataclass
class Band:
    name: str
    f_mhz: float
    p_tx_dbm: float
    g_tx_dbi: float
    g_rx_dbi: float
    l_other_db: float


@dataclass
class Scenario:
    label: str
    bands: List[Band]
    sensitivity_dbm: float
    reference_km: float


# ---------------------------------------------------------------------------
# 4. Analysis helpers
# ---------------------------------------------------------------------------

def max_range_km(distances_km: np.ndarray,
                 p_rx_dbm: np.ndarray,
                 sensitivity_dbm: float) -> float:
    """
    Largest distance at which P_RX still exceeds sensitivity.
    Returns 0.0 if the smallest tested distance already fails, and the
    largest tested distance if every tested point passes.
    """
    above = p_rx_dbm >= sensitivity_dbm
    if not np.any(above):
        return 0.0
    if np.all(above):
        return float(distances_km[-1])
    idx = int(np.max(np.where(above)[0]))
    return float(distances_km[idx])


def link_margin_db(p_rx_dbm: np.ndarray,
                   distances_km: np.ndarray,
                   sensitivity_dbm: float,
                   reference_km: float) -> float:
    idx = int(np.argmin(np.abs(distances_km - reference_km)))
    return float(p_rx_dbm[idx] - sensitivity_dbm)


def snr_db(p_rx_dbm: np.ndarray, noise_floor_dbm: float) -> np.ndarray:
    return p_rx_dbm - noise_floor_dbm


def shannon_capacity_bps(snr_db: np.ndarray, bandwidth_hz: float) -> np.ndarray:
    """
    Shannon capacity C = B * log2(1 + SNR).
    Linear SNR reconstructed from dB; -30 dB floor to avoid NaN.
    """
    snr_lin = np.power(10.0, np.maximum(snr_db, -30.0) / 10.0)
    return bandwidth_hz * np.log2(1.0 + snr_lin)


# ---------------------------------------------------------------------------
# 5. Run one scenario
# ---------------------------------------------------------------------------

def run_scenario(scenario: Scenario,
                 distances_km: np.ndarray,
                 noise_floor_dbm: Optional[float] = None,
                 bandwidth_hz: Optional[float] = None
                 ) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for b in scenario.bands:
        l_path = fspl_db(distances_km, b.f_mhz)
        p_rx = link_budget_dbm(b.p_tx_dbm, b.g_tx_dbi, l_path,
                               b.g_rx_dbi, b.l_other_db)
        r_max = max_range_km(distances_km, p_rx, scenario.sensitivity_dbm)
        margin = link_margin_db(p_rx, distances_km,
                                scenario.sensitivity_dbm,
                                scenario.reference_km)
        row = {
            "name": b.name,
            "f_mhz": b.f_mhz,
            "p_tx_dbm": b.p_tx_dbm,
            "g_tx_dbi": b.g_tx_dbi,
            "g_rx_dbi": b.g_rx_dbi,
            "l_other_db": b.l_other_db,
            "sensitivity_dbm": scenario.sensitivity_dbm,
            "reference_km": scenario.reference_km,
            "l_path_ref_db": float(fspl_db(scenario.reference_km, b.f_mhz)),
            "p_rx_ref_dbm": float(link_budget_dbm(
                b.p_tx_dbm, b.g_tx_dbi,
                fspl_db(scenario.reference_km, b.f_mhz),
                b.g_rx_dbi, b.l_other_db)),
            "link_margin_ref_db": margin,
            "max_range_km": r_max,
        }
        if noise_floor_dbm is not None:
            snr = snr_db(p_rx, noise_floor_dbm)
            row["snr_ref_db"] = float(snr[
                int(np.argmin(np.abs(distances_km - scenario.reference_km)))])
            if bandwidth_hz is not None:
                cap = shannon_capacity_bps(snr, bandwidth_hz)
                row["capacity_ref_bps"] = float(cap[
                    int(np.argmin(np.abs(distances_km
                                          - scenario.reference_km)))])
        out[b.name] = row
    return out


# ---------------------------------------------------------------------------
# 6. Plots
# ---------------------------------------------------------------------------

def plot_p_rx(scenario: Scenario,
              distances_km: np.ndarray,
              out_path: str,
              title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    for b in scenario.bands:
        l_path = fspl_db(distances_km, b.f_mhz)
        p_rx = link_budget_dbm(b.p_tx_dbm, b.g_tx_dbi, l_path,
                               b.g_rx_dbi, b.l_other_db)
        ax.plot(distances_km, p_rx, linewidth=2,
                label=f"{b.name}  "
                      f"({b.f_mhz:.0f} MHz, P_TX={b.p_tx_dbm:.0f} dBm, "
                      f"G_TX={b.g_tx_dbi:.0f} dBi)")
    ax.axhline(scenario.sensitivity_dbm, color="red", linestyle="--",
               linewidth=1.4,
               label=f"sensitivity = {scenario.sensitivity_dbm:.0f} dBm")
    ax.set_xscale("log")
    ax.set_xlabel("Distance (km, log scale)")
    ax.set_ylabel("Received power P_RX (dBm)")
    ax.set_title(title)
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_snr_and_capacity(scenario: Scenario,
                          distances_km: np.ndarray,
                          noise_floor_dbm: float,
                          bandwidth_hz: float,
                          out_path: str) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    for b in scenario.bands:
        l_path = fspl_db(distances_km, b.f_mhz)
        p_rx = link_budget_dbm(b.p_tx_dbm, b.g_tx_dbi, l_path,
                               b.g_rx_dbi, b.l_other_db)
        snr = snr_db(p_rx, noise_floor_dbm)
        cap = shannon_capacity_bps(snr, bandwidth_hz)
        ax1.plot(distances_km, snr, linewidth=2, label=b.name)
        ax2.plot(distances_km, cap / 1e6, linewidth=2, label=b.name)
    ax1.axhline(0.0, color="grey", linewidth=0.8, linestyle=":")
    ax1.set_xscale("log")
    ax1.set_xlabel("Distance (km, log scale)")
    ax1.set_ylabel("SNR (dB)")
    ax1.set_title(f"SNR vs. distance (noise floor = {noise_floor_dbm} dBm)")
    ax1.grid(True, which="both", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper right", fontsize=9)

    ax2.set_xscale("log")
    ax2.set_xlabel("Distance (km, log scale)")
    ax2.set_ylabel("Shannon capacity (Mbit/s)")
    ax2.set_title(f"Capacity vs. distance (B = {bandwidth_hz/1e6:.0f} MHz)")
    ax2.grid(True, which="both", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 7. CSV writer (union of keys)
# ---------------------------------------------------------------------------

def write_summary_csv(rows: List[dict], path: str) -> None:
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


# ---------------------------------------------------------------------------
# 8. Band sets
# ---------------------------------------------------------------------------

def _base_bands() -> List[Band]:
    """
    FIX-2: three bands in the base scenario.
      700 MHz (low band)          -- required by the manual
      28 GHz (mmWave, free space) -- required by the manual
      28 GHz (+30 dB excess loss) -- comparison curve for realistic mmWave
    """
    return [
        Band("700 MHz (low band)",            700.0,  40.0, 15.0, 0.0, 3.0),
        Band("28 GHz (mmWave, free space)", 28000.0,  40.0, 15.0, 0.0, 3.0),
        Band("28 GHz (+30 dB excess loss)", 28000.0,  40.0, 15.0, 0.0, 3.0 + 30.0),
    ]


def _task1_bands() -> List[Band]:
    return [
        Band("700 MHz (low band)",                 700.0,  40.0, 15.0, 0.0, 3.0),
        Band("28 GHz (free space, G_TX=24 dBi)", 28000.0,  40.0, 24.0, 0.0, 3.0),
    ]


def _task2_bands() -> List[Band]:
    return [
        Band("700 MHz (low band)",   700.0,  40.0, 15.0, 0.0, 3.0),
        Band("3.5 GHz (mid band)",  3500.0,  40.0, 15.0, 0.0, 3.0),
        Band("28 GHz (mmWave)",    28000.0,  40.0, 15.0, 0.0, 3.0),
    ]


def _task3_bands() -> List[Band]:
    return [
        Band("700 MHz (+8 dB shadow)",  700.0,  40.0, 15.0, 0.0, 3.0 + 8.0),
        Band("28 GHz (+8 dB shadow)", 28000.0,  40.0, 15.0, 0.0, 3.0 + 8.0),
    ]


# ---------------------------------------------------------------------------
# 9. Driver
# ---------------------------------------------------------------------------

def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    plots_dir = os.path.join(root, "plots")
    results_dir = os.path.join(root, "results")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    # FIX-1: extended sweep 0.01 km to 1000 km.
    distances_km = np.logspace(-2, 3, 600)

    sensitivity_dbm = -100.0
    reference_km = 1.0
    noise_floor_dbm = -104.0                 # 10 MHz channel
    bandwidth_hz = 10e6

    all_rows: List[dict] = []

    # ---------- Base scenario ----------
    base = Scenario("base", _base_bands(), sensitivity_dbm, reference_km)
    base_results = run_scenario(base, distances_km,
                                noise_floor_dbm, bandwidth_hz)
    print("=" * 72)
    print("BASE SCENARIO")
    print("=" * 72)
    for name, r in base_results.items():
        print(f"  {name}")
        print(f"    L_path @ {reference_km:.1f} km = {r['l_path_ref_db']:.2f} dB")
        print(f"    P_RX   @ {reference_km:.1f} km = {r['p_rx_ref_dbm']:.2f} dBm")
        print(f"    margin @ {reference_km:.1f} km = {r['link_margin_ref_db']:.2f} dB")
        print(f"    max range above sensitivity   = {r['max_range_km']:.3f} km")
        print(f"    SNR    @ {reference_km:.1f} km = {r['snr_ref_db']:.2f} dB")
        print(f"    capacity @ {reference_km:.1f} km = "
              f"{r['capacity_ref_bps']/1e6:.2f} Mbit/s")
        all_rows.append({"scenario": "base", **r})

    plot_p_rx(base, distances_km,
              os.path.join(plots_dir, "link_budget_comparison.png"),
              "P_RX vs. distance — 700 MHz vs 28 GHz "
              "(P_TX=40 dBm, G_TX=15 dBi, G_RX=0 dBi)")
    plot_snr_and_capacity(base, distances_km,
                          noise_floor_dbm, bandwidth_hz,
                          os.path.join(plots_dir, "snr_capacity.png"))

    # ---------- Task 1 ----------
    t1 = Scenario("task1_mmwave_g_tx_24", _task1_bands(),
                  sensitivity_dbm, reference_km)
    t1_results = run_scenario(t1, distances_km)
    print()
    print("=" * 72)
    print("LAB TASK 1: 28 GHz G_TX raised from 15 to 24 dBi")
    print("=" * 72)
    for name, r in t1_results.items():
        print(f"  {name}: max range = {r['max_range_km']:.3f} km  "
              f"margin @ 1 km = {r['link_margin_ref_db']:.2f} dB")
        all_rows.append({"scenario": "task1", **r})
    base_mm = base_results["28 GHz (mmWave, free space)"]["max_range_km"]
    t1_mm = t1_results["28 GHz (free space, G_TX=24 dBi)"]["max_range_km"]
    print(f"  recovered mmWave range: {base_mm:.3f} km -> {t1_mm:.3f} km "
          f"({t1_mm/base_mm:.2f}x)")

    # ---------- Task 2 ----------
    t2 = Scenario("task2_mid_band", _task2_bands(),
                  sensitivity_dbm, reference_km)
    t2_results = run_scenario(t2, distances_km)
    print()
    print("=" * 72)
    print("LAB TASK 2: 3.5 GHz mid-band added")
    print("=" * 72)
    for name, r in t2_results.items():
        print(f"  {name}: max range = {r['max_range_km']:.3f} km  "
              f"P_RX @ 1 km = {r['p_rx_ref_dbm']:.2f} dBm")
        all_rows.append({"scenario": "task2", **r})
    plot_p_rx(t2, distances_km,
              os.path.join(plots_dir, "link_budget_with_midband.png"),
              "P_RX vs. distance — 700 MHz, 3.5 GHz, 28 GHz")

    # ---------- Task 3 ----------
    t3 = Scenario("task3_shadow_margin", _task3_bands(),
                  sensitivity_dbm, reference_km)
    t3_results = run_scenario(t3, distances_km)
    print()
    print("=" * 72)
    print("LAB TASK 3: +8 dB shadowing margin into L_other")
    print("=" * 72)
    for name, r in t3_results.items():
        print(f"  {name}: max range = {r['max_range_km']:.3f} km")
        all_rows.append({"scenario": "task3", **r})
    for base_name, shadow_name in [
        ("700 MHz (low band)", "700 MHz (+8 dB shadow)"),
        ("28 GHz (mmWave, free space)", "28 GHz (+8 dB shadow)"),
    ]:
        r0 = base_results[base_name]["max_range_km"]
        r1 = t3_results[shadow_name]["max_range_km"]
        print(f"  {base_name}: {r0:.3f} km -> {r1:.3f} km "
              f"(shrink factor {r0/r1:.2f}x)")

    # ---------- Task 4 ----------
    print()
    print("=" * 72)
    print("LAB TASK 4: SNR and Shannon capacity ceiling "
          "(10 MHz channel, noise floor -104 dBm)")
    print("=" * 72)
    for name, r in base_results.items():
        print(f"  {name}: SNR @ 1 km = {r['snr_ref_db']:.2f} dB  "
              f"capacity @ 1 km = {r['capacity_ref_bps']/1e6:.2f} Mbit/s")

    # ---------- Task 5 (FIX-3: self-contained, no cross-scenario lookups) ----
    print()
    print("=" * 72)
    print("LAB TASK 5: double P_TX vs double bandwidth")
    print("=" * 72)

    # A dedicated baseline band set so the three variants share band names.
    baseline_bands_t5 = [
        Band("700 MHz (low band)",  700.0, 40.0, 15.0, 0.0, 3.0),
        Band("28 GHz (mmWave)",   28000.0, 40.0, 15.0, 0.0, 3.0),
    ]
    bands_dbl_tx = [
        Band("700 MHz (low band)",  700.0, 43.0, 15.0, 0.0, 3.0),
        Band("28 GHz (mmWave)",   28000.0, 43.0, 15.0, 0.0, 3.0),
    ]

    t5_base_scn = Scenario("task5_baseline", baseline_bands_t5,
                           sensitivity_dbm, reference_km)
    t5_dbl_tx_scn = Scenario("task5_dbl_tx", bands_dbl_tx,
                             sensitivity_dbm, reference_km)

    base_t5 = run_scenario(t5_base_scn, distances_km,
                           noise_floor_dbm, bandwidth_hz)
    dbl_tx  = run_scenario(t5_dbl_tx_scn, distances_km,
                           noise_floor_dbm, bandwidth_hz)
    dbl_bw  = run_scenario(t5_base_scn, distances_km,
                           noise_floor_dbm, 2 * bandwidth_hz)

    for name in ["700 MHz (low band)", "28 GHz (mmWave)"]:
        cap0   = base_t5[name]["capacity_ref_bps"]
        cap_tx = dbl_tx[name]["capacity_ref_bps"]
        cap_bw = dbl_bw[name]["capacity_ref_bps"]
        print(f"  {name}")
        print(f"    baseline capacity      = {cap0/1e6:.2f} Mbit/s")
        print(f"    double P_TX capacity   = {cap_tx/1e6:.2f} Mbit/s  "
              f"({cap_tx/cap0:.3f}x)")
        print(f"    double bandwidth cap   = {cap_bw/1e6:.2f} Mbit/s  "
              f"({cap_bw/cap0:.3f}x)")
        all_rows.append({"scenario": "task5_baseline", **base_t5[name]})
        all_rows.append({"scenario": "task5_dbl_tx",   **dbl_tx[name]})
        all_rows.append({"scenario": "task5_dbl_bw",   **dbl_bw[name]})

    # ---------- Task 6 ----------
    print()
    print("=" * 72)
    print("LAB TASK 6: TDD guard-period duty-cycle note (qualitative)")
    print("=" * 72)
    print("  FDD transmits continuously in each direction on paired carriers.")
    print("  TDD shares one carrier in time: guard periods consume slots that")
    print("  carry no traffic, and the effective duty cycle per direction is")
    print("  reduced below 1.0 even before any traffic asymmetry is applied.")
    print("  In a link budget this appears as an effective reduction of the")
    print("  per-direction average transmit power (or equivalently an added")
    print("  loss term proportional to -10 log10(duty_cycle)). With a 1-in-20")
    print("  guard fraction, the TDD duty cycle loss is approximately")
    print(f"      -10 log10(19/20) = {-10*np.log10(19/20):.3f} dB")
    print("  FDD pays no equivalent per-direction loss.")

    # ---------- CSV ----------
    write_summary_csv(all_rows,
                      os.path.join(results_dir, "link_budget_summary.csv"))

    print()
    print("Plot:", os.path.join(plots_dir, "link_budget_comparison.png"))
    print("Plot:", os.path.join(plots_dir, "snr_capacity.png"))
    print("Plot:", os.path.join(plots_dir, "link_budget_with_midband.png"))
    print("CSV :", os.path.join(results_dir, "link_budget_summary.csv"))
    print("Done.")


if __name__ == "__main__":
    main()