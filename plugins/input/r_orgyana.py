# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
import plugins
import os

class input_orgyana(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'orgyana'
	def get_name(self): return 'Orgyana'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['org']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:synth-osc']
		in_dict['projtype'] = 'r'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(6)
		if bytesdata == b'Org-02' or bytesdata == b'Org-03': return True
		else: return False

	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_orgyana
		from objects import colors
		from objects import audio_data

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('orgyana', './data_main/dataset/orgyana.dset')
		colordata = colors.colorset.from_dataset('orgyana', 'track', 'orgmaker_2')

		project_obj = proj_orgyana.orgyana_project()
		if not project_obj.load_from_file(input_file): exit()

		orgsamp_filename = os.path.join(dv_config.path_external_data, 'orgyana', 'orgsamp.dat')

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
						drum_filename = os.path.join(dv_config.path_samples_extracted+'orgmaker_drum_'+str(orgtrack_obj.instrument)+'.wav')
						if not os.path.exists(drum_filename):
							audio_obj = audio_data.audio_obj()
							audio_obj.set_codec('int8')
							audio_obj.rate = orgsamp_obj.drum_rate
							audio_obj.pcm_from_list(orgsamp_obj.drum_data[orgtrack_obj.instrument])
							audio_obj.to_file_wav(drum_filename)
						plugin_obj, pluginid, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler__genid(drum_filename, None)
						sp_obj.trigger = 'oneshot'
						track_obj.inst_pluginid = pluginid
				else: 
					track_obj.visual.name = "Melody "+str(tracknum+1)
					if orgsamp_obj.loaded:
						plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
						track_obj.inst_pluginid = pluginid
						osc_data = plugin_obj.osc_add()
						osc_data.prop.type = 'wave'
						osc_data.prop.nameid = 'main'
						wave_obj = plugin_obj.wave_add('main')
						wave_obj.set_all_range(list(orgsamp_obj.sample_data[orgtrack_obj.instrument]), -128, 128)
						track_obj.inst_pluginid = pluginid

				track_obj.visual.color.set_float(colordata.getcolornum(tracknum))
				track_obj.params.add('pitch', (orgtrack_obj.pitch-1000)/1800, 'float')

				posnotes = {}
				for org_note in orgtrack_obj.notes: posnotes[org_note[0]] = org_note[1:5]
				posnotes = dict(sorted(posnotes.items(), key=lambda item: item[0]))
				endnote = None
				notedur = 0
				org_notelist = []
				for pos, orgnote in posnotes.items():
					note, dur, vol, pan = orgnote
					if endnote != None: 
						if pos >= endnote: endnote = None
					if orgnote[1] != 1:
						notedur = orgnote[1]
						endnote = pos+notedur
					if endnote != None: isinsidenote = False if endnote-pos == notedur else True
					else: isinsidenote = False
					if not isinsidenote: 
						track_obj.placements.notelist.add_r(pos, dur, note-24 if tracknum > 7 else note-36, vol/254, {'pan': (pan-6)/6})

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', (1/(project_obj.wait/122))*122, 'float')
		convproj_obj.timesig = [project_obj.stepsperbar, project_obj.beatsperstep]

		if project_obj.loop_beginning != 0: 
			convproj_obj.loop_active = True
			convproj_obj.loop_start = project_obj.loop_beginning
			convproj_obj.loop_end = project_obj.loop_end