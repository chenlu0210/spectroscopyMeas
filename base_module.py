import os
import csv
import numpy as np
#from Res_Meas import utilities as util
from spectroscopyMeas import utilities as util
from matplotlib import animation
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import itertools
import time


class base_instrument():

    def __init__(self, device, name='base_instr', func='example', mode='', unit=''):
        self.name = name
        self.device = device
        self.func = func
        self.mode = mode
        self.unit = unit
        self.set_func(func=func)
        self.set_mode(mode=mode)
        self.set_unit(unit=unit)

    def set_func(self, func=None):
        # func can be "Sense1/2", "Sweep1/2", "Bias1,2,3,...."
        if func is None:
            return self.func
        else:
            self.func = func

    def set_mode(self, mode=None):
        if mode is None:
            return self.mode
        else:
            self.mode = mode

    def set_unit(self, unit=None):
        if unit is None:
            return self.unit
        else:
            self.unit = unit

    def read_val(self):
        pass

    def write_val(self, val):
        pass

    def on(self):
        pass

    def off(self):
        pass

    def get_settings(self):
        settings = {'name':name, 'func':func, 'mode':mode, 'unit':unit}
        return settings

## Update this: change the data structure from list to dictionary
class instr_list():
    #{'Sense1': dmm, 'Sense2': dmm2, 'Bias': yokogawa, 'Sweep': smu}
    # dmm, dmm2, yokogawa, smu are all base_instrument objects
    def __init__(self, list):
        self.instr_list = {}
        for instr in list:
            util.update_dict(self.instr_list, instr.func, instr)

    # Implement this later
    def add_instr(self, instr):
        self.instr_list[instr.func] = instr
        
    def delete_instr(self, instr):
        self.instr_list.pop(instr.func)

    def save_settings(self, path, fileName='instr_settings'):
        with open(path+'//{}.csv'.format(fileName), 'w') as f:
            writer = csv.writer(f)
            for instr in self.instr_list.values():
                writer.writerow(instr.get_settings().keys())
                writer.writerow(instr.get_settings().values())

