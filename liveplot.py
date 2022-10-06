from itertools import count
from meas_scripts import utilities as util
from meas_scripts import spectroscopyMeas as st
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

class livePlotter():

	vals_1 = []
	vals_2 = []
	xs = []
	ys = []
	size = 0

	def __init__(self, measType, folder, id):
		self.ani = FuncAnimation(plt.gcf(), self.animate, interval = 1000)
		self.valName = valName
		self.
		if id==0:
			self.folder = self.measurement.get_path + '\\' + str(self.measurement.get_id())
		else:
			self.folder = self.measurement.get_path + '\\' + str(id)
		util.check_dir(self.folder)
		if self.measurement.name == 'singleTonePowerSweep':
			self.xs = np.loadtxt('freqs.txt')
			self.paramSpace = np.loadtxt('powers.txt')
		if self.

	def update_vals(self):
		util.check_dir(self.folder)
		self.vals = np.loadtxt("%s.csv" %self.valName)
		self.size = len(self.vals)

	def update_ys(self):
		return self.paramSpace[:self.size]

	def animate(self, i):
		
		if self.size < len(self.paramSpace):
			
			self.update_vals()
			self.update_ys()

			plt.cla()
			plt.imshow(vals,extent = (min(xs), max(xs), min(ys), max(ys)), 
                 origin='lower', aspect='auto')

		else:
			self.ani.event_source.stop()

	def run(self):
		plt.tight_layout()
		plt.show()