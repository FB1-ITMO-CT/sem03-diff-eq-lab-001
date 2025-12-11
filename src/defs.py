from collections.abc import Callable

import numpy as np
import numpy.typing as npt

Coord = npt.NDArray[np.float64]
Func = Callable[[Coord], float]


def make_coord(x: float, y: float) -> Coord:
    return np.array((x, y), dtype=np.float64)