class base_measurement():

    name = 'base_meas'

    def __init__(self, parent_dir, date, instr_list=None, name=None):
        self.change_name(name=name)
        self.parent_dir = parent_dir + '\\' + self.name
        #self.instr_list = instr_list
        util.check_dir(self.parent_dir)

        
        self.date = date
        ## date in string format: ddmmyy

        ## Initialise Measurement Logs
        self.counter = 1
        self.markers = {str(self.counter): []}
        if os.path.exists(self.parent_dir + '\\' + 'Measurement_log.csv'):
            self.recover()
        else:
            log_keys = ['Date', 'Id', 'Note']
            with open('Measurement_log.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(log_keys)
        
        util.check_dir(self.date)
        self.path = self.parent_dir + '\\' + self.date

    def change_name(self, name=None):
        if name is not None:
            self.name = name

    def recover(self):
        
        log_data = util.grab_file('Measurement_log.csv', path=self.parent_dir, skip_rows=1)
        if len(log_data)!=0:
            if isinstance(log_data[0], str):
                if log_data[0] == self.date:
                    self.markers[log_data[1]] = log_data[2]
                    self.counter = 2
            else:
                for entry in log_data:
                    if entry[0]==self.date:
                        self.markers[entry[1]] = entry[2]
                if len(self.markers['1'])!=0:
                    self.counter = max([int(a) for a in list(self.markers.keys())]) + 1



    def update_date(self, new_date):
        self.date = new_date
        util.change_dir(self.parent_dir)
        util.check_dir(self.date)
        self.path = self.parent_dir + '\\' + self.date
        self.counter = 1
        self.markers = {str(self.counter): []}


    def grab_file(self, fileName, date=None,path=None, counter=None, skip_rows=0):
        if not path:
            path = self.path
        elif not date:
            path = self.parent_dir + '\\' + self.date
        if not counter:
            counter = self.counter-1
        path = path + '\\' + str(counter)
        if os.path.exists(path+'\\'+fileName):
            if fileName.split('.')[1] == 'csv':
                return np.loadtxt(open(os.path.join(path, fileName), "rb"), delimiter=",", skiprows=skip_rows)
            elif fileName.split('.')[1] == 'txt':
                return np.loadtxt(os.path.join(path, fileName), skiprows=skip_rows)
        else:
            raise Exception('File does not exist!')


    def mark(self, id=None, message=''):
        if not id:
            id = str(self.get_id())
        if id in self.markers:
            if len(self.markers[id])!=0:
                self.markers[id] = self.markers[id] + '_' + message
                self.log_from_markers()
            else:
                self.markers[id] = message
                log_info = [self.date, id, self.markers[id]]
                self.update_log(log_info)
        else:
            self.markers[id] = message
            log_info = [self.date, id, self.markers[id]]
            self.update_log(log_info)



    def update_log(self, log_info):
        util.check_dir(self.parent_dir)
        with open('Measurement_log.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(log_info)


    def log_from_markers(self):
        if self.markers:
            ids = list(self.markers.keys())
            messages = list(self.markers.values())
            new_info = [[self.date, ids[i], messages[i]] for i in range(len(ids))]
            old_data = util.grab_file('Measurement_log.csv', path=self.parent_dir, skip_rows=1)
            log_keys = ['Date', 'Id', 'Note']
            
            if len(old_data)==0:
                print('There is a logging error resulting in empty file. Please check your Measurement_log.')
            else:
                with open('Measurement_log.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(log_keys)
                
                if isinstance(old_data[0], str):
                    if old_data[0] == self.date:
                        old_data = new_info[0]
                    with open('Measurement_log.csv', 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(old_data)
                else:
                    j = 0
                    for i in range(len(old_data)):
                        if old_data[i][0] == self.date and j<len(new_info):
                            old_data[i] = new_info[j]
                            j+=1

                    #print(old_data)
                
                    with open('Measurement_log.csv', 'a') as f:
                        writer = csv.writer(f)
                        for entry in old_data:
                            writer.writerow(entry)
        else:
            print('You dont have anything to write!')



    def get_markers(self):
        return self.markers

    def get_id(self):
        return self.counter - 1

    def update_id(self):
        self.counter += 1

    def get_path(self):
        return self.path

    def write_path(self):
        util.change_dir(self.path)


class OneDSweeper(base_measurement):

    name = '1D Sweep'

    def __init__(self, parent_dir, date, instr_list=None, sweep_param=None, numofsense=None, fig=None, axes=None, name=None):
        super().__init__(parent_dir, date, instr_list=instr_list, name=name)
        ####
        #sweep_param: list of values that you want to sweep
        # numofsense: numbers of sense variables
        # rt_x: real time list of x values that have been swept
        # sense_data: list of data holders for sense parameter
        # fig, axes: graph for plotting
        self.set_sweep_param(sweep_param=sweep_param)
        self.set_numofsense(numofsense=numofsense)
        self.init_data_holders()

    def set_numofsense(self, numofsense=None):
        if numofsense is None:
            self.numofsense = 1
        else:
            self.numofsense = numofsense

    def set_sweep_param(self, sweep_param=None, key='sweep_param'):
        self.sweep_param = {key: None}
        if sweep_param is None:
            self.sweep_param[key] = range(10)
        else:
            self.sweep_param[key] = sweep_param
        self.set_frames()

    def set_frames(self):
        if len(self.get_sweep_param()) == 0:
            self.f = 0
        elif self.get_sweep_param()[0] is None:
            self.f=0
        else:
            self.f = len(self.get_sweep_param()[0])

    def get_sweep_param(self):
        return tuple(self.sweep_param.values())

    def get_sweep_keys(self):
        return tuple(self.sweep_param.keys())

    def get_sense_data(self):
        return tuple(self.sense_data.values())

    def get_sense_keys(self):
        return tuple(self.sense_data.keys())

    def init_data_holders(self, sense_keys=None):
        self.sense_data = {}
        self.rt_x = []
        if sense_keys is None:
            for i in range(self.numofsense):
                self.sense_data['sense{}'.format(i+1)] = np.zeros(self.f)
        else:
            try:
                for k in sense_keys:
                    self.sense_data[k] = np.zeros(self.f)
            except IndexError:
                print('Index of sense_keys do not match the number of sense parameters')


            # create a new data holder with the same length of sweep_param

    def init_axes(self, fig=None, axes=None):
        if fig is None:
            self.fig = plt.figure()

        if axes is None:
            self.axes = []
            for i in range(self.numofsense):
                self.axes.append(self.fig.add_subplot(self.numofsense,1,i+1))
        if fig is not None and axes is not None:
            self.fig = fig
            self.axes = axes

    def update_axes(self):
        sweep_key, = self.get_sweep_keys()
        sense_keys = self.get_sense_keys()
        i = 0
        last = len(self.axes)
        for ax in self.axes:
            ax.set_xlabel(sweep_key)
            ax.set_ylabel(sense_keys[i])
            i+=1
        self.fig.suptitle('Trace Live Plot')     


    def save_xdata(self, path=None, counter=None):
        sweep_param, = self.get_sweep_param()
        sweep_key, = self.get_sweep_keys()
        if not path:
            path = self.path
        if not counter:
            counter = self.counter
        path = path + '\\' + str(counter) 
        np.savetxt(path+"\\{}.txt".format(sweep_key), self.rt_x)

    def save_zdata(self, path=None, counter=None):
        if not path:
            path = self.path
        if not counter:
            counter = self.counter
        path = path + '\\' + str(counter)
        i = 0
        sense_data, sense_keys = self.get_sense_data(), self.get_sense_keys()
        for data in sense_data:
            np.savetxt(path+"\\{}.txt".format(sense_keys[i]), data)
            i += 1

    def update_sweep(self, i):
        self.rt_x = self.get_sweep_param()[0][:i+1]

    def update_sense(self, i, save_data=True):
        for j in range(self.numofsense):
            self.get_sense_data()[j][i] = self.get_sweep_param()[0][i]
        if save_data:
            self.save_zdata()

    def update_plot(self, i, save_plot=True, figName='TracePlot',n=10):
        if i == self.f - 1:
            plt.clf()
            self.init_axes(fig=self.fig)
            self.update_axes()
            lines = []
            for j in range(len(self.axes)):
                lines.append(self.axes[j].plot(self.rt_x, self.get_sense_data()[j][:], 'k.-',label='{}'.format(i)))            
            path = self.path + '\\' + str(self.counter)
            if save_plot:
                self.fig.savefig(path+'\\{}.pdf'.format(figName))
        if i%n==0 and i//n>0:
            plt.clf()
            self.init_axes(fig=self.fig)
            self.update_axes()
            lines = []
            for j in range(len(self.axes)):
                lines.append(self.axes[j].plot(self.rt_x, self.get_sense_data()[j][:i+1], 'k.-',label='{}'.format(i)))
                #self.axes[j].legend()




    def update_data(self, i, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None):
        self.update_sweep(i)
        self.update_sense(i, save_data=save_data)
        lines = self.update_plot(i, save_plot=save_plot, n=n)
        if opt_func is not None and opt_param is not None:
            opt_func(i, *opt_param)
        if i == self.f - 1:
            self.end_func(save_data=save_data)
        return lines


    def init_func(self, fig=None, axes=None, save_data=True): 
        self.write_path()
        util.check_dir(str(self.counter))
        self.init_axes(fig=fig, axes=axes)
        self.update_axes()
        self.set_frames()
        self.rt_x = []
        self.init_data_holders()
        self.start_time = time.time()

    def end_func(self, save_data=True):
        if save_data:
            self.save_xdata()
        self.end_time = time.time()
        self.update_id()
        self.mark()


    def mark(self, id=None, message=None):
        sweep_param, = self.get_sweep_param()
        if message is None:
            message = '{:2f}to{:2f}in{}steps'.format(sweep_param[0],sweep_param[-1],len(sweep_param))
        super().mark(id=id, message=message)



    def live_plot(self, fig=None, axes=None, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None):
        self.init_func(fig=fig, axes=axes, save_data=save_data)
        for i in range(self.f):
            self.update_data(i, save_data=save_data, save_plot=save_plot, n=n, opt_func=opt_func, opt_param=opt_param)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            time.sleep(0.1)
        plt.show(block=True)



class TwoDSweeper(OneDSweeper):

    name = '2D Sweep'

    def __init__(self, parent_dir, date, instr_list=None, sweep_param1=None, sweep_param2=None, numofsense=None, fig=None, axes=None, name=None):
        super(OneDSweeper, self).__init__(parent_dir, date, instr_list=instr_list, name=name)
        ####
        #sweep_param: list of values that you want to sweep
        # numofsense: numbers of sense variables
        # rt_x: real time list of x values that have been swept
        # sense_data: list of data holders for sense parameter
        # fig, axes: graph for plotting
        self.set_sweep_param(sweep_param1=sweep_param1, sweep_param2=sweep_param2)
        self.set_numofsense(numofsense=numofsense)
        self.init_data_holders()


    def set_sweep_param(self, sweep_param1=None, sweep_param2=None, keys=None):
        if sweep_param1 is None:
            sweep_param1 = range(10)
        if sweep_param2 is None:
            sweep_param2 = range(10)
        self.sweep_param = {}
        if keys is None:
            self.sweep_param['sweep_param1'] = sweep_param1
            self.sweep_param['sweep_param2'] = sweep_param2
        self.set_frames()

    def set_frames(self):
        if len(self.get_sweep_param()) == 0:
            self.f = 0
        elif self.get_sweep_param()[0] is None:
            self.f=0
        else:
            self.f = len(self.get_sweep_param()[0])*len(self.get_sweep_param()[1])
            self.cols = len(self.get_sweep_param()[0])


    def init_data_holders(self, sense_keys=None):
        self.sense_data = {}
        self.rt_x = []
        self.rt_y = []
        sweep_param1, sweep_param2 = self.get_sweep_param()
        if sense_keys is None:
            for i in range(self.numofsense):
                self.sense_data['sense{}'.format(i+1)] = np.zeros((len(sweep_param2), len(sweep_param1)))
        else:
            try:
                for k in sense_keys:
                    self.sense_data[k] = np.zeros((len(sweep_param2), len(sweep_param1)))
            except IndexError:
                print('Index of sense_keys do not match the number of sense parameters')


    def init_axes(self, fig=None, axes=None):
        if fig is None:
            self.fig = plt.figure()

        if axes is None:
            self.axes = []
            for i in range(self.numofsense):
                self.axes.append(self.fig.add_subplot(self.numofsense,2,2*i+1))
                self.axes.append(self.fig.add_subplot(self.numofsense,2,2*i+2))
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
            if i == 2:
                ax.set_title('Color Map')
            if i%2 == 1:
                ax.set_xlabel(self.get_sweep_keys()[0])
                ax.set_ylabel(self.get_sense_keys()[i//2])
            if i%2 == 0:
                ax.set_xlabel(self.get_sweep_keys()[0])
                ax.set_ylabel(self.get_sweep_keys()[1])
                #ax.set_ylabel('Sense{}'.format(i//2))   


    def save_xdata(self, path=None, counter=None):
        if not path:
            path = self.path
        if not counter:
            counter = self.counter
        path = path + '\\' + str(counter) 
        np.savetxt(path+"\\{}.txt".format(self.get_sweep_keys()[0]), self.rt_x)


    def save_ydata(self, fileName='sweep_param2', path=None, counter=None):
        if not path:
            path = self.path
        if not counter:
            counter = self.counter
        path = path + '\\' + str(counter) 
        np.savetxt(path+"\\{}.txt".format(self.get_sweep_keys()[1]), self.rt_y)



    def update_sweep(self, i):
        self.rt_x = self.get_sweep_param()[0][:i%self.cols+1]
        self.rt_y = self.get_sweep_param()[1][:i//self.cols+1]

    def update_sense(self, i, save_data=True):
        r, c = i//self.cols, i%self.cols
        for j in range(self.numofsense):
            self.get_sense_data()[j][r][c] = r*self.get_sweep_param()[0][c]
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
            for j in range(self.numofsense):
                lines.append(self.axes[2*j].plot(self.rt_x, self.get_sense_data()[j][r,:c+1], 'k.-',label='{}'.format(i)))
                if (i+1)%self.cols == 0:
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
            for j in range(self.numofsense):
                lines.append(self.axes[2*j].plot(self.rt_x, self.get_sense_data()[j][r,:c+1], 'k.-',label='{}'.format(i)))
                if (i+1)%self.cols == 0:
                    im = self.axes[2*j+1].pcolormesh(self.get_sweep_param()[0], self.rt_y, self.get_sense_data()[j][:r+1, :])
                    self.fig.colorbar(im, ax = self.axes[2*j+1])

            #self.axes[j].legend()


    def init_func(self, fig=None, axes=None, save_data=True): 
        self.write_path()
        util.check_dir(str(self.counter))
        self.init_axes(fig=fig, axes=axes)
        self.update_axes()
        self.rt_x = []
        self.rt_y = []
        self.init_data_holders()
        self.start_time = time.time()

    def end_func(self, save_data=True):
        if save_data:
            self.save_xdata()
            self.save_ydata()        
        self.end_time = time.time()
        self.update_id()
        self.mark()


    def mark(self, id=None, message=None):
        sweep_param1, sweep_param2 = self.get_sweep_param()
        if message is None:
            message = '{:2f}to{:2f}in{}steps_{:2f}to{:2f}in{}steps'.format(sweep_param1[0],sweep_param1[-1],self.cols,sweep_param2[0],sweep_param2[-1],len(sweep_param2))
        super(OneDSweeper, self).mark(id=id, message=message)
   

    def live_plot(self, fig=None, axes=None, save_data=True, save_plot=True, n=1, opt_func=None, opt_param=None):
        self.init_func(fig=fig, axes=axes, save_data=save_data)
        for i in range(self.f):
            self.update_data(i, save_data=save_data, save_plot=save_plot, n=n, opt_func=opt_func, opt_param=opt_param)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            time.sleep(0.1)
        plt.show(block=True)