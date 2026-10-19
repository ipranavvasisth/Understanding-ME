import numpy as np
import pytest

from FeC.Phases import equilibrium


def test_liquid():
    assert equilibrium(1.0, 1600).phases == ("L",)


def test_eutectoid_lever_rule_matches_textbook():
    eq = equilibrium(0.76, 700)
    assert eq.phases == ("α", "Fe3C")
    assert eq.fractions["α"] == pytest.approx(0.889, abs=0.003)
    assert eq.fractions["Fe3C"] == pytest.approx(0.111, abs=0.003)


@pytest.mark.parametrize("c,T,phases", [
    (0.76, 800, ("γ",)),
    (0.01, 600, ("α",)),
    (0.50, 600, ("α", "Fe3C")),
    (0.40, 800, ("α", "γ")),
    (3.00, 1200, ("γ", "L")),
    (5.50, 1170, ("L", "Fe3C")),
    (3.00, 1000, ("γ", "Fe3C")),
    (0.30, 1480, ("γ", "L")),
    (0.05, 1520, ("δ", "L")),
    (0.07, 1450, ("δ", "γ")),
    (6.67, 500, ("Fe3C",)),
])
def test_regions(c, T, phases):
    assert set(equilibrium(c, T).phases) == set(phases)


def test_alpha_gamma_fraction():
    eq = equilibrium(0.40, 800)
    assert 0.85 < eq.fractions["γ"] < 0.88


def test_fractions_sum_to_one_everywhere():
    for c in np.linspace(0, 6.67, 40):
        for T in np.linspace(25, 1600, 60):
            eq = equilibrium(float(c), float(T))
            assert sum(eq.fractions.values()) == pytest.approx(1.0)
            assert all(-1e-9 <= f <= 1 + 1e-9 for f in eq.fractions.values())


def test_invalid_inputs():
    with pytest.raises(ValueError):
        equilibrium(7.0, 800)
    with pytest.raises(ValueError):
        equilibrium(0.5, -10)
