# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import blackboxprotobuf
import struct
import json

def int2float(value): return struct.unpack("<f", struct.pack("<I", value))[0]

def float2int(value): return struct.unpack("<I", struct.pack("<f", value))[0]

def dict2list(i_dict):
    if isinstance(i_dict, list) == False: return [i_dict]
    else: return i_dict

class onlineseq_marker:
	__slots__ = ['pos','value','type','id','param']
	def __init__(self, pd):
		self.pos = 0
		self.value = 0
		self.type = 0
		self.id = 0
		self.param = 0

		if pd != None:
			if '1' in pd: self.pos = int2float(int(pd['1']))
			if '2' in pd: self.param = int(pd['2'])
			if '3' in pd: self.id = int(pd['3'])
			if '4' in pd: self.value = int2float(int(pd['4']))
			if '5' in pd: self.type = int(pd['5'])

	def write(self):
		outjson = {}
		if self.pos != 0: outjson['1'] = float2int(self.pos)
		if self.param != 0: outjson['2'] = self.param
		if self.id != 0: outjson['3'] = self.id
		if self.value != 0: outjson['4'] = float2int(self.value)
		if self.type != 0: outjson['5'] = self.type
		return outjson

class onlineseq_synth_env:
	def __init__(self, pd):
		self.enabled = 0
		self.attack = 0
		self.decay = 0
		self.sustain = 0
		self.release = 0
		if pd != None:
			if '1' in pd: self.enabled = int(pd['1'])
			if '2' in pd: self.attack = int2float(int(pd['2']))
			if '4' in pd: self.decay = int2float(int(pd['4']))
			if '5' in pd: self.sustain = int2float(int(pd['5']))
			if '6' in pd: self.release = int2float(int(pd['6']))

	def write(self):
		outjson = {}
		if self.enabled != 0: outjson['1'] = self.enabled
		if self.attack != 0: outjson['2'] = float2int(self.attack)
		if self.decay != 0: outjson['4'] = float2int(self.decay)
		if self.sustain != 0: outjson['5'] = float2int(self.sustain)
		if self.release != 0: outjson['6'] = float2int(self.release)
		return outjson

class onlineseq_synth:
	def __init__(self, pd):
		self.shape = 0
		self.env_vol = None
		self.env_filt = None
		self.filter_freq = 0
		self.filter_reso = 0
		self.filter_type = 0
		self.lfo_on = 0
		self.lfo_shape = 0
		self.lfo_freq = 0
		self.lfo_freq_custom = 0
		self.lfo_amount = 0
		self.lfo_dest = 0

		if pd != None:
			if '1' in pd: self.shape = int(pd['1'])
			if '2' in pd: self.env_vol = onlineseq_synth_env(pd['2'])
			if '3' in pd: self.env_filt = onlineseq_synth_env(pd['3'])
			if '4' in pd: self.filter_freq = int2float(int(pd['4']))
			if '5' in pd: self.filter_reso = int2float(int(pd['5']))
			if '6' in pd: self.filter_type = int(pd['6'])
			if '7' in pd: self.lfo_on = int(pd['7'])
			if '8' in pd: self.lfo_shape = int(pd['8'])
			if '9' in pd: self.lfo_freq = int2float(int(pd['9']))
			if '10' in pd: self.lfo_amount = int2float(int(pd['10']))
			if '11' in pd: self.lfo_dest = int(pd['11'])
			if '12' in pd: self.lfo_freq_custom = int(pd['12'])

	def write(self):
		outjson = {}
		if self.shape != 0: outjson['1'] = self.shape 
		if self.env_vol: outjson['2'] = self.env.write()
		if self.env_filt: outjson['3'] = self.env_filt.write()
		if self.filter_freq != 0: outjson['4'] = int2float(self.filter_freq)
		if self.filter_reso != 0: outjson['5'] = int2float(self.filter_reso)
		if self.filter_type != 0: outjson['6'] = self.filter_type
		if self.lfo_on != 0: outjson['7'] = self.lfo_on
		if self.lfo_shape != 0: outjson['8'] = self.lfo_shape
		if self.lfo_freq != 0: outjson['9'] = int2float(self.lfo_freq)
		if self.lfo_amount != 0: outjson['10'] = int2float(self.lfo_amount)
		if self.lfo_dest != 0: outjson['11'] = self.lfo_dest
		if self.lfo_freq_custom != 0: outjson['12'] = self.lfo_freq_custom
		return outjson

