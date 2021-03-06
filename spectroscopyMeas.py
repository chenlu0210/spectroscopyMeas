import os
from meas_scripts import utilities as util
import csv
import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt


class spectroscopyMeas:


    def __init__(self, parent_dir, date, vna, source, vna_settings, source_settings):
        self.parent_dir = parent_dir
        util.change_dir(parent_dir)
        ## home_dir path in string format
        self.date = date
        ## date in string format: ddmmyy
        self.vna = vna
        self.source = source
        ## QCODES instrument instances
        self.vna_settings = vna_settings
        self.write_vna_settings(vna_settings)
        ## vna_settings = {'avg': 10, 'band': 100, 'npts': 201, 'span': 100e3, 'center': 6.7e9, 'power': -50}
        self.source_settings = source_settings
        self.write_source_settings(source_settings)
        ## source_settings = {'status': 0, 'cur': 1e-3}

        util.check_dir(date)
        self.path = parent_dir + '\\' + date

        self.counter = 1
        self.markers = {self.date: []}

    def update_date(self, new_date):
        self.date = new_date
        util.change_dir(self.parent_dir)
        util.check_dir(self.date)
        self.path = self.parent_dir + '\\' + self.date
        self.counter = 1
        self.markers[self.date] = []

    def prepare_meas(self):
        self.vna.rf_on()

    def end_meas(self):
        self.vna.rf_off()
        self.source.off

    def grab_file(self, fileName, path=None, counter=None):
        files = []
        if not path:
            path = self.path
        if not counter:
            counter = self.counter-1
        path = path + '\\' + str(counter)
        if fileName.split('.')[1] == 'csv':
            return np.loadtxt(open(os.path.join(path, fileName), "rb"), delimiter=",")
        elif fileName.split('.')[1] == 'txt':
            return np.loadtxt(os.path.join(path, fileName))

    def mark(self, id=None):
        if id:
            self.self.markers[self.date].append(id)
        else:
            self.markers[self.date].append(self.get_id())

    def get_markers(self):
        return self.markers[self.date]

    def get_id(self):
        return self.counter - 1

    def update_id(self):
        self.counter += 1

    def get_path(self):
        return self.path

    def write_path(self):
        util.change_dir(self.path)

    def write_vna_settings(self, vna_settings=None):
        if vna_settings:
            self.vna_settings = vna_settings
        channel = self.vna.channels.S21
        channel.avg(self.vna_settings['avg'])
        channel.bandwidth(self.vna_settings['band'])
        channel.npts(self.vna_settings['npts'])
        channel.power(self.vna_settings['power'])
        channel.center(self.vna_settings['center'])
        channel.span(self.vna_settings['span'])

    def save_vna_settings(self):
        with open('vna_settings.csv', 'w') as f:
            for key in self.vna_settings.keys():
                f.write("%s, %s\n" % (key, self.vna_settings[key]))

    def write_source_settings(self, source_settings=None):
        if source_settings:
            self.source_settings = source_settings
        if self.source_settings['status']:
            self.source.on()
        else:
            self.source.off()
        self.source.current(util.cur2A(self.source_settings['cur']))

    def save_source_settings(self):
        with open('current_settings.csv', 'w') as f:
            for key in self.source_settings.keys():
                f.write("%s, %s\n" % (key, self.source_settings[key]))


class singleToneFreqSweep(spectroscopyMeas):

    name = 'singleToneFreqSweep'

    def __init__(self, parent_dir, date, vna, source, vna_settings, source_settings):
        super().__init__(parent_dir, date, vna, source, vna_settings, source_settings)

        ## For next step, check the path
        
        util.check_dir(self.name)
        self.path = self.path + '\\' + self.name

    def update_date(self, new_date):
        super().update_date(new_date)
        self.path = self.path + '\\' + self.name
        util.check_dir(self.path)


