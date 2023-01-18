import os
import numpy as np
import matplotlib.pyplot as plt
from resonator_tools import circuit
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.style.use('classic')

class InstrumentError(Exception):
    pass


## Unit Conversion
def mag2dB(mag):
    return 10*np.log10(mag)

def freq2GHz(freq):
    return freq*1e-9

def cur2A(current):
    return current*1e-3



def sweep(center, span, npts):
    start = center - span/2
    stop = center + span/2
    vals = np.linspace(start, stop, npts)
    return vals

## Rough version without doing proper fit
def readout_loc(mag, freqs):
    freq_max = freqs[np.argmax(mag)]
    freq_min = freqs[np.argmin(mag)]
    if freq_min > freq_max:
        ## the resonator is asymmetric and leaning to the left side
        return freq_min - (freq_min - freq_max)/3
    if freq_min < freq_max:
        ## the asymmetric resonator leans towards the right side
        return freq_min + (freq_max - freq_min)/3



## Simple Plot helper function
def tracePlot(vals, xs, save=False, style=None):
    fig, ax = plt.subplots()
    ax.set_xlabel('Freqs')
    ax.set_ylabel('Mag')
    if style:
        ax.plot(xs, vals, style)
    else:
        ax.plot(xs, vals)
    plt.tight_layout()
    if save:
        plt.savefig('mag_trace.png')
    plt.show()

def colorPlot(fig, ax, cax, vals, xs, ys, save=False):
    #ax.set_xlabel('Freqs')
    #ax.set_ylabel('Powers')
    #ax.set_title('Mag')
    im = ax.imshow(vals,extent = (min(xs), max(xs), min(ys), max(ys)), 
                 origin='lower', aspect='auto')
    fig.colorbar(im, cax=cax)
    if save:
        plt.savefig('mag_color.png')
    
def initialize_Plot():
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
## Track cavity helper functions
def fit_cavity(freqs, mag, phase, dtype='dBmagphaserad'):
    port1 = circuit.notch_port()
    port1.f_data = freqs*1e9
    port1.z_data_raw = port1._ConvToCompl(mag, phase, dtype)
    port1.autofit()
    return port1.fitresults

def find_Q(freqs, mag, phase):
    port1 = circuit.notch_port()
    port1.f_data = freqs*1e9
    port1.z_data_raw = port1._ConvToCompl(mag, phase, 'dBmagphaserad')
    port1.autofit()
    Qi = port1.fitresults['Qi_dia_corr']
    Qierr = port1.fitresults['Qi_dia_corr_err']
    Ql = port1.fitresults['Ql']
    Qlerr = port1.fitresults['Ql_err']
    return [Qi, Qierr, Ql, Qlerr]

def find_Q_GUI(freqs, mag, phase):
    port1 = circuit.notch_port()
    port1.f_data = freqs*1e9
    port1.z_data_raw = port1._ConvToCompl(mag, phase, 'dBmagphaserad')
    port1.GUIfit()


## Directory related helper functions
class PathError(Exception):
    pass

def check_dir(path):
    if os.path.isdir(path):
        print("The directory %s had been created. Transfer to the directory now." %path)
        os.chdir(path)
    else:
        os.mkdir(path)
        os.chdir(path)

def create_dir(path):
    if os.path.isdir(path):
        raise PathError("The directory %s had been created." %path)
    else:
            os.mkdir(path)

def change_dir(path):
    if os.path.isdir(path):
        os.chdir(path)
    else:
        raise PathError("The directory %s doesn't exist." %path)

def grab_file(fileName, path, skip_rows=0, dtype=str):
    change_dir(path)
    if fileName.split('.')[1] == 'csv':
        return np.loadtxt(open(os.path.join(path, fileName), "rb"), delimiter=",", skiprows=skip_rows, dtype=dtype)
    elif fileName.split('.')[1] == 'txt':
        return np.loadtxt(os.path.join(path, fileName), skiprows=skip_rows, dtype=dtype)

def save_dict(fileName, path, d, opt='w'):
    change_dir(path)
    with open(path+'//'+fileName, opt) as f:
        writer = csv.writer(f)
        writer.writerow(d.keys())
        writer.writerow(d.values())

def update_dict(d, k, v):
    if k in d:
        d[k] = [d[k]].append(v)
    else:
        d[k] = v

## Grab data in files
#def grab_file(dir, file):

        