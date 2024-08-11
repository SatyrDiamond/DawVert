# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes

t_retg_alg = [['mul', 1], ['minus', 1], ['minus', 2], ['minus', 4], ['minus', 8], ['minus', 16], ['mul', 2/3], ['mul', 1/2], ['mul', 1], ['plus', 1], ['plus', 2], ['plus', 4], ['plus', 8], ['plus', 16], ['mul', 3/2], ['mul', 2]]

LinearSlideUpTable = [0,237,475,714,953,1194,1435,1677,1920,2164,2409,2655,2902,3149,3397,3647,3897,4148,4400,4653,4907,5157,5417,5674,5932,6190,6449,6710,6971,7233,7496,7761,8026,8292,8559,8027,9096,9366,9636,9908,10181,10455,10730,11006,11283,11560,11839,12119,12400,12682,12965,13249,13533,13819,14106,14394,14684,14974,15265,15557,15850,16145,16440,16737,17034,17333,17633,17933,18235,18538,18842,19147,19454,19761,20070,20379,20690,21002,21315,21629,21944,22260,22578,22897,23216,23537,23860,24183,24507,24833,25160,25488,25817,26148,26479,26812,27146,27481,27818,28155,28494,28834,29175,29518,29862,30207,30553,30900,31248,31599,31951,32303,32657,33012,33369,33726,34085,34446,34807,35170,35534,35900,36267,36635,37004,37375,37747,38121,38496,38872,39250,39629,40009,40391,40774,41158,41544,41932,42320,42710,43102,43495,43889,44285,44682,45081,45481,45882,46285,46690,47095,47503,47917,48322,48734,49147,49562,49978,50396,50815,51236,51658,52082,52507,52934,53363,53793,54224,54658,55092,55529,55966,56406,56847,57289,57734,58179,58627,59076,59527,59979,60433,60889,61346,61805,62265,62727,63191,63657,64124,64593,65064,65536,66010,66486,66963,67442,67923,68406,68891,69377,69863,70354,70846,71339,71834,72331,72830,73330,73832,74336,74842,75350,75859,76371,76884,77399,77916,78435,78955,79478,80003,80529,81057,81587,82119,82653,83189,83727,84267,84809,85353,85898,86446,86996,87547,88101,88657,89214,89774,90336,90899,91465,91033,92603,93175,93749,94325,94903,95483,96066,96650,97237,97825,98416,99009,99604]

def splitparams(value, firstname, secondname):
	dualparams = {}
	dualparams[firstname], dualparams[secondname] = data_bytes.splitbyte(value)
	return dualparams

def getfineval(value):
	volslidesplit = data_bytes.splitbyte(value)
	volslideout = 0
	if volslidesplit[0] == 0 and volslidesplit[1] == 0: volslideout = 0
	elif volslidesplit[0] == 15 and volslidesplit[1] == 15: volslideout = volslidesplit[0]/16
	elif volslidesplit[0] == 0 and volslidesplit[1] == 15: volslideout = -15
	elif volslidesplit[0] == 0 and volslidesplit[1] != 0: volslideout = volslidesplit[1]*-1
	elif volslidesplit[0] != 0 and volslidesplit[1] == 0: volslideout = volslidesplit[0]
	elif volslidesplit[0] == 15 and volslidesplit[1] != 15: volslideout = (volslidesplit[0]*-1)/16
	elif volslidesplit[0] != 15 and volslidesplit[1] == 15: volslideout = volslidesplit[0]/16
	return volslideout

def addminusval(i_val):
	pos, neg = data_bytes.splitbyte(i_val)
	return (neg*-1) + pos

class tracker_channel:
	def __init__(self):
		self.name = None
		self.color = None
		self.type = None
		self.vol = 1
		self.pan = 0
		self.fx_plugins = []

class tracker_cell:
	__slots__ = ['note', 'inst', 'fx', 'g_fx']
	def __init__(self):
		self.note = None
		self.inst = None
		self.fx = None
		self.g_fx = None

