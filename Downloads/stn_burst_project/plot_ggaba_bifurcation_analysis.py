#!/usr/bin/env python3
"""
plot_ggaba_bifurcation_analysis.py

Synaptic Conductance (g_GABA) Sweep & Bifurcation Analysis:
1. Phase Plane: V-nullcline vs w-nullcline for g_GABA = 0.20, 0.64 (Normal), 1.14 (PD), 3.20 & 3.50 nS (SN Bifurcation threshold).
   - Full y-axis range [-140, 120] to clearly show the full w-nullcline step down to -122.4 pA at V = -70 mV.
   - Shows exact intersection points (Fixed Points) where parabola meets the purple line.
2. Gap vs g_GABA: Demonstrates Saddle-Node Bifurcation at g_GABA ≈ 3.20 nS (where FP count goes 0 -> 2).
3. Membrane Potential Traces V(t): Shows Tonic -> Rebound Burst Cluster -> Silent regime changes as g_GABA varies.
4. Quantitative Firing Rate & CV curves vs g_GABA.
"""

import sys, os
sys.path.insert(0, "/Users/jieun/Downloads/stn_burst_project")

_MPL_CACHE = "/Users/jieun/Downloads/stn_burst_project/figures/.mplcache"
os.makedirs(_MPL_CACHE, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", _MPL_CACHE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from pathlib import Path

from stn_borderline_tonic_burst_transition import simulate_ad_ex, MECHANISM_COLUMNS
from pd_input_patterns import generate_scenario

# AdEx Base Constants (Lindahl 2016)
g_L = 10.0; E_L = -80.2; V_T = -64.0; dT = 16.2
a_PVp = -12.0; GATE = -70.0; E_AMPA = 0.0; E_GABA = -84.0
V = np.linspace(-92, -44, 4000)

w_ampa_fixed = 0.35

def v_null(gG, gA=w_ampa_fixed, I=0.0):
    ea = np.minimum((V - V_T) / dT, 5.0)
    return (-g_L*(V-E_L) + g_L*dT*np.exp(ea)
            + gA*(E_AMPA-V) + gG*(E_GABA-V) + I)

def w_null_pvp():
    # w = a*(V - E_L) for V < GATE, 0 for V >= GATE
    return np.where(V < GATE, a_PVp*(V - E_L), 0.0)

ww = w_null_pvp()

# Generate inputs strictly from Scenario 2 (Mallet 2008 Rat Pair - Scenario ID 11 for PD)
# CTX: 13.5 Hz + 20.5 Hz Beta, GPe: 14.6 Hz + 20.5 Hz Beta
TOTAL_MS = 3500.0
T_START, T_END = 2000.0, 3500.0
gpe_spikes_p, ctx_spikes_p, weights_p, _ = generate_scenario(11, total_ms=TOTAL_MS, n_gpe=30, n_ctx=80, seed=42)

p_pv_plus = MECHANISM_COLUMNS["PV+ Dynamic Reset ON"]

# Sweep values for g_GABA
g_gaba_list = [0.20, 0.64, 1.14, 2.20, 3.50]
labels_list = [
    "g_GABA = 0.20 nS (Weak Inh → High Tonic Firing)",
    "g_GABA = 0.64 nS (Normal Baseline → Regular Firing)",
    "g_GABA = 1.14 nS (PD Elevated Inh → Rebound Burst)",
    "g_GABA = 2.20 nS (Strong Inh → Sparse Rebound)",
    "g_GABA = 3.50 nS (SN Bifurcation → Near Silent / FP=2)"
]
colors_list = ["#1565c0", "#2e7d32", "#c62828", "#6a1b9a", "#333333"]

# 1. Simulate V(t) traces for key g_GABA values
sim_results = []
for gG in g_gaba_list:
    t, v, _, _, fr, cv = simulate_ad_ex(
        p_pv_plus, gpe_spikes_p, ctx_spikes_p,
        g_gaba=gG, w_ampa=0.35, g_nmda=0.15,
        total_ms=TOTAL_MS, use_dynamic_reset=True
    )
    sim_results.append((t, v, fr, cv))

# 2. Fine sweep for FR and CV curve vs g_GABA
gG_fine = np.linspace(0.1, 4.0, 35)
fr_fine, cv_fine = [], []
for gG in gG_fine:
    _, _, _, _, fr, cv = simulate_ad_ex(
        p_pv_plus, gpe_spikes_p, ctx_spikes_p,
        g_gaba=gG, w_ampa=0.35, g_nmda=0.15,
        total_ms=TOTAL_MS, use_dynamic_reset=True
    )
    fr_fine.append(fr)
    cv_fine.append(cv)

fr_fine = np.array(fr_fine)
cv_fine = np.array(cv_fine)

# Create Figure layout (2x2 grid)
fig = plt.figure(figsize=(17, 11), facecolor="white")
fig.suptitle(
    "Scenario 2 (Mallet 2008 Rat) — Synaptic Weight (g_GABA) Sweep & Bifurcation Analysis",
    fontsize=14, fontweight="bold", y=0.98
)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.34, wspace=0.24,
                       left=0.06, right=0.96, top=0.92, bottom=0.07)

