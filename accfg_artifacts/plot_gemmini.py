import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import pandas as pd
import argparse

def process_data(data):
    data["ops"] = data["size"]**3*2
    data["bw_conf_eff"] = 16*data["rocc"]/(data["cycles"]*3)
    data["Ioc"] = data["ops"]/(data["rocc"]*16)
    data["p_attain_seq"] =  round(1 / ((1/512) + (1/(data["Ioc"]*data["bw_conf_eff"])))).astype(int)
    print(data)
    data_simple = data.query("option in ['C baseline', 'MLIR deduplicated']")
    return data_simple


def plot_data(data, output):
    ax = sns.barplot(data, x="size", y="p_attain_seq", hue="option")
    ax.set_ylabel('$P_{approximated}$ (ops/cycle)')
    ax.set_xlabel("Square Matrix Multiplication size")
    ax.set_xlim(-0.5,4.5)

    key_order = list(data["option"].unique())

    # Add little 'x' markers on top of the bars for P_attain
    for i, row in data.iterrows():
        kind = key_order.index(row["option"])
        # Get the x position for the marker
        x = ax.get_xticks()[list(data["size"].unique()).index(row["size"])] + (
            (kind - (len(key_order)/2)) * 0.3
        ) + 0.03 # adjust based on hue offset
        # Plot the 'x' marker
        ax.text(x, row['p_attain_seq'] + 10, row['p_attain_seq'], size=10)

    ax.plot([-.5,4.5],[512,512], linestyle='--', linewidth=.8, color="red", label="$P_{Peak}$ (512 ops/cycle)")


    # Adding legend for the x markers
    plt.legend(loc="lower right")
    ax.yaxis.set_major_locator(MultipleLocator(128))
    ax.yaxis.set_minor_locator(MultipleLocator(32))
    plt.savefig(output,bbox_inches='tight')



def main():
    parser = argparse.ArgumentParser(description="Generate performance plots (roofline or bar).")
    parser.add_argument(
        '-i',
        '--input-path', 
        type=str, 
        help="Path to the pickle file or results folder."
    )
    parser.add_argument(
        '-o',
        '--output-path', 
        type=str, 
        help="Path to the output, also enables figure exporting"
    )

    args = parser.parse_args()
    data = pd.read_pickle(args.input_path)
    data = process_data(data)
    plot_data(data,args.output_path)

if __name__ == "__main__":
    main()

