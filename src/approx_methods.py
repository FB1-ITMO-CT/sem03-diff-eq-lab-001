from collections.abc import Callable

from .defs import Coord, Func, make_coord

Approx = Callable[[Func, Coord, float], Coord]


def adapter(original: Callable[[Func, Coord, float], float]) -> Approx:
    def impl(f: Func, r: Coord, dist: float) -> Coord:
        return r + make_coord(dist, original(f, r, dist))

    return impl


@adapter
def euler(f: Func, r: Coord, dist: float) -> float:
    return f(r) * dist


@adapter
def heun(f: Func, r: Coord, dist: float) -> float:
    y_tmp = dist * (fr := f(r))
    return 0.5 * dist * (fr + f(r + make_coord(dist, y_tmp)))


@adapter
def runge_kutta_4(f: Func, r: Coord, dist: float) -> float:
    half_dist = dist * (1.0 / 2.0)

    k1 = f(r)
    k2 = f(r + make_coord(half_dist, half_dist * k1))
    k3 = f(r + make_coord(half_dist, half_dist * k2))
    k4 = f(r + make_coord(dist, dist * k3))

    return dist * (k1 + k2 + k2 + k3 + k3 + k4) * (1.0 / 6.0)


@adapter
def runge_kutta_4_38(f: Func, r: Coord, dist: float) -> float:
    third_dist = dist * (1.0 / 3.0)

    k1 = f(r)
    k2 = f(r + make_coord(third_dist, third_dist * k1))
    k3 = f(r + make_coord(third_dist + third_dist, -third_dist * k1 + dist * k2))
    k4 = f(r + make_coord(dist, dist * (k1 - k2 + k3)))

    return dist * (k1 + k2 * 3 + k3 * 3 + k4) * (1.0 / 8.0)


@adapter
def runge_kutta_5(f: Func, r: Coord, dist: float = 0.1) -> float:
    table = [
        (1.0 / 3.0, [1.0 / 3.0]),
        (2.0 / 5.0, [4.0 / 25.0, 6.0 / 25.0]),
        (1.0, [1.0 / 4.0, -3.0, 15.0 / 4.0]),
        (2.0 / 3.0, [2.0 / 27.0, 10.0 / 9.0, -50.0 / 81.0, 8.0 / 81.0]),
        (4.0 / 5.0, [2.0 / 25.0, 12.0 / 25.0, 2.0 / 15.0, 8.0 / 75.0]),
    ]

    ks = [f(r)]

    for off, coeffs in table:
        point = r + make_coord(off, sum(k * c for k, c in zip(ks, coeffs, strict=False))) * dist
        ks.append(f(point))

    return (ks[0] * (23.0 / 192.0) + ks[2] * (125.0 / 192.0) + ks[4] * (-27.0 / 64.0) + ks[5] * (125.0 / 192.0)) * dist
