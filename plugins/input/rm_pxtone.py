# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import audio_data
from functions import colors
from objects import globalstore
from objects.file_proj import proj_pxtone
import struct
import math
import os
import numpy as np
import plugins

def get_float(in_int): return struct.unpack("<f", struct.pack("I", in_int))[0]

class input_pxtone(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'ptcop'
	def gettype(self): return 'rm'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'PxTone'
		dawinfo_obj.file_ext = 'ptcop'
		dawinfo_obj.auto_types = ['nopl_ticks']
		dawinfo_obj.track_nopl = True
		dawinfo_obj.plugin_included = ['sampler:single']
		dawinfo_obj.audio_filetypes = ['wav','ogg']
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(16)
		if bytesdata == b'PTCOLLAGE-071119': return True
		elif bytesdata == b'PTTUNE--20071119': return True
		else: return False
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'rm'

		project_obj = proj_pxtone.ptcop_song()
		project_obj.load_from_file(input_file)
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
			inst_obj = convproj_obj.add_instrument(cvpj_instid)
			inst_obj.visual.name = voice_obj.name
			#inst_obj.visual.color = [0.14, 0.00, 0.29]

			cvpj_instvol = 1.0

			if voice_obj.type == 'ogg':
				cvpj_instvol = 0.4
				ogg_path = samplefolder + 'ptcop_' + str(voicenum+1).zfill(2) + '.ogg'
				if not os.path.exists(samplefolder): os.makedirs(samplefolder)
				ogg_fileobj = open(ogg_path, 'wb')
				ogg_fileobj.write(voice_obj.data)
				plugin_obj, pluginid, sampleref_obj, samplepart_obj = convproj_obj.add_plugin_sampler_genid(ogg_path, None)
				plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
				samplepart_obj.interpolation = "linear" if 1 in voice_obj.sps2 else "none"
				inst_obj.pluginid = pluginid

			if voice_obj.type == 'pcm':
				cvpj_instvol = 0.4
				wave_path = samplefolder + 'ptcop_' + str(voicenum+1).zfill(2) + '.wav'

				audio_obj = audio_data.audio_obj()
				audio_obj.set_codec('int16' if voice_obj.bits == 16 else 'int8')
				audio_obj.rate = voice_obj.hz
				audio_obj.channels = voice_obj.ch
				audio_obj.pcm_from_bytes(voice_obj.data)
				audio_obj.to_file_wav(wave_path)

				plugin_obj, pluginid, sampleref_obj, samplepart_obj = convproj_obj.add_plugin_sampler_genid(wave_path, None)
				plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
				samplepart_obj.interpolation = "linear" if 1 in voice_obj.sps2 else "none"
				inst_obj.pluginid = pluginid

			inst_obj.params.add('vol', cvpj_instvol, 'float')
			inst_obj.datavals.add('middlenote', voice_obj.basic_key_field-60)

		for unitnum, unit_obj in enumerate(project_obj.units):
			unit_notes = project_obj.events.data[np.where(project_obj.events.data['unitnum'] == unitnum)[0]]

			cvpj_trackid = str(unitnum+1)
			track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 0, False)
			track_obj.visual.name = unit_obj.name
			track_obj.visual.color.set_float(colordata.getcolor())

			notestart = 0
			noteend = 0

			cur_pitch = 9
			cur_porta = 0
			cur_voice = 0

			for e in unit_notes:
				if e['eventnum'] == 2: 
					if noteend>e['d_position']:
						slide_pitch = (e['value']//256)-87
						slidepos = int(e['d_position']-notestart)
						track_obj.placements.notelist.last_add_slide(slidepos, float(cur_porta), float(slide_pitch), 1, None)
					else:
						cur_pitch = (e['value']//256)-87

				if e['eventnum'] == 6: cur_porta = e['value']
				if e['eventnum'] == 12: cur_voice = e['value']

				if e['eventnum'] == 5: 
					convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'vol'], 'float', e['d_position'], e['value']/128)
				if e['eventnum'] == 15: 
					convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'pan'], 'float', e['d_position'], ((e['value']/128)-0.5)*2)
				if e['eventnum'] == 14: 
					convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'pitch'], 'float', e['d_position'], math.log2(get_float(e['value']))*12)

				if e['eventnum'] == 1:
					track_obj.placements.notelist.add_m('ptcop_'+str(cur_voice), e['d_position'], e['value'], cur_pitch, 1, None)
					noteend = int(e['value']+e['d_position'])
					notestart = int(e['d_position'])

			track_obj.placements.notelist.notemod_conv()

		if project_obj.repeat != 0: 
			convproj_obj.loop_active = True
			convproj_obj.loop_start = project_obj.repeat
			convproj_obj.loop_end = project_obj.last

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')