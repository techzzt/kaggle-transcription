#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stn_borderline_tonic_burst_transition.py  (v15 — Standard Biophysical AdEx Model)

Hypothesis:
  PV- STN: unresponsive to input perturbation (no dynamic reset)
  PV+ STN: same intrinsic parameters as PV+ in both Tonic and Burst form;
    the two differ only in whether the w-dependent dynamic reset is applied
    (use_dynamic_reset ON = Burst, OFF = Tonic → current_vr = vr_mV fixed).

Biophysical Mechanisms:
  - Gated a_nS (Table 6, active only below -70 mV):
      PV- = +0.3 nS  (adapting)      PV+ = -12.0 nS (rebound-capable)
    The gate is what keeps a<0 self-limiting: hyperpolarisation arms the
    rebound (z<0), depolarisation disarms it (a_eff=0, z decays back to 0).
  - Small adaptation increment: d_pA = 0.05 (b in paper)
  - Dynamic reset (PV+ Burst only): current_vr = vr_mV + max(z - 15, 20.0) if z < 0, else vr_mV
    (PV+ Tonic keeps current_vr = vr_mV fixed; PV- never applies this reset.)

Input Scenario Scales (Single-Unit Axon Scale vs Aggregate Population Scale):
  - Scale A: Single-Unit Axon Scale (Goldberg 2002 / Mallet 2008 ECoG)
      CTX lambda = 12.0~15.0 Hz (Single presynaptic axon rate), GPe Normal 33.7 Hz -> PD 14.6 Hz (-57%)
  - Scale B: Aggregate Population Scale (Lindahl 2016 eNeuro Table 1)
      CTX lambda = 250.0 Hz (25 converging axons x 10 Hz), GPe Normal 50 Hz -> PD 38 Hz (-24%)
  - Scale C: Consensus Scale (Tachibana 2011 Awake Primate)
      GPe Normal 50 Hz -> PD 32 Hz (-37% awake drop), STN output +40% increase validation target

Outputs:
  results/stn_borderline_phase_diagram.png   — (V,w) phase plane
  results/stn_borderline_7_scenarios.png     — 7 scenarios × 3 subtypes
  results/stn_borderline_pv_comparison.png   — PV+ Borderline focus
  results/stn_side_by_side_normal_pd.png     — Normal vs PD side-by-side
