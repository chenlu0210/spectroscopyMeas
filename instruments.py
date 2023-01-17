from Res_Meas.base_module import base_instrument

class DMM(base_instrument):
	def __init__(self, device, name='DMM', func='Sense', mode='voltage', unit='V', avgs=None, maxim=None):
        super().__init__(device, name, func, mode, unit)
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
		if self.unit == 'uA':
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
	def __init__(self, device, name='Keithley6500', func='Sense', mode='dc voltage', unit='V', avgs=None, maxim=None):
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
			self.maxim = maxim*self.factor
			self.device.range(self.maxim)

    def read_val(self):
		return self.device.amplitude()/self.factor


# Update this 
class Keithley_Sense(DMM):
	def __init__(self, device, name='Keithley2450', func='Sense', mode='dc voltage', unit='V', avgs=None, maxim=None):
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
			self.maxim = maxim*self.factor
			self.device.range(self.maxim)

    def read_val(self):
		return self.device.amplitude()/self.factor


                                                                           