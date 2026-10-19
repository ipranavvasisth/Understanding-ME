"""Rough property estimates by rule of mixtures. INDICATIVE ONLY.

Constituent values are approximate typical figures for slow-cooled (annealed)
plain-carbon steel. Real properties depend on grain size, interlamellar
spacing, alloying and heat treatment (typically ±15–20 % or worse). Check
them against a handbook (e.g. ASM Handbook) before citing numbers.
"""
from .Boundaries import C_EUT_GAMMA, C_EUTECTOID
from .Cooling import room_temperature_microstructure

# constituent: (Brinell hardness, UTS in MPa or None)
CONSTITUENT_PROPS = {
    "Ferrite": (90, 300),
    "Proeutectoid ferrite": (90, 300),
    "Pearlite": (200, 680),
    "Proeutectoid cementite": (700, None),  # hard and brittle; UTS not mixed
}


def estimate_properties(c):
    """Approximate hardness (HB) and UTS (MPa) of a slow-cooled steel, else Nones."""
    if c > C_EUT_GAMMA:
        return {"HB": None, "UTS_MPa": None,
                "note": "Cast irons are not covered (brittle, graphite/ledeburite dependent)."}
    micro = room_temperature_microstructure(c)
    hb = sum(f * CONSTITUENT_PROPS[k][0] for k, f in micro.items())
    uts = None
    if c <= C_EUTECTOID + 0.01:
        uts = sum(f * CONSTITUENT_PROPS[k][1] for k, f in micro.items())
    note = "Rule-of-mixtures estimate for annealed plain-carbon steel; ±15–20 % or more."
    if uts is None:
        note += " UTS omitted: grain-boundary cementite makes it brittle, not additive."
    return {"HB": round(hb), "UTS_MPa": None if uts is None else round(uts), "note": note}
