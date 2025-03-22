# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import objects.midi_modernize.gfunc as gfunc
import objects.midi_modernize.devices_types as devices_types
from functions import value_midi

class midivis_data:
	def __init__(self):
		self.name = None
		self.color = None
		self.uses_name = False
		self.uses_color = False
		self.is_drum = False
		self.used = False
		self.name_level = 0

	def __repr__(self):
		return ('[INST' if not self.is_drum else '[DRUM')+"> Name: %s, Color: %s]" % (str(self.name), str(self.color))

	def get_color(self):
		if not self.uses_color:
			if self.used:
				return [207, 204, 209] if self.is_drum else [20, 20, 20]
			else:
				return [167, 164, 169] if self.is_drum else [10, 10, 10]
		else:
			return self.color

	def set_color_force(self, color):
		self.color = color
		self.uses_color = True

	def set_color(self, color):
		if not self.uses_color:
			self.color = color
			self.uses_color = True

	def set_name(self, name):
		if not self.uses_name:
			self.name = name
			self.uses_name = True

	def get_from_other(self, oobj, force_color, force_name):
		if (not self.uses_name or force_name) and oobj.uses_name:
			self.name = oobj.name
			self.uses_name = True
		if (not self.uses_color or force_color) and oobj.uses_color:
			self.color = oobj.color
			self.uses_color = True
		if not self.used and oobj.used:
			self.used = oobj.used

	def to_cvpj_visual(self, visual_obj):
		visual_obj.name = self.name
		visual_obj.color.set_int(self.get_color())

visual_dtype = np.dtype([
	('name', np.str_, 256),
	('color', np.uint8, 3),
	('uses_name', np.uint8),
	('uses_color', np.uint8),
	])

class visstore_data:
	instvs = ['drum','bank_hi','bank','patch','device']

	def __init__(self, num_ports, num_channels):
		self.num_ports = num_ports
		self.num_channels = num_channels
		self.vis_fxchan = [[midivis_data() for _ in range(self.num_channels)] for _ in range(self.num_ports)]
		self.vis_track = []
		self.vis_inst = []
		self.used_inst = []
		self.vis_track_chan = []

		for p in range(self.num_ports):
			for c in range(self.num_channels):
				if c != 9:
					if self.num_ports == 1: name = "Ch. #%s" % (str(c+1))
					else: name = "Port %s, Ch. #%s" % (str(p+1), str(c+1))
				else:
					if self.num_ports == 1: name = "Drum Ch."
					else: name = "Port %s, Drum Ch." % (str(p+1))

				self.vis_fxchan[p][c].name = name
			self.vis_fxchan[p][9].is_drum = True

	def setlen_track(self, n):
		self.vis_track = [midivis_data() for _ in range(n)]
		self.vis_track_chan = [-1 for _ in range(n)]

	def set_track_chan(self, n, p, c):
		self.vis_track_chan[n] = gfunc.calc_channum(c, p, self.num_channels)

	def vis_track_set_name(self, t, v):
		self.vis_track[t].set_name(v)

	def vis_track_set_color(self, t, v):
		self.vis_track[t].set_color(v)

	def vis_track_set_color_force(self, t, v):
		self.vis_track[t].set_color_force(v)

	def vis_fxchan_set_name(self, p, c, v):
		self.vis_fxchan[p][c].set_name(v)

	def vis_fxchan_set_color(self, p, c, v):
		self.vis_fxchan[p][c].set_color(v)

	def set_used_inst(self, used_inst):
		self.used_inst = used_inst
		self.vis_inst = [midivis_data() for _ in range(len(used_inst))]

		for n, x in enumerate(self.used_inst):
			outdevice = devices_types.get_devname(x['device'])
			name, color = value_midi.get_visual_inst(x['bank_hi'], x['bank'], x['patch'], x['drum'], outdevice)
			if name: self.vis_inst[n].set_name(name)
			if color: self.vis_inst[n].set_color(color)
			self.is_drum = bool(x['drum'])
			self.vis_fxchan[x['port']][x['chan']].used = True

	def iter_chanport_inst(self):
		used_inst = self.used_inst
		for po in range(self.num_ports):
			for ch in range(self.num_channels):
				chanport = gfunc.calc_channum(ch, po, self.num_channels)
				yield chanport, po, ch, np.where(self.used_inst['chanport']==chanport)[0]

	def proc__inst_to_fx(self):
		for chanport, port, chan, chanwhere in self.iter_chanport_inst():
			if len(chanwhere):
				found_inst = self.used_inst[chanwhere]
				first_inst = found_inst[0]
				first_num = chanwhere[0]
				if np.all(found_inst[visstore_data.instvs]==first_inst[visstore_data.instvs]):
					self.vis_fxchan[port][chan].get_from_other(self.vis_inst[first_num], 0, 0)

	def proc__track_to_inst(self):
		if len(self.vis_track)>1:
			for n, v in enumerate(self.vis_track):
				trackinsts_where = np.where(self.used_inst['track']==n)[0]
				if len(trackinsts_where):
					found_inst = self.used_inst[trackinsts_where]
					first_inst = found_inst[0]
					for n in trackinsts_where:
						self.vis_inst[n].get_from_other(v, 1, 0)

	def proc__track_to_fx__inst(self):
		for n, v in enumerate(self.vis_track):
			chanwhere = np.where(self.used_inst['track']==n)[0]
			if len(chanwhere):
				found_inst = self.used_inst[chanwhere]
				first_inst = found_inst[0]
				if np.all(found_inst[visstore_data.instvs]==first_inst[visstore_data.instvs]):
					p, c = gfunc.split_channum(first_inst['chanport'], self.num_channels)
					curfx = self.vis_fxchan[p][c]
					curfx.get_from_other(self.vis_inst[chanwhere[0]], 0, 0)
					if not curfx.uses_name:
						curfx.name = "Track #%i (%s)" % (n+1, curfx.name)

	def proc__track_to_fx__track(self):
		for n, v in enumerate(self.vis_track):
			chanport = self.vis_track_chan[n]
			if chanport != -1:
				p, c = gfunc.split_channum(chanport, self.num_channels)
				self.vis_fxchan[p][c].get_from_other(v, 0, 0)

	def proc__fx_to_track(self):
		for n, v in enumerate(self.vis_track):
			trackinsts_where = np.where(self.used_inst['track']==n)[0]
			if len(trackinsts_where):
				found_inst = self.used_inst[trackinsts_where]
				first_inst = found_inst[0]
				if np.all(found_inst['chanport']==first_inst['chanport']):
					p, c = gfunc.split_channum(first_inst['chanport'], self.num_channels)
					v.get_from_other(self.vis_fxchan[p][c], 0, 0)

	def proc__inst_to_track(self):
		for n, v in enumerate(self.vis_track):
			trackinsts_where = np.where(self.used_inst['track']==n)[0]
			if len(trackinsts_where):
				found_inst = self.used_inst[trackinsts_where]
				first_inst = found_inst[0]
				if np.all(found_inst[visstore_data.instvs]==first_inst[visstore_data.instvs]):
					v.get_from_other(self.vis_inst[trackinsts_where[0]], 0, 0)
