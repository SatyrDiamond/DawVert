# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import fileref
import os

VERBOSE = False

class cvpj_videoref:
	def __init__(self):
		self.fileref = fileref.cvpj_fileref()
		self.found = False
		self.dur_samples = -1
		self.dur_sec = -1
		self.hz = 44100
		self.defined_meta = []

	def set_hz(self, val):
		if 'hz' not in self.defined_meta:
			self.defined_meta.append('hz')
		self.hz = val
		self.timebase = val

	def set_dur_samples(self, val):
		if 'dur_samples' not in self.defined_meta: self.defined_meta.append('dur_samples')
		self.dur_samples = val

	def set_dur_sec(self, val):
		if 'dur_sec' not in self.defined_meta: self.defined_meta.append('dur_sec')
		self.dur_sec = val

	def convert__dur_sec__dur_samples(self, overwrite):
		cond_samp = ('dur_samples' not in self.defined_meta) or overwrite
		if ('dur_sec' in self.defined_meta) or cond_samp:
			if ('hz' in self.defined_meta): 
				#logger_project.warning('Guessing dur_samples from dur_sec')
				self.set_dur_samples(int(self.dur_sec*self.timebase))
				return 1
			else: return -1
		else: return 0

	def convert__dur_samples__dur_sec(self, overwrite):
		cond_samp = ('dur_sec' not in self.defined_meta) or overwrite
		if ('dur_samples' in self.defined_meta) or cond_samp:
			if ('hz' in self.defined_meta): 
				#logger_project.warning('Guessing dur_sec from dur_samples')
				self.set_dur_sec(self.dur_samples/self.timebase)
				return 1
			else: return -1
		else: return 0

	def get_hz(self):
		if 'hz' not in self.defined_meta: self.get_info('get_hz')
		if 'hz' in self.defined_meta: return self.hz

	def get_hz_opt(self):
		if 'hz' in self.defined_meta: return self.hz

	def get_dur_samples(self):
		resd = self.convert__dur_sec__dur_samples(False)
		if resd == -1:
			if self.get_info('get_dur_samples'): self.convert__dur_sec__dur_samples(False)

		if 'dur_samples' in self.defined_meta:
			return self.dur_samples

	def get_dur_sec(self):
		resd = self.convert__dur_samples__dur_sec(False)
		if resd == -1:
			if self.get_info('get_dur_sec'): self.convert__dur_samples__dur_sec(False)

		if 'dur_sec' in self.defined_meta:
			return self.dur_sec

	def get_exists(self):
		orgpath = self.fileref.get_path(None, False)
		return os.path.exists(orgpath)

	def set_path(self, in_os_type, in_path):
		self.fileref.set_path(in_os_type, in_path, 0)

	def find_relative(self, searchseries):
		if not self.found:
			orgpath = self.fileref.get_path(None, False)
			iffound = False
			if not os.path.exists(orgpath):
				iffound = self.fileref.search(searchseries)
			return iffound
		return False

	def search_local(self, dirpath):
		return self.fileref.search_local(dirpath)

