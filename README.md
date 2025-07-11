# Artifacts Evaluation for - The Configuration Wall: Characterization and Elimination of Accelerator Configuration Overhead Automatic  

## Installation and requirements

**Software Requirements:**
* linux (to run docker) or other linux-like environments (WSL), but these are untested.
* git (to obtain the source code for the experiments)
* docker (to run the experiments)

**Hardware Requirements:**

These experiments should run on any typical x86 computer.
As all hardware testing is done in simulation, no special hardware is required.
Some parts of those simulations/postprocessing are rather compute-intensive, and will run faster on a faster machine.
All software needs to be pulled from ghcr.io and pypi, machines with faster internet connection will finish this faster.
These requirements should be plenty:

* 4-core x86 CPU
* 8 GB RAM
* A working internet connection (to download the docker container, this repository, and additional python packages)
* 16 GB of free disk space

All time estimations are based on such typical machines.

### Getting the source (~ <1 minute)

To run the experiments in this repository, please clone the repository

This repository relies on submodules.
Therefore, we recommmend cloning as follows:

```sh
git clone --recursive https://github.com/KULeuven-MICAS/accfg-artifacts
```

If you already cloned the repository, but forgot the `--recursive` flag, do:

```sh
git submodule update --init --recursive --remote
```

## (RECOMMENDED) Running all experiments at once (~ 2 hours):

After cloning the repository with all submodules, `cd` into it, and run the `./run-all.sh` script. This will spawn the docker container automatically and run itself within it. 
You can alternatively start the docker container manually using: `docker run --rm -itv $PWD:/repo:z ghcr.io/kuleuven-micas/accfg-artifacts:latest /repo/run-all.sh`
The docker image itself is about ~9 GB.

**Note on time:** On modern Desktop CPUs we saw times at around ~30 minutes, but lower-power CPUs seem to struggle a lot with these simulation workloads.

## Or, run individual experiments:

### OpenGeMM experiments (~20 minutes)

This repository can run all experiments for OpenGeMM.

`cd` into `accfg-artifacts` and then:
```sh 
docker run --rm -itv $PWD:/repo:z ghcr.io/kuleuven-micas/accfg-artifacts:latest 
```
**Explanation:** Get (if not downloaded yet) the docker image and start the docker container.
Mount the repository in the docker container. All experiments need to be run inside the docker container.
The docker contains all required simulators, compilers to compile the binaries to run on the container.

_~5 minutes if need to download or ~5 seconds if downloaded already._

```sh
# inside the repository
pip install /repo -e /repo/snax-mlir
```
**Explanation:** Install the experiments package and prerequisites to gather and plot experiment results.

_~ 1 minute_

```sh
cd /repo/snax-mlir/kernels/streamer_matmul
python3 genbenchmark.py
```
**Explanation:** Compile all binaries for the OpenGEMM system, and run them in a pre-compiled verilator simulation-binary.

_~ 15 minutes_

```sh
cd /repo/accfg-artifacts
# Perform post processing on the numbers themselves
python3 get_all_numbers.py -i /repo/snax-mlir/kernels/streamer_matmul/results -o results.pkl
```
**Explanation:** Gather performance data of all results and dump in a small pickle file (contains a pandas DataFrame)

_~ <1 minute_

```sh
# Plot the figures
python3 plot_snax.py -i /repo/accfg_artifacts/results.pkl --plot=bar_plot -o bar_plot.png
python3 plot_snax.py -i /repo/accfg_artifacts/results.pkl --plot=roofline -o roofline.png
```

**Explanation:** From the results in the pickle file, make bar chart and roofline plot.

_~ <1 minute_

### Gemmini Experiments (~ 1h 30 minutes)

This repository can run all experiments for Gemmini

`cd` into `accfg-artifacts` and then:

```sh
docker run --rm -itv $PWD:/repo:z ghcr.io/kuleuven-micas/accfg-artifacts:latest
```

**Explanation:** Get (if not downloaded yet) the docker image and start the docker container.
Mount the repository in the docker container. All experiments need to be run inside the docker container.
The docker contains all required simulators, compilers to compile the binaries to run on the container.

_~5 minutes if need to download or ~5 seconds if downloaded already._

```sh
# Prepare folder structure and object files by building all tests
cd /repo/gemmini-rocc-tests && ./build.sh
# name: build tiled matmul tests (MLIR and MLIR optimized)
cd /repo/gemmini-rocc-tests/bareMetalMLIR && make all_binaries_opt all_binaries_no_opt
```

**Explanation:** Build all binaries for simulation. This includes C binaries, non-optimized MLIR and optimized MLIR binaries.

_~ <2 minutes_ 

```
# Install postprocessing requirements
cd /repo && pip install . --break-system-packages
# Run postprocessing and number gathering
python3 accfg_artifacts/gemmini_get_all_numbers.py gemmini-rocc-tests -o /repo/artifacts/gemmini_results.pkl
```

**Explanation:** Run all binaries in spike instruction accurate simulator (--> `mcycle` == `minstret` --> cycle counts match instruction counts in this simulation).
The `gemmini_get_all_numbers` script runs all spike simulations, watches the stdout for cycles/instruction printing, and dumps all instructions executed to count the amount of special RoCC instructions are executed.
All this information is stored in the pickle file.

_~ 1h 30 minutes_

```
python3 plot_gemmini.py -i /repo/accfg_artifacts/gemmini_results.pkl -o gemmini_barplot.png
```

**Explanation:** From the results in the pickle file, make plots.

_~ <1 minute_

