"""Streamlit app: interactive Fe–Fe3C phase diagram explorer."""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from FeC.Boundaries import C_CEMENTITE
from FeC.Cooling import (classify_alloy, cooling_events, fraction_history,
                         room_temperature_microstructure)
from FeC.Phases import equilibrium
from FeC.Plot import phase_diagram_figure
from FeC.Properties import estimate_properties
from FeC.ttt import ttt_figure

st.set_page_config(page_title="Fe–Fe₃C Explorer", layout="wide")
st.title("Fe–Fe₃C Phase Diagram Explorer")
st.caption("Schematic diagram built from textbook invariant points with linear "
           "boundaries. For learning and reports, not quantitative design.")

c = st.sidebar.slider("Carbon content (wt %)", 0.0, C_CEMENTITE, 0.40, 0.01)
st.sidebar.markdown(f"**{classify_alloy(c)}**")


def show(fig):
    st.pyplot(fig)
    plt.close(fig)


def fraction_table(eq):
    return pd.DataFrame({
        "Phase": list(eq.phases),
        "Composition (wt % C)": [round(eq.compositions[p], 3) for p in eq.phases],
        "Mass fraction": [round(eq.fractions[p], 4) for p in eq.phases],
    })


tab1, tab2, tab3, tab4 = st.tabs(
    ["Phase explorer", "Cooling simulator", "Microstructure & properties", "TTT (schematic)"])

with tab1:
    T = st.slider("Temperature (°C)", 25, 1600, 800, key="T_explore")
    eq = equilibrium(c, float(T))
    left, right = st.columns([3, 2])
    with left:
        show(phase_diagram_figure(eq))
    with right:
        st.subheader(eq.region)
        st.dataframe(fraction_table(eq), hide_index=True)
        if eq.tie_line:
            st.caption(f"Tie-line at {T} °C: {eq.tie_line[0]:.3f} to "
                       f"{eq.tie_line[1]:.3f} wt % C (lever rule).")

with tab2:
    T_now = st.slider("Cooling: current temperature (°C)", 25, 1600, 1600, key="T_cool")
    eq2 = equilibrium(c, float(T_now))
    left, right = st.columns([3, 2])
    with left:
        show(phase_diagram_figure(eq2, path_from=1600))
    with right:
        st.subheader(eq2.region)
        st.dataframe(fraction_table(eq2), hide_index=True)
        st.markdown("**Transformations on slow cooling**")
        events = cooling_events(c)
        if events:
            st.dataframe(pd.DataFrame(events).rename(columns={
                "T": "T (°C)", "from": "From", "to": "To", "event": "Reaction"}),
                hide_index=True)
    Ts, hist = fraction_history(c)
    df = pd.DataFrame({p: v for p, v in hist.items() if v.any()}, index=Ts)
    df.index.name = "Temperature (°C)"
    st.markdown("**Phase fractions vs temperature**")
    st.line_chart(df)

with tab3:
    micro = room_temperature_microstructure(c)
    props = estimate_properties(c)
    left, right = st.columns(2)
    with left:
        st.subheader("Room-temperature microconstituents")
        st.dataframe(pd.DataFrame({"Constituent": list(micro),
                                   "Mass fraction": [round(v, 4) for v in micro.values()]}),
                     hide_index=True)
        st.bar_chart(pd.Series(micro, name="Mass fraction"))
    with right:
        st.subheader("Property estimates (indicative)")
        if props["HB"] is None:
            st.info(props["note"])
        else:
            st.metric("Hardness (HB)", props["HB"])
            if props["UTS_MPa"] is not None:
                st.metric("UTS (MPa)", props["UTS_MPa"])
            st.caption(props["note"])

with tab4:
    st.caption("Schematic only: a single C-curve for eutectoid steel. "
               "Real TTT diagrams are measured and composition-dependent.")
    show(ttt_figure())
