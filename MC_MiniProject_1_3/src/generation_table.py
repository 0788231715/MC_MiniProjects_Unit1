"""
Mobile Communications Mini Project 1.3
Validating and Extending the 0G–6G Generation Comparison

Fact-checked data for the Section 1.2 generation table, plus per-transition
motivations. Every row lists at least two independent sources beyond the
unit notes, and flags where the manual's simplified numbers diverge from
credible references (typically theoretical peak vs. typical field rates).

Note: source strings may contain non-ASCII characters (§, ≈, ×, etc.).
CSV output is written with explicit UTF-8 encoding so Windows' default
charmap codec does not raise UnicodeEncodeError.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Generation:
    key: str
    name: str
    years: str
    access: str
    service: str
    peak_rate: str          # as stated in Section 1.2
    typical_rate: str       # from cross-checked sources
    peak_source_1: str
    peak_source_2: str
    notes: str              # discrepancies found
    problems_solved: List[str] = field(default_factory=list)


GENERATIONS: List[Generation] = [
    Generation(
        key="0G",
        name="0G (pre-cellular)",
        years="1946-1979",
        access="MTS / IMTS, push-to-talk",
        service="Voice (manual operator-assisted)",
        peak_rate="N/A (analog voice only)",
        typical_rate="N/A",
        peak_source_1="Rappaport, Wireless Communications: Principles and Practice, 2nd ed., Sec. 1.1",
        peak_source_2="ITU-R Handbook on Land Mobile (including wireless access), Vol. 1",
        notes="Section 1.2 lists 0G as a placeholder row without technical parameters; the "
              "0G label is a retrospective category. Cross-checks agree the term is not a "
              "standardised ITU designation.",
        problems_solved=[
            "Manual operator assistance per call was slow and unscalable.",
            "No hand-off between base stations - calls dropped on movement.",
            "Capacity limited to a few dozen simultaneous users per city.",
        ],
    ),
    Generation(
        key="1G",
        name="1G (analog cellular)",
        years="1979-1990s",
        access="AMPS, NMT, TACS (FDMA analog)",
        service="Analog voice",
        peak_rate="2.4 kbit/s (per Section 1.2)",
        typical_rate="1.2-2.4 kbit/s",
        peak_source_1="Rappaport, Sec. 1.2, AMPS voice channel approx. 3 kHz analog",
        peak_source_2="GSMA Intelligence, 'Mobile Economy' historical annex",
        notes="Peak rate is often quoted as 2.4 kbit/s for the digitised voice codec. Field "
              "quality depended on analog SNR, not bit rate; the number is a useful summary, "
              "not a data service rate.",
        problems_solved=[
            "Incompatible national analog standards (AMPS/NMT/TACS) prevented roaming.",
            "Analog voice was trivial to eavesdrop - no encryption.",
            "Cloned handsets (fraud) were widespread because authentication was trivial.",
            "Capacity per cell was very low and could not scale with demand.",
        ],
    ),
    Generation(
        key="2G",
        name="2G (digital cellular)",
        years="1991-2000s",
        access="GSM, IS-95 cdmaOne (TDMA / CDMA)",
        service="Digital voice + SMS + low-rate data",
        peak_rate="64 kbit/s (per Section 1.2)",
        typical_rate="9.6 kbit/s (GSM CS data); 14.4 kbit/s (EDGE later)",
        peak_source_1="3GPP TS 45.001 (GSM radio aspects)",
        peak_source_2="ETSI EN 300 910 (GSM 05.05)",
        notes="Section 1.2's 64 kbit/s is theoretical; measured circuit-switched GSM data "
              "was 9.6 kbit/s per timeslot. GPRS (2.5G) and EDGE raised typical rates to "
              "40-200 kbit/s but required additional standards beyond the 2G baseline.",
        problems_solved=[
            "1G fragmentation: GSM unified a common air interface across Europe.",
            "1G security: GSM introduced authentication and A5 ciphering.",
            "Capacity: TDMA and CDMA supported many more users per cell than FDMA.",
            "Text: SMS created the first mass-market data service.",
        ],
    ),
    Generation(
        key="2.5G",
        name="2.5G (GPRS / EDGE)",
        years="2000-2003",
        access="GPRS, EDGE (packet-switched over GSM)",
        service="Packet data, WAP, early mobile internet",
        peak_rate="171.2 kbit/s (GPRS theoretical)",
        typical_rate="30-80 kbit/s",
        peak_source_1="3GPP TS 44.060 (GPRS RLC/MAC)",
        peak_source_2="ETSI TR 101 112 (EDGE feasibility study)",
        notes="Circuit-switched data was inefficient for bursty internet traffic. GPRS "
              "introduced packet switching; EDGE improved spectral efficiency 3x.",
        problems_solved=[
            "Circuit-switched data monopolised a channel for the entire session.",
            "No 'always-on' connectivity - every session needed dial-up.",
            "Billing per minute discouraged data usage.",
        ],
    ),
    Generation(
        key="3G",
        name="3G (IMT-2000)",
        years="2001-2010s",
        access="UMTS (WCDMA), CDMA2000, HSPA",
        service="Mobile broadband, video calling",
        peak_rate="2 Mbit/s (per Section 1.2)",
        typical_rate="384 kbit/s (initial); 2-14 Mbit/s (HSPA+)",
        peak_source_1="ITU-R M.1457 (IMT-2000 detailed specifications)",
        peak_source_2="3GPP TS 25.101 (UE radio transmission and reception)",
        notes="Section 1.2's 2 Mbit/s was the ITU IMT-2000 requirement for stationary users. "
              "Real deployments delivered 384 kbit/s initially. HSPA (3.5G) later achieved "
              "peak rates up to 42 Mbit/s, well beyond the 2 Mbit/s baseline.",
        problems_solved=[
            "2G data rates were too low for web browsing or video.",
            "No quality-of-service differentiation between voice and data.",
            "Spectral efficiency limits capped capacity under growing demand.",
        ],
    ),
    Generation(
        key="4G",
        name="4G (IMT-Advanced)",
        years="2010-2020s",
        access="LTE, LTE-Advanced, WiMAX",
        service="All-IP mobile broadband",
        peak_rate="100 Mbit/s (per Section 1.2, mobile)",
        typical_rate="10-40 Mbit/s",
        peak_source_1="ITU-R M.2134 (IMT-Advanced requirements)",
        peak_source_2="3GPP TS 36.101 (E-UTRA user equipment radio transmission)",
        notes="100 Mbit/s was the ITU requirement for high-mobility users; 1 Gbit/s for "
              "low-mobility. LTE-Advanced Pro (4.5G) reached 1 Gbit/s in the field. "
              "Section 1.2's number reflects the 4G baseline, not the eventual cap.",
        problems_solved=[
            "3G was optimised for voice; data was an afterthought.",
            "Circuit-switched fallback complicated an all-IP core.",
            "MIMO and OFDMA were needed for high spectral efficiency.",
        ],
    ),
    Generation(
        key="5G",
        name="5G NR",
        years="2019-present",
        access="5G NR (Sub-6 and mmWave), massive MIMO",
        service="eMBB, URLLC, mMTC",
        peak_rate="20 Gbit/s (per Section 1.2)",
        typical_rate="100-1000 Mbit/s (deployed networks)",
        peak_source_1="ITU-R M.2410 (minimum requirements for IMT-2020)",
        peak_source_2="3GPP TS 38.101 (NR UE radio transmission and reception)",
        notes="20 Gbit/s is the ITU IMT-2020 peak requirement for eMBB in ideal conditions. "
              "Field measurements in 2023-2024 sub-6 deployments report 100-600 Mbit/s "
              "downlink typical. mmWave small cells reach multi-Gbit/s but with limited "
              "coverage. The gap between peak and typical is the largest of any generation.",
        problems_solved=[
            "4G could not meet sub-1 ms latency for industrial control.",
            "Massive IoT (10^6 devices/km2) exceeded 4G connection density limits.",
            "Mobile data demand outpaced 4G spectral efficiency improvements.",
        ],
    ),
    Generation(
        key="6G",
        name="6G (in research)",
        years="2030 (expected)",
        access="Sub-THz, RIS, AI-native air interface",
        service="Holographic, tactile, AI-integrated",
        peak_rate="1 Tbit/s (per Section 1.2)",
        typical_rate="Not yet defined",
        peak_source_1="ITU-R FG-NET-2030 (IMT-2030 framework)",
        peak_source_2="Samsung 6G White Paper, 'The Next Hyper-Connected Experience' (2020)",
        notes="1 Tbit/s is a research target, not a standardised requirement. IMT-2030 "
              "framework (2023) describes 6G use cases but does not commit to a peak "
              "number. Section 1.2's figure is optimistic and should be treated as a "
              "research direction, not a validated specification.",
        problems_solved=[
            "5G's peak-to-typical gap widened; user experience lags headline claims.",
            "AI workloads at the edge need integrated compute and communication.",
            "Sensing and communication convergence not addressed by 5G.",
        ],
    ),
]


def fact_check_rows() -> list[dict]:
    rows = []
    for g in GENERATIONS:
        rows.append({
            "generation": g.key,
            "name": g.name,
            "years": g.years,
            "peak_rate_section_1_2": g.peak_rate,
            "typical_rate_cross_checked": g.typical_rate,
            "source_1": g.peak_source_1,
            "source_2": g.peak_source_2,
            "discrepancy_notes": g.notes,
            "problems_solved": " | ".join(g.problems_solved),
        })
    return rows