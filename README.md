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

`cd` into `accfg-artifacts` and then:

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

## Gemmini Experiments

This repository can run all experiments for Gemmini

`cd` into `accfg-artifacts` and then:

```sh
docker run -itv $PWD:/repo:z ghcr.io/kuleuven-micas/gemmini-test:latest
# Prepare folder structure and object files by building all tests
cd gemmini-rocc-tests && ./build.sh
# Run and build all tiled matmul tests (GCC)
cd gemmini-rocc-tests/build && make test-baremetal-bareMetalC
# name: build tiled matmul tests (MLIR and MLIR optimized)
cd gemmini-rocc-tests/bareMetalMLIR && make all_binaries all_binaries_no_opt
# Install postprocessing requirements
pip install -e . --break-system-packages
# Run postprocessing and number gathering
cd accfg_artifacts && python3 gemmini_get_all_numbers.py ../gemmini-rocc-tests -o results.pkl
```
