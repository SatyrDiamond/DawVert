# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
import plugins
import os

class input_orgyana(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'orgyana'
	
	def get_name(self):
		return 'Orgyana'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['org']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:synth-osc']
		in_dict['projtype'] = 'r'

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'Org-02'])
		detectdef_obj.headers.append([0, b'Org-03'])

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_uncommon import orgyana as proj_orgyana
		from objects import colors
		from objects import audio_data

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('orgyana', './data_main/dataset/orgyana.dset')
		colordata = colors.colorset.from_dataset('orgyana', 'track', 'orgmaker_2')

		project_obj = proj_orgyana.orgyana_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		orgsamp_filename = os.path.join(dawvert_intent.path_external_data, 'orgyana', 'orgsamp.dat')

		orgdrum_sob = {}

		orgsamp_obj = proj_orgyana.orgyana_orgsamp()
		if os.path.exists(orgsamp_filename): orgsamp_obj.load_from_file(orgsamp_filename)

		for tracknum, orgtrack_obj in enumerate(project_obj.tracks):
			if len(orgtrack_obj.notes) != 0:

				idval = 'org_'+str(tracknum)
				track_obj = convproj_obj.track__add(idval, 'instrument', 0, False)
				if tracknum > 7: 
					track_obj.visual.from_dset('orgyana', 'drums', str(orgtrack_obj.instrument), False)
					track_obj.is_drum = True
					if orgsamp_obj.loaded:
						drum_filename = os.path.join(dawvert_intent.path_samples['extracted']+'orgmaker_drum_'+str(orgtrack_obj.instrument)+'.wav')

						if orgtrack_obj.instrument not in orgdrum_sob:
							audio_obj = audio_data.audio_obj()
							audio_obj.set_codec('int8')
							audio_obj.rate = orgsamp_obj.drum_rate
							audio_obj.pcm_from_list(orgsamp_obj.drum_data[orgtrack_obj.instrument])
							audio_obj.to_file_wav(drum_filename)
							sampleref_obj = convproj_obj.sampleref__add(drum_filename, drum_filename, None)
							sampleref_obj.set_fileformat('wav')
							audio_obj.to_sampleref_obj(sampleref_obj)
							orgdrum_sob[orgtrack_obj.instrument] = sampleref_obj

						plugin_obj, pluginid, sp_obj = convproj_obj.plugin__addspec__sampler__genid__s_obj(orgdrum_sob[orgtrack_obj.instrument], drum_filename)
						sp_obj.trigger = 'oneshot'
						track_obj.plugslots.set_synth(pluginid)
				else: 
					track_obj.visual.name = "Melody "+str(tracknum+1)
					if orgsamp_obj.loaded:
						plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
						track_obj.plugslots.set_synth(pluginid)
						osc_data = plugin_obj.osc_add()
						osc_data.prop.type = 'wave'
						osc_data.prop.nameid = 'main'
						wave_obj = plugin_obj.wave_add('main')
						wave_obj.set_all_range(list(orgsamp_obj.sample_data[orgtrack_obj.instrument]), -128, 128)
						track_obj.plugslots.set_synth(pluginid)

				track_obj.visual.color.set_int(colordata.getcolornum(tracknum))
				track_obj.params.add('pitch', (orgtrack_obj.pitch-1000)/1800, 'float')

				posnotes = {}
				for org_note in orgtrack_obj.notes: posnotes[org_note[0]] = org_note[1:5]
				posnotes = dict(sorted(posnotes.items(), key=lambda item: item[0]))
				endnote = None
				notedur = 0
				org_notelist = []

				cvpj_notelist = track_obj.placements.notelist

				pan_autoid = ['track', idval, 'pan']

				last_pan_pos = 0
				last_pan_val = 0

				for pos, orgnote in posnotes.items():
					note, dur, vol, pan = orgnote
					pan = (pan-6)/6

					if endnote != None: 
						if pos >= endnote: endnote = None
					if orgnote[1] != 1:
						notedur = orgnote[1]
						endnote = pos+notedur
					if endnote != None: isinsidenote = False if endnote-pos == notedur else True
					else: isinsidenote = False
					if not isinsidenote: 
						cvpj_notelist.add_r(pos, dur, note-24 if tracknum > 7 else note-36, vol/254, None)
						notepos = pos
						if pan or last_pan_val:
							convproj_obj.automation.add_autopoint(pan_autoid, 'float', pos, pan, 'instant')
						last_pan_pos = pos
						last_pan_val = pan
					else:
						if pan!=last_pan_val:
							if last_pan_pos>1:
								insidepos = pos-notepos
								convproj_obj.automation.add_autopoint(pan_autoid, 'float', pos-0.25, last_pan_val, 'normal')
								convproj_obj.automation.add_autopoint(pan_autoid, 'float', pos+0.25, pan, 'normal')
						last_pan_pos = pos
						last_pan_val = pan

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', (1/(project_obj.wait/122))*122, 'float')
		convproj_obj.timesig = [project_obj.stepsperbar, project_obj.beatsperstep]

		if project_obj.loop_beginning != 0: 
			convproj_obj.transport.loop_active = True
			convproj_obj.transport.loop_start = project_obj.loop_beginning
			convproj_obj.transport.loop_end = project_obj.loop_end