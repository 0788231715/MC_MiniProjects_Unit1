"""
Mobile Communications Mini Project 1.3
Recommender tool: map a plain-language communication requirement to the
generation that first solved it, with justification.

Approach: keyword matching against a hand-curated mapping. No machine
learning. The mapping is derived from the per-generation problems_solved
list in generation_table.py, so the tool's justifications are traceable
to the same sources.

All CSV output uses explicit UTF-8 encoding so Windows' default charmap
codec does not raise UnicodeEncodeError on non-ASCII source strings.
"""

from __future__ import annotations

import csv
import os
import sys
from typing import List, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)

from generation_table import fact_check_rows  # noqa: E402


# ---------------------------------------------------------------------------
# Keyword -> generation mapping
# ---------------------------------------------------------------------------
# Each entry: (list of trigger keywords, generation key, justification).
# Matching is case-insensitive and substring-based. A statement matches a
# generation if ANY of its keywords is found.

RULES: List[Tuple[List[str], str, str]] = [
    # 0G
    (["operator", "manual call", "manual switchboard", "push to talk",
      "taxi dispatch", "pre-cellular"],
     "0G",
     "0G systems used manual operator assistance and push-to-talk; they "
     "addressed the first need for mobile voice outside an office."),

    # 1G
    (["analog voice", "first mobile phone", "car phone", "handoff",
      "hand-off", "cellular concept"],
     "1G",
     "1G introduced the cellular concept with analog FDMA, enabling "
     "frequency reuse and automatic hand-off between base stations."),

    # 2G
    (["sms", "text message", "digital voice", "roaming across countries",
      "secure voice call", "encrypted voice", "authentication",
      "european standard", "fragmentation"],
     "2G",
     "2G (GSM) unified a European air interface, introduced "
     "authentication and ciphering, and created SMS."),

    # 2.5G
    (["packet data", "always-on", "bursty traffic", "internet browsing",
      "wap", "gprs", "charging by volume", "always on connection"],
     "2.5G",
     "2.5G (GPRS/EDGE) moved from circuit switching to packet switching, "
     "enabling always-on bursty data and volume billing."),

    # 3G
    (["video call", "video calling", "mobile broadband", "web browsing",
      "384 kbit", "streaming", "mobile internet at speed"],
     "3G",
     "3G (UMTS/CDMA2000) delivered the first true mobile broadband, "
     "supporting video calling and web browsing at hundreds of kbit/s."),

    # 4G
    (["all-ip", "all ip", "ofdma", "mimo", "high spectral efficiency",
      "broadband at mobile speed", "hspa", "lte", "mobile hd video"],
     "4G",
     "4G (LTE) is all-IP, uses OFDMA and MIMO, and delivers tens of "
     "Mbit/s to mobile users - the first generation designed data-first."),

    # 5G
    (["ultra low latency", "ultra-low latency", "low latency control",
      "robotic arm", "industrial automation", "massive iot",
      "machine type communication", "mmwave", "mm wave",
      "network slicing", "sub-1 ms", "sub 1 ms", "1 ms latency"],
     "5G",
     "5G (NR) is the first generation to address URLLC (sub-1 ms) and "
     "mMTC (10^6 devices/km2) alongside eMBB, enabling industrial "
     "control and massive IoT."),

    # 6G
    (["holographic", "hologram", "tactile internet", "terahertz",
      "sub-thz", "ai native", "integrated sensing and communication",
      "isac", "reconfigurable intelligent surface", "ris", "digital twin"],
     "6G",
     "6G (IMT-2030 research) targets holographic/tactile communication, "
     "sub-THz spectrum, and AI-native networking; use cases are defined "
     "but not yet standardised."),
]


def _matches(statement: str, keywords: List[str]) -> bool:
    s = statement.lower()
    return any(k.lower() in s for k in keywords)


def recommend(statement: str) -> Tuple[str, str]:
    """
    Return (generation_key, justification).

    Matching order matters: the rules are listed from oldest to newest, so
    the earliest generation whose keywords appear in the statement wins.
    This is the correct semantics - the manual asks for 'the generation
    that FIRST solved it'.

    If no rule matches, return ('unmapped', explanation).
    """
    for keywords, gen, just in RULES:
        if _matches(statement, keywords):
            return gen, just
    return ("unmapped",
            "No keyword matched. The statement does not map cleanly to a "
            "single generation, or uses vocabulary outside the tool's "
            "hand-curated rule set.")


# ---------------------------------------------------------------------------
# Test cases (>= 6 required, including one that does not map cleanly)
# ---------------------------------------------------------------------------

TEST_CASES: List[str] = [
    "I need low-latency control for a robotic arm",
    "Send short text messages between users",
    "Provide video calling between two mobile subscribers",
    "Support one million IoT sensors per square kilometre",
    "I want an always-on internet connection for bursty browsing",
    "Make sure the network can do holographic telepresence",
    # Non-mapping case, deliberately out-of-scope
    "I want to broadcast FM radio to cars",
]


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

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
    # encoding='utf-8' is required on Windows: default charmap (cp1252)
    # cannot encode certain characters used in the source strings.
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> None:
    results_dir = os.path.join(_ROOT, "results")
    os.makedirs(results_dir, exist_ok=True)

    # ---- Fact-check table ----
    fc_rows = fact_check_rows()
    write_csv(os.path.join(results_dir, "fact_check.csv"), fc_rows)
    print("=" * 72)
    print("FACT-CHECK TABLE (written to results/fact_check.csv)")
    print("=" * 72)
    for r in fc_rows:
        print(f"  {r['generation']:5s}  peak(section 1.2) = "
              f"{r['peak_rate_section_1_2']}")
        print(f"           typical(cross-checked) = "
              f"{r['typical_rate_cross_checked']}")

    # ---- Recommender tests ----
    print()
    print("=" * 72)
    print("RECOMMENDER TEST CASES")
    print("=" * 72)
    test_rows: List[dict] = []
    for i, tc in enumerate(TEST_CASES, 1):
        gen, just = recommend(tc)
        test_rows.append({
            "case": i,
            "statement": tc,
            "recommended_generation": gen,
            "justification": just,
        })
        print(f"  Case {i}: {tc}")
        print(f"    -> {gen}")
        print(f"       {just}")
    write_csv(os.path.join(results_dir, "test_cases.csv"), test_rows)

    print()
    print("Outputs:", results_dir)
    print("Done.")


if __name__ == "__main__":
    main()