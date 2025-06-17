# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects import globalstore
from functions import xtramath

PL_MODE = 0

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
		in_dict['plugin_included'] = ['universal:sampler:single']
		in_dict['projtype'] = 'mi'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_uncommon import hydrogen as proj_hydrogen
		from objects import colors
		from objects.convproj import fileref

		convproj_obj.type = 'mi'
		convproj_obj.fxtype = 'none'
		convproj_obj.set_timings(48)

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_points']

		project_obj = proj_hydrogen.hydrogen_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()
		
		fileref.cvpj_fileref_global.add_prefix('hydrogen_drumkits', 'win', "C:\\Program Files\\Hydrogen\\data\\drumkits\\")

		globalstore.dataset.load('hydrogen', './data_main/dataset/hydrogen.dset')
		color_pattern = colors.colorset.from_dataset('hydrogen', 'pattern', 'main')
		color_track = colors.colorset.from_dataset('hydrogen', 'track', 'main')

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.author = project_obj.author
		convproj_obj.metadata.comment_text = project_obj.notes
		convproj_obj.metadata.data['license'] = project_obj.license

		bpm = project_obj.bpm

		if project_obj.BPMTimeLine:
			convproj_obj.automation.add_autopoint(['main', 'bpm'], 'float', 0, project_obj.bpm, 'instant')
			for bpmtl in project_obj.BPMTimeLine:
				convproj_obj.automation.add_autopoint(['main', 'bpm'], 'float', bpmtl.bar*48*4, bpmtl.bpm, 'instant')
				if bpmtl.bar == 0: bpm = bpmtl.bpm

		convproj_obj.params.add('bpm', bpm , 'float')
		convproj_obj.track_master.params.add('vol', project_obj.volume, 'float')
		convproj_obj.track_master.params.add('enabled', not project_obj.isMuted, 'float')

		plnum = 0

		if project_obj.playbackTrackFilename:
			playlist_obj = convproj_obj.playlist__add(plnum, 1, True)
			playlist_obj.visual.from_dset('hydrogen', 'track', 'playback', False)
			sampleref_obj = convproj_obj.sampleref__add('playbackTrack', project_obj.playbackTrackFilename, None)
			sre_obj = convproj_obj.sampleindex__add('playbackTrack')
			sre_obj.from_sampleref_obj(sampleref_obj)
			sre_obj.sampleref = 'playbackTrack'
			sre_obj.stretch.timing.set__speed(bpm, 1)
			sre_obj.visual.from_dset('hydrogen', 'track', 'playback', False)
			cvpj_placement = playlist_obj.placements.add_audio_indexed()
			cvpj_placement.fromindex = 'playbackTrack'
			dur_sec = sampleref_obj.get_dur_sec()
			if dur_sec: 
				time_obj = placement_obj.time
				time_obj.set_posdur(0, dur_sec*48*2*(bpm/120))
			plnum += 1

		for tag in project_obj.timeLineTag:
			timemarker_obj = convproj_obj.timemarker__add()
			timemarker_obj.position = tag.bar*48*4
			timemarker_obj.visual.name = tag.tag

		for autopath in project_obj.automationPaths:
			if autopath.adjust == 'velocity':
				for p, v in autopath.points.items():
					convproj_obj.automation.add_autopoint(['master', 'vol'], 'float', p*48*4, v, 'normal')

		for instrument in project_obj.instrumentList:
			inst_obj = convproj_obj.instrument__add(str(instrument.id))
			inst_obj.visual.name = instrument.name
			drumkit = instrument.drumkit
			opan, ovol = xtramath.sep_pan_to_vol(instrument.pan_L, instrument.pan_R)
			inst_obj.params.add('pan', opan, 'float')
			inst_obj.params.add('vol', instrument.volume*instrument.gain*ovol, 'float')
			inst_obj.params.add('enabled', not bool(instrument.isMuted), 'float')
			inst_obj.params.add('solo', bool(instrument.isSoloed), 'float')
			inst_obj.is_drum = True

			plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
			plugin_obj.role = 'synth'
			inst_obj.plugslots.set_synth(synthid)

			inst_obj.datavals.add('middlenote', -int(instrument.pitchOffset))
			inst_obj.datavals.add('random_pitch', instrument.randomPitchFactor)
			inst_obj.datavals.add('random_pitch', instrument.randomPitchFactor)

			if instrument.filterActive:
				filter_id = str(instrument.id)+'_filter'
				filtplug_obj = convproj_obj.plugin__add(filter_id, 'universal', 'filter', None)
				filtplug_obj.filter.on = True
				filtplug_obj.filter.type.set('low_pass', None)
				filtplug_obj.filter.freq = xtramath.midi_filter(instrument.filterCutoff)*2.3
				filtplug_obj.filter.q = (instrument.filterResonance*10)+1
				filtplug_obj.role = 'effect'
				inst_obj.plugslots.slots_audio.append(filter_id)

			for layer in instrument.instrumentComponent.layers:
				filename = layer.filename
				sampleid = drumkit+'__'+filename
				sampleref_obj = convproj_obj.sampleref__add__prefix(sampleid, 'hydrogen_drumkits', '.\\GMRockKit\\'+filename)
				sampleref_obj.fileref.resolve_prefix()

				sp_obj = plugin_obj.sampleregion_add(-50, 50, 0, None)
				sp_obj.sampleref = sampleid
				sp_obj.vel_min = layer.min
				sp_obj.vel_max = layer.max
				sp_obj.vol = layer.gain
				sp_obj.trigger = 'oneshot'
				sp_obj.pitch = layer.pitch
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
			cvpj_notelist = nle_obj.notelist
			for note in pattern.noteList:
				extra = {}
				if note.probability: extra['probability'] = note.probability
				cvpj_notelist.add_m(str(note.instrument), note.position, 12, 0, note.velocity, extra if extra else None)
				cvpj_notelist.last_add_pan(note.pan)

		maxdup = min([len(x) for x in project_obj.patternSequence]) if project_obj.patternSequence else 0

		if maxdup > 1 or PL_MODE:
			for n, pattern in enumerate(project_obj.patternList):
				playlist_obj = convproj_obj.playlist__add(plnum, 1, True)
				playlist_obj.visual.name = pattern.name
				playlist_obj.visual.color.set_int(color_track.getcolornum(n))
				for p, x in enumerate([pattern.name in x for x in project_obj.patternSequence]):
					if x:
						cvpj_placement = playlist_obj.placements.add_notes_indexed()
						cvpj_placement.fromindex = pattern.name
						time_obj = cvpj_placement.time
						time_obj.set_posdur(p*48*4, pattern.size)
				plnum += 1
		else:
			playlist_obj = convproj_obj.playlist__add(plnum, 1, True)
			playlist_obj.visual.name = 'Main'
			playlist_obj.visual.color.set_int(color_track.getcolornum(n))
			for p, x in enumerate(project_obj.patternSequence):
				for fromindex in x:
					cvpj_placement = playlist_obj.placements.add_notes_indexed()
					cvpj_placement.fromindex = fromindex
					time_obj = cvpj_placement.time
					time_obj.set_posdur(p*48*4, pattern.size)

		convproj_obj.do_actions.append('do_sorttracks')
		convproj_obj.do_actions.append('do_addloop')

		#for sendnum in range(4):
		#	returnid = 'return__'+str(sendnum)
		#	track_obj = convproj_obj.track_master.fx__return__add(returnid)
