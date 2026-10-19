"""Slow (equilibrium) cooling: transformation events, phase fractions, microstructure."""
import numpy as np

from .Boundaries import (
    C_CEMENTITE, C_EUT_GAMMA, C_EUT_L, C_EUTECTOID, C_EUTECTOID_ALPHA,
    T_EUTECTIC, T_EUTECTOID, T_PERITECTIC, T_ROOM,
)
from .Phases import equilibrium

INVARIANTS = {
    T_PERITECTIC: "Peritectic reaction",
    T_EUTECTIC: "Eutectic reaction",
    T_EUTECTOID: "Eutectoid reaction",
}
PHASES = ("L", "δ", "γ", "α", "Fe3C")


def _refine(c, T_hi, T_lo, hi_region, tol=1e-3):
    """Bisect for the temperature where the region changes from `hi_region`."""
    while T_hi - T_lo > tol:
        mid = 0.5 * (T_hi + T_lo)
        if equilibrium(c, mid).region == hi_region:
            T_hi = mid
        else:
            T_lo = mid
    return 0.5 * (T_hi + T_lo)


def cooling_events(c, T_start=1600.0, T_end=T_ROOM, dT=1.0):
    """List of region changes met while slowly cooling an alloy of composition c."""
    Ts = np.arange(T_start, T_end - 1e-9, -dT)
    events, prev = [], equilibrium(c, Ts[0])
    for T_hi, T_lo in zip(Ts[:-1], Ts[1:]):
        cur = equilibrium(c, T_lo)
        if cur.region != prev.region:
            T_x = _refine(c, T_hi, T_lo, prev.region)
            label = next((n for Ti, n in INVARIANTS.items() if abs(T_x - Ti) < 0.5), "")
            events.append({"T": round(T_x, 1), "from": prev.region,
                           "to": cur.region, "event": label})
        prev = cur
    return events


def fraction_history(c, T_start=1600.0, T_end=T_ROOM, dT=5.0):
    """(temperatures, {phase: mass-fraction array}) along the cooling path."""
    Ts = np.arange(T_start, T_end - 1e-9, -dT)
    out = {p: np.zeros(len(Ts)) for p in PHASES}
    for i, T in enumerate(Ts):
        for p, f in equilibrium(c, T).fractions.items():
            out[p][i] = f
    return Ts, out


def classify_alloy(c):
    """Textbook classification by carbon content (wt %)."""
    if c < C_EUTECTOID_ALPHA:
        return "Iron (ferritic, below max C solubility in α)"
    if abs(c - C_EUTECTOID) < 0.01:
        return "Eutectoid steel"
    if c < C_EUTECTOID:
        return "Hypoeutectoid steel"
    if c <= C_EUT_GAMMA:
        return "Hypereutectoid steel"
    if abs(c - C_EUT_L) < 0.02:
        return "Eutectic cast iron (white)"
    if c < C_EUT_L:
        return "Hypoeutectic cast iron (white)"
    return "Hypereutectic cast iron (white)"


def room_temperature_microstructure(c):
    """Mass fractions of microconstituents after slow cooling (metastable Fe–Fe3C).

    Standard textbook lever-rule results. Cast irons assume white iron
    (no graphite); ledeburite is the eutectic mixture of austenite + Fe3C that
    transforms on further cooling.
    """
    if c < C_EUTECTOID_ALPHA:
        return {"Ferrite": 1.0}
    if abs(c - C_EUTECTOID) < 0.01:
        return {"Pearlite": 1.0}
    if c < C_EUTECTOID:
        w_pearlite = (c - C_EUTECTOID_ALPHA) / (C_EUTECTOID - C_EUTECTOID_ALPHA)
        return {"Proeutectoid ferrite": 1 - w_pearlite, "Pearlite": w_pearlite}
    if c <= C_EUT_GAMMA:
        w_cem = (c - C_EUTECTOID) / (C_CEMENTITE - C_EUTECTOID)
        return {"Proeutectoid cementite": w_cem, "Pearlite": 1 - w_cem}
    if abs(c - C_EUT_L) < 0.02:
        return {"Ledeburite": 1.0}
    if c < C_EUT_L:
        w_led = (c - C_EUT_GAMMA) / (C_EUT_L - C_EUT_GAMMA)
        return {"Primary austenite (→ pearlite + Fe₃C)": 1 - w_led, "Ledeburite": w_led}
    w_prim = (c - C_EUT_L) / (C_CEMENTITE - C_EUT_L)
    return {"Primary cementite": w_prim, "Ledeburite": 1 - w_prim}
