from typing import List
import matplotlib
from matplotlib.axes import Axes
import seaborn as sns
import numpy as np


LABLES = {
    "Baseline": "#949494",
    "Chainguard": "#9745E6",
    "RapidFort": "#8dc7c7"
}

LINE_WIDTH = 1.2
MARKER_SZ = 30
YLABEL_FONT_SZ = 8
XLABEL_FONT_SZ = 10
LEGEND_FONT_SZ = 10
TITLE_PADDING = 10


def apply_style(ax: Axes):
    sns.despine(ax=ax)
    matplotlib.rcParams["font.family"] = "serif"


def plot_hline_chart(ax: Axes, baseline: np.ndarray, chainguard: np.ndarray,
                     rapidfort: np.ndarray, flavors: List[str], title: str,
                     xlabel: str):
    """
    Plot provider data as points on a horizontal lines represetning the original.

    @param ax: Axis for plotting
    @param org: Array of data for original images
    @param cg: Array of data for Chainguard images
    @param rf: Array of data for RapidFort
    @param flavors: List of image flavors
    """
    n_flavors = len(flavors)

    if len(baseline) != n_flavors:
        raise ValueError(f"Length of Original data does not match number of flavors: {len(baseline)} != {n_flavors}")
    if len(chainguard) != n_flavors:
        raise ValueError(f"Length of Chainguard data does not match number of flavors: {len(chainguard)} != {n_flavors}")
    if len(rapidfort) != n_flavors:
        raise ValueError(f"Length of RapidFort data does not match number of flavors: {len(chainguard)} != {n_flavors}")

    apply_style(ax)

    vendors = [baseline, chainguard, rapidfort]
    
    labeled = False
    for y in range(n_flavors):
        for pr, (lb, clr) in zip(vendors, LABLES.items()):
            if not labeled:
                ax.scatter(pr[y], y, color=clr, s=MARKER_SZ,
                        label=lb)
                ax.vlines(np.mean(pr), 0, n_flavors-1, linewidth=LINE_WIDTH,
                            color=clr, zorder=-1, linestyle="--")
            else:
                ax.scatter(pr[y], y, color=clr, s=MARKER_SZ)
        labeled = True
    
    ax.set_title(title, pad=TITLE_PADDING)
    ax.legend(loc='upper right', ncols=1, fontsize=LEGEND_FONT_SZ)

    xticks = ax.get_xticks()
    if xticks[0] % 1 != 0: # Preseve decimal in float labels
        xticks_labels = [str(t) for t in xticks]
    else:
        xticks_labels = [str(int(t)) for t in xticks]
    ax.set_xticks(xticks, xticks_labels, fontsize=XLABEL_FONT_SZ)
    ax.margins(x=0)
    ax.set_xlabel(xlabel, fontsize=XLABEL_FONT_SZ)
    
    ax.set_yticks(np.arange(n_flavors), flavors, fontsize=YLABEL_FONT_SZ)