# Panel A: Uncut Phase Plane (V-nullcline vs w-nullcline with full y-axis range [-140, 120])
ax_a = fig.add_subplot(gs[0, 0])
ax_a.axvspan(-92, GATE, color="#fff3e0", alpha=0.35)
ax_a.axvspan(GATE, -44, color="#e8f5e9", alpha=0.25)
ax_a.axhline(0, color="#ccc", lw=0.7)
ax_a.axvline(GATE, color="#aaa", lw=0.7, ls=":")
ax_a.axvline(V_T, color="#aaa", lw=0.7, ls="--")
ax_a.text(V_T + 0.3, 112, "$V_T$", fontsize=9, color="#555")
ax_a.text(GATE - 0.8, -135, "Gate V=-70 mV\n(w drops to -122 pA)", fontsize=8, color="#6a1b9a", fontweight="bold")

# Full w-nullcline
ax_a.plot(V, ww, color="#6a1b9a", lw=3.2, label="w-nullcline (PV+)", zorder=10)
# Draw the vertical connection at V = -70 mV to make the step down visually clear
ax_a.plot([-70.0, -70.0], [0.0, a_PVp * (-70.0 - E_L)], color="#6a1b9a", lw=3.2, zorder=10)

for gG, lbl, col in zip(g_gaba_list, labels_list, colors_list):
    wv = v_null(gG, gA=0.35)
    ls = "--" if gG >= 3.20 else "-"
    ax_a.plot(V, wv, color=col, lw=1.9, ls=ls, label=f"{lbl.split(' (')[0]}")

# Mark the exact Saddle-Node Bifurcation intersection point (FP creation)
# At g_GABA ≈ 3.20 nS, parabola intersects w-nullcline at V = -70 mV, w = -122.4 pA
ax_a.scatter([-70.0], [-122.4], color="#d50000", s=120, marker="*", zorder=15, label="SN Bifurcation Intersection\n(FP created at g_GABA ≈ 3.2 nS)")
ax_a.annotate("SN Bifurcation FP\n(V=-70 mV, w=-122.4 pA)", xy=(-70.0, -122.4), xytext=(-88, -100),
            arrowprops=dict(arrowstyle="->", color="#d50000", lw=1.5),
            fontsize=8.5, color="#d50000", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="#ffebee", ec="#d50000", lw=1))

ax_a.set_xlim(-92, -44); ax_a.set_ylim(-145, 120)
ax_a.set_xlabel("Membrane Potential V (mV)", fontsize=10, fontweight="bold")
ax_a.set_ylabel("Adaptation w (pA)", fontsize=10, fontweight="bold")
ax_a.set_title("A. Complete Phase Plane (Uncut Y-axis [-145, 120] pA)\nIntersections (Fixed Points) shown at V=-70 mV step", fontsize=11, fontweight="bold")
ax_a.legend(loc="upper left", fontsize=7.8, framealpha=0.95)
ax_a.grid(True, alpha=0.2)
ax_a.spines["top"].set_visible(False); ax_a.spines["right"].set_visible(False)

# Panel B: Gap (V-null - w-null min) vs g_GABA showing SN Bifurcation
ax_b = fig.add_subplot(gs[0, 1])
gG_gap_sweep = np.linspace(0.1, 4.5, 200)
gaps = [float((v_null(gG, gA=0.35) - ww).min()) for gG in gG_gap_sweep]
gaps = np.array(gaps)

ax_b.fill_between(gG_gap_sweep, gaps, 0, where=(gaps >= 0), color="#43a047", alpha=0.2, label="gap > 0 → FP = 0 (Continuous Firing Regime)")
ax_b.fill_between(gG_gap_sweep, gaps, 0, where=(gaps < 0), color="#e53935", alpha=0.2, label="gap < 0 → FP = 2 (Resting / Silent State)")
ax_b.plot(gG_gap_sweep, gaps, color="#1a237e", lw=2.2)
ax_b.axhline(0, color="black", lw=1.2, ls="--", label="Bifurcation Boundary (gap = 0)")

