from typing import Dict, List
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

COLOR_CHAINGUARD = "#3443f4"
COLOR_RAPIDFORT = "#0e7090"
COLOR_NULL = "#474747"

# TODO: Correct bug where legend labels get dimmed
ALPHA_DIMMED = 0.3

    
def plot_stacked_bar(ax: Axes, org: np.ndarray, cg: np.ndarray, rf: np.ndarray,
                     flavors: List[str]):
    """
    Plots a single stacked bar per provider.

    @param ax: Axis for plotting
    @param org: Array of data for original images
    @param cg: Array of data for Chainguard images
    @param rf: Array of data for RapidFort
    """
    n_flavors = len(flavors)
    colors = [COLOR_NULL, COLOR_CHAINGUARD, COLOR_RAPIDFORT]
    providers = ["Original", "Chainguard", "RapidFort"]

    if len(org) != n_flavors:
        raise ValueError(f"Length of Original data does not match number of flavors: {len(org)} != {n_flavors}")
    if len(cg) != n_flavors:
        raise ValueError(f"Length of Chainguard data does not match number of flavors: {len(cg)} != {n_flavors}")
    if len(rf) != n_flavors:
        raise ValueError(f"Length of RapidFort data does not match number of flavors: {len(cg)} != {n_flavors}")
    
    data = np.concatenate(([org], [cg], [rf]), axis=0)
    zorder = np.argsort(data, axis=0)
    labeled = False
    for flavor_i in range(data.shape[1]):
        bottom = 0
        for provider_i in range(data.shape[0]):
            x = flavor_i
            order = zorder[provider_i, flavor_i]
            y = data[order, flavor_i]
            height = y-bottom

            label = None if labeled else providers[order]

            ax.bar(x, height, width=.9, bottom=bottom, color=colors[order],
                   label=label)
            bottom += height

        labeled = True
    
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_xticks(np.arange(data.shape[1]), flavors, fontsize=8)
    ax.legend(loc='upper right', ncols=1)


def plot_grouped_bar(ax: Axes, org: np.ndarray, cg: np.ndarray, rf: np.ndarray,
                     flavors: List[str], highlight_min=False):
    """
    Plots a group of bars per provider.
    
    @param ax: Axis for plotting
    @param org: Array of data for original images
    @param cg: Array of data for Chainguard images
    @param rf: Array of data for RapidFort
    """
    n_flavors = len(flavors)

    if len(org) != n_flavors:
        raise ValueError(f"Length of Original data does not match number of flavors: {len(org)} != {n_flavors}")
    if len(cg) != n_flavors:
        raise ValueError(f"Length of Chainguard data does not match number of flavors: {len(cg)} != {n_flavors}")
    if len(rf) != n_flavors:
        raise ValueError(f"Length of RapidFort data does not match number of flavors: {len(cg)} != {n_flavors}")

    labeled = False
    for x in range(n_flavors):
        bar_width = 0.25
        alpha = [1, 1]

        if highlight_min:
            if cg[x] < rf[x]:
                alpha[1] = ALPHA_DIMMED
            elif rf[x] < cg[x]:
                alpha[0] = ALPHA_DIMMED

        labels = [None] * 3
        if not labeled:
            labels = ["Chainguard", "Original", "RapidFort"]
        
        ax.bar(x - bar_width, cg[x], bar_width,
               color=COLOR_CHAINGUARD,
               alpha=alpha[0], label=labels[0])
        ax.bar(x, rf[x], bar_width, color=COLOR_RAPIDFORT,
               alpha=alpha[1], label=labels[1])
        ax.bar(x + bar_width, org[x], bar_width, color=COLOR_NULL,
               label=labels[2])
        
        labeled = True
    
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_xticks(np.arange(n_flavors), flavors, fontsize=8)
    ax.legend(loc='upper right', ncols=1)


# TODO:
#   1) Add stacked bar for original
#   2) Thin line for original?
def plot_sbs_grouped_bar(ax: List[Axes], org: np.ndarray, cg: np.ndarray, rf: np.ndarray,
                         flavors: List[str], highlight_min=False):
    """
    Plot side-by-side subplots of provider vs original grouped bars.
    
    @param ax: Axis for plotting
    @param org: Array of data for original images
    @param cg: Array of data for Chainguard images
    @param rf: Array of data for RapidFort
    """
    n_flavors = len(flavors)

    if len(org) != n_flavors:
        raise ValueError(f"Length of Original data does not match number of flavors: {len(org)} != {n_flavors}")
    if len(cg) != n_flavors:
        raise ValueError(f"Length of Chainguard data does not match number of flavors: {len(cg)} != {n_flavors}")
    if len(rf) != n_flavors:
        raise ValueError(f"Length of RapidFort data does not match number of flavors: {len(cg)} != {n_flavors}")
    
    labeled = False

    for x in range(n_flavors):
        bar_width = 0.45
        offset = 0.5 * bar_width
        alpha = [1, 1]

        if highlight_min:
            if cg[x] < rf[x]:
                alpha[1] = ALPHA_DIMMED
            elif rf[x] < cg[x]:
                alpha[0] = ALPHA_DIMMED

        labels = [None] * 3
        if not labeled:
            labels = ["Chainguard", "Original", "RapidFort"]

        ax[0].bar(x - offset, cg[x], bar_width,
               color=COLOR_CHAINGUARD,
               alpha=alpha[0], label=labels[0])
        ax[1].bar(x - offset, rf[x], bar_width, color=COLOR_RAPIDFORT,
               alpha=alpha[1], label=labels[1])
        for i in [0, 1]:
            ax[i].bar(x + offset, org[x], bar_width, color=COLOR_NULL,
                      label=labels[2])
        
        labeled = True
    
    for i in [0, 1]:
        ax[i].yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax[i].set_xticks(np.arange(n_flavors), flavors, fontsize=8)
        ax[i].legend(loc='upper right', ncols=1)


