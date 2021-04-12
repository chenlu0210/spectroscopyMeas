import os
import numpy as np
import matplotlib.pyplot as plt

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

def colorPlot(vals, xs, ys, save=False):
	fig, ax = plt.subplots()
	ax.set_xlabel('Freqs')
	ax.set_ylabel('Powers')
	ax.set_title('Mag')
	im = ax.imshow(vals,extent = (min(xs), max(xs), min(ys), max(ys)), 
                 origin='lower', aspect='auto')
	plt.tight_layout()
	if save:
		plt.savefig('mag_color.png')
	plt.show()

## Track cavity helper functions




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

## Grab data in files
#def grab_file(dir, file):

    	