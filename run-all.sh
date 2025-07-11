#!/usr/bin/env bash
set -eu -o pipefail

if ! mountpoint -q /repo; then
	docker run --rm -itv $PWD:/repo:z ghcr.io/kuleuven-micas/accfg-artifacts:latest /repo/run-all.sh || exit 1
	exit 0
fi

# OpenGEMM Experiments:
pip install /repo -e /repo/snax-mlir --break-system-packages
cd /repo/snax-mlir/kernels/streamer_matmul
python3 genbenchmark.py
cd /repo/accfg_artifacts
python3 get_all_numbers.py /repo/snax-mlir/kernels/streamer_matmul/results -o /repo/artifacts/opengemm_results.pkl
python3 plot_snax.py -i /repo/artifacts/opengemm_results.pkl --plot=bar_plot -o /repo/artifacts/fig_11_bar_plot.png
python3 plot_snax.py -i /repo/artifacts/opengemm_results.pkl --plot=roofline -o /repo/artifacts/fig_12_roofline.png


# Gemmini Experiments:
cd /repo/gemmini-rocc-tests && ./build.sh
cd /repo/gemmini-rocc-tests/bareMetalMLIR && make all_binaries all_binaries_no_opt
#cd /repo && pip install . --break-system-packages
cd /repo
python3 accfg_artifacts/gemmini_get_all_numbers.py gemmini-rocc-tests -o /repo/artifacts/gemmini_results.pkl
cd /repo/accfg_artifacts
python3 plot_gemmini.py -i /repo/artifacts/gemmini_results.pkl -o /repo/artifacts/fig10_bar_plot.png
