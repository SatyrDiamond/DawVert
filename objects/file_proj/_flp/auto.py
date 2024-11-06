# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.data_bytes import bytereader

class flp_autoloc:
	def __init__(self):
		self.loc = []
		self.debugprint = False

	def to_loctxt(self):
		return '/'.join([str(x) for x in self.loc])

	def decode(self, i_loc):
		i_control = i_loc&0xffff
		i_group = (i_loc&0xffff0000)>>16
		group_type = i_group>>13
		if group_type == 0: 
			group = i_group&0x0fff
			control_group = i_control>>13
			control = i_control&0x0fff
			ctrl_s_g = i_control>>8
			ctrl_s_p = i_control&0xff
			self.loc.append('chan')
			self.loc.append(group)
			if control_group == 0:

				if ctrl_s_g == 0:
					self.loc.append('param')
					if ctrl_s_p == 0: self.loc.append('vol')
					elif ctrl_s_p == 1: self.loc.append('pan')
					elif ctrl_s_p == 2: self.loc.append('mod_x')
					elif ctrl_s_p == 3: self.loc.append('mod_y')
					elif ctrl_s_p == 4: self.loc.append('pitch')
					elif ctrl_s_p == 5: self.loc.append('filt_type')
					elif ctrl_s_p == 6: self.loc.append('poly_slide')
					elif ctrl_s_p == 7: self.loc.append('mute')
					elif ctrl_s_p == 8: self.loc.append('fxrack')
					elif ctrl_s_p == 9: self.loc.append('time_gate')
					elif ctrl_s_p == 11: self.loc.append('time_shift')
					elif ctrl_s_p == 12: self.loc.append('time_swing')
					elif ctrl_s_p == 13: self.loc.append('startoffset')
					elif ctrl_s_p == 14: self.loc.append('stretchtime')
					elif ctrl_s_p == 16: self.loc.append('adjust_vol')
					elif ctrl_s_p == 17: self.loc.append('adjust_pan')
					elif ctrl_s_p == 19: self.loc.append('adjust_mod_x')
					elif ctrl_s_p == 20: self.loc.append('adjust_mod_y')
					else: self.loc.append('unknown'+str(ctrl_s_p))

				elif ctrl_s_g == 2:
					self.loc.append('echofat')
					if ctrl_s_p == 0: self.loc.append('feed')
					elif ctrl_s_p == 1: self.loc.append('pan')
					elif ctrl_s_p == 6: self.loc.append('modx')
					elif ctrl_s_p == 5: self.loc.append('mody')
					elif ctrl_s_p == 2: self.loc.append('pitch')
					elif ctrl_s_p == 4: self.loc.append('time')
					elif ctrl_s_p == 3: self.loc.append('echoes')
					else: self.loc.append('unknown'+str(ctrl_s_p))

				elif ctrl_s_g == 3:
					self.loc.append('arp')
					if ctrl_s_p == 0: self.loc.append('type')
					elif ctrl_s_p == 3: self.loc.append('time')
					elif ctrl_s_p == 4: self.loc.append('gate')
					elif ctrl_s_p == 1: self.loc.append('range')
					elif ctrl_s_p == 5: self.loc.append('repeat')
					elif ctrl_s_p == 2: self.loc.append('chord')
					else: self.loc.append('unknown'+str(ctrl_s_p))

				elif ctrl_s_g == 5:
					self.loc.append('tracking')
					if ctrl_s_p == 0: self.loc.append('vol_pan')
					elif ctrl_s_p == 1: self.loc.append('vol_modx')
					elif ctrl_s_p == 2: self.loc.append('vol_mody')
					elif ctrl_s_p == 16: self.loc.append('key_pan')
					elif ctrl_s_p == 17: self.loc.append('key_modx')
					elif ctrl_s_p == 18: self.loc.append('key_mody')
					else: self.loc.append('unknown'+str(ctrl_s_p))

				elif ctrl_s_g in [17,18,19,20]:
					self.loc.append('envlfo')
					if ctrl_s_g == 17: self.loc.append('vol')
					elif ctrl_s_g == 18: self.loc.append('modx')
					elif ctrl_s_g == 19: self.loc.append('mody')
					elif ctrl_s_g == 20: self.loc.append('pitch')

					if ctrl_s_p == 2: self.loc.append('env_delay')
					elif ctrl_s_p == 3: self.loc.append('env_att')
					elif ctrl_s_p == 4: self.loc.append('env_hold')
					elif ctrl_s_p == 5: self.loc.append('env_dec')
					elif ctrl_s_p == 6: self.loc.append('env_sus')
					elif ctrl_s_p == 7: self.loc.append('env_rel')
					elif ctrl_s_p == 8: self.loc.append('env_amount')
					elif ctrl_s_p == 9: self.loc.append('lfo_predelay')
					elif ctrl_s_p == 10: self.loc.append('lfo_att')
					elif ctrl_s_p == 11: self.loc.append('lfo_amount')
					elif ctrl_s_p == 12: self.loc.append('lfo_speed')
					elif ctrl_s_p == 14: self.loc.append('env_att_ten')
					elif ctrl_s_p == 15: self.loc.append('env_dec_ten')
					elif ctrl_s_p == 16: self.loc.append('env_rel_ten')
					else: self.loc.append('unknown'+str(ctrl_s_p))

				else:
					self.loc.append('unknown'+str(ctrl_s_g))
			elif control_group == 4:
				if ctrl_s_g > 127:
					self.loc.append('plugin')
					self.loc.append(i_control-32768)
				else: self.loc.append('unknown'+str(ctrl_s_g))
			else: self.loc.append('unknown'+str(control_group))
		elif group_type == 1: 
			self.loc.append('fx')
			fxnum = (i_group>>6)-128
			fxslot = i_group&0xf
			fxparam = i_control&0xff
			fxpgrp = fxparam>>6
			fxparam = fxparam&0x3f

			self.loc.append(fxnum)

			if fxpgrp == 0:
				if i_control>>15:
					self.loc.append('plugin')
					self.loc.append(fxslot)
					self.loc.append(i_control-32768)
				else:
					self.loc.append('slot')
					self.loc.append(fxslot)
					if fxparam == 1: self.loc.append('wet')
					elif fxparam == 0: self.loc.append('on')
					else: self.loc.append('unknown'+str(fxparam))
			elif fxpgrp == 1:
				self.loc.append('route')
				self.loc.append(fxparam)
			elif fxpgrp == 2:
				self.loc.append('route')
				self.loc.append(fxparam+64)
			elif fxpgrp == 3:
				self.loc.append('param')
				if fxparam == 0: self.loc.append('vol')
				elif fxparam == 1: self.loc.append('pan')
				elif fxparam == 2: self.loc.append('stereo_sep')
				elif fxparam == 24: self.loc.append('eq1_freq')
				elif fxparam == 25: self.loc.append('eq2_freq')
				elif fxparam == 26: self.loc.append('eq3_freq')
				elif fxparam == 32: self.loc.append('eq1_width')
				elif fxparam == 33: self.loc.append('eq2_width')
				elif fxparam == 34: self.loc.append('eq3_width')
				elif fxparam == 16: self.loc.append('eq1_level')
				elif fxparam == 17: self.loc.append('eq2_level')
				elif fxparam == 18: self.loc.append('eq3_level')
				else: self.loc.append('unknown'+str(fxparam))
			else: 
				self.loc.append('unknown'+str(fxpgrp))
		elif group_type == 2: 
			control_group = i_control>>13
			control = i_control&0x0fff

			self.loc.append('main')
			if control == 0: self.loc.append('vol')
			elif control == 1: self.loc.append('swing')
			elif control == 2: self.loc.append('pitch')
			elif control == 5: self.loc.append('tempo')
			else: self.loc.append('unknown'+str(control))
		else: self.loc.append('unknown'+str(group_type))
		if self.debugprint: print(i_control.to_bytes(2, 'big')[::-1].hex()+i_group.to_bytes(2, 'big')[::-1].hex(),'|',i_control, i_group, '|',self.loc )

	def encode(self):
		valid_auto = True
		icrc_control = 0
		icrc_group = 0
		if self.loc[0] == 'chan':
			icrc_group = self.loc[1]
			if self.loc[2] == 'param':
				if self.loc[3] == 'vol': icrc_control = 0
				elif self.loc[3] == 'pan': icrc_control = 1
				elif self.loc[3] == 'mod_x': icrc_control = 2
				elif self.loc[3] == 'mod_y': icrc_control = 3
				elif self.loc[3] == 'pitch': icrc_control = 4
				elif self.loc[3] == 'filt_type': icrc_control = 5
				elif self.loc[3] == 'poly_slide': icrc_control = 6
				elif self.loc[3] == 'mute': icrc_control = 7
				elif self.loc[3] == 'fxrack': icrc_control = 8
				elif self.loc[3] == 'time_gate': icrc_control = 9
				elif self.loc[3] == 'time_shift': icrc_control = 11
				elif self.loc[3] == 'time_swing': icrc_control = 12
				elif self.loc[3] == 'startoffset': icrc_control = 13
				elif self.loc[3] == 'stretchtime': icrc_control = 14
				elif self.loc[3] == 'adjust_vol': icrc_control = 16
				elif self.loc[3] == 'adjust_pan': icrc_control = 17
				elif self.loc[3] == 'adjust_mod_x': icrc_control = 19
				elif self.loc[3] == 'adjust_mod_y': icrc_control = 20
			elif self.loc[2] == 'echofat':
				icrc_control += 512
				if self.loc[3] == 'feed': icrc_control += 0
				elif self.loc[3] == 'pan': icrc_control += 1
				elif self.loc[3] == 'modx': icrc_control += 6
				elif self.loc[3] == 'mody': icrc_control += 5
				elif self.loc[3] == 'pitch': icrc_control += 2
				elif self.loc[3] == 'time': icrc_control += 4
				elif self.loc[3] == 'echoes': icrc_control += 3
			elif self.loc[2] == 'arp':
				icrc_control += 768
				if self.loc[3] == 'type': icrc_control += 0
				elif self.loc[3] == 'time': icrc_control += 3
				elif self.loc[3] == 'gate': icrc_control += 4
				elif self.loc[3] == 'range': icrc_control += 1
				elif self.loc[3] == 'repeat': icrc_control += 5
				elif self.loc[3] == 'chord': icrc_control += 2
			elif self.loc[2] == 'tracking':
				icrc_control += 1280
				if self.loc[3] == 'vol_pan': icrc_control += 0
				elif self.loc[3] == 'vol_modx': icrc_control += 1
				elif self.loc[3] == 'vol_mody': icrc_control += 2
				elif self.loc[3] == 'key_pan': icrc_control += 16
				elif self.loc[3] == 'key_modx': icrc_control += 17
				elif self.loc[3] == 'key_mody': icrc_control += 18
			elif self.loc[3] == 'envlfo':
				if self.loc[3] == 'vol': icrc_control = 4352
				elif self.loc[3] == 'modx': icrc_control = 4608
				elif self.loc[3] == 'mody': icrc_control = 4864
				elif self.loc[3] == 'pitch': icrc_control = 5120
				else: valid_auto = False

				if self.loc[4] == 'env_delay': icrc_control += 2
				elif self.loc[4] == 'env_att': icrc_control += 3
				elif self.loc[4] == 'env_hold': icrc_control += 4
				elif self.loc[4] == 'env_dec': icrc_control += 5
				elif self.loc[4] == 'env_sus': icrc_control += 6
				elif self.loc[4] == 'env_rel': icrc_control += 7
				elif self.loc[4] == 'env_amount': icrc_control += 8
				elif self.loc[4] == 'lfo_predelay': icrc_control += 9
				elif self.loc[4] == 'lfo_att': icrc_control += 10
				elif self.loc[4] == 'lfo_amount': icrc_control += 11
				elif self.loc[4] == 'lfo_speed': icrc_control += 12
				elif self.loc[4] == 'env_att_ten': icrc_control += 14
				elif self.loc[4] == 'env_dec_ten': icrc_control += 15
				elif self.loc[4] == 'env_rel_ten': icrc_control += 16
				else: valid_auto = False
			elif self.loc[2] == 'plugin': 
				icrc_control = int(self.loc[3])+(128<<8)
			else: valid_auto = False
		elif self.loc[0] == 'fx':
			icrc_group += (2<<12)+(int(self.loc[1])<<6)
			if self.loc[2] == 'param':
				icrc_control += (31<<8)+(12<<4)
				if self.loc[3] == 'vol': icrc_control += 0
				elif self.loc[3] == 'pan': icrc_control += 1
				elif self.loc[3] == 'stereo_sep': icrc_control += 2
				elif self.loc[3] == 'eq1_freq': icrc_control += 24
				elif self.loc[3] == 'eq2_freq': icrc_control += 25
				elif self.loc[3] == 'eq3_freq': icrc_control += 26
				elif self.loc[3] == 'eq1_width': icrc_control += 32
				elif self.loc[3] == 'eq2_width': icrc_control += 33
				elif self.loc[3] == 'eq3_width': icrc_control += 34
				elif self.loc[3] == 'eq1_level': icrc_control += 16
				elif self.loc[3] == 'eq2_level': icrc_control += 17
				elif self.loc[3] == 'eq3_level': icrc_control += 18
				else: valid_auto = False

				#if self.loc[3] in ['eq1_freq','eq2_freq','eq3_freq','eq1_width','eq2_width','eq3_width','eq1_level','eq2_level','eq3_level']:
				#	icrc_group += 9

			elif self.loc[2] == 'route':
				icrc_control += (31<<8)+(4<<4)
				icrc_control += int(self.loc[3])
			elif self.loc[2] == 'slot':
				icrc_group += int(self.loc[3])
				icrc_control += (31<<8)
				if self.loc[4] == 'wet': icrc_control += 1
				elif self.loc[4] == 'on': icrc_control += 0
			elif self.loc[2] == 'plugin':
				icrc_group += int(self.loc[3])
				icrc_control += (128<<8)+self.loc[4]

			else: valid_auto = False
		elif self.loc[0] == 'main':
			icrc_group += (4<<12)
			if self.loc[1] == 'vol': icrc_control = 0
			elif self.loc[1] == 'swing': icrc_control = 1
			elif self.loc[1] == 'pitch': icrc_control = 2
			elif self.loc[1] == 'tempo': icrc_control = 5
			else: valid_auto = False
		else: valid_auto = False

		if self.debugprint: print(icrc_control.to_bytes(2, 'big')[::-1].hex()+icrc_group.to_bytes(2, 'big')[::-1].hex(),'|',icrc_control, icrc_group, '|',self.loc,'|',valid_auto)

		bytes_out = icrc_control.to_bytes(2, 'big')[::-1]+int(icrc_group).to_bytes(2, 'big')[::-1]
		return bytes_out, valid_auto

