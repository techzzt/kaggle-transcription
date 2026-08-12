#!/usr/bin/env python3
"""
plot_bifurcation_proof.py

Simplified: I_syn sweep phase plane — 3 key curves only.
왼쪽 패널 하나로 핵심 전달:
  - Normal / PD 운영점에서 V-nullcline이 w-nullcline과 만나지 않음 (FP = 0)
  - 오른쪽에는 같은 내용을 gap 수치로 보조 확인만 표시
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# ── AdEx parameters (Lindahl 2016 Table 6) ───────────────────────────────────
g_L = 10.0;  E_L = -80.2;  V_T = -64.0;  dT = 16.2
a_PVp = -12.0;  GATE = -70.0
E_AMPA, E_GABA = 0.0, -84.0

V = np.linspace(-92, -44, 3000)

def v_null(gA, gG, I=0.0):
    ea = np.minimum((V - V_T) / dT, 5.0)
    return (-g_L*(V-E_L) + g_L*dT*np.exp(ea)
            + gA*(E_AMPA-V) + gG*(E_GABA-V) + I)

def w_null_pvp():
    return np.where(V < GATE, a_PVp*(V - E_L), 0.0)

ww = w_null_pvp()

# Mallet base conductances
gA_base, gG_base = 0.25, 0.64

# ── Only 3 key curves ─────────────────────────────────────────────────────────
CURVES = [
    dict(I=0,   label="Normal  (I_syn = 0 pA)",        color="#1565c0", lw=2.4, ls="-",  zorder=6),
    dict(I=10,  label="PD approx  (I_syn = +10 pA)",   color="#c62828", lw=2.4, ls="-",  zorder=6),
    dict(I=-33, label="Bifurcation threshold  (I_syn ≈ −33 pA)\n← first crossing with w-nullcline",
                                                         color="#555",   lw=1.6, ls="--", zorder=5),
]

# gap sweep for right panel (simplified)
I_sweep = np.linspace(-60, 80, 500)
min_gaps = [float((v_null(gA_base, gG_base, I) - ww).min()) for I in I_sweep]
min_gaps = np.array(min_gaps)

# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), facecolor="white",
                         gridspec_kw={"width_ratios": [1.4, 1.0], "wspace": 0.30})
fig.suptitle(
    "I_syn is NOT a Bifurcation Parameter — Phase Plane Evidence",
    fontsize=13, fontweight="bold", y=1.00
)

# ═══════════════════════════════════════════════════════════════════════════
# LEFT: Phase Plane
# ═══════════════════════════════════════════════════════════════════════════
ax = axes[0]

# Minimal zone shading
ax.axvspan(-92, GATE, color="#fff3e0", alpha=0.40)
ax.axvspan(GATE, -44, color="#e8f5e9", alpha=0.30)
ax.axhline(0, color="#ccc", lw=0.7)
ax.axvline(GATE, color="#aaa", lw=0.8, ls=":")
ax.axvline(V_T,  color="#aaa", lw=0.8, ls="--")
ax.text(V_T + 0.3, 108, "$V_T$", fontsize=9.5, color="#555")
ax.text(-90, 108, "a-gate ON\n(V < −70)", fontsize=8.5, color="#bf360c", va="top")

# w-nullcline
ax.plot(V, ww, color="#6a1b9a", lw=3.0, zorder=10, label="w-nullcline  PV+")

# 3 V-nullclines
for c in CURVES:
    wv = v_null(gA_base, gG_base, c["I"])
    ax.plot(V, wv, color=c["color"], lw=c["lw"], ls=c["ls"],
            alpha=0.95, zorder=c["zorder"], label=c["label"])

# Annotate min gap for Normal and PD
for I_op, label, col, dy in [(0, "gap = {:.1f} pA\n(no crossing)", "#1565c0", 12),
                               (10, "gap = {:.1f} pA\n(no crossing)", "#c62828", -22)]:
    wv_op = v_null(gA_base, gG_base, I_op)
    gap_op = float((wv_op - ww).min())
    idx = int(np.argmin(wv_op - ww))
    v_pt = V[idx]; w_pt = ww[idx]; wvpt = wv_op[idx]
    # arrow between the two curves at closest point
    ax.annotate("", xy=(v_pt, w_pt), xytext=(v_pt, wvpt),
                arrowprops=dict(arrowstyle="<->", color=col, lw=1.5))
    ax.text(v_pt + 0.8, (w_pt + wvpt)/2 + dy,
            label.format(gap_op),
            fontsize=8.5, color=col, fontweight="bold", va="center")

ax.set_xlim(-92, -44); ax.set_ylim(-28, 118)
ax.set_xlabel("Membrane Potential V (mV)", fontsize=11, fontweight="bold")
ax.set_ylabel("Adaptation current w (pA)", fontsize=11, fontweight="bold")
ax.set_title("Phase Plane: V-nullcline (curves) vs w-nullcline (purple line)\n"
             "Curves shift up with I_syn — but never cross the purple line",
             fontsize=10, fontweight="bold")
ax.legend(loc="upper left", fontsize=9, framealpha=0.97)
ax.grid(True, alpha=0.18)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# ═══════════════════════════════════════════════════════════════════════════
# RIGHT: min gap vs I_syn — simplified
# ═══════════════════════════════════════════════════════════════════════════
ax2 = axes[1]

ax2.fill_between(I_sweep, min_gaps, 0,
                 where=min_gaps >= 0, color="#43a047", alpha=0.20,
                 label="No FP  →  Firing")
ax2.fill_between(I_sweep, min_gaps, 0,
                 where=min_gaps < 0, color="#e53935", alpha=0.20,
                 label="FP exists  →  Silent")
ax2.plot(I_sweep, min_gaps, color="#1a237e", lw=2.0)
ax2.axhline(0, color="black", lw=1.2, ls="--", label="FP boundary (gap = 0)")

# Bifurcation marker
bif = I_sweep[np.where(np.diff(np.sign(min_gaps)))[0][0]]
ax2.axvline(bif, color="#555", lw=1.3, ls="-.")
ax2.text(bif + 1, 10, f"Bifurcation\nI_syn ≈ {bif:.0f} pA", fontsize=8.5,
         color="#555", fontweight="bold")

# Normal and PD dots
for I_op, lbl, col in [(0, "Normal", "#1565c0"), (10, "PD approx", "#c62828")]:
    gap = float((v_null(gA_base, gG_base, I_op) - ww).min())
    ax2.scatter([I_op], [gap], color=col, s=100, zorder=8)
    ax2.text(I_op + 2, gap + 2, lbl, fontsize=9, color=col, fontweight="bold")

# Highlight Normal/PD range
ax2.axvspan(0, 10, color="#ffeb3b", alpha=0.20)
ax2.text(1, -25, "Normal/PD\nrange", fontsize=8.5, color="#f57f17", fontweight="bold")

ax2.set_xlim(-60, 80)
ax2.set_xlabel("I_syn (pA)", fontsize=11, fontweight="bold")
ax2.set_ylabel("min gap  (V-null − w-null)  [pA]\npositive = no intersection", fontsize=9.5)
ax2.set_title("Gap between curves vs I_syn\n(gap > 0  →  FP = 0  →  always firing)",
              fontsize=10, fontweight="bold")
ax2.legend(loc="lower right", fontsize=8.5, framealpha=0.97)
ax2.grid(True, alpha=0.18)
ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)

out = Path("results/bifurcation_proof.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved {out.resolve()}")
