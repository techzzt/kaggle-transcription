#!/usr/bin/env python3
"""
plot_synaptic_weight_bifurcation_membrane_only.py

Simple & Clean Membrane Potential V(t) Traces Figure:
Demonstrates that Synaptic Weight (g_GABA) acts as a true Bifurcation Parameter
moving the STN neuron between 3 distinct firing regimes:
  1. Tonic Firing Regime (Low g_GABA)
  2. Rebound Bursting Regime (Physiological PD g_GABA)
  3. Silent / Resting State (High g_GABA)
"""

import sys, os
sys.path.insert(0, "/Users/jieun/Downloads/stn_burst_project")

_MPL_CACHE = "/Users/jieun/Downloads/stn_burst_project/figures/.mplcache"
os.makedirs(_MPL_CACHE, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", _MPL_CACHE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from stn_borderline_tonic_burst_transition import simulate_ad_ex, MECHANISM_COLUMNS
from pd_input_patterns import generate_scenario

# Generate presynaptic inputs (Scenario 2: Mallet 2008 Rat Pair - Scenario ID 11 for PD)
TOTAL_MS = 3500.0
T_START, T_END = 2000.0, 3500.0
gpe_spikes, ctx_spikes, _, _ = generate_scenario(11, total_ms=TOTAL_MS, n_gpe=30, n_ctx=80, seed=42)

p_pvp = MECHANISM_COLUMNS["PV+ Dynamic Reset ON"]

# 3 Representative Synaptic Weights
weight_cases = [
    dict(g_gaba=0.20, label="Low Synaptic Weight (g_GABA = 0.20 nS)", regime="Tonic Firing Regime", color="#1565c0"),
    dict(g_gaba=1.14, label="PD Synaptic Weight (g_GABA = 1.14 nS)", regime="Rebound Bursting Regime", color="#c62828"),
    dict(g_gaba=3.20, label="High Synaptic Weight (g_GABA = 3.20 nS)", regime="Silent / Resting State", color="#333333"),
]

fig, axes = plt.subplots(len(weight_cases), 1, figsize=(12, 7.5), sharex=True, facecolor="white")
fig.suptitle(
    "Synaptic Weight (g_GABA) acts as a Firing Regime Bifurcation Parameter",
    fontsize=14, fontweight="bold", y=0.98
)

for idx, case in enumerate(weight_cases):
    gG = case["g_gaba"]
    t, v, _, _, fr, cv = simulate_ad_ex(
        p_pvp, gpe_spikes, ctx_spikes,
        g_gaba=gG, w_ampa=0.35, g_nmda=0.15,
        total_ms=TOTAL_MS, use_dynamic_reset=True
    )
    mask = (t >= T_START) & (t <= T_END)
    ax = axes[idx]
    
    ax.plot(t[mask], v[mask], color=case["color"], lw=1.2)
    ax.axhline(-70, color="gray", lw=0.6, ls=":", alpha=0.6, label="Reset / Gate Threshold (-70 mV)")
    
    ax.set_xlim(T_START, T_END)
    ax.set_ylim(-90, 25)
    ax.set_ylabel("Vm (mV)", fontsize=10, fontweight="bold")
    
    # Subplot Title & Annotations
    ax.set_title(
        f"{case['label']}  ➔  {case['regime']}  (Rate: {fr:.1f} Hz, CV: {cv:.2f})",
        fontsize=11, fontweight="bold", color=case["color"], loc="left", pad=4
    )
    ax.grid(True, alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

axes[-1].set_xlabel("Time (ms)", fontsize=11, fontweight="bold")

plt.tight_layout(rect=[0, 0, 1, 0.95])
out = Path("results/synaptic_weight_bifurcation_membrane_only.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"✅ Saved figure to {out.resolve()}")
