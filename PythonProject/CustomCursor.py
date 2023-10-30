import numpy as np
from matplotlib import pyplot as plt


class CustomCursor(object):
    def __init__(self, axes, color, xlimits, ylimits):
        self.gid = None
        self.items = np.zeros(shape=(len(axes), 3), dtype=object)
        self.col = color
        self.focus = 0
        i = 0
        for ax in axes:
            axis = ax
            axis.set_gid(i)
            lx = ax.axvline(ymin=ylimits[0], ymax=ylimits[1], color=color, linestyle='--', linewidth=1)
            ly = ax.axhline(xmin=xlimits[0], xmax=xlimits[1], color=color, linestyle='--', linewidth=1)
            item = list([axis, lx, ly])
            self.items[i] = item
            i += 1

    def show_xy(self, event):
        if event.inaxes:
            self.focus = event.inaxes.get_gid()
            for ax in self.items[:, 0]:
                self.gid = ax.get_gid()
                for lx in self.items[:, 1]:
                    lx.set_xdata(event.xdata)
                if event.inaxes.get_gid() == self.gid:
                    self.items[self.gid, 2].set_ydata(event.ydata)
                    self.items[self.gid, 2].set_visible(True)
        plt.draw()

    # noinspection PyUnusedLocal
    def hide_y(self, event):
        for ax in self.items[:, 0]:
            if self.focus == ax.get_gid():
                self.items[self.focus, 2].set_visible(False)
