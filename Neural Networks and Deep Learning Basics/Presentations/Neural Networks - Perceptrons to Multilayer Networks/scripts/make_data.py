"""Build data/digits.json for the digit-recognition slide.

Source: the 1,797 UCI optdigits images (8x8, pixel values 0-16), as already exported for the
Dimensionality Reduction deck. Each image is 64 base-17 characters ('0'-'9', 'a'-'g').
We keep the image strings and labels, and fix a seeded 1,500 / 297 train/test split.
"""
import json
import random
from pathlib import Path

here = Path(__file__).resolve().parent.parent
src = here.parents[2] / "Unsupervised Learning/Presentations/Dimensionality Reduction - PCA, t-SNE, UMAP/data/digits.json"
d = json.loads(src.read_text())
idx = list(range(len(d["y"])))
random.Random(7).shuffle(idx)
train, test = idx[:1500], idx[1500:]
out = {
    "train": {"img": [d["img"][i] for i in train], "y": [d["y"][i] for i in train]},
    "test": {"img": [d["img"][i] for i in test], "y": [d["y"][i] for i in test]},
}
(here / "data/digits.json").write_text(json.dumps(out, separators=(",", ":")))
print("train", len(train), "test", len(test))
