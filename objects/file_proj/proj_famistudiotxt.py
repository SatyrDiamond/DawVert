# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import shlex
from functions import data_values
from functions import xtramath

from objects.inst_params import fm_vrc7
from objects.inst_params import fm_epsm
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

def read_regs(cmd_params, startname, size):
	regdata = [0 for x in range(size)]
	for regnum in range(size):
		regname = startname+str(regnum)
		if regname in cmd_params: regdata[regnum] = int(cmd_params[regname])
	return regdata

def NoteToMidi(keytext):
	l_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
	s_octave = (int(keytext[-1])-5)*12
	lenstr = len(keytext)
	if lenstr == 3: t_key = keytext[:-1]
	else: t_key = keytext[:-1]
	s_key = l_key.index(t_key)
	return s_key + s_octave

class dpcm_sample:
	def __init__(self, data):
		self.data_txt = data
		self.data_bytes = b''
		if data: self.data_bytes = bytes.fromhex(data)

class dpcm_mappings:
	__slots__ = ['data']
	def __init__(self):
		self.data = {}

	def add(self, cmd_params):
		if 'Note' in cmd_params:
			notekey = NoteToMidi(cmd_params['Note'])
			mapdata = {}
			mapdata['Sample'] = cmd_params['Sample'] if 'Sample' in cmd_params else ''
			mapdata['Pitch'] = int(cmd_params['Pitch']) if 'Pitch' in cmd_params else 15
			mapdata['Loop'] = (cmd_params['Loop'] == 'True') if 'Loop' in cmd_params else False
			self.data[notekey] = mapdata

class inst_envelope:
	__slots__ = ['Values','Length','Loop','Release']
	def __init__(self, cmd_params):
		self.Values = [int(x) for x in cmd_params['Values'].split(',')] if 'Values' in cmd_params else []
		self.Length = int(cmd_params['Length']) if 'Length' in cmd_params else len(arpdata['Values'])
		self.Loop = int(cmd_params['Loop']) if 'Loop' in cmd_params else 0
		self.Release = int(cmd_params['Release']) if 'Release' in cmd_params else -1

class fs_arpeggio:
	__slots__ = ['Values','Length','Loop']
	def __init__(self, cmd_params):
		self.Values = [int(x) for x in cmd_params['Values'].split(',')] if 'Values' in cmd_params else []
		self.Length = int(cmd_params['Length']) if 'Length' in cmd_params else len(arpdata['Values'])
		self.Loop = int(cmd_params['Loop']) if 'Loop' in cmd_params else 0

class fs_instrument:
	__slots__ = ['Name','Expansion','Regs','Patch','DPCMMappings','Arpeggio','Envelopes','N163WavePreset','N163WaveSize','N163WavePos','N163WaveCount','FM']
	def __init__(self):
		self.Name = ''
		self.Expansion = ''
		self.Regs = []
		self.Patch = 0
		self.DPCMMappings = dpcm_mappings()
		self.Arpeggio = {}
		self.Envelopes = {}
		self.FM = None

		self.N163WavePreset = ''
		self.N163WaveSize = 0
		self.N163WavePos = 0
		self.N163WaveCount = 0

class fs_patternsettings:
	__slots__ = ['Length','BeatLength','NoteLength','Groove','GroovePaddingMode','bpm']
	def __init__(self, cmd_params):
		self.Length = int(cmd_params['Length']) if 'Length' in cmd_params else 32
		self.BeatLength = int(cmd_params['BeatLength']) if 'BeatLength' in cmd_params else 4
		self.NoteLength = int(cmd_params['NoteLength']) if 'NoteLength' in cmd_params else 6
		if 'Groove' in cmd_params:
			self.Groove = [int(x) for x in cmd_params['Groove'].split('-')] if 'Groove' in cmd_params else [6]
			self.bpm = 60/(xtramath.average(self.Groove)/60*self.BeatLength)
		else:
			self.Groove = []
			self.bpm = None
		self.GroovePaddingMode = cmd_params['GroovePaddingMode'] if 'GroovePaddingMode' in cmd_params else 'Middle'

