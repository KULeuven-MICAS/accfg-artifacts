import get_all_numbers
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def change_option_labels(data):
    """
    Change labels of data:
        * NO_ACCFG_OPT -> Base
        * OVERLAP_ONLY -> Overlapped
        * DEDUP_ONLY   -> Deduplicated
        * ACCFG_BOTH   -> All
    """
    data = data.sort_values(["option", "size"])
    category_map = {'NO_ACCFG_OPT': 'Base', 'OVERLAP_ONLY': 'Overlapped', 'DEDUP_ONLY': 'Deduplicated', 'ACCFG_BOTH': 'All'}
    data['option'] = data['option'].cat.rename_categories(category_map)
    return data 

def plot_data(data, write=False, roofline=False, print_export=False):
    if print_export:
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

    custom_params = {"axes.spines.right": False, "axes.spines.top": False, 'figure.figsize':(6,3), "ytick.left" : True, "figure.dpi":300, **rc_fonts}
    colors = tuple((r/256,g/256,b/256) for (r,g,b) in [(51,117,56),(93,168,153),(148,203,236),(220,205,125),(194,106,119),(159,74,150),(126,41,84)])
    sns.set_theme(style="ticks", palette=colors, rc=custom_params)

    baseline = dict((row['size'], row['p_meas']) for i,row in data.query("option == 'Base'").iterrows())
    ax = sns.barplot(data, x="size", y="p_meas", hue="option")
    ax.set_ylabel('$P_{measured}$ (ops/cycle)')
    ax.set_xlabel('Square Matrix Multiplication Size')
    ax.set_xlim(-0.5,5.5)

    key_order = ["Base", "Deduplicated", "Overlapped", "All"]

    # Add little 'x' markers on top of the bars for P_attain
    for i, row in data.iterrows():
        kind = key_order.index(row["option"])
        # Get the x position for the marker
        x = ax.get_xticks()[list(data["size"].unique()).index(row["size"])] + (
            (kind - (len(key_order)/2)) * 0.2
        ) + 0.05 # adjust based on hue offset
        # Plot the 'x' marker
        if kind != 0:
            rel_perf = row['p_meas'] / baseline[row["size"]]
            ax.text(
                x, row['p_meas'] + 10, f"×{rel_perf:.2f}", 
                size=7,
                #color = "red" if rel_perf < 1 else None,
                rotation=90,
            )

    if roofline:
        ax.plot([-.5,5.5],[1024,1024], linestyle='--', linewidth=.8, color=colors[-1], label="Roofline (512 ops/cycle)")

    # Adding legend for the x markers
    plt.legend(loc="lower right")
    ax.yaxis.set_major_locator(MultipleLocator(128))
    ax.yaxis.set_minor_locator(MultipleLocator(32))
    if write:
        plt.savefig('snax_measured_perf.pdf',bbox_inches='tight')
    else:
        plt.show()

if __name__ == "__main__":
    all_data = get_all_numbers.walk_folder("../results_papaer")
    data = change_option_labels(all_data)
    plot_data(data)
