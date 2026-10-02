# Mini Project 1.3 — Validating and Extending the 0G–6G Generation Comparison

## Authors

1. Abel NIYIGENA — 223026691
2. Marie Ange TUYIZERE IRADUKUNDA — 223026692
3. Remy Boris RWIGAMBA — 223026974

**Course:** Mobile Communications — Unit 1 Laboratory
**Reference:** MC-MP_Unit1.pdf, Section 1.2
**Source Code:** `src/generation_table.py`, `src/recommender.py`
**Data:** `results/fact_check.csv`, `results/test_cases.csv`

---

# 1. Introduction

This mini project examines the development of mobile communication technologies from 0G to 6G.

The main objectives are:

1. To check the information in the 0G–6G table from Section 1.2.
2. To identify the main problems solved by each new generation.
3. To develop a simple program that recommends a mobile generation based on a given communication requirement.
4. To test the program using different examples.

The project also compares **theoretical peak data rates** with **typical practical rates**, since the maximum rate specified by a standard is not always the rate experienced by users.

---

# 2. Fact-Checking the 0G–6G Table

Each generation was compared with information from technical standards and other reliable sources.

| Generation | Peak Rate in Notes |    Typical / Representative Rate | Main Observation                                        |
| ---------- | -----------------: | -------------------------------: | ------------------------------------------------------- |
| 0G         |                N/A |                              N/A | Historical term, not a formal ITU generation            |
| 1G         |         2.4 kbit/s |                   1.2–2.4 kbit/s | Mainly analog voice                                     |
| 2G         |          64 kbit/s |                       9.6 kbit/s | Digital voice and SMS; circuit-switched data was slower |
| 2.5G       |       171.2 kbit/s |                     30–80 kbit/s | GPRS introduced packet data                             |
| 3G         |           2 Mbit/s |                      ~384 kbit/s | Introduced mobile broadband                             |
| 4G         |         100 Mbit/s |                     10–40 Mbit/s | Designed for high-speed mobile data                     |
| 5G         |          20 Gbit/s |                 ~100–1000 Mbit/s | 20 Gbit/s is a peak requirement under ideal conditions  |
| 6G         |   Research targets | Not yet a normal commercial rate | Still being developed under IMT-2030                    |

The main finding is that **peak rate and typical rate are different**.

For example, the 20 Gbit/s value for 5G represents a maximum performance requirement under specified conditions. It does not mean that every 5G user receives 20 Gbit/s.

The complete fact-checking results are stored in:

```text
results/fact_check.csv
```

---

# 3. Problems Solved by Each Generation

## 3.1 1G → 2G

1G mainly provided analog voice communication.

Important problems included:

* poor security;
* different standards between countries;
* limited capacity;
* lack of digital services.

2G introduced digital communication, better security, authentication, and services such as SMS.

---

## 3.2 2G → 2.5G

2G data communication was slow and mainly circuit-switched.

2.5G introduced packet-switched data through technologies such as GPRS.

This made Internet access more suitable for bursty data traffic.

---

## 3.3 2.5G → 3G

2.5G was still too slow for applications such as mobile Internet and multimedia.

3G provided:

* higher data rates;
* mobile Internet;
* better multimedia support;
* improved support for data services.

---

## 3.4 3G → 4G

3G could provide mobile data, but data traffic was increasing rapidly.

4G introduced a more data-focused network using technologies such as:

* OFDMA;
* MIMO;
* all-IP networking.

This resulted in higher data rates and improved network efficiency.

---

## 3.5 4G → 5G

4G was not designed for all of the new requirements created by modern mobile applications.

5G was developed to support:

* higher data rates;
* lower latency;
* massive numbers of IoT devices;
* industrial applications;
* different types of services.

The main 5G service categories are:

* **eMBB** — enhanced Mobile Broadband;
* **URLLC** — Ultra-Reliable Low-Latency Communications;
* **mMTC** — massive Machine-Type Communications.

---

## 3.6 5G → 6G

6G is being developed to support requirements beyond traditional mobile broadband.

Examples include:

* immersive communication;
* AI-assisted communication;
* integrated sensing and communication;
* very high data rates;
* improved coverage;
* advanced IoT applications.

6G is currently part of the **IMT-2030** development and standardization process.

---

# 4. Recommender Program

The recommender is implemented in:

