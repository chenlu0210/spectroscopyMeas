import os
import time
import csv
import numpy as np
from Res_Meas.base_module import OneDSweeper, instr_list, TwoDSweeper
from Res_Meas import utilities as util
from matplotlib import animation
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import itertools

class OneDMeas(OneDSweeper):

    name = 'OneDMeas'

    def __init__(self, parent_dir, date, instrs, settings=None):
        super(OneDSweeper, self).__init__(parent_dir, date)
        self.set_instr_list(instrs = instrs)
        self.set_settings(settings = settings)
        self.init_data_holders()


    def set_instr_list(self, instrs):
        self.instr_list = instr_list(instrs)
        numofsense, numofbias, numofsweep = 0, 0, 0
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k:
                numofsweep += 1
            if 'bias' in k:
                numofbias += 1
            if 'sense' in k:
                numofsense += 1
        self.numofsense = numofsense
        self.numofbias = numofbias
        if numofsweep!=1:
            print('You do not just have one sweep instrument. Check your instr_list!')      


    def set_settings(self, settings=None):
        if settings is None:
            self.create_empty_settings()
        else:
            self.settings = settings
        self.write_settings()

    def create_empty_settings(self):
        settings = {}
        for k in self.instr_list.instr_list.keys():
            if 'bias' in k or 'sweep' in k:
                settings[k] = None
        self.settings = settings


    def write_settings(self):
        for k in self.settings.keys():
            if 'sweep' in k:
                self.set_sweep_param(sweep_param=self.settings[k])
            if 'bias' in k:
                try:
                    self.instr_list.instr_list[k].write_val(self.settings[k])
                except KeyError:
                    print('instr_list does not match settings')


    def save_settings(self, fileName='instr_settings', path=None, counter=None):
        if not path:
            path = self.path
        if not counter:
            counter = self.counter
        path = path + '\\' + str(counter)
        self.instr_list.save_settings(path, fileName=fileName)

    def get_sense_instr(self, i):
        if self.numofsense==1:
            for k in self.instr_list.instr_list.keys():
                if 'sense' in k:
                    return self.instr_list.instr_list[k]
        else:
            for k in self.instr_list.instr_list.keys():
                if 'sense' in k and str(i) in k:
                    return self.instr_list.instr_list[k]

    def get_bias_instr(self, i):
        for k in self.instr_list.instr_list.keys():
            if 'bias' in k and str(i) in k:
                return self.instr_list.instr_list[k]

    def get_sweep_instr(self):
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k:
                return self.instr_list.instr_list[k]

    def sense(self, i):
        instr = self.get_sense_instr(i)
        return instr.read_val()

    def update_sweep(self, i):
        self.rt_x = self.sweep_param[:i+1]
        self.get_sweep_instr().write_val(self.sweep_param[i])

    def update_sense(self, i, save_data=True):
        for j in range(self.numofsense):
            self.sense_data[j][i] = self.sense(j+1)
        if save_data:
            self.save_zdata()

    # def update_plot(self, i, save_plot=True, figName='TracePlot'):
    #     lines = []
    #     for j in range(self.numofsense):
    #         lines.append(self.axes[j].plot(self.rt_x, self.sense_data[j][:i+1], label='{}'.format(i)))
    #         #self.axes[j].legend()

    #     if i == len(self.sweep_param) - 1:
    #         path = self.path + '\\' + str(self.counter)
    #         if save_plot:
    #             self.fig.savefig(path+'\\{}.pdf'.format(figName))

    #     return tuple(lines)

    # def update_data(self, i, save_data=True, save_plot=True):
    #     self.update_sweep(i)
    #     self.update_sense(i, save_data=save_data)
    #     lines = self.update_plot(i, save_plot=save_plot)
    #     if i == len(self.sweep_param) - 1:
    #         self.end_func()
    #     return lines


    # def init_func(self): 
    #     self.rt_x = []
    #     self.init_data_holders()
    #     self.start_time = time.time()

    def end_func(self):
        self.end_time = time.time()
        self.off()
        self.update_id()
        self.mark()
        log_info = [self.date, str(self.get_id()), self.markers[str(self.get_id())]]
        self.update_log(log_info)

    # def mark(self, id=None, message=None):
    #     if message is None:
    #         message = '{:2f}to{:2f}in{}steps'.format(np.min(self.sweep_param),np.max(self.sweep_param),len(self.sweep_param))
    #     super().mark(id, message)


    # def init_axes(self, fig=None, axes=None):
    #     if fig is None and axes is None:
    #         self.fig = plt.figure()
    #         self.axes = []
    #         for i in range(self.numofsense):
    #             self.axes.append(self.fig.add_subplot(self.numofsense,1,i+1))
    #     else:
    #         self.fig = fig
    #         self.axes = axes

    # def update_axes(self):
    #     i = 0
    #     last = len(self.axes)
    #     for ax in self.axes:
    #         i += 1
    #         ax.set_xlabel('X')
    #         ax.set_ylabel('Sense{}'.format(i))
    #     self.fig.suptitle('Trace Live Plot')     


    # def save_xdata(self, fileName='sweep_param', path=None, counter=None):
    #     if not path:
    #         path = self.path
    #     if not counter:
    #         counter = self.counter
    #     path = path + '\\' + str(counter) 
    #     np.savetxt(path+"\\{}.txt".format(fileName), self.sweep_param)

    # def save_zdata(self, fileName='sense_param', path=None, counter=None):
    #     if not path:
    #         path = self.path
    #     if not counter:
    #         counter = self.counter
    #     path = path + '\\' + str(counter)
    #     i = 0
    #     for data in self.sense_data:
    #         i+=1
    #         np.savetxt(path+"\\{}{}.txt".format(fileName,i), data)
    def on(self):
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k or 'bias' in k or 'sense' in k:
                self.instr_list.instr_list[k].on()

    def off(self):
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k or 'bias' in k or 'sense' in k:
                self.instr_list.instr_list[k].off()

    def live_plot(self, fig=None, axes=None, save_data=True, save_plot=True, instrs=None):
        self.write_path()
        util.check_dir(str(self.counter))
        if instrs is not None:
            self.set_instr_list(instrs)
        self.write_settings()
        self.init_axes(fig=fig, axes=axes)
        self.update_axes()
        if save_data:
            self.save_xdata()
            self.save_settings()
        self.on()
        self.ani = animation.FuncAnimation(self.fig, self.update_data, frames=len(self.sweep_param), repeat=False, init_func=self.init_func, blit=False, fargs=(save_data,save_plot,))
        plt.show(block=True)    


