# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import plugins
import numpy as np
from functions import xtramath
from objects import globalstore
import os

def do_automation(convproj_obj, trackid, atype, timelineobj, usetimeline):
	if usetimeline:
		nextinstant = False
		autoloc = ['track', trackid, atype] if trackid else ['master', atype]
		for event in timelineobj:
			value = 0
			if atype == 'vol': value = event.value/100
			if atype == 'pan': value = (event.value-50)/50
			autopoint_obj = convproj_obj.automation.add_autopoint(autoloc, 'float', event.position, value, 'normal' if not nextinstant else 'instant')
			if nextinstant: nextinstant = False
			if event.fade == 'Exponential': autopoint_obj.tension = -1
			if event.fade == 'Logarithmic': autopoint_obj.tension = 1
			if event.fade == 'Edge': nextinstant = True

keynums = {}
keynums['B'] = 11
keynums['ASharp'] = 10
keynums['A'] = 9
keynums['GSharp'] = 8
keynums['G'] = 7
keynums['FSharp'] = 6
keynums['F'] = 5
keynums['E'] = 4
keynums['DSharp'] = 3
keynums['D'] = 2
keynums['CSharp'] = 1
keynums['C'] = 0

class input_zmaestro(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'z_maestro'
	
	def get_name(self):
		return 'Z-Maestro'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['zmm']
		in_dict['audio_stretch'] = ['rate']
		in_dict['audio_filetypes'] = ['wav']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['placement_loop'] = ['loop']
		in_dict['projtype'] = 'r'
		in_dict['plugin_included'] = ['native:z_maestro','universal:midi','universal:soundfont2']

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import z_maestro as proj_z_maestro
		from objects import audio_data
		from objects.inst_params import fx_delay

		samplefolder = dawvert_intent.path_samples['extracted']

		globalstore.dataset.load('z_maestro', './data_main/dataset/z_maestro.dset')

		convproj_obj.type = 'r'
		convproj_obj.set_timings(0.25, True)

		project_obj = proj_z_maestro.zmaestro_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		tempodiv = project_obj.tempo/120

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.author = project_obj.author
		convproj_obj.metadata.comment_text = project_obj.comments
		convproj_obj.params.add('bpm', project_obj.tempo, 'float')
		convproj_obj.transport.loop_start = project_obj.loopstart
		convproj_obj.transport.loop_end = project_obj.loopstart+project_obj.looplength
		convproj_obj.transport.loop_active = project_obj.loopenabled

		if project_obj.key in keynums:
			timemarker_obj = convproj_obj.timemarker__add_key(keynums[project_obj.key])

		do_automation(convproj_obj, '', 'vol', project_obj.volumetimeline, project_obj.usevolumetimeline)
		do_automation(convproj_obj, '', 'pan', project_obj.pantimeline, project_obj.usepantimeline)

		for tracknum, md in enumerate(project_obj.tracks):
			tracktype, zm_track = md
			cvpj_trackid = 'track_'+str(tracknum)

			if tracktype in ['MIDITrack', 'MIDIDrumTrack']:
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
				track_obj.params.add('vol', zm_track.volume/100, 'float')
				track_obj.params.add('pan', (zm_track.pan-50)/50, 'float')
				if not zm_track.soundfont:
					track_obj.midi.out_inst.patch = zm_track.instrumentcode
					track_obj.midi.out_inst.bank = zm_track.instrumentbank
					track_obj.to_midi(convproj_obj, cvpj_trackid, True)
					track_obj.visual.name = zm_track.name
				else:
					track_obj.visual.from_dset('z_maestro', 'track', tracktype, True)
					track_obj.visual.name = zm_track.name
					plugin_obj = convproj_obj.plugin__add(cvpj_trackid, 'universal', 'soundfont2', None)
					track_obj.plugslots.set_synth(cvpj_trackid)
					sf2_path = os.path.join(dawvert_intent.input_folder, zm_track.soundfont)
					fileref_obj = convproj_obj.fileref__add(sf2_path, sf2_path, None)
					plugin_obj.filerefs['file'] = sf2_path
					fileref_obj.search_local(dawvert_intent.input_folder)
					plugin_obj.midi.from_sf2(zm_track.instrumentbank, zm_track.instrumentcode)

				if tracktype == 'MIDIDrumTrack': track_obj.is_drum = True

				do_automation(convproj_obj, cvpj_trackid, 'vol', zm_track.volumetimeline, zm_track.usevolumetimeline)
				do_automation(convproj_obj, cvpj_trackid, 'pan', zm_track.pantimeline, zm_track.usepantimeline)

				for part in zm_track.parts:
					placement_obj = track_obj.placements.add_notes()
					placement_obj.visual.name = part.name
					if part.repeats:
						placement_obj.time.set_loop_data(0, 0, part.length)
						placement_obj.time.set_posdur(part.start, part.length+part.repeats)
					else:
						placement_obj.time.set_posdur(part.start, part.length)

					for note in part.notes:
						placement_obj.notelist.add_r(note.start, note.length, note.pitch-60, note.velocity/127, None)

			if tracktype == 'AudioTrack':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
				track_obj.params.add('vol', zm_track.volume/100, 'float')
				track_obj.params.add('pan', (zm_track.pan-50)/50, 'float')
				track_obj.visual.from_dset('z_maestro', 'track', 'AudioTrack', True)
				track_obj.visual.name = zm_track.name

				for n, fx in enumerate(zm_track.fx):
					fxid = cvpj_trackid+'_fx_'+str(n)
					fxtype = fx.type
					fxparams = fx.params

					if fxtype == 'LowPassFilter':
						plugin_obj = convproj_obj.plugin__add(fxid, 'universal', 'filter', None)
						if 'Frequency' in fxparams:
							plugin_obj.filter.on = True
							plugin_obj.filter.type.set('low_pass', None)
							plugin_obj.filter.freq = int(fxparams['Frequency'])/2
					elif fxtype == 'HighPassFilter':
						plugin_obj = convproj_obj.plugin__add(fxid, 'universal', 'filter', None)
						if 'Frequency' in fxparams:
							plugin_obj.filter.on = True
							plugin_obj.filter.type.set('high_pass', None)
							plugin_obj.filter.freq = int(fxparams['Frequency'])/2
					elif fxtype == 'Echo':
						delay_obj = fx_delay.fx_delay()
						delay_obj.feedback_first = True
						if 'Decay' in fxparams: delay_obj.feedback[0] = xtramath.from_db(float(fxparams['Decay']))
						timing_obj = delay_obj.timing_add(0)
						if 'Delay' in fxparams: timing_obj.set_seconds(float(fxparams['Delay']))
						plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, fxid)
					elif fxtype == 'StereoWiden':	
						plugin_obj = convproj_obj.plugin__add(fxid, 'universal', 'width', None)
						if 'Amount' in fxparams: plugin_obj.params.add('width', float(fxparams['Amount'])-1, 'float')
					elif fxtype == 'Invert':	
						plugin_obj = convproj_obj.plugin__add(fxid, 'universal', 'invert', None)
					elif fxtype == 'Compressor':
						plugin_obj = convproj_obj.plugin__add(fxid, 'universal', 'compressor', None)
						if 'Attack' in fxparams: plugin_obj.params.add('attack', float(fxparams['Attack'])/1000, 'float')
						plugin_obj.params.add('pregain', 0, 'float')
						if 'Soft_Knee' in fxparams: plugin_obj.params.add('knee', float(fxparams['Soft_Knee']), 'float')
						if 'Output_Gain' in fxparams: plugin_obj.params.add('postgain', float(fxparams['Output_Gain']), 'float')
						if 'Ratio' in fxparams: plugin_obj.params.add('ratio', float(fxparams['Ratio']), 'float')
						if 'Release' in fxparams: plugin_obj.params.add('release', float(fxparams['Release'])/1000, 'float')
						if 'Threshold' in fxparams: plugin_obj.params.add('threshold', float(fxparams['Threshold']), 'float')
					else:
						plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'z_maestro', fx.type)
						for key, val in fx.params.items():
							if val.replace('.', '').isnumeric(): plugin_obj.params.add(key, float(val), 'float')
							elif val in ['true', 'false']: plugin_obj.params.add(key, val=='true', 'bool')
							else: plugin_obj.datavals.add(key, val)
					plugin_obj.role = 'fx'
					track_obj.plugin_autoplace(plugin_obj, fxid)

				do_automation(convproj_obj, cvpj_trackid, 'vol', zm_track.volumetimeline, zm_track.usevolumetimeline)
				do_automation(convproj_obj, cvpj_trackid, 'pan', zm_track.pantimeline, zm_track.usepantimeline)

				for num, part in enumerate(zm_track.parts):
					placement_obj = track_obj.placements.add_audio()
					placement_obj.visual.name = part.name
					if part.repeats:
						placement_obj.time.set_loop_data(0, 0, part.length)
						placement_obj.time.set_posdur(part.start, part.length+part.repeats)
					else:
						placement_obj.time.set_posdur(part.start, part.length)

					sp_obj = placement_obj.sample
					if not part.oneshot:
						sp_obj.stretch.set_rate_tempo(project_obj.tempo, (part.recordedtempo/part.currenttempo)*tempodiv, True)
						sp_obj.stretch.preserve_pitch = True
					else:
						sp_obj.stretch.set_rate_speed(project_obj.tempo, 1, True)
					sp_obj.stretch.algorithm = 'stretch'

					audio_obj = audio_data.audio_obj()

					if 'nSamplesPerSec' in part.format:
						audio_obj.rate = int(part.format['nSamplesPerSec'])

					if 'nChannels' in part.format:
						audio_obj.channels = int(part.format['nChannels'])

					if 'wBitsPerSample' in part.format:
						bitss = part.format['wBitsPerSample']
						if bitss == '8': audio_obj.set_codec('int8')
						if bitss == '16': audio_obj.set_codec('int16')

					wave_path = samplefolder+'track_'+str(tracknum)+'_part_'+str(num)+'.wav'
					sampleref_id = 'track_'+str(tracknum)+'_part_'+str(num)

					if part.channels:
						sp_obj.sampleref = sampleref_id

						audio_obj.pcm_from_bytes(part.channels)
						audio_obj.to_file_wav(wave_path)

						convproj_obj.sampleref__add(sampleref_id, wave_path, None)

					if project_obj.zipfile:
						try:
							bitss = int(part.format['wBitsPerSample'])
							channels = [project_obj.zipfile.read('Audio/'+part.id+'/Channel'+str(n)) for n in range(audio_obj.channels)]
							lensample = len(channels[0])
		
							if len(channels)==2:
								if bitss == 16:
									outdata = np.zeros(lensample, dtype=np.uint16)
									outdata[:lensample][0::2] = np.frombuffer(channels[0], dtype=np.uint16)
									outdata[:lensample][1::2] = np.frombuffer(channels[1], dtype=np.uint16)
								if bitss == 8:
									outdata = np.zeros(lensample, dtype=np.uint8)
									outdata[:lensample][0::2] = np.frombuffer(channels[0], dtype=np.uint8)
									outdata[:lensample][1::2] = np.frombuffer(channels[1], dtype=np.uint8)
								audio_obj.pcm_from_bytes(outdata.tobytes())
							if len(channels)==1:
								audio_obj.pcm_from_bytes(channels[0])

							audio_obj.to_file_wav(wave_path)
							convproj_obj.sampleref__add(sampleref_id, wave_path, None)
							sp_obj.sampleref = sampleref_id
						except:
							pass