"""

import os
from pathlib import Path
import numpy as np

_MPL_CACHE = Path(__file__).resolve().parent / "figures" / ".mplcache"
_MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

from pd_input_patterns import (
    generate_scenario,
    get_pause_intervals,
    compute_population_rate,
    SCENARIO_REGISTRY,
)

# ─────────────────────────────────────────────────────────────────────────────
# AdEx Neuron Cell Types  (I_ext = 0 pA in every scenario; Lindahl 2016 Table 6)
# ─────────────────────────────────────────────────────────────────────────────
ADEX_BASE = dict(
    C_pF=60.0, g_L_nS=10.0, E_L_mV=-80.2,
    tau_w_ms=333.0, vr_mV=-70.0,
    vt_mV=-64.0, Delta_T_mV=16.2,
    d_pA=0.05,
    I_ext_pA=0,
    refractory_ms=2.0, v_init_mV=-70.0, z_init_pA=0.0, th_mV=15.0
)

# The ONLY difference between the two cell classes is the subthreshold
# adaptation current `a` (and, for PV+, the reset it enables).  Everything else
# is Lindahl 2016 Table 6.
#
# `a_gate_mV` is Table 6's own condition ("subthreshold adaptation below -70,
# otherwise equal to 0") and is what makes a negative `a` self-limiting:
#   V < -70 (hyperpolarised by a GPe barrage) -> a acts -> z driven negative
#                                                -> rebound is ARMED
#   V > -70 (depolarised / firing)            -> a_eff = 0 -> z decays to 0
#                                                -> rebound DISARMS itself
# Without the gate a<0 keeps z negative forever and the dynamic reset fires on
# every spike, which is the runaway (V_reset = -50 mV sits above V_T = -64 mV).
CELL_TYPES = {
    # Table 6 exactly: adapting, no rebound machinery.
    "PV-": {**ADEX_BASE, "a_nS": 0.3, "a_gate_mV": -70.0},
    # Rebound-capable.  Lindahl 2016 models STN as ONE population with a = +0.3
    # and has no PV+/PV- split, so NOTHING about this cell is a paper value --
    # it is this project's hypothesis for what a rebound-competent STN subtype
    # looks like.  Two parameters are moved away from Table 6, both of them
    # descriptions of the same thing (the slow subthreshold rebound current
    # that PV+ is hypothesised to express more strongly):
    #
    #   a      +0.3 -> -3.0 nS   sign flip is what lets hyperpolarisation drive
    #                            z NEGATIVE (a>0 drives it positive), and z<0 is
    #                            the paper's own condition for the burst reset.
    #   tau_w   333 -> 100 ms    the rebound conductance has to engage within a
    #                            single pallidal barrage; 333 ms is far slower
    #                            than T-type Ca de-inactivation (~50-200 ms), so
    #                            with Table 6's tau_w z never has time to move.
    #
    # Everything else is Table 6 untouched -- crucially vr (-70) and the a-gate
    # (-70).  Those two are NOT free: because vr == a_gate, the gate only opens
    # when synaptic inhibition drags V below the reset, i.e. only during a real
    # GPe barrage.  Moving either one opens the gate all the time and the
    # control condition bursts too, which destroys the comparison:
    #     vr -70 -> -73 :  Sc10 NORMAL goes to CV 1.19  (should stay tonic)
    #     gate -70 -> -66: Sc10 NORMAL goes to CV 2.12
    #
    # Chosen operating point, with Table 7 conductances, NMDA enabled and
    # I_ext = 0:
    #   tau_w  a       Sc10 NORMAL OFF/ON        Sc11 PD OFF/ON
    #    100   -3.0    8.0/8.0 Hz  CV .37/.37    26.5/31.0 Hz  CV .30/.47  no sep
    #    100   -5.0    8.0/8.0 Hz  CV .37/.37    26.5/34.5 Hz  CV .30/.56  no sep
    #    100   -8.0    8.0/8.0 Hz  CV .37/.37    26.5/37.0 Hz  CV .30/.65  marginal
    #    100  -12.0    8.0/8.0 Hz  CV .37/.37    26.5/55.0 Hz  CV .30/.86  <- used
    #     50  -12.0    8.0/8.0 Hz  CV .37/.37    26.5/38.5 Hz  CV .30/.65
    # NORMAL is identical in both reset states (the gate never opens there), so
    # the burst in PD is attributable to the reset and not to `a` itself.
    #
    # CAVEAT: |a| = 12 nS now EXCEEDS g_L = 10 nS, i.e. the hypothesised rebound
    # conductance is larger than the leak.  That is a strong assumption and the
    # main thing a reviewer will push on.  It got this large because NMDA (Table
    # 7, tau = 160 ms) holds the cell depolarised, keeping V above the -70 mV
    # gate; before NMDA was implemented a = -3.0 sufficed.  If NMDA is disabled
    # again, retune downwards.
    "PV+": {**ADEX_BASE, "a_nS": -12.0, "a_gate_mV": -70.0, "tau_w_ms": 100.0},
}

# Borderline / Burst are interpretations of the same PV+ cell under different
# input protocols, not separate cell types with distinct physiology.
INPUT_PROTOCOLS = {
    "Borderline": dict(gpe_pause_ms=100, gpe_pause_strength=0.3),
    "Burst": dict(gpe_pause_ms=300, gpe_pause_strength=0.8),
}

# Mechanism-verification comparison columns:
# 1) PV- control (strong adaptation / no dynamic reset)
# 2) PV+ with dynamic reset ON
# 3) PV+ with dynamic reset OFF (ablation control)
MECHANISM_COLUMNS = {
    "PV-": {**CELL_TYPES["PV-"], "use_dynamic_reset": False},
    "PV+ Dynamic Reset OFF": {**CELL_TYPES["PV+"], "use_dynamic_reset": False},
    "PV+ Dynamic Reset ON": {**CELL_TYPES["PV+"], "use_dynamic_reset": True},
}

# Shorter, reader-facing labels for the figure column headers.
COLUMN_DISPLAY_NAMES = {
    "PV-": "PV-",
    "PV+ Dynamic Reset OFF": "PV+ Tonic (reset OFF)",
    "PV+ Dynamic Reset ON": "PV+ Burst (reset ON)",
}

# Backward-compatible alias used by the existing plotting code.
SUBTYPES_3 = {
    "PV-": CELL_TYPES["PV-"],
    "PV+ Borderline": CELL_TYPES["PV+"],
    "PV+ Burst": CELL_TYPES["PV+"],
}


# ─────────────────────────────────────────────────────────────────────────────
# AdEx Simulation Core
# ─────────────────────────────────────────────────────────────────────────────
# Synaptic time constants, Lindahl 2016 Table 7 (Baufreton et al. 2005 for the
# two fast ones).  Exposed as named constants / arguments rather than magic
# numbers inside the integration loop so they can be varied or refitted.
TAU_AMPA_MS = 4.0      # tau_ampa CTX-STN
TAU_GABA_MS = 8.0      # tau_gaba GPe-STN
TAU_NMDA_MS = 160.0    # tau_nmda CTX-STN ("same as for MSN")
E_AMPA_MV, E_GABA_MV, E_NMDA_MV = 0.0, -84.0, 0.0
MG_MM = 1.0            # [Mg2+] in the Jahr-Stevens block, Eq. 4


def nmda_mg_block(v, mg_mM=MG_MM):
    """Lindahl 2016 Eq. 4: B(v) = 1 / (1 + [Mg2+]/3.57 * exp(-0.062 v)).

    NMDA is almost fully blocked at rest (B ~ 0.04 at -70 mV) and unblocks as
    the cell depolarises, so it contributes mainly during depolarisation.
    """
    return 1.0 / (1.0 + (mg_mM / 3.57) * np.exp(-0.062 * v))


def simulate_ad_ex(p_neuron, gpe_spikes, ctx_spikes,
                   g_gaba=0.35, w_ampa=0.25, g_nmda=0.0,
                   total_ms=3500.0, dt=0.02,
                   use_dynamic_reset=None,
                   tau_ampa=TAU_AMPA_MS, tau_gaba=TAU_GABA_MS,
                   tau_nmda=TAU_NMDA_MS, mg_mM=MG_MM):
    """
    Simulate AdEx neuron with Lindahl 2016 eNeuro dynamics:
      - Gated a_nS (Table 6, active only when V < a_gate_mV = -70)
      - Dynamic reset (PV+ Burst only): current_vr = vr_mV + max(z - 15, 20.0) if z < 0, else vr_mV

    Synaptic dynamics:
      dg_ampa/dt = -g_ampa / tau_ampa;  tau_ampa = 4 ms
      dg_gaba/dt = -g_gaba / tau_gaba;  tau_gaba = 8 ms
      I_syn = g_ampa*(E_ampa - V) + g_gaba*(E_gaba - V)
      E_ampa = 0 mV, E_gaba = -84 mV
    """
    n_steps = int(np.ceil(total_ms / dt))
    t = np.arange(n_steps) * dt

    if use_dynamic_reset is None:
        use_dynamic_reset = bool(p_neuron.get("use_dynamic_reset", True))

    v, z = float(p_neuron["v_init_mV"]), float(p_neuron["z_init_pA"])
    v_tr = np.empty(n_steps, dtype=np.float32)
    w_tr = np.empty(n_steps, dtype=np.float32)
    spikes = []
    ref = 0.0
    vcut = float(p_neuron.get("th_mV", 15.0))
    I_ext = float(p_neuron.get("I_ext_pA", 0.0))
    g_ampa_val = 0.0
    g_gaba_val = 0.0
    g_nmda_val = 0.0
    gpe_idx = ctx_idx = 0
    just_spiked = False

    # Exact per-step decay factors for dg/dt = -g/tau (Lindahl Eq. 3).
    dec_ampa = np.exp(-dt / tau_ampa)
    dec_gaba = np.exp(-dt / tau_gaba)
    dec_nmda = np.exp(-dt / tau_nmda)


    for k in range(n_steps):
        tnow = t[k]

        # Deliver GPe (GABA) spikes
        while gpe_idx < len(gpe_spikes) and gpe_spikes[gpe_idx][0] <= tnow:
            g_gaba_val += g_gaba
            gpe_idx += 1

        # Deliver CTX spikes (AMPA + NMDA ride on the same afferent)
        while ctx_idx < len(ctx_spikes) and ctx_spikes[ctx_idx][0] <= tnow:
            g_ampa_val += w_ampa
            g_nmda_val += g_nmda
            ctx_idx += 1

        # Synaptic current (conductance-based).  NMDA carries the Jahr-Stevens
        # magnesium block, so it is negligible at rest and grows as V rises.
        I_syn = (g_ampa_val * (E_AMPA_MV - v)
                 + g_gaba_val * (E_GABA_MV - v))
        if g_nmda_val > 0.0:
            I_syn += g_nmda_val * nmda_mg_block(v, mg_mM) * (E_NMDA_MV - v)

        # Dynamic reset potential for the current step.
        # Use the adaptation variable z as the recovery variable (w in the paper).
        # Hyperpolarization-induced burst: V_reset = Vr + max(z - 15, 20.0) when z < 0,
        # otherwise V_reset = Vr.
        current_vr = float(p_neuron["vr_mV"])
        if use_dynamic_reset and z < 0.0:
            current_vr += max(z - 15, 20.0)

        if just_spiked:
            v_tr[k], w_tr[k] = 10.0, float(z)
            just_spiked = False
        else:
            v_tr[k], w_tr[k] = float(v), float(z)

        if ref > 0:
            v = current_vr
            ref -= dt
        elif v >= vcut:
            spikes.append((k, tnow))
            v = current_vr
            z += float(p_neuron["d_pA"])
            ref = float(p_neuron.get("refractory_ms", 2.0))
            just_spiked = True
        else:
            ea  = min((v - float(p_neuron["vt_mV"])) / float(p_neuron["Delta_T_mV"]), 20.0)
            ex  = float(p_neuron["g_L_nS"]) * float(p_neuron["Delta_T_mV"]) * np.exp(ea)
            dv  = (-float(p_neuron["g_L_nS"]) * (v - float(p_neuron["E_L_mV"]))
                   + ex - z + I_syn + I_ext) / float(p_neuron["C_pF"])
            v  += dv * dt
            # Table 6: "Subthreshold adaptation (below -70) otherwise equal to 0"
            a_gate = p_neuron.get("a_gate_mV")
            a_eff = (float(p_neuron["a_nS"])
                     if (a_gate is None or v < float(a_gate)) else 0.0)
            dw  = (a_eff * (v - float(p_neuron["E_L_mV"])) - z) / float(p_neuron["tau_w_ms"])
            z  += dw * dt

        g_ampa_val *= dec_ampa
        g_gaba_val *= dec_gaba
        g_nmda_val *= dec_nmda

    # Stats: last 2000 ms
    analysis_t0 = max(0.0, total_ms - 2000.0)
    w_spikes = [s[1] for s in spikes if s[1] >= analysis_t0]
    fr = len(w_spikes) / ((total_ms - analysis_t0) / 1000.0)
    if len(w_spikes) > 1:
        isis = np.diff(w_spikes)
        mean_isi = float(np.mean(isis))
        cv = float(np.std(isis) / mean_isi) if mean_isi > 0 else 0.0
    else:
        cv = 0.0

    return t, v_tr, w_tr, spikes, fr, cv


def classify_pattern(fr, cv, is_beta_drive=False):
    """
    Classify STN firing pattern.

    Silent      : fr < 0.5 Hz
    Burst       : CV >= 0.65
    Beta-locked : is_beta_drive=True AND 12<=fr<=35 Hz AND cv<0.25
    Irregular   : CV in [0.40, 0.65)
    Tonic       : CV < 0.40, fr >= 0.5 Hz
    """
    if fr < 0.5:
        return "Silent",      "#607d8b"
    elif cv >= 0.65:
        return "Burst",       "#d32f2f"
    elif is_beta_drive and 12.0 <= fr <= 35.0 and cv < 0.25:
        return "Beta-locked", "#7b1fa2"
    elif cv >= 0.40:
        return "Irregular",   "#ff8f00"
    else:
        return "Tonic",       "#2e7d32"


# ─────────────────────────────────────────────────────────────────────────────
# Figure 1 — (V, w) Phase Plane (3 conditions)
# ─────────────────────────────────────────────────────────────────────────────
def generate_phase_diagram():
    """
    (V, w) phase plane in the style of Naud et al. (2008) Fig. 1
    ("Firing patterns in the adaptive exponential integrate-and-fire model",
    Biol Cybern 99:335-347), applied to the two STN cell classes.

    Naud's drawing conventions, followed here:
      w-nullcline .................. green
      V-nullcline, no input ........ curved DASHED black
      V-nullcline, with input ...... curved SOLID black
      state of rest ................ blue cross
      unstable fixed point ......... encircled
      spike trajectory ............. blue, with squares

    Naud's key result is that the firing pattern is set by WHERE THE RESET
    POINT LANDS relative to the V-nullcline (their Sect. on sharp vs broad
    SAPs):
      reset BELOW the V-nullcline -> dV/dt > 0 immediately -> sharp reset,
                                     the cell climbs straight back to threshold
      reset ABOVE the V-nullcline -> dV/dt < 0 first       -> broad reset,
                                     the voltage sags before it can spike
    and "reset points jumping above the V-nullcline lead to initial bursting".

    That is exactly the knob our dynamic reset turns.  With z >= 0 the cell
    resets to Vr = -70 mV; once a GPe barrage drives z < 0 the reset jumps to
    Vr + max(z-15, 20) = -50 mV, i.e. to the far side of V_T, deep BELOW the
    V-nullcline -> immediate re-spike -> burst.  Both reset points are drawn
    and labelled so the mechanism is readable off the figure.

    Everything is taken from the live model: cell parameters from CELL_TYPES,
    input as the scenario's synaptic CONDUCTANCE, and trajectories straight out
    of simulate_ad_ex, so the phase portrait cannot disagree with the traces.
    """
    print("\n[Fig 1: Phase Plane Diagram — Naud et al. 2008 Fig. 1 style]")

    TOTAL_MS = 3500.0
    T0, T1 = 2000.0, 3500.0
    N_GPE, N_CTX = 30, 50

    b = ADEX_BASE
    gL, EL, VT, dT = b["g_L_nS"], b["E_L_mV"], b["vt_mV"], b["Delta_T_mV"]
    VR = b["vr_mV"]
    E_AMPA, E_GABA = 0.0, -84.0
    GATE = CELL_TYPES["PV-"]["a_gate_mV"]

    V = np.linspace(-92.0, -44.0, 1600)

    def v_null(gA, gG):
        ea = np.minimum((V - VT) / dT, 4.0)
        return (-gL * (V - EL) + gL * dT * np.exp(ea)
                + gA * (E_AMPA - V) + gG * (E_GABA - V))

    def v_null_at(v0, gA, gG):
        ea = min((v0 - VT) / dT, 4.0)
        return (-gL * (v0 - EL) + gL * dT * np.exp(ea)
                + gA * (E_AMPA - v0) + gG * (E_GABA - v0))

    def w_null(a):
        return np.where(V < GATE, a * (V - EL), 0.0)

    def fixed_points(wv, ww):
        d = wv - ww
        out = []
        for i in np.where(np.sign(d[:-1]) != np.sign(d[1:]))[0]:
            # stable if the V-nullcline is still falling there (left branch)
            out.append((V[i], ww[i], wv[i + 1] < wv[i]))
        return out

    # Only Normal (Mallet 2008 Control) vs PD (Mallet 2008 6-OHDA) — Slice removed!
    conditions = [
        (10, "Normal State (Mallet 2008 Control)", "#2e7d32"),
        (11, "PD State (Mallet 2008 6-OHDA 20.5 Hz Beta)", "#c62828"),
    ]

    fig = plt.figure(figsize=(16, 11), facecolor="white")
    fig.suptitle("STN AdEx Phase Plane & Dynamics: Normal vs PD State",
                 fontsize=15, fontweight="bold", y=0.985)
    fig.text(0.5, 0.945,
             "Side-by-Side Comparison: Normal (Left, Green) vs PD (Right, Red)\n"
             "Firing pattern is set by where the RESET lands relative to V-nullcline: below -> sharp burst; above -> sag / tonic",
             ha="center", fontsize=10, color="#444")

    # 2 Columns (Normal Left, PD Right) x 2 Rows (Top: Phase Portrait, Bottom: V(t) Traces)
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.22,
                           left=0.07, right=0.96, top=0.90, bottom=0.07,
                           height_ratios=[1.2, 1.0])

    for col_idx, (sid, label, theme_color) in enumerate(conditions):
        gpe, ctx, wts, info = generate_scenario(
            sid, total_ms=TOTAL_MS, n_gpe=N_GPE, n_ctx=N_CTX, seed=42)
        dur = TOTAL_MS / 1000.0
        gG = wts["g_gaba"] * len(gpe) / dur * 0.008
        gA = wts["w_ampa"] * len(ctx) / dur * 0.004

        wv0 = v_null(0.0, 0.0)      # dashed: no input
        wv = v_null(gA, gG)         # solid: with scenario's input

        # Top Row: (V, w) Phase Portrait
        ax = fig.add_subplot(gs[0, col_idx])
        
        # Zone 1 vs Zone 2 Shading
        ax.axvspan(-92, GATE, color="#ffebee", alpha=0.35, label="Zone 1: Arming (V < -70 mV)")
        ax.axvspan(GATE, -44, color="#e8f5e9", alpha=0.35, label="Zone 2: Tonic (V > -70 mV)")

        ax.axhline(0, color="#bbb", lw=0.8, zorder=1)
        ax.axvline(GATE, color="#999", lw=1.0, ls=":", zorder=1)
        ax.axvline(VT, color="#999", lw=0.8, ls="--", zorder=1)
        ax.text(VT + 0.3, 138, "$V_T$", fontsize=9.5, color="#555", va="top")
        ax.text(GATE - 3.6, 138, "a-gate", fontsize=8.5, color="#555", va="top")

        ax.plot(V, wv, color="k", ls="-", lw=2.2, zorder=4,
                label=f"V-nullcline (Active Input: g_AMPA={gA:.2f}, g_GABA={gG:.2f} nS)")

        # Clear distinct w-nullclines: PV- (Blue) vs PV+ (Green/Red)
        ww_pv_minus = w_null(CELL_TYPES["PV-"]["a_nS"])
        ww_pv_plus  = w_null(CELL_TYPES["PV+"]["a_nS"])
        ax.plot(V, ww_pv_minus, color="#1565c0", ls="-", lw=2.0, zorder=5,
                label="w-null PV- (a=+0.3 nS, Blue)")
        ax.plot(V, ww_pv_plus, color=theme_color, ls="--", lw=2.0, zorder=5,
                label=f"w-null PV+ (a=-12.0 nS, {theme_color})")

        # Fixed points
        for vf, wf, stable in fixed_points(wv, ww_pv_plus):
            ax.scatter([vf], [wf], color="#1565c0", marker="x", s=95, linewidths=2.4, zorder=8)

        # Reset points
        wv_at_vr = v_null_at(VR, gA, gG)
        wv_at_arm = v_null_at(-50.0, gA, gG)
        ax.scatter([VR], [0.0], marker="o", s=85, facecolor="white", edgecolor=theme_color, linewidths=2.0, zorder=9)
        ax.annotate(f"Unarmed Reset\n$V_r$={VR:.0f} mV", xy=(VR, 0.0), xytext=(VR - 12, 45),
                    fontsize=8, color=theme_color, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=theme_color, lw=1.2))
        ax.scatter([-50.0], [0.0], marker="o", s=85, color=theme_color, zorder=9)
        ax.annotate("Armed Reset\n$V_r$=-50 mV", xy=(-50.0, 0.0), xytext=(-49.5, 45),
                    fontsize=8, color=theme_color, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=theme_color, lw=1.2))

        # Trajectories
        # Trajectories (Bold, vibrant orbital loops over 2000-3500 ms)
        pc_plus = MECHANISM_COLUMNS["PV+ Dynamic Reset ON"]
        t_arr, v_tr, w_tr, sp, fr_p, cv_p = simulate_ad_ex(
            pc_plus, gpe, ctx, g_gaba=wts["g_gaba"], w_ampa=wts["w_ampa"], g_nmda=wts["g_nmda"],
            total_ms=TOTAL_MS, use_dynamic_reset=True)
        m = (t_arr >= T0) & (t_arr <= T1)
        ax.plot(v_tr[m], w_tr[m], color=theme_color, lw=1.6, alpha=0.85, zorder=7, label="Spiking Trajectory Orbit (V, w)")
        # Scatter markers along orbit to show flow direction
        ax.scatter(v_tr[m][::100], w_tr[m][::100], color=theme_color, s=16, alpha=0.7, zorder=8)

        ax.set_xlim(V[0], V[-1])
        ax.set_ylim(-45, 145)
        ax.set_title(f"{label}\n(V, w) Phase Portrait", fontsize=11, fontweight="bold", color=theme_color)
        ax.set_xlabel("Voltage V (mV)", fontsize=9.5, fontweight="bold")
        ax.set_ylabel("Adaptation w (pA)", fontsize=9.5, fontweight="bold")
        ax.legend(loc="upper left", fontsize=7.5, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

        # Bottom Row: V(t) Traces (PV+ in bold theme color, PV- in clean blue, NO OVERLAP BLUR!)
        axt = fig.add_subplot(gs[1, col_idx])
        pc_minus = MECHANISM_COLUMNS["PV-"]
        _, v_tr_m, _, _, fr_m, cv_m = simulate_ad_ex(
            pc_minus, gpe, ctx, g_gaba=wts["g_gaba"], w_ampa=wts["w_ampa"], g_nmda=wts["g_nmda"],
            total_ms=TOTAL_MS, use_dynamic_reset=False)

        axt.plot(t_arr[m], v_tr[m], color=theme_color, lw=1.2, label=f"PV+ Burst: {fr_p:.1f} Hz (CV {cv_p:.2f})")
        axt.plot(t_arr[m], v_tr_m[m], color="#1565c0", lw=1.0, ls="--", alpha=0.7, label=f"PV- Adapting: {fr_m:.1f} Hz (CV {cv_m:.2f})")
        axt.axhline(GATE, color="#999", lw=0.8, ls=":", label="a-gate (-70 mV)")

        axt.set_xlim(T0, T1); axt.set_ylim(-92, 25)
        axt.set_title(f"{label}\nMembrane Potential V(t)", fontsize=11, fontweight="bold", color=theme_color)
        axt.set_xlabel("Time (ms)", fontsize=9.5, fontweight="bold")
        axt.set_ylabel("Voltage V (mV)", fontsize=9.5, fontweight="bold")
        axt.legend(loc="upper right", fontsize=8, framealpha=0.95)
        axt.grid(True, alpha=0.3)
        axt.spines["top"].set_visible(False); axt.spines["right"].set_visible(False)

    out = Path("results/stn_borderline_phase_diagram.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ Refactored Phase Diagram saved -> {out.resolve()}")
    plt.close(fig)
    print(f"  ✓ {out.resolve()}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 2 — 7 Scenarios × 3 Subtypes
# ─────────────────────────────────────────────────────────────────────────────
def run_7_scenarios_all_subtypes():
    """
    7-row × 4-column grid:
      Col 0: Input rasters (GPe + CTX)
      Cols 1-3: mechanism-verification columns (PV-, PV+ ON, PV+ OFF)
    """
    TOTAL_MS = 3500.0
    T_START, T_END = 2000.0, 3000.0  # 1-second window (2000 ms to 3000 ms)
    N_GPE, N_CTX = 30, 50
    subtype_list = list(MECHANISM_COLUMNS.items())

    fig = plt.figure(figsize=(24, 28), facecolor='#f8f9fa')
    fig.suptitle(
        "STN Subtypes Tonic→Burst Transition: 7 Input Scenarios × 3 Subtypes  [I_ext = 0]\n"
        "Lindahl 2016 eNeuro Model (a>0, Vr<VT, w-dependent Dynamic Reset)\n"
        "Tonic Equivalence in Normal (Sc2-3) vs Differential Rebound Bursting in PD (Sc4-7)",
        fontsize=14, fontweight='bold', y=0.998
    )

    gs = gridspec.GridSpec(7, 4, figure=fig, hspace=0.55, wspace=0.28,
                           left=0.05, right=0.98, top=0.94, bottom=0.04)

    print("\n" + "=" * 90)
    print("  7 SCENARIOS × 3 SUBTYPES | Lindahl 2016 Biophysical Dynamics")
    print("=" * 90)

    for sc_idx in range(1, 8):
        row  = sc_idx - 1
        info = SCENARIO_REGISTRY[sc_idx]
        is_pd = info["is_pd"]
        col_theme = info["color"]
        is_beta = sc_idx == 6

        print(f"\n▶ Scenario {sc_idx}: {info['name']}")

        gpe, ctx, weights, _ = generate_scenario(
            sc_idx, total_ms=TOTAL_MS, n_gpe=N_GPE, n_ctx=N_CTX, seed=42
        )
        g_gaba = weights["g_gaba"]
        w_ampa = weights["w_ampa"]

        # Detect population pause times in GPe (Using threshold=15.0ms)
        pauses = get_pause_intervals(gpe, N_GPE, threshold_ms=15.0)

        # ── Col 0: Input Raster ───────────────────────────────────────────
        ax_ras = fig.add_subplot(gs[row, 0])
        """
        # GPe pause shading
        for ps, pe in pauses:
            if ps <= T_END and pe >= T_START:
                ax_ras.axvspan(max(ps, T_START), min(pe, T_END),
                               alpha=0.22, color='#ff5722', zorder=0)

        # Beta phase markers for CTX (Sc6 only)
        if sc_idx == 6:
            for bt in np.arange(T_START, T_END, 50.0):   # 20 Hz = 50 ms
                ax_ras.axvline(bt, color='#8e24aa', alpha=0.18, lw=0.8, ls=':')
        """
        # GPe spikes
        gpe_t = [t for t, _ in gpe if T_START <= t <= T_END]
        gpe_n = [n for t, n in gpe if T_START <= t <= T_END]
        if gpe_t:
            ax_ras.scatter(gpe_t, gpe_n, color='#388e3c', marker='|',
                           s=16, alpha=0.80, linewidths=0.7)

        # CTX spikes
        ctx_t = [t for t, _ in ctx if T_START <= t <= T_END]
        ctx_n = [n + N_GPE + 2 for t, n in ctx if T_START <= t <= T_END]
        if ctx_t:
            ax_ras.scatter(ctx_t, ctx_n, color='#1565c0', marker='|',
                           s=16, alpha=0.75, linewidths=0.7)

        ax_ras.axhline(N_GPE + 1, color='gray', lw=0.6, ls='--', alpha=0.6)
        ax_ras.set_xlim(T_START, T_END)
        ax_ras.set_ylim(-2, N_GPE + N_CTX + 4)

        sc_label_short = info["label"]
        ax_ras.set_title(f"[Sc{sc_idx}] {sc_label_short}\n"
                         f"{info['name'].split(':')[1].strip()[:24]}",
                         fontsize=9, fontweight='bold', color=col_theme)

        if row == 0:
            ax_ras.legend(
                handles=[
                    Line2D([0],[0], marker='|', color='w',
                           markeredgecolor='#388e3c', markersize=8, label=f'GPe×{N_GPE}'),
                    # N_CTX is raster rows only -- cortex is one aggregate
                    # Poisson process, so labelling it "CTX x 50" would imply a
                    # physical afferent count the model does not have.
                    Line2D([0],[0], marker='|', color='w',
                           markeredgecolor='#1565c0', markersize=8, label='CTX (aggregate)'),
                ],
                loc='upper right', fontsize=7, framealpha=0.9
            )

        if sc_idx in (5, 6):
            ax_ras.text(0.02, 0.96, '▒ GPe pause', transform=ax_ras.transAxes,
                        fontsize=6.5, color='#ff5722', va='top')
        if sc_idx == 6:
            ax_ras.text(0.02, 0.86, '┊ 20Hz β', transform=ax_ras.transAxes,
                        fontsize=6.5, color='#8e24aa', va='top')

        # GPe has a real anatomical convergence (30, Lindahl Table 1), so a
        # per-afferent rate is meaningful.  CTX does not: it is one aggregate
        # Poisson process (Lindahl Table 1 gives only v_CTX-STN in Hz), so it is
        # reported as a TOTAL rate.  Dividing it by N_CTX would just scale the
        # printed number by an arbitrary display constant.
        n_ctx_spk = sum(1 for t, _ in ctx if T_START <= t <= T_END)
        ctx_rate  = n_ctx_spk / ((T_END - T_START) / 1000.0)
        n_gpe_spk = sum(1 for t, _ in gpe if T_START <= t <= T_END)
        gpe_rate  = n_gpe_spk / (N_GPE * (T_END - T_START) / 1000.0)
        ax_ras.text(0.02, 0.05,
                    f"GPe {gpe_rate:.0f} Hz/cell\nCTX {ctx_rate:.0f} Hz total",
                    transform=ax_ras.transAxes, fontsize=6.5,
                    color='#333', va='bottom')

        ref_short = info["ref"].split("\n")[0][:35]
        ax_ras.text(0.02, 0.01, ref_short, transform=ax_ras.transAxes,
                    fontsize=5.5, color='#666', va='bottom', style='italic')

        if row == 6:
            ax_ras.set_xlabel("Time (ms)", fontsize=9, fontweight='bold')
        ax_ras.set_ylabel("Neuron ID", fontsize=8.5, fontweight='bold')
        ax_ras.spines['top'].set_visible(False)
        ax_ras.spines['right'].set_visible(False)
        ax_ras.tick_params(labelsize=7.5)

        # ── Cols 1–3: Mechanism-verification traces ─────────────────────────
        for st_idx, (st_name, st_params) in enumerate(subtype_list):
            col = 1 + st_idx
            ax_n = fig.add_subplot(gs[row, col])

            # The three mechanism-verification columns must use the SAME input
            # protocol. Only the dynamic-reset mechanism is toggled ON/OFF.
            # This keeps the interpretation faithful to the paper hypothesis:
            # same cell, same stimulus, different mechanism state.
            t_arr, v_tr, w_tr, sp, fr, cv = simulate_ad_ex(
                st_params, gpe, ctx, g_gaba=g_gaba, w_ampa=w_ampa,
                total_ms=TOTAL_MS,
                use_dynamic_reset=st_params.get("use_dynamic_reset", True)
            )

            mask = (t_arr >= T_START) & (t_arr <= T_END)
            ax_n.plot(t_arr[mask], v_tr[mask], color=col_theme, lw=0.95)
            """
            # Shade pauses in neuron trace for alignment check
            for ps, pe in pauses:
                if ps <= T_END and pe >= T_START:
                    ax_n.axvspan(max(ps, T_START), min(pe, T_END),
                                 alpha=0.10, color='#ff5722', zorder=0)
            """
            ax_n.set_xlim(T_START, T_END)
            ax_n.set_ylim(-90, 25)
            ax_n.spines['top'].set_visible(False)
            ax_n.spines['right'].set_visible(False)
            ax_n.tick_params(labelsize=7.5)

            if row == 0:
                ax_n.set_title(f"{st_name}", fontsize=9.5, fontweight='bold')
            if row == 6:
                ax_n.set_xlabel("Time (ms)", fontsize=9, fontweight='bold')
            if col == 1:
                ax_n.set_ylabel(f"Sc{sc_idx}\nVm (mV)", fontsize=8.5, fontweight='bold')

            pat, pat_col = classify_pattern(fr, cv, is_beta_drive=is_beta)
            bg = {'Burst':'#fdf2f2','Beta-locked':'#f3e5f5',
                  'Tonic':'#f4fbf7','Irregular':'#fff8e1'}.get(pat, 'white')
            
            # Quantitative Metrics calculation inside visual window
            fsl_val = 0.0
            spikes_in_window = [s[1] for s in sp if T_START <= s[1] <= T_END]
            spikes_per_burst = 0
            min_w_val = float(np.min(w_tr[mask]))
            
            if pauses and spikes_in_window:
                # Find first GPe pause within window
                valid_pauses = [p for p in pauses if p[0] >= T_START and p[1] <= T_END]
                if valid_pauses:
                    first_p = valid_pauses[0]
                    # First spike after pause start
                    sp_after_pause = [s for s in spikes_in_window if s >= first_p[0]]
                    if sp_after_pause:
                        fsl_val = sp_after_pause[0] - first_p[0]
                        # Count spikes within 70ms after pause release (rebound burst window)
                        sp_in_burst = [s for s in sp_after_pause if first_p[1] <= s <= first_p[1] + 70.0]
                        spikes_per_burst = len(sp_in_burst)
            
            metrics_str = f"{pat}\n{fr:.1f}Hz CV:{cv:.2f}"
            if sc_idx in (5, 6) and spikes_per_burst > 0:
                metrics_str += f"\nFSL: {fsl_val:.1f}ms\nBurst Spk: {spikes_per_burst}\nMin w: {min_w_val:.1f}"

            ax_n.text(0.97, 0.96, metrics_str,
                      transform=ax_n.transAxes, ha='right', va='top',
                      fontsize=7, fontweight='bold', color=pat_col,
                      bbox=dict(boxstyle='round,pad=0.2', facecolor=bg,
                                edgecolor=pat_col, alpha=0.95))

            print(f"  {st_name:<22} → {pat:<11} {fr:>5.1f} Hz  CV={cv:.2f} | Burst Spk={spikes_per_burst}, Min w={min_w_val:.2f}")

    out = Path("results/stn_borderline_7_scenarios.png")
    fig.savefig(out, dpi=150, bbox_inches='tight', facecolor='#f8f9fa')
    plt.close(fig)
    print("\n" + "=" * 90)
    print(f"  ✓ {out.resolve()}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 3 — Paired Normal vs PD Scenario Comparison
# ─────────────────────────────────────────────────────────────────────────────
def run_normal_pd_paired_comparison():
    """
    Pair the Normal control with its pathological PD counterpart row-by-row.

    Layout:
      rows = biological paired comparisons
      cols = [Normal Raster | PV- | PV+ ON | PV+ OFF | PD Raster | PV- | PV+ ON | PV+ OFF]
    """
    TOTAL_MS = 3500.0
    # Show the WHOLE run, not just the steady state.  The 2000-3000 ms window
    # used previously hid a real difference: in the Lindahl PD condition the
    # dynamic reset fires only during the initial transient (w starts at 0 and
    # dips negative before settling), so reset ON/OFF differ over 500-1500 ms
    # 1500 ms window starting from 2000 ms [2000ms, 3500ms] as requested
    T_START, T_END = 2000.0, 3500.0
    ANALYSIS_T0 = 2000.0      # fr / CV measured in steady-state window
    N_GPE, N_CTX = 30, 50
    subtype_list = list(MECHANISM_COLUMNS.items())

    # Only the two scenarios that actually carry synaptic input.
    paired_layout = [
        ("Scenario 1 — Lindahl 2016 Baseline Pair", 2, 4,
         "Normal: CTX 250 Hz / GPe 50 Hz  →  PD: CTX 250 Hz / GPe 38 Hz + 20 Hz Beta"),
        ("Scenario 2 — Mallet 2008 Rat Pair", 10, 11,
         "Normal: CTX 13.5 Hz / GPe 33.7 Hz  →  PD: CTX 13.5 Hz + 20.5 Hz Beta / GPe 14.6 Hz + 20.5 Hz Beta"),
    ]

    fig = plt.figure(figsize=(38, 4.8 * len(paired_layout)), facecolor='white')
    fig.suptitle(
        "STN response to paired Normal vs PD presynaptic input",
        fontsize=15, fontweight='bold', y=0.995
    )
    fig.text(0.5, 0.968,
             "PV−: a=+0.3 nS, reset OFF (tonic)   "
             "PV+ Reset OFF: a=−12 nS, reset OFF (does a alone cause burst?)   "
             "PV+ Reset ON: a=−12 nS, reset ON (true burst cell)",
             ha='center', fontsize=9.5, color='#333')
    fig.text(0.5, 0.948,
             "Time window: 2000–3500 ms  |  Green = Normal state,  Red = PD state",
             ha='center', fontsize=9, color='#666')

    # Layout: 2 rows × 8 cols
    # [Normal Raster | PV- | PV+ OFF | PV+ ON | PD Raster | PV- | PV+ OFF | PV+ ON]
    gs = gridspec.GridSpec(len(paired_layout), 8, figure=fig,
                           hspace=0.50, wspace=0.16,
                           left=0.03, right=0.99, top=0.93, bottom=0.07,
                           width_ratios=[0.9, 1.05, 1.05, 1.05, 0.9, 1.05, 1.05, 1.05])

    for row_idx, (title, normal_id, pd_id, note) in enumerate(paired_layout):
        normal_gpe, normal_ctx, normal_weights, _ = generate_scenario(
            normal_id, total_ms=TOTAL_MS, n_gpe=N_GPE, n_ctx=N_CTX, seed=42
        )
        pd_gpe, pd_ctx, pd_weights, _ = generate_scenario(
            pd_id, total_ms=TOTAL_MS, n_gpe=N_GPE, n_ctx=N_CTX, seed=42
        )

        p_pv_plus  = MECHANISM_COLUMNS["PV+ Dynamic Reset ON"]
        p_pv_minus = MECHANISM_COLUMNS["PV-"]

        def _sim(params, gpe, ctx, weights, use_reset):
            g_gaba = weights["g_gaba"]
            w_ampa = weights["w_ampa"]
            g_nmda = weights["g_nmda"]
            return simulate_ad_ex(params, gpe, ctx,
                                  g_gaba=g_gaba, w_ampa=w_ampa, g_nmda=g_nmda,
                                  total_ms=TOTAL_MS, use_dynamic_reset=use_reset)

        def _sim_pd(params, gpe, ctx, use_reset):
            return simulate_ad_ex(params, gpe, ctx,
                                  g_gaba=0.64, w_ampa=0.35, g_nmda=0.15,
                                  total_ms=TOTAL_MS, use_dynamic_reset=use_reset)

        # Normal: PV-, PV+ OFF, PV+ ON
        t_n_m,  v_n_m,  _, _, fr_n_m,  cv_n_m  = _sim(p_pv_minus, normal_gpe, normal_ctx, normal_weights, False)
        t_n_p0, v_n_p0, _, _, fr_n_p0, cv_n_p0 = _sim(p_pv_plus,  normal_gpe, normal_ctx, normal_weights, False)
        t_n_p1, v_n_p1, _, _, fr_n_p1, cv_n_p1 = _sim(p_pv_plus,  normal_gpe, normal_ctx, normal_weights, True)

        # PD: PV-, PV+ OFF, PV+ ON
        t_p_m,  v_p_m,  _, _, fr_p_m,  cv_p_m  = _sim_pd(p_pv_minus, pd_gpe, pd_ctx, False)
        t_p_p0, v_p_p0, _, _, fr_p_p0, cv_p_p0 = _sim_pd(p_pv_plus,  pd_gpe, pd_ctx, False)
        t_p_p1, v_p_p1, _, _, fr_p_p1, cv_p_p1 = _sim_pd(p_pv_plus,  pd_gpe, pd_ctx, True)

        m_n = (t_n_m  >= T_START) & (t_n_m  <= T_END)
        m_p = (t_p_m  >= T_START) & (t_p_m  <= T_END)
        m_np0 = (t_n_p0 >= T_START) & (t_n_p0 <= T_END)
        m_np1 = (t_n_p1 >= T_START) & (t_n_p1 <= T_END)
        m_pp0 = (t_p_p0 >= T_START) & (t_p_p0 <= T_END)
        m_pp1 = (t_p_p1 >= T_START) & (t_p_p1 <= T_END)

        def _panel(col, title, t, v, mask, color, ylabel=True):
            ax = fig.add_subplot(gs[row_idx, col])
            ax.plot(t[mask], v[mask], color=color, lw=1.1)
            ax.axhline(-70, color='gray', lw=0.6, ls=':', alpha=0.55)
            ax.set_xlim(T_START, T_END); ax.set_ylim(-90, 25)
            ax.set_title(title, fontsize=8.5, fontweight='bold', color=color)
            if ylabel:
                ax.set_ylabel("Vm (mV)", fontsize=8)
            ax.tick_params(labelsize=7)
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            return ax

        def _raster(col, gpe_spikes, ctx_spikes, title, title_color):
            ax = fig.add_subplot(gs[row_idx, col])
            gt = [t for t, _ in gpe_spikes if T_START <= t <= T_END]
            gn = [n for t, n in gpe_spikes if T_START <= t <= T_END]
            ct = [t for t, _ in ctx_spikes if T_START <= t <= T_END]
            cn = [n + N_GPE + 2 for t, n in ctx_spikes if T_START <= t <= T_END]
            if gt: ax.scatter(gt, gn, color='#388e3c', marker='|', s=9, alpha=0.8)
            if ct: ax.scatter(ct, cn, color='#1565c0', marker='|', s=9, alpha=0.75)
            ax.axhline(N_GPE + 1, color='gray', lw=0.5, ls='--', alpha=0.5)
            ax.set_xlim(T_START, T_END); ax.set_ylim(-2, N_GPE + N_CTX + 4)
            ax.set_title(title, fontsize=8.5, fontweight='bold', color=title_color)
            ax.set_ylabel("Afferent ID", fontsize=8)
            ax.tick_params(labelsize=7)
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            return ax

        # ──── NORMAL side ────
        _raster(0, normal_gpe, normal_ctx,
                f"{title}\nNormal (GPe green / CTX blue)", '#2e7d32')
        _panel(1, f"PV−  (a=+0.3, reset OFF)\n{fr_n_m:.1f} Hz  CV {cv_n_m:.2f}",
               t_n_m, v_n_m, m_n, '#1565c0')
        _panel(2, f"PV+ Reset OFF  (a=−12)\n{fr_n_p0:.1f} Hz  CV {cv_n_p0:.2f}",
               t_n_p0, v_n_p0, m_np0, '#6a1b9a')
        _panel(3, f"PV+ Reset ON  (a=−12)\n{fr_n_p1:.1f} Hz  CV {cv_n_p1:.2f}",
               t_n_p1, v_n_p1, m_np1, '#2e7d32')

        # ──── PD side ────
        _raster(4, pd_gpe, pd_ctx,
                f"{title}\nPD (GPe green / CTX blue)", '#c62828')
        _panel(5, f"PV−  (a=+0.3, reset OFF)\n{fr_p_m:.1f} Hz  CV {cv_p_m:.2f}",
               t_p_m, v_p_m, m_p, '#1565c0')
        _panel(6, f"PV+ Reset OFF  (a=−12)\n{fr_p_p0:.1f} Hz  CV {cv_p_p0:.2f}",
               t_p_p0, v_p_p0, m_pp0, '#6a1b9a')
        _panel(7, f"PV+ Reset ON = BURST\n{fr_p_p1:.1f} Hz  CV {cv_p_p1:.2f}",
               t_p_p1, v_p_p1, m_pp1, '#c62828')

        if row_idx == len(paired_layout) - 1:
            for col in range(8):
                fig.axes[-(8 - col)].set_xlabel("Time (ms)", fontsize=8, fontweight='bold')

    out = Path("results/stn_normal_vs_pd_pairs.png")
    fig.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  ✓ {out.resolve()}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    Path("results").mkdir(exist_ok=True)
    print("=" * 80)
    print(" STN PV+ Borderline: Tonic → Burst Transition Simulation  [I_ext = 0]")
    print(" 2 Main Scenario Pairs (Lindahl 2016 & Mallet 2008)")
    print("=" * 80)

    generate_phase_diagram()
    # Focus purely on the 2 Main Normal vs PD Scenario Pairs (Pair 1: Lindahl 2016, Pair 2: Mallet 2008)
    run_normal_pd_paired_comparison()

    print("\n✅ Main Normal vs PD Paired Figures saved to results/")


if __name__ == "__main__":
    main()
