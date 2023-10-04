from typing import List, Tuple, Dict
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np


FIGSIZE = (15, 15)
BYTES_PER_MB = 1000000
COLORS = ["blue", "red", "green", "gray", "yellow"]


def get_registry_y(registry: str, images: List[str], df: pd.DataFrame) -> np.ndarray:
    n_images = len(images)
    bar_y = np.zeros((n_images))
    
    for img_i, img in enumerate(images):
        rmask = df["registry-name"] == registry
        imask = df["image-name"] == img
        sz = df[rmask & imask]["image-size"]
        if sz.shape[0] == 0:
            bar_y[img_i] = 0
        else:
            bar_y[img_i] = int(sz.iloc[0] / BYTES_PER_MB)
    
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
                  color: str):    
    n_images = len(images)
    bar_x = np.arange(n_images)
    
    # Manually plot the first severity level of each images
    ax.bar(bar_x+offset, y_data, bar_width,
           color=color, label=registry)

def main():
    # TODO change this to arg parse
    parser = argparse.ArgumentParser(
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
        color = COLORS[i % len(COLORS)]
        plot_registry(ax, reg, images,
                      y_data, bar_width, offset,
                      color)
       
    # Define figure title and labels
    ax.set_title("Image Size by Registry")
    ax.legend(loc='upper left', ncols=1)
    ax.set_xlabel("Image")
    ax.set_ylabel("Size (MB)")
    ax.set_xticks(np.arange(len(images)) + 0.25, images)
    ax.set_xticklabels(images, rotation=45)

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()