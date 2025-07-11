#!/usr/bin/env bash
set -eu -o pipefail

pip install /repo -e /repo/snax-mlir

echo "============="

xdsl-opt --version
snax-opt --version
mlir-opt-17 --version
which spike
verilator --version
riscv64-unknown-elf-gcc --version

echo "If you see this, all is well!"
