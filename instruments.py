from spectroscopyMeas.base_module import base_instrument

#Double check unit conversion in setting the maxim!!!
class DMM(base_instrument):
	def __init__(self, device, name='DMM', func='sense', mode='voltage', unit='V', avgs=None, maxim=None):
		super().__init__(device, name=name, func=func, mode=mode, unit=unit)
		self.set_avgs(avgs)
		self.set_maxim(maxim)

	def set_unit(self, unit=None):
		super().set_unit(unit=unit)
		#factor=instr unit/device unit
		#dmm device unit defaults are usually Amp and Volt
		#Make sure to change it if your device has different default units
		if self.unit == 'A' or self.unit == 'V':
			self.factor = 1
		if self.unit == 'mA' or self.unit == 'mV':
			self.factor = 1e-3
		if self.unit == 'uA' or self.unit == 'uV':
			self.factor = 1e-6
		if self.unit == 'nA':
			self.factor = 1e-9

	def set_avgs(self, avgs=None):
		if avgs is None:
			self.avgs = 1
			return self.avgs
		else:
			self.avgs = avgs

	def set_maxim(self, maxim=None):
		if maxim is None:
			self.maxim = 1e-3/self.factor
			return self.maxim
		else:
			self.maxim = maxim

	def get_settings(self):
		return self.__dict__.copy()

class Keithley_DMM(DMM):
	def __init__(self, device, name='Keithley6500', func='sense', mode='dc voltage', unit='V', avgs=None, maxim=None):
		super().__init__(device, name=name, func=func, mode=mode, unit=unit, avgs=avgs, maxim=maxim)


	def set_mode(self, mode=None):
		#"ac current": "CURR:AC",
		#"dc current": "CURR:DC",
		#"ac voltage": "VOLT:AC",
		#"dc voltage": "VOLT:DC",
		#"2w resistance": "RES",
		#"4w resistance": "FRES",
		#"temperature": "TEMP",
		#"frequency": "FREQ",
		super().set_mode(mode)
		self.device.mode(self.mode)

	def set_avgs(self, avgs=None):
		if avgs is None:
			self.avgs = self.device.averaging_count()
			return self.avgs
		else:
			self.avgs = avgs
			self.device.averaging_count(self.avgs)

	def set_maxim(self, maxim=None):
		if maxim is None:
			self.maxim = self.device.range()/self.factor
			return self.maxim
		else:
			self.maxim = maxim
			self.device.range(self.maxim*self.factor)

	def read_val(self):
		return self.device.amplitude()/self.factor



# Double check with driver 
class Keithley_Sense(DMM):
	def __init__(self, device, name='Keithley2450', func='sense', mode='current', unit='A', avgs=None, maxim=None):
		super().__init__(device, name=name, func=func, mode=mode, unit=unit, avgs=avgs, maxim=maxim)


	def set_mode(self, mode=None):
		#"ac current": "CURR:AC",
		#"dc current": "CURR:DC",
		#"ac voltage": "VOLT:AC",
		#"dc voltage": "VOLT:DC",
		#"2w resistance": "RES",
		#"4w resistance": "FRES",
		#"temperature": "TEMP",
		#"frequency": "FREQ",
		super().set_mode(mode)
		self.device.sense.function(mode)

	def set_avgs(self, avgs=None):
		if avgs is None:
			self.avgs = self.device.sense.count()
			return self.avgs
		else:
			self.avgs = avgs
			self.device.sense.count(self.avgs)

	def set_maxim(self, maxim=None):
		if maxim is None:
			self.maxim = self.device.range()/self.factor
			return self.maxim
		else:
			self.maxim = maxim
			self.device.sense.range(self.maxim*self.factor)

	def read_val(self):
		if self.mode == 'current':
			return self.sense.current()/self.factor
		if self.mode == 'voltage':
			return self.sense.voltage()/self.factor
		if self.mode == 'resistance':
			return self.sense.resistance()/self.factor

	def on(self):
		self.device.output_enabled(1)

	def off(self):
		self.device.output_enabled(0)

