import get_all_numbers
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator


# Convert data to format that plotting script expects

all_data = get_all_numbers.walk_folder("../results_papaer")


selected_columns = all_data[["option","size","p_meas","Ioc","p_attain_opt"]].sort_values(["option", "size"])
selected_columns.columns = ['Name', 'Size', 'P_measured', 'I_conf', 'P_max_attain']
category_map = {'NO_ACCFG_OPT': 'Base', 'OVERLAP_ONLY': 'Overlapped', 'DEDUP_ONLY': 'Deduplicated', 'ACCFG_BOTH': 'All'}
selected_columns['Name'] = selected_columns['Name'].replace(category_map)
print(selected_columns)

data = selected_columns

not_print = False
roofline = False

# Plot data

if not_print:
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


baseline = dict((row['Size'], row['P_measured']) for i,row in data.query("Name == 'Base'").iterrows())
ax = sns.barplot(data, x="Size", y="P_measured", hue="Name")
ax.set_ylabel('$P_{measured}$ (ops/cycle)')
ax.set_xlabel('Square Matrix Multiplication Size')
ax.set_xlim(-0.5,5.5)

key_order = ["Base", "Deduplicated", "Overlapped", "All"]

# Add little 'x' markers on top of the bars for P_attain
for i, row in data.iterrows():
    kind = key_order.index(row["Name"])
    # Get the x position for the marker
    x = ax.get_xticks()[list(data["Size"].unique()).index(row["Size"])] + (
        (kind - (len(key_order)/2)) * 0.2
    ) + 0.05 # adjust based on hue offset
    # Plot the 'x' marker
    if kind != 0:
        rel_perf = row['P_measured'] / baseline[row["Size"]]
        ax.text(
            x, row['P_measured'] + 10, f"×{rel_perf:.2f}", 
            size=7,
            #color = "red" if rel_perf < 1 else None,
            rotation=90,
        )

    
if roofline:
    ax.plot([-.5,5.5],[1024,1024], linestyle='--', linewidth=.8, color=colors[-1], label="Roofline (512 ops/cycle)")


# Adding legend for the x markers
plt.legend(loc="lower right")
#plt.title("Measured Performance on SNAX, with relative improvement")
ax.yaxis.set_major_locator(MultipleLocator(128))
ax.yaxis.set_minor_locator(MultipleLocator(32))
plt.savefig('snax_measured_perf.pdf',bbox_inches='tight')