```text
src/recommender.py
```

The generation information is stored in:

```text
src/generation_table.py
```

The program uses **keyword matching** rather than machine learning.

For example, if the user enters:

```text
I need low-latency control for a robotic arm
```

the program searches for matching keywords such as:

```text
low latency
robotic arm
industrial automation
```

It then recommends:

```text
5G
```

because these requirements are associated with 5G URLLC.

The rules are arranged from older generations to newer generations. Therefore, the program attempts to identify the generation that **first addressed** the given problem.

If no suitable rule is found, the program returns:

```text
unmapped
```

---

# 5. Test Results

Seven test cases were used to evaluate the recommender.

| No. | Statement                                                   | Result       |
| --: | ----------------------------------------------------------- | ------------ |
|   1 | I need low-latency control for a robotic arm                | **5G**       |
|   2 | Send short text messages between users                      | **2G**       |
|   3 | Provide video calling between mobile users                  | **3G**       |
|   4 | Support one million IoT sensors per square kilometre        | **Unmapped** |
|   5 | I want an always-on Internet connection for bursty browsing | **2.5G**     |
|   6 | Support holographic telepresence                            | **6G**       |
|   7 | Broadcast FM radio to cars                                  | **Unmapped** |

Most test cases produced the expected results.

---

# 6. Analysis of the Test Cases

### Case 1 — Robotic Arm

The requirement for low-latency robotic control maps to **5G**, particularly the URLLC service category.

### Case 2 — SMS

SMS is strongly associated with **2G**, so the program correctly maps this requirement to 2G.

### Case 3 — Video Calling

Mobile video services became practical with the higher data rates provided by **3G**.

### Case 4 — Massive IoT

The statement:

```text
Support one million IoT sensors per square kilometre
```

should map to **5G mMTC**, but the program returns `unmapped`.

This happens because the rule contains terms such as:

```text
massive IoT
machine type communication
```

but does not contain all possible expressions such as:

```text
IoT sensors
one million IoT
sensor per square kilometre
```

This shows a limitation of keyword matching.

### Case 7 — FM Radio

The FM broadcasting requirement correctly returns `unmapped` because FM radio broadcasting is outside the cellular-generation categories being studied.

---

# 7. Improving the Recommender

The 5G rule can be improved by adding more keywords:

```python
"massive iot",
"iot sensor",
"iot sensors",
"one million iot",
"sensor per square",
"machine type communication",
```

This would allow the program to recognize more descriptions of massive IoT requirements.

A more advanced system could use machine learning or semantic matching, but the keyword approach is suitable for this project because it is:

* simple;
* fast;
* transparent;
* easy to test;
* easy to modify.

---

# 8. Peak Rate Versus Typical Rate

One of the main findings of this project is that **theoretical peak rates should not be confused with typical user rates**.

For example:

$$
\text{Peak Rate} \neq \text{Typical User Rate}
$$

The peak rate is normally measured or defined under favorable conditions, while actual performance depends on:

* signal strength;
* available bandwidth;
* network traffic;
* distance from the base station;
* propagation conditions;
* device capability;
* network configuration.

Therefore, a generation comparison is more useful when both peak and typical rates are considered.

---

# 9. Reproduction

The program can be executed using:

```powershell
cd 'C:\Users\Anum\Desktop\Academic\2027\mobile_comm\project\MC_MiniProject_1_3'
..\.venv\Scripts\Activate.ps1
python src\recommender.py
```

The program displays the fact-checking information and test results.

It generates:

```text
results/fact_check.csv
results/test_cases.csv
```

---

# 10. Conclusion

This project validated the 0G–6G comparison presented in Section 1.2 and identified the main problems addressed by each generation.

The analysis showed that **peak data rates are different from typical practical rates**, so both should be considered when comparing mobile generations.

The recommender successfully identified most of the test requirements. The IoT test demonstrated a limitation of simple keyword matching because different users may describe the same requirement using different words.

The project also showed that each new mobile generation was developed to address limitations of previous systems, including low data rates, limited security, high latency, insufficient capacity, and increasing numbers of connected devices.

Finally, 6G should be considered an emerging technology under the **IMT-2030** development process rather than as a fully deployed commercial generation. Its development includes higher performance as well as new capabilities such as AI integration, immersive communication, and integrated sensing and communication.
