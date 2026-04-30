# AWS us-west-2 JupyterHubs

NASA VEDA, ASF OpenScienceLab and CryoCloud are all JupyterHubs in AWS us-west-2. Below is a quick comparison of their specs.

Further below are instructions for connecting programmatically via terminal + vscode remote ssh to both CryoCloud and NASA VEDA, including how to specify custom images and resource options.


## Summary Comparison

| Feature | OpenScience Lab | CryoCloud | NASA VEDA |
|---|---|---|---|
| **URL** | opensciencelab.asf.alaska.edu | hub.cryointhecloud.com | hub.openveda.cloud |
| **AWS Region** | us-west-2 | us-west-2 | us-west-2 |
| **MFA Required** | ✅ | ❌ | ❌ |
| **Max RAM** | 16 GB | 120 GB | 120 GB |
| **Max CPU** | 4 | 15 | 15 |
| **GPU** | ❌ | ✅ NVIDIA Tesla T4 (16 GB) | ❌ |
| **Home Storage** | 500 GB EBS | 10 GB NFS | 10 GB NFS |
| **Scratch Storage** | — | 50 GB | 50 GB |
| **S3 Scratch Bucket** | ❌ | ✅ (not persistent) | ✅ (not persistent) |
| **Storage Expiry** | Deleted after 30 days inactivity | — | — |
| **SSH / VSCode Remote** | ❌ | ✅  | ✅ |

### OpenScience Lab

https://opensciencelab.asf.alaska.edu

- requires MFA
- 2 compute options:
    - m6a.large RAM Guarantee: 5G. RAM limit: 8G. CPU limit: 2.
    - m6a.xlarge RAM Guarantee: 10G. RAM limit: 16G. CPU limit: 4. Storage: 500G.
- EBS Storage: 500G
    - user storage is permanently deleted after 30 days of inactivity!
- No SSH / remote VSCode

### CryoCloud

https://hub.cryointhecloud.com

- S3 scratch bucket for data storage (no persistent s3 storage)
- Wide variety of compute options:
    - ~2 GB RAM & 4 CPU up to 120 GB RAM & 15 CPU.
    - NVIDIA Tesla T4 GPU with 16 GB, 4 CPU
- NFS (slow) Home directory quota of 10 GB
- 50 GB scratch space
- SSH / VSCode (not currently functional)

### NASA VEDA

- S3 scratch bucket for data storage (no persistent s3 storage)
- Same CPU options as CryoCloud (both run by 2i2c), but no GPU option
- NFS (slow) Home directory quota of 10 GB
- 50 GB scratch space
- SSH / VSCode remote access

## Connecting programmatically via terminal + vscode remote ssh


**First follow these docs!** https://docs.openveda.cloud/user-guide/scientific-computing/ssh.html

**NOTE: unfortunately the default cryocloud image doesn't work with ssh currently, so you need to specify a custom image**

```bash
export JHUB_URL=https://hub.cryointhecloud.com
export JHUB_TOKEN=XXXXXXXXX
export JHUB_USER=scottyhq
#export JHUB_IMAGE=quay.io/pangeo/base-notebook:2026.04.29
# Older / specific cryocloud image
#export JHUB_IMAGE=quay.io/cryointhecloud/cryo-hub-image:d624b28e39c4
# VEDA images:
export JHUB_IMAGE=public.ecr.aws/nasa-veda/pangeo-notebook-veda-image:2025.12.30-v1
# The other resource options available are mem_2_gb, mem_4_gb, mem_7_gb, mem_29_gb, mem_60_gb, and mem_119_gb
export JHUB_VM=mem_4_gb
```

```bash
# Launch with default image and resources
curl -X POST \
  $JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"cpu-only","image":"01-python","resource_allocation":"%s"}' $JHUB_VM)"

# Launch with custom image and resources:
curl -X POST \
  $JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"cpu-only","image":"unlisted_choice","image--unlisted-choice":"%s","resource_allocation":"%s"}' $JHUB_IMAGE $JHUB_VM)"

# GPU instance
curl -X POST \
  $JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"gpu","image":"pytorch"}')"

# Check launch status
curl -s \
  $JHUB_URL/hub/api/users/$JHUB_USER \
  -H "Authorization: token $JHUB_TOKEN" | jq

# Connect via vscode remote ssh
code --remote ssh-remote+hub.cryointhecloud.com /home/jovyan
```

### Connecting to NASA VEDA via terminal + vscode

The other resource options available are mem_2_gb, mem_4_gb, mem_7_gb, mem_29_gb, mem_60_gb, and mem_119_gb

```bash
# setup
export JHUB_URL=https://hub.openveda.cloud
export JHUB_TOKEN=XXXXXX
export JHUB_USER=scottyhq
#export JHUB_IMAGE=01-modify-pangeo # built-in 'named images'
export JHUB_IMAGE=quay.io/pangeo/base-notebook:2026.04.29
export JHUB_VM=mem_15_gb

# launch server w/ custom image (NOTE: form changes a bit with image--unlisted-choice)
curl -X POST \
  $JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"choose-your-environment-and-resources","image":"unlisted_choice","image--unlisted-choice":"%s","resource_allocation":"%s"}' "$JHUB_IMAGE" "$JHUB_VM")"

# Check server status
curl -s \
  $JHUB_URL/hub/api/users/$JHUB_USER \
  -H "Authorization: token $JHUB_TOKEN" | jq


# Launch local vscode with remote ssh connection to VEDA
code --remote ssh-remote+hub.openveda.cloud /home/jovyan


# Stop server
curl -X DELETE \
  $JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN"
```
