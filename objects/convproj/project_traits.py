# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class cvpj_project_traits:
	def __init__(self):
		self.audio_filetypes = []
		self.audio_nested = False
		self.audio_stretch = []
		self.auto_types = []
		self.fxchain_mixer = False
		self.fxrack = False
		self.fxrack_params = ['vol','enabled']
		self.notes_midi = False
		self.placement_cut = False
		self.placement_loop = []
		self.plugin_ext = []
		self.plugin_ext_arch = [32, 64]
		self.plugin_ext_platforms = ['win', 'unix']
		self.time_seconds = False
		self.track_hybrid = False
		self.track_lanes = False
		self.track_nopl = False
		
	def from_dict(self, indict):
		if 'audio_filetypes' in indict: self.audio_filetypes = indict['audio_filetypes']
		if 'audio_nested' in indict: self.audio_nested = indict['audio_nested']
		if 'audio_stretch' in indict: self.audio_stretch = indict['audio_stretch']
		if 'auto_types' in indict: self.auto_types = indict['auto_types']
		if 'fxchain_mixer' in indict: self.fxchain_mixer = indict['fxchain_mixer']
		if 'fxrack' in indict: self.fxrack = indict['fxrack']
		if 'fxrack_params' in indict: self.fxrack_params = indict['fxrack_params']
		if 'notes_midi' in indict: self.notes_midi = indict['notes_midi']
		if 'placement_cut' in indict: self.placement_cut = indict['placement_cut']
		if 'placement_loop' in indict: self.placement_loop = indict['placement_loop']
		if 'plugin_ext' in indict: self.plugin_ext = indict['plugin_ext']
		if 'plugin_ext_arch' in indict: self.plugin_ext_arch = indict['plugin_ext_arch']
		if 'plugin_ext_platforms' in indict: self.plugin_ext_platforms = indict['plugin_ext_platforms']
		if 'time_seconds' in indict: self.time_seconds = indict['time_seconds']
		if 'track_hybrid' in indict: self.track_hybrid = indict['track_hybrid']
		if 'track_lanes' in indict: self.track_lanes = indict['track_lanes']
		if 'track_nopl' in indict: self.track_nopl = indict['track_nopl']

