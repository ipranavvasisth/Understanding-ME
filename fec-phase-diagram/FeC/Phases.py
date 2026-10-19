from dataclasses import dataclass
from typing import Optional

from .Boundaries import (
    C_CEMENTITE, C_EUT_L, T_A3_FE, T_A4, T_EUTECTIC, T_EUTECTOID,
    T_PERITECTIC, c_at, liquidus_T,
)

SINGLE_NAMES = {
    "L": "Liquid (L)", "δ": "δ-ferrite", "γ": "Austenite (γ)",
    "α": "Ferrite (α)", "Fe3C": "Cementite (Fe₃C)",
}

@dataclass(frozen = True)
class Equilibrium:
    c0: float
    T: float
    region: str
    phases: tuple
    compositions: dict
    fractions: dict
    tie_line: Optional[tuple] = None

def lever_rule(c0: float, c_a: float, c_b: float):
    """Mass fractions (f_a, f_b) of phases with compositions c_a < c_b."""
    f_b = min(1.0, max(0.0, (c0 - c_a) / (c_b - c_a)))
    return 1.0 - f_b, f_b

def _single(c, T, ph):
    return Equilibrium(c, T, SINGLE_NAMES[ph], (ph,), {ph: c}, {ph: 1.0})


def _two(c, T, name, a, b):
    (pa, ca), (pb, cb) = a, b
    lo, hi = sorted([(ca, pa), (cb, pb)])
    fa, fb = lever_rule(c, lo[0], hi[0])
    return Equilibrium(
        c, T, name, (lo[1], hi[1]), {lo[1]: lo[0], hi[1]: hi[0]},
        {lo[1]: fa, hi[1]: fb}, (lo[0], hi[0]),
    )

def equilibrium(c: float, T: float) -> Equilibrium:
    """Equilibrium phases, compositions and mass fractions at (c wt% C, T °C)."""
    if not 0.0 <= c <= C_CEMENTITE:
        raise ValueError(f"carbon content must be within 0–{C_CEMENTITE} wt %")
    if T < 0:
        raise ValueError("temperature must be >= 0 °C")

    if T >= liquidus_T(c):
        return _single(c, T, "L")
    if c >= C_CEMENTITE - 1e-9:
        return _single(c, T, "Fe3C")

    # Above the peritectic: only δ and L+δ exist
    if T > T_PERITECTIC:
        c_s = c_at("delta_solidus", T)
        if c <= c_s:
            return _single(c, T, "δ")
        return _two(c, T, "L + δ", ("δ", c_s), ("L", c_at("liquidus_left", T)))

    # Between eutectic and peritectic temperatures
    if T >= T_EUTECTIC:
        if c > C_EUT_L:
            return _two(c, T, "L + Fe₃C", ("L", c_at("liquidus_right", T)),
                        ("Fe3C", C_CEMENTITE))
        if T > T_A4:
            c_d, c_g = c_at("delta_solvus", T), c_at("gamma_delta", T)
            if c <= c_d:
                return _single(c, T, "δ")
            if c < c_g:
                return _two(c, T, "δ + γ", ("δ", c_d), ("γ", c_g))
        c_gs = c_at("gamma_solidus", T)
        if c <= c_gs:
            return _single(c, T, "γ")
        return _two(c, T, "L + γ", ("γ", c_gs), ("L", c_at("liquidus_left", T)))

    # Between eutectoid and eutectic temperatures
    if T > T_EUTECTOID:
        if T < T_A3_FE:
            c_a, c_a3 = c_at("alpha_gamma", T), c_at("a3", T)
            if c <= c_a:
                return _single(c, T, "α")
            if c < c_a3:
                return _two(c, T, "α + γ", ("α", c_a), ("γ", c_a3))
        c_acm = c_at("acm", T)
        if c <= c_acm:
            return _single(c, T, "γ")
        return _two(c, T, "γ + Fe₃C", ("γ", c_acm), ("Fe3C", C_CEMENTITE))

    # At or below the eutectoid temperature
    c_a = c_at("alpha_solvus", T)
    if c <= c_a:
        return _single(c, T, "α")
    return _two(c, T, "α + Fe₃C", ("α", c_a), ("Fe3C", C_CEMENTITE))