def plot_hist(ax: List[Axes], org: np.ndarray, cg: np.ndarray, rf: np.ndarray,
              flavors: List[str], nbins: any, alpha=1.0, uselines=False):
    """
    Plot histogram of data using bars or lines.
    
    @param ax: Axis for plotting
    @param org: Array of data for original images
    @param cg: Array of data for Chainguard images
    @param rf: Array of data for RapidFort
    """
    n_flavors = len(flavors)
    providers = ["Chainguard", "RapidFort", "Original"]
    colors = [COLOR_CHAINGUARD, COLOR_RAPIDFORT, COLOR_NULL]
    
    if len(org) != n_flavors:
        raise ValueError(f"Length of Original data does not match number of flavors: {len(org)} != {n_flavors}")
    if len(cg) != n_flavors:
        raise ValueError(f"Length of Chainguard data does not match number of flavors: {len(cg)} != {n_flavors}")
    if len(rf) != n_flavors:
        raise ValueError(f"Length of RapidFort data does not match number of flavors: {len(cg)} != {n_flavors}")

    for data, label, clr in zip([cg, rf, org], providers, colors):
        counts, b = np.histogram(data, nbins)
        bin_sz = b[1] - b[0]
        x = ((bin_sz) / 2) + b[:-1]
        if uselines:
            ax.plot(x, counts, color=clr, alpha=alpha,
                    label=label)
        else:
            ax.bar(x, counts, width=bin_sz, color=clr, alpha=alpha,
                    label=label)
    
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.legend(loc='upper right', ncols=1)


def plot_hline_chart(ax: Axes, org: np.ndarray, cg: np.ndarray, rf: np.ndarray,
                     flavors: List[str], highlight_min=False):
    """
    Plot provider data as points on a horizontal lines represetning the original.

    @param ax: Axis for plotting
    @param org: Array of data for original images
    @param cg: Array of data for Chainguard images
    @param rf: Array of data for RapidFort
    """
    n_flavors = len(flavors)

    if len(org) != n_flavors:
        raise ValueError(f"Length of Original data does not match number of flavors: {len(org)} != {n_flavors}")
    if len(cg) != n_flavors:
        raise ValueError(f"Length of Chainguard data does not match number of flavors: {len(cg)} != {n_flavors}")
    if len(rf) != n_flavors:
        raise ValueError(f"Length of RapidFort data does not match number of flavors: {len(cg)} != {n_flavors}")
    
    labeled = False

    for y in range(n_flavors):
        alpha = [1, 1]

        if highlight_min:
            if cg[y] < rf[y]:
                alpha[1] = ALPHA_DIMMED
            elif rf[y] < cg[y]:
                alpha[0] = ALPHA_DIMMED

        labels = [None] * 3
        if not labeled:
            labels = ["Chainguard", "RapidFort", "Original"]

        ax.scatter(cg[y], y, color=COLOR_CHAINGUARD,
                   alpha=alpha[0], label=labels[0])
        ax.scatter(rf[y], y, color=COLOR_RAPIDFORT,
                   alpha=alpha[1], label=labels[1])
        ax.hlines(y, 0, org[y], color=COLOR_NULL,
                  label=labels[2], zorder=-1)
        ax.scatter(org[y], y, color=COLOR_NULL,
                   zorder=-1, marker="|")
        
        labeled = True
    
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.set_yticks(np.arange(n_flavors), flavors, fontsize=8)
        ax.legend(loc='upper right', ncols=1)


if __name__ == "__main__":
    fig, ax = plt.subplots()

    n_flavors = 28
    original = np.random.randint(15, 25, size=(n_flavors))
    chainguard = np.random.randint(0, 8, size=(n_flavors))
    rapidfort = np.random.randint(5, 12, size=(n_flavors))
    flavors = ["flv_" + str(i) for i in range(n_flavors)]

    nbins = np.arange(0, n_flavors, 3)
    plot_hline_chart(ax, original, chainguard, rapidfort, flavors, highlight_min=True)
    
    plt.show()