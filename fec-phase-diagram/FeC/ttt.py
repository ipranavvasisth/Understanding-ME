"""SCHEMATIC isothermal transformation (TTT) diagram for eutectoid steel.

Qualitative only: one C-curve with a nose near 540 °C. Real diagrams have
separate pearlite and bainite curves and depend on composition and grain size.
"""
import numpy as np
import matplotlib.pyplot as plt

from .Boundaries import T_EUTECTOID

T_NOSE, T_NOSE_TIME, T_SLOW_TIME = 540.0, 1.0, 1e4  # °C, s, s (schematic choices)


def martensite_start(c):
    """Andrews linear estimate for plain carbon steel (°C): Ms ≈ 539 − 423·C."""
    return 539.0 - 423.0 * c


def ttt_curves(c=0.76, n=300):
    Ms = martensite_start(c)
    Mf = Ms - 215.0  # rough rule of thumb
    Ts = np.linspace(Ms + 3, T_EUTECTOID - 3, n)
    k = np.log(T_SLOW_TIME / T_NOSE_TIME)
    span = np.where(Ts >= T_NOSE, T_EUTECTOID - T_NOSE, T_NOSE - Ms)
    t_start = T_NOSE_TIME * np.exp(k * ((Ts - T_NOSE) / span) ** 2)
    return {"T": Ts, "start": t_start, "finish": 8 * t_start, "Ms": Ms, "Mf": Mf}


def ttt_figure(c=0.76, figsize=(7.5, 5.5)):
    d = ttt_curves(c)
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(d["start"], d["T"], "k", lw=1.8, label="Transformation start")
    ax.plot(d["finish"], d["T"], "k--", lw=1.4, label="Transformation finish")
    ax.axhline(T_EUTECTOID, color="C3", lw=1.2)
    ax.axhline(d["Ms"], color="C0", lw=1.2)
    ax.axhline(d["Mf"], color="C0", lw=1.0, ls=":")
    ax.text(0.15, T_EUTECTOID + 8, "A₁ (727 °C)", color="C3", fontsize=9)
    ax.text(0.15, d["Ms"] + 8, f"Mₛ ≈ {d['Ms']:.0f} °C", color="C0", fontsize=9)
    ax.text(0.15, d["Mf"] + 8, f"M_f ≈ {d['Mf']:.0f} °C", color="C0", fontsize=9)
    ax.text(0.3, 700, "Austenite (γ)", fontsize=10)
    ax.text(2e3, 640, "Pearlite", fontsize=10)
    ax.text(2e3, 430, "Bainite", fontsize=10)
    ax.text(0.3, d["Ms"] - 60, "Martensite", fontsize=10)
    ax.set_xscale("log")
    ax.set_xlim(0.1, 1e6)
    ax.set_ylim(0, 800)
    ax.set_xlabel("Time (s, log scale)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title(f"Schematic TTT diagram, eutectoid steel ({c:.2f} wt % C)")
    ax.grid(alpha=0.25, which="both")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    return fig
