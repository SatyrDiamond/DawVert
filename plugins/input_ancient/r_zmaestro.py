# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import plugins
import numpy as np

def do_automation(convproj_obj, trackid, atype, timelineobj):
	nextinstant = False
	for event in timelineobj:
		value = 0
		if atype == 'vol': value = event.value/100
		if atype == 'pan': value = (event.value-50)/50

		autopoint_obj = convproj_obj.automation.add_autopoint(['track', trackid, atype], 'float', event.position, value, 'normal' if not nextinstant else 'instant')
		if nextinstant: nextinstant = False
		if event.fade == 'Exponential': autopoint_obj.tension = -1
		if event.fade == 'Logarithmic': autopoint_obj.tension = 1
		if event.fade == 'Edge': nextinstant = True

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
		in_dict['audio_filetypes'] = ['wav']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['placement_loop'] = ['loop']
		in_dict['projtype'] = 'r'
		in_dict['plugin_included'] = ['native:z_maestro','universal:midi']

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import z_maestro as proj_z_maestro
		from objects import audio_data

		samplefolder = dawvert_intent.path_samples['extracted']

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

		for tracknum, md in enumerate(project_obj.tracks):
			tracktype, zm_track = md
			cvpj_trackid = 'track_'+str(tracknum)

			if tracktype in ['MIDITrack', 'MIDIDrumTrack']:
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
				track_obj.params.add('vol', zm_track.volume/100, 'float')
				track_obj.params.add('pan', (zm_track.pan-50)/50, 'float')
				track_obj.visual.name = zm_track.name
				track_obj.midi.out_inst.patch = zm_track.instrumentcode
				track_obj.midi.out_inst.bank = zm_track.instrumentbank
				track_obj.to_midi(convproj_obj, cvpj_trackid, True)
				if tracktype == 'MIDIDrumTrack': track_obj.is_drum = True

				do_automation(convproj_obj, cvpj_trackid, 'vol', zm_track.volumetimeline)
				do_automation(convproj_obj, cvpj_trackid, 'pan', zm_track.pantimeline)

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
				track_obj.visual.name = zm_track.name

				for n, fx in enumerate(zm_track.fx):
					fxid = cvpj_trackid+'_fx_'+str(n)
					plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'z_maestro', fx.type)
					plugin_obj.role = 'fx'
					for key, val in fx.params.items():
						if val.replace('.', '').isnumeric(): plugin_obj.params.add(key, float(val), 'float')
						elif val in ['true', 'false']: plugin_obj.params.add(key, val=='true', 'bool')
						else: plugin_obj.datavals.add(key, val)
					track_obj.plugin_autoplace(plugin_obj, fxid)

				do_automation(convproj_obj, cvpj_trackid, 'vol', zm_track.volumetimeline)
				do_automation(convproj_obj, cvpj_trackid, 'pan', zm_track.pantimeline)

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
					else:
						sp_obj.stretch.set_rate_tempo(project_obj.tempo, (part.recordedtempo/part.currenttempo), True)
					sp_obj.stretch.preserve_pitch = True
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