import itertools
import os

precisions = tuple(2 ** (-0.5 * val) for val in range(27))
fnames = tuple(f"standard-{precision:.06f}-h.png" for precision in precisions)

for precision, fname in zip(precisions[::-1], fnames[::-1], strict=True):
    os.system(f"run {precision} -out ./examples/{fname} -x_min -8.0 -x_max 8.0")

with open("./examples/ffmpeg_list.txt", "w") as f:
    print("ffconcat version 1.0  ", file=f)

    for fname in itertools.chain(fnames, fnames[-2:0:-1]):
        print(f"file '{fname}' ", file=f)
        print("duration 0.1", file=f)
