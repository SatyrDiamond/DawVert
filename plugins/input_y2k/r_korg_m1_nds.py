# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os
from objects import globalstore

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
		convproj_obj.set_timings(4, True)

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['pl_points']

		project_obj = proj_korg_m1_nds.korg_m1_proj()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.dataset.load('korg_m1d', './data_main/dataset/korg_m1d.dset')

		projsong_obj = project_obj.songs[dawvert_intent.songnum]
		steps = projsong_obj.steps
		swing = projsong_obj.swing

		convproj_obj.params.add('bpm', projsong_obj.tempo, 'float')
		convproj_obj.metadata.name = projsong_obj.name

		return_obj = convproj_obj.track_master.fx__return__add('trackfx')
		return_obj.visual.name = 'FX'

		#for n, tempo in enumerate(projsong_obj.blockTempos):
		#	print(n, tempo, projsong_obj.blockSteps[n])

		tempopos = [(x if x else projsong_obj.tempo) for x in projsong_obj.blockTempos]
		stepsizes = [(x if x else projsong_obj.steps) for x in projsong_obj.blockSteps]
		poslist = []
		curnum = 0
		for stepsize in stepsizes:
			poslist.append(curnum)
			curnum += stepsize

		curpos = 0
		for n, tempo in enumerate(tempopos):
			stepcur = stepsizes[n]
			autopl_obj = convproj_obj.automation.add_pl_points(['main','bpm'], 'float')
			autopl_obj.time.set_posdur(curpos, stepcur)

			autopoints_obj = autopl_obj.data
			autopoints_obj.points__add_normal(0, tempo, 0, None)

			curpos += stepcur

		for num, channel_obj in enumerate(projsong_obj.channels):
			cvpj_trackid = str(num)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
			track_obj.params.add('vol', channel_obj.volume/127, 'float')
			track_obj.params.add('pan', channel_obj.pan/5, 'float')
			track_obj.params.add('enabled', 1 not in channel_obj.flags, 'bool')
			track_obj.params.add('solo', 2 in channel_obj.flags, 'bool')

			if 0 in channel_obj.flags:
				track_obj.sends.add('trackfx', None, 1)

			if channel_obj.mode<3:
				instset = ['m1','m1w','ex'][channel_obj.mode]
				dset_cat_obj = globalstore.dataset.get_cat('korg_m1d', instset)
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
				stepcur = stepsizes[n]

				placement_obj = track_obj.placements.add_notes()
				placement_obj.time.set_posdur(poslist[block_obj.offset], stepsizes[block_obj.offset])

				cvpj_notelist = placement_obj.notelist

				for note in block_obj.notes:
					oswing = ((swing-50)/50) if (note.offset%2) else 0
					cvpj_notelist.add_r(note.offset+oswing, note.length, (note.pitch-128)-60, note.velocity/15, None)
				curpos += stepcur

		convproj_obj.timemarker__from_patlenlist(stepsizes, 0)
