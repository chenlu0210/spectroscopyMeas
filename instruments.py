from Res_Meas.base_module import base_instrument

class DMM(base_instrument):
	def __init__(self, device, name='DMM', func='sense', mode='voltage', unit='V', avgs=None, maxim=None):
        super().__init__(device, name=name, func=func, mode=mode, unit=unit)
        self.set_avgs(avgs)
        self.set_maxim(maxim)

    def set_unit(self, unit=None):
        super().set_unit()
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
			self.maxim = 1e-3
			return self.maxim
		else:
			self.maxim = maxim*self.factor

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
			self.maxim = self.device.range()
			return self.maxim
		else:
			self.maxim = maxim
			self.device.range(self.maxim*self.factor)

    def read_val(self):
		return self.device.amplitude()/self.factor



# Double check with driver 
class Keithley_Sense(DMM):
	def __init__(self, device, name='Keithley2450', func='sense', mode='current', unit='A', avgs=None, maxim=None):
        super().__init__(device, name, func, mode, unit, avgs, maxim)


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
    	self.device.sense_function(mode)

	def set_avgs(self, avgs=None):
		if avgs is None:
			self.avgs = self.device.sense.count()
			return self.avgs
		else:
			self.avgs = avgs
			self.device.sense.count(self.avgs)

	def set_maxim(self, maxim=None):
		if maxim is None:
			self.maxim = self.device.sense.range()
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
        super().set_unit()
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
			self.maxim = 1e-3
			return self.maxim
		else:
			self.maxim = maxim

    def get_settings(self):
    	settings = self.__dict__.copy()
    	if 'sweep' in self.func:
    		return settings
        elif 'bias' in self.func:
        	settings['bias'] = self.write_val()
        	return settings

    def write_val(self, val=None):
    	return val


class Yokogawa(source_unit):
	def __init__(self, device, name='yokogawa', func='sweep', mode='VOLT', unit='V', maxim=None):
        super().__init__(device, name=name, func=func, mode=mode, unit=unit, maxim=maxim)

    def set_unit(self, unit=None):
        super().set_unit()
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
				return self.device.voltage_range()
			else:
				self.maxim = maxim
				self.device.voltage_range(self.maxim*self.factor)
		elif self.mode == 'CURR':
			if maxim is None:
				return self.device.current_range()
			else:
				self.maxim = maxim*self.factor
				self.device.current_range(self.maxim)			


    def write_val(self, val=None):
    	if self.mode == 'VOLT':
    		if val is None:
    			return self.device.voltage()
    		else:
    			self.device.voltage(val*self.factor)
    	if self.mode == 'CURR':
    		if val is None:
    			return self.device.current()
    		else:
    			self.device.current(val*self.factor)

    def on(self):
    	self.device.ouput(1)

    def off(self):
    	self.device.output(0)



class Keithley_Source(source_unit):
	def __init__(self, device, name='Keithley2450', func='bias', mode='voltage', unit='V', avgs=None, maxim=None):
        super().__init__(device, name, func, mode, unit, avgs, maxim)


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
    	self.device.source_function(mode)


	def set_maxim(self, maxim=None):
		if maxim is None:
			self.maxim = self.device.source.range()
			return self.maxim
		else:
			self.maxim = maxim
			self.device.source.range(self.maxim*self.factor)

    def write_val(self, val=None):
    	if self.mode == 'VOLT':
    		if val is None:
    			return self.device.source.voltage()
    		else:
    			self.device.source.voltage(val*self.factor)
    	if self.mode == 'CURR':
    		if val is None:
    			return self.device.source.current()
    		else:
    			self.device.source.current(val*self.factor)

	def on(self):
		self.device.output_enabled(1)

	def off(self):
		self.device.output_enabled(0)