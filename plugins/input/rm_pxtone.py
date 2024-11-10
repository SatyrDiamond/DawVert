# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import math
import os
import numpy as np
import plugins
from objects import globalstore

def get_float(in_int): return struct.unpack("<f", struct.pack("I", in_int))[0]

class pxtone_cmdstream():
	def __init__(self, cvpj_notelist, convproj_obj, cvpj_trackid):
		self.notestart = 0
		self.noteend = 0
		self.cvpj_notelist = cvpj_notelist
		self.cvpj_auto = convproj_obj.automation
		self.cvpj_trackid = cvpj_trackid

		self.cur_pitch = 9
		self.cur_porta = 0
		self.cur_voice = 0

	def note_pitch(self, i_pos, i_value):
		if self.noteend>i_pos:
			slide_pitch = (i_value//256)-87
			slidepos = int(i_pos-self.notestart)
			self.cvpj_notelist.last_add_slide(slidepos, float(self.cur_porta), float(slide_pitch), 1, None)
		else:
			self.cur_pitch = (i_value//256)-87

	def porta(self, i_value):
		self.cur_porta = i_value

	def voice(self, i_value):
		self.cur_voice = i_value

	def vol(self, i_pos, i_value):
		self.cvpj_auto.add_autotick(['track', self.cvpj_trackid, 'vol'], 'float', i_pos, i_value/128)

	def pan(self, i_pos, i_value):
		self.cvpj_auto.add_autotick(['track', self.cvpj_trackid, 'pan'], 'float', i_pos, ((i_value/128)-0.5)*2)

	def pitch(self, i_pos, i_value):
		self.cvpj_auto.add_autotick(['track', self.cvpj_trackid, 'pitch'], 'float', i_pos, math.log2(get_float(i_value))*12)

	def note(self, i_pos, i_value):
		self.cvpj_notelist.add_m('ptcop_'+str(self.cur_voice), i_pos, i_value, self.cur_pitch, 1, None)
		self.noteend = int(i_value+i_pos)
		self.notestart = int(i_pos)

class input_pxtone(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'ptcop'
	def get_name(self): return 'PxTone'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['ptcop']
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:sampler:single']
		in_dict['audio_filetypes'] = ['wav','ogg']
		in_dict['projtype'] = 'rm'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(16)
		if bytesdata == b'PTCOLLAGE-071119': return True
		elif bytesdata == b'PTTUNE--20071119': return True
		else: return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects import colors
		from objects import audio_data
		from objects.file_proj import proj_pxtone
		
		convproj_obj.type = 'rm'

		project_obj = proj_pxtone.ptcop_song()
		if not project_obj.load_from_file(input_file): exit()
		project_obj.postprocess()

		globalstore.dataset.load('pxtone', './data_main/dataset/pxtone.dset')
		colordata = colors.colorset.from_dataset('pxtone', 'track', 'main')

		samplefolder = dv_config.path_samples_extracted

		timebase = 480
		if project_obj.header == b'PTCOLLAGE-071119': timebase = 480
		if project_obj.header == b'PTTUNE--20071119': timebase = 48
		convproj_obj.set_timings(timebase, True)

		for voicenum, voice_obj in project_obj.voices.items():
			cvpj_instid = 'ptcop_'+str(voicenum)
			inst_obj = convproj_obj.instrument__add(cvpj_instid)
			inst_obj.visual.name = voice_obj.name
			#inst_obj.visual.color.set_float([0.14, 0.00, 0.29])

			cvpj_instvol = 1.0

			if voice_obj.type == 'ogg':
				cvpj_instvol = 0.4
				ogg_path = samplefolder + 'ptcop_' + str(voicenum+1).zfill(2) + '.ogg'
				if not os.path.exists(samplefolder): os.makedirs(samplefolder)
				ogg_fileobj = open(ogg_path, 'wb')
				ogg_fileobj.write(voice_obj.data)
				plugin_obj, pluginid, sampleref_obj, samplepart_obj = convproj_obj.plugin__addspec__sampler__genid(ogg_path, None)
				plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
				samplepart_obj.interpolation = "linear" if 1 in voice_obj.sps2 else "none"
				inst_obj.pluginid = pluginid

			if voice_obj.type == 'pcm':
				cvpj_instvol = 0.4
				wave_path = samplefolder + 'ptcop_' + str(voicenum+1).zfill(2) + '.wav'
				audio_obj = audio_data.audio_obj()
				audio_obj.set_codec('int16' if voice_obj.bits == 16 else 'uint8')
				audio_obj.rate = voice_obj.hz
				audio_obj.channels = voice_obj.ch
				audio_obj.pcm_from_bytes(voice_obj.data)
				audio_obj.to_file_wav(wave_path)

				plugin_obj, pluginid, sampleref_obj, samplepart_obj = convproj_obj.plugin__addspec__sampler__genid(wave_path, None)
				plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
				samplepart_obj.interpolation = "linear" if 1 in voice_obj.sps2 else "none"
				if len(voice_obj.data) <= 256: 
					samplepart_obj.loop_start = 0
					samplepart_obj.loop_end = len(voice_obj.data)
					samplepart_obj.loop_active = True
				inst_obj.pluginid = pluginid

			inst_obj.params.add('vol', cvpj_instvol, 'float')
			inst_obj.datavals.add('middlenote', voice_obj.basic_key_field-60)

		for unitnum, unit_obj in enumerate(project_obj.units):
			unit_notes = project_obj.events.data[np.where(project_obj.events.data['unitnum'] == unitnum)[0]]

			cvpj_trackid = str(unitnum+1)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 0, False)
			track_obj.visual.name = unit_obj.name
			track_obj.visual.color.set_float(colordata.getcolor())

			unitstream = pxtone_cmdstream(track_obj.placements.notelist, convproj_obj, cvpj_trackid)

			for e in unit_notes:
				if e['eventnum'] == 1: unitstream.note(e['d_position'], e['value'])
				if e['eventnum'] == 2: unitstream.note_pitch(e['d_position'], e['value'])
				if e['eventnum'] == 5: unitstream.vol(e['d_position'], e['value'])
				if e['eventnum'] == 6: unitstream.porta(e['value'])
				if e['eventnum'] == 12: unitstream.voice(e['value'])
				if e['eventnum'] == 14: unitstream.pitch(e['d_position'], e['value'])
				if e['eventnum'] == 15: unitstream.pan(e['d_position'], e['value'])

			track_obj.placements.notelist.notemod_conv()

		if project_obj.repeat != 0: 
			convproj_obj.loop_active = True
			convproj_obj.loop_start = project_obj.repeat
			convproj_obj.loop_end = project_obj.last

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', project_obj.beattempo, 'float')