# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from dataclasses import field

from objects.convproj import visual
from objects.convproj import stretch

cvpj_visual = visual.cvpj_visual
cvpj_stretch = stretch.cvpj_stretch

@dataclass
class cvpj_sample_region:
	start: int = 0
	end: int = -1
	name: str = ''
	custom_key: int = -1
	is_custom_key: bool = False
	reverse: bool = False

@dataclass
class cvpj_sample_slice:
	start: int = 0
	end: int = -1
	name: str = ''
	custom_key: int = -1
	is_custom_key: bool = False
	reverse: bool = False

@dataclass
class cvpj_sample_entry:
	visual: cvpj_visual = field(default_factory=cvpj_visual)
	sampleref: str = ''
	audiomod: dict = field(default_factory=dict)
	data: dict = field(default_factory=dict)
	pan: float = 0
	vol: float = 1
	enabled: bool = True
	pitch: float = 0
	reverse: bool = False
	fxrack_channel: int = -1
	stretch: cvpj_stretch = field(default_factory=cvpj_stretch)
	interpolation: str = "linear"
	trigger: str = "normal"

	length: float = -1

	point_value_type: str = 'percent'
	start: float = 0
	end: float = 1

	envs: dict = field(default_factory=dict)

	vel_min: float = 0
	vel_max: float = 1

	loop_start: float = 0
	loop_end: float = 1
	loop_active: bool = False
	loop_mode: str = "normal"
	loop_data: dict = field(default_factory=dict)

	slicer_start_key: int = 0
	slicer_active: bool = False
	slicer_slices: list = field(default_factory=list)

	#def __eq__(self, other):
	#	from dataclasses import asdict
	#	dictdata_a = asdict(self.stretch)
	#	dictdata_b = asdict(other.stretch)
	#	diffrence = []
	#	for n, x in dictdata_a.items():
	#		if dictdata_a[n] != dictdata_b[n]: diffrence.append(n)

	def get_data(self, name, fallback): 
		return self.data[name] if name in self.data else fallback

	def get_filepath(self, convproj_obj, os_type): 
		ref_found, sampleref_obj = convproj_obj.get_sampleref(self.sampleref)
		if ref_found: 
			return sampleref_obj.fileref.get_path(os_type, False)
		else:
			return ''

	def from_sampleref_obj(self, sampleref_obj):
		self.convpoints_samples(sampleref_obj)
		self.loop_end = sampleref_obj.dur_samples
		if sampleref_obj.loop_found:
			self.loop_active = sampleref_obj.loop_found
			self.loop_start = sampleref_obj.loop_start
			self.loop_end = sampleref_obj.loop_end

	def from_sampleref(self, convproj_obj, sampleref): 
		ref_found, sampleref_obj = convproj_obj.get_sampleref(sampleref)
		if ref_found:
			self.sampleref = sampleref
			self.from_sampleref_obj(sampleref_obj)

	def convpoints_percent(self, sampleref_obj): 
		if self.point_value_type == 'samples' and sampleref_obj.dur_samples:
			if sampleref_obj.dur_samples != 0:
				self.loop_start = self.loop_start / sampleref_obj.dur_samples
				self.loop_end = self.loop_end / sampleref_obj.dur_samples
				self.start = self.start / sampleref_obj.dur_samples
				self.end = self.end / sampleref_obj.dur_samples
				if self.loop_end == 0 or self.loop_start == self.loop_end: self.loop_end = 1.0
			self.point_value_type = 'percent'

	def convpoints_samples(self, sampleref_obj): 
		if self.point_value_type == 'percent' and sampleref_obj.dur_samples:
			if sampleref_obj.dur_samples != 0:
				if self.loop_end == 0 or self.loop_start == self.loop_end: self.loop_end = 1.0
				self.loop_start = self.loop_start * sampleref_obj.dur_samples
				self.loop_end = self.loop_end * sampleref_obj.dur_samples
				self.start = self.start * sampleref_obj.dur_samples
				self.end = self.end * sampleref_obj.dur_samples
			self.point_value_type = 'samples'

	def add_slice(self): 
		slice_obj = cvpj_sample_slice()
		self.slicer_slices.append(slice_obj)
		return slice_obj

	def stretch_get_pitch_nonsync(self):
		if not self.stretch.is_warped:
			if not self.stretch.uses_tempo:
				return pow(2, -self.pitch/12)
		return 1
