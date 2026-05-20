# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

This repo uses [pixi](https://prefix.dev/docs/pixi/overview) for environment management (`pixi.toml`). The environment targets `osx-arm64` and `linux-64`.

```bash
pixi install          # create/update the environment
pixi run jupyter lab  # launch JupyterLab with the pixi kernel
```

## Notebook workflow

Notebooks are paired `.ipynb` / `.py` files via [jupytext](https://jupytext.readthedocs.io/) (configured in `jupytext.toml`). The `py:percent` format is the source of truth for version control; `.ipynb` files are derived.

- When editing notebooks programmatically, ALWAYS prefer the `.py` file (cleaner diffs, no cell output noise).
- Cell delimiters are `# %%` (code) and `# %% [markdown]` (markdown).

## Data & compute context

- Notebooks are designed to run on cloud JupyterHubs in **AWS us-west-2**: NASA VEDA (`hub.openveda.cloud`), CryoCloud (`hub.cryointhecloud.com`), or ASF OpenScience Lab (`opensciencelab.asf.alaska.edu`).
- Data is fetched from NASA/ASF endpoints (requires Earthdata login) and written to `/tmp/` or S3 scratch buckets — nothing is committed to the repo.
- See [JupyterHubs.md](JupyterHubs.md) for hub comparison, SSH/VSCode remote access setup, and IRSA credential wiring for AWS S3 access in SSH sessions.

## Key dependencies

| Package | Purpose |
|---|---|
| `geopandas` / `xvec` | Vector geospatial data |
| `rioxarray` | Raster I/O with xarray |
| `asf_search` | ASF Earthdata search API |
| `gdal` (CLI) | KMZ → GeoJSON conversion via `gdal vector pipeline` |
| `cartopy` / `contextily` | Map visualization |
| `jupytext` | `.py` ↔ `.ipynb` sync |

## Notebook content

- **`observation-plan.py`** — converts the NISAR observation plan KMZ to GeoJSON (via GDAL CLI), then parses the `snippet` field into structured columns (`band`, `mode`, `track`, `frame`, etc.) and saves as geoparquet.
- **`context.ipynb`** — contextual/exploratory notebook (purpose derivable from content).