class TwoDMeas(TwoDSweeper):

    name = 'TwoDMeas'

    def __init__(self, parent_dir, date, instrs, settings=None):
        super(OneDSweeper, self).__init__(parent_dir, date)
        self.set_instr_list(instrs = instrs)
        self.set_settings(settings = settings)
        self.init_data_holders()


    def set_instr_list(self, instrs):
        self.instr_list = instr_list(instrs)
        numofsense, numofbias, numofsweep = 0, 0, 0
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k:
                numofsweep += 1
            if 'bias' in k:
                numofbias += 1
            if 'sense' in k:
                numofsense += 1
        self.numofsense = numofsense
        self.numofbias = numofbias
        if numofsweep!=2:
            print('You do not just have two sweep instruments. Check your instr_list!')     


    def set_settings(self, settings=None):
        if settings is None:
            self.create_empty_settings()
        else:
            self.settings = settings
        self.write_settings()

    def create_empty_settings(self):
        settings = {}
        for k in self.instr_list.instr_list.keys():
            if 'bias' in k or 'sweep' in k:
                settings[k] = None
        self.settings = settings


    def write_settings(self):
        for k in self.settings.keys():
            if 'sweep' in k and '1' in k:
                sweep_param1 = self.settings[k]
            if 'sweep' in k and '2' in k:
                sweep_param2 = self.settings[k]
            if 'bias' in k:
                try:
                    self.instr_list.instr_list[k].write_val(self.settings[k])
                except KeyError:
                    print('instr_list does not match settings')
        self.set_sweep_param(sweep_param1=sweep_param1, sweep_param2=sweep_param2)


    def save_settings(self, fileName='instr_settings', path=None, counter=None):
        if not path:
            path = self.path
        if not counter:
            counter = self.counter
        path = path + '\\' + str(counter)
        self.instr_list.save_settings(path, fileName=fileName)

    def get_sense_instr(self, i):
        if self.numofsense==1:
            for k in self.instr_list.instr_list.keys():
                if 'sense' in k:
                    return self.instr_list.instr_list[k]
        else:
            for k in self.instr_list.instr_list.keys():
                if 'sense' in k and str(i) in k:
                    return self.instr_list.instr_list[k]

    def get_bias_instr(self, i):
        for k in self.instr_list.instr_list.keys():
            if 'bias' in k and str(i) in k:
                return self.instr_list.instr_list[k]

    def get_sweep_instr(self, i):
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k and str(i) in k:
                return self.instr_list.instr_list[k]

    def sense(self, i):
        instr = self.get_sense_instr(i)
        return instr.read_val()

    def update_sweep(self, i):
        self.rt_x = self.sweep_param1[:i%len(self.sweep_param1)+1]
        self.rt_y = self.sweep_param2[:i//len(self.sweep_param1)+1]
        self.get_sweep_instr(1).write_val(self.sweep_param1[i%len(self.sweep_param1)])
        self.get_sweep_instr(2).write_val(self.sweep_param2[i//len(self.sweep_param1)])

    def update_sense(self, i, save_data=True):
        r, c = i//len(self.sweep_param1), i%len(self.sweep_param1)
        for j in range(self.numofsense):
            self.sense_data[j][r][c] = self.sense(j+1)
        if save_data:
            self.save_zdata()


    def end_func(self):
        self.end_time = time.time()
        self.off()
        self.update_id()
        self.mark()
        log_info = [self.date, str(self.get_id()), self.markers[str(self.get_id())]]
        self.update_log(log_info)


    def live_plot(self, fig=None, axes=None, save_data=True, save_plot=True, instrs=None):
        self.write_path()
        util.check_dir(str(self.counter))
        if instrs is not None:
            self.set_instr_list(instrs)
        self.write_settings()
        self.init_axes(fig=fig, axes=axes)
        self.update_axes()
        if save_data:
            self.save_xdata()
            self.save_ydata()
            self.save_settings()
        self.on()
        self.ani = animation.FuncAnimation(self.fig, self.update_data, frames=len(self.sweep_param1)*len(self.sweep_param2), repeat=False, init_func=self.init_func, blit=False, fargs=(save_data,save_plot,))
        plt.show(block=True)      

    def on(self):
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k or 'bias' in k or 'sense' in k:
                self.instr_list.instr_list[k].on()

    def off(self):
        for k in self.instr_list.instr_list.keys():
            if 'sweep' in k or 'bias' in k or 'sense' in k:
                self.instr_list.instr_list[k].off()