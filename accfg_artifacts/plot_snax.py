import get_all_numbers
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
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
custom_params = {"axes.spines.right": False, "axes.spines.top": False, 'figure.figsize':(6,3), "ytick.left" : True, "figure.dpi":300, **rc_fonts}
#colors = ["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c"]
# remove second blue to mark both our contributions green 
#colors = ["#a6cee3", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c"]
#colors = sns.color_palette("husl", 6)
colors = tuple((r/256,g/256,b/256) for (r,g,b) in [(51,117,56),(93,168,153),(148,203,236),(220,205,125),(194,106,119),(159,74,150),(126,41,84)])
#colors = tuple((r/256,g/256,b/256) for (r,g,b) in [(0,158,115),(0,114,178),(86,180,233),(230,159,0),(213,94,0),(204,121,167)])
sns.set_theme(style="ticks", palette=colors, rc=custom_params)

data = get_all_numbers.walk_folder("../results_papaer")
#data = pd.read_csv("snax_results.csv")
print(data)
exit()



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

# plot the P_max_attain
x_vals = ax.get_xticks()
y_vals = list(data.query("Name == 'Both'")['P_max_attain'])

#ax.plot(
#    [x_vals[i//2] + ((-1)**(i%2+1)*0.4) for i in range(2*len(x_vals))],
#    [y_vals[i//2] for i in range(2*len(y_vals))],
#    "r--",
#    label="Max Attainable Perf",
#    linewidth=0.8,
#)
    

#ax.plot([-.5,4.5],[512,512], linestyle='--', linewidth=.8, color=colors[-1], label="Roofline (512 ops/cycle)")


# Adding legend for the x markers
plt.legend(loc="lower right")
#plt.title("Measured Performance on SNAX, with relative improvement")
ax.yaxis.set_major_locator(MultipleLocator(128))
ax.yaxis.set_minor_locator(MultipleLocator(32))
plt.savefig('snax_measured_perf.pdf',bbox_inches='tight')