class tracker_column:
	def __init__(self):
		self.data = {}

	def auto_cell(self, row_num):
		if row_num not in self.data: self.data[row_num] = tracker_cell()
		return self.data[row_num]

	def cell_note(self, row_num, note, inst):
		row = self.auto_cell(row_num)
		row.note = note
		row.inst = inst

	def cell_param(self, row_num, p_name, p_val):
		row = self.auto_cell(row_num)
		if row.fx == None: row.fx = {}
		row.fx[p_name] = p_val

	def cell_g_param(self, row_num, p_name, p_val):
		row = self.auto_cell(row_num)
		if row.g_fx == None: row.g_fx = {}
		row.g_fx[p_name] = p_val

	def cell_fx_mod(self, row_num, fx_type, fx_value):
		if fx_type == 1: self.cell_param(row_num, 'slide_up', fx_value)
		if fx_type == 2: self.cell_param(row_num, 'slide_down', fx_value)
		if fx_type == 3: self.cell_param(row_num, 'slide_to_note', fx_value)
		if fx_type == 4: self.cell_param(row_num, 'vibrato', splitparams(fx_value, 'speed', 'depth'))
		if fx_type == 6: self.cell_param(row_num, 'vol_slide', addminusval(fx_value))
		if fx_type == 7: self.cell_param(row_num, 'tremolo', splitparams(fx_value, 'speed', 'depth'))
		if fx_type == 8: self.cell_param(row_num, 'pan', (fx_value-128)/128)
		if fx_type == 9: self.cell_param(row_num, 'sample_offset', fx_value*256)
		if fx_type == 10: self.cell_param(row_num, 'vol_slide', addminusval(fx_value))

		if fx_type == 0 and fx_value != 0:
			arpeggio_first, arpeggio_second = data_bytes.splitbyte(fx_value)
			self.cell_param(row_num, 'arp', [arpeggio_first, arpeggio_second])

		if fx_type == 5:
			valueout = addminusval(fx_value) 
			self.cell_param(row_num, 'vol_slide', valueout)
			self.cell_param(row_num, 'slide_to_note', valueout)

		if fx_type == 14: 
			ext_type, ext_value = data_bytes.splitbyte(fx_value)
			if ext_type == 0: self.cell_param(row_num, 'filter_amiga_led', ext_value)
			if ext_type == 1: self.cell_param(row_num, 'fine_slide_up', ext_value)
			if ext_type == 2: self.cell_param(row_num, 'fine_slide_down', ext_value)
			if ext_type == 3: self.cell_param(row_num, 'glissando_control', ext_value)
			if ext_type == 4: self.cell_param(row_num, 'vibrato_waveform', ext_value)
			if ext_type == 5: self.cell_param(row_num, 'set_finetune', ext_value)
			if ext_type == 6: self.cell_param(row_num, 'pattern_loop', ext_value)
			if ext_type == 7: self.cell_param(row_num, 'tremolo_waveform', ext_value)
			if ext_type == 8: self.cell_param(row_num, 'set_pan', ext_value)
			if ext_type == 9: self.cell_param(row_num, 'retrigger_note', ext_value)
			if ext_type == 10: self.cell_param(row_num, 'fine_vol_slide_up', ext_value)
			if ext_type == 11: self.cell_param(row_num, 'fine_vol_slide_down', ext_value)
			if ext_type == 12: self.cell_param(row_num, 'note_cut', ext_value)
			if ext_type == 13: self.cell_param(row_num, 'note_delay', ext_value)
			if ext_type == 14: self.cell_param(row_num, 'pattern_delay', ext_value)
			if ext_type == 15: self.cell_param(row_num, 'invert_loop', ext_value)

	def cell_fx_s3m(self, row_num, fx_type, fx_value):
		if fx_type == 1: self.cell_g_param(row_num, 'speed', fx_value)
		if fx_type == 2: self.cell_g_param(row_num, 'pattern_jump', fx_value)
		if fx_type == 3: self.cell_g_param(row_num, 'break_to_row', fx_value)
		if fx_type == 4: self.cell_param(row_num, 'vol_slide', getfineval(fx_value))
		if fx_type == 5: 
			if 240 <= fx_value:		 self.cell_param(row_num, 'fine_slide_down', (fx_value-240)/8)
			if 224 <= fx_value <= 239:  self.cell_param(row_num, 'fine_slide_down', (fx_value-224)/16)
			else:					   self.cell_param(row_num, 'slide_down', fx_value)
		if fx_type == 6: 
			if 240 <= fx_value:		 self.cell_param(row_num, 'fine_slide_up', (fx_value-240)/8)
			if 224 <= fx_value <= 239:  self.cell_param(row_num, 'fine_slide_up', (fx_value-224)/16)
			else:					   self.cell_param(row_num, 'slide_up', fx_value)
		if fx_type == 7: self.cell_param(row_num, 'slide_to_note', fx_value)
		if fx_type == 8: self.cell_param(row_num, 'vibrato', splitparams(fx_value, 'speed', 'depth'))
		if fx_type == 9: self.cell_param(row_num, 'tremor', splitparams(fx_value, 'ontime', 'offtime'))
		if fx_type == 11: self.cell_param(row_num, 'vol_slide', getfineval(fx_value))
		if fx_type == 13: self.cell_param(row_num, 'channel_vol', fx_value/64)
		if fx_type == 14: self.cell_param(row_num, 'channel_vol_slide', getfineval(fx_value))
		if fx_type == 15: self.cell_param(row_num, 'sample_offset', fx_value*256)
		if fx_type == 16: self.cell_param(row_num, 'pan_slide', getfineval(fx_value)*-1)
		if fx_type == 18: self.cell_param(row_num, 'tremolo', splitparams(fx_value, 'speed', 'depth'))
		if fx_type == 22: self.cell_g_param(row_num, 'global_volume', fx_value/64)
		if fx_type == 23: self.cell_g_param(row_num, 'global_volume_slide', getfineval(fx_value))
		if fx_type == 24: self.cell_param(row_num, 'set_pan', fx_value/255)
		if fx_type == 25: self.cell_param(row_num, 'panbrello', splitparams(fx_value, 'speed', 'depth'))

		if fx_type == 10:
			arpeggio_first, arpeggio_second = data_bytes.splitbyte(fx_value)
			self.cell_param(row_num, 'arp', [arpeggio_first, arpeggio_second])

		if fx_type == 12:
			self.cell_param(row_num, 'vol_slide', getfineval(fx_value))
			self.cell_param(row_num, 'slide_to_note', getfineval(fx_value))

		if fx_type == 17:
			retrigger_params = {}
			retrigger_alg, retrigger_params['speed'] = data_bytes.splitbyte(fx_value)
			retrigger_params['alg'], retrigger_params['val'] = t_retg_alg[retrigger_alg]
			self.cell_param(row_num, 'retrigger', retrigger_params)
	
		if fx_type == 19: 
			ext_type, ext_value = data_bytes.splitbyte(fx_value)
			if ext_type == 1: self.cell_param(row_num, 'glissando_control', ext_value)
			if ext_type == 3: self.cell_param(row_num, 'vibrato_waveform', ext_value)
			if ext_type == 4: self.cell_param(row_num, 'tremolo_waveform', ext_value)
			if ext_type == 5: self.cell_param(row_num, 'panbrello_waveform', ext_value)
			if ext_type == 6: self.cell_param(row_num, 'fine_pattern_delay', ext_value)
			if ext_type == 7: self.cell_param(row_num, 'it_inst_control', ext_value)
			if ext_type == 8: self.cell_param(row_num, 'set_pan', ext_value/16)
			if ext_type == 9: self.cell_param(row_num, 'it_sound_control', ext_value)
			if ext_type == 10: self.cell_param(row_num, 'sample_offset_high', ext_value*65536)
			if ext_type == 11: self.cell_param(row_num, 'loop_start', ext_value)
			if ext_type == 12: self.cell_param(row_num, 'note_cut', ext_value)
			if ext_type == 13: self.cell_param(row_num, 'note_delay', ext_value)
			if ext_type == 14: self.cell_param(row_num, 'pattern_delay', ext_value)
			if ext_type == 15: self.cell_param(row_num, 'it_active_macro', ext_value)