class onlineseq_inst_param:
	def __init__(self, pd):
		self.vol = 1
		self.delay_on = 0
		self.reverb_on = 0
		self.pan = 0
		self.enable_eq = 0
		self.eq_low = 0
		self.eq_mid = 0
		self.eq_high = 0
		self.detune = 0
		self.reverb_type = 0
		self.reverb_wet = 0
		self.distort_type = 0
		self.distort_wet = 0
		self.bitcrush_on = 0
		self.bitcrush_depth = 16
		self.bitcrush_level = 0.5
		self.name = None
		self.used_fx = []
		self.synth = None

		if pd != None:
			if '1' in pd: self.vol = int2float(int(pd['1']))
			if '2' in pd: 
				self.delay_on = int(pd['2'])
				if self.delay_on: self.used_fx.append('delay')
			if '3' in pd: self.reverb_on = int(pd['3'])
			if '4' in pd: self.pan = int2float(int(pd['4']))
			if '5' in pd: self.enable_eq = int(pd['5'])
			if '6' in pd: self.eq_low = int2float(int(pd['6']))
			if '7' in pd: self.eq_mid = int2float(int(pd['7']))
			if '8' in pd: self.eq_high = int2float(int(pd['8']))
			if '9' in pd: self.detune = int2float(int(pd['9']))
			if '10' in pd: self.reverb_type = int(pd['10'])
			if '11' in pd: self.reverb_wet = int2float(int(pd['11']))
			if '12' in pd: self.distort_type = int(pd['12'])
			if '13' in pd: self.distort_wet = int2float(int(pd['13']))
			if '15' in pd: self.name = pd['15']

			if '14' in pd: self.synth = onlineseq_synth(pd['14'])
			if '18' in pd: self.bitcrush_on = int(pd['18'])
			if '19' in pd: self.bitcrush_depth = int(pd['19'])
			if '20' in pd: self.bitcrush_level = int2float(int(pd['20']))

			if self.bitcrush_on and (('18' in pd) or ('19' in pd) or ('20' in pd)): self.used_fx.append('bitcrush')
			if self.enable_eq and (('6' in pd) or ('7' in pd) or ('9' in pd)): self.used_fx.append('eq')
			if self.reverb_on and (('10' in pd) or ('11' in pd)): self.used_fx.append('reverb')
			if self.distort_type and (('12' in pd) or ('13' in pd)): self.used_fx.append('distort')

	def write(self):
		outjson = {}

		if self.vol != 0: outjson['1'] = float2int(self.vol)
		if self.delay_on != 0: outjson['2'] = self.delay_on
		if self.reverb_on != 0: outjson['3'] = self.reverb_on
		if self.pan != 0: outjson['4'] = float2int(self.pan)
		if self.enable_eq != 0: outjson['5'] = self.enable_eq
		if self.eq_low != 0: outjson['6'] = float2int(self.eq_low)
		if self.eq_mid != 0: outjson['7'] = float2int(self.eq_mid)
		if self.eq_high != 0: outjson['8'] = float2int(self.eq_high)
		if self.detune != 0: outjson['9'] = float2int(self.detune)
		if self.reverb_type != 0: outjson['10'] = self.reverb_type
		if self.reverb_wet != 0: outjson['11'] = float2int(self.reverb_wet)
		if self.distort_type != 0: outjson['12'] = self.distort_type
		if self.distort_wet != 0: outjson['13'] = float2int(self.distort_wet)
		if self.name != None: outjson['15'] = self.name
		if self.bitcrush_on != 0: outjson['18'] = self.bitcrush_on
		if self.bitcrush_depth != 16: outjson['19'] = self.bitcrush_depth
		if self.bitcrush_level != 0.5: outjson['20'] = float2int(self.bitcrush_level)
		if self.synth != None: outjson['14'] = self.synth.write()

		return outjson

