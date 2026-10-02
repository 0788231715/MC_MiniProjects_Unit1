# Mini Project 1.1 — Simulating Link Budgets and Coverage Range

## Authors

1. Abel NIYIGENA — 223026691
2. Marie Ange TUYIZERE IRADUKUNDA — 223026692
3. Remy Boris RWIGAMBA — 223026974

**Course:** Mobile Communications — Unit 1 Laboratory
**Reference:** MC-MP_Unit1.pdf, Section 1.10
**Source Code:** `src/link_budget.py`
**Generated Plots:**

* `plots/link_budget_comparison.png`
* `plots/link_budget_with_midband.png`
* `plots/snr_capacity.png`

**Generated Data:** `results/link_budget_summary.csv`

---

# 1. Introduction

This mini project investigates the relationship between carrier frequency, free-space path loss, received signal power, link margin, coverage range, signal-to-noise ratio (SNR), and theoretical channel capacity. The analysis is based on the link-budget and free-space path-loss (FSPL) models introduced in Section 1.10 of the Mobile Communications course material.

The simulation compares links operating at **700 MHz** and **28 GHz**, with an additional **3.5 GHz** mid-band scenario introduced to examine the trade-off between coverage and available capacity. The analysis also considers the effects of antenna gain, additional propagation losses, shadow margin, transmit power, bandwidth, and TDD guard periods.

The objective is to demonstrate quantitatively how frequency and link-budget parameters influence wireless coverage and theoretical capacity.

---

# 2. Methodology

## 2.1 Free-Space Path Loss

The free-space path loss is calculated using:

$$
L_{\mathrm{dB}}
=
20\log_{10}(d_{\mathrm{km}})
+
20\log_{10}(f_{\mathrm{MHz}})
+
32.44
$$

where:

* \(L_{\mathrm{dB}}\) is the free-space path loss in decibels;
* \(d_{\mathrm{km}}\) is the transmitter-receiver distance in kilometres;
* \(f_{\mathrm{MHz}}\) is the carrier frequency in megahertz.

This equation shows that path loss increases with both distance and carrier frequency.

---

## 2.2 Link-Budget Equation

The received power is determined using the following link-budget equation:

$$
P_{\mathrm{RX}}
=
P_{\mathrm{TX}}
+
G_{\mathrm{TX}}
-
L_{\mathrm{path}}
+
G_{\mathrm{RX}}
-
L_{\mathrm{other}}
$$

where:

* \(P_{\mathrm{RX}}\) is the received power in dBm;
* \(P_{\mathrm{TX}}\) is the transmit power in dBm;
* \(G_{\mathrm{TX}}\) is the transmitter antenna gain in dBi;
* \(G_{\mathrm{RX}}\) is the receiver antenna gain in dBi;
* \(L_{\mathrm{path}}\) is the propagation path loss in dB;
* \(L_{\mathrm{other}}\) represents additional system or propagation losses.

The common simulation parameters are summarized below.

| Parameter                               |   Base Value |        Modified Value Where Applicable |
| --------------------------------------- | -----------: | -------------------------------------: |
| Transmit power, \(P_{\mathrm{TX}}\)     |       40 dBm | 80 dBm for the power-doubling analysis |
| Transmitter gain, \(G_{\mathrm{TX}}\)   |       15 dBi |                       24 dBi in Task 1 |
| Receiver gain, \(G_{\mathrm{RX}}\)      |        0 dBi |                                      — |
| Additional loss, \(L_{\mathrm{other}}\) |         3 dB |                        11 dB in Task 3 |
| Receiver sensitivity                    |     −100 dBm |                                      — |
| Reference distance                      |         1 km |                                      — |
| Noise floor                             |     −104 dBm |                                      — |
| Bandwidth                               |       10 MHz |                       20 MHz in Task 5 |
| Distance sweep                          | 0.01–1000 km |                                      — |

Since the 700 MHz and 28 GHz scenarios use identical transmitter and receiver parameters, differences between their baseline curves are primarily attributable to the carrier-frequency term in the FSPL equation.

---

# 3. Base-Scenario Results

The baseline simulation was performed for 700 MHz and 28 GHz. An additional 28 GHz case incorporating 30 dB of excess loss was included to represent the impact of practical propagation losses that are not captured by the ideal free-space model.

