from typing import Dict, List, Iterable
import matplotlib
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


def plot_hlines(ax: Axes, members: Dict[str, float], control_member: str, groups: List[str],
                colors: Dict[str, str]):
    n_groups = len(groups)

    # Sort groups by control_member size
    xi = np.argsort(members[control_member])

    # Plot hlines for control memeber
    y = np.arange(n_groups)
    xmax = np.array(members[control_member])[xi]
    clr = colors[control_member]
    ax.hlines(y, 0, xmax, color=clr, zorder=-1)
    ax.scatter(xmax, y, color=clr, marker="|", zorder=-1)

    # Plot points for each non-control member
    for mem in members.keys():
        # Skip control member - already plotted
        if mem == control_member:
            continue
        x = np.array(members[mem])[xi]
        clr = colors[mem]
        ax.scatter(x, y, color=clr, label=mem)
    
    ax.set_yticks(y, groups)
    ax.legend(loc='lower right', ncols=1)


def plot_stack(ax: Axes, members: Dict[str, float], control_member: str, groups: List[str],
                colors: Dict[str, str]):
    n_groups = len(groups)

    # Sort groups by control_member size
    x = np.arange(n_groups)
    yi = np.argsort(members[control_member])

    # Plot points for each non-control member
    labeled = False
    for i, x in enumerate(yi):
        y = [mem_y[x] for mem_y in members.values()]
        zorders = np.argsort(y)
        for mem, _y, z in zip(list(members.keys()), y, zorders):
            clr = colors[mem]
            label = None if labeled else mem
            ax.barh(i, _y, height=.9, color=clr, zorder=-z, label=label)
        labeled = True
    
    ax.set_yticks(yi, groups, fontsize=8)
    ax.legend(loc='lower right', ncols=1)

    

if __name__ == "__main__":
    fig, ax = plt.subplots()
    members = {
        "chainguard": [3, 7, 4],
        "rapidfort": [12, 21, 15],
        "original": [50, 123, 92]
    }
    groups = ["redis", "mongodb", "nginx"]
    colors = {
        "chainguard": "purple",
        "rapidfort": "red",
        "original": "grey"
    }
    
    plot_stack(ax, members, "original", groups, colors)
    plt.show()