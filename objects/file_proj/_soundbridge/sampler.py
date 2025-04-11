# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from functions_spec import soundbridge as soundbridge_func
from functions import xtramath

def readstring(byr_stream):
	return byr_stream.string(byr_stream.uint64_b())

def makestring(textd, byw_stream):
	data = textd.encode()
	byw_stream.uint64_b(len(data))
	byw_stream.raw(data)

debug_count = 0

class soundbridge_sampler_main:
	def __init__(self):
		self.sampler_mode = 0
		self.samples = []
		self.params = [soundbridge_sampler_params() for _ in range(64)]
		self.params_used = [False for _ in range(64)]
		self.treshold = 0
		self._unk1 = 0
		self._unk2 = 0

	def alloc_param(self):
		for n, x in enumerate(self.params_used):
			if not x:
				self.params_used[n] = True
				return n
		return -1

	def add_single(self):
		paramnum = self.alloc_param()
		if paramnum != -1:
			sampler_entry = soundbridge_sampler_entry()
			sampler_entry.params_num = paramnum
			sampler_entry.params_num_end = 64
			self.samples.append(sampler_entry)
			return sampler_entry, self.params[paramnum]
		else:
			return None

	def add_slices(self, slices):
		slicedata = []
		for _ in range(slices):
			paramnum = self.alloc_param()
			if paramnum != -1:
				slicedata.append([paramnum, self.params[paramnum]])

		if slicedata:
			sampler_entry = soundbridge_sampler_entry()
			sampler_entry.params_num = slicedata[0][0]
			sampler_entry.slicemode = 1
			sampler_entry.params_num_end = slicedata[-1][0]
			sampler_entry.numslices = len(slicedata)
			sampler_entry.slices = [[x[0], 0, 0, 4] for x in slicedata]
			self.samples.append(sampler_entry)

			return sampler_entry, slicedata

	def read(self, byr_stream):
		byr_stream.uint64_b() # 1
		self.sampler_mode = byr_stream.uint64_b()
		self._unk1 = byr_stream.uint64_b() # 0
		num_samples = byr_stream.uint64_b()
		for x in range(num_samples):
			sampler_entry = soundbridge_sampler_entry()
			sampler_entry.read(byr_stream)
			self.params_used[sampler_entry.params_num] = True
			self.samples.append(sampler_entry)
		byr_stream.skip(4)
		self.treshold = byr_stream.float_b()
		self._unk2 = byr_stream.float_b()
		for n in range(64): self.params[n].read(byr_stream)
		#self.debug_to_json()

	def debug_to_json(self):
		global debug_count

		import json
		out = {}
		out['sampler_mode'] = self.sampler_mode
		out['samples'] = [x.debug_to_json() for x in self.samples]
		out['params'] = [x.debug_to_json() for x in self.params]
		out['params_used'] = self.params_used
		out['treshold'] = self.treshold
		out['_unk1'] = self._unk1
		out['_unk2'] = self._unk2

		with open(str(debug_count)+'_out.txt', 'w') as f: json.dump(out, f, indent=2)

		debug_count += 1

	def write(self, byw_stream):
		byw_stream.uint64_b(1)
		byw_stream.uint64_b(self.sampler_mode)
		byw_stream.uint64_b(0)
		byw_stream.uint64_b(len(self.samples))
		for sampler_entry in self.samples: sampler_entry.write(byw_stream)
		byw_stream.uint32_b(0)
		byw_stream.float_b(self.treshold)
		byw_stream.float_b(self._unk2)
		for param in self.params: param.write(byw_stream)

