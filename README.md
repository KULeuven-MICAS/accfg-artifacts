# Artifacts Evaluation for - The Configuration Wall: Characterization and Elimination of Accelerator Configuration Overhead Automatic  

## Claims:

1. Performance on OpenGEMM is improved by 1.99x geomean, and up to 2.71x for some sizes through our optimizations.
2. Performance on Gemmini is improved by 10.5% geomean.
3. Figures 10, 11 and 12 in the paper can be reproduced.

## Installation and requirements

**Software Requirements:**
* linux (to run docker) or other linux-like environments (WSL), but these are untested.
* git (to obtain the source code for the experiments)
* docker (to run the experiments)

**Hardware Requirements:**

These experiments should run on any typical x86 computer.
As all hardware testing is done in simulation, no special hardware is required.
Some parts of those simulations/post-processing are rather compute-intensive, and will run faster on a faster machine.
All software needs to be pulled from ghcr.io and pypi, machines with faster internet connection will finish this faster.
These requirements should be plenty:

* 4-core x86 CPU
* 8 GB RAM
* A working internet connection (to download the docker container, this repository, and additional python packages)
* 16 GB of free disk space


**Note on time:** On modern Desktop CPUs we saw times at around ~15 minutes to complete the entire evaluation, but 
lower-power CPUs seem to struggle a lot with the simulation workloads. We based our time estimations on typical
student machine. If there is access to a fast workstation, times can be expected to be significantly lower.

### Getting the source (~ <1 minute)