class fs_pattern:
	__slots__ = ['Name','Notes']
	def __init__(self, cmd_params):
		self.Name = cmd_params['Name'] if 'Name' in cmd_params else ''
		self.Notes = []

class fs_channel:
	__slots__ = ['Type','Instances','Patterns']
	def __init__(self, cmd_params):
		self.Type = cmd_params['Type'] if 'Type' in cmd_params else ''
		self.Instances = {}
		self.Patterns = {}

class fs_note:
	__slots__ = ['Time','Value','Duration','Instrument','SlideTarget','Attack','FinePitch','Volume','VolumeSlideTarget','VibratoSpeed','VibratoDepth','Arpeggio']
	def __init__(self, cmd_params):
		self.Time = int(cmd_params['Time']) if 'Time' in cmd_params else ''
		key = cmd_params['Value'] if 'Value' in cmd_params else None
		if key not in ['Stop', None]: self.Value = NoteToMidi(key)
		else: self.Value = key
		self.Duration = int(cmd_params['Duration']) if 'Duration' in cmd_params else None
		self.Instrument = cmd_params['Instrument'] if 'Instrument' in cmd_params else None
		self.SlideTarget = NoteToMidi(cmd_params['SlideTarget']) if 'SlideTarget' in cmd_params else None
		self.Attack = (cmd_params['Attack']=='True') if 'Attack' in cmd_params else None
		self.FinePitch = int(cmd_params['FinePitch']) if 'FinePitch' in cmd_params else None
		self.Volume = int(cmd_params['Volume']) if 'Volume' in cmd_params else None
		self.VolumeSlideTarget = int(cmd_params['VolumeSlideTarget']) if 'VolumeSlideTarget' in cmd_params else None
		self.VibratoSpeed = int(cmd_params['VibratoSpeed']) if 'VibratoSpeed' in cmd_params else None
		self.VibratoDepth = int(cmd_params['VibratoDepth']) if 'VibratoDepth' in cmd_params else None
		self.Arpeggio = cmd_params['Arpeggio'] if 'Arpeggio' in cmd_params else None

class fs_song:
	__slots__ = ['Name','LoopPoint','PatternLength','PatternSettings','PatternCustomSettings','Channels']
	def __init__(self, cmd_params):
		self.Name = cmd_params['Name'] if 'Name' in cmd_params else ''
		self.LoopPoint = int(cmd_params['LoopPoint']) if 'LoopPoint' in cmd_params else 0
		self.PatternLength = int(cmd_params['PatternLength']) if 'PatternLength' in cmd_params else 16
		self.PatternSettings = fs_patternsettings(cmd_params)
		self.PatternCustomSettings = {}
		self.Channels = []

