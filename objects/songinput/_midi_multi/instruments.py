# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np
from objects.data_bytes import structalloc

instrument_premake = structalloc.dynarray_premake([
	('track', np.uint8),
	('chan', np.uint8),
	('drum', np.uint8),
	('bank', np.uint8),
	('bank_hi', np.uint8),
	('inst', np.uint8),
	('is_custom', np.uint8),
	('custom_name', np.str_, 128),
	('custom_color_used', np.uint8),
	('custom_color', np.uint8, 3)])

class midi_instruments:
	def __init__(self):
		self.midi_instruments = instrument_premake.create()

	def add_instrument(self, i_track, i_chan, i_bank, i_bank_hi, i_patch, i_drum):
		self.midi_instruments.add()
		self.midi_instruments['track'] = i_track
		self.midi_instruments['chan'] = i_chan
		self.midi_instruments['drum'] = i_drum
		self.midi_instruments['bank'] = i_bank
		self.midi_instruments['bank_hi'] = i_bank_hi
		self.midi_instruments['inst'] = i_patch

	def to_cvpj(self, convproj_obj, device, fx_offset):
		self.midi_instruments.clean()

		for inst in self.midi_instruments:
			instid = '_'.join([
				str(inst['track']), 
				str(inst['chan']), 
				str(inst['inst']), 
				str(inst['bank']), 
				str(inst['bank_hi']), 
				str(inst['drum'])])
			midiinst = int(inst['inst']) if inst['inst']!=255 else 0

			inst_obj = convproj_obj.instrument__add(instid)

			inst_obj.visual.name = inst['custom_name'] if inst['custom_name'] else None
			if inst['custom_color_used']: 
				inst_obj.visual.color.set_int([x for x in inst['custom_color']])
			inst_obj.visual.from_dset_midi(inst['bank_hi'], inst['bank'], midiinst, inst['drum'], device, False)

			plugin_obj = convproj_obj.plugin__addspec__midi(instid, int(inst['bank_hi']), int(inst['bank']), int(midiinst), int(inst['drum']), device)
			plugin_obj.role = 'synth'
			inst_obj.pluginid = instid
			inst_obj.fxrack_channel = int(inst['chan'])+1+fx_offset

			if inst['drum']: inst_obj.visual.color.set_float([0.81, 0.80, 0.82])

	def get_idx(self, idxnum):
		return self.midi_instruments.data[idxnum]

	def find_idx_track(self, tracknum):
		return np.where(self.midi_instruments.data['track']==tracknum)[0]

	def find_idx_chan(self, usedchan):
		return np.where(self.midi_instruments.data['chan']==usedchan)[0]

	def get_single_trackinst(self, tracknum):
		sametrknum = self.find_idx_track(tracknum)
		if len(sametrknum)==1:
			i = self.get_idx(sametrknum[0])
			return [str(i['bank_hi']),str(i['bank']),str(i['inst']),str(i['drum']),str(i['chan'])]
