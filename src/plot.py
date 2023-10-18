"""
Helper logic for creating figures.
"""


from typing import List, Tuple
from dataclasses import dataclass
import matplotlib
from matplotlib.axes import Axes
import seaborn as sns
import numpy as np
from src import utils


N_VENDORS = 3

# Vendor legend labels
BASELINE_LABEL = "Baseline"
RAPIDFORT_LABEL = "RapidFort"
CHAINGUARD_LABEL = "Chainguard"

# Vendor colors
BASELINE_COLOR = "#949494"
RAPIDFORT_COLOR = "#8dc7c7"
CHAINGUARD_COLOR = "#9745E6"

# Figure params
LINE_WIDTH = 1.2        # Width of mean lines
MARKER_SZ = 30          # Size of scatter points
YLABEL_FONT_SZ = 8      # Font size of the image types listed on the y axis
XLABEL_FONT_SZ = 10     # Font size of the x axis
LEGEND_FONT_SZ = 10     # Font size of the legend
TITLE_PADDING = 10      # Padding below the figure title


@dataclass
class MetricData:
    """
    Represents the data of a figure.

    @param baseline: A numpy array of baseline data
    @param rapidfort: A numpy array of rapidfort data
    @param chainguard: A numpy array of chainguard data
    @param image_types: A list of image types.

    All inputs must be the same length. The image type at index i is described
    by data at index i of the baseline, rapidfort, and chaingaurd arrays.

    For example, if the goal is to represent component counts,
    and image_types[4] = "nginx", then baseline[4], rapidfort[4], and chainguard[4]
    are the components counts for "nginx" of each vendor.
    """
    def __init__(self, baseline: np.ndarray, rapidfort: np.ndarray,
                 chainguard: np.ndarray, image_types: List[str]):
        utils.check_equal_size([baseline, rapidfort, chainguard, image_types])
        self.baseline = baseline
        self.rapidfort = rapidfort
        self.chainguard = chainguard
        self.image_types = image_types


    def vendors_iter(self) -> Tuple(np.ndarray, str, str):
        """
        @returns an iter over the data, label, and color of each vendor

        Each item is a Tuple of the for (data, label, color)
        """
        items = [
            (self.baseline, BASELINE_LABEL, BASELINE_COLOR),
            (self.rapidfort, RAPIDFORT_LABEL, RAPIDFORT_COLOR),
            (self.chainguard, CHAINGUARD_LABEL, CHAINGUARD_COLOR)]
        return iter(items)
    
    def num_vendors(self) -> int:
        """
        @returns the number of vendors
        """
        return N_VENDORS

    def num_image_types(self) -> int:
        """
        @returns the number of image types
        """
        return len(self.image_types)


def _apply_style(ax: Axes):
    """
    Applies a common style to the provided axis.

    @param ax: The matplotlib axis to apply styling to.
    """
    sns.despine(ax=ax)
    matplotlib.rcParams["font.family"] = "serif"


def plot_hline_chart(ax: Axes, data: MetricData, title: str,
                     xlabel: str):
    """
    Plots vendor data as a multicolored scatter plot where the y axis
    is image type and each color represents a different vendor.

    @param ax: Axis for plotting
    @param data: a MetricData object of the data to use in the figure
    @param title: The title of the figure
    @param xlabel: The x axis label of the figure.
    """
    n_types = data.num_image_types()

    _apply_style(ax)
    
    is_labeled = False # Control flag to ensure vendors only get labeled once each
    # Loop over each y value (image type index)
    for y in range(data.num_image_types()):
        # Loop over each vendor. We zip this with the label and color for each vendor.
        for x, label, color in data.vendors_iter():
            if not is_labeled:
                ax.scatter(x, y, color=color, s=MARKER_SZ,
                           label=label)
                ax.vlines(np.mean(x), 0, n_types-1, linewidth=LINE_WIDTH,
                          color=color, zorder=-1, linestyle="--")
            else:
                ax.scatter(x, y, color=color, s=MARKER_SZ)
        is_labeled = True

    # Set title and legend
    ax.set_title(title, pad=TITLE_PADDING)
    ax.legend(loc='upper right', ncols=1, fontsize=LEGEND_FONT_SZ)

    # Apply font size to x axis ticks
    xticks = ax.get_xticks()
    if xticks[0] % 1 != 0: # Preseve decimal in float labels
        xticks_labels = [str(t) for t in xticks]
    else:
        xticks_labels = [str(int(t)) for t in xticks]
    ax.set_xticks(xticks, xticks_labels, fontsize=XLABEL_FONT_SZ)

    # Set min x axis value to 0
    ax.margins(x=0)

    # Label x axis
    ax.set_xlabel(xlabel, fontsize=XLABEL_FONT_SZ)

    # Set y axis ticks to image types
    ax.set_yticks(np.arange(n_types), data.image_types, fontsize=YLABEL_FONT_SZ)
