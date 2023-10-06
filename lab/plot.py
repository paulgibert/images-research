from typing import Dict, List, Iterable
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np


def plot_hbar_groups(ax: Axes, members: Dict[str, any],
                     groups: List[str],
                     colors: Dict[str, any]):
    bar_width = .1

    y = np.arange(len(groups))

    for i, (name, x) in enumerate(members.items()):
        labeled = False
        clr = colors[name]
        offset = bar_width * i
        for _y, _x in zip(range(len(groups)), x):
            left = 0
            if type(_x) is list:

                if type(clr) is not list:
                    raise TypeError("Must provide a list of colors for multi-color bar displays.")
                
                for __x, _clr in zip(_x, clr):
                    label = None if labeled else name
                    ax.barh(_y + offset, __x, bar_width, left=left, color=_clr, label=label)
                    labeled = True
                    left += __x

            else:
                label = None if labeled else name
                ax.barh(_y + offset, _x, bar_width, color=clr, label=label)
                labeled = True
    
    ax.set_yticks(y, groups)
    ax.legend(loc='upper right', ncols=1)


if __name__ == "__main__":
    fig, ax = plt.subplots()
    members = {
        "chainguard": [[1, 5], 5, 10],
        "alpine": [[2, 6], 6, 12],
        "rapidfort": [[3, 3], 7, [2, 5, 6, 2, 1, 0]],
        "slim.ai": [[4, 1], 8, 16]
    }
    groups = ["redis", "mongodb", "nginx"]
    colors = {
        "chainguard": ["lightblue", "blue"],
        "alpine": ["pink", "red"],
        "rapidfort": ["red", "black"],
        "slim.ai": ["yellow"]
    }

    plot_hbar_groups(ax, members, groups, colors)
    plt.show()