| Band / Scenario             | Path Loss @ 1 km | \(P_{\mathrm{RX}}\) @ 1 km | Link Margin | Maximum Range | SNR @ 1 km | Capacity @ 1 km |
| --------------------------- | ---------------: | -------------------------: | ----------: | ------------: | ---------: | --------------: |
| 700 MHz                     |         89.34 dB |                 −37.34 dBm |    62.59 dB |     ≥ 1000 km |   66.59 dB |   221.21 Mbit/s |
| 28 GHz (free space)         |        121.38 dB |                 −69.38 dBm |    30.55 dB |      33.31 km |   34.55 dB |   114.78 Mbit/s |
| 28 GHz (+30 dB excess loss) |        121.38 dB |                 −99.38 dBm |     0.55 dB |       1.07 km |    4.55 dB |    19.45 Mbit/s |

At a reference distance of 1 km, the path-loss difference between 700 MHz and 28 GHz is approximately **32.04 dB**. This difference is given by:

$$
20\log_{10}\left(\frac{28000}{700}\right)
=
32.04\text{ dB}
$$

Therefore, the difference between the two baseline curves is directly explained by the frequency-dependent component of the FSPL equation.

The 700 MHz link does not reach the receiver-sensitivity threshold within the simulated distance interval of 0.01–1000 km. Consequently, its reported range of ≥1000 km represents a **lower bound imposed by the simulation sweep**, rather than the actual theoretical maximum range.

For the 28 GHz scenario, introducing an additional 30 dB loss reduces the received power at 1 km to approximately −99.38 dBm and reduces the predicted range to approximately 1.07 km. This illustrates the significant effect of practical propagation losses on high-frequency links.

---

# 4. Laboratory Task Results

## 4.1 Task 1 — Effect of Increasing Transmitter Antenna Gain

For the 28 GHz link, the transmitter antenna gain was increased from **15 dBi to 24 dBi**, corresponding to a 9 dB increase.

The resulting maximum range increased from:

$$
33.31\text{ km}
\rightarrow
94.04\text{ km}
$$

This corresponds to a range increase factor of:

$$
\frac{94.04}{33.31}
\approx 2.82
$$

The theoretical relationship is:

$$
10^{9/20}=2.82
$$

Therefore, an increase in link budget of 9 dB produces approximately a **2.82-fold increase in coverage range** under the FSPL model.

This result demonstrates that additional antenna gain can compensate for propagation loss. However, the relationship between dB gain and physical range is logarithmic rather than linear.

---

## 4.2 Task 2 — Addition of the 3.5 GHz Mid-Band

A 3.5 GHz scenario was introduced to represent a typical mid-band cellular frequency.

At 1 km, the simulated received power is:

$$
P_{\mathrm{RX}}=-51.32\text{ dBm}
$$

Compared with 700 MHz, the received power is lower by:

$$
20\log_{10}\left(\frac{3500}{700}\right)
=
13.98\text{ dB}
$$

Compared with 28 GHz, it is higher by:

$$
20\log_{10}\left(\frac{28000}{3500}\right)
=
18.06\text{ dB}
$$

The resulting theoretical coverage range is approximately:

$$
270.6\text{ km}
$$

The 3.5 GHz result therefore lies between the 700 MHz and 28 GHz scenarios in terms of propagation loss and coverage. This illustrates the fundamental coverage-versus-capacity trade-off associated with different cellular frequency bands.

---

## 4.3 Task 3 — Effect of an Additional 8 dB Shadow Margin

An additional 8 dB shadow margin was introduced to evaluate the effect of additional propagation loss.

The resulting coverage ranges were:

| Band    | Original Range | Range with +8 dB Margin |           Reduction |
| ------- | -------------: | ----------------------: | ------------------: |
| 700 MHz |       ≥1000 km |                540.6 km | Approximately 1.85× |
| 28 GHz  |       33.31 km |                13.50 km | Approximately 2.47× |

The 28 GHz link experiences a proportionally greater reduction in range because its initial link margin is substantially smaller than that of the 700 MHz link.

This result demonstrates why high-frequency cellular systems are generally more sensitive to additional propagation losses and may require shorter inter-site distances and denser network deployment.

---

# 5. Task 4 — SNR and Shannon Capacity

The signal-to-noise ratio was calculated from the difference between received signal power and the noise floor:

$$
\mathrm{SNR}_{\mathrm{dB}}
=
P_{\mathrm{RX}}-P_{\mathrm{noise}}
$$

