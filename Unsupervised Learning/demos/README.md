# Unsupervised Learning Demos

Interactive Plotly demos for PCA, t-SNE, and UMAP. Each script opens its figures in the browser.

```bash
cd "Unsupervised Learning/demos"

# PCA
uv run eigenfaces.py               # PCA on 400 face photos (4096 pixels each)
uv run genes_mirror_geography.py   # PCA on DNA from 938 people worldwide

# t-SNE and UMAP (compared with PCA)
uv run swiss_roll.py               # a rolled-up sheet: PCA can't unroll it, t-SNE/UMAP can
uv run mnist_tsne_umap.py          # 10,000 handwritten digits from 784 dimensions to 2 (~40 s)
```

## Interactive explorers (open in the browser)

These are small [Dash](https://dash.plotly.com) apps: run the script, then open the link it prints.
Press `Ctrl+C` in the terminal to stop them.

```bash
uv run mnist_explorer.py        # http://127.0.0.1:8050  click a point to see its digit
uv run eigenfaces_explorer.py   # http://127.0.0.1:8051  click a face, then slide k to rebuild it
```

The MNIST explorer saves its t-SNE/UMAP results to `data/`, so only the first start takes ~30 s.

Datasets are downloaded on the first run into `data/` (git ignores this folder).
