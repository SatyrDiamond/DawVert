# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import notelist

LinearSlideUpTable = [0,237,475,714,953,1194,1435,1677,1920,2164,2409,2655,2902,3149,3397,3647,3897,4148,4400,4653,4907,5157,5417,5674,5932,6190,6449,6710,6971,7233,7496,7761,8026,8292,8559,8027,9096,9366,9636,9908,10181,10455,10730,11006,11283,11560,11839,12119,12400,12682,12965,13249,13533,13819,14106,14394,14684,14974,15265,15557,15850,16145,16440,16737,17034,17333,17633,17933,18235,18538,18842,19147,19454,19761,20070,20379,20690,21002,21315,21629,21944,22260,22578,22897,23216,23537,23860,24183,24507,24833,25160,25488,25817,26148,26479,26812,27146,27481,27818,28155,28494,28834,29175,29518,29862,30207,30553,30900,31248,31599,31951,32303,32657,33012,33369,33726,34085,34446,34807,35170,35534,35900,36267,36635,37004,37375,37747,38121,38496,38872,39250,39629,40009,40391,40774,41158,41544,41932,42320,42710,43102,43495,43889,44285,44682,45081,45481,45882,46285,46690,47095,47503,47917,48322,48734,49147,49562,49978,50396,50815,51236,51658,52082,52507,52934,53363,53793,54224,54658,55092,55529,55966,56406,56847,57289,57734,58179,58627,59076,59527,59979,60433,60889,61346,61805,62265,62727,63191,63657,64124,64593,65064,65536,66010,66486,66963,67442,67923,68406,68891,69377,69863,70354,70846,71339,71834,72331,72830,73330,73832,74336,74842,75350,75859,76371,76884,77399,77916,78435,78955,79478,80003,80529,81057,81587,82119,82653,83189,83727,84267,84809,85353,85898,86446,86996,87547,88101,88657,89214,89774,90336,90899,91465,91033,92603,93175,93749,94325,94903,95483,96066,96650,97237,97825,98416,99009,99604]

def calc_tracker_pitch_porta(pitch, speed):
	return (pitch/5)*((speed/6)*1.3)

def calc_tracker_pitch(pitch, speed):
	if pitch>0: return LinearSlideUpTable[pitch]*((speed/6)*0.0015)
	return 0

class autostream:
	def __init__(self):
		self.placements = []
		self.pl_pos = 0
		self.cur_pos = 0
		self.active = False

	def next(self):
		self.cur_pos += 1
		if self.placements: self.placements[-1][2] = self.cur_pos

	def do_point(self, point):
		if not self.active:
			self.active = True
			self.placements.append([self.pl_pos, [], 0])
		self.placements[-1][1].append([self.cur_pos, point])

	def add_pl(self):
		self.active = False
		self.pl_pos += self.cur_pos
		self.cur_pos = 0

	def to_cvpj(self, convproj_obj, autoloc):
		for tpl in self.placements:
			autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
			autopl_obj.time.set_posdur((tpl[0])+tpl[1][0][0], tpl[2])
			for tap in tpl[1]: 
				autopoint_obj = autopl_obj.data.add_point()
				autopoint_obj.pos = tap[0]-tpl[1][0][0]
				autopoint_obj.value = tap[1]
				autopoint_obj.type = 'instant'

