"""Matplotlib drawing helpers for the Fe–Fe3C diagram."""
import matplotlib.pyplot as plt

from .Boundaries import BOUNDARIES, HORIZONTALS, T_CURIE, T_ROOM

# (x, y, text) or (x, y, text, (x_target, y_target)) for a leader arrow
REGION_LABELS = [
    (3.0, 1400, "Liquid (L)"), (0.30, 1440, "δ", (0.04, 1470)),
    (1.1, 960, "Austenite (γ)"), (0.75, 870, "α + γ", (0.05, 850)),
    (0.60, 480, "α", (0.012, 450)), (3.3, 1040, "γ + Fe₃C"),
    (3.0, 1170, "L + γ"), (5.2, 1330, "L + Fe₃C", (5.5, 1172)),
    (3.3, 400, "α + Fe₃C"), (6.35, 800, "Fe₃C"),
]
INVARIANT_POINTS = {"P": (0.53, 1493), "E": (4.30, 1147),
                    "S": (0.76, 727), "C": (2.14, 1147)}


def draw_phase_diagram(ax, labels=True):
    for pts in BOUNDARIES.values():
        xs, ys = zip(*pts)
        ax.plot(xs, ys, "k", lw=1.5)
    for c0, c1, T in HORIZONTALS.values():
        ax.plot([c0, c1], [T, T], "k", lw=1.5)
    ax.plot([0, 0.58], [T_CURIE, T_CURIE], color="gray", ls="--", lw=1)
    for name, (x, y) in INVARIANT_POINTS.items():
        ax.plot(x, y, "o", color="darkred", ms=4)
        ax.annotate(name, (x, y), textcoords="offset points", xytext=(5, 5),
                    fontsize=8, color="darkred")
    if labels:
        for x, y, t, *target in REGION_LABELS:
            if target:
                ax.annotate(t, xy=target[0], xytext=(x, y), fontsize=9, ha="center",
                            arrowprops=dict(arrowstyle="-", color="gray", lw=0.8))
            else:
                ax.text(x, y, t, fontsize=9, ha="center")
    ax.axvline(2.14, color="gray", lw=0.6, ls=":")
    ax.text(1.07, 60, "Steels", ha="center", fontsize=9, style="italic")
    ax.text(4.4, 60, "Cast irons", ha="center", fontsize=9, style="italic")
    ax.set(xlim=(0, 6.9), ylim=(0, 1600), xlabel="Carbon content (wt %)",
           ylabel="Temperature (°C)", title="Fe–Fe₃C phase diagram (schematic)")
    ax.grid(alpha=0.25)


def phase_diagram_figure(eq=None, path_from=None, figsize=(8.5, 6.2)):
    """Diagram with optional operating point/tie-line (eq) and cooling path.

    eq: an Equilibrium; path_from: starting temperature of a vertical cooling path.
    """
    fig, ax = plt.subplots(figsize=figsize)
    draw_phase_diagram(ax)
    if eq is not None:
        if path_from is not None:
            ax.plot([eq.c0, eq.c0], [path_from, T_ROOM], color="C0", lw=1.2, ls="-.")
        if eq.tie_line:
            ax.plot(eq.tie_line, [eq.T, eq.T], color="C0", lw=2.5)
            for cc in eq.tie_line:
                ax.plot(cc, eq.T, "|", color="C0", ms=14, mew=2)
        ax.plot(eq.c0, eq.T, "o", color="C1", ms=9, mec="k", zorder=5)
    fig.tight_layout()
    return fig
