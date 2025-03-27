# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects import globalstore

class input_hydrogen(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'hydrogen'
	
	def get_name(self):
		return 'Hydrogen'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['h2song']
		in_dict['plugin_included'] = ['universal:sampler:single']
		in_dict['projtype'] = 'mi'
		in_dict['fxtype'] = 'none'
		in_dict['track_lanes'] = True

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_uncommon import hydrogen as proj_hydrogen
		from objects import colors
		from objects.convproj import fileref

		convproj_obj.type = 'mi'
		convproj_obj.fxtype = 'none'
		convproj_obj.set_timings(48, True)

		project_obj = proj_hydrogen.hydrogen_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		fileref.filesearcher.add_searchpath_full_append('hydrogen_drumkits', "C:\\Program Files\\Hydrogen\\data\\drumkits\\", 'win')

		globalstore.dataset.load('hydrogen', './data_main/dataset/hydrogen.dset')
		color_pattern = colors.colorset.from_dataset('hydrogen', 'pattern', 'main')
		color_track = colors.colorset.from_dataset('hydrogen', 'track', 'main')

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.author = project_obj.author
		convproj_obj.metadata.comment_text = project_obj.notes

		convproj_obj.params.add('bpm', project_obj.bpm , 'float')

		for instrument in project_obj.instrumentList:
			inst_obj = convproj_obj.instrument__add(str(instrument.id))
			inst_obj.visual.name = instrument.name
			drumkit = instrument.drumkit
			inst_obj.params.add('vol', instrument.volume*instrument.gain, 'float')
			inst_obj.params.add('enabled', not bool(instrument.isMuted), 'float')
			inst_obj.params.add('solo', bool(instrument.isSoloed), 'float')
			inst_obj.is_drum = True

			plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
			plugin_obj.role = 'synth'
			inst_obj.plugslots.set_synth(synthid)

			for layer in instrument.instrumentComponent.layers:
				filename = layer.filename
				sampleid = drumkit+'__'+filename
				sampleref_obj = convproj_obj.sampleref__add(sampleid, '.\\GMRockKit\\'+filename, 'win')
				sampleref_obj.find_relative('hydrogen_drumkits')
				sp_obj = plugin_obj.sampleregion_add(-50, 50, 0, None)
				sp_obj.sampleref = sampleid
				sp_obj.vel_min = layer.min
				sp_obj.vel_max = layer.max
				sp_obj.vol = layer.gain
				sp_obj.trigger = 'oneshot'
			#inst_obj.sends.add('return__0', None, instrument.FX1Level)
			#inst_obj.sends.add('return__1', None, instrument.FX2Level)
			#inst_obj.sends.add('return__2', None, instrument.FX3Level)
			#inst_obj.sends.add('return__3', None, instrument.FX4Level)

		for n, pattern in enumerate(project_obj.patternList):
			nle_obj = convproj_obj.notelistindex__add(pattern.name)
			nle_obj.visual.name = pattern.name
			nle_obj.visual.comment = pattern.info
			nle_obj.visual.color.set_int(color_pattern.getcolornum(n))
			nle_obj.timesig_auto.add_point(0, [4, pattern.denominator])
			for note in pattern.noteList:
				extra = {}
				if note.pan: extra['pan'] = note.pan
				if note.probability: extra['probability'] = note.probability
				nle_obj.notelist.add_m(str(note.instrument), note.position, 12, 0, note.velocity, extra if extra else None)

		for n, pattern in enumerate(project_obj.patternList):
			playlist_obj = convproj_obj.playlist__add(n, 1, True)
			playlist_obj.visual.name = pattern.name
			playlist_obj.visual.color.set_int(color_track.getcolornum(n))
			for p, x in enumerate([pattern.name in x for x in project_obj.patternSequence]):
				if x:
					cvpj_placement = playlist_obj.placements.add_notes_indexed()
					cvpj_placement.fromindex = pattern.name
					cvpj_placement.time.set_posdur(p*48*4, pattern.size)

		convproj_obj.do_actions.append('do_sorttracks')
		convproj_obj.do_actions.append('do_addloop')

		#for sendnum in range(4):
		#	returnid = 'return__'+str(sendnum)
		#	track_obj = convproj_obj.track_master.fx__return__add(returnid)
