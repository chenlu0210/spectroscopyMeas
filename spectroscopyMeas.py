import os
from Res_Meas import utilities as util
import csv
import numpy as np
from matplotlib import animation
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import itertools


class spectroscopyMeas:

    name = 'spectroscopyMeas'


    def __init__(self, parent_dir, date, vna=None, vna_settings=None, fridge=None):
        self.parent_dir = parent_dir + '\\' + self.name
        util.check_dir(self.parent_dir)

        
        self.date = date
        ## date in string format: ddmmyy
        self.vna = vna
        ## QCODES instrument instances
        self.vna_settings = vna_settings
        self.fridge = fridge
        self.write_vna_settings(vna_settings)
        ## vna_settings = {'avg': 10, 'band': 100, 'npts': 201, 'span': 100e3, 'center': 6.7e9, 'power': -50}

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


    def prepare_meas(self):
        if self.vna:
            self.vna.rf_on()
        else:
            print('There is no vna connected.')

    def end_meas(self):
        if self.vna:
            self.vna.rf_off()
        else:
            print('There is no vna connected.')

    def get_temp(self):
        if self.fridge:
            return self.fridge.MC.get()*1e3
        else:
            print('There is no fridge connected.')
            return 0.0

    def grab_file(self, fileName, path=None, counter=None, skip_rows=0):
        files = []
        if not path:
            path = self.path
        if not counter:
            counter = self.counter-1
        path = path + '\\' + str(counter)
        if fileName.split('.')[1] == 'csv':
            return np.loadtxt(open(os.path.join(path, fileName), "rb"), delimiter=",", skiprows=skip_rows)
        elif fileName.split('.')[1] == 'txt':
            return np.loadtxt(os.path.join(path, fileName), skiprows=skip_rows)

    def mark(self, id=None, message=None):
        if not id:
            id = str(self.get_id())
        
        if not message:
            message = 'center:{:.4f}GHz_span:{:.0e}kHz_avg:{:d}_power:{:d}_npts:{:d}'.format(self.vna_settings['center']*1e-9, self.vna_settings['span']*1e-3, 
                self.vna_settings['avg'], self.vna_settings['power'], self.vna_settings['npts'])
        if id in self.markers:
            if len(self.markers[id])!=0:
                self.markers[id] = self.markers[id] + '_' + message
                self.log_from_markers()
            else:
                self.markers[id] = message
        else:
            self.markers[id] = message

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

    def write_vna_settings(self, vna_settings=None):
        if self.vna:
            if vna_settings:
                self.vna_settings = vna_settings
            channel = self.vna.channels.S21
            channel.avg(self.vna_settings['avg'])
            channel.bandwidth(self.vna_settings['band'])
            channel.npts(self.vna_settings['npts'])
            channel.power(self.vna_settings['power'])
            channel.center(self.vna_settings['center'])
            channel.span(self.vna_settings['span'])
        else:
            print('There is no vna connected.')

    def save_vna_settings(self):
        if self.vna_settings:
            with open('vna_settings.csv', 'w') as f:
                for key in self.vna_settings.keys():
                    f.write("%s, %s\n" % (key, self.vna_settings[key]))
                if self.fridge:
                    f.write("%s, %s\n" % ('temp', self.get_temp()))
        else:
            print('The vna settings is empty!')



class singleToneFreqSweep(spectroscopyMeas):

    name = 'singleToneFreqSweep'

    def __init__(self, parent_dir, date, vna=None, vna_settings=None, fridge=None):
        super().__init__(parent_dir, date, vna, vna_settings, fridge)


