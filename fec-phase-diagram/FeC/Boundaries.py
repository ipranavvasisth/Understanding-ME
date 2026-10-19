import numpy as np


#Pure Fe
T_MELT_FE, T_A4, T_A3_FE, T_CURIE = 1538.0, 1394.0, 912.0, 770.0
T_MELT_CEMENTITE = 1227.0
C_CEMENTITE = 6.67

#Reactions
T_PERITECTIC, T_EUTECTIC, T_EUTECTOID = 1493.0, 1147.0, 727.0
C_PERI_DELTA, C_PERI_GAMMA, C_PERI_L = 0.09, 0.17, 0.53
C_EUT_GAMMA, C_EUT_L = 2.14, 4.30
C_EUTECTOID, C_EUTECTOID_ALPHA = 0.76, 0.022
C_ALPHA_ROOM = 0.006
T_ROOM = 25

#Boundaries of the plot all the different phases
#Each phase is a list of (wt% C, T °C) points
BOUNDARIES = {
    "liquidus_left": [(0, 1538), (0.53, 1493), (4.30, 1147)],
    "liquidus_right": [(4.30, 1147), (6.67, 1227)],
    "delta_solidus": [(0, 1538), (0.09, 1493)],
    "delta_solvus": [(0, 1394), (0.09, 1493)],   # δ / (δ+γ)
    "gamma_delta": [(0, 1394), (0.17, 1493)],    # γ / (δ+γ)
    "gamma_solidus": [(0.17, 1493), (2.14, 1147)],
    "a3": [(0, 912), (0.76, 727)],               # γ / (α+γ)
    "acm": [(0.76, 727), (2.14, 1147)],          # γ / (γ+Fe3C)
    "alpha_gamma": [(0, 912), (0.022, 727)],     # α / (α+γ)
    "alpha_solvus": [(0.006, 25), (0.022, 727)], # α / (α+Fe3C)
    "cementite": [(6.67, 25), (6.67, 1227)],
}

# Invariant lines: (c_min, c_max, T)
HORIZONTALS = {
    "peritectic": (0.09, 0.53, 1493),
    "eutectic": (2.14, 6.67, 1147),
    "eutectoid": (0.0, 6.67, 727),
}

LIQUIDUS = BOUNDARIES["liquidus_left"] + BOUNDARIES["liquidus_right"][1:]


def c_at(name: str, T: float) -> float:
    """Composition of boundary `name` at temperature T (linear interpolation)."""
    cs, Ts = zip(*BOUNDARIES[name])
    order = np.argsort(Ts)
    return float(np.interp(T, np.array(Ts)[order], np.array(cs)[order]))


def liquidus_T(c: float) -> float:
    """Liquidus temperature at composition c."""
    cs, Ts = zip(*LIQUIDUS)
    return float(np.interp(c, cs, Ts))