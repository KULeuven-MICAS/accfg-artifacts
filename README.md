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

If you already cloned the repository, but forgot the `--recursive` flag, do:

```sh
git submodule update --init --recursive --remote
```

## SNAX experiments

This repository can run all experiments for SNAX.

We increased the L1 memory size for our experiments, so build the container as follows

From the root of this repository, run:

```sh
docker build . -f containers/snax.Containerfile -t ghcr.io/kuleuven-micas/accfg-experiments:latest
```

This build can take up to 5 minutes, depending on the amount of parallel make jobs you can run.
Next, `cd` into `snax-mlir` and then:

```sh 
docker run -itv $PWD:/repo:z ghcr.io/kuleuven-micas/accfg-experiments:latest
# inside the repository
pip install -r /repo/snax-mlir/requirements.txt -e /repo/snax-mlir
cd /repo/snax-mlir/kernels/streamer_matmul
python3 genbenchmark.py
```
