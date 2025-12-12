import itertools
import os


def standard_animation() -> None:
    precisions = tuple(2 ** (-0.5 * val) for val in range(27))
    fnames = tuple(f"standard-{precision:.06f}-h.png" for precision in precisions)

    for precision, fname in zip(precisions[::-1], fnames[::-1], strict=True):
        os.system(f"run {precision} -out ./examples/{fname} -x_min -8.0 -x_max 8.0")

    with open("./examples/ffmpeg_list-standard.txt", "w") as f:
        print("ffconcat version 1.0  ", file=f)

        for fname in itertools.chain(fnames, fnames[-2:0:-1]):
            print(f"file '{fname}' ", file=f)
            print("duration 0.1", file=f)


def delta_animation() -> None:
    precisions = tuple(2 ** (-val) for val in range(1, 7))
    fnames = tuple(f"delta-{precision:.06f}-h.png" for precision in precisions)

    for precision, fname in zip(precisions[::-1], fnames[::-1], strict=True):
        os.system(f"run {precision} -out ./examples/{fname} -x_max 2.0 --delta")

    with open("./examples/ffmpeg_list-delta.txt", "w") as f:
        print("ffconcat version 1.0  ", file=f)

        for fname in itertools.chain(fnames, fnames[-2:0:-1]):
            print(f"file '{fname}' ", file=f)
            print("duration 1.0", file=f)
        print(f"file '{fnames[0]}' ", file=f)
        print("duration 0.01", file=f)


def main() -> None:
    raise Exception("This file is not intended for direct use, modify before running!")


if __name__ == "__main__":
    main()
