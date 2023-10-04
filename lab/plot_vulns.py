from typing import List, Tuple, Dict
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np


FIGSIZE = (15, 15)
SEVERITIES = ["unknown",
              "negligible",
              "low",
              "medium",
              "high",
              "critical"]
COLOR_SCHEMES = [
    {"turquoise": [
        "lightcyan",
        "paleturquoise",
        "turquoise",
        "lightseagreen",
        "teal",
        "darkslategray"]},
    {"firebrick": [
        "mistyrose",
        "lightcoral",
        "indianred",
        "firebrick",
        "maroon",
        "dimgrey"]},
    {"gold": [
        "papayawhip",
        "navajowhite",
        "gold",
        "tan",
        "goldenrod",
        "darkgoldenrod"]},
    {"seagreen": [
        "aquamarine",
        "mediumspringgreen",
        "mediumseagreen",
        "seagreen",
        "green",
        "darkgreen"]},
    {"violet": [
        "thistle",
        "plum",
        "violet",
        "mediumorchid",
        "darkviolet",
        "indigo"]},
    {"cornflowerblue": [
        "lavender",
        "lightsteelblue",
        "cornflowerblue",
        "royalblue",
        "mediumblue",
        "navy"]},
    {"darkgray": [
        "gainsboro",
        "silver",
        "darkgray",
        "gray",
        "dimgray",
        "black"]},
]

COLOR_SCHEMES_SIMPLE = [
    {"turquoise": [
        "turquoise",
        "turquoise",
        "turquoise",
        "turquoise",
        "turquoise",
        "darkslategray"]},
    {"firebrick": [
        "firebrick",
        "firebrick",
        "firebrick",
        "firebrick",
        "firebrick",
        "dimgrey"]},
    {"gold": [
        "gold",
        "gold",
        "gold",
        "gold",
        "gold",
        "darkgoldenrod"]},
    {"seagreen": [
        "seagreen",
        "seagreen",
        "seagreen",
        "seagreen",
        "seagreen",
        "darkgreen"]},
    {"violet": [
        "violet",
        "violet",
        "violet",
        "violet",
        "violet",
        "indigo"]},
    {"cornflowerblue": [
        "cornflowerblue",
        "cornflowerblue",
        "cornflowerblue",
        "cornflowerblue",
        "cornflowerblue",
        "navy"]},
    {"darkgray": [
        "darkgray",
        "darkgray",
        "darkgray",
        "darkgray",
        "darkgray",
        "black"]},
]

def get_registry_y(registry: str, images: List[str], df: pd.DataFrame) -> np.ndarray:
    n_severities = len(df["severity"].unique())
    n_images = len(images)
    bar_y = np.zeros((n_severities, n_images))
    
    for img_i, img in enumerate(images):
        rmask = df["registry-name"] == registry
        imask = df["image-name"] == img
        counts = df[rmask & imask]["severity"].value_counts()
        for sev_i, sev in enumerate(SEVERITIES):
            if sev not in counts.keys():
                bar_y[sev_i, img_i] = 0
            else:
                bar_y[sev_i, img_i] = counts[sev]
    
    return bar_y


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


def plot_registry(ax: Axes,
                  registry: str,
                  images: List[str],
                  y_data: np.ndarray,
                  bar_width: float,
                  offset: float,
                  color_scheme: Dict[str, List[str]]):    
    n_images = len(images)
    n_severities = len(SEVERITIES)

    bar_x = np.arange(n_images)

    label_color = list(color_scheme.keys())[0]
    colors = list(color_scheme.values())[0]
    
    # Manually plot the first severity level of each images
    ax.bar(bar_x+offset, y_data[0,:], bar_width,
           color=colors[0])

    # Iteratively plot the remaining severity levels
    for i in range(1, n_severities):
        bottom = np.sum(y_data[0:i, :], axis=0)
        label = registry if colors[i] == label_color else None
        color = colors[i] if label is None else label_color
        ax.bar(bar_x+offset, y_data[i, :], bar_width,
               bottom=bottom, color=color, label=label)


def main():
    # TODO change this to arg parse
    parser = argparse.ArgumentParser(
                    prog='parse.py',
                    description='Produces datasets from parsed scan reports.')
    
    parser.add_argument("--dataset", "-d",
                        required=True,
                        help="The dataset to build the vizualization from.")
    
    dataset = parser.parse_args().dataset
    df = pd.read_csv(dataset)

    registries = df["registry-name"].unique()
    n_registries = len(registries)
    
    images = df["image-name"].unique()

    fig, ax = plt.subplots(figsize=FIGSIZE)

    for i, reg in enumerate(registries):
        y_data = get_registry_y(reg, images, df)
        bar_width, offset = get_bar_width(n_registries, i)
        color_scheme = COLOR_SCHEMES[i % len(COLOR_SCHEMES)]
        plot_registry(ax, reg, images,
                      y_data, bar_width, offset,
                      color_scheme)
       
    # Define figure title and labels
    ax.set_title("Image Vulnerabilities by Registry")
    ax.legend(loc='upper left', ncols=1)
    ax.set_xlabel("Image")
    ax.set_ylabel("Number of Vulnerabilities")
    ax.set_xticks(np.arange(len(images)) + 0.25, images)
    ax.set_xticklabels(images, rotation=45)

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()