class soundbridge_sampler_entry:
	def __init__(self):
		self.params_num = 0
		self.start = 0
		self.end = 0
		self.filter_on = 0
		self.filter_type = 0
		self.pitch_algo = 4
		self.env_amp_on = 0
		self.env_filter_on = 0
		self.env_pitch_on = 0
		self.order = 0
		self.filename = ''
		self.name = ''
		self.metadata = {}
		self.slicemode = 0
		self.params_num_end = 0
		self.numslices = 0
		self.slices = []
		self.unk = 0

	def read(self, byr_stream):
		#print('---------')
		self.params_num = byr_stream.uint64_b()
		self.start = byr_stream.uint64_b()
		self.end = byr_stream.uint64_b()
		self.filter_on = byr_stream.uint8()
		self.filter_type = byr_stream.uint64_b()
		self.pitch_algo = byr_stream.uint64_b()
		self.env_amp_on = byr_stream.uint8()
		self.env_filter_on = byr_stream.uint8()
		self.env_pitch_on = byr_stream.uint8()
		self.slicemode = byr_stream.uint8()
		if not self.slicemode:
			self.params_num_end = byr_stream.uint64_b() # 64
			self.order = byr_stream.uint64_b()
		else:
			self.params_num_end = byr_stream.uint64_b()
			self.order = byr_stream.uint64_b() # 0
		self.filename = byr_stream.string(byr_stream.uint64_b())
		self.name = byr_stream.string(byr_stream.uint64_b())
		self.metadata = dict([[readstring(byr_stream), readstring(byr_stream)] for x in range(byr_stream.uint64_b())])
		self.numslices = byr_stream.uint64_b()
		for _ in range(self.numslices):
			slice1 = byr_stream.uint64_b()
			slice2 = byr_stream.uint64_b()
			slice3 = byr_stream.uint64_b()
			slice4 = byr_stream.uint64_b()
			byr_stream.skip(3)
			self.slices.append([slice1, slice2, slice3, slice4])

	def debug_to_json(self):
		out = {}
		out['params_num'] = self.params_num
		out['start'] = self.start
		out['end'] = self.end
		out['filter_on'] = self.filter_on
		out['filter_type'] = self.filter_type
		out['pitch_algo'] = self.pitch_algo
		out['env_amp_on'] = self.env_amp_on
		out['env_filter_on'] = self.env_filter_on
		out['env_pitch_on'] = self.env_pitch_on
		out['slicemode'] = self.slicemode
		out['params_num_end'] = self.params_num_end
		out['order'] = self.order
		out['filename'] = self.filename
		out['name'] = self.name
		out['metadata'] = self.metadata
		out['numslices'] = self.numslices
		out['slices'] = self.slices
		return out

	def write(self, byw_stream):
		byw_stream.uint64_b(self.params_num)
		byw_stream.uint64_b(self.start)
		byw_stream.uint64_b(self.end)
		byw_stream.uint8(self.filter_on)
		byw_stream.uint64_b(self.filter_type)
		byw_stream.uint64_b(self.pitch_algo)
		byw_stream.uint8(self.env_amp_on)
		byw_stream.uint8(self.env_filter_on)
		byw_stream.uint8(self.env_pitch_on)
		byw_stream.uint8(self.slicemode)
		if not self.slicemode:
			byw_stream.uint64_b(64)
			byw_stream.uint64_b(self.order)
		else:
			byw_stream.uint64_b(self.params_num_end)
			byw_stream.uint64_b(0)
		makestring(self.filename, byw_stream)
		makestring(self.name, byw_stream)
		byw_stream.uint64_b(len(self.metadata))
		for n, v in self.metadata.items():
			makestring(n, byw_stream)
			makestring(v, byw_stream)
		byw_stream.uint64_b(len(self.slices))
		for slice1, slice2, slice3, slice4 in self.slices:
			byw_stream.uint64_b(slice1)
			byw_stream.uint64_b(slice2)
			byw_stream.uint64_b(slice3)
			byw_stream.uint64_b(slice4)
			byw_stream.raw(b'\0\0\0')

class soundbridge_sampler_params_env:
	def __init__(self):
		self.env_a = 0.0
		self.cnvx_a = 0.5
		self.env_d = 0.187838613986969
		self.cnvx_d = 0.5
		self.env_s = 1.0
		self.env_r = 0.07146752625703812
		self.cnvx_r = 0.5

	def debugtxt(self):
		print('ENV:', self.env_a, self.env_d, self.env_s, self.env_r, '|', self.cnvx_a, self.cnvx_d, self.cnvx_r, '|')

	def debug_to_json(self):
		out = {}
		out['env_a'] = self.env_a
		out['cnvx_a'] = self.cnvx_a
		out['env_d'] = self.env_d
		out['cnvx_d'] = self.cnvx_d
		out['env_s'] = self.env_s
		out['env_r'] = self.env_r
		out['cnvx_r'] = self.cnvx_r
		return out

	def read(self, byr_stream):
		self.env_a = byr_stream.float_b()
		self.cnvx_a = byr_stream.float_b()
		self.env_d = byr_stream.float_b()
		self.cnvx_d = byr_stream.float_b()
		self.env_s = byr_stream.float_b()
		self.env_r = byr_stream.float_b()
		self.cnvx_r = byr_stream.float_b()

	def write(self, byw_stream):
		byw_stream.float_b(self.env_a)
		byw_stream.float_b(self.cnvx_a)
		byw_stream.float_b(self.env_d)
		byw_stream.float_b(self.cnvx_d)
		byw_stream.float_b(self.env_s)
		byw_stream.float_b(self.env_r)
		byw_stream.float_b(self.cnvx_r)

class soundbridge_sampler_params:
	def __init__(self):
		self.key_root = 36
		self.key_min = 0
		self.key_max = 127
		self.pitch_semi = 0
		self.pitch_cent = 0
		self.vel_min = 0
		self.vel_max = 127
		self.env_amp = soundbridge_sampler_params_env()
		self.env_filt = soundbridge_sampler_params_env()
		self.env_pitch = soundbridge_sampler_params_env()
		self.gain = 0
		self.pan = 0
		self.filter_freq = 0.9253513813018799
		self.filter_res = 0.82
		self.vol_vel = 0.3
		self._unk2 = 1.0
		self.filt_env_amt = 0.5
		self.pitch_env_amt = 0.5

	def debug_to_json(self):
		out = {}
		out['key_root'] = self.key_root
		out['key_min'] = self.key_min
		out['key_max'] = self.key_max
		out['pitch_semi'] = self.pitch_semi
		out['pitch_cent'] = self.pitch_cent
		out['vel_min'] = self.vel_min
		out['vel_max'] = self.vel_max
		out['env_amp'] = self.env_amp
		out['env_filt'] = self.env_filt
		out['env_pitch'] = self.env_pitch
		out['gain'] = self.gain
		out['pan'] = self.pan
		out['filter_freq'] = self.filter_freq
		out['filter_res'] = self.filter_res
		out['vol_vel'] = self.vol_vel
		out['_unk2'] = self._unk2
		out['filt_env_amt'] = self.filt_env_amt
		out['pitch_env_amt'] = self.pitch_env_amt

		out['env_amp'] = self.env_amp.debug_to_json()
		out['env_filt'] = self.env_filt.debug_to_json()
		out['env_pitch'] = self.env_pitch.debug_to_json()
		return out

	def debugtxt(self):
		print('MAIN:', self.gain, self.pan, '|')
		print('FILTER:', self.filter_freq, self.filter_res, '|')
		print('ENV VOL:', self.vol_vel)
		print('ENV FILTER:', self.filt_env_amt)
		print('KEY:', self.key_root, self.key_min, self.key_max, '|', end=' ')
		print('PITCH:', self.pitch_semi, self.pitch_cent, '|', end=' ')
		print('VEL:', self.vel_min, self.vel_max, '|')
		print('-------------------')

	def read(self, byr_stream):
		self.key_root = int(byr_stream.float_b()*127)
		self.key_min = int(byr_stream.float_b()*127)
		self.key_max = int(byr_stream.float_b()*127)
		self.pitch_semi = (byr_stream.float_b()-0.5)*24
		self.pitch_cent = byr_stream.float_b()*100
		self.vel_min = int(byr_stream.float_b()*127)
		self.vel_max = int(byr_stream.float_b()*127)
		self.gain = (byr_stream.float_b()-0.5)*24
		self.pan = (byr_stream.float_b()-0.5)*2
		self.filter_freq = byr_stream.float_b()
		self.filter_res = xtramath.between_from_one(0.2, 3, byr_stream.float_b())
		self.vol_vel = byr_stream.float_b()
		self.env_amp.read(byr_stream)
		self._unk2 = byr_stream.float_b()
		self.env_filt.read(byr_stream)
		self.filt_env_amt = byr_stream.float_b()
		self.env_pitch.read(byr_stream)
		self.pitch_env_amt = byr_stream.float_b()

	def write(self, byw_stream):
		byw_stream.float_b(self.key_root/127)
		byw_stream.float_b(self.key_min/127)
		byw_stream.float_b(self.key_max/127)
		byw_stream.float_b((self.pitch_semi/24)+0.5)
		byw_stream.float_b(self.pitch_cent/100)
		byw_stream.float_b(self.vel_min/127)
		byw_stream.float_b(self.vel_max/127)
		byw_stream.float_b((self.gain/24)+0.5)
		byw_stream.float_b((self.pan/2)+0.5)
		byw_stream.float_b(self.filter_freq)
		byw_stream.float_b(xtramath.between_to_one(0.2, 3, self.filter_res))
		byw_stream.float_b(self.vol_vel)
		self.env_amp.write(byw_stream)
		byw_stream.float_b(self._unk2)
		self.env_filt.write(byw_stream)
		byw_stream.float_b(self.filt_env_amt)
		self.env_pitch.write(byw_stream)
		byw_stream.float_b(self.pitch_env_amt)
