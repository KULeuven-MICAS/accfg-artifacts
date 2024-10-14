import subprocess
import re
import os
import pandas
import itertools

data = []
for size, option in itertools.product([32, 64, 128, 256, 512],["C baseline", "MLIR"]):
    print(f"Working on option {option} for size {size}")
    # Use different binaries for the different options
    binary = None
    if option == "C baseline":
        binary = '/repo/build/../build/bareMetalC/tiled_matmul_ws_{}x{}-baremetal'.format(size, size)
    elif option == "MLIR":
        binary = '/repo/bareMetalMLIR/tiled_matmul_{}x{}.acc_dialect.x'.format(size, size)
    elif option == "MLIR deduplicated":
        raise NotImplementedError()
    command = [ 'spike', '-l', '--extension=gemmini', binary]

    """
    The following code will launch spike and process the output streams separately:
        * stderr: spike instruction log, counts amount of "unknown" instructions
        * stdout: spike stdout log, logs what is printf'ed by the program, 
                  regexed on first "Cycles taken:" number that is encountered
    """
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
        universal_newlines=True  # This makes the output a string instead of bytes
    )
    stdout, stderr = process.communicate()
    # Run fgrep with LC_ALL=C locale to speed up search
    env = os.environ.copy()
    env["LC_ALL"] = "C"  # Set LC_ALL=C
    fgrep_process = subprocess.Popen(
        ['fgrep', 'unknown'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
        universal_newlines=True, env=env  # Pass the environment variable to fgrep
    )
    fgrep_output, _ = fgrep_process.communicate(input=stderr)
    # Count amount of occurences with `wc -l`
    wc_process = subprocess.Popen(
        ['wc', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True
    )
    wc_output, _ = wc_process.communicate(input=fgrep_output)
    # Get the amount of the program
    unknown_count = int(wc_output.strip())

    # Regex the output of the program - looks for the line 'Cycles taken: <number>
    stdout_pattern = r"Cycles taken: (\d+)"  
    stdout_match = re.search(stdout_pattern, stdout)
    cycles = int(stdout_match.group(1)) if stdout_match else None

    # Append the extracted values to a dataframe for further processing
    data.append({"option": option, "size": size, "rocc": unknown_count, "cycles": cycles})

print(pandas.DataFrame(data))

