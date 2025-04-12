# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np

fxmaker_idstor = np.dtype([
	('used', np.int8),
	('chanid', np.int32),
	('mem', np.uintp),
	])

fxmaker_port = np.dtype([
	('reverb_idstor', fxmaker_idstor),
	])

fxmaker_channel = np.dtype([
	('fx__reverb__used', np.int8),
	('fx__chorus__used', np.int8),
	('fx__filter__used', np.int8),
	('fx__detune__used', np.int8),
	('fx__tremolo__used', np.int8),
	('fx__phaser__used', np.int8),
	('idstor', fxmaker_idstor),
	('val_cc', np.uint8, 128),
	('val_pressure', np.uint8),
	('val_pitch', np.int32),
	])

class fxchans_maker:
	def __init__(self, num_ports, num_channels):
		import objects.midi_modernize.ctrls as ctrls
		self.num_channels = num_channels
		self.num_ports = num_ports
		self.data_port = np.zeros((num_ports), dtype=fxmaker_port)
		self.data_channel = np.zeros((num_ports, num_channels), dtype=fxmaker_channel)
		self.data_channel['val_cc'][0:128] = ctrls.cc_defualtvals
		self.data_objs = {}

	def add_fx(self, p, c, t):
		d = self.data_channel[p][c]
		if 'reverb' in t: d['fx__reverb__used'] = 1
		if 'tremolo' in t: d['fx__tremolo__used'] = 1
		if 'chorus' in t: d['fx__chorus__used'] = 1
		if 'detune' in t: d['fx__detune__used'] = 1
		if 'phaser' in t: d['fx__phaser__used'] = 1
		if 'filter' in t: d['fx__filter__used'] = 1

	def add_obj(self, idstor, fxnum, objdata):
		idval = id(objdata)
		idstor['mem'] = idval
		idstor['chanid'] = fxnum
		idstor['used'] = 1
		self.data_objs[idval] = objdata

	def get_obj(self, idstor):
		return self.data_objs[idstor['mem']] if idstor['mem'] else None

	def generate(self, convproj_obj):
		import objects.midi_modernize.ctrls as ctrls
		calcval = ctrls.calcval

		fxchannel_obj = convproj_obj.fx__chan__add(0)
		fxchannel_obj.visual.name = "Master"
		fxchannel_obj.visual.color.set_float([0.3, 0.3, 0.3])

		fxnum = 1
		for p in range(self.num_ports):
			curd_port = self.data_port[p]

			for c in range(self.num_channels):
				curd_channel = self.data_channel[p][c]

				chan_cc = curd_channel['val_cc']

				fxchannel_obj = convproj_obj.fx__chan__add(fxnum)

				fxchannel_obj.params.add('enabled', True, 'float')
				fxchannel_obj.params.add('vol', calcval(chan_cc[7], 7), 'float')
				if chan_cc[10] != 64:
					fxchannel_obj.params.add('pan', calcval(chan_cc[10], 10), 'float')
				fxchannel_obj.params.add('modulation', calcval(chan_cc[1], 1), 'float')
				fxchannel_obj.params.add('breath', calcval(chan_cc[2], 2), 'float')
				fxchannel_obj.params.add('expression', calcval(chan_cc[11], 11), 'float')
				fxchannel_obj.params.add('sustain', calcval(chan_cc[64], 64), 'float')
				fxchannel_obj.params.add('portamento', calcval(chan_cc[65], 65), 'float')
				fxchannel_obj.params.add('sostenuto', calcval(chan_cc[66], 66), 'float')
				fxchannel_obj.params.add('soft_pedal', calcval(chan_cc[67], 67), 'float')
				fxchannel_obj.params.add('legato', calcval(chan_cc[68], 68), 'float')

				self.add_obj(curd_channel['idstor'], fxnum, fxchannel_obj)
				fxnum += 1

				if curd_channel['fx__chorus__used']:
					chorus_pluginid = '_'.join([str(p), str(c), 'chorus'])
					chorus_plugin_obj = convproj_obj.plugin__add(chorus_pluginid, 'simple', 'chorus', None)
					chorus_plugin_obj.visual.name = 'Chorus'
					chorus_plugin_obj.params.add('amount', calcval(chan_cc[93], 93), 'float')
					fxchannel_obj.plugslots.slots_audio.append(chorus_pluginid)

			if np.any(self.data_channel[p]['fx__reverb__used']):
				reverb_fxchannel_obj = convproj_obj.fx__chan__add(fxnum)
				reverb_fxchannel_obj.visual.name = 'Reverb'
				reverb_fxchannel_obj.visual_ui.other['docked'] = 1
				idval = id(reverb_fxchannel_obj)
				self.add_obj(curd_port['reverb_idstor'], fxnum, reverb_fxchannel_obj)
				reverb_pluginid = str(p)+'_reverb'
				plugin_obj = convproj_obj.plugin__add(reverb_pluginid, 'simple', 'reverb', None)
				plugin_obj.visual.name = 'Reverb'
				plugin_obj.fxdata_add(1, 0.5)
				reverb_fxchannel_obj.plugslots.slots_audio.append(reverb_pluginid)
				for c in range(self.num_channels):
					curd_channel = self.data_channel[p][c]
					chan_cc = curd_channel['val_cc']
					fxchannel_obj = self.get_obj(self.data_channel[p][c]['idstor'])
					if fxchannel_obj: fxchannel_obj.sends.add(fxnum, '_'.join([str(p), str(c), 'reverb']), calcval(chan_cc[91], 91))
				fxnum += 1

	def add_cc_vals(self, p, c, s, v):
		self.data_channel[p][c]['val_cc'][s] = v

	def make_autoloc(self, convproj_obj, autoloc_store):
		import objects.midi_modernize.automation as automation
		import objects.midi_modernize.ctrls as ctrls
		for p in range(self.num_ports):
			curd_port = self.data_port[p]
			for c in range(self.num_channels):
				curd_channel = self.data_channel[p][c]
				autoloc_store.add_fxchan(p, curd_port, c, curd_channel)

	def get_fxid(self, po, ch):
		return self.data_channel[po][ch]['idstor']['chanid']

	def get_fxobj(self, po, ch):
		return self.get_obj(self.data_channel[po][ch]['idstor'])