"""Genes mirror geography: PCA on human DNA recovers a map of the world.

We use the Human Genome Diversity Project (HGDP): 938 people from 53
populations around the world, each measured at about 660,000 positions in the
genome (SNPs). Each person becomes a point in a very high-dimensional space.
PCA never sees where anyone is from, but the first components still line up
with geography.

Inspired by Novembre et al. (2008), "Genes mirror geography within Europe".
Data: Novembre Lab teaching repo (HGDP_PopStruct_Exercise) and HGDP metadata.

Run with:  uv run genes_mirror_geography.py
"""

import gzip
import shutil
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
from bed_reader import open_bed
from sklearn.decomposition import PCA

DATA_DIR = Path(__file__).parent / "data"
GENOTYPES_URL = "https://raw.githubusercontent.com/NovembreLab/HGDP_PopStruct_Exercise/master/data/"
METADATA_URL = "https://ngs.sanger.ac.uk/production/hgdp/hgdp_wgs.20190516/metadata/hgdp_wgs.20190516.metadata.txt"


def download(url, path):
    """Download a file once and reuse it on later runs."""
    if not path.exists():
        print(f"Downloading {path.name} ...")
        urllib.request.urlretrieve(url, path)


# 1. Download the data (about 75 MB, only the first time).
# The genotypes are in PLINK format: .bed (the DNA), .bim (SNP info), .fam (people).
DATA_DIR.mkdir(exist_ok=True)
for name in ["H938.bed.gz", "H938.bim", "H938.fam", "H938.clst.txt"]:
    download(GENOTYPES_URL + name, DATA_DIR / name)
download(METADATA_URL, DATA_DIR / "hgdp_metadata.txt")

if not (DATA_DIR / "H938.bed").exists():
    with gzip.open(DATA_DIR / "H938.bed.gz") as source, open(DATA_DIR / "H938.bed", "wb") as target:
        shutil.copyfileobj(source, target)

# 2. Load the genotypes.
# Each entry is 0, 1, or 2: how many copies of the less common DNA letter a
# person carries at that SNP. To keep things fast, we use every 20th SNP.
bed = open_bed(DATA_DIR / "H938.bed")
X = bed.read(index=np.s_[:, ::20], dtype="float32")

print(f"People: {X.shape[0]}")
print(f"SNPs used (dimensions): {X.shape[1]}  (out of {bed.shape[1]})\n")

# 3. Clean up the data before PCA.
# a) A few genotypes are missing (NaN). Fill them with that SNP's average.
snp_means = np.nanmean(X, axis=0)
X = np.where(np.isnan(X), snp_means, X)

# b) Drop SNPs that are identical for everyone. They carry no information
#    and would cause a divide-by-zero when we standardize.
X = X[:, X.std(axis=0) > 0]

# c) Standardize each SNP so that rare and common SNPs count equally.
X = (X - X.mean(axis=0)) / X.std(axis=0)

# 4. Run PCA and keep the first 3 components.
pca = PCA(n_components=3)
scores = pca.fit_transform(X)

for i, ratio in enumerate(pca.explained_variance_ratio_, start=1):
    print(f"PC{i} explains {ratio:.1%} of the variance")
print("(Small numbers are normal for DNA: most variation is individual noise.)\n")

# 5. Find out where each person is from.
# PCA did not use this information. We only use it now to color the plots.
people = pd.read_csv(DATA_DIR / "H938.clst.txt", sep=" ", names=["family", "id", "population"])
metadata = pd.read_csv(DATA_DIR / "hgdp_metadata.txt", sep="\t")
places = metadata[["sample", "region", "latitude", "longitude"]]

people = people.merge(places, left_on="id", right_on="sample", how="left")

# A few people are missing from the metadata, so we copy the location
# of someone else from the same population.
for column in ["region", "latitude", "longitude"]:
    people[column] = people.groupby("population")[column].transform("first")

people["region"] = people["region"].str.replace("_", " ").str.title()
people["population"] = people["population"].str.replace("_", " ")
people["PC1"] = scores[:, 0]
people["PC2"] = scores[:, 1]
people["PC3"] = scores[:, 2]

# 6. Point the axes like a map.
# The sign of a principal component is arbitrary (flipping it changes nothing).
# We flip the signs so Africa is at the bottom (south) and East Asia is on the
# right (east), which makes the PCA plot easy to compare with a world map.
region_means = people.groupby("region")[["PC1", "PC2"]].mean()
if region_means.loc["Africa", "PC1"] > 0:
    people["PC1"] = -people["PC1"]
if region_means.loc["East Asia", "PC2"] < 0:
    people["PC2"] = -people["PC2"]

# 7. Plot the real map, then the PCA "map". Use the same colors so they are easy to compare.
region_order = ["Africa", "Middle East", "Europe", "Central South Asia", "East Asia", "Oceania", "America"]
colors = dict(zip(region_order, px.colors.qualitative.Bold))

populations = people.groupby(["population", "region"], as_index=False)[["latitude", "longitude"]].first()
fig = px.scatter_geo(
    populations,
    lat="latitude",
    lon="longitude",
    color="region",
    hover_name="population",
    color_discrete_map=colors,
    category_orders={"region": region_order},
    projection="natural earth",
    title="Where the 53 HGDP populations live",
)
fig.update_traces(marker_size=9)
fig.show()

fig = px.scatter(
    people,
    x="PC2",
    y="PC1",
    color="region",
    hover_name="population",
    color_discrete_map=colors,
    category_orders={"region": region_order},
    title="PCA of DNA alone: 938 people, colored by where they are from",
)
fig.update_traces(marker_size=6, marker_opacity=0.8)
fig.show()

# 8. Add a third component to see more structure.
# PC3 separates Native American populations from East Asians.
fig = px.scatter_3d(
    people,
    x="PC2",
    y="PC1",
    z="PC3",
    color="region",
    hover_name="population",
    color_discrete_map=colors,
    category_orders={"region": region_order},
    title="The first three principal components of human DNA",
)
fig.update_traces(marker_size=3)
fig.show()
