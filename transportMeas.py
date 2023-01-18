import os
import time
import csv
import numpy as np
#from Res_Meas.base_module import OneDSweeper, instr_list, TwoDSweeper
#from Res_Meas import utilities as util
from spectroscopyMeas.base_module import OneDSweeper, instr_list, TwoDSweeper
from spectroscopyMeas import utilities as util
from matplotlib import animation
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import itertools

class OneDMeas(OneDSweeper):

    name = 'OneDMeas'

    def __init__(self, parent_dir, date, instrs, settings=None):
        super(OneDSweeper, self).__init__(parent_dir, date)

        self.set_instr_list(instrs = instrs, settings=settings)


    def set_instr_list(self, instrs, settings=None):
        self.instr_list = instr_list(instrs)
        self.set_sweeper()
        self.set_settings(settings=settings)

    def set_sweeper(self):
        sense_keys = []
        numofsense, numofbias, numofsweep = 0, 0, 0
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k:
                numofsweep += 1
            if 'bias' in k:
                numofbias += 1
            if 'sense' in k:
                numofsense += 1
                sense_keys.append(k)
        if numofsweep!=1:
            print('You do not just have one sweep instrument. Check your instr_list!')    
            if numofsense == 0:
                print('You do not have any sense instrument. Check your instr_list!')
        self.numofsense = numofsense
        self.numofbias = numofbias
        self.init_data_holders(sense_keys=sense_keys)


    def add_instr(self, instr, val=None):
        self.instr_list.add_instr(instr)
        self.set_sweeper()
        self.update_settings(instr, val=val)


    def delete_instr(self, instr):
        if instr in self.instr_list.instr_list.values():
            self.set_sweeper()
            self.update_settings(instr, mode='delete')
        else:
            print('instr not present in instr_list')

    def update_func(self, instr, func, val=None):
        if instr in self.instr_list.instr_list.values():
            if instr.func in self.settings.keys():
                self.settings.pop(instr.func)
            instr.set_func(func=func)
            self.set_sweeper()
            self.update_settings(instr, val=val)		

    def set_settings(self, settings=None):
        if settings is None:
            self.create_empty_settings()
            print('Make sure to update your settings!')
        else:
            self.settings = settings
        self.write_settings()

    def create_empty_settings(self):
        settings = {}
        for k in self.instr_list.instr_list.keys():
            if 'bias' in k or 'sweep' in k:
                settings[k] = None
        self.settings = settings

    def update_settings(self, instr, val=None, mode='modify'):
        if mode == 'modify':
            if instr in self.instr_list.instr_list.values():
                if not instr.func in self.settings.keys() and 'sense' not in instr.func:
                    print('new instr added to the settings')
                    self.settings[instr.func] = val
            else:
                print('This instrument is not in your instr_list. Make sure to add it first.')
       	if mode == 'delete':
            if instr.func in self.settings.keys():
                self.settings.pop(instr.func)
            print('instr deleted from the settings')
        self.write_settings()	


    def write_settings(self):
        for k in self.settings.keys():
            if 'sweep' in k:
                self.sweep_param[k] = self.settings[k]
            if 'bias' in k:
                try:
                    self.instr_list.instr_list[k].write_val(self.settings[k])
                except KeyError:
                    print('instr_list does not match settings')
        self.set_frames()


    def save_settings(self, fileName='instr_settings', path=None, counter=None):
        if not path:
            path = self.path
        if not counter:
            counter = self.counter
        path = path + '\\' + str(counter)
        self.instr_list.save_settings(path, fileName=fileName)

    def get_sense_instr(self, i):
        keys = self.get_sense_keys()
        return self.instr_list.instr_list[keys[i]]

    def get_bias_instr(self, i):
        bias_instrs = []
        for k in self.instr_list.instr_list.keys():
            if 'bias' in k:
                bias_instrs.append(self.instr_list.instr_list[k])
        return bias_instrs[i]

    def get_sweep_instr(self):
        keys = self.get_sense_keys()
        return self.instr_list.instr_list[keys[i]]

    def sense(self, i):
        instr = self.get_sense_instr(i)
        return instr.read_val()

    def update_sweep(self, i):
        super().update_sweep(i=i)
        self.get_sweep_instr().write_val(self.rt_x[i])

    def update_sense(self, i, save_data=True):
        for j in range(self.numofsense):
            self.get_sense_data()[j][i] = self.sense(j)
        if save_data:
            self.save_zdata()


    def update_axes(self):
        sweep_key, = self.get_sweep_keys()
        sense_keys = self.get_sense_keys()
        i = 0
        last = len(self.axes)
        for ax in self.axes:
            ax.set_xlabel('{} [{}]'.format(sweep_key, self.instr_list.instr_list[sweep_key].unit))
            ax.set_ylabel('{} [{}]'.format(sense_keys[i], self.instr_list.instr_list[sense_keys[i]].unit))
            i+=1
        self.fig.suptitle('Trace Live Plot')


    def on(self):
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k or 'bias' in k or 'sense' in k:
                self.instr_list.instr_list[k].on()

    def off(self):
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k or 'bias' in k or 'sense' in k:
                self.instr_list.instr_list[k].off()

    def init_func(self, fig=None, axes=None, save_data=True): 
        super().init_func(fig=fig, axes=axes, save_data=save_data)
        self.on()


class TwoDMeas(TwoDSweeper, OneDMeas):

    name = 'TwoDMeas'

    def __init__(self, parent_dir, date, instrs, settings=None):
        OneDMeas.__init__(parent_dir, date, date, instrs, settings=settings)


    def set_sweeper(self):
        sense_keys, sweep_keys = [], []
        numofsense, numofbias, numofsweep = 0, 0, 0
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k:
                numofsweep += 1
            if 'bias' in k:
                numofbias += 1
            if 'sense' in k:
                numofsense += 1
                sense_keys.append(k)
        if numofsweep!=2:
            print('You do not just have two sweep instruments. Check your instr_list!')    
        if numofsense == 0:
            print('You do not have any sense instrument. Check your instr_list!')
        self.numofsense = numofsense
        self.numofbias = numofbias
        self.init_data_holders(sense_keys=sense_keys)

    def update_axes(self):
        i = 0
        last = len(self.axes)
        for ax in self.axes:
            i += 1
            if i == 1:
                ax.set_title('Line Trace')
            if i == 2:
                ax.set_title('Color Map')
            if i%2 == 1:
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sense_keys()[i//2], self.instr_list.instr_list[self.get_sense_keys()[i//2]].unit))
            if i%2 == 0:
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sweep_keys()[1], self.instr_list.instr_list[self.get_sweep_keys()[1]].unit))
                #ax.set_ylabel('Sense{}'.format(i//2))   


    def update_sweep(self, i):
        super().update_sweep(i)
        self.get_sweep_instr(0).write_val(self.rt_x[i%len(self.cols)])
        self.get_sweep_instr(1).write_val(self.rt_y[i//len(self.cols)])

    def update_sense(self, i, save_data=True):
        r, c = i//self.cols, i%self.cols
        for j in range(self.numofsense):
            self.get_sense_data()[j][r][c] = self.sense(j)
        if save_data:
            self.save_zdata()

    def init_func(self, fig=None, axes=None, save_data=True): 
        super().init_func(fig=fig, axes=axes, save_data=save_data)
        self.on()