## Retrieving data
    def get_mag(self, path=None, counter=None):
        return self.grab_file('mag.txt', path, counter)

    def get_phase(self, path=None, counter=None):
        return self.grab_file('phase.txt', path, counter)

    def get_freqs(self, path=None, counter=None):
        return self.grab_file('freqs.txt', path, counter)

    def meas(self, vna_settings=None, source_settings=None, plot=True, save=True, style=None):
        channel = self.vna.channels.S21
        self.write_vna_settings(vna_settings)
        self.write_source_settings(source_settings)

        self.prepare_meas()
        
        ## Start Measurement
        amp, phase = channel.trace_mag_phase()
        #mag = 10*np.log10(mag)
        mag = util.mag2dB(amp)

        #if reduce_bg:
        #    channel.power(-70)
        #    mag_bg, phase_bg = channel.trace_mag_phase()
        #    mag = mag - util.mag2dB(mag_bg)
        #    phase = phase - phase_bg

        ## Plot and save data
        

        freqs = util.sweep(self.vna_settings['center'], self.vna_settings['span'], self.vna_settings['npts'])
        freqs = util.freq2GHz(freqs)        

        if save:
            self.write_path()
            util.check_dir(str(self.counter))            
            self.save_vna_settings()
            self.save_source_settings()

            np.savetxt('mag.txt', mag)
            np.savetxt('freqs.txt', freqs)
            np.savetxt('phase.txt', phase)

        if plot:
            util.tracePlot(mag, freqs, save, style)


        self.update_id()
        return [freqs, mag, phase]


