#!/usr/bin/env bash
set -eu -o pipefail

if [[ ! -d /repo ]]; then
	docker run --rm -itv $PWD:/repo:z ghcr.io/kuleuven-micas/gemmini-test:latest /repo/run-all.sh || exit 1
	exit 0
fi

cd /repo/gemmini-rocc-tests && ./build.sh
cd /repo/gemmini-rocc-tests/bareMetalMLIR && make all_binaries all_binaries_no_opt
cd /repo && pip install . --break-system-packages
python3 accfg_artifacts/gemmini_get_all_numbers.py gemmini-rocc-tests -o results.pkl


