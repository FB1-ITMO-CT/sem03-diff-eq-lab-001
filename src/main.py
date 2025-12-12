import argparse
import typing as tp

import matplotlib.axes as mpl_ax
import matplotlib.figure as mpl_fig
import matplotlib.pyplot as plt
import numba
import numpy as np

from . import approx_methods
from .defs import Coord, make_coord

if tp.TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from .approx_methods import Approx


@numba.jit
def func(r: Coord) -> float:
    x, y = r
    return x**3 * y**3 - x * y


def solution[T](x: T) -> T:
    return 1 / np.sqrt(x**2 + 1)  # pyright: ignore[reportOperatorIssue]


def iterate(
    approx: Approx,
    r0: Coord,
    condition: Callable[[Coord], bool],
    precision: float,
) -> tuple[Sequence[float], Sequence[float]]:
    """Iterates using selected approximation function.
    Simply follows direction and tests condition.
    """
    coords: list[float] = []
    result: list[float] = []

    def impl(r0: Coord) -> Coord:
        return approx(func, r0, precision)

    while condition(r0):
        coords.append(r0[0])
        result.append(r0[1])
        r0 = impl(r0)

    return coords, result


X_VALUE_INIT = 0.0
Y_VALUE_INIT = 1.0
Y_VALUE_RANGE = (-0.1, 2)

ALL_APPROX_FUNCTIONS = ["euler", "heun", "runge kutta 4", "runge_kutta 4 38", "runge kutta 5"]

SETTINGS: dict[str, tp.Any] = {
    "SHOW_DEVIATION": False,
    "APPROX_FUNCTIONS": ALL_APPROX_FUNCTIONS[:3],
    "X_VALUE_RANGE": [X_VALUE_INIT, 8.0],
}


def render(precision: float) -> tuple[mpl_fig.Figure, mpl_ax.Axes]:
    x_value_range = SETTINGS["X_VALUE_RANGE"]
    approx_functions = SETTINGS["APPROX_FUNCTIONS"]
    show_deviation = SETTINGS["SHOW_DEVIATION"]

    fig, ax = plt.subplots(1, 1, layout="constrained", figsize=(12, 8))

    r0 = make_coord(X_VALUE_INIT, Y_VALUE_INIT)

    def condition(r: Coord) -> bool:
        return (
            (r0 == r0).any() and r[0] >= x_value_range[0] and r[0] <= x_value_range[1]
            # and r[1] >= Y_VALUE_RANGE[0]
            # and r[1] <= Y_VALUE_RANGE[1]
        )

    ax.plot(
        xs := np.arange(x_value_range[0], x_value_range[1], (x_value_range[1] - x_value_range[0]) / 666),
        solution(xs),
        label="true value",
        linestyle=":",
        linewidth=3.0,
        color="green",
    )

    for method in approx_functions:
        f = getattr(approx_methods, "_".join(method.split()))

        line = ax.plot([X_VALUE_INIT], [Y_VALUE_INIT], label=method)[0]
        dev, rel_dev = 0.0, 0.0

        for signed_precision in (precision, -precision):
            xs, ys = iterate(f, r0, condition, signed_precision)
            ax.plot(xs, ys, color=line.get_color())

            true_ys = solution(np.array(xs))

            if show_deviation:
                dev = max(dev, np.max(np.abs(true_ys - ys)))
                rel_dev = max(rel_dev, np.max(np.abs((true_ys - ys) / true_ys)))

        if show_deviation:
            line.set_label(f"{method}: Δ={dev:.02E} δ={rel_dev:.02E}")

    ax.set_xlim(*x_value_range)
    ax.set_ylim(*Y_VALUE_RANGE)
    ax.set_title(f"[{x_value_range[0]:.3f}; {x_value_range[1]:.3f}] range with {precision:.6f} precision")
    ax.legend(loc="upper right", ncols=1)

    return (fig, ax)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("precision", default=0.1, type=float, metavar="step", help="Approximation step")
    parser.add_argument("-x_min", default=X_VALUE_INIT, type=float, metavar="range[0]", help="Displayed range start")
    parser.add_argument("-x_max", default=8.0, type=float, metavar="range[1]", help="Displayed range end")
    parser.add_argument(
        "-out",
        type=str,
        metavar="{*.png, *.jpg, ...}",
        help="Enables writting to file, pass destination file path",
    )
    parser.add_argument(
        "-methods",
        default=[*SETTINGS["APPROX_FUNCTIONS"]],
        nargs="+",
        type=str,
        metavar="method",
        choices=ALL_APPROX_FUNCTIONS,
        help=f"list of approximation function from `approx_methods.py`: {'{'}{', '.join(ALL_APPROX_FUNCTIONS)}{'}'}",
    )
    parser.add_argument(
        "--delta",
        default=SETTINGS["SHOW_DEVIATION"],
        action="store_true",
        help="show Δ and δ",
    )

    args = parser.parse_args()

    if not (args.x_min <= args.x_max):
        raise ValueError("Range arguments have to be ordered correctly")

    SETTINGS["APPROX_FUNCTIONS"] = args.methods
    SETTINGS["X_VALUE_RANGE"] = (args.x_min, args.x_max)
    SETTINGS["SHOW_DEVIATION"] = args.delta

    fig, _ = render(abs(tp.cast("float", args.precision)))

    if args.out is not None:
        fig.savefig(args.out)
    else:
        fig.show()
        plt.show()


if __name__ == "__main__":
    main()