class flp_autopoint:
	def __init__(self, event_bio):
		self.pos = 0
		self.val = 0
		self.tension = 0
		self.type = 0
		self.selected = 0
		self.t_sign = 0
		if event_bio is not None:
			self.read(event_bio)

	def read(self, event_bio):
		self.pos = event_bio.double()
		self.val = event_bio.double()
		self.tension = event_bio.float()
		self.type = event_bio.uint16()
		self.selected = event_bio.uint8()
		self.t_sign = event_bio.uint8()

class flp_autopoints:
	def __init__(self):
		pass

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		self.version = event_bio.uint32()
		_unk1 = event_bio.uint32() # 64
		_unk2 = event_bio.uint32() # 1024
		_unk3 = event_bio.uint8() # 768
		_unk4 = event_bio.uint32() # 768
		numpoints = event_bio.uint32() # 0
		self.points = [flp_autopoint(event_bio) for x in range(numpoints)]

class flp_remotecontrol:
	def __init__(self):
		self.channel = 0
		self.autoloc = flp_autoloc()
		self.flags = 8
		self.smooth = 469
		self.formula = ''

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		event_bio.skip(2)
		self.channel = event_bio.uint32()
		event_bio.skip(2)
		self.autoloc.decode(event_bio.uint32())
		self.flags = event_bio.uint32()
		self.smooth = event_bio.uint32()

	def write(self):
		autohex, isvalid = self.autoloc.encode()

		bytes_remote = b'\x00\x00'
		bytes_remote += self.channel.to_bytes(4, "little")
		bytes_remote += b'\x00\x00'
		bytes_remote += autohex
		bytes_remote += self.flags.to_bytes(4, "little")
		bytes_remote += self.smooth.to_bytes(4, "little")
		return bytes_remote, isvalid

class flp_initvals:
	def __init__(self):
		self.initvals = {}

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		while event_bio.tell() < len(event_data):
			icrc_dummy = event_bio.read(4)
			icrc_loc = event_bio.int32()
			icrc_value = event_bio.int32()
			autoloc_obj = flp_autoloc()
			autoloc_obj.decode(icrc_loc)
			self.initvals[autoloc_obj.to_loctxt()] = icrc_value

	def write(self):
		bytes_initfxvals = b''
		for autoloc, autoval in self.initvals.items():
			autoloc_obj = flp_autoloc()
			autoloc_obj.loc = autoloc.split('/')
			autohex, isvalid = autoloc_obj.encode()
			if isvalid:
				bytes_initfxvals += b'\x00\x00\x00\x00'
				bytes_initfxvals += autohex
				bytes_initfxvals += autoval.to_bytes(4, 'little', signed=True)
		return bytes_initfxvals
