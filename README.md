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


**Note on time:** On modern Desktop CPUs we saw times at around ~30 minutes to complete the entire evaluation, but 
lower-power CPUs seem to struggle a lot with these simulation workloads.

All time estimations are based on typical student machines, where there is access to a fast workstation, times can
be expected to be significantly lower.

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

*~5 minutes if need to download or ~5 seconds if downloaded already.*

```sh
# inside the repository
pip install /repo -e /repo/snax-mlir
```
**Explanation:** Install the experiments package and prerequisites to gather and plot experiment results.

*~ 1 minute.*

```sh
cd /repo/snax-mlir/kernels/streamer_matmul
python3 genbenchmark.py
```
**Explanation:** Compile all binaries for the OpenGEMM system, and run them in a pre-compiled verilator simulation-binary.

*~ 15 minutes.*

```sh
cd /repo/accfg-artifacts
# Perform post processing on the numbers themselves
python3 get_all_numbers.py -i /repo/snax-mlir/kernels/streamer_matmul/results -o /repo/artifacts/gemmini_results.pkl
```
**Explanation:** Gather performance data of all results and dump in a small pickle file (contains a pandas DataFrame)

*~ <1 minute.*

```sh
# Plot the figures
python3 plot_snax.py -i /repo/artifacts/gemmini_results.pkl --plot=bar_plot -o /repo/artifacts/fig_11_bar_plot.png
python3 plot_snax.py -i /repo/artifacts/gemmini_results.pkl --plot=roofline -o /repo/artifacts/fig_12_roofline.png
```

**Explanation:** From the results in the pickle file, make bar chart and roofline plot.

*~ <1 minute.*

### Gemmini Experiments (~ 1h 30 minutes)

This repository can run all experiments for Gemmini

`cd` into `accfg-artifacts` and then:

```sh
docker run --rm -itv $PWD:/repo:z ghcr.io/kuleuven-micas/accfg-artifacts:latest
```

**Explanation:** Get (if not downloaded yet) the docker image and start the docker container.
Mount the repository in the docker container. All experiments need to be run inside the docker container.
The docker contains all required simulators, compilers to compile the binaries to run on the container.

*~5 minutes if need to download or ~5 seconds if downloaded already.*

```sh
# Prepare folder structure and object files by building all tests
cd /repo/gemmini-rocc-tests && ./build.sh
# name: build tiled matmul tests (MLIR and MLIR optimized)
cd /repo/gemmini-rocc-tests/bareMetalMLIR && make all_binaries_opt all_binaries_no_opt
```

**Explanation:** Build all binaries for simulation. This includes C binaries, non-optimized MLIR and optimized MLIR binaries.

*~ <2 minutes.*

```
# Install postprocessing requirements
cd /repo && pip install . --break-system-packages
# Run postprocessing and number gathering
python3 accfg_artifacts/gemmini_get_all_numbers.py gemmini-rocc-tests -o /repo/artifacts/gemmini_results.pkl
```

**Explanation:** Run all binaries in spike instruction accurate simulator (--> `mcycle` == `minstret` --> cycle counts match instruction counts in this simulation).
The `gemmini_get_all_numbers` script runs all spike simulations, watches the stdout for cycles/instruction printing, and dumps all instructions executed to count the amount of special RoCC instructions are executed.
All this information is stored in the pickle file.

*~ 1h 30 minutes.*

```
python3 plot_gemmini.py -i /repo/artifacts/gemmini_results.pkl -o /repo/artifacts/fig_10_bar_plot.png
```

**Explanation:** From the results in the pickle file, make plots.

*~ <1 minute.*

## Understanding the Results:

The `artifacts` folder in the repository should contain two pickled pandas DataFrames, and three figures (10, 11 ad 12).

The figures should be identical (excpet for minor formatting changes) to the ones reported in the paper.

The DataFrames are printed during benchmarking, and their contents are epxlained below. Looking into the plotting scripts
inside the `accfg_artifacts` folder will provide helpful snippets for digging into the data if one is inclided to do so themselves.

### OpenGEMM:

For OpenGEMM, the following table will be printed out:

```
    size              option   csrw  ...  p_attain_conc  p_attain_opt      p_meas
4     16         Base (MLIR)     40  ...      78.019048     72.495575   48.473373
8     32         Base (MLIR)    160  ...     156.038095    135.404959  107.789474
0     64         Base (MLIR)    640  ...     312.076190    239.182482  199.804878
20   128         Base (MLIR)   2560  ...     624.152381    387.786982  338.796769
12   256         Base (MLIR)  12288  ...    1024.000000    531.732252  510.784144
16   512         Base (MLIR)  49152  ...    1024.000000    699.983979  682.194771
5     16        Deduplicated     19  ...     167.397190    143.877058   97.523810
9     32        Deduplicated     55  ...     469.161521    321.747775  261.099602
1     64        Deduplicated    199  ...    1024.000000    516.698984  461.521127
21   128        Deduplicated    775  ...    1024.000000    693.194616  619.817349
13   256        Deduplicated   3081  ...    1024.000000    827.808266  777.028738
17   512        Deduplicated  12297  ...    1024.000000    915.717975  884.763433
6     16          Overlapped     60  ...      53.065587     53.065587   36.408889
10    32          Overlapped    200  ...     126.334458    126.334458   97.669151
2     64          Overlapped    720  ...     279.247936    279.247936  222.911565
22   128          Overlapped   2720  ...     589.501616    589.501616  479.842581
14   256          Overlapped  12672  ...    1024.000000   1024.000000  818.600439
18   512          Overlapped  49920  ...    1024.000000   1024.000000  916.546728
7     16  With Optimizations     25  ...     134.432821    134.432821   90.021978
11    32  With Optimizations     67  ...     400.372661    400.372661  292.571429
3     64  With Optimizations    223  ...     952.060833    952.060833  541.619835
23   128  With Optimizations    823  ...    1024.000000   1024.000000  694.881378
15   256  With Optimizations   3177  ...    1024.000000   1024.000000  834.770425
19   512  With Optimizations  12489  ...    1024.000000   1024.000000  921.502276
```

Here we measure the `csrw` instructions which write configuration to OpenGemm, together with cycle counts for the kernel (not shown in this print, but can be found inside the DataFrame when inspecting).

### Gemmini:

For Gemmini, the following table will be printed out:

```
               option  size  rocc  cycles        ops  bw_conf_eff           Ioc  p_attain_seq
0          C baseline    32    12     117      65536     0.547009    341.333333           137
1                MLIR    32    12      79      65536     0.810127    341.333333           180
2   MLIR deduplicated    32    12      85      65536     0.752941    341.333333           171
3          C baseline    64    12     120     524288     0.533333   2730.666667           379
4                MLIR    64    12      83     524288     0.771084   2730.666667           412
5   MLIR deduplicated    64    12      89     524288     0.719101   2730.666667           406
6          C baseline   128    30     607    4194304     0.263591   8738.133333           419
7                MLIR   128    30     171    4194304     0.935673   8738.133333           482
8   MLIR deduplicated   128    26     167    4194304     0.830339  10082.461538           482
9          C baseline   256    78    1373   33554432     0.302986  26886.564103           482
10               MLIR   256    78     283   33554432     1.469965  26886.564103           505
11  MLIR deduplicated   256    58     259   33554432     1.194337  36157.793103           506
12         C baseline   512   258    4159  268435456     0.330849  65027.968992           500
13               MLIR   512   258    1110  268435456     1.239640  65027.968992           509
14  MLIR deduplicated   512   178     482  268435456     1.969571  94254.022472           511
```

The columns have the following meaning:

- **size:** Square Matrix Size (32 means 32x32x32)
- **rocc:** Number of ROCC configuration instructions used
- **cycles:** Number of *instructions* used to configure the accelerator (note that spike simplifies cycles=instructions). We approximate the number of cycles by multiplying with 3. See paper footnote 3 (line 659) for more information.
- **ops:** Computational complexity of the kernel. Calculated as $$2 \cdot \text{size}^3$$
- **bw_conf_eff:** Effective configuration bandwidth. Calculated as $$\frac{16 \cdot \text{rocc}}{3 \cdot \text{cycles}}$$. The paper gives the formula for this in equation 4.
  - Each rocc instruction configures 2 registers worth of data, so 2 * 8 bytes
  - As stated above, spike assumes each instruction takes 1 cycle, we correct by that by multiplying by 3. See the paper for more details on this.
- **Ioc:** Operation-to-configuration complexity, the amount of accelerator operations that can be executed per byte of configuration. Calculated as $$\frac{\text{ops}}{3 \cdot \text{rocc}}$$
- **p_attain_seq:** Attained performance in sequential mode, calculated according to equation 3 in the paper from **Ioc**, **bw_conf_eff** and the stated **P_peak** of Gemmini of 512 ops/cycle.

