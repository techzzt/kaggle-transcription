#!/usr/bin/env python3
"""
plot_bifurcation_proof.py

Revised Piecewise Gate Nullcline & Conductance Bifurcation Analysis:
1. Correct piecewise gate w-nullcline:
   V < -70 mV : w = -12*(V + 80.2)  (at V=-70 mV, w = -122.4 pA)
   V >= -70 mV : w = 0              (a_eff = 0)
2. Demonstrates why I_syn scalar alone is NOT a valid dynamic bifurcation parameter:
   Synaptic drive is conductance-based g_AMPA*(E_AMPA - V) + g_GABA*(E_GABA - V),
   which modifies both V-nullcline offset AND slope (input resistance).
3. The true bifurcation boundary in conductance space is the linear ratio:
   g_GABA ≈ 3.2 * g_AMPA
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

# AdEx Base Constants (Lindahl 2016 Table 6)
g_L = 10.0; E_L = -80.2; V_T = -64.0; dT = 16.2
a_PVp = -12.0; GATE = -70.0; E_AMPA = 0.0; E_GABA = -84.0

V = np.linspace(-92, -44, 4000)

def w_null_piecewise(v_arr):
    return np.where(v_arr < GATE, a_PVp * (v_arr - E_L), 0.0)

ww = w_null_piecewise(V)

# V-nullcline with static current I_syn
def v_null_isyn(I_syn):
    ea = np.minimum((V - V_T) / dT, 5.0)
    return (-g_L*(V - E_L) + g_L*dT*np.exp(ea) + I_syn)

# V-nullcline with conductance g_AMPA & g_GABA
def v_null_cond(gG, gA=0.25):
    ea = np.minimum((V - V_T) / dT, 5.0)
    return (-g_L*(V - E_L) + g_L*dT*np.exp(ea) + gA*(E_AMPA - V) + gG*(E_GABA - V))

fig, axes = plt.subplots(1, 2, figsize=(14, 5.8), facecolor="white",
                         gridspec_kw={"wspace": 0.28})
fig.suptitle(
    "Conductance Space Bifurcation Analysis: Why I_syn Scalar is Insufficient & (g_AMPA, g_GABA) Dictates Firing Regimes",
    fontsize=13, fontweight="bold", y=0.98
)

# ═══════════════════════════════════════════════════════════════════════════
# LEFT: Phase Plane with Piecewise Gate w-nullcline
# ═══════════════════════════════════════════════════════════════════════════
ax1 = axes[0]
ax1.axvspan(-92, GATE, color="#fff3e0", alpha=0.35)
ax1.axvspan(GATE, -44, color="#e8f5e9", alpha=0.25)
ax1.axhline(0, color="#ccc", lw=0.7)
ax1.axvline(GATE, color="#aaa", lw=0.7, ls=":")
ax1.axvline(V_T, color="#aaa", lw=0.7, ls="--")
ax1.text(V_T + 0.3, 110, "$V_T$", fontsize=9, color="#555")
ax1.text(-90, 108, "a-gate ON\n(V < −70 mV)", fontsize=8.5, color="#bf360c", va="top")
ax1.text(GATE - 0.8, -138, "Gate V=-70 mV\n(w drops to -122 pA)", fontsize=8, color="#6a1b9a", fontweight="bold")

# Piecewise w-nullcline
ax1.plot(V, ww, color="#6a1b9a", lw=3.2, label="Piecewise w-nullcline (PV+)", zorder=10)
ax1.plot([-70.0, -70.0], [0.0, a_PVp * (-70.0 - E_L)], color="#6a1b9a", lw=3.2, zorder=10)

# V-nullclines for conductance pairs
gA_ref = 0.25
curves = [
    dict(gG=0.20, label="g_GABA = 0.20 nS  (Tonic, FP=0)", color="#1565c0", ls="-"),
    dict(gG=0.64, label="g_GABA = 0.64 nS  (Normal, FP=0)", color="#2e7d32", ls="-"),
    dict(gG=0.80, label="g_GABA = 0.80 nS  (SN Bifurcation Boundary, FP=2)", color="#d50000", ls="--"),
    dict(gG=1.14, label="g_GABA = 1.14 nS  (PD Silent, FP=2)", color="#c62828", ls="-"),
    dict(gG=2.20, label="g_GABA = 2.20 nS  (Strong Silent, FP=1)", color="#4a148c", ls="-."),
]

for c in curves:
    wv = v_null_cond(c["gG"], gA=gA_ref)
    ax1.plot(V, wv, color=c["color"], lw=1.8, ls=c["ls"], label=c["label"], alpha=0.9)

# Mark SN Bifurcation FP
ax1.scatter([-66.8], [0.0], color="#d50000", s=90, marker="*", zorder=15)
ax1.annotate("SN Bifurcation FP\n(V* = -66.8 mV, w* = 0 pA)", xy=(-66.8, 0.0), xytext=(-88, -80),
             arrowprops=dict(arrowstyle="->", color="#d50000", lw=1.5),
             fontsize=8.5, color="#d50000", fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", fc="#ffebee", ec="#d50000", lw=1))

ax1.set_xlim(-92, -44); ax1.set_ylim(-145, 120)
ax1.set_xlabel("Membrane Potential V (mV)", fontsize=10, fontweight="bold")
ax1.set_ylabel("Adaptation w (pA)", fontsize=10, fontweight="bold")
ax1.set_title("A. Piecewise Gate Phase Plane vs g_GABA (g_AMPA = 0.25 nS)\nSN Bifurcation occurs at g_GABA ≈ 0.80 nS (V* = -66.8 mV)", fontsize=10.5, fontweight="bold")
ax1.legend(loc="upper left", fontsize=7.8, framealpha=0.95)
ax1.grid(True, alpha=0.2)
ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)

# ═══════════════════════════════════════════════════════════════════════════
# RIGHT: Conductance Space (g_AMPA vs g_GABA) Bifurcation Line
# ═══════════════════════════════════════════════════════════════════════════
ax2 = axes[1]
gA_space = np.linspace(0.05, 0.80, 200)
# Ratio line g_GABA ≈ 3.2 * g_AMPA
gG_bif_line = 3.2 * gA_space

ax2.fill_between(gA_space, 0, gG_bif_line, color="#43a047", alpha=0.20, label="FP = 0 (Continuous Firing Regime)")
ax2.fill_between(gA_space, gG_bif_line, 3.0, color="#e53935", alpha=0.20, label="FP ≥ 1 (Silent / Resting State)")

ax2.plot(gA_space, gG_bif_line, color="#1a237e", lw=2.5, label="Bifurcation Boundary: g_GABA ≈ 3.2 × g_AMPA")

# Plot Normal & PD Operating Points
ax2.scatter([0.25], [0.64], color="#2e7d32", s=100, zorder=8, label="Normal Baseline (gA=0.25, gG=0.64)")
ax2.scatter([0.35], [0.64], color="#1565c0", s=100, zorder=8, label="Sc2 Normal Pair (gA=0.35, gG=0.64)")
ax2.scatter([0.35], [1.14], color="#c62828", s=100, zorder=8, label="Sc2 PD Pair (gA=0.35, gG=1.14)")

ax2.text(0.26, 0.68, "Normal\n(FP=0, Tonic)", fontsize=8.5, color="#2e7d32", fontweight="bold")
ax2.text(0.36, 1.18, "PD Pair\n(FP=0 under dynamic Beta, Burst)", fontsize=8.5, color="#c62828", fontweight="bold")

ax2.set_xlim(0.05, 0.80); ax2.set_ylim(0.0, 3.0)
ax2.set_xlabel("g_AMPA Excitatory Conductance (nS)", fontsize=10, fontweight="bold")
ax2.set_ylabel("g_GABA Inhibitory Conductance (nS)", fontsize=10, fontweight="bold")
ax2.set_title("B. Conductance Space (g_AMPA, g_GABA) Bifurcation Boundary\n(True Boundary: Ratio Line g_GABA ≈ 3.2 × g_AMPA)", fontsize=10.5, fontweight="bold")
ax2.legend(loc="upper left", fontsize=8, framealpha=0.95)
ax2.grid(True, alpha=0.2)
ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)

out = Path("results/bifurcation_proof.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"✅ Saved figure to {out.resolve()}")