class famistudiotxt_project:
	def __init__(self):
		self.Version = ''
		self.TempoMode = ''
		self.Name = ''
		self.Author = ''
		self.Copyright = ''
		self.Expansions = []
		self.NumN163Channels = 0

		self.Arpeggios = {}
		self.Songs = {}
		self.DPCMSamples = {}
		self.Instruments = {}
		self.DPCMMappings = dpcm_mappings()

	def load_from_file(self, input_file):
		try:
			f_fst = open(input_file, 'r')
			famistudiotxt_lines = f_fst.readlines()
		except UnicodeDecodeError:
			raise ProjectFileParserException('famistudio_txt: File is not text')

		for line in famistudiotxt_lines:
			t_cmd = line.split(" ", 1)
			t_precmd = t_cmd[0]
			tabs_num = t_precmd.count('\t')
		
			cmd_name = t_precmd.split()[0]
			cmd_params = dict(token.split('=') for token in shlex.split(t_cmd[1]))
			
			if cmd_name == 'Project' and tabs_num == 0:
				if 'Version' in cmd_params: self.Version = cmd_params['Version']
				if 'TempoMode' in cmd_params: self.TempoMode = cmd_params['TempoMode']
				if 'Name' in cmd_params: self.Name = cmd_params['Name']
				if 'Author' in cmd_params: self.Author = cmd_params['Author']
				if 'Copyright' in cmd_params: self.Copyright = cmd_params['Copyright']
				if 'Expansions' in cmd_params: self.Expansions = cmd_params['Expansions'].split(',')
				if 'NumN163Channels' in cmd_params: self.NumN163Channels = int(cmd_params['NumN163Channels'])

			elif cmd_name == 'DPCMSample' and tabs_num == 1: self.DPCMSamples[cmd_params['Name']] = dpcm_sample(cmd_params['Data'])

			elif cmd_name == 'Instrument' and tabs_num == 1:
				cur_inst = fs_instrument()
				if 'Name' in cmd_params: cur_inst.Name = cmd_params['Name']
				if 'Expansion' in cmd_params: cur_inst.Expansion = cmd_params['Expansion']
				self.Instruments[cur_inst.Name] = cur_inst

				if 'N163WavePreset' in cmd_params: cur_inst.N163WavePreset = cmd_params['N163WavePreset']
				if 'N163WaveSize' in cmd_params: cur_inst.N163WaveSize = int(cmd_params['N163WaveSize'])
				if 'N163WavePos' in cmd_params: cur_inst.N163WavePos = int(cmd_params['N163WavePos'])
				if 'N163WaveCount' in cmd_params: cur_inst.N163WaveCount = int(cmd_params['N163WaveCount'])

				if cur_inst.Expansion == 'EPSM':
					fm_obj = cur_inst.FM = fm_epsm.epsm_inst()
					if 'EpsmPatch' in cmd_params: fm_obj.Patch = int(cmd_params['EpsmPatch'])
					cur_inst.Regs = read_regs(cmd_params, 'EpsmReg', 31)
					if fm_obj.patch != 0: fm_obj.from_patch()
					else: fm_obj.from_regs(cur_inst.Regs)

				if cur_inst.Expansion == 'VRC7': 
					fm_obj = cur_inst.FM = fm_vrc7.vrc7_inst()
					if 'Vrc7Patch' in cmd_params: fm_obj.patch = int(cmd_params['Vrc7Patch'])
					cur_inst.Regs = read_regs(cmd_params, 'Vrc7Reg', 8)
					if fm_obj.patch != 0: fm_obj.from_patch()
					else: fm_obj.from_regs(cur_inst.Regs)

			elif cmd_name == 'DPCMMapping' and tabs_num == 1: self.DPCMMappings.add(cmd_params)

			elif cmd_name == 'DPCMMapping' and tabs_num == 2: cur_inst.DPCMMappings.add(cmd_params)

			elif cmd_name == 'Arpeggio' and tabs_num == 1:
				if 'Name' in cmd_params: 
					self.Arpeggios[cmd_params['Name']] = fs_arpeggio(cmd_params)

			elif cmd_name == 'Envelope' and tabs_num == 2:
				if 'Type' in cmd_params: cur_inst.Envelopes[cmd_params['Type']] = inst_envelope(cmd_params)

			elif cmd_name == 'Song' and tabs_num == 1:
				if 'Name' in cmd_params:
					cur_song = fs_song(cmd_params)
					self.Songs[cmd_params['Name']] = cur_song

			elif cmd_name == 'PatternCustomSettings' and tabs_num == 2:
				cur_song.PatternCustomSettings[int(cmd_params['Time'])] = fs_patternsettings(cmd_params)

			elif cmd_name == 'Channel' and tabs_num == 2:
				cur_chan = fs_channel(cmd_params)
				cur_song.Channels.append(cur_chan)

			elif cmd_name == 'Pattern' and tabs_num == 3:
				cur_pat = fs_pattern(cmd_params)
				cur_chan.Patterns[cmd_params['Name']] = cur_pat
	
			elif cmd_name == 'PatternInstance' and tabs_num == 3:
				cur_chan.Instances[int(cmd_params['Time'])] = cmd_params['Pattern']
	
			elif cmd_name == 'Note' and tabs_num == 4:
				cur_pat.Notes.append(fs_note(cmd_params))

			else:
				raise ProjectFileParserException('famistudio_txt: unexpected command and/or wrong tabs: '+cmd_name)
		return True