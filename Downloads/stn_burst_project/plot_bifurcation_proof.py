#!/usr/bin/env python3
"""
plot_bifurcation_proof.py

Focused visualization: I_syn을 바꿔도 Fixed Point가 안 생긴다는 것을 Phase Plane에서 직접 보여줌

Left panel  — Phase plane: I_syn 값별 V-nullcline 여러 개를 겹쳐 그림
              w-nullcline(직선)이 어느 곡선과도 만나지 않음을 보임

Right panel — min gap(V-null - w-null) vs I_syn 스위프
              gap > 0 이면 교점 없음(FP=0), gap < 0 이면 교점 존재(FP>0)
              Normal/PD 운영점 표시
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
from pathlib import Path

# ── AdEx parameters (Lindahl 2016 Table 6) ───────────────────────────────────
g_L  = 10.0;  E_L = -80.2;  V_T = -64.0;  dT = 16.2
a_PVp = -12.0;  GATE = -70.0
E_AMPA, E_GABA = 0.0, -84.0

V = np.linspace(-92, -44, 3000)

def v_null(gA, gG, I_scalar=0.0):
    ea = np.minimum((V - V_T) / dT, 5.0)
    return (-g_L*(V-E_L) + g_L*dT*np.exp(ea)
            + gA*(E_AMPA-V) + gG*(E_GABA-V)
            + I_scalar)

def w_null_pvp():
    return np.where(V < GATE, a_PVp*(V - E_L), 0.0)

ww = w_null_pvp()

# Base conductances: Mallet 2008 Normal (Sc10)
gA_base, gG_base = 0.25, 0.64

# ── I_syn sweep values ────────────────────────────────────────────────────────
I_values = np.array([-30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 80])
# Color: negative I_syn = cool (blue), positive = warm (red)
cmap = plt.cm.RdYlBu_r
norm_c = plt.Normalize(I_values.min(), I_values.max())

# min gap for each I_syn (positive = no crossing = FP count 0)
I_sweep = np.linspace(-60, 100, 600)
min_gaps = []
for I in I_sweep:
    wv = v_null(gA_base, gG_base, I)
    gap = wv - ww           # positive where V-null > w-null
    min_gaps.append(float(gap.min()))
min_gaps = np.array(min_gaps)

# ─────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 5.5), facecolor="white")
fig.suptitle(
    "Why I_syn is NOT a Bifurcation Parameter: Phase Plane Evidence",
    fontsize=13, fontweight="bold", y=0.99
)
fig.text(
    0.5, 0.95,
    "Varying I_syn shifts the V-nullcline vertically.\n"
    "But the V-nullcline (parabola) NEVER crosses the w-nullcline (line) "
    "in the Normal/PD operating range  →  Fixed Point count stays 0.",
    ha="center", fontsize=10, color="#333"
)

gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.32,
                       left=0.07, right=0.97, top=0.84, bottom=0.12,
                       width_ratios=[1.35, 1.0])

# ═══════════════════════════════════════════════════════════════════════════
# LEFT: Phase plane — V-nullclines for each I_syn
# ═══════════════════════════════════════════════════════════════════════════
ax = fig.add_subplot(gs[0])

# Zone shading
ax.axvspan(-92, GATE, color="#fff3e0", alpha=0.5)
ax.axvspan(GATE, -44, color="#e8f5e9", alpha=0.5)
ax.text(-90, 105, "Zone 1\nV < -70 mV\n(a-gate ON)", fontsize=8,
        color="#bf360c", va="top")
ax.text(-65, 105, "Zone 2\nV > -70 mV\n(a-gate OFF)", fontsize=8,
        color="#2e7d32", va="top")

# w-nullcline — prominent
ax.plot(V, ww, color="#6a1b9a", lw=2.8, zorder=10,
        label="w-nullcline  PV+  (a = -12 nS)")

# V-nullclines for each I_syn value
for I in I_values:
    wv = v_null(gA_base, gG_base, I)
    col = cmap(norm_c(I))
    lw = 2.2 if I in (0, 10) else 1.4
    alpha = 1.0 if I in (0, 10) else 0.70
    label = f"I_syn = {I:+.0f} pA"
    if I == 0:
        label += "  ← Normal operating point"
    if I == 10:
        label += "  ← PD approx"
    ax.plot(V, wv, color=col, lw=lw, alpha=alpha, zorder=5, label=label)

# Arrow annotations showing "gap" between closest approach and w-null
# Pick I=0 as example
wv0 = v_null(gA_base, gG_base, 0.0)
idx_min = int(np.argmin(wv0 - ww))   # where the gap is smallest
v_closest = V[idx_min]
w_null_closest = ww[idx_min]
v_null_closest = wv0[idx_min]
ax.annotate("",
    xy=(v_closest, w_null_closest),
    xytext=(v_closest, v_null_closest),
    arrowprops=dict(arrowstyle="<->", color="#e53935", lw=1.8))
ax.text(v_closest + 1.0, (w_null_closest + v_null_closest) / 2,
        f"min gap\n= {v_null_closest - w_null_closest:.1f} pA\n(I_syn = 0)",
        fontsize=8.5, color="#e53935", fontweight="bold", va="center")

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_c)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.01, shrink=0.8)
cbar.set_label("I_syn (pA)", fontsize=9)

ax.set_xlim(-92, -44); ax.set_ylim(-30, 115)
ax.axhline(0, color="#bbb", lw=0.7)
ax.axvline(GATE, color="#999", lw=0.8, ls=":")
ax.axvline(V_T,  color="#999", lw=0.8, ls="--")
ax.text(V_T + 0.3, 112, "$V_T$", fontsize=9, color="#555")
ax.set_xlabel("Membrane Potential V (mV)", fontsize=11, fontweight="bold")
ax.set_ylabel("Adaptation w (pA)", fontsize=11, fontweight="bold")
ax.set_title("Phase Plane: I_syn sweep\n(parabola color = I_syn value; purple line = w-nullcline)",
             fontsize=10.5, fontweight="bold")
ax.legend(loc="upper left", fontsize=7.5, framealpha=0.96, ncol=1)
ax.grid(True, alpha=0.2)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# ═══════════════════════════════════════════════════════════════════════════
# RIGHT: min gap vs I_syn
# ═══════════════════════════════════════════════════════════════════════════
ax2 = fig.add_subplot(gs[1])

# Color the line by sign
pos = min_gaps >= 0
neg = min_gaps < 0

ax2.fill_between(I_sweep, min_gaps, 0,
                 where=pos, color="#43a047", alpha=0.25,
                 label="gap > 0  →  FP = 0  (Firing)")
ax2.fill_between(I_sweep, min_gaps, 0,
                 where=neg, color="#e53935", alpha=0.25,
                 label="gap < 0  →  FP exists  (Silent)")
ax2.plot(I_sweep, min_gaps, color="#1565c0", lw=2.0, zorder=5)
ax2.axhline(0, color="black", lw=1.2, ls="--", label="FP boundary (gap = 0)")

# Mark the bifurcation point
bif_idx = np.where(np.diff(np.sign(min_gaps)))[0]
for bi in bif_idx:
    ax2.axvline(I_sweep[bi], color="black", lw=1.5, ls="-.", alpha=0.7)
    ax2.text(I_sweep[bi] + 1, min_gaps.max() * 0.55,
             f"Saddle-Node\nBifurcation\nI_syn ≈ {I_sweep[bi]:.0f} pA",
             fontsize=8.5, color="black", fontweight="bold")

# Mark Normal and PD operating points
# Compute actual gap at I_syn=0 (Normal) and I_syn~+10 (PD)
for I_op, label, col in [(0, "Normal\n(I_syn≈0)", "#2e7d32"),
                          (10, "PD approx\n(I_syn≈+10)", "#c62828")]:
    wv_op = v_null(gA_base, gG_base, I_op)
    gap_op = float((wv_op - ww).min())
    ax2.scatter([I_op], [gap_op], color=col, s=110, zorder=10)
    ax2.annotate(label, (I_op, gap_op),
                 xytext=(I_op + 5, gap_op - 4),
                 fontsize=9, color=col, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=col, lw=1.2))

ax2.set_xlim(I_sweep[0], I_sweep[-1])
ax2.set_xlabel("I_syn (pA)", fontsize=11, fontweight="bold")
ax2.set_ylabel("min(V-null − w-null)  [pA]\n(positive = no crossing)", fontsize=10, fontweight="bold")
ax2.set_title("Min gap between V-null and w-null\nvs. I_syn — where does FP appear?",
              fontsize=10.5, fontweight="bold")
ax2.legend(loc="lower right", fontsize=8.5, framealpha=0.96)
ax2.grid(True, alpha=0.2)
ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)

# Shaded region annotation for Normal/PD range
ax2.axvspan(0, 20, color="#ffeb3b", alpha=0.18, zorder=0,
            label="Normal/PD operating range")
ax2.text(1, min_gaps.min() * 0.6,
         "Normal / PD\noperating range\n(gap >> 0,  FP = 0)",
         fontsize=8.5, color="#f57f17", fontweight="bold")

out = Path("results/bifurcation_proof.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved {out.resolve()}")