To run the experiments in this repository, please clone the repository or download the [Zenodo Artifact](https://doi.org/10.5281/zenodo.16260752).

**Notes for Git:**

This repository relies on submodules.
Therefore, we recommend cloning as follows:

```sh
git clone --recursive https://github.com/KULeuven-MICAS/accfg-artifacts
```

If you already cloned the repository, but forgot the `--recursive` flag, do:

```sh
git submodule update --init --recursive --remote
```

**Notes for Zenodo:**
The Zenodo artifact comes in two parts, the docker container `accfg-artifacts.container.tar.gz` and the repository `accfg-artifacts.repo.tar.gz`.

The repository can be extracted by running `tar -xzf accfg-artifacts.repo.tar.gz`.

The `container` file needs to be imported using docker/podman by running `docker image load accfg-artifacts.container.tar.gz`.

### Basic Test:

A basic test to see if everything is working (next to just running `run-all.sh` and see if it crashes), is to run the simple `hello-world.sh` inside the docker container:

```bash
docker run --rm -itv $PWD:/repo:z ghcr.io/kuleuven-micas/accfg-artifacts:latest /repo/hello-world.sh
```

This should install all dependencies and check that all binaries are found and working. At the end it will print `If you see this, all is well!`.


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
**Explanation:** Compile all binaries for the OpenGEMM system, and run them in a pre-compiled Verilator simulation-binary.

*~ 15 minutes.*

```sh
cd /repo/accfg_artifacts
# Perform post processing on the numbers themselves
python3 get_all_numbers.py /repo/snax-mlir/kernels/streamer_matmul/results -o /repo/artifacts/opengemm_results.pkl
```
**Explanation:** Gather performance data of all results and dump in a small pickle file (contains a pandas DataFrame)

*~ <1 minute.*

```sh
# Plot the figures
python3 plot_snax.py -i /repo/artifacts/opengemm_results.pkl --plot=bar_plot -o /repo/artifacts/fig_11_bar_plot.png
python3 plot_snax.py -i /repo/artifacts/opengemm_results.pkl --plot=roofline -o /repo/artifacts/fig_12_roofline.png
```

**Explanation:** From the results in the pickle file, make bar chart and roofline plot.

*~ <1 minute.*

### Gemmini Experiments (~ 1h 30 minutes)

This repository can run all experiments for Gemmini

`cd` into the cloned `accfg-artifacts` folder and then:

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
cd /repo/gemmini-rocc-tests/bareMetalMLIR && make all_binaries_opt
```

**Explanation:** Build all binaries for simulation. This includes C binaries and optimized MLIR binaries.

*~ <2 minutes.*

```sh
# Install postprocessing requirements
cd /repo && pip install . --break-system-packages
# Run postprocessing and number gathering
python3 accfg_artifacts/gemmini_get_all_numbers.py gemmini-rocc-tests -o /repo/artifacts/gemmini_results.pkl
```

**Explanation:** Run all binaries in spike instruction accurate simulator (--> `mcycle` == `minstret` --> cycle counts match instruction counts in this simulation).
The `gemmini_get_all_numbers` script runs all spike simulations, watches the stdout for cycles/instruction printing, and dumps all instructions executed to count the amount of special RoCC instructions are executed.
All this information is stored in the pickle file.

*~ 1h 30 minutes.*

```sh
python3 /repo/accfg_artifacts/plot_gemmini.py -i /repo/artifacts/gemmini_results.pkl -o /repo/artifacts/fig_10_bar_plot.png
```

**Explanation:** From the results in the pickle file, make plots.

*~ <1 minute.*

## Understanding the Results:

The `artifacts` folder in the repository should contain two pickled pandas DataFrames, and three figures (10, 11 ad 12).

Running `python3 /repo/accfg_artifacts/show_results.py -i /repo/artifacts/` will print all the data again, and calculate geomean speedup to verify claims 1 and 2.

The figures produced should be identical (except for minor formatting changes) to the ones printed in the paper, allowing the verification of claim 3.

### OpenGEMM:

For OpenGEMM, the following table will be printed out:

```
OpenGemm Data:
    size              option   csrw  csrwi  cycles        ops  cycles_peak  no_opt_cycles   speedup  setup ins          Ioc  p_attain_seq  p_attain_conc  p_attain_opt      p_meas
0     16         Base (MLIR)     40     80     169       8192          8.0            169  1.000000        120    39.009524     72.495575      78.019048     72.495575   48.473373
12    32         Base (MLIR)    160    320     608      65536         64.0            608  1.000000        480    78.019048    135.404959     156.038095    135.404959  107.789474
4     64         Base (MLIR)    640   1280    2624     524288        512.0           2624  1.000000       1920   156.038095    239.182482     312.076190    239.182482  199.804878
8    128         Base (MLIR)   2560   5120   12380    4194304       4096.0          12380  1.000000       7680   312.076190    387.786982     624.152381    387.786982  338.796769
16   256         Base (MLIR)  12288  18432   65692   33554432      32768.0          65692  1.000000      30720   553.046414    531.732252    1024.000000    531.732252  510.784144
20   512         Base (MLIR)  49152  73728  393488  268435456     262144.0         393488  1.000000     122880  1106.092827    699.983979    1024.000000    699.983979  682.194771
1     16        Deduplicated     19     35      84       8192          8.0            169  2.011905         54    83.698595    143.877058     167.397190    143.877058   97.523810
13    32        Deduplicated     55     95     251      65536         64.0            608  2.422311        150   234.580761    321.747775     469.161521    321.747775  261.099602
5     64        Deduplicated    199    335    1136     524288        512.0           2624  2.309859        534   521.485018    516.698984    1024.000000    516.698984  461.521127
9    128        Deduplicated    775   1295    6767    4194304       4096.0          12380  1.829467       2070  1072.883517    693.194616    1024.000000    693.194616  619.817349
17   256        Deduplicated   3081   5133   43183   33554432      32768.0          65692  1.521247       8214  2160.324618    827.808266    1024.000000    827.808266  777.028738
21   512        Deduplicated  12297  20493  303398  268435456     262144.0         393488  1.296937      32790  4329.874746    915.717975    1024.000000    915.717975  884.763433
2     16          Overlapped     60    110     225       8192          8.0            169  0.751111        170    26.532794     50.451116      53.065587     53.065587   36.408889
14    32          Overlapped    200    380     671      65536         64.0            608  0.906110        580    63.167229    112.459888     126.334458    126.334458   97.669151
6     64          Overlapped    720   1400    2352     524288        512.0           2624  1.115646       2120   139.623968    219.413266     279.247936    279.247936  222.911565
10   128          Overlapped   2720   5360    8741    4194304       4096.0          12380  1.416314       8080   294.750808    374.123985     589.501616    589.501616  479.842581
18   256          Overlapped  12672  18848   40990   33554432      32768.0          65692  1.602635      31520   537.145931    524.271617    1024.000000   1024.000000  818.600439
22   512          Overlapped  49920  74560  292877  268435456     262144.0         393488  1.343526     124480  1089.960435    696.721006    1024.000000   1024.000000  916.546728
3     16  With Optimizations     25     35      91       8192          8.0            169  1.857143         60    67.216410    118.832276     134.432821    134.432821   90.021978
15    32  With Optimizations     67     95     224      65536         64.0            608  2.714286        162   200.186331    287.833105     400.372661    400.372661  292.571429
7     64  With Optimizations    223    335     968     524288        512.0           2624  2.710744        558   476.030417    493.360466     952.060833    952.060833  541.619835
11   128  With Optimizations    823   1295    6036    4194304       4096.0          12380  2.051027       2118  1022.658011    682.368186    1024.000000   1024.000000  694.881378
19   256  With Optimizations   3177   5133   40196   33554432      32768.0          65692  1.634292       8310  2108.203599    823.905626    1024.000000   1024.000000  834.770425
23   512  With Optimizations  12489  20493  291302  268435456     262144.0         393488  1.350791      32982  4276.893146    914.520005    1024.000000   1024.000000  921.502276
```

Here we measure the various `csr` instructions which write configuration to OpenGemm, together with cycle counts for the kernel (not shown in this print, but can be found inside the DataFrame when inspecting). From these we calculate the final measured attained performance `P_meas`.
- **size**: Square Matrix Size (32 means 32x32x32)
- **option**: Optimization option: `Base` means no optimizations, `Deduplicated` means just use deduplication, and `Overlapped` means just overlapping. `With Optimizations` uses both deduplication and overlapping
- **csrw**: Number of traced RISC-V CSRW instructions in simulation.
- **csrwi**: Number of traced RISC-V CSRWI instructions in simulation.
- **cycles**: Cycles used to configure the accelerator. This is a verilator-based and thus cycle-accurate simulation.
- **cycles_peak**: Cycles the matrix multiply would take if the accelerator were to operate at peak performance. 
- **no_opt_cycles**: Cycles of baseline, used to calculate speedup.
- **setup_ins**: sum of CSRW and CSRWI instructions.
- **Ioc:** Operation-to-configuration complexity, the amount of accelerator operations that can be executed per byte of configuration. Calculated as $$\frac{\text{ops}}{\frac{5}{8} \cdot \text{csrwi} + 4 \cdot \text{csrw}}$$
- **p_attain_seq**: Maximum attainable performance for sequential configuration.
- **p_attain_conc**: Maximum attainable performance for concurrent configuration.
- **p_attain_opt**: Maximum attainable performance for sequential configuration when used without overlapping, and for concurrent configuration when used with overlapping.
- **p_meas**: Actual measured performance. 


### Gemmini:

For Gemmini, the following table will be printed out:

```
              option  size  rocc  cycles        ops  bw_conf_eff           Ioc  p_attain_seq
8         C baseline    32    12     117      65536     0.547009    341.333333           137
9  MLIR deduplicated    32    12      85      65536     0.752941    341.333333           171
6         C baseline    64    12     120     524288     0.533333   2730.666667           379
7  MLIR deduplicated    64    12      89     524288     0.719101   2730.666667           406
4         C baseline   128    30     607    4194304     0.263591   8738.133333           419
5  MLIR deduplicated   128    26     167    4194304     0.830339  10082.461538           482
2         C baseline   256    78    1373   33554432     0.302986  26886.564103           482
3  MLIR deduplicated   256    58     259   33554432     1.194337  36157.793103           506
0         C baseline   512   258    4159  268435456     0.330849  65027.968992           500
1  MLIR deduplicated   512   178     482  268435456     1.969571  94254.022472           511
```

The columns have the following meaning:

- **size:** Square Matrix Size (32 means 32x32x32)
- **rocc:** Number of ROCC configuration instructions used
- **cycles:** Number of *instructions* used to configure the accelerator (note that since spike is only instruction accurate cycles=instructions). We approximate the actual number of cycles by multiplying with 3. See paper footnote 4 for more information.
- **ops:** Computational complexity of the kernel. Calculated as $$2 \cdot \text{size}^3$$
- **bw_conf_eff:** Effective configuration bandwidth. Calculated as $$\frac{16 \cdot \text{rocc}}{3 \cdot \text{cycles}}$$. The paper gives the formula for this in equation 4.
  - Each rocc instruction configures 2 registers worth of data, so 2 * 8 bytes
  - As stated above, spike assumes each instruction takes 1 cycle, we correct by that by multiplying by 3. See the paper for more details on this.
- **Ioc:** Operation-to-configuration complexity, the amount of accelerator operations that can be executed per byte of configuration. Calculated as $$\frac{\text{ops}}{\text{rocc}}$$
- **p_attain_seq:** Attained performance in sequential mode, calculated according to equation 3 in the paper from **Ioc**, **bw_conf_eff** and the stated **P_peak** of Gemmini of 512 ops/cycle.