The theoretical channel capacity was then calculated using Shannon's capacity equation:

$$
C
=
B\log_2(1+\mathrm{SNR})
$$

where \(C\) is the theoretical channel capacity and \(B\) is the channel bandwidth.

The results at 1 km are:

| Scenario                   |      SNR | Theoretical Capacity |
| -------------------------- | -------: | -------------------: |
| 700 MHz                    | 66.59 dB |        221.21 Mbit/s |
| 28 GHz                     | 34.55 dB |        114.78 Mbit/s |
| 28 GHz + 30 dB excess loss |  4.55 dB |         19.45 Mbit/s |

The results show that capacity does not vary linearly with received power because SNR appears inside the logarithmic term of the Shannon equation.

At high SNR, increases in received power produce relatively small improvements in theoretical capacity. Conversely, when the SNR approaches a low operating region, capacity decreases significantly.

The realistic 28 GHz case demonstrates this effect: the additional 30 dB propagation loss reduces the SNR to 4.55 dB and the theoretical capacity to approximately 19.45 Mbit/s.

---

# 6. Task 5 — Effect of Transmit Power and Bandwidth

The effect of doubling transmit power was compared with the effect of doubling bandwidth.

| Band    | Baseline Capacity | Double \(P_{\mathrm{TX}}\) |       Double Bandwidth |
| ------- | ----------------: | -------------------------: | ---------------------: |
| 700 MHz |     221.21 Mbit/s |     231.18 Mbit/s (1.045×) | 442.42 Mbit/s (2.000×) |
| 28 GHz  |     114.78 Mbit/s |     124.74 Mbit/s (1.087×) | 229.56 Mbit/s (2.000×) |

The results follow directly from Shannon's capacity equation:

$$
C=B\log_2(1+\mathrm{SNR})
$$

Bandwidth, \(B\), acts as a direct multiplier. Consequently, doubling the bandwidth results in exactly twice the theoretical capacity when all other parameters remain constant.

Transmit power, on the other hand, affects SNR and therefore appears inside the logarithmic term. As a result, doubling transmit power produces only a relatively modest capacity increase.

In the simulated scenarios, doubling transmit power increases capacity by approximately **4.5% at 700 MHz** and **8.7% at 28 GHz**, whereas doubling bandwidth produces a **100% increase** in theoretical capacity.

---

# 7. Task 6 — TDD Guard Periods

For a time-division duplexing (TDD) system with a guard fraction of 1/20, the effective capacity loss associated with the guard interval can be expressed as:

$$
L_{\mathrm{guard}}
=
-10\log_{10}\left(\frac{19}{20}\right)
$$

which gives approximately:

$$
L_{\mathrm{guard}}\approx0.223\text{ dB}
$$

Thus, the guard interval introduces a relatively small fixed loss in effective link budget.

Frequency-division duplexing (FDD) does not require the same type of time-domain guard period between uplink and downlink transmissions. However, FDD uses separate frequency resources and does not provide the same flexibility to dynamically adjust the uplink/downlink allocation.

Therefore, TDD introduces a small overhead in exchange for greater flexibility in allocating radio resources between uplink and downlink traffic.

---

# 8. FSPL Analysis: Effect of Frequency on Coverage Range

The maximum propagation distance can be obtained by setting the received power equal to the receiver sensitivity:

$$
P_{\mathrm{RX}}=P_{\mathrm{sens}}
$$

Rearranging the link-budget equation and the FSPL equation shows that, under the free-space model:

$$
d_{\max}\propto\frac{1}{f}
$$

Therefore, the theoretical coverage range is inversely proportional to carrier frequency when the remaining link-budget parameters are held constant.

For example, increasing the carrier frequency from 700 MHz to 28 GHz represents a factor of:

$$
\frac{28000}{700}=40
$$

Therefore, the ideal FSPL model predicts a range reduction by a factor of approximately 40.

However, the 700 MHz simulation reports a range of ≥1000 km because the selected simulation interval terminates at 1000 km before the sensitivity threshold is reached. Consequently, the measured ratio cannot directly demonstrate the theoretical 40-fold relationship within the selected sweep.

Extending the simulation range would allow the sensitivity threshold to be reached and would provide a direct numerical verification of the theoretical relationship.

---

# 9. Interpretation of the Simulation Results

