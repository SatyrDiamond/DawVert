# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os
from objects import globalstore
from objects import regions

class input_korg_m1_nds(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'

	def get_shortname(self):
		return 'korg_m1_nds'

	def get_name(self):
		return 'Korg M01 DS'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import korg_m1_nds as proj_korg_m1_nds

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.set_timings(4.0)

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['pl_ticks']

		project_obj = proj_korg_m1_nds.korg_m1_proj()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.datapack.load('korg_m1d', './data/datapack/realsynth/korg_m1d.xml')

		projsong_obj = project_obj.songs[dawvert_intent.songnum]
		
		convproj_obj.params.add('bpm', projsong_obj.tempo, 'float')
		convproj_obj.metadata.name = projsong_obj.name

		# ------------------------------------------ tempoblocks ------------------------------------------

		tempoblocks = regions.posdurblocks(99, projsong_obj.steps, projsong_obj.tempo)
		for n, x in enumerate(projsong_obj.blockTempos):
			if x: tempoblocks.set_tempo(n, x)
		for n, x in enumerate(projsong_obj.blockSteps):
			if x: tempoblocks.set_steps(n, x)
		tempoblocks.proc()
		tempoblocks.to_cvpj(convproj_obj)

		# ------------------------------------------ song ------------------------------------------

		swing = projsong_obj.swing

		return_obj = convproj_obj.track_master.fx__return__add('trackfx')
		return_obj.visual.name = 'FX'

		if projsong_obj.fx_type:
			return_obj.params.add('vol', projsong_obj.reverb_level/127, 'float')
			plugin_obj = convproj_obj.plugin__add('trackfx', 'native', 'korg_m1', 'reverb')
			param_obj = plugin_obj.params.add('time', projsong_obj.reverb_time, 'int')
			param_obj.add_range(0, 127)
		else:
			return_obj.params.add('vol', projsong_obj.delay_level/127, 'float')
			plugin_obj = convproj_obj.plugin__add('trackfx', 'native', 'korg_m1', 'delay')

			param_obj = plugin_obj.params.add('tempo', bool(projsong_obj.delay_tempo), 'bool')
			param_obj.visual.name = 'Tempo'

			param_obj = plugin_obj.params.add('time', projsong_obj.delay_time, 'int')
			param_obj.visual.name = 'Time'
			param_obj.add_range(0, 127)

			param_obj = plugin_obj.params.add('lr_ratio', projsong_obj.delay_lr_ratio, 'int')
			param_obj.visual.name = 'L/R Ratio'
			param_obj.add_range(-63, 63)

			param_obj = plugin_obj.params.add('fb', projsong_obj.delay_fb, 'int')
			param_obj.visual.name = 'Feedback'
			param_obj.add_range(0, 127)

		return_obj.plugslots.slots_audio.append('trackfx')


		for num, channel_obj in enumerate(projsong_obj.channels):
			cvpj_trackid = str(num)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
			track_obj.params.add('vol', channel_obj.volume/127, 'float')
			track_obj.params.add('pan', channel_obj.pan/5, 'float')
			track_obj.params.add('enabled', 1 not in channel_obj.flags, 'bool')
			track_obj.params.add('solo', 2 in channel_obj.flags, 'bool')
			if 0 in channel_obj.flags: track_obj.sends.add('trackfx', None, 1)

			if channel_obj.mode<3:
				instset = ['m1','m1w','ex'][channel_obj.mode]
				dset_cat_obj = globalstore.datapack.get_cat('korg_m1d', instset)
				if dset_cat_obj:
					if 'numstarts' in dset_cat_obj.data:
						try:
							numstart = [int(x) for x in dset_cat_obj.data['numstarts'].split('|')][channel_obj.cat]
							realpatch = numstart+channel_obj.patch
							dset_obj = dset_cat_obj.objects.get(str(realpatch))
							if dset_obj: track_obj.visual.name = dset_obj.visual.name
							plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'korg_m1', instset)
							track_obj.plugslots.set_synth(pluginid)

							plugin_obj.datavals.add('set', instset)
							plugin_obj.datavals.add('patch', realpatch)
							plugin_obj.datavals.add('attack', channel_obj.attack)
							plugin_obj.datavals.add('release', channel_obj.release)

							for n, drumparam in enumerate(channel_obj.drumparams):
								starttxt = 'drum_%i_' % n
								plugin_obj.params.add(starttxt+'level', drumparam.level/15, 'float')
								plugin_obj.params.add(starttxt+'pan', (drumparam.pan-5)/5, 'float')
								plugin_obj.params.add(starttxt+'tune', drumparam.tune, 'float')
						except:
							pass

			curpos = 0
			for n, block_obj in enumerate(channel_obj.blocks):
				placement_obj = track_obj.placements.add_notes()

				p_start, p_steps = tempoblocks.get_posdur(block_obj.offset)

				time_obj = placement_obj.time
				time_obj.set_posdur(p_start, p_steps)
				cvpj_notelist = placement_obj.notelist
				for note in block_obj.notes:
					oswing = ((swing-50)/50) if (note.offset%2) else 0
					cvpj_notelist.add_r(note.offset+oswing, note.length, (note.pitch-128)-60, note.velocity/15, None)