class onlineseq_project:
	def __init__(self):
		self.bpm = 120
		self.numerator = 4
		self.notes = []
		self.markers = []
		self.params = {}

	def load_from_file(self, input_file):
		os_data_song_stream = open(input_file, 'rb')
		os_data_song_data = os_data_song_stream.read()
		message, typedef = blackboxprotobuf.protobuf_to_json(os_data_song_data)
		os_data = json.loads(message)

		if '1' in os_data:
			os_main = os_data['1']
			if '1' in os_main: self.bpm = int(os_main['1'])
			if '2' in os_main: self.numerator = int(os_main['2'])
			if '3' in os_main: 
				for i in dict2list(os_main['3']): 
					instid = int(i['1'])
					self.params[instid] = onlineseq_inst_param(i['2'])

		if '2' in os_data:
			for n in dict2list(os_data['2']): 
				note = [int(n['1']),0,0,0,0]
				if '2' in n: note[1] = int2float(int(n['2']))
				if '3' in n: note[2] = int2float(int(n['3']))
				if '4' in n: note[3] = int(n['4'])
				if '5' in n: note[4] = int2float(int(n['5']))
				self.notes.append(note)

		if '3' in os_data:
			for marker in dict2list(os_data['3']): self.markers.append(onlineseq_marker(marker))

		s = json.dumps(os_data, indent=4)
		return True
		#open("in.json","w").write(s)

	def save_to_file(self, output_file):
		outjson = {}
		os_main = outjson['1'] = {}
		os_main['1'] = self.bpm
		if self.numerator != 4: os_main['2'] = self.numerator

		if self.params: 
			os_main['3'] = []
			for instid, instparams in self.params.items():
				os_main['3'].append({'1': instid, '2': instparams.write()})

		outjson['2'] = []
		for note in self.notes:
			notej = {}
			if note[0] != 0: notej['1'] = note[0]
			if note[1] != 0: notej['2'] = float2int(note[1])
			if note[2] != 0: notej['3'] = float2int(note[2])
			if note[3] != 0: notej['4'] = note[3]
			if note[4] != 0: notej['5'] = float2int(note[4])
			outjson['2'].append(notej)

		outjson['3'] = [x.write() for x in self.markers]

		#open("out.json","w").write(json.dumps(outjson, indent=4))

		protobuf_typedef = {
		'1': {
			'type': 'message', 'message_typedef': {
				'1': {'type': 'int', 'name': ''}, 
				'3': {'type': 'message', 'message_typedef': {
					'1': {'type': 'int', 'name': ''}, 
					'2': {'type': 'message', 'message_typedef': {
						'1': {'type': 'fixed32', 'name': ''}, 
						'4': {'type': 'fixed32', 'name': ''}, 
						'10': {'type': 'int', 'name': ''}, 
						'15': {'type': 'bytes', 'name': ''}
					}, 'name': ''}
				}, 'name': ''}
			}, 'name': ''}, 
		'2': {
			'type': 'message', 'message_typedef': {
				'1': {'type': 'int', 'name': ''}, 
				'3': {'type': 'fixed32', 'name': ''}, 
				'4': {'type': 'int', 'name': ''},
				'5': {'type': 'fixed32', 'name': ''},
				'2': {'type': 'fixed32', 'name': ''}
			}, 'name': ''},
		'3': {
			'type': 'message', 'message_typedef': {
				'1': {'type': 'fixed32', 'name': ''}, 
				'4': {'type': 'fixed32', 'name': ''}, 
				'5': {'type': 'int', 'name': ''}, 
				'2': {'type': 'int', 'name': ''}, 
				'3': {'type': 'int', 'name': ''}
			}, 'name': ''}
		}
		with open(output_file, "wb") as fileout:
			fileout.write(blackboxprotobuf.encode_message(outjson,protobuf_typedef))

	def seperate_markers(self):
		markers = {}
		for marker in self.markers:
			#print(marker.id, marker.param, '|', marker.pos, '+', marker.value, marker.type)
			if marker.id not in markers: markers[marker.id] = {}
			if marker.param not in markers[marker.id]: markers[marker.id][marker.param] = []
			markers[marker.id][marker.param].append(marker)
		return markers

	def seperate_notes(self, short):
		insts = {}
		for x in self.notes:
			if x[3] not in insts: insts[x[3]] = []
			if (x[2] > 0.00001) or short: insts[x[3]].append(x)
		return insts
