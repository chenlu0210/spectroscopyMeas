import os
from spectroscopyMeas import utilities as util
from spectroscopyMeas.base_module import OneDSweeper, instr_list, TwoDSweeper
from spectroscopyMeas.transportMeas import OneDMeas, TwoDMeas
import csv
import numpy as np
from matplotlib import animation
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import itertools

class oneDS21Sweep(OneDMeas):

    name = 'oneDS21Sweep'

    def __init__(self, parent_dir, date, instrs, settings=None, name='oneDVNASweep'):
        super().__init__(parent_dir, date, instrs, settings=settings, name=name)


    def get_sense_instr(self, i):
        ## Make sure S21 is always the first sense instr
        keys = []
        for k in self.instr_list.instr_list.keys():
            if 'S21' in k or 'sense' in k:
                keys.append(k)
        return self.instr_list.instr_list[keys[i]]   

    def set_sweeper(self):
        sense_keys = []
        numofsense, numofbias, numofsweep = 0, 0, 0
        for k in self.instr_list.instr_list.keys():
            if 'S21' in k:
                numofsense += 2
                sense_keys.append('S21 Mag')
                sense_keys.append('S21 Phase')
            elif 'sense' in k:
                numofsense += 1
                sense_keys.append(k)
            elif 'sweep' in k:
                numofsweep += 1
            elif 'bias' in k:
                numofbias += 1
        self.numofsense = numofsense
        self.numofbias = numofbias
        self.numofsweep = numofsweep
        self.sense_keys = sense_keys
        print(sense_keys)
        self.init_data_holders(sense_keys=sense_keys)

    def fit(self, x, mag, phase, fit_func=None):
        if fit_func is None:
            fit_results = util.fit_cavity(x, mag, phase, dtype=self.get_sense_instr(0).dtype)
        else:
            fit_results = fit_func(x, mag, phase, dtype=self.get_sense_instr(0).dtype)
        return fit_results

    def save_fit(self, fit_results, path=None, counter=None):
        if not path:
            path = self.path
        if not counter:
            counter = self.counter
        path = path + '\\' + str(counter)
        if os.path.exists(path+'\\fit_results.csv'):
            with open('fit_results.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(fit_results.values())
        else:
            with open('fit_results.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(fit_results.keys())
                writer.writerow(fit_results.values())

    def update_sense(self, i, save_data=True, fit=False, fit_func=None):
        # Making sure S21 is the first sense instr
        j = 0
        for k in self.sense_keys:
            if j == 0:
                if 'S21' not in k:
                    raise Exception('S21 has to be the first sense instr')
                mag, phase = self.sense(j)
                self.get_sense_data()[j][i] = mag
                j += 1
                self.get_sense_data()[j][i] = phase
                if i==self.f-1 and fit:
                    fit_results = self.fit(self.rt_x, mag, phase, fit_func=fit_func)
                    self.fit_results.append(fit_results)
                    self.save_fit(fit_results)        
            elif j < self.numofsense - 1:
                j += 1
                self.get_sense_data()[j][i] = self.sense(j-1)
        if j != self.numofsense-1:
            raise Exception('Sense number mismatched!')
        if save_data:
            self.save_zdata()



    def update_data(self, i, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None, fit=False, fit_func=None):
        self.update_sweep(i)
        self.update_sense(i, save_data=save_data, fit=fit, fit_func=fit_func)
        lines = self.update_plot(i, save_plot=save_plot, n=n)
        if opt_func is not None and opt_param is not None:
            opt_func(i, *opt_param)
        if i == self.f - 1:
            self.end_func(save_data=save_data)
        return lines

    def update_axes(self):
        sweep_key, = self.get_sweep_keys()
        sense_keys = self.get_sense_keys()
        i = 0
        last = len(self.axes)
        for ax in self.axes:
            if i == 0:
                ax.set_xlabel('{} [{}]'.format(sweep_key, self.instr_list.instr_list[sweep_key].unit))
                ax.set_ylabel('{} [{}]'.format(sense_keys[i], self.get_sense_instr(i).mag_unit))
            if i == 1:
                ax.set_xlabel('{} [{}]'.format(sweep_key, self.instr_list.instr_list[sweep_key].unit))
                ax.set_ylabel('{} [{}]'.format(sense_keys[i], self.get_sense_instr(i-1).phase_unit))
            else:
                ax.set_xlabel('{} [{}]'.format(sweep_key, self.instr_list.instr_list[sweep_key].unit))
                ax.set_ylabel('{} [{}]'.format(sense_keys[i], self.get_sense_instr(i-1).unit))                             
            i+=1
        self.fig.suptitle('S21 Trace')

    def update_plot(self, i, save_plot=True, figName='S21 Trace',n=1):
        super().update_plot(i, save_plot=save_plot, figName=figName, n=n)


    def live_plot(self, fig=None, axes=None, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None, fit=False, fit_func=None):
        self.init_func(fig=fig, axes=axes, save_data=save_data)
        for i in range(self.f):
            self.update_data(i, save_data=save_data, save_plot=save_plot, n=n, opt_func=opt_func, opt_param=opt_param, fit=fit, fit_func=fit_func)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            time.sleep(0.1)
        plt.show(block=True)

    def get_mag(self, date=None, path=None, counter=None, skip_rows=0):
        return self.grab_file('S21 mag.txt', date=date, path=path, counter=counter, skip_rows=skip_rows)

    def get_phase(self, date=None, path=None, counter=None, skip_rows=0):
        return self.grab_file('S21 phase.txt', date=date, path=path, counter=counter, skip_rows=skip_rows)

    def get_x(self, date=None, path=None, counter=None, skip_rows=0):
        sweep_key, = self.get_sweep_keys()
        return self.grab_file('{}.txt'.format(sweep_key), date=date, path=path, counter=counter, skip_rows=skip_rows)

class TwoDS21Sweep(TwoDMeas, OneDS21Sweep):

    name = 'TwoDS21Sweep'

    def __init__(self, parent_dir, date, instrs, settings=None, name='TwoDS21Sweep'):
        super().__init__(parent_dir, date, instrs, settings=settings, name=name)

    def get_sense_instr(self, i):
        ## Make sure S21 is always the first sense instr
        oneDS21Sweep.get_sense_instr(i)

    def set_sweeper(self):
        oneDS21Sweep.set_sweeper()

    def update_sense(self, i, save_data=True, fit=False, fit_func=None):
        r, c = i//self.cols, i%self.cols
        if c==0:
            time.sleep(0.5)
        j = 0
        for k in self.sense_keys:
            if j == 0:
                if 'S21' not in k:
                    raise Exception('S21 has to be the first sense instr')
                mag, phase = self.sense(j)
                self.get_sense_data()[j][r][c] = mag
                j += 1
                self.get_sense_data()[j][r][c] = phase
            elif j < self.numofsense - 1:
                j += 1
                self.get_sense_data()[j][r][c] = self.sense(j-1)
        if j != self.numofsense-1:
            raise Exception('Sense number mismatched!')
        if c == self.cols-1:
            if fit:
                fit_results = self.fit(self.rt_x, mag, phase, fit_func=fit_func)
                self.fit_results.append(fit_results)
                self.save_fit(fit_results)
        if save_data:
            self.save_zdata()

    def update_axes(self):
        i = 0
        last = len(self.axes)
        for ax in self.axes:
            i += 1
            if i == 1:
                ax.set_title('Line Trace')
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sense_keys()[0], self.get_sense_instr(0).mag_unit))                
            elif i == 2:
                ax.set_title('Color Map')
            elif i == 3:
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sense_keys()[1], self.get_sense_instr(0).phase_unit))
            elif i%2 == 1:
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sense_keys()[i//2], self.instr_list.instr_list[self.get_sense_keys()[i//2]].unit))            
            if i%2 == 0:
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sweep_keys()[1], self.instr_list.instr_list[self.get_sweep_keys()[1]].unit))
                #ax.set_ylabel('Sense{}'.format(i//2))  

    def update_data(self, i, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None, fit=False, fit_func=None):
        self.update_sweep(i)
        self.update_sense(i, save_data=save_data, fit=fit, fit_func=fit_func)
        lines = self.update_plot(i, save_plot=save_plot, n=n)
        if opt_func is not None and opt_param is not None:
            opt_func(i, *opt_param)
        if i == self.f - 1:
            self.end_func(save_data=save_data)
        return lines

    def live_plot(self, fig=None, axes=None, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None, fit=False, fit_func=None):
        self.init_func(fig=fig, axes=axes, save_data=save_data)
        for i in range(self.f):
            self.update_data(i, save_data=save_data, save_plot=save_plot, n=n, opt_func=opt_func, opt_param=opt_param, fit=fit, fit_func=fit_func)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            time.sleep(0.1)
        plt.show(block=True)


    def get_x(self, date=None, path=None, counter=None, skip_rows=0):
        sweep_key = self.get_sweep_keys()[0]
        return self.grab_file('{}.txt'.format(sweep_key), date=date, path=path, counter=counter, skip_rows=skip_rows)
        
    def get_y(self, date=None, path=None, counter=None, skip_rows=0):
        sweep_key = self.get_sweep_keys()[1]
        return self.grab_file('{}.txt'.format(sweep_key), date=date, path=path, counter=counter, skip_rows=skip_rows)
        