class notestream:
	def __init__(self, text_inst_start):
		self.placements = []
		self.used_inst = []
		self.cur_inst = None
		self.note_active = False
		self.text_inst_start = text_inst_start
		self.cur_pos = 0
		self.note_pos = 0
		self.slide_speed = 0
		self.vol = 1
		self.freeze_inst = -1
		self.freeze_octave = 0
		self.key_to_inst = 0
		self.off_methods = {}
		self.record_off_methods = False

	def add_off_method(self, instnum, cuttype):
		if instnum not in self.off_methods: self.off_methods[instnum] = {}
		if cuttype not in self.off_methods[instnum]: self.off_methods[instnum][cuttype] = 0
		self.off_methods[instnum][cuttype] += 1

	def note_on(self, c_note, c_fx):
		self.note_active = True
		last_nl = self.placements[-1][1]
		self.note_pos = 0
		if c_fx:
			if 'vol' in c_fx: 
				self.vol = c_fx['vol']
			init_pan = c_fx['pan'] if 'pan' in c_fx else 0
		else: init_pan = 0
		if self.cur_inst != None:
			last_nl.add_m(self.text_inst_start+str(self.cur_inst), self.cur_pos, 0, c_note, self.vol, {'pan': init_pan})
		self.slide_pitch = notelist.pitchmod(c_note)

	def note_off(self):
		if self.note_active: 
			self.slide_pitch.to_points(self.placements[-1][1])
			self.note_active = False

	def do_cell_obj(self, cell_obj, s_speed):
		if cell_obj:
			self.do_cell(cell_obj.note, cell_obj.inst, cell_obj.fx, s_speed)
		else:
			self.do_cell(None, None, None, s_speed)


	def do_cell(self, c_note, c_inst, c_fx, s_speed):
		if c_fx:
			if 'freeze_inst' in c_fx: self.freeze_inst = c_fx['freeze_inst']
			if 'freeze_octave' in c_fx: self.freeze_octave = c_fx['freeze_octave']
			if 'key_to_inst' in c_fx: self.key_to_inst = c_fx['key_to_inst']

		if self.freeze_inst != -1: c_inst = self.freeze_inst
		if c_inst != None: 
			self.cur_inst = c_inst
			self.vol = 1

		if c_note != None:
			if c_note not in ['off', 'cut', 'fade']:
				new_note = True
				if c_fx:
					if 'std_slide_to_note' in c_fx and self.note_active: new_note = False
				if new_note:
					if self.freeze_octave: c_note = c_note%12
					if self.key_to_inst: self.cur_inst += c_note
					self.note_off()
					#if self.cur_inst and self.record_off_methods: 
					#	self.add_off_method(self.cur_inst, 'off')
					self.note_on(c_note if not self.key_to_inst else 0, c_fx)
				elif self.note_active: self.slide_pitch.slide_tracker_porta_targ(c_note)
			else:
				if self.record_off_methods and self.cur_inst:
					self.add_off_method(self.cur_inst, c_note)

				self.note_off()

		if c_inst != None: 
			if self.cur_inst not in self.used_inst: self.used_inst.append(self.cur_inst)

		self.cur_pos += 1
		self.placements[-1][0] += 1
		if self.note_active: 
			if c_fx:
				if 'std_slide_to_note' in c_fx:
					if c_fx['std_slide_to_note'] != 0: 
						self.slide_speed = calc_tracker_pitch_porta(c_fx['std_slide_to_note'], s_speed)
					self.slide_pitch.slide_porta(self.note_pos, self.slide_speed)

				if 'std_slide_up' in c_fx:
					if c_fx['std_slide_up'] != 0: 
						self.slide_speed = calc_tracker_pitch(c_fx['std_slide_up'], s_speed)
					self.slide_pitch.slide_up(self.note_pos, self.slide_speed)

				if 'std_slide_down' in c_fx:
					if c_fx['std_slide_down'] != 0: 
						self.slide_speed = calc_tracker_pitch(c_fx['std_slide_down'], s_speed)
					self.slide_pitch.slide_down(self.note_pos, self.slide_speed)

				if 'fine_slide_up' in c_fx:
					self.slide_speed = c_fx['fine_slide_up']/4
					self.slide_pitch.slide_up(self.note_pos, self.slide_speed)

				if 'fine_slide_down' in c_fx:
					self.slide_speed = c_fx['fine_slide_down']/4
					self.slide_pitch.slide_down(self.note_pos, self.slide_speed)

			self.note_pos += 1
			self.placements[-1][1].last_extend(1)

	def add_pl(self, patnum):
		if self.note_active: self.slide_pitch.to_points(self.placements[-1][1])
		self.placements.append([0, notelist.cvpj_notelist(4, True), patnum, self.used_inst])
		self.cur_pos = 0
		self.note_pos = 0
		self.note_active = False

