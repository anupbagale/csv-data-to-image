"""Make docs/overview.png, the figure at the top of the README.

Run from the repository root:  python scripts/make_overview.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from skimage import data  # noqa: E402

out = Path(__file__).resolve().parents[1] / "docs" / "overview.png"
out.parent.mkdir(exist_ok=True)

image = data.camera()
r, c, n = 125, 220, 8
patch = image[r:r + n, c:c + n]

fig, ax = plt.subplots(1, 3, figsize=(16, 5.6), gridspec_kw={"width_ratios": [1, 1, 1]})

ax[0].imshow(image, cmap="gray")
ax[0].add_patch(plt.Rectangle((c, r), n, n, fill=False, edgecolor="red", lw=1.5))
ax[0].set_title("image")

ax[1].imshow(patch, cmap="gray", vmin=0, vmax=255)
for (i, j), v in np.ndenumerate(patch):
    ax[1].text(j, i, v, ha="center", va="center", fontsize=10, color="black" if v > 127 else "white")
ax[1].set_title(f"pixel values ({n} x {n} patch)")

# one CSV line per image row, placed at the same height as that row
for i, row in enumerate(patch):
    ax[2].text(0.04, i, ",".join(str(v) for v in row), family="monospace", fontsize=12, va="center")
ax[2].set_title("the same rows in the CSV file")
ax[2].set_xlim(0, 1)
ax[2].set_ylim(n - 0.5, -0.5)

for a in ax:
    a.set_xticks([])
    a.set_yticks([])
for side in ("top", "right", "bottom", "left"):
    ax[2].spines[side].set_color("#cccccc")
ax[0].axis("off")
ax[1].axis("off")

fig.tight_layout()
fig.savefig(out, dpi=110, bbox_inches="tight")
print("wrote", out)
