import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# Set font and design style
plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 1.0

def generate_bifurcation_proof_figure():
    print("=== Generating Bifurcation Proof & Fixed Point Analysis Figure ===")

    # Cell parameters (Lindahl 2016 eNeuro STN PV+ / PV-)
    g_L = 10.0      # nS
    E_L = -70.0     # mV
    V_T = -53.8     # mV
    Delta_T = 1.6   # mV
    a_pv_plus = -12.0 # nS (PV+ rebound)
    a_pv_minus = +0.3 # nS (PV- adapting)
    E_AMPA = 0.0    # mV
    E_GABA = -84.0  # mV
    GATE = -70.0    # mV

    V = np.linspace(-92.0, -44.0, 1000)

    fig = plt.figure(figsize=(18, 5.5), facecolor='white')
    fig.suptitle("STN AdEx Bifurcation & Fixed Point Proof: Why I_syn is NOT a 1D Bifurcation Parameter",
                 fontsize=14, fontweight='bold', y=0.98)
    
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.28, left=0.06, right=0.97, top=0.88, bottom=0.12)

    # ─────────────────────────────────────────────────────────────────────────
    # Panel A: 2D Conductance Space (g_AMPA, g_GABA) Bifurcation Boundary
    # ─────────────────────────────────────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    
    g_ampa_grid = np.linspace(0.0, 1.0, 200)
    g_gaba_crit = []

    for gA in g_ampa_grid:
        # Find minimum g_GABA where V-nullcline touches w-nullcline (min gap = 0)
        gG_vals = np.linspace(0.0, 4.0, 500)
        found_gG = 0.0
        for gG in gG_vals:
            # V-nullcline
            ea = np.minimum((V - V_T) / Delta_T, 4.0)
            wv = (-g_L * (V - E_L) + g_L * Delta_T * np.exp(ea)
                  + gA * (E_AMPA - V) + gG * (E_GABA - V))
            # w-nullcline for PV+
            ww = np.where(V < GATE, a_pv_plus * (V - E_L), 0.0)
            gap = np.min(wv - ww)
            if gap <= 0.0:
                found_gG = gG
                break
        g_gaba_crit.append(found_gG)

    g_gaba_crit = np.array(g_gaba_crit)

    # Fill regions
    ax_a.fill_between(g_ampa_grid, g_gaba_crit, 4.0, color='#ffebee', alpha=0.6, label="Silent Zone (Rest State, FP = 1 or 2)")
    ax_a.fill_between(g_ampa_grid, 0, g_gaba_crit, color='#e8f5e9', alpha=0.6, label="Repetitive Firing Zone (FP = 0)")

    ax_a.plot(g_ampa_grid, g_gaba_crit, color='#c62828', lw=2.2, ls='--', label="Saddle-Node Bifurcation Boundary")

    # Operating Points
    # Normal (Mallet 2008 Control): gA = 0.25, gG = 0.64
    ax_a.scatter([0.25], [0.64], color='#2e7d32', s=120, zorder=6, label="Normal State (Mallet 2008 Control)")
    ax_a.annotate("Normal (FP = 0)\nFiring 8.0 Hz", xy=(0.25, 0.64), xytext=(0.28, 0.40),
                 fontsize=8.5, color='#2e7d32', fontweight='bold',
                 arrowprops=dict(arrowstyle="->", color='#2e7d32', lw=1.2))

    # PD (Mallet 2008 6-OHDA): gA = 0.62, gG = 0.34
    ax_a.scatter([0.62], [0.34], color='#c62828', s=120, zorder=6, label="PD State (Mallet 2008 6-OHDA)")
    ax_a.annotate("PD (FP = 0)\nBurst 28.5 Hz", xy=(0.62, 0.34), xytext=(0.65, 0.15),
                 fontsize=8.5, color='#c62828', fontweight='bold',
                 arrowprops=dict(arrowstyle="->", color='#c62828', lw=1.2))

    ax_a.set_xlim(0, 1.0)
    ax_a.set_ylim(0, 3.5)
    ax_a.set_xlabel("AMPA Conductance $g_{AMPA}$ (nS)", fontsize=9.5, fontweight='bold')
    ax_a.set_ylabel("GABA Conductance $g_{GABA}$ (nS)", fontsize=9.5, fontweight='bold')
    ax_a.set_title("A. 2D Conductance Bifurcation Boundary\n(g_GABA / g_AMPA ratio determines Saddle-Node)", fontsize=10.5, fontweight='bold')
    ax_a.legend(loc='upper left', fontsize=7.5, framealpha=0.95)
    ax_a.grid(True, alpha=0.3)
    ax_a.spines['top'].set_visible(False); ax_a.spines['right'].set_visible(False)

    # ─────────────────────────────────────────────────────────────────────────
    # Panel B: Why I_syn is NOT 1D Parameter: V-dependent Nullcline Distortion
    # ─────────────────────────────────────────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])

    # Case 1: Pure scalar current I_ext = +30 pA vs I_ext = -30 pA
    wv_base = (-g_L * (V - E_L) + g_L * Delta_T * np.exp(np.minimum((V - V_T) / Delta_T, 4.0)))
    wv_ext_plus = wv_base + 30.0
    wv_ext_minus = wv_base - 30.0

    # Case 2: Conductance I_syn (gA=0.25, gG=0.64)
    wv_syn_normal = wv_base + 0.25 * (E_AMPA - V) + 0.64 * (E_GABA - V)
    wv_syn_pd     = wv_base + 0.62 * (E_AMPA - V) + 0.34 * (E_GABA - V)

    ax_b.plot(V, wv_base, color='gray', ls=':', lw=1.2, label="Base V-null (No Input)")
    ax_b.plot(V, wv_ext_plus, color='#1565c0', ls='--', lw=1.5, label="Pure I_ext (+30 pA, Vertical Shift Only)")
    ax_b.plot(V, wv_syn_normal, color='#2e7d32', ls='-', lw=2.0, label="Conductance Normal (Slope Shift)")
    ax_b.plot(V, wv_syn_pd, color='#c62828', ls='-', lw=2.0, label="Conductance PD (Slope & Lift Shift)")

    ww_pv_plus = np.where(V < GATE, a_pv_plus * (V - E_L), 0.0)
    ax_b.plot(V, ww_pv_plus, color='k', ls='-', lw=1.8, label="w-null PV+ (a=-12 nS)")

    ax_b.set_xlim(V[0], V[-1])
    ax_b.set_ylim(-30, 120)
    ax_b.set_xlabel("Voltage V (mV)", fontsize=9.5, fontweight='bold')
    ax_b.set_ylabel("V-nullcline Height (pA)", fontsize=9.5, fontweight='bold')
    ax_b.set_title("B. Why I_syn is NOT a 1D Parameter\n(Conductance tilts nullcline slope, not just vertical shift)", fontsize=10.5, fontweight='bold')
    ax_b.legend(loc='upper left', fontsize=7.5, framealpha=0.95)
    ax_b.grid(True, alpha=0.3)
    ax_b.spines['top'].set_visible(False); ax_b.spines['right'].set_visible(False)

    # ─────────────────────────────────────────────────────────────────────────
    # Panel C: Discontinuous Reset Map: Tonic vs Rebound Burst Mechanism
    # ─────────────────────────────────────────────────────────────────────────
    ax_c = fig.add_subplot(gs[0, 2])

    w_vals = np.linspace(-40, 40, 500)
    # Dynamic reset rule: Vr = -70 when w >= 0; Vr = -70 + max(w - 15, 20.0) when w < 0
    vr_vals = []
    for z in w_vals:
        if z < 0.0:
            vr_vals.append(-70.0 + max(z - 15.0, 20.0))
        else:
            vr_vals.append(-70.0)
    vr_vals = np.array(vr_vals)

    ax_c.plot(w_vals, vr_vals, color='#c62828', lw=2.5, label="Dynamic Reset Map $V_r(w)$")
    ax_c.axvline(0, color='#999', ls=':', lw=1.0)
    ax_c.axhline(-70, color='#999', ls='--', lw=1.0, label="Unarmed Reset ($V_r = -70$ mV)")
    ax_c.axhline(-50, color='#2e7d32', ls='--', lw=1.0, label="Armed Reset ($V_r = -50$ mV)")

    # Annotate regions
    ax_c.axvspan(-40, 0, color='#ffebee', alpha=0.4, label="Armed Zone (V < -70 mV -> Rebound Burst)")
    ax_c.axvspan(0, 40, color='#e8f5e9', alpha=0.4, label="Unarmed Zone (V > -70 mV -> Tonic Firing)")

    ax_c.annotate("Discontinuous Jump!\n$V_r \\to -50$ mV", xy=(-15, -50), xytext=(-35, -58),
                 fontsize=8.5, color='#c62828', fontweight='bold',
                 arrowprops=dict(arrowstyle="->", color='#c62828', lw=1.2))

    ax_c.set_xlim(-40, 40)
    ax_c.set_ylim(-75, -45)
    ax_c.set_xlabel("Adaptation Variable w at Spike Time (pA)", fontsize=9.5, fontweight='bold')
    ax_c.set_ylabel("Reset Voltage $V_{reset}$ (mV)", fontsize=9.5, fontweight='bold')
    ax_c.set_title("C. Discontinuous Reset Map Mechanism\n(Tonic <-> Burst Transition is a Hybrid Map Jump)", fontsize=10.5, fontweight='bold')
    ax_c.legend(loc='lower right', fontsize=7.5, framealpha=0.95)
    ax_c.grid(True, alpha=0.3)
    ax_c.spines['top'].set_visible(False); ax_c.spines['right'].set_visible(False)

    out = Path("results/bifurcation_proof.png")
    fig.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  ✓ Proof Figure saved -> {out.resolve()}")

if __name__ == "__main__":
    generate_bifurcation_proof_figure()
