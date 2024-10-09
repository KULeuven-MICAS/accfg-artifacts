FROM ghcr.io/kuleuven-micas/snax:v0.1.6 AS increase-memory

COPY snax_cluster/ /snax_cluster/

RUN cd snax_cluster && \
    make CFG_OVERRIDE=cfg/snax-streamer-gemm.hjson -C target/snitch_cluster rtl-gen && \
    make CFG_OVERRIDE=cfg/snax-streamer-gemm.hjson -C target/snitch_cluster bin/snitch_cluster.vlt -j$(nproc) && \
    make -B -C target/snitch_cluster sw CFG_OVERRIDE=cfg/snax-streamer-gemm.hjson SELECT_RUNTIME=rtl-generic SELECT_TOOLCHAIN=llvm-generic

FROM ghcr.io/kuleuven-micas/snax:v0.1.6 AS base

COPY --from=increase-memory /snax_cluster/target/snitch_cluster/bin/snitch_cluster.vlt /opt/snax-streamer-gemm-rtl/bin/snitch_cluster.vlt
COPY --from=increase-memory /snax_cluster/sw/snRuntime/ /opt/snax-streamer-gemm/sw/snRuntime/
COPY --from=increase-memory /snax_cluster/target/snitch_cluster/sw /opt/snax-streamer-gemm/target/snitch_cluster/sw
COPY --from=increase-memory /snax_cluster/sw/ /opt/snax-streamer-gemm/sw

#     cp -r sw/snRuntime /opt/snax-streamer-gemm/sw/snRuntime && \
# FROM increase-memory 
#     cp -r target/snitch_cluster/bin/snitch_cluster.vlt /opt/snax-streamer-gemm-rtl/bin/snitch_cluster.vl && \
#     cp -r target/snitch_cluster/sw /opt/snax-streamer-gemm/target/snitch_cluster/sw && \
#     cp -r sw /opt/snax-streamer-gemm/sw