class oneDVNASweep(oneDS21Sweep):

    name = 'oneDVNASweep'

    def __init__(self, parent_dir, date, instrs, settings=None, name='oneDVNASweep'):
        super().__init__(parent_dir, date, instrs, settings=settings, name=name)


### Change this for 2D sweep
    def set_frames(self):
        if len(self.get_sweep_param()) == 0:
            self.f = 0
        elif self.get_sweep_param()[0] is None:
            self.f=0
        else:
            self.f = 1


    def init_data_holders(self, sense_keys=None):
        self.sense_data = {}
        self.rt_x = []
        if sense_keys is None:
            for i in range(self.numofsense):
                self.sense_data['sense{}'.format(i+1)] = np.zeros(self.f)
        else:
            try:
                for k in sense_keys:
                    if 'S21' in k:
                        self.sense_data[k] = np.zeros(len(self.get_sweep_param()[0]))
                    else:
                        self.sense_data[k] = np.zeros(self.f)
            except IndexError:
                print('Index of sense_keys do not match the number of sense parameters')

    def update_sweep(self, i):
        self.rt_x = self.get_sweep_param()[0][:]
        self.get_sweep_instr(0).write_val(self.get_sweep_param()[0])


    def update_sense(self, i, save_data=True, fit=False, fit_func=None):
        # Making sure S21 is the first sense instr
        j = 0
        for k in self.sense_keys:
            if j == 0:
                if 'S21' not in k:
                    raise Exception('S21 has to be the first sense instr')
                mag, phase = self.sense(j)
                self.get_sense_data()[j][:] = mag
                j += 1
                self.get_sense_data()[j][:] = phase
                if fit:
                    fit_results = self.fit(self.rt_x, mag, phase, fit_func=fit_func)
                    self.fit_results.append(fit_results)
                    self.save_fit(fit_results)
            elif j < self.numofsense - 1:
                j += 1
                self.get_sense_data()[j][:] = self.sense(j-1)
        if j != self.numofsense-1:
            raise Exception('Sense number mismatched!')
        if save_data:
            self.save_zdata()



    def init_axes(self, fig=None, axes=None):
        # Only plotting S21
        if fig is None:
            self.fig = plt.figure()

        if axes is None:
            self.axes = []
            for i in range(2):
                self.axes.append(self.fig.add_subplot(2,1,i+1))
        if fig is not None and axes is not None:
            self.fig = fig
            self.axes = axes

    def update_axes(self):
        sweep_key, = self.get_sweep_keys()
        sense_keys = self.get_sense_keys()
        i = 0
        last = len(self.axes)
        for ax in self.axes:
            if i == 0:
                ax.set_xlabel('{} [{}]'.format(sweep_key, self.instr_list.instr_list[sweep_key].unit))
                ax.set_ylabel('{} [{}]'.format(sense_keys[i], self.get_sense_instr(i).mag_unit))
            if i == 1:
                ax.set_xlabel('{} [{}]'.format(sweep_key, self.instr_list.instr_list[sweep_key].unit))
                ax.set_ylabel('{} [{}]'.format(sense_keys[i], self.get_sense_instr(i-1).phase_unit))
            else:
                ax.set_xlabel('{} [{}]'.format(sweep_key, self.instr_list.instr_list[sweep_key].unit))
                ax.set_ylabel('{} [{}]'.format(sense_keys[i], self.get_sense_instr(i-1).unit))                             
            i+=1
        self.fig.suptitle('S21 Trace')

    def update_plot(self, i, save_plot=True, figName='S21 Trace',n=1):
        super().update_plot(i, save_plot=save_plot, figName=figName, n=n)



