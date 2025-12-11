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

    if (r0 == r0).any():
        coords.append(r0[0])
        result.append(r0[1])

    return coords, result


X_VALUE_INIT = 0.0
Y_VALUE_RANGE = (-0.1, 2)
Y_VALUE_INIT = 1.0


def render(x_value_range: tuple[float, float], precision: float) -> tuple[mpl_fig.Figure, mpl_ax.Axes]:
    fig, ax = plt.subplots(1, 1, layout="constrained", figsize=(12, 8))

    r0 = make_coord(X_VALUE_INIT, Y_VALUE_INIT)

    def condition(r: Coord) -> bool:
        return (
            r[0] >= x_value_range[0]
            and r[0] <= x_value_range[1]
            and r[1] >= Y_VALUE_RANGE[0]
            and r[1] <= Y_VALUE_RANGE[1]
        )

    ax.plot(
        xs := np.arange(*x_value_range, (x_value_range[1] - x_value_range[0]) / 666),
        solution(xs),
        label="true value",
        linestyle=":",
        linewidth=3.0,
        color="green",
    )

    for method in ("euler", "heun", "runge kutta 4", "runge_kutta 4 38", "runge kutta 5"):
        f = getattr(approx_methods, "_".join(method.split()))
        if x_value_range[1] > X_VALUE_INIT:
            ax.plot(*iterate(f, r0, condition, precision), label=method)
        if x_value_range[0] < X_VALUE_INIT:
            ax.plot(*iterate(f, r0, condition, -precision), label=method)

    ax.set_xlim(*x_value_range)
    ax.set_ylim(*Y_VALUE_RANGE)
    ax.legend(loc="upper right", ncols=1)

    return (fig, ax)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("precision", default=0.1, type=float)
    parser.add_argument("-x_min", default=X_VALUE_INIT, type=float)
    parser.add_argument("-x_max", default=8.0, type=float)
    parser.add_argument("-out", type=str)

    args = parser.parse_args()

    if not (args.x_min <= args.x_max):
        raise ValueError("Range arguments have to be ordered correctly")

    fig, _ = render((args.x_min, args.x_max), abs(tp.cast("float", args.precision)))

    if args.out is not None:
        fig.savefig(args.out)
    else:
        fig.show()
        plt.show()


if __name__ == "__main__":
    main()