## Retrieving data
    def get_mag(self, path=None, counter=None):
        return self.grab_file('mag.txt', path, counter)

    def get_phase(self, path=None, counter=None):
        return self.grab_file('phase.txt', path, counter)

    def get_freqs(self, path=None, counter=None):
        return self.grab_file('freqs.txt', path, counter)

    def meas(self, vna_settings=None, plot=True, save=True, reduce_bg=False, style=None):
        channel = self.vna.channels.S21
        self.write_vna_settings(vna_settings)

        self.prepare_meas()
        
        ## Start Measurement
        amp, phase = channel.trace_mag_phase()
        #mag = 10*np.log10(mag)
        mag = util.mag2dB(amp)

        if reduce_bg:
            channel.power(-80)
            mag_bg, phase_bg = channel.trace_mag_phase()
            mag = mag - util.mag2dB(mag_bg)
            phase = phase - phase_bg

        ## Plot and save data
        

        freqs = util.sweep(self.vna_settings['center'], self.vna_settings['span'], self.vna_settings['npts'])
        freqs = util.freq2GHz(freqs)  

        self.write_path()
        util.check_dir(str(self.counter))           

        if plot:
            util.tracePlot(mag, freqs, save, style)

        if save:       
            self.save_vna_settings()

            np.savetxt('mag.txt', mag)
            np.savetxt('freqs.txt', freqs)
            np.savetxt('phase.txt', phase)

            self.update_id()

            self.mark()
            log_info = [self.date, str(self.get_id()), self.markers[str(self.get_id())]]
            self.update_log(log_info)

        return freqs, mag, phase


## Basic Data Analysis



        

        



