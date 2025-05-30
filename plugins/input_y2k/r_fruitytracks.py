# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os

from objects.convproj import fileref

def calc_tick_val(bpmdiv, inpos):
	return (inpos/5512)/bpmdiv

def make_auto(convproj_obj, autoloc, plpos, pldur, startval, endval, envpoints, defval, iseff, bpmdiv):
	autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
	time_obj = autopl_obj.time
	time_obj.set_posdur(plpos, pldur)

	autopoints_obj = autopl_obj.data

	autopoints_obj.points__add_normal(1, startval if not iseff else startval*defval, 0, None)

	if envpoints:
		for pos, val in envpoints:
			pos = calc_tick_val(bpmdiv, pos)
			if pos<pldur:
				autopoints_obj.points__add_normal(pos, val if not iseff else val*defval, 0, None)

	autopoints_obj.points__add_normal(pldur-0.0001, endval if not iseff else endval*defval, 0, None)

	return autopl_obj

class input_fruitytracks(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'

	def get_shortname(self):
		return 'fruitytracks'

	def get_name(self):
		return 'FruityTracks'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import fruitytracks as proj_fruitytracks

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		traits_obj = convproj_obj.traits
		traits_obj.placement_cut = True
		traits_obj.audio_filetypes = ['wav', 'mp3']
		traits_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
		traits_obj.audio_stretch = ['rate']
		traits_obj.auto_types = ['pl_points']

		fileref.filesearcher.add_searchpath_partial('fruitytracks', '../Samples/', 'projectfile')

		project_obj = proj_fruitytracks.ftr_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		convproj_obj.track_master.params.add('vol', project_obj.vol/128, 'float')

		bpmdiv = 120/project_obj.bpm
		bpmticks = 5512

		if project_obj.title: convproj_obj.metadata.name = project_obj.title
		if project_obj.url: convproj_obj.metadata.url = project_obj.url
		if project_obj.comment:
			convproj_obj.metadata.comment_text = project_obj.comment
			convproj_obj.metadata.comment_datatype = 'rtf'
		convproj_obj.metadata.show = project_obj.showinfo

		if project_obj.loopend:
			convproj_obj.transport.loop_active = True
			convproj_obj.transport.loop_start = calc_tick_val(bpmdiv, project_obj.loopstart)
			convproj_obj.transport.loop_end = calc_tick_val(bpmdiv, project_obj.loopstart+project_obj.loopend)

		for tracknum, ftr_track in enumerate(project_obj.tracks):
			trackid = str(tracknum)
			track_obj = convproj_obj.track__add(trackid, 'audio', 1, False)
			track_obj.visual.name = ftr_track.name if ftr_track.name else 'Track '+str(tracknum)
			track_obj.params.add('pan', (ftr_track.pan-64)/64, 'float')
			track_obj.params.add('vol', ftr_track.vol/128, 'float')
			track_obj.params.add('enabled', not bool(ftr_track.muted), 'bool')

			for pid in sorted(ftr_track.plugins):
				flplug = ftr_track.plugins[pid]

				fxid = trackid+'_'+str(pid)
				splitfile = flplug.name.split('.')
				plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'fruitytracks', splitfile[0].lower())
				plugin_obj.visual.name = splitfile[0]
				plugin_obj.datavals.add('file', flplug.name)
				for n, v in enumerate(flplug.params): plugin_obj.params.add(str(n), v, 'float')
				plugin_obj.role = 'fx'
				plugin_obj.fxdata_add(bool(flplug.enabled), None)
				track_obj.plugslots.slots_audio.append(fxid)

			for ftr_clip in ftr_track.clips:
				placement_obj = track_obj.placements.add_audio()
				placement_obj.visual.name = ftr_clip.name
				placement_obj.muted = bool(ftr_clip.muted)
				time_obj = placement_obj.time

				sampleref_obj = convproj_obj.sampleref__add(ftr_clip.file, ftr_clip.file, 'win')
				sampleref_obj.search_local(dawvert_intent.input_folder)
				sampleref_obj.find_relative('projectfile')
				sampleref_obj.find_relative('fruitytracks')

				sp_obj = placement_obj.sample
				sp_obj.sampleref = ftr_clip.file

				plpos = calc_tick_val(bpmdiv, ftr_clip.pos)
				if ftr_clip.stretch == 0:
					pldur = (ftr_clip.dur/bpmticks)
					time_obj.set_loop_data(0, 0, (ftr_clip.repeatlen/bpmticks))
				else:
					pldur = calc_tick_val(bpmdiv, ftr_clip.dur)
					repeatlen = calc_tick_val(bpmdiv, ftr_clip.repeatlen)
					offset = 0 if not ftr_clip.dontstart else calc_tick_val(bpmdiv, ftr_clip.pos%ftr_clip.repeatlen)
					time_obj.set_loop_data(offset, 0, calc_tick_val(bpmdiv, ftr_clip.repeatlen))
					stretch_obj = sp_obj.stretch
					stretch_obj.preserve_pitch = True
					stretch_obj.timing.set__beats(ftr_clip.stretch/4)
				time_obj.set_posdur(plpos, pldur)

				envpoints = ftr_clip.vol_env

				if (ftr_clip.vol_start == ftr_clip.vol_end) and not envpoints:
					sp_obj.vol = ftr_clip.vol_start/128
				else:
					autopl_obj = make_auto(convproj_obj, ['track', trackid, 'vol'], plpos, pldur, ftr_clip.vol_start/128, ftr_clip.vol_end/128, envpoints, ftr_track.vol/128, True, bpmdiv)
					autopl_obj.visual.name = ftr_clip.name

				if (ftr_clip.pan_start == ftr_clip.pan_end):
					sp_obj.pan = (ftr_clip.pan_start-64)/64
				else:
					autopl_obj = make_auto(convproj_obj, ['track', trackid, 'pan'], plpos, pldur, (ftr_clip.pan_start-64)/64, (ftr_clip.pan_end-64)/64, None, (ftr_track.pan-64)/64, False, bpmdiv)
					autopl_obj.visual.name = ftr_clip.name

		convproj_obj.automation.set_persist_all(False)