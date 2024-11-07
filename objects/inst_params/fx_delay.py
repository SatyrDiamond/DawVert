# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import time

class fx_delay:
	def __init__(self):
		self.input = None
		self.dry = None
		self.input_pan = None
		self.stereo_offset = None
		self.cut_low = None
		self.cut_high = None
		self.feedback_invert = None
		self.feedback_first = False
		self.mode = 'normal'
		self.submode = None
		self.num_echoes = None

		self.feedback = {}
		self.feedback_cross = {}
		self.feedback_pan = {}
		self.vol = {}

		self.timings = {}

	def to_cvpj_sep(self, plugin_obj, is_sep, dname, dvalues):
		if dvalues:
			if is_sep:
				plugin_obj.datavals.add('l_'+dname, dvalues[0])
				plugin_obj.datavals.add('r_'+dname, dvalues[1])
			else:
				plugin_obj.datavals.add('c_'+dname, dvalues[0])

	def to_cvpj(self, convproj_obj, pluginid):
		if pluginid in convproj_obj.plugins: 
			on, wet = convproj_obj.plugins[pluginid].fxdata_get()
			plugin_obj = convproj_obj.plugins[pluginid]
			plugin_obj.replace('universal', 'delay', None)
		else:
			on, wet = True, 1
			if pluginid != None:
				plugin_obj = convproj_obj.plugin__add(pluginid, 'universal', 'delay', None)
			else:
				plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'delay', None)
			
		plugin_obj.role = 'fx'

		plugin_obj.datavals.add('mode', self.mode)
		plugin_obj.datavals.add('submode', self.submode)

		if self.input != None: plugin_obj.datavals.add('input', self.input)
		if self.dry != None: plugin_obj.datavals.add('dry', self.dry)
		if self.input_pan != None: plugin_obj.datavals.add('input_pan', self.input_pan)
		if self.stereo_offset != None: plugin_obj.datavals.add('stereo_offset', self.stereo_offset)
		if self.cut_low != None: plugin_obj.datavals.add('cut_low', self.cut_low)
		if self.cut_high != None: plugin_obj.datavals.add('cut_high', self.cut_high)
		if self.feedback_invert != None: plugin_obj.datavals.add('feedback_invert', self.feedback_invert)
		if self.num_echoes != None: plugin_obj.datavals.add('num_echoes', self.num_echoes)
		plugin_obj.datavals.add('feedback_first', self.feedback_first)

		traits_seperated = []
		if 1 in self.feedback: traits_seperated.append('feedback')
		if 1 in self.feedback_cross: traits_seperated.append('feedback_cross')
		if 1 in self.feedback_pan: traits_seperated.append('feedback_pan')
		if 1 in self.vol: traits_seperated.append('vol')
		if 1 in self.timings: traits_seperated.append('time')

		self.to_cvpj_sep(plugin_obj, 'feedback' in traits_seperated, 'feedback', self.feedback)
		self.to_cvpj_sep(plugin_obj, 'feedback_cross' in traits_seperated, 'feedback_cross', self.feedback_cross)
		self.to_cvpj_sep(plugin_obj, 'feedback_pan' in traits_seperated, 'feedback_pan', self.feedback_pan)
		self.to_cvpj_sep(plugin_obj, 'vol' in traits_seperated, 'vol', self.vol)

		if 'time' in traits_seperated:
			plugin_obj.timing['left'] = self.timings[0]
			plugin_obj.timing['right'] = self.timings[1]
		else:
			plugin_obj.timing['center'] = self.timings[0]

		plugin_obj.datavals.add('seperated', traits_seperated)

		plugin_obj.fxdata_add(on, wet)

		return plugin_obj, pluginid

	def timing_add(self, num): 
		self.timings[num] = time.cvpj_time()
		return self.timings[num]