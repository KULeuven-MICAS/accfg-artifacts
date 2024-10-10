import os
import subprocess
import pandas as pd
import glob
import re

CMD_CSRWI = 'cat {} | grep "csrwi   unknown" | wc -l'
CMD_CSRW = 'cat {} | grep "csrw    unknown" | wc -l'
CMD_CYCLES = "cat {} | grep 'cycles' | awk 'NR == 2' | sed 's/.*: \\([0-9]*\\).*/\\1/'"

def extract_first_number(pattern):
    # Use regex to find the first number of the form ixixi, like 128x128x128
    match = re.search(r'(\d+)x\d+x\d+', pattern)
    if match:
        return int(match.group(1))  # Return the first number as an integer
    return None

def extract_count(trace_file, cmd):
    try:
        # Run the command and capture the output
        result = subprocess.check_output(cmd.format(trace_file), shell=True, universal_newlines=True).strip()
        cycles = int(result)  # Convert the result to integer

        # Update the DataFrame with the cycle count
        return cycles
    
    except subprocess.CalledProcessError as e:
        print(f"Failed to process {trace_file}: {e}")
    except ValueError as ve:
        print(f"Could not convert output to integer for {trace_file}: {ve}")

# Base folder path to start walking through the tree

base_path = 'results_paper'
data = []

for folder in glob.iglob(os.path.join(base_path, "tiled_matmul_generated_*x*x*")):
    number = extract_first_number(folder)
    for option, experiment in [(option, os.path.join(folder, f"test_generated_{number}x{number}x{number}"+"_"+option)) for option in ["NO_ACCFG_OPT","DEDUP_ONLY", "OVERLAP_ONLY", "ACCFG_BOTH"]]:
        cycle_file = os.path.join(experiment,'trace_hart_00000.trace.json')
        trace_file = os.path.join(experiment,'trace_hart_00000.trace.txt')
        if os.path.exists(cycle_file) and os.path.exists(trace_file):
            data.append({
                'size': number,
                'option': option,
                'csrw': extract_count(trace_file, CMD_CSRW),
                'csrwi': extract_count(trace_file, CMD_CSRWI),
                'cycles': extract_count(cycle_file, CMD_CYCLES)
            })


df = pd.DataFrame(data)

# Define the custom sort order for 'category'
# Convert 'option' column to a categorical type with the specified order
category_order = ['NO_ACCFG_OPT', 'DEDUP_ONLY', 'OVERLAP_ONLY','ACCFG_BOTH']
df['option'] = pd.Categorical(df['option'], categories=category_order, ordered=True)

conf_bandwidth = 2
peak_perf = 1024
df['ops'] = (df['size']**3)*2
df['setup ins'] = df['csrw'] + df['csrwi']
df['Ioc'] = df['ops']/((5/8)*df['csrwi'] + (4)*df['csrw'])
df['cycles_peak'] = df['ops'] / peak_perf
df['p_meas'] = df['ops'] / df['cycles']
df['p_attain_seq'] = (1/((1/peak_perf) + (1/(df['Ioc']*conf_bandwidth))))
df['p_attain_conc'] = (df['Ioc'] * conf_bandwidth).clip(upper=peak_perf)

def get_p_attain_opt(row):
    # For these two options, the sequential attainable is the maximum attainable
    if row['option'] in ['NO_ACCFG_OPT', 'DEDUP_ONLY']:
        return row['p_attain_seq']
    # In the other case, you are competing against the concurrent attainable
    else:
        return row['p_attain_conc']

# Apply the function to create the new column
df['p_attain_opt'] = df.apply(get_p_attain_opt, axis=1)

print(df.sort_values(["size", "option"]))
