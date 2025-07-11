import argparse
import subprocess
import re
import os
import pandas
import itertools
from concurrent.futures import ThreadPoolExecutor
import os

def get_spike_data(input_folder):
    with ThreadPoolExecutor(max(1, os.cpu_count() // 2)) as pool:
        print(f"Running on {pool._max_workers} threads")
        print("Sizes like 512 and 256 will take a long time. We are sorry. Please grab a drink of choice, maybe go for a walk.")
        def body(args: tuple[int, str]):
            size, option = args
            print(f"Working on option {option} for size {size}")
            # Use different binaries for the different options
            binary = None
            if option == "C baseline":
                binary = '{}/build/../build/bareMetalC/tiled_matmul_ws_{}x{}-baremetal'.format(input_folder, size, size)
            elif option == "MLIR":
                binary = '{}/bareMetalMLIR/tiled_matmul_{}x{}.no_opt.acc_dialect.x'.format(input_folder, size, size)
            elif option == "MLIR deduplicated":
                binary = '{}/bareMetalMLIR/tiled_matmul_{}x{}.opt.acc_dialect.x'.format(input_folder, size, size)
            command = [ 'spike', '-l', '--extension=gemmini', binary]

            """
            The following code will launch spike and process the output streams separately:
                * stderr: spike instruction log, counts amount of "unknown" instructions
                * stdout: spike stdout log, logs what is printf'ed by the program, 
                        regexed on first "Cycles taken:" number that is encountered
            """
            process = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)

            cycles = None
            stdout_pattern = re.compile(r"Cycles taken: (\d+)")
            unknown_count = 0
            # check each line in process output for cycles taken statement and if it contains "unknown"
            while True:
                line = process.stdout.readline()
                if line == "":
                    break
                # Regex the output of the program - looks for the line 'Cycles taken: <number>
                if cycles is None:
                    stdout_match = re.search(stdout_pattern, line)
                    cycles = int(stdout_match.group(1)) if stdout_match else None
                if 'unknown' in line:
                    unknown_count += 1

            assert cycles is not None

            # Append the extracted values to a dataframe for further processing
            return {"option": option, "size": size, "rocc": unknown_count, "cycles": cycles}

        data = list(pool.map(body, itertools.product([512, 256, 128, 64, 32],["C baseline", "MLIR deduplicated"])))
    return pandas.DataFrame(data).sort_values('size')


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process gemmini builds, by running them in spike.")

    # Add the directory argument
    parser.add_argument(
        'directory',
        type=str,
        help='Path to the gemmini-rocc-tests directory, with binaries buildt.'
    )
    parser.add_argument(
        '-o',
        '--output_path',
        type=str,
        default=None,
        help='Output path for .pkl creation.'
    )

    # Parse the arguments
    args = parser.parse_args()
    dataframe = get_spike_data(args.directory) 
    if dataframe.empty:
        raise RuntimeError("No results were found")
    print(dataframe)
    if args.output_path is not None:
        dataframe.to_pickle(args.output_path)

if __name__ == "__main__":
    main()
