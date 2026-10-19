"""Overlay a CALPHAD (pycalphad) Fe–C diagram on this project's schematic one.

Usage:  python validation/pycalphad_compare.py --tdb path/to/Fe-C.tdb

Needs `pip install pycalphad` and an Fe–C thermodynamic database (.tdb) that
includes a cementite phase. pycalphad plots in atom fraction, so this project's
wt % C boundaries are converted before overlaying (dashed red lines).
NOTE: written against the pycalphad binplot API but not run in the project's
test setup because no .tdb file is bundled.
"""
import argparse
import os
import sys

import matplotlib.pyplot as plt
from pycalphad import Database, binplot, variables as v

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from FeC.Boundaries import BOUNDARIES, HORIZONTALS  # noqa: E402

M_FE, M_C = 55.845, 12.011


def wt_to_x(w):
    n_c, n_fe = w / M_C, (100.0 - w) / M_FE
    return n_c / (n_c + n_fe)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tdb", required=True)
    ap.add_argument("--phases", nargs="+",
                    default=["LIQUID", "BCC_A2", "FCC_A1", "CEMENTITE"])
    args = ap.parse_args()

    dbf = Database(args.tdb)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    binplot(dbf, ["FE", "C", "VA"], args.phases,
            {v.X("C"): (0, 0.26, 0.005), v.T: (400, 1900, 10), v.P: 101325, v.N: 1},
            plot_kwargs={"ax": ax})

    first = True
    for pts in BOUNDARIES.values():
        xs = [wt_to_x(c) for c, _ in pts]
        ax.plot(xs, [T + 273.15 for _, T in pts], "r--", lw=1.2,
                label="schematic (this project)" if first else None)
        first = False
    for c0, c1, T in HORIZONTALS.values():
        ax.plot([wt_to_x(c0), wt_to_x(c1)], [T + 273.15] * 2, "r--", lw=1.2)
    ax.legend()
    ax.set_title("CALPHAD (pycalphad) vs schematic Fe–Fe₃C diagram (T in K)")
    fig.savefig("validation_overlay.png", dpi=200)
    plt.show()


if __name__ == "__main__":
    main()
