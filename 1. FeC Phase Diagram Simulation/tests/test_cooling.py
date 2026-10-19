import pytest

from FeC.Cooling import (classify_alloy, cooling_events,
                         room_temperature_microstructure)
from FeC.Properties import estimate_properties


def _reaction_temp(events, name):
    return next(e["T"] for e in events if e["event"] == name)


def test_eutectoid_steel_transforms_at_727():
    events = cooling_events(0.76)
    assert _reaction_temp(events, "Eutectoid reaction") == pytest.approx(727, abs=0.5)
    assert events[-1]["to"] == "α + Fe₃C"


def test_hypoeutectoid_path_has_peritectic_and_eutectoid():
    events = cooling_events(0.40)
    assert _reaction_temp(events, "Peritectic reaction") == pytest.approx(1493, abs=0.5)
    assert _reaction_temp(events, "Eutectoid reaction") == pytest.approx(727, abs=0.5)


def test_eutectic_cast_iron_solidifies_at_1147():
    assert _reaction_temp(cooling_events(4.30), "Eutectic reaction") == pytest.approx(1147, abs=0.5)


def test_microstructure_fractions():
    m = room_temperature_microstructure(0.40)
    assert m["Pearlite"] == pytest.approx(0.512, abs=0.005)
    assert sum(m.values()) == pytest.approx(1.0)
    assert room_temperature_microstructure(0.76) == {"Pearlite": 1.0}
    m = room_temperature_microstructure(1.2)
    assert m["Proeutectoid cementite"] == pytest.approx(0.0744, abs=0.002)


@pytest.mark.parametrize("c", [0.01, 0.4, 0.76, 1.2, 3.0, 4.3, 5.5])
def test_microstructure_always_sums_to_one(c):
    assert sum(room_temperature_microstructure(c).values()) == pytest.approx(1.0)


def test_classification():
    assert classify_alloy(0.3) == "Hypoeutectoid steel"
    assert classify_alloy(0.76) == "Eutectoid steel"
    assert classify_alloy(1.2) == "Hypereutectoid steel"
    assert "Hypoeutectic" in classify_alloy(3.0)


def test_property_estimates_plausible():
    p = estimate_properties(0.40)
    assert 130 < p["HB"] < 170 and 450 < p["UTS_MPa"] < 600
    assert estimate_properties(3.0)["HB"] is None