sn_threshold = gG_gap_sweep[np.where(np.diff(np.sign(gaps)))[0][0]]
ax_b.axvline(sn_threshold, color="#6a1b9a", ls="-.", lw=1.5)
ax_b.text(sn_threshold + 0.1, 12, f"Saddle-Node Bifurcation\ng_GABA ≈ {sn_threshold:.2f} nS", fontsize=9, color="#6a1b9a", fontweight="bold")

# Highlight Normal (0.64) & PD (0.88 ~ 1.14) Operating Regimes
ax_b.axvspan(0.64, 1.14, color="#ffeb3b", alpha=0.25, label="Physiological Operating Range")
ax_b.scatter([0.64, 1.14], [float((v_null(0.64, gA=0.35)-ww).min()), float((v_null(1.14, gA=0.35)-ww).min())], color=["#2e7d32", "#c62828"], s=80, zorder=8)
ax_b.text(0.64, 28, "Normal (0.64 nS)", fontsize=8.5, color="#2e7d32", fontweight="bold")
ax_b.text(1.14, 20, "PD (1.14 nS)", fontsize=8.5, color="#c62828", fontweight="bold")

ax_b.set_xlim(0.1, 4.5); ax_b.set_ylim(-50, 80)
ax_b.set_xlabel("g_GABA Conductance (nS)", fontsize=10, fontweight="bold")
ax_b.set_ylabel("min(V-null - w-null) [pA]", fontsize=10, fontweight="bold")
ax_b.set_title("B. Fixed Point Existence & SN Bifurcation Threshold\n(FP = 0 in Normal/PD range; FP = 2 only when g_GABA > 3.2 nS)", fontsize=11, fontweight="bold")
ax_b.legend(loc="lower right", fontsize=8, framealpha=0.95)
ax_b.grid(True, alpha=0.2)
ax_b.spines["top"].set_visible(False); ax_b.spines["right"].set_visible(False)

# Panel C: Stacked Membrane Potential Traces V(t) across g_GABA values
gs_c = gridspec.GridSpecFromSubplotSpec(len(g_gaba_list), 1, subplot_spec=gs[1, 0], hspace=0.15)
for idx, (gG, lbl, col) in enumerate(zip(g_gaba_list, labels_list, colors_list)):
    t, v, fr, cv = sim_results[idx]
    mask = (t >= T_START) & (t <= T_END)
    ax = fig.add_subplot(gs_c[idx])
    ax.plot(t[mask], v[mask], color=col, lw=1.0)
    ax.axhline(-70, color="gray", lw=0.5, ls=":", alpha=0.5)
    ax.set_xlim(T_START, T_END); ax.set_ylim(-90, 25)
    ax.set_ylabel("Vm", fontsize=7.5)
    ax.set_title(f"{lbl}  |  FR: {fr:.1f} Hz, CV: {cv:.2f}", fontsize=8, fontweight="bold", color=col, pad=2)
    ax.tick_params(labelsize=7)
    if idx < len(g_gaba_list) - 1:
        ax.set_xticklabels([])
    else:
        ax.set_xlabel("Time (ms)", fontsize=8, fontweight="bold")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# Panel D: Firing Rate & CV vs g_GABA Sweep (Dynamic Regime Transition)
ax_d = fig.add_subplot(gs[1, 1])
ax_d_twin = ax_d.twinx()

line1 = ax_d.plot(gG_fine, fr_fine, color="#1565c0", lw=2.0, marker="o", ms=3, label="Firing Rate (Hz)")
line2 = ax_d_twin.plot(gG_fine, cv_fine, color="#c62828", lw=2.0, marker="s", ms=3, ls="--", label="CV (Burst Indicator)")

ax_d.axvline(3.20, color="#6a1b9a", ls="-.", lw=1.2, label="SN Bifurcation (g_GABA ≈ 3.2 nS)")
ax_d.axvspan(0.64, 1.14, color="#ffeb3b", alpha=0.2, label="Physiological Range (Normal~PD)")

ax_d.set_xlabel("g_GABA Conductance (nS)", fontsize=10, fontweight="bold")
ax_d.set_ylabel("Firing Rate (Hz)", fontsize=10, fontweight="bold", color="#1565c0")
ax_d_twin.set_ylabel("Coefficient of Variation (CV)", fontsize=10, fontweight="bold", color="#c62828")

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax_d.legend(lines, labels, loc="upper right", fontsize=8, framealpha=0.95)
ax_d.set_title("D. Firing Rate & Burstiness (CV) vs g_GABA\n(Tonic Firing → High-CV Rebound Burst → Silent)", fontsize=11, fontweight="bold")
ax_d.grid(True, alpha=0.2)
ax_d.spines["top"].set_visible(False)
ax_d_twin.spines["top"].set_visible(False)

out = Path("results/ggaba_bifurcation_analysis.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"✅ Saved updated figure to {out.resolve()}")