The simulation demonstrates several important properties of wireless link budgets.

### 9.1 Frequency Dependence

Carrier frequency directly affects free-space path loss. For identical transmit power, antenna gains, distance, and other losses, increasing the carrier frequency increases the propagation loss.

The approximately 32 dB difference between 700 MHz and 28 GHz at 1 km is therefore a direct consequence of the frequency term in the FSPL equation.

---

### 9.2 Relationship Between Link Budget and Range

Because distance appears in the FSPL equation through:

$$
20\log_{10}(d)
$$

a change in link budget produces a multiplicative change in range.

For example:

* 6 dB of additional link budget approximately doubles the range;
* 20 dB approximately increases the range by a factor of 10;
* 9 dB produces approximately a 2.82-fold increase.

This relationship was confirmed by Task 1, where a 9 dB increase in transmitter antenna gain increased the theoretical 28 GHz range from 33.31 km to 94.04 km.

---

### 9.3 Frequency Gap and Antenna Gain

The approximately 32 dB loss difference between 700 MHz and 28 GHz would theoretically require a comparable increase in antenna gain to compensate for it if all other parameters remained unchanged.

For a transmitter-only compensation, the required gain would be approximately:

$$
G_{\mathrm{TX}}
=
15+32.04
\approx47.04\text{ dBi}
$$

Such high gain would generally require highly directional antenna systems, such as large phased arrays, particularly at millimetre-wave frequencies.

---

# 10. Practical Limitations of the Free-Space Model

The FSPL model represents an ideal propagation environment and does not account for several effects encountered in practical wireless systems.

These include:

* atmospheric absorption;
* rain attenuation;
* foliage losses;
* building penetration losses;
* diffraction;
* multipath propagation;
* shadowing;
* blockage by physical obstacles.

These effects can become particularly significant at higher frequencies.

The simulation illustrates this limitation by introducing an additional 30 dB loss to the 28 GHz scenario. The predicted range decreases from:

$$
33.31\text{ km}
\rightarrow
1.07\text{ km}
$$

This demonstrates how additional propagation losses can substantially reduce the coverage predicted by an ideal FSPL model.

Consequently, practical high-frequency cellular networks generally require appropriate antenna configurations, beam management, and denser cell deployment to compensate for the increased propagation loss and sensitivity to blockage.

---

# 11. Reproducibility

The simulation can be reproduced using the following PowerShell commands:

```powershell
cd 'C:\Users\Anum\Desktop\Academic\2027\mobile_comm\project\MC_MiniProject_1_1'
..\.venv\Scripts\Activate.ps1
python src\link_budget.py
```

The program produces the following outputs:

1. A base link-budget results table in the console;
2. Numerical results for Tasks 1–6;
3. `plots/link_budget_comparison.png`;
4. `plots/link_budget_with_midband.png`;
5. `plots/snr_capacity.png`;
6. `results/link_budget_summary.csv`.

These outputs provide both numerical and graphical evidence for the analysis presented in this report.

---

# 12. Conclusion

This mini project investigated the effects of carrier frequency, antenna gain, propagation loss, shadow margin, transmit power, bandwidth, and TDD guard periods on wireless link performance.

The simulation confirmed the fundamental behaviour predicted by the free-space path-loss model. In particular, the 700 MHz and 28 GHz scenarios exhibit an approximately **32 dB difference in path loss at 1 km**, which is entirely explained by the frequency-dependent term of the FSPL equation. The analysis also confirmed that theoretical coverage range varies approximately as \(f^{-1}\) when all other link-budget parameters remain constant.

The results further demonstrated that additional antenna gain can substantially increase coverage range, while additional propagation losses can significantly reduce the practical coverage of high-frequency links. The 3.5 GHz scenario provided an intermediate case between the lower-frequency 700 MHz and higher-frequency 28 GHz systems.

The Shannon-capacity analysis showed that bandwidth has a linear effect on theoretical capacity, whereas transmit power affects capacity through the logarithmic SNR term. Consequently, doubling the simulated bandwidth doubled the theoretical capacity, while doubling transmit power resulted in comparatively smaller increases.

Finally, the introduction of additional losses at 28 GHz demonstrated the difference between an ideal free-space model and practical wireless propagation. These results emphasize the importance of considering both link-budget calculations and real propagation conditions when evaluating cellular network coverage and capacity.
