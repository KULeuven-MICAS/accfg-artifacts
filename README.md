# ACCFG artifacts

## Installation and requirements

We only test these instructions on Linux.

Requirements:
* git
* docker

### Getting the source

This repository relies on submodules.
Therefore, we recommmend cloning as follows:

```sh
git clone --recursive https://github.com/KULeuven-MICAS/accfg-artifacts
```

If you already cloned the repository, but forgot the recursive flag, do:

```sh
git submodule update --init --recursive --remote
```

## SNAX experiments

This repository can run all experiments for SNAX.
Use it with container `ghcr.io/kuleuven-micas/snax:v0.1.6`

From the root of this repository, run:

```sh
docker run -itv $PWD:/repo:z ghcr.io/kuleuven-micas/snax:v0.1.6

# inside the docker container:

pip install -r /repo/snax-mlir/requirements.txt -e /repo/snax-mlir
cd /repo/snax-mlir/kernels/streamer_matmul
python3 genbenchmark.py
```
