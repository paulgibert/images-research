from typing import List
import matplotlib
from matplotlib.axes import Axes
import seaborn as sns
import numpy as np


COLOR_CHAINGUARD = "#3443f4"
COLOR_RAPIDFORT = "#8dc7c7"
COLOR_NULL = "#949494"

LINE_WIDTH = 1.2
MARKER_SZ = 30
XSTEP = 50
YLABEL_FONT_SZ = 8
XLABEL_FONT_SZ = 10
LEGEND_FONT_SZ = 10
TITLE_PADDING = 10


def apply_style(ax: Axes):
    sns.despine(ax=ax)
    matplotlib.rcParams["font.family"] = "serif"


def plot_hline_chart(ax: Axes, org: np.ndarray, cg: np.ndarray, rf: np.ndarray,
                     flavors: List[str], title: str, xlabel: str):
    """
    Plot provider data as points on a horizontal lines represetning the original.

    @param ax: Axis for plotting
    @param org: Array of data for original images
    @param cg: Array of data for Chainguard images
    @param rf: Array of data for RapidFort
    @param flavors: List of image flavors
    """
    n_flavors = len(flavors)

    if len(org) != n_flavors:
        raise ValueError(f"Length of Original data does not match number of flavors: {len(org)} != {n_flavors}")
    if len(cg) != n_flavors:
        raise ValueError(f"Length of Chainguard data does not match number of flavors: {len(cg)} != {n_flavors}")
    if len(rf) != n_flavors:
        raise ValueError(f"Length of RapidFort data does not match number of flavors: {len(cg)} != {n_flavors}")

    apply_style(ax)

    providers = [cg, rf, org]
    colors = [COLOR_CHAINGUARD, COLOR_RAPIDFORT, COLOR_NULL]
    
    labeled = False
    for y in range(n_flavors):
        labels = [None] * 3
        if not labeled:
            labels = ["Chainguard", "RapidFort", "Original"]

        for pr, clr, lb in zip(providers, colors, labels):
            ax.scatter(pr[y], y, color=clr, s=MARKER_SZ,
                       label=lb)
            if not labeled:
                ax.vlines(np.mean(pr), 0, n_flavors-1, linewidth=LINE_WIDTH,
                          color=clr, zorder=-1, linestyle="--")
        labeled = True
    
    ax.set_title(title, pad=TITLE_PADDING)
    ax.legend(loc='upper right', ncols=1, fontsize=LEGEND_FONT_SZ)

    xticks = np.arange(0, 500, XSTEP)
    xticks_labels = [str(int(t)) for t in xticks]
    ax.set_xticks(xticks, xticks_labels, fontsize=XLABEL_FONT_SZ)
    ax.set_xlabel(xlabel, fontsize=XLABEL_FONT_SZ)
    
    ax.set_yticks(np.arange(n_flavors), flavors, fontsize=YLABEL_FONT_SZ)