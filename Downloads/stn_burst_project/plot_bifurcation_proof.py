#!/usr/bin/env python3
"""
plot_bifurcation_proof.py — Phase Plane Fixed Point Analysis

최종 목표:
  Normal -> PD 전환 시 Phase Plane에서:
  1) Fixed Point가 몇 개인가? (개수 변화?)
  2) 안정점(Stable)인가 불안정점(Unstable)인가? (안정성 변화?)
  3) Bifurcation parameter는 I_syn인가 아닌가?

그래프 구성 (3 panels):
  Panel A: Normal vs PD Phase Plane  — V-nullcline + w-nullcline + 교점
  Panel B: I_syn sweep시 Fixed Point 개수 변화 (bifurcation diagram)
  Panel C: g_GABA sweep시 Fixed Point 개수 변화 (진짜 bifurcation parameter 탐색)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# ── AdEx parameters (Lindahl 2016 Table 6) ───────────────────────────────────
g_L   = 10.0    # nS  leak conductance
E_L   = -80.2   # mV  leak reversal
V_T   = -64.0   # mV  threshold potential
dT    = 16.2    # mV  slope factor (exponential)
a_PVm = 0.3     # nS  subthreshold adaptation (PV-)
a_PVp = -12.0   # nS  subthreshold adaptation (PV+, rebound)
GATE  = -70.0   # mV  a-gate: a only active when V < GATE

E_AMPA = 0.0    # mV
E_GABA = -84.0  # mV

V = np.linspace(-92, -44, 2000)

# ── Nullcline functions ───────────────────────────────────────────────────────
def v_nullcline(gA, gG):
    """dV/dt = 0  ↔  w = f(V)
    = -g_L(V-E_L) + g_L*dT*exp((V-V_T)/dT) + I_syn(V)
    where I_syn(V) = gA*(E_AMPA - V) + gG*(E_GABA - V)
    """
    ea = np.minimum((V - V_T) / dT, 5.0)
    I_leak = -g_L * (V - E_L)
    I_exp  = g_L * dT * np.exp(ea)
    I_syn  = gA * (E_AMPA - V) + gG * (E_GABA - V)
    return I_leak + I_exp + I_syn

def w_nullcline(a_nS):
    """dw/dt = 0  ↔  w = a*(V - E_L)  [only when V < GATE, else 0]"""
    return np.where(V < GATE, a_nS * (V - E_L), 0.0)

def find_fixed_points(wv, ww):
    """Find intersections of V-nullcline and w-nullcline.
    Returns list of (V_fp, w_fp, is_stable).
    Stable if at crossing V-nullcline is ABOVE w-nullcline on the left
    (i.e. the Jacobian has negative eigenvalues on the slow branch).
    """
    d = wv - ww
    fps = []
    for i in range(len(d) - 1):
        if d[i] * d[i+1] < 0:  # sign change = crossing
            # Linear interpolation
            t = d[i] / (d[i] - d[i+1])
            v_fp = V[i] + t * (V[i+1] - V[i])
            w_fp = ww[i] + t * (ww[i+1] - ww[i])
            # Stability heuristic: on the left branch (V < V_T) a fixed point
            # is stable if the V-nullcline approaches from above (slope of gap > 0)
            # i.e. d[i] > 0  (V-null ABOVE w-null just left of crossing)
            is_stable = d[i] > 0
            fps.append((v_fp, w_fp, is_stable))
    return fps

# ── Scenario operating points ─────────────────────────────────────────────────
# From pd_input_patterns.py generate_scenario results:
# Sc10 Normal (Mallet):  g_AMPA ~ 0.25, g_GABA ~ 0.64
# Sc11 PD    (Mallet):   g_AMPA ~ 0.35, g_GABA ~ 0.64
# Sc2  Normal (Lindahl): g_AMPA ~ 0.25, g_GABA ~ 0.50
# Sc4  PD    (Lindahl):  g_AMPA ~ 0.62, g_GABA ~ 0.42
scenarios = {
    "Sc1 Normal\n(Lindahl Baseline)": dict(gA=0.25, gG=0.50, color="#2e7d32", ls="-"),
    "Sc1 PD\n(Lindahl Baseline)":    dict(gA=0.62, gG=0.42, color="#c62828", ls="-"),
    "Sc2 Normal\n(Mallet 2008)":     dict(gA=0.25, gG=0.64, color="#1565c0", ls="--"),
    "Sc2 PD\n(Mallet 2008)":         dict(gA=0.35, gG=0.64, color="#e65100", ls="--"),
}

fig = plt.figure(figsize=(18, 6.5), facecolor="white")
fig.suptitle(
    "STN AdEx Phase Plane: Fixed Point Analysis — Normal vs PD\n"
    "Is I_syn the Bifurcation Parameter?",
    fontsize=13, fontweight="bold", y=0.98
)

gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.32,
                       left=0.06, right=0.97, top=0.88, bottom=0.12)

# ═══════════════════════════════════════════════════════════════════════════
# PANEL A — Phase Plane: Normal vs PD (all 4 scenarios overlaid)
# ═══════════════════════════════════════════════════════════════════════════
ax_a = fig.add_subplot(gs[0, 0])

# Zone shading
ax_a.axvspan(-92, GATE, color="#ffebee", alpha=0.25, label="Zone 1: V < -70 mV (a-gate ON)")
ax_a.axvspan(GATE, -44, color="#e8f5e9", alpha=0.25, label="Zone 2: V > -70 mV (a-gate OFF)")
ax_a.axhline(0, color="#ccc", lw=0.7)
ax_a.axvline(GATE, color="#999", lw=0.8, ls=":")
ax_a.axvline(V_T,  color="#999", lw=0.8, ls="--")
ax_a.text(V_T + 0.3, 115, "$V_T$", fontsize=9, color="#555")
ax_a.text(GATE - 3.5, 115, "a-gate", fontsize=8, color="#555")

# w-nullclines
ww_pvm = w_nullcline(a_PVm)
ww_pvp = w_nullcline(a_PVp)
ax_a.plot(V, ww_pvm, color="#1565c0", lw=2.0, zorder=5, label="w-null PV− (a=+0.3 nS)")
ax_a.plot(V, ww_pvp, color="#6a1b9a", lw=2.0, zorder=5, label="w-null PV+ (a=−12 nS)")

# V-nullclines for each scenario + fixed points
for name, sc in scenarios.items():
    wv = v_nullcline(sc["gA"], sc["gG"])
    ax_a.plot(V, wv, color=sc["color"], lw=1.8, ls=sc["ls"], alpha=0.85, zorder=4,
              label=f"{name.replace(chr(10), ' ')} (gA={sc['gA']:.2f}, gG={sc['gG']:.2f})")

    # Fixed points wrt PV+ w-nullcline (the rebound cell)
    fps = find_fixed_points(wv, ww_pvp)
    for vfp, wfp, stable in fps:
        marker = "o" if stable else "x"
        fc     = sc["color"] if stable else "white"
        ax_a.scatter([vfp], [wfp], marker=marker, s=110,
                     facecolor=fc, edgecolors=sc["color"], linewidths=2.2, zorder=10)
        label_txt = "Stable FP" if stable else "Unstable FP"
        ax_a.annotate(label_txt, (vfp, wfp), xytext=(vfp+1, wfp+10),
                      fontsize=7, color=sc["color"], fontweight="bold")

    # If NO fixed points, annotate
    if not fps:
        ax_a.text(0.02, 0.04, "FP = 0 → Continuous Firing",
                  transform=ax_a.transAxes, fontsize=7.5, color="#b71c1c",
                  fontweight="bold", ha="left")

ax_a.set_xlim(-92, -44); ax_a.set_ylim(-30, 120)
ax_a.set_xlabel("Membrane Potential V (mV)", fontsize=10, fontweight="bold")
ax_a.set_ylabel("Adaptation w (pA)", fontsize=10, fontweight="bold")
ax_a.set_title("A. Phase Plane: V-nullcline vs w-nullcline\n(● = Stable FP,  ✕ = Unstable FP,  없음 = Firing Regime)",
               fontsize=10, fontweight="bold")
ax_a.legend(loc="upper left", fontsize=6.5, framealpha=0.95, ncol=1)
ax_a.grid(True, alpha=0.25)
ax_a.spines["top"].set_visible(False); ax_a.spines["right"].set_visible(False)

# ═══════════════════════════════════════════════════════════════════════════
# PANEL B — I_syn (scalar) sweep: does adding a flat I_syn create FPs?
# ═══════════════════════════════════════════════════════════════════════════
ax_b = fig.add_subplot(gs[0, 1])

# Use Mallet Normal conductances as base (gA=0.25, gG=0.64)
gA_base, gG_base = 0.25, 0.64
I_sweep = np.linspace(-60, 80, 500)  # pA
n_fps_isyn = []

for I_val in I_sweep:
    # Add a constant scalar I_ext to V-nullcline
    ea = np.minimum((V - V_T) / dT, 5.0)
    wv = (-g_L*(V - E_L) + g_L*dT*np.exp(ea)
          + gA_base*(E_AMPA - V) + gG_base*(E_GABA - V)
          + I_val)   # <-- scalar shift
    fps = find_fixed_points(wv, ww_pvp)
    n_fps_isyn.append(len(fps))

ax_b.plot(I_sweep, n_fps_isyn, color="#1565c0", lw=2.2)
ax_b.axhline(0, color="#aaa", lw=0.8, ls="--")
ax_b.fill_between(I_sweep, n_fps_isyn, 0,
                  where=np.array(n_fps_isyn) > 0,
                  color="#e53935", alpha=0.25, label="FP exists (Silent / Rest state)")
ax_b.fill_between(I_sweep, n_fps_isyn, 0,
                  where=np.array(n_fps_isyn) == 0,
                  color="#43a047", alpha=0.20, label="FP = 0 (Continuous Firing)")

# Mark Normal and PD I_syn operating ranges
ax_b.axvline(0, color="#2e7d32", ls=":", lw=1.5, label="I_syn ≈ 0 (Mallet Normal)")
ax_b.axvline(10, color="#c62828", ls=":", lw=1.5, label="I_syn ≈ +10 (Mallet PD approx)")

# Annotate bifurcation point if any
bif_indices = np.where(np.diff(n_fps_isyn) != 0)[0]
for bi in bif_indices:
    ax_b.axvline(I_sweep[bi], color="black", ls="-.", lw=1.2, alpha=0.7)
    ax_b.text(I_sweep[bi]+1, 1.5, f"Bifurcation\nI_syn={I_sweep[bi]:.0f} pA",
              fontsize=7.5, color="black", fontweight="bold")

ax_b.set_xlim(I_sweep[0], I_sweep[-1])
ax_b.set_ylim(-0.3, 2.8)
ax_b.set_xlabel("Scalar I_syn (pA) — vertical shift of V-nullcline", fontsize=10, fontweight="bold")
ax_b.set_ylabel("Fixed Point Count", fontsize=10, fontweight="bold")
ax_b.set_title("B. Scalar I_syn sweep: does FP count change?\n(Mallet Normal base: gA=0.25, gG=0.64 fixed)",
               fontsize=10, fontweight="bold")
ax_b.legend(loc="upper right", fontsize=7.5, framealpha=0.95)
ax_b.grid(True, alpha=0.25)
ax_b.spines["top"].set_visible(False); ax_b.spines["right"].set_visible(False)

# ═══════════════════════════════════════════════════════════════════════════
# PANEL C — g_GABA sweep
# ═══════════════════════════════════════════════════════════════════════════
ax_c = fig.add_subplot(gs[0, 2])

gA_fixed = 0.25   # fix AMPA
gG_sweep = np.linspace(0.0, 5.0, 500)
n_fps_gaba_pvm = []
n_fps_gaba_pvp = []

for gG in gG_sweep:
    wv = v_nullcline(gA_fixed, gG)
    n_fps_gaba_pvm.append(len(find_fixed_points(wv, ww_pvm)))
    n_fps_gaba_pvp.append(len(find_fixed_points(wv, ww_pvp)))

ax_c.plot(gG_sweep, n_fps_gaba_pvp, color="#6a1b9a", lw=2.2, label="FP count (PV+ w-null)")
ax_c.plot(gG_sweep, n_fps_gaba_pvm, color="#1565c0", lw=1.8, ls="--", label="FP count (PV− w-null)")
ax_c.axhline(0, color="#aaa", lw=0.8, ls="--")

# Mark scenario operating points
for name, sc in scenarios.items():
    if sc["gA"] == gA_fixed:
        short = name.split("\n")[0]
        ax_c.axvline(sc["gG"], color=sc["color"], ls=":", lw=1.8, label=f"{short} gG={sc['gG']:.2f}")

# Annotate bifurcation(s)
bif_pvp = np.where(np.diff(n_fps_gaba_pvp) != 0)[0]
for bi in bif_pvp:
    ax_c.axvline(gG_sweep[bi], color="#6a1b9a", ls="-.", lw=1.3, alpha=0.8)
    ax_c.text(gG_sweep[bi]+0.05, 1.4, f"FP created\ng_GABA={gG_sweep[bi]:.2f}",
              fontsize=7.5, color="#6a1b9a", fontweight="bold")

ax_c.set_xlim(0, 5.0)
ax_c.set_ylim(-0.3, 2.8)
ax_c.set_xlabel("g_GABA (nS) — V-nullcline slope change", fontsize=10, fontweight="bold")
ax_c.set_ylabel("Fixed Point Count", fontsize=10, fontweight="bold")
ax_c.set_title("C. g_GABA sweep: FP count change?\n(True bifurcation parameter? gA=0.25 fixed)",
               fontsize=10, fontweight="bold")
ax_c.legend(loc="upper left", fontsize=7.5, framealpha=0.95)
ax_c.grid(True, alpha=0.25)
ax_c.spines["top"].set_visible(False); ax_c.spines["right"].set_visible(False)

# ─────────────────────────────────────────────────────────────────────────────
out = Path("results/bifurcation_proof.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"✓ Saved {out.resolve()}")
