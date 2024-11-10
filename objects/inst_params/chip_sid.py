# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

sid_att = [2, 8, 16, 24, 38, 56, 68, 80, 100, 250, 500, 800, 1000, 3000, 5000, 8000]
sid_decrel = [6, 24, 48, 72, 114, 168, 204, 240, 300, 750, 1500, 2400, 3000, 9000, 15000, 24000]
sid_wave = ['square', 'triangle', 'saw', 'noise_4bit']

class sid_osc:
	def __init__(self):
		self.on = 0
		self.wave_pulse = 0
		self.wave_triangle = 0
		self.wave_saw = 0
		self.wave_noise = 0
		self.coarse = 0
		self.attack = 0
		self.decay = 0
		self.sustain = 0
		self.release = 0
		self.pulse_width = 0
		self.ringmod = 0
		self.syncmod = 0
		self.to_filter = 0
		self.volume_to_cutoff = 0
		self.filterval_inst = 0

class sid_inst:
	def __init__(self):
		self.num_oscs = 3
		self.oscs = [sid_osc() for _ in range(3)]
		self.filter_resonance = 0
		self.filter_cutoff = 0
		self.filter_mode = 0

	def to_cvpj(self, convproj_obj, pluginid):
		plugin_obj = convproj_obj.plugin__add(pluginid, 'chip', 'sid', None)

		plugin_obj.params.add('filter_resonance', self.filter_resonance, 'int')
		plugin_obj.params.add('filter_cutoff', self.filter_cutoff, 'int')
		plugin_obj.params.add('filter_mode', self.filter_mode, 'int')

		for opnum, oscdata in enumerate(self.oscs):
			oppv = 'osc'+str(opnum)+'/'
			plugin_obj.params.add(oppv+'on', oscdata.on, 'int')
			plugin_obj.params.add(oppv+'wave_pulse', oscdata.wave_pulse, 'int')
			plugin_obj.params.add(oppv+'wave_triangle', oscdata.wave_triangle, 'int')
			plugin_obj.params.add(oppv+'wave_saw', oscdata.wave_saw, 'int')
			plugin_obj.params.add(oppv+'wave_noise', oscdata.wave_noise, 'int')
			plugin_obj.params.add(oppv+'coarse', oscdata.coarse, 'int')
			plugin_obj.params.add(oppv+'attack', oscdata.attack, 'int')
			plugin_obj.params.add(oppv+'decay', oscdata.decay, 'int')
			plugin_obj.params.add(oppv+'sustain', oscdata.sustain, 'int')
			plugin_obj.params.add(oppv+'release', oscdata.release, 'int')
			plugin_obj.params.add(oppv+'pulse_width', oscdata.pulse_width, 'int')
			plugin_obj.params.add(oppv+'ringmod', oscdata.ringmod, 'int')
			plugin_obj.params.add(oppv+'syncmod', oscdata.syncmod, 'int')
			plugin_obj.params.add(oppv+'to_filter', oscdata.to_filter, 'int')
			plugin_obj.params.add(oppv+'volume_to_cutoff', oscdata.volume_to_cutoff, 'int')
			plugin_obj.params.add(oppv+'filterval_inst', oscdata.filterval_inst, 'int')

			sid_attack = sid_att[int(oscdata.attack)]/1000
			sid_decay = sid_decrel[int(oscdata.decay)]/1000
			sid_sustain = oscdata.sustain/15
			sid_release = sid_decrel[int(oscdata.release)]/1000

			asdr_name = 'osc'+str(opnum)
			plugin_obj.env_asdr_add(asdr_name, 0, sid_attack, 0, sid_decay, sid_sustain, sid_release, 1)

		return plugin_obj










