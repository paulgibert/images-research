"""
Things to visualize:

1) Per image, a bar graph where the x axis is severity,
   y axis is num vulns, and colors are different regs
   chainguard blue
   rapidfort red
   docker light gray
   alpine pink
"""

from typing import Tuple, List
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.axes import Axes
import pandas as pd
import numpy as np


RESULTS_PATH = "results.csv"
SEVERITIES = ["unknown", "negligible", "low", "medium", "high", "critical"]
DEFAULT_FIGSIZE = (10, 10)
DEFAULT_COLORS = ["blue", "red", "green", "gray"]


def get_registry_names(df: pd.DataFrame) -> List[str]:
    names = []
    for col in df.columns:
        if "critical" in col:
            names.append(col.split("-")[0])
    return names


def get_image_names(df: pd.DataFrame) -> List[str]:
    return list(df["image-name"])


def get_registry_vulnerability_counts(registry: str, df: pd.DataFrame) -> np.array:
    counts = df[[f"{registry}-{sev}" for sev in SEVERITIES]]
    return np.array(counts)


def get_index_offset(bar_width: float, bar_spacing: float) -> float:
    return bar_width / bar_spacing


def get_bar_width(n_bars: int, index: int,
                  bar_spacing: float=0.05,
                  tick_padding: float=0.2) -> Tuple[float, float]:
    """

        c  ||          ||  
        ||a||   b   || ||   
    ------|-----------|------
    
    a - bar_spacing
    b - tick_padding
    c - bar_width (calculated)

    (bar_width + bar_spacing) * n_bars + (2 * tick_padding) = 1

    therefore:

    bar_width = ((1 - (2 * tick_padding)) / n_bars) - bar_spacing

    """

    bar_width = ((1 - (2 * tick_padding)) / n_bars) - bar_spacing
    offset = (bar_width + bar_spacing) * index

    return bar_width, offset


def _plot_image_vulnerabilties_by_registry(ax: Axes, registry: str, index: int, df: pd.DataFrame,
                  color: str):
    counts = get_registry_vulnerability_counts(registry, df)
    
    bar_x = np.arange(len(get_image_names(df)))
    n_registries = len(get_registry_names(df))
    n_severity_levels = counts.shape[1]
    
    bar_width, offset = get_bar_width(n_registries, index)

    alphas = np.linspace(1 / n_severity_levels, 1, n_severity_levels)

    # Manually plot the first severity level of each images
    ax.bar(bar_x + offset, counts[:,0], bar_width,
           color=color, alpha=alphas[0])
    
    # Iteratively plot the remaining severity levels
    for i in range(1, n_severity_levels):
        bottom = np.sum(counts[:, 0:i], axis=1)
        label = registry if i == n_severity_levels - 1 else None
        ax.bar(bar_x + offset, counts[:,i], bar_width,
               bottom=bottom, color=color,
               alpha=alphas[i],
               label=label)


def plot_image_vulnerabilities_by_registry(df,
                                           figsize: Tuple[int]=None,
                                           colors: List[str]=None):
    regs = get_registry_names(df)
    images = get_image_names(df)

    if figsize is None:
        figsize = DEFAULT_FIGSIZE

    if colors is None:
        colors = DEFAULT_COLORS
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot each registry
    for i in range(len(regs)):
        r = regs[i]
        color = colors[i % len(colors)]
        _plot_image_vulnerabilties_by_registry(ax, r, i, df,
                      color=color)

    # Define figure title and labels
    ax.set_title("Image Vulnerabilities by Registry")
    ax.legend(loc='upper left', ncols=1)
    ax.set_xlabel("Image")
    ax.set_ylabel("Number of Vulnerabilities")
    ax.set_xticks(np.arange(len(images)) + 0.25, images)

    fig.tight_layout()
    plt.show()


def get_registry_image_sizes_MB(registry: str, df: pd.DataFrame) -> float:
    return np.array(df[f"{registry}-img-sz"]) / 1000000


def _plot_image_size_by_registry(ax: Axes, registry: str, index: int, df: pd.DataFrame,
                                 color: str):
    image_sizes = get_registry_image_sizes_MB(registry, df)
    
    bar_x = np.arange(len(get_image_names(df)))
    n_registries = len(get_registry_names(df))

    bar_width, offset = get_bar_width(n_registries, index)

    ax.bar(bar_x + offset, image_sizes, bar_width,
           color=color, label=registry)


def plot_image_size_by_registry(df,
                                figsize: Tuple[int]=None,
                                colors: List[str]=None):
    regs = get_registry_names(df)
    images = get_image_names(df)

    if figsize is None:
        figsize = DEFAULT_FIGSIZE

    if colors is None:
        colors = DEFAULT_COLORS
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot each registry
    for i in range(len(regs)):
        r = regs[i]
        color = colors[i % len(colors)]
        _plot_image_size_by_registry(ax, r, i, df, color)

    # Define figure title and labels
    ax.set_title("Image Size by Registry")
    ax.legend(loc='upper left', ncols=1)
    ax.set_xlabel("Image")
    ax.set_ylabel("Size (MB)")
    ax.set_xticks(np.arange(len(images)) + 0.25, images)

    fig.tight_layout()
    plt.show()


def main():
    # TODO: Figure out how to handle NA values
    df = pd.read_csv(RESULTS_PATH)

    plot_image_vulnerabilities_by_registry(df)
    plot_image_size_by_registry(df)

if __name__ == "__main__":
    main()