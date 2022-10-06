# -*- coding: utf-8 -*-
"""
Created on Sun Sep 26 21:55:33 2021

@author: liu_c
"""
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from Res_Meas import utilities as util

class test_class:
    def __init__(self):
        self.name = "blah"
        
    def test(self, powers, powerSweep, vna, vna_settings):
        fig, line_ax1, line_ax2, color_ax1, color_ax2, line_ax3, line_ax4, cax1, cax2 = util.initialize_Plot()

        frames = len(powers)

        Qis, Qi_errs = [], []
        Qls, Ql_errs = [], []
        mags = []
        phases = []

        def init_func():
            Qis, Qi_errs = [], []
            Qls, Ql_errs = [], []
            mags = []
            phases = []

        freqs = util.sweep(vna_settings['center'], vna_settings['span'], vna_settings['npts'])
        freqs = util.freq2GHz(freqs)

        def animate(i):

            print(i)
            p = powers[i]
            vna_settings['power'] = p
            powerSweep.write_vna_settings(vna_settings)
            mag, phase = vna.channels.S21.trace_mag_phase()
            line1 = line_ax1.plot(freqs, mag)
            line2 = line_ax2.plot(freqs, phase)
            mags.append(mag)
            phases.append(phase)

            cax1.cla()
            cax2.cla()
            cmap1 = util.colorPlot(fig, color_ax1, cax1, mags, freqs, powers[:i+1])
            cmap2 = util.colorPlot(fig, color_ax2, cax2, phases, freqs, powers[:i+1])

            if check_Q:
                Qi, Qierr, Ql, Qlerr = util.find_Q(freqs, mag, phase)
                Qis.append(Qi)
                Qi_errs.append(Qierr)
                Qls.append(Ql)
                Ql_errs.append(Qlerr)
                line3 = line_ax3.errorbar(powers[:i+1], Qls, yerr=Ql_errs)
                line4 = line_ax4.errorbar(powers[:i+1], Qis, yerr=Qi_errs)
            return line1, line2, cmap1, cmap2, line3, line4, 


        ani = animation.FuncAnimation(fig, animate, frames=frames, init_func=init_func, repeat=False)
        plt.tight_layout()
        plt.show()
        return ani