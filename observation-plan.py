# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: default
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Convert observation plan from KMZ to alternative formats
#
#
# https://science.nasa.gov/mission/nisar/data/

# %%
# !wget -nc -P /tmp/ https://assets.science.nasa.gov/content/dam/science/missions/nisar/kmz/NISAR_Feb2026_ReseasedData-20260305.kmz

# %%
path = "/tmp/NISAR_Feb2026_ReseasedData-20260305.kmz"
# !gdal vector info {path}

# %%
layer = "Descending"
output = "/tmp/NISAR_Feb2026_ReseasedData-20260305-descending.geojson"
# !gdal vector info {path} --layer {layer} --features --limit 1

# %% magic_args="-s {path} {layer} {output}" language="bash"
# # _ogr_geometry_ explicitly. That's the special name used when the source has no named geometry column, which is the case with KMZ
# gdal vector pipeline \
#   ! read $1 --layer $2 \
#   ! select --fields "_ogr_geometry_,Name,snippet" \
#   ! set-geom-type --geometry-type Polygon \
#   ! write --overwrite $3

# %%
# !gdal vector info {output} --features --limit 1

# %%
# !head {output}

# %%
# !ls -ltrh {output}

# %%
layer = "Ascending"
output = "/tmp/NISAR_Feb2026_ReseasedData-20260305-ascending.geojson"


# %% magic_args="-s {path} {layer} {output}" language="bash"
# # _ogr_geometry_ explicitly. That's the special name used when the source has no named geometry column, which is the case with KMZ
# gdal vector pipeline \
#   ! read $1 --layer $2 \
#   ! select --fields "_ogr_geometry_,Name,snippet" \
#   ! set-geom-type --geometry-type Polygon \
#   ! write --overwrite $3

# %%
# !ls -ltrh {output}

# %% [markdown]
# ## Reformat as geoparquet
#
# Explode the attributes as separate columns for filtering more easily

# %%
import geopandas as gpd
import pandas as pd

gfd = gpd.GeoDataFrame.from_file("/tmp/NISAR_Feb2026_ReseasedData-20260305-descending.geojson")
gfa = gpd.GeoDataFrame.from_file("/tmp/NISAR_Feb2026_ReseasedData-20260305-ascending.geojson")
gf = pd.concat([gfd, gfa], ignore_index=True)
gf.head(3)

# %% [markdown]
# ### L-band Mnemonic Scheme
#
# The mnemonic scheme for L-band radar modes is the following:
#
# **L:CCC:MM:BB<sub>_l_</sub>P<sub>_l_</sub>+BB<sub>_u_</sub>P<sub>_u_</sub>:WW:DD:FFF**
#
# | **Attribute**&emsp; | **Meaning**                                                                                                                                                |
# |---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
# | L                   | L-band                                                                                                                                                     |
# | CCC                 | Mode category (ENG = engineering mode, SCI = science mode, PST = post-take, PRE = pre-take)                                                                |
# | MM                  | Mode name (QP = quad pol; DH = dual pol HH/HV; SH = single pol HH; QD = HH in lower band, VV in upper band; QQ = HH/HV in lower band, VV/VH in upper band) |
# | BB<sub>_l_</sub>    | Bandwidth of lower band                                                                                                                                    |
# | P<sub>_l_</sub>     | Pulse width of lower band (W = wide, M = medium, N = narrow)                                                                                               |
# | BB<sub>_u_</sub>    | Bandwidth of upper band                                                                                                                                    |
# | P<sub>_u_</sub>     | Pulse width of upper band                                                                                                                                  |
# | WW                  | Swath width (FS = full swath 240 km, HS = half swath)                                                                                                      |
# | DD                  | Bit depth (B4 = 4 bit quantization, B3 = 3 bit quantization)                                                                                               |
# | FFF                 | Pulse repetition frequency scheme (e.g. F28 is fixed PRF scheme, D01 is a variable PRF scheme)                                                             |
#
# ### S-band Mnemonic Scheme
#
# The S-band mnemonic scheme is similar to L-band: 
#
# **S:XX:MM:BBP:WW:DD:FFF**
#
# | **Attribute**&emsp; | **Meaning**                                                                                                                                                |
# |---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
# | S                   | S-band                                                                                                                                                     |
# | XX                  | Beam-forming mode (DB = beamform; DR = raw channels of the beamformer; NR = no beamforming)                                                                |
# | MM                  | Mode name (QP = quad pol; DH = dual pol HH/HV; SH = single pol HH; QD = HH in lower band, VV in upper band; QQ = HH/HV in lower band, VV/VH in upper band) |
# | BB                  | Bandwidth                                                                                                                                                  |
# | P                   | Pulse width  (W = wide, M = medium, N = narrow)                                                                                                            |
# | WW                  | Swath width. **S-band acquisitions are always full swath, so this term is left off the mnemonic.**                                                         |
# | DD                  | Bit depth (B4 = 4 bit quantization, B3 = 3 bit quantization)                                                                                               |
# | FFF                 | Pulse repetition frequency scheme. **For joint modes, the PRF scheme is left off the mnemonic because it is the same as the L-band PRF.**        

# %%
import re

def snippet2cols(snippet):
    mnemonic_str = snippet.split("|")[-1].strip()
    # there may be an S-band token after L-band; grab only L:...
    l_mnemonic = next((t for t in mnemonic_str.split() if t.startswith("L:")), None)
    if l_mnemonic is None:
        return {k: None for k in ("band", "mode_cat", "mode", "bw_l", "pulse_l", "bw_u", "pulse_u", "swath", "bit_depth", "prf")}

    band, mode_cat, mode, bw_pulse, swath, bit_depth, prf = l_mnemonic.split(":")

    if "+" in bw_pulse:
        lower, upper = bw_pulse.split("+")
        bw_l, pulse_l = re.match(r"(\d+)([WMN])", lower).groups()
        upper_match = re.match(r"(\d+)([WMN])", upper)
        bw_u, pulse_u = upper_match.groups() if upper_match else (None, None)
    else:
        bw_l, pulse_l = re.match(r"(\d+)([WMN])", bw_pulse).groups()
        bw_u, pulse_u = None, None

    return {
        "band": band,
        "mode_cat": mode_cat,
        "mode": mode,
        "bw_l": int(bw_l),
        "pulse_l": pulse_l,
        "bw_u": int(bw_u) if bw_u else None,
        "pulse_u": pulse_u,
        "swath": swath,
        "bit_depth": bit_depth,
        "prf": prf,
    }


# %%
gf[["band","mode_cat","mode","bw_l","pulse_l","bw_u","pulse_u","swath","bit_depth","prf"]] = gf["snippet"].apply(snippet2cols).apply(pd.Series)

# %%
gf = gf.drop(columns=["snippet"]).rename(columns={"Name": "name"})
gf[["track", "frame"]] = gf["name"].str.extract(r"T(\d+)_F(\d+)").astype(int)
gf.head()

# %%
output_parquet = "/tmp/nisar_observation_plan.parquet"
gf.to_parquet(output_parquet, index=False)

# %%
# !ls -ltrh /tmp/nisar*

# %%
# !gdal vector info {output_parquet}

# %%
