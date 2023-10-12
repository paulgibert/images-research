import os
import sys

# Add parent dir to path
sys.path.append("/".join(os.path.dirname(__file__).split("/")[0:-1]))

from typing import Tuple
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import seaborn as sns
import numpy as np
from src.plot import plot_hline_chart


def get_column(df: pd.DataFrame, provider: str, column: str) -> np.ndarray:
    data = df[df["image_provider"] == provider]
    return np.array(
        data.sort_values(by=["image_flavor"])[column])


def make_fig(df: pd.DataFrame, column: str) -> Tuple[Figure, Axes]:
    import matplotlib as mpl
    mpl.rcParams["font.family"] = "serif"
    fig, ax = plt.subplots(figsize=(8,6))
    column = "n_vulnerabilities"
    flavors = df["image_flavor"].unique()

    org = get_column(df, "original", column)
    cg = get_column(df, "chainguard", column)
    rf = get_column(df, "rapidfort", column)

    plot_hline_chart(ax, org, cg, rf, flavors)
    return fig, ax


def make_n_vulns_fig(df: pd.DataFrame, out_path: str):
    fig, ax = make_fig(df, "n_vulnerabilities")

    sns.despine(ax=ax, offset=5)
    ax.set_title("Number of Vulnerabilities Per Image", pad=10)
    ax.set_xlabel("Number of Vulnerabilities")
    xticks = np.arange(0, 300, 50)
    ax.set_xticks(xticks, [str(int(t)) for t in xticks], fontsize=10)
    ax.set_xlabel("Number of Vulnerabilities", fontsize=10)

    fig.tight_layout()


def main():

    df = pd.read_csv("data/datasets/agg.csv")
    make_n_vulns_fig(df, "n_vulns.png")

    # import matplotlib as mpl
    # from matplotlib.font_manager import get_font_names
    # for font in get_font_names():
        
    #     print(font)
    #     plt.show()
    plt.show()

if __name__ == "__main__":
    main()