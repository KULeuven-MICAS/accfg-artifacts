# Script that enters snax_cluster repository, and installs right version
cd snax_cluster
git apply ../increase_memory.patch
make CFG_OVERRIDE=cfg/snax-streamer-gemm.hjson -C target/snitch_cluster rtl-gen
make CFG_OVERRIDE=cfg/snax-streamer-gemm.hjson -C target/snitch_cluster bin/snitch_cluster.vlt -j$(nproc)
make -B -C target/snitch_cluster sw CFG_OVERRIDE=cfg/snax-streamer-gemm.hjson SELECT_RUNTIME=rtl-generic SELECT_TOOLCHAIN=llvm-generic
cp -r target/snitch_cluster/bin/snitch_cluster.vlt /opt/snax-streamer-gemm-rtl/bin/snitch_cluster.vl
cp -r sw/snRuntime /opt/snax-streamer-gemm/sw/snRuntime
cp -r target/snitch_cluster/sw /opt/snax-streamer-gemm/target/snitch_cluster/sw
cp -r sw /opt/snax-streamer-gemm/sw



