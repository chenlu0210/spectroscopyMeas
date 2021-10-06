# -*- coding: utf-8 -*-
"""
Created on Sun Sep 26 21:55:33 2021

@author: liu_c
"""
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import utilities as util
fig, line_ax1, line_ax2, color_ax1, color_ax2, line_ax3, line_ax4, cax1, cax2 = util.initialize_Plot()

a = np.linspace(0,3,4)
mags, phases = [], []
Qis, Qls = [], []

def animate(i):
    line1 = line_ax1.plot(a, a)
    line2 = line_ax2.plot(a, a+i)
    mags.append((a+4).tolist())
    phases.append(a.tolist())
    Qis.append(a[i])
    Qls.append(a[i]+1)
    print(a[:i+1])
    print(mags)
    cmap1 = util.colorPlot(fig, color_ax1, cax1, mags, a, a[:i+1])
    cmap2 = util.colorPlot(fig, color_ax2, cax2, phases, a, a[:i+1])

    line3 = line_ax3.plot(a[:i+1], Qis, 'r*')
    line4 = line_ax4.plot(a[:i+1], Qls, 'r*')
    return line1, line2, line3, line4, cmap1, cmap2, 

def init_func():
    mags, phases = [], []
    Qis, Qls = [], []
    
ani = animation.FuncAnimation(fig, animate, frames=len(a), repeat=False, init_func=init_func, interval=2000)
plt.tight_layout()
plt.show()