class singleTonePowerSweep(singleToneFreqSweep):

    name = 'singleTonePowerSweep'

    def __init__(self, parent_dir, date, vna=None, vna_settings=None, fridge=None):
        super().__init__(parent_dir, date, vna, vna_settings, fridge)


    def save_vna_settings(self):
        if self.vna:
            with open('vna_settings.csv', 'w') as f:
                for key in [*self.vna_settings][:-1]:
                    f.write("%s, %s\n" % (key, self.vna_settings[key]))
                if self.fridge:
                    f.write("%s, %s\n" % ('temp', self.get_temp()))
        else:
            print('There is no fridge connected.')

    def mark(self, powers, id=None, message=None):
        if not id:
            id = str(self.get_id())
        if not message:
            message = 'center:{:2f}_span:{:2f}_power_min:{:0f}_power_max:{:0f}'.format(self.vna_settings['center'], self.vna_settings['span'], 
                min(powers), max(powers))
        if id in self.markers:
            if self.markers[id]:
                self.markers[id] = self.markers[id] + '_' + message
                self.log_from_markers()
            else:
                self.markers[id] = message
        else:
            self.markers[id] = message


    
    def get_mag(self, path=None, counter=None):
        if path is None:
            path = self.path
        if counter is None:
            counter = self.get_id()
        return self.grab_file('mags.csv', path, counter)

    def get_phase(self, path=None, counter=None):
        if path is None:
            path = self.path
        if counter is None:
            counter = self.get_id()
        return self.grab_file('phases.csv', path, counter)

    def get_powers(self, path=None, counter=None):
        if path is None:
            path = self.path
        if counter is None:
            counter = self.get_id()
        return self.grab_file('powers.txt', path, counter)

    def colorPlot(self, fig, ax, cax, vals, xs, ys, save=False, filename='mag_color'):
        ax.set_xlabel('Freqs (GHz)')
        ax.set_ylabel('Powers (dBm)')
        im = ax.imshow(vals,extent = (min(xs), max(xs), min(ys), max(ys)), 
                     origin='lower', aspect='auto')
        fig.colorbar(im, cax=cax)
        if save:
            plt.savefig(filename+'.pdf')

    def initialize_Plot(self):
        fig = plt.figure()
        line_ax1 = fig.add_subplot(3,2,1)
        line_ax1.set_title('Trace (Mag)')
        line_ax2 = fig.add_subplot(3,2,2)
        line_ax2.set_title('Trace (Phase)')
        color_ax1 = fig.add_subplot(3,2,3)
        color_ax1.set_title('Color Plot (Mag)')
        color_ax2 = fig.add_subplot(3,2,4)
        color_ax2.set_title('Color Plot (Phase)')
        line_ax3 = fig.add_subplot(3,2,5)
        line_ax3.set_title('Total Quality Factor')
        line_ax4 = fig.add_subplot(3,2,6)
        line_ax4.set_title('Internal Quality Factor')    
        div1 = make_axes_locatable(color_ax1)
        cax1 = div1.append_axes('right', '5%', '5%')
        div2 = make_axes_locatable(color_ax2)
        cax2 = div2.append_axes('right', '5%', '5%')
        return [fig, line_ax1, line_ax2, color_ax1, color_ax2, line_ax3, line_ax4, cax1, cax2]

    def live_meas_test(self):
        fig, line_ax1, line_ax2, color_ax1, color_ax2, line_ax3, line_ax4, cax1, cax2 = self.initialize_Plot()
    
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
    
        def init_func(self):
            mags, phases = [], []
            Qis, Qls = [], []
            
        ani = animation.FuncAnimation(fig, animate, frames=len(a), repeat=False, init_func=init_func, interval=2000)
        plt.tight_layout()
        plt.show()
        return ani

    def meas(self, powers, vna_settings=None, check_Q=True, plot=True, save=True):
        self.write_path()
        util.check_dir(str(self.counter))
        self.write_vna_settings(vna_settings)
        self.save_vna_settings()
        
        if check_Q:
            fit_header = ["Qi_dia_corr", "Qi_no_corr", "absQc", "Qc_dia_corr", "Ql", "fr", "theta0", "phi0", "phi0_err", "Ql_err", "absQc_err", "fr_err", "chi_square", "Qi_no_corr_err", "Qi_dia_corr_err", "temp"]
            with open('fit_results.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(fit_header)

        np.savetxt('powers.txt', powers)

        Qis, Qi_errs = [], []
        Qls, Ql_errs = [], []
        fcs, fc_errs = [], []
        mags, phases = [], []
        
        for p in powers:
            vna_settings['power'] = p
            freqs, mag, phase = super().meas(vna_settings, plot=True, save=False, reduce_bg=False, style=None)
            plt.show()
            mags.append(mag)
            phases.append(phase)

            if save:
                self.write_path()
                util.check_dir(str(self.get_id()))
                with open('mags.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(mag)
                with open('phases.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(phase)

            if check_Q:
                results = util.fit_cavity(freqs, mag, phase)
                a = list(results.values())
                a.append(self.get_temp())
                with open('fit_results.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(a)
                Qis.append(results["Qi_dia_corr"])
                Qi_errs.append(results["Qi_dia_corr_err"])
                Qls.append(results["Ql"])
                Ql_errs.append(results["Ql_err"])
                fcs.append(results["fr"])
                fc_errs.append(results["fr_err"])

            plt.clf()


        if plot:
            fig1, (color_ax1, color_ax2) = plt.subplots(1,2)
            div1 = make_axes_locatable(color_ax1)
            cax1 = div1.append_axes('right', '5%', '5%')
            div2 = make_axes_locatable(color_ax2)
            cax2 = div2.append_axes('right', '5%', '5%')
            cmap1 = self.colorPlot(fig1, color_ax1, cax1, mags, freqs, powers, save)
            cmap2 = self.colorPlot(fig1, color_ax2, cax2, phases, freqs, powers, save, filename='phase_color')

            if check_Q:
                fig2,(ax1, ax2, ax3) = plt.subplots(3,1)
                line1 = ax1.errorbar(powers, Qls, yerr=Ql_errs)
                ax1.set_ylabel('Loaded Quality Factor')
                line2 = ax2.errorbar(powers, Qis, yerr=Qi_errs)
                ax2.set_ylabel('Internal Quality Factor')
                line3 = ax3.errorbar(powers, fcs, yerr=fc_errs)
                ax1.set_ylabel('Cavity Frequency')
                

            plt.show()

        if save:
            fig2.savefig('fit.pdf')
            self.update_id()
            self.mark(powers)
            log_info = [self.date, str(self.get_id()), self.markers[str(self.get_id())]]
            self.update_log(log_info)
        
        return freqs, mags, phases

    def live_meas(self, powers, vna_settings=None, check_Q=True):
        self.prepare_meas()
        ## Initialize Plot
        fig, line_ax1, line_ax2, color_ax1, color_ax2, line_ax3, line_ax4, cax1, cax2 = self.initialize_Plot()
        
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
        
        self.write_path()
        util.check_dir(str(self.counter))
        self.write_vna_settings(vna_settings)
        self.save_vna_settings()
        fit_header = ["Qi_dia_corr", "Qi_no_corr", "absQc", "Qc_dia_corr", "Ql", "fr", "theta0", "phi0", "phi0_err", "Ql_err", "absQc_err", "fr_err", "chi_square", "Qi_no_corr_err", "Qi_dia_corr_err", "temp"]
        with open('fit_results.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(fit_header)
        freqs = util.sweep(self.vna_settings['center'], self.vna_settings['span'], self.vna_settings['npts'])
        freqs = util.freq2GHz(freqs)
        np.savetxt('powers.txt', powers)
        np.savetxt('freqs.txt', freqs)
        
        def animate(i):
            p = powers[i]
            vna_settings['power'] = p
            self.write_vna_settings(vna_settings)
            amp, phase = self.vna.channels.S21.trace_mag_phase()
            mag = util.mag2dB(amp)
            
            line1 = line_ax1.plot(freqs, mag)
            line2 = line_ax2.plot(freqs, phase)
            mags.append(mag)
            phases.append(phase)
            
            #np.savetxt('mags.txt', mags)
            #np.savetxt('phases.txt', phases)
            self.write_path()
            util.check_dir(str(self.get_id()))
            with open('mags.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(mag)
            with open('phases.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(phase)
            cax1.cla()
            cax2.cla()
            cmap1 = self.colorPlot(fig, color_ax1, cax1, mags, freqs, powers[:i+1])
            cmap2 = self.colorPlot(fig, color_ax2, cax2, phases, freqs, powers[:i+1])
            
            if check_Q:
                results = util.fit_cavity(freqs, mag, phase)
                a = list(results.values())
                a.append(self.get_temp())
                with open('fit_results.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(a)
                Qis.append(results["Qi_dia_corr"])
                Qi_errs.append(results["Qi_dia_corr_err"])
                Qls.append(results["Ql"])
                Ql_errs.append(results["Ql_err"])
                line3 = line_ax3.errorbar(powers[:i+1], Qls, yerr=Ql_errs)
                line4 = line_ax4.errorbar(powers[:i+1], Qis, yerr=Qi_errs)

            return line1, line2, cmap1, cmap2, line3, line4, 
        
        self.update_id()
        self.mark(powers)
        log_info = [self.date, str(self.get_id()), self.markers[str(self.get_id())]]
        self.update_log(log_info)


        ani = animation.FuncAnimation(fig, animate, frames=frames, repeat=False, init_func=init_func)
        plt.tight_layout()
        plt.show(block=True)
        return ani, fig
                

class singleToneTempSweep(singleToneFreqSweep):

    name = 'singleToneTempSweep'

    def __init__(self, parent_dir, date, vna=None, vna_settings=None, fridge=None):
        super().__init__(parent_dir, date, vna, vna_settings, fridge)

    
    def get_mag(self, path=None, counter=None):
        if path is None:
            path = self.path
        if counter is None:
            counter = self.get_id()
        return self.grab_file('mags.csv', path, counter)

    def get_phase(self, path=None, counter=None):
        if path is None:
            path = self.path
        if counter is None:
            counter = self.get_id()
        return self.grab_file('phases.csv', path, counter)

    def colorPlot(self, fig, ax, cax, vals, xs, ys, save=False):
        ax.set_xlabel('Freqs (GHz)')
        ax.set_ylabel('Temps (mK)')
        im = ax.imshow(vals,extent = (min(xs), max(xs), min(ys), max(ys)), 
                     origin='lower', aspect='auto')
        fig.colorbar(im, cax=cax)
        if save:
            plt.savefig('mag_color.png')

    def initialize_Plot(self):
        fig = plt.figure()
        line_ax1 = fig.add_subplot(3,2,1)
        line_ax1.set_title('Trace (Mag)')
        line_ax2 = fig.add_subplot(3,2,2)
        line_ax2.set_title('Trace (Phase)')
        color_ax1 = fig.add_subplot(3,2,3)
        color_ax1.set_title('Color Plot (Mag)')
        color_ax2 = fig.add_subplot(3,2,4)
        color_ax2.set_title('Color Plot (Phase)')
        line_ax3 = fig.add_subplot(3,2,5)
        line_ax3.set_title('Resonance Frequency')
        line_ax4 = fig.add_subplot(3,2,6)
        line_ax4.set_title('Internal Quality Factor')    
        div1 = make_axes_locatable(color_ax1)
        cax1 = div1.append_axes('right', '5%', '5%')
        div2 = make_axes_locatable(color_ax2)
        cax2 = div2.append_axes('right', '5%', '5%')
        return [fig, line_ax1, line_ax2, color_ax1, color_ax2, line_ax3, line_ax4, cax1, cax2]




    def live_meas(self, vna_settings=None, check_Q=True):
        ## Initialize Plot
        fig, line_ax1, line_ax2, color_ax1, color_ax2, line_ax3, line_ax4, cax1, cax2 = self.initialize_Plot()
        
        Qis, Qi_errs = [], []
        fcs, fc_errs = [], []
        mags = []
        phases = []
        temps = []

        def init_func():
            Qis, Qi_errs = [], []
            fcs, fc_errs = [], []
            mags = []
            phases = []
            temps = []
        
        self.write_path()
        util.check_dir(str(self.counter))
        self.write_vna_settings(vna_settings)
        self.save_vna_settings()
        fit_header = ["Qi_dia_corr", "Qi_no_corr", "absQc", "Qc_dia_corr", "Ql", "fr", "theta0", "phi0", "phi0_err", "Ql_err", "absQc_err", "fr_err", "chi_square", "Qi_no_corr_err", "Qi_dia_corr_err", "temp"]
        with open('fit_results.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fit_header)
        freqs = util.sweep(self.vna_settings['center'], self.vna_settings['span'], self.vna_settings['npts'])
        freqs = util.freq2GHz(freqs)
        np.savetxt('freqs.txt', freqs)
        self.prepare_meas()
        
        def animate(i):
            temp = self.get_temp()
            temps.append(temp)
            amp, phase = self.vna.channels.S21.trace_mag_phase()
            mag = util.mag2dB(amp)
            
            line1 = line_ax1.plot(freqs, mag)
            line2 = line_ax2.plot(freqs, phase)
            mags.append(mag)
            phases.append(phase)
            
            with open('mags.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(mag)
            with open('phases.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(phase)
            cax1.cla()
            cax2.cla()
            cmap1 = self.colorPlot(fig, color_ax1, cax1, mags, freqs, temps)
            cmap2 = self.colorPlot(fig, color_ax2, cax2, phases, freqs, temps)
            
            if check_Q:
                results = util.fit_cavity(freqs, mag, phase)
                a = list(results.values())
                a.append(self.get_temp())
                with open('fit_results.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(a)
                Qis.append(results["Qi_dia_corr"])
                Qi_errs.append(results["Qi_dia_corr_err"])
                fcs.append(results["fr"])
                fc_errs.append(results["fr_err"])
                line3 = line_ax3.errorbar(temps, fcs, yerr=fc_errs)
                line4 = line_ax4.errorbar(temps, Qis, yerr=Qi_errs)

            return line1, line2, cmap1, cmap2, line3, line4, 
        
        self.update_id()
        self.mark()
        log_info = [self.date, str(self.get_id()), self.markers[str(self.get_id())]]
        self.update_log(log_info)

        ani = animation.FuncAnimation(fig, animate, repeat=False, init_func=init_func, interval=20000, frames=itertools.count())
        plt.tight_layout()
        plt.show()
        return ani, fig


#class singleToneCurrentSweep(singleToneFreqSweep)


class twoToneFreqSweep(singleToneFreqSweep):

    name = 'twoToneFreqSweep'

    def __init__(self, parent_dir, date, vna=None, vna_settings=None, readout_settings=None, fridge=None):
        super().__init__(parent_dir, date, vna, vna_settings, fridge)
        self.readout_settings = readout_settings


    def write_readout_settings(self, readout_settings=None):
        if self.vna:
            channel = self.vna.channels.S21
            if readout_settings:
                self.readout_settings = readout_settings
            channel.ftt_freq(self.readout_settings['readout_freq'])
            channel.ftt_power(self.readout_settings['readout_power'])

    def save_readout_settings(self):
        if self.vna:
            with open('readout_settings.csv', 'w') as f:
                for key in self.readout_settings.keys():
                    f.write("%s, %s\n" % (key, self.readout_settings[key]))

    def mark(self, id=None, message=None):
        if not id:
            id = str(self.get_id())
        if not message:
            message = 'center:{:2f}_span:{:2f}_power:{:0f}_readout_freq:{:2f}_readout_power:{:0f}'.format(self.vna_settings['center'], self.vna_settings['span'], 
                self.vna_settings['power'], self.readout_settings['readout_freq'], self.readout_settings['readout_power'])
        if id in self.markers:
            if self.markers[id]:
                self.markers[id] = self.markers[id] + '_' + message
                self.log_from_markers()
            else:
                self.markers[id] = message
        else:
            self.markers[id] = message


## Retrieving data
    def get_mag(self, path=None, counter=None):
        return self.grab_file('mag.txt', path, counter)

    def get_phase(self, path=None, counter=None):
        return self.grab_file('phase.txt', path, counter)

    def get_freqs(self, path=None, counter=None):
        return self.grab_file('freqs.txt', path, counter)

    def prepare_meas(self):
        super().prepare_meas()
        if self.vna:
            channel = self.vna.channels.S21
			#channel.ftt_on()
            channel.gen_on()

    def end_meas(self):
        if self.vna:
            channel = self.vna.channels.S21
            channel.ftt_off()

    def meas(self, vna_settings=None, readout_settings=None, plot=True, save=True, reduce_bg=False, style=None):
        channel = self.vna.channels.S21
        self.write_vna_settings(vna_settings)
        self.write_readout_settings(readout_settings)
        self.prepare_meas()
        
        ## Start Measurement
        amp, phase = channel.trace_mag_phase()
        #mag = 10*np.log10(mag)
        mag = util.mag2dB(amp)

        if reduce_bg:
            channel.power(-80)
            mag_bg, phase_bg = channel.trace_mag_phase()
            mag = mag - util.mag2dB(mag_bg)
            phase = phase - phase_bg

        ## Plot and save data
        

        freqs = util.sweep(self.vna_settings['center'], self.vna_settings['span'], self.vna_settings['npts'])
        freqs = util.freq2GHz(freqs)  

        self.write_path()
        util.check_dir(str(self.counter))           

        if plot:
            util.tracePlot(mag, freqs, save, style)

        if save:       
            self.save_vna_settings()

            np.savetxt('mag.txt', mag)
            np.savetxt('freqs.txt', freqs)
            np.savetxt('phase.txt', phase)

            self.update_id()

            self.mark()
            log_info = [self.date, str(self.get_id()), self.markers[str(self.get_id())]]
            self.update_log(log_info)
        return freqs, mag, phase


class twoTonePowerSweep(singleTonePowerSweep):

    name = 'twoTonePowerSweep'

    def __init__(self, parent_dir, date, vna=None, vna_settings=None, readout_settings=None, fridge=None):
        super().__init__(parent_dir, date, vna, vna_settings, fridge)
        self.readout_settings = readout_settings


    def write_readout_settings(self, readout_settings=None):
        if self.vna:
            channel = self.vna.channels.S21
            if readout_settings:
                self.readout_settings = readout_settings
            channel.ftt_freq(self.readout_settings['readout_freq'])
            channel.ftt_power(self.readout_settings['readout_power'])

    def save_readout_settings(self):
        if self.vna:
            with open('readout_settings.csv', 'w') as f:
                for key in self.readout_settings.keys():
                    f.write("%s, %s\n" % (key, self.readout_settings[key]))


    def prepare_meas(self):
        super().prepare_meas()
        if self.vna:
            channel = self.vna.channels.S21
            #channel.ftt_on()
            channel.gen_on()

    def end_meas(self):
        if self.vna:
            channel = self.vna.channels.S21
            channel.ftt_off()

    def meas(self, powers, vna_settings=None, readout_settings=None, check_Q=True, plot=True, save=True):
        self.write_readout_settings(readout_settings)
        self.save_readout_settings(readout_settings)
        freqs, mags, phases = super().meas(self, powers, vna_settings=None, check_Q=True)
        return freqs, mags, phases

    def live_meas(self, powers, vna_settings=None, readout_settings=None, check_Q=True):
        self.write_readout_settings(readout_settings)
        self.save_readout_settings(readout_settings)
        ani, fig = super().live_meas(self, powers, vna_settings=None, check_Q=True)
        return ani, fig