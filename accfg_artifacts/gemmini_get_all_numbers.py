import argparse
import subprocess
import re
import os
import pandas
import itertools

def get_spike_data(input_folder):
    data = []
    for size, option in itertools.product([32, 64, 128, 256, 512],["C baseline", "MLIR", "MLIR deduplicated"]):
        print(f"Working on option {option} for size {size}")
        # Use different binaries for the different options
        binary = None
        if option == "C baseline":
            binary = '{}/build/../build/bareMetalC/tiled_matmul_ws_{}x{}-baremetal'.format(input_folder, size, size)
        elif option == "MLIR":
            binary = '{}/bareMetalMLIR/tiled_matmul_{}x{}.no_opt.acc_dialect.x'.format(input_folder, size, size)
        elif option == "MLIR deduplicated":
            binary = '{}/bareMetalMLIR/tiled_matmul_{}x{}.acc_dialect.x'.format(input_folder, size, size)
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
        lines = 0
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
        data.append({"option": option, "size": size, "rocc": unknown_count, "cycles": cycles})

    return (pandas.DataFrame(data))



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