class TwoDVNASweep(TwoDS21Sweep, oneDVNASweep):

    name = 'TwoDVNASweep'

    def __init__(self, parent_dir, date, instrs, settings=None, name='TwoDVNASweep'):
        super().__init__(parent_dir, date, instrs, settings=settings, name=name)


    def set_frames(self):
        if len(self.get_sweep_param()) == 0:
            self.f = 0
        elif self.get_sweep_param()[0] is None:
            self.f=0
        else:
            self.f = len(self.get_sweep_param()[1])
            self.cols = len(self.get_sweep_param()[0])


    def init_data_holders(self, sense_keys=None):
        self.sense_data = {}
        self.rt_x = []
        self.rt_y = []
        sweep_param1, sweep_param2 = self.get_sweep_param()
        if sense_keys is None:
            for i in range(self.numofsense):
                self.sense_data['sense{}'.format(i+1)] = np.zeros((self.f, self.cols))
        else:
            try:
                for k in sense_keys:
                    if 'S21' in k:
                        self.sense_data[k] = np.zeros((self.f, self.cols))
                    else:
                        self.sense_data[k] = np.zeros(self.f)
            except IndexError:
                print('Index of sense_keys do not match the number of sense parameters')

    def init_axes(self, fig=None, axes=None):
        if fig is None:
            self.fig = plt.figure()

        if axes is None:
            self.axes = []
            for i in range(2):
                self.axes.append(self.fig.add_subplot(2,2,2*i+1))
                self.axes.append(self.fig.add_subplot(2,2,2*i+2))
        elif fig is not None:
            self.fig = fig
            self.axes = axes

    def update_axes(self):
        i = 0
        last = len(self.axes)
        for ax in self.axes:
            i += 1
            if i == 1:
                ax.set_title('Line Trace')
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sense_keys()[0], self.get_sense_instr(0).mag_unit))                
            if i == 2:
                ax.set_title('Color Map')
            if i == 3:
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sense_keys()[1], self.get_sense_instr(0).phase_unit)) 
            if i%2 == 0:
                ax.set_xlabel('{} [{}]'.format(self.get_sweep_keys()[0], self.instr_list.instr_list[self.get_sweep_keys()[0]].unit))
                ax.set_ylabel('{} [{}]'.format(self.get_sweep_keys()[1], self.instr_list.instr_list[self.get_sweep_keys()[1]].unit))
                #ax.set_ylabel('Sense{}'.format(i//2))   

    def update_sweep(self, i):
        self.rt_x = self.get_sweep_param()[0][:]
        self.rt_y = self.get_sweep_param()[1][:i+1]
        self.get_sweep_instr(0).write_val(self.get_sweep_param()[0])
        self.get_sweep_instr(1).write_val(self.rt_y[i])
        self.rt_y[i] = self.get_sweep_instr(1).write_val()

    def update_sense(self, i, save_data=True, fit=False, fit_func=None):
        # Making sure S21 is the first sense instr
        j = 0
        for k in self.sense_keys:
            if j == 0:
                if 'S21' not in k:
                    raise Exception('S21 has to be the first sense instr')
                mag, phase = self.sense(j)
                self.get_sense_data()[j][i][:] = mag
                j += 1
                self.get_sense_data()[j][i][:] = phase
                if fit:
                    fit_results = self.fit(self.rt_x, mag, phase, fit_func=fit_func)
                    self.fit_results.append(fit_results)
                    self.save_fit(fit_results)
            elif j < self.numofsense - 1:
                j += 1
                self.get_sense_data()[j][i] = self.sense(j-1)
        if j != self.numofsense-1:
            raise Exception('Sense number mismatched!')
        if save_data:
            self.save_zdata()

    def update_plot(self, i, save_plot=True, figName='Sweep', n=1):
        if i == self.f - 1:
            plt.clf()
            self.init_axes(fig=self.fig)
            self.update_axes()
            lines = []
            cmaps = []
            caxes = []
            r, c = i//self.cols, i%self.cols
            for j in range(2):
                lines.append(self.axes[2*j].plot(self.rt_x, self.get_sense_data()[j][r,:], 'k.-',label='{}'.format(i)))
                im = self.axes[2*j+1].pcolormesh(self.get_sweep_param()[0], self.rt_y, self.get_sense_data()[j][:r+1, :])
                self.fig.colorbar(im, ax = self.axes[2*j+1])

            path = self.path + '\\' + str(self.counter)
            if save_plot:
                self.fig.savefig(path+'\\{}.pdf'.format(figName))
        if i%n == 0 and i//n > 0:
            plt.clf()
            self.init_axes(fig=self.fig)
            self.update_axes()
            lines = []
            cmaps = []
            caxes = []
            r, c = i//self.cols, i%self.cols
            for j in range(2):
                lines.append(self.axes[2*j].plot(self.rt_x, self.get_sense_data()[j][r,:], 'k.-',label='{}'.format(i)))
                im = self.axes[2*j+1].pcolormesh(self.get_sweep_param()[0], self.rt_y, self.get_sense_data()[j][:r+1, :])
                self.fig.colorbar(im, ax = self.axes[2*j+1])

    def update_data(self, i, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None, fit=False, fit_func=None):
        self.update_sweep(i)
        self.update_sense(i, save_data=save_data, fit=fit, fit_func=fit_func)
        lines = self.update_plot(i, save_plot=save_plot, n=n)
        if opt_func is not None and opt_param is not None:
            opt_func(i, *opt_param)
        if i == self.f - 1:
            self.end_func(save_data=save_data)
        return lines

    def live_plot(self, fig=None, axes=None, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None, fit=False, fit_func=None):
        self.init_func(fig=fig, axes=axes, save_data=save_data)
        for i in range(self.f):
            self.update_data(i, save_data=save_data, save_plot=save_plot, n=n, opt_func=opt_func, opt_param=opt_param, fit=fit, fit_func=fit_func)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            time.sleep(0.1)
        plt.show(block=True)


    def get_x(self, date=None, path=None, counter=None, skip_rows=0):
        sweep_key = self.get_sweep_keys()[0]
        return self.grab_file('{}.txt'.format(sweep_key), date=date, path=path, counter=counter, skip_rows=skip_rows)
        
    def get_y(self, date=None, path=None, counter=None, skip_rows=0):
        sweep_key = self.get_sweep_keys()[1]
        return self.grab_file('{}.txt'.format(sweep_key), date=date, path=path, counter=counter, skip_rows=skip_rows)
        



