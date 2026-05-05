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
| **Home Storage Expiry** | Deleted after 30 days inactivity | — | — |
| **Scratch Storage** | — | /tmp/ (50 GB) | /tmp/ (50 GB) |
| **S3 Scratch Bucket** | ❌ | ✅ s3://nasa-cryo-scratch/ (7 days) | ✅ s3://nasa-veda-scratch (7 days) |
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

### EarthScope Geolab

https://www.earthscope.org/data/geolab/

- 50GB of available storage in their home directory
- home directory (jovyan) will be deleted after 6 months of inactivity
- in AWS us-east-2 (location of S3 buckets with seismic & GPS data)

## Connecting programmatically via terminal + vscode remote ssh

**First follow these docs!** https://docs.openveda.cloud/user-guide/scientific-computing/ssh.html

**NOTE:** unfortunately the default CryoCloud image doesn't work with ssh currently, so you need to specify a custom image** The docker image must have a working version of `jupyter-sshd-proxy` installed.

## CryoCloud

### Set up environment variables
```bash
export JHUB_URL=hub.cryointhecloud.com
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

### Launch default env
```bash
# Launch with default image and resources
curl -X POST \
  https://$JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"cpu-only","image":"01-python","resource_allocation":"%s"}' $JHUB_VM)"
```

### Launch with custom image and resources:
```bash
curl -X POST \
  https://$JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"cpu-only","image":"unlisted_choice","image--unlisted-choice":"%s","resource_allocation":"%s"}' $JHUB_IMAGE $JHUB_VM)"
```

### GPU instance
```bash
curl -X POST \
  https://$JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"gpu","image":"pytorch"}')"
```

### Check launch status
```bash
curl -s \
  https://$JHUB_URL/hub/api/users/$JHUB_USER \
  -H "Authorization: token $JHUB_TOKEN" | jq

```

### Connect via vscode remote ssh
```
code --remote ssh-remote+$JHUB_USER /home/jovyan
```

## NASA VEDA Hub

NOTE: fancy jhub profile forms differ, so curl commands differ from above

The other resource options available are mem_2_gb, mem_4_gb, mem_7_gb, mem_29_gb, mem_60_gb, and mem_119_gb

### Launch default env
```bash
# setup
export JHUB_URL=hub.openveda.cloud
export JHUB_TOKEN=XXXXXX
export JHUB_USER=scottyhq
#export JHUB_IMAGE=01-modify-pangeo # built-in 'named images'
#export JHUB_IMAGE=quay.io/pangeo/base-notebook:2026.04.29
export JHUB_VM=mem_29_gb
```

### Launch with default image
```bash
curl -X POST \
  https://$JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"choose-your-environment-and-resources","image":"01-modify-pangeo","resource_allocation":"%s"}' $JHUB_VM)"
```

### Launch server w/ custom image 

(NOTE: form changes a bit from CryoCloud so curl commands are different

```bash
curl -X POST \
  https://$JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(printf '{"profile":"choose-your-environment-and-resources","image":"unlisted_choice","image--unlisted-choice":"%s","resource_allocation":"%s"}' "$JHUB_IMAGE" "$JHUB_VM")"
```

### Check server status
```bash
curl -s \
  https://$JHUB_URL/hub/api/users/$JHUB_USER \
  -H "Authorization: token $JHUB_TOKEN" | jq
```

### Launch local vscode with remote ssh connection to VEDA
```bash
code --remote ssh-remote+$JHUB_URL /home/jovyan
```

### Stop server
```bash
curl -X DELETE \
  $JHUB_URL/hub/api/users/$JHUB_USER/servers/ \
  -H "Authorization: token $JHUB_TOKEN"
```


## Pixi environments

The following pixi config will install packages to `/tmp` in order to not bloat your limited home directory. `/tmp` is also a faster disk than the NFS-mounted home directory, so performance should be faster:

`~/.pixi/config.toml`:
```
detached-environments = "/tmp/pixi"
```

**NOTE:**: it seems for the pixi kernel to be detected for jupyter notebooks you must select `File -> Open Folder` and choose your repo folder. Then the automatic kernel detection finds the environments in `.pixi/envs`. If you start ing `/home/jovyan` and navigate to a notebook in a subfolder it is not found... Possible solutions here https://github.com/renan-r-santos/pixi-code


## ~/.bashrc and credentials

After a bit of troubleshooting with Claude we came up with this ~/.bashrc to get the same AWS credentials in a SSH terminal as you do in JupyterLab browser environment (granting you access to S3 buckets):

```bash
# Colors and prompt customization
# https://unix.stackexchange.com/questions/148/colorizing-your-terminal-and-shell-environment
PS1='\e[34;1m\u@\h: \e[36m\W\e[0m\$ '

#export LS_COLORS='rs=0:di=01;34:ln=01;36:mh=00:pi=40;33'
LS_COLORS=$LS_COLORS:'di=1;35:' ; export LS_COLORS
export LS_OPTIONS='--color=auto'
alias ls='ls $LS_OPTIONS'

# Put pixi executable in the path
export PATH="/home/jovyan/.pixi/bin:$PATH"

# === VEDA JupyterHub IRSA credentials (injected at pod start, not in SSH sessions) ===
# Read AWS_ROLE_ARN and AWS_WEB_IDENTITY_TOKEN_FILE from PID 1's environment
# so botocore can call sts:AssumeRoleWithWebIdentity and get the nasa-veda-prod role.
_read_proc1_var() { cat /proc/1/environ 2>/dev/null | tr '\0' '\n' | grep "^$1=" | cut -d= -f2-; }
export AWS_ROLE_ARN="$(_read_proc1_var AWS_ROLE_ARN)"
export AWS_WEB_IDENTITY_TOKEN_FILE="$(_read_proc1_var AWS_WEB_IDENTITY_TOKEN_FILE)"
export AWS_DEFAULT_REGION="$(_read_proc1_var AWS_DEFAULT_REGION)"
export AWS_REGION="$(_read_proc1_var AWS_REGION)"
export AWS_STS_REGIONAL_ENDPOINTS="$(_read_proc1_var AWS_STS_REGIONAL_ENDPOINTS)"
unset -f _read_proc1_var
# === end VEDA IRSA ===


# Earthdata Login Token (expires 2026-06-03T18:23:02Z)
export EARTHDATA_TOKEN="XXXXXXXX"
```


## Jupyter Kernels

Jupyter Notebook kernels do not have access to ~/.bashrc environment variables apparently, so you can create a startup script that sources ~/.bashrc any time you launch a kernel:

`~/.ipython/profile_default/startup/00-env.py`:
```python
"""
Load environment variables from ~/.bashrc into every Jupyter kernel at startup.

~/.bashrc is only sourced for interactive bash shells, not by the Jupyter kernel
process (which is spawned directly by JupyterHub without going through a shell).
This startup script bridges that gap.

On VEDA JupyterHub the IRSA vars (AWS_ROLE_ARN, AWS_WEB_IDENTITY_TOKEN_FILE) are
set in PID 1's environment and picked up by the ~/.bashrc snippet we added.
By sourcing ~/.bashrc here, botocore can then use AssumeRoleWithWebIdentity to
get the nasa-veda-prod role credentials automatically.

To add a secret, just `export MY_VAR=value` in ~/.bashrc as normal.
"""
import os
import subprocess

result = subprocess.run(
    ["bash", "-i", "-c", "export -p"],
    capture_output=True,
    text=True,
)

for line in result.stdout.splitlines():
    # Lines look like: declare -x KEY="value"  or  export KEY="value"
    if not (line.startswith("declare -x ") or line.startswith("export ")):
        continue
    line = line.removeprefix("declare -x ").removeprefix("export ")
    if "=" not in line:
        continue
    key, _, val = line.partition("=")
    key = key.strip()
    # Strip surrounding quotes added by `export -p`
    val = val.strip()
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    # Don't override vars already set in the environment (e.g. K8s-injected vars)
    if key and val and key not in os.environ:
        os.environ[key] = val
```