class singleTonePowerSweep(singleToneFreqSweep):

    name = 'singleTonePowerSweep'

    def __init__(self, parent_dir, date, vna, source, vna_settings, source_settings):
        super().__init__(parent_dir, date, vna, source, vna_settings, source_settings)


    def save_vna_settings(self):
        with open('vna_settings.csv', 'w') as f:
            for key in [*self.vna_settings][:-1]:
                f.write("%s, %s\n" % (key, self.vna_settings[key]))

    
    def get_mag(self, path=None, counter=None):
        return self.grab_file('mags.csv', path, counter)

    def get_phase(self, path=None, counter=None):
        return self.grab_file('phases.csv', path, counter)

    def get_powers(self, path=None, counter=None):
        return self.grab_file('powers.txt', path, counter)

    def live_meas(self, powers, vna_settings=None, source_settings=None, check_Q = True):
        ## Initialize Plot
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
        
        self.write_path()
        util.check_dir(str(self.counter))
        self.save_vna_settings()
        self.save_source_settings()
        freqs = util.sweep(self.vna_settings['center'], self.vna_settings['span'], self.vna_settings['npts'])
        freqs = util.freq2GHz(freqs)
        np.savetxt('powers.txt', powers)
        
        def animate(i):
            p = powers[i]
            vna_settings['power'] = p
            freqs, mag, phase = super().meas(vna_settings, source_settings, False, False)
            self.counter -= 1
            
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
        
        self.update_id()

        ani = FuncAnimation(fig, animate, frames=frames, init_func=init_func, repeat=False)
        plt.tight_layout()
        plt.show()
                
            
        
        
        
    def meas(self, powers, vna_settings=None, source_settings=None, plot=True, save=True, style=None):

        channel = self.vna.channels.S21
        
        if save:
            self.write_path()
            util.check_dir(str(self.counter))

        ## Start measurement and save live data
        mags = []
        for p in powers:
            vna_settings['power'] = p
            freqs, mag, phase = super().meas(vna_settings, source_settings, False, False, style)
            self.counter -= 1
            mags.append(mag)
            with open('mags.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(mag)
            with open('phases.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(phase)
        if plot:
            util.colorPlot(mags, freqs, powers, save)

        if save:
            self.save_vna_settings()
            self.save_source_settings()
            np.savetxt('freqs.txt', freqs)
            np.savetxt('powers.txt', powers)


        self.update_id()

class singleToneCurrentSweep(singleToneFreqSweep):

    name = 'singleToneCurrentSweep'

    def __init__(self, parent_dir, date, vna, source, vna_settings, source_settings):
        super().__init__(parent_dir, date, vna, source, vna_settings, source_settings)

    def check_source_on(self):
        if self.source_settings['status']:
            print('The source is on.')
        else:
            raise util.InstrumentError("The source is off. Please turn it on.")

    def prepare_meas(self):
        super().prepare_meas()
        self.check_source_on()

    def get_mag(self, path=None, counter=None):
        return self.grab_file('mags.csv', path, counter)

    def get_phase(self, path=None, counter=None):
        return self.grab_file('phases.csv', path, counter)

    def get_currents(self, path=None, counter=None):
        return self.grab_file('currents.txt', path, counter)

    def meas(self, currents, vna_settings=None, source_settings=None, plot=True, save=True, style=None):

        channel = self.vna.channels.S21
        
        if save:
            self.write_path()
            util.check_dir(str(self.counter))
        

        ## Start measurement and save live data
        mags = []
        for c in currents:
            source_settings['cur'] = c
            freqs, mag, phase = super().meas(vna_settings, source_settings, False, False, style)
            self.counter-=1
            print(self.source_settings['cur'])
            mags.append(mag)
            with open('mags.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(mag)
            with open('phases.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(phase)
        if plot:
            util.colorPlot(mags, freqs, currents, save)

        if save:
            self.save_vna_settings()
            np.savetxt('freqs.txt', freqs)
            np.savetxt('currents.txt', currents)

        self.update_id()

class twoToneFreqSweep(spectroscopyMeas):

    name = "TwoToneFreqSweep"

    def __init__(self, parent_dir, date, vna, source, vna_settings, source_settings, readout_settings):
        super().__init__(parent_dir, date, vna, source, vna_settings, source_settings)

        ## For next step, check the path
        ## vna settings
        self.readout_settings = readout_settings
        util.check_dir(self.name)
        self.path = self.path + '\\' + self.name
        self.write_path()

    def update_date(self, new_date):
        super().update_date(new_date)
        self.path = self.path + '\\' + self.name
        util.check_dir(self.path)
        self.write_path()    

    def write_readout_settings(self, readout_settings=None):
        channel = self.vna.channels.S21
        if readout_settings:
            self.readout_settings = readout_settings
        channel.ftt_on()
        channel.gen_on()
        channel.ftt_freq(self.readout_settings['readout_freq'])
        channel.ftt_power(self.readout_settings['readout_power'])

    def save_readout_settings(self):
        with open('readout_settings.csv', 'w') as f:
            for key in self.readout_settings.keys():
                f.write("%s, %s\n" % (key, self.readout_settings[key]))

    def get_mag(self, path=None, counter=None):
        return self.grab_file('mag.txt', path, counter)

    def get_phase(self, path=None, counter=None):
        return self.grab_file('phase.txt', path, counter)

    def get_freqs(self, path=None, counter=None):
        return self.grab_file('freqs.txt', path, counter)

    def check_source_on(self):
        if self.source_settings['status']:
            print('The source is on.')
        else:
            raise util.InstrumentError("The source is off. Please turn it on.")

    def prepare_meas(self):
        self.vna.rf_on()
        self.check_source_on()


    def end_twoTone(self):
        channel = self.vna.channels.S21
        channel.gen_off()
        channel.ftt_off()

    def ref_meas(self, vna_settings=None, source_settings=None, plot=True, save=True, style=None):

        self.end_twoTone()

        channel = self.vna.channels.S21
        self.write_vna_settings(vna_settings)
        self.write_source_settings(source_settings)
        self.vna.rf_on()
        
        if save:
            self.write_path()
            util.check_dir('ref_' + str(self.counter))

        ## Start Measurement
        amp, phase = channel.trace_mag_phase()
        #mag = 10*np.log10(mag)
        mag = util.mag2dB(amp)

        #if reduce_bg:
        #    channel.power(-70)
        #    mag_bg, phase_bg = channel.trace_mag_phase()
        #    mag = mag - util.mag2dB(mag_bg)
        #    phase = phase - phase_bg

        ## Plot and save data
        

        freqs = util.sweep(self.vna_settings['center'], self.vna_settings['span'], self.vna_settings['npts'])
        freqs = util.freq2GHz(freqs)        

        if plot:
            util.tracePlot(mag, freqs, save, style)
        
        if save:
            np.savetxt('mag.txt', mag)
            np.savetxt('freqs.txt', freqs)
            np.savetxt('phase.txt', phase)
            self.save_vna_settings()
            self.save_source_settings()
        else:
            return [freqs, mag, phase]

    def meas(self, vna_settings=None, source_settings=None, readout_settings=None, plot=True, save=True, style=None):
        channel = self.vna.channels.S21
        self.write_vna_settings(vna_settings)
        self.write_source_settings(source_settings)
        self.write_readout_settings(readout_settings)

        self.prepare_meas()
        
        if save:
            self.write_path()
            util.check_dir(str(self.counter))
            self.save_vna_settings()
            self.save_source_settings()
            self.save_readout_settings()

        ## Start Measurement
        amp, phase = channel.trace_mag_phase()
        #mag = 10*np.log10(mag)
        mag = util.mag2dB(amp)

        #if reduce_bg:
        #    channel.power(-70)
        #    mag_bg, phase_bg = channel.trace_mag_phase()
        #    mag = mag - util.mag2dB(mag_bg)
        #    phase = phase - phase_bg

        ## Plot and save data
        

        freqs = util.sweep(self.vna_settings['center'], self.vna_settings['span'], self.vna_settings['npts'])
        freqs = util.freq2GHz(freqs)        

        if plot:
            util.tracePlot(mag, freqs, save, style)

        self.update_id()

        if save:
            np.savetxt('mag.txt', mag)
            np.savetxt('freqs.txt', freqs)
            np.savetxt('phase.txt', phase)
        else:
            return [freqs, mag, phase]

class twoTonePowerSweep(twoToneFreqSweep):

    name = "TwoTonePowerSweep"

    def __init__(self, parent_dir, date, vna, source, vna_settings, source_settings, readout_settings):
        super().__init__(parent_dir, date, vna, source, vna_settings, source_settings, readout_settings)

    
    def save_vna_settings(self):
        with open('vna_settings.csv', 'w') as f:
            for key in [*self.vna_settings][:-1]:
                f.write("%s, %s\n" % (key, self.vna_settings[key]))

    def get_mag(self, path=None, counter=None):
        return self.grab_file('mags.csv', path, counter)

    def get_phase(self, path=None, counter=None):
        return self.grab_file('phases.csv', path, counter)

    def get_powers(self, path=None, counter=None):
        return self.grab_file('powers.txt', path, counter)

    def meas(self, powers, vna_settings=None, source_settings=None, readout_settings=None, plot=True, save=True, style=None):

        channel = self.vna.channels.S21

        
        if save:
            self.write_path()
            util.check_dir(str(self.counter))        
        
        
## Start measurement and save live data
        mags = []
        
        for p in powers:
            vna_settings['power'] = p
            freqs, mag, phase = super().meas(vna_settings, source_settings, readout_settings, False, False, style)
            self.counter = self.counter - 1
            mags.append(mag)
            with open('mags.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(mag)
            with open('phases.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(phase)
        
        if plot:
            util.colorPlot(mags, freqs, powers, save)

        if save:
            self.save_vna_settings()
            self.save_source_settings()
            self.save_readout_settings()
            np.savetxt('powers.txt', powers)
            np.savetxt('freqs.txt', freqs)

        self.update_id()

class twoToneCurrentSweep(twoToneFreqSweep):

    name = "TwoToneCurrentSweep"

    def __init__(self, parent_dir, date, vna, source, vna_settings, source_settings, readout_settings):
        super().__init__(parent_dir, date, vna, source, vna_settings, source_settings, readout_settings)

    def get_mag(self, path=None, counter=None):
        return self.grab_file('mags.csv', path, counter)

    def get_phase(self, path=None, counter=None):
        return self.grab_file('phases.csv', path, counter)

    def get_currents(self, path=None, counter=None):
        return self.grab_file('currents.txt', path, counter)


    def meas(self, currents, vna_settings_1, vna_settings_2, source_settings, readout_settings, plot=True, save=True, style=None):

        channel = self.vna.channels.S21

        
        if save:
            self.write_path()
            util.check_dir(str(self.counter))
        #self.save_source_settings()
        #self.save_readout_settings()
        
        

        mags = []
        readout_freq = []


        ## Start measurement and save live data

        for c in currents:

            source_settings['cur'] = c
            ## Locate the initial readout freq
            freqs, mag, phase = self.ref_meas(vna_settings_2, source_settings, False, False, style)
            f = util.readout_loc(mag, freqs)
            readout_freq.append(f)
            readout_settings['readout_freq'] = f*1e9


            freqs, mag, phase = super().meas(vna_settings_1, source_settings, readout_settings, False, False, style)
            self.counter = self.counter - 1
            
            mags.append(mag)
            with open('mags.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(mag)
            with open('phases.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(phase)
            
        if plot:
            util.colorPlot(mags, freqs, currents, save)

        if save:
            self.save_vna_settings()
            np.savetxt('currents.txt', currents)
            np.savetxt('freqs.txt', freqs)
            np.savetxt('readout_freqs.txt', readout_freq)

        self.update_id()
