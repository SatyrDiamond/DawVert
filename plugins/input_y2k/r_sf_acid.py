# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os.path
from objects import globalstore

class input_piyopiyo(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'sf_acid'
	
	def get_name(self):
		return 'Sonic Foundry ACID'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['fxtype'] = 'groupreturn'

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import sony_acid as sony_acid

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.set_timings(768, False)

		project_obj = sony_acid.sony_acid_file()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.dataset.load('sony_acid', './data_main/dataset/sony_acid.dset')
		colordata = colors.colorset.from_dataset('sony_acid', 'track', 'acid_1')
		convproj_obj.params.add('bpm', project_obj.tempo, 'float')

		samplefolder = dawvert_intent.path_samples['extracted']

		for x in range(2):
			returnid = 'return__'+str(x)
			track_obj = convproj_obj.track_master.fx__return__add(returnid)
			track_obj.visual.name = 'FX '+str(x+1)

		for tracknum, track in enumerate(project_obj.tracks):
			cvpj_trackid = 'track_'+str(tracknum)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
			track_obj.visual.name = track.name
			track_obj.visual.color.set_int(colordata.getcolornum(track.color))
			track_obj.params.add('vol', track.vol, 'float')
			track_obj.params.add('pan', track.pan, 'float')

			for send in track.sends:
				returnid = 'return__'+str(send.id)
				track_obj.sends.add(returnid, 'send_%i_%i' % (tracknum, send.id), send.vol)

			sample_tempo = track.stretch__tempo
			sample_beats = track.num_beats

			sample_path = None

			if project_obj.audios:
				if len(project_obj.audios)>=tracknum:
					wave_path = samplefolder+'track_'+str(tracknum)+'.wav'
					outaudio = bytearray(project_obj.audios[tracknum])
					if len(outaudio)>12:
						if outaudio[8:12] == b'wave': outaudio[8:12] = b'WAVE'

					wav_fileobj = open(wave_path, 'wb')
					wav_fileobj.write(outaudio)
					sampleref_obj = convproj_obj.sampleref__add(wave_path, wave_path, 'win')
					sample_path = wave_path
			else:
				sample_path = track.path
				sampleref_obj = convproj_obj.sampleref__add(sample_path, sample_path, 'win')
				sampleref_obj.search_local(os.path.dirname(dawvert_intent.input_file))

			trackpitch = track.pitch
			root_note = track.root_note

			noteo = 60-root_note
			notec = ((noteo+6)//12)*12
			notec = noteo-notec

			stretch_size = sample_tempo/project_obj.tempo

			for region in track.regions:
				placement_obj = track_obj.placements.add_audio()

				time_obj = placement_obj.time
				time_obj.set_startend(region.start, region.end)
				time_obj.set_loop_data(0, 0, sample_beats*768)

				sp_obj = placement_obj.sample
				sp_obj.sampleref = sample_path

				sp_obj.stretch.set_rate_tempo(project_obj.tempo, sample_tempo/120, True)
				sp_obj.stretch.preserve_pitch = True

				sp_obj.pitch = trackpitch + region.pitch + notec

				for env in region.envs:
					autoloc = None
					if env.type == 0: autoloc = ['track', cvpj_trackid, 'vol']
					if env.type == 1: autoloc = ['track', cvpj_trackid, 'pan']
					if env.type == 2: autoloc = ['send', 'send_%i_%i' % (tracknum, 0), 'amount']
					if env.type == 3: autoloc = ['send', 'send_%i_%i' % (tracknum, 1), 'amount']
					if autoloc:
						autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
						autopl_obj.time.set_startend(region.start, region.end)
						for point in env.points:
							autopoint_obj = autopl_obj.data.add_point()
							autopoint_obj.pos = point[0]
							if point[0] == 2:
								autopoint_obj.tension = 1
							if point[0] == -2:
								autopoint_obj.tension = -1
							autopoint_obj.type = 'normal'
							autopoint_obj.value = point[1]

		convproj_obj.automation.set_persist_all(False)