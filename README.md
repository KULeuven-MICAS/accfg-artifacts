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

`cd` into `snax-mlir` and then:

```sh 
docker run -itv $PWD:/repo:z ghcr.io/kuleuven-micas/snax:v0.1.6
# inside the repository
pip install -e . -e /repo/snax-mlir
cd /repo/snax-mlir/kernels/streamer_matmul
python3 genbenchmark.py
cd /repo/accfg-artifacts
# Perform post processing on the numbers themselves
python3 get_all_numbers.py -i /repo/snax-mlir/kernels/streamer_matmul/results -o results.pkl
# Plot the figures
python3 plot_snax.py -i /repo/accfg_artifacts/results.pkl --plot=bar_plot -o bar_plot.png
python3 plot_snax.py -i /repo/accfg_artifacts/results.pkl --plot=roofline -o roofline.png
```