class source_unit(base_instrument):
	def __init__(self, device, name='source_unit', func='sweep', mode='voltage', unit='V', maxim=None):
		super().__init__(device, name=name, func=func, mode=mode, unit=unit)
		self.set_maxim(maxim)

	def set_unit(self, unit=None):
		super().set_unit(unit=unit)
		#factor=instr unit/device unit
		#dmm device unit defaults are usually Amp and Volt
		#Make sure to change it if your device has different default units
		if self.unit == 'A' or self.unit == 'V':
			self.factor = 1
		if self.unit == 'mA' or self.unit == 'mV':
			self.factor = 1e-3
		if self.unit == 'uA' or self.unit == 'uV':
			self.factor = 1e-6
		if self.unit == 'nA':
			self.factor = 1e-9


	def set_maxim(self, maxim=None):
		if maxim is None:
			self.maxim = 1e-3/self.factor
			return self.maxim
		else:
			self.maxim = maxim

	def get_settings(self):
		settings = self.__dict__.copy()
		if 'sweep' in self.func:
			return settings
		elif 'bias' in self.func:
			settings['val'] = self.write_val()
			return settings

	def write_val(self, val=None):
		return val


class Yokogawa(source_unit):
	def __init__(self, device, name='yokogawa', func='sweep', mode='VOLT', unit='V', maxim=None):
		super().__init__(device, name=name, func=func, mode=mode, unit=unit, maxim=maxim)

	def set_unit(self, unit=None):
		super().set_unit(unit=unit)
		#factor=instr unit/device unit
		#dmm device unit defaults are usually Amp and Volt
		#Make sure to change it if your device has different default units
		if self.unit == 'A' or self.unit == 'V':
			self.factor = 1
		if self.unit == 'mA' or self.unit == 'mV':
			self.factor = 1e-3
		if self.unit == 'uA' or self.unit == 'uV':
			self.factor = 1e-6
		if self.unit == 'nA':
			self.factor = 1e-9
    

	def set_mode(self, mode=None):
		#'VOLT' or 'CURR'
		super().set_mode(mode)
		self.device.source_mode(mode)


	def set_maxim(self, maxim=None):
		if self.mode == 'VOLT':
			if maxim is None:
				return self.device.voltage_range()/self.factor
			else:
				self.maxim = maxim
				self.device.voltage_range(self.maxim*self.factor)
		elif self.mode == 'CURR':
			if maxim is None:
				return self.device.current_range()/self.factor
			else:
				self.maxim = maxim
				self.device.current_range(self.maxim*self.factor)			


	def write_val(self, val=None):
		if self.mode == 'VOLT':
			if val is None:
				return self.device.voltage()/self.factor
			else:
				self.device.voltage(val*self.factor)
		if self.mode == 'CURR':
			if val is None:
				return self.device.current()/self.factor
			else:
				self.device.current(val*self.factor)

	def on(self):
		self.device.output('on')

	def off(self):
		self.device.output('off')



class Keithley_Source(source_unit):
	def __init__(self, device, name='Keithley2450', func='bias', mode='voltage', unit='V', avgs=None, maxim=None):
		super().__init__(device, name=name, func=func, mode=mode, unit=unit, maxim=maxim)


	def set_mode(self, mode=None):
		#"ac current": "CURR:AC",
		#"dc current": "CURR:DC",
		#"ac voltage": "VOLT:AC",
		#"dc voltage": "VOLT:DC",
		#"2w resistance": "RES",
		#"4w resistance": "FRES",
		#"temperature": "TEMP",
		#"frequency": "FREQ",
		super().set_mode(mode)
		self.device.source.function(mode)


	def set_maxim(self, maxim=None):
		if maxim is None:
			self.maxim = self.device.source.range()/self.factor
			return self.maxim
		else:
			self.maxim = maxim
			self.device.source.range(self.maxim*self.factor)

	def write_val(self, val=None):
		if self.mode == 'voltage':
			if val is None:
				return self.device.source.voltage()/self.factor
			else:
				self.device.source.voltage(val*self.factor)
		if self.mode == 'current':
			if val is None:
				return self.device.source.current()/self.factor
			else:
				self.device.source.current(val*self.factor)

	def on(self):
		self.device.output_enabled(1)

	def off(self):
		self.device.output_enabled(0)