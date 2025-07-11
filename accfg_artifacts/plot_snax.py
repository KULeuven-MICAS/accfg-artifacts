import get_all_numbers
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import argparse


def change_option_labels(data):
    """
    Change labels of data:
        * NO_ACCFG_OPT -> Base
        * OVERLAP_ONLY -> Overlapped
        * DEDUP_ONLY   -> Deduplicated
        * ACCFG_BOTH   -> All
    """
    data = data.sort_values(["option", "size"])
    category_map = {'NO_ACCFG_OPT': 'Base (MLIR)', 'OVERLAP_ONLY': 'Overlapped', 'DEDUP_ONLY': 'Deduplicated', 'ACCFG_BOTH': 'With Optimizations'}
    data['option'] = data['option'].cat.rename_categories(category_map)
    return data 

def bar_plot_data(data, colors, filename, roofline=False, write=False):

    print(data)
    data_simple = data.query('option == "Base (MLIR)" or option == "With Optimizations"')
    data = data_simple
    baseline = dict((row['size'], row['p_meas']) for i,row in data.query("option == 'Base (MLIR)'").iterrows())

    ax = sns.barplot(data_simple, x="size", y="p_meas", hue="option")
    ax.set_ylabel('$P_{measured}$ (ops/cycle)')
    ax.set_xlabel('Square Matrix Multiplication Size')
    ax.set_xlim(-0.5,5.5)

    key_order = ["Base (MLIR)", "With Optimizations"]

    # Add little 'x' markers on top of the bars for P_attain
    for i, row in data_simple.iterrows():
        kind = key_order.index(row["option"])
        # Get the x position for the marker
        x = ax.get_xticks()[list(data_simple["size"].unique()).index(row["size"])] + (
            (kind - (len(key_order)/2)) * 0.2
        ) + 0.05 # adjust based on hue offset
        # Plot the 'x' marker
        if kind != 0:
            rel_perf = row['p_meas'] / baseline[row["size"]]
            ax.text(
                x, row['p_meas'] + 10, f"×{rel_perf:.2f}",
                size=10            ,
                #color = "red" if rel_perf < 1 else None,
                rotation=0,
            )

    # plot the P_max_attain
    x_vals = ax.get_xticks()
    y_vals = list(data_simple.query("option == 'With Optimizations'")['p_attain_conc'])

    #ax.plot(
    #    [x_vals[i//2] + ((-1)**(i%2+1)*0.4) for i in range(2*len(x_vals))],
    #    [y_vals[i//2] for i in range(2*len(y_vals))],
    #    "r--",
    #    label="Max Attainable Perf",
    #    linewidth=0.8,
    #)


    #ax.plot([-.5,4.5],[512,512], linestyle='--', linewidth=.8, color=colors[-1], label="Roofline (512 ops/cycle)")


    # Adding legend for the x markers
    #plt.legend(loc="lower right")
    plt.title("Measured Performance on SNAX, with relative improvement")
    ax.yaxis.set_major_locator(MultipleLocator(128))
    ax.yaxis.set_minor_locator(MultipleLocator(32))

    #baseline = dict((row['size'], row['p_meas']) for _,row in data.query("option == 'Base (MLIR)'").iterrows())
    #ax = sns.barplot(data, x="size", y="p_meas", hue="option")
    #ax.set_ylabel('$P_{measured}$ (ops/cycle)')
    #ax.set_xlabel('Square Matrix Multiplication Size')
    #ax.set_xlim(-0.5,5.5)

    ##key_order = ["Base", "Deduplicated", "Overlapped", "All"]
    #key_order = ["Base (MLIR)", "Deduplicated", "Overlapped", "With Optimizations"]

    ## Add little 'x' markers on top of the bars for P_attain
    #for _, row in data.iterrows():
    #    kind = key_order.index(row["option"])
    #    # Get the x position for the marker
    #    x = ax.get_xticks()[list(data["size"].unique()).index(row["size"])] + (
    #        (kind - (len(key_order)/2)) * 0.2
    #    ) + 0.05 # adjust based on hue offset
    #    # Plot the 'x' marker
    #    if kind != 0:
    #        rel_perf = row['p_meas'] / baseline[row["size"]]
    #        ax.text(
    #            x, row['p_meas'] + 10, f"×{rel_perf:.2f}", 
    #            size=7,
    #            #color = "red" if rel_perf < 1 else None,
    #            rotation=90,
    #        )

    #if roofline:
    #    ax.plot([-.5,5.5],[1024,1024], linestyle='--', linewidth=.8, color=colors[-1], label="Roofline (512 ops/cycle)")

    ## Adding legend for the x markers
    #plt.legend(loc="lower right")
    #ax.yaxis.set_major_locator(MultipleLocator(128))
    #ax.yaxis.set_minor_locator(MultipleLocator(32))
    if write:
        plt.savefig(filename,bbox_inches='tight')
    else:
        plt.show()

def roofline_plot_data(data, filename, colors, bw_conf=2, p_peak=1024, write=False):
    xlim = [15, 5000]
    ylim = [30,1300]


    palette = dict(
        zip((16, 32, 64, 128, 256, 512), colors)
    )
    # Create scatter plot
    plt.rcParams.update({
            'legend.fontsize': 7,         # Font size for legends
            'legend.title_fontsize': 8,   # Font size for legend titles
        })


    ax = sns.scatterplot(data=data, x="Ioc", y="p_meas", hue="size", style="option", palette=palette)
    plt.xscale("log")
    plt.yscale("log")

    ## Plot rooflines
    ax.plot(ax.get_xticks(), [p_peak for _ in ax.get_xticks()], "--", color="#000", linewidth=0.8, scalex=False, scaley=False)
    ax.plot(ax.get_xticks(), [i * bw_conf for i in ax.get_xticks()], "--", color="#000", linewidth=0.8, scalex=False, scaley=False, label="Concurrent")
    x_ticks = np.logspace(1, 4)
    y_ticks = 1 / ((1 / p_peak) + (1 / (bw_conf * x_ticks)))
    plt.plot(x_ticks, y_ticks, "r--", scalex=False, scaley=False, linewidth=0.8, label="Sequential")

    ax.set_ylabel('$P_{measured}$(ops/cycle)')
    ax.set_xlabel('$I_{OC}$ (ops/byte)')
    plt.xlim(xlim)
    plt.ylim(ylim)

    ## Shrink current axis by 20% to fit legend
    box = ax.get_position()
    ax.set_position((box.x0, box.y0, box.width * 0.8, box.height))

    ## Extract handles and labels for separate legends
    handles, labels = ax.get_legend_handles_labels()

    ## Split handles and labels based on your data (Size vs. Name)
    size_handles = handles[1:7]   # Assuming first 6 are sizes (adjust this based on actual output)
    size_labels = labels[1:7]
    name_handles = handles[8:12]   # Assuming rest are names (adjust accordingly)
    name_labels = labels[8:12]

    legend_fontsize=8
    legend_columnspacing=0.5

    ## Adding the Size legend
    size_legend = ax.legend(size_handles, size_labels, title="Square Matrix Multiplication Size", loc='upper center',fontsize=legend_fontsize, columnspacing=legend_columnspacing,
                            bbox_to_anchor=(0.1, -0.25), ncol=3, fancybox=True, shadow=False)

    ## Adding the Name legend separately
    ax.add_artist(size_legend)
    print(name_handles)
    print("help")
    print(name_handles)
    ax.legend(name_handles, name_labels, title="Optimization", loc='upper center', fontsize=legend_fontsize, columnspacing=legend_columnspacing,
              bbox_to_anchor=(0.7, -0.25), ncol=2, fancybox=True, shadow=False)

    # Save the plot
    if write:
        plt.savefig(filename, bbox_inches='tight')
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="Generate performance plots (roofline or bar).")
    parser.add_argument(
        '--plot', 
        type=str, 
        choices=['roofline', 'bar_plot'], 
        default='roofline',
        help="Type of plot to generate: 'roofline' (default) or 'bar_plot'."
    )
    parser.add_argument(
        '--parse', 
        action='store_true',
        help="If set, parse data from folder instead of reading from pickle file."
    )
    parser.add_argument(
        '--print-export', 
        action='store_true',
        help="If set, use TeX and large font for exporting figures."
    )
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
    if not args.parse:
        all_data = pd.read_pickle(args.input_path)
    else:
        all_data = get_all_numbers.walk_folder(args.input_path)

    if args.print_export:
        rc_fonts = {
        "font.family": "serif",
        "font.size": 20,
        'figure.figsize': (5, 3),
        "text.usetex": True,
        'text.latex.preamble': 
            r"""
            \usepackage{libertine}
            \usepackage[libertine]{newtxmath}
            """,
        }
    else:
        rc_fonts = {}

    if args.output_path is None:
        write = False
    else:
        write = True

    custom_params = {"axes.spines.right": False, "axes.spines.top": False, 'figure.figsize':(6,3), "ytick.left" : True, "figure.dpi":300, **rc_fonts}
    colors = tuple((r/256,g/256,b/256) for (r,g,b) in [(51,117,56),(93,168,153),(148,203,236),(220,205,125),(194,106,119),(159,74,150),(126,41,84)])
    sns.set_theme(style="ticks", palette=colors, rc=custom_params)
    data = change_option_labels(all_data)
    if args.plot == "bar_plot":
        bar_plot_data(data, filename=args.output_path, colors=colors, write=write)
    elif args.plot == "roofline":
        roofline_plot_data(data, filename=args.output_path, colors=colors, write=write)

if __name__ == "__main__":
    main()

