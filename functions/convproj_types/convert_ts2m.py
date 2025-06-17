# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
from objects.convproj.tracker import pat_data

logger_project = logging.getLogger('project')

def convert(convproj_obj):
	logger_project.info('ProjType Convert: TrackerSingle > Multiple')
	assert convproj_obj.tracker_single is not None
	tracker_obj = convproj_obj.tracker_single

	convproj_obj.type = 'm'
	convproj_obj.set_timings(4.0)

	convproj_obj.do_actions.append('do_addloop')
	convproj_obj.do_actions.append('do_lanefit')
	convproj_obj.params.add('bpm', tracker_obj.tempo/(tracker_obj.speed/6), 'float')

	playstr = pat_data.playstream()
	playstr.init_tempo(tracker_obj.tempo, tracker_obj.speed)
	for _ in range(tracker_obj.num_chans): playstr.add_channel(tracker_obj.assoc_instid)

	for i, n in enumerate(tracker_obj.orders):
		if n in tracker_obj.patdata:
			singlepat_obj = tracker_obj.patdata[n]
			playstr.init_patinfo(singlepat_obj.num_rows, n)
			playstr.columns = singlepat_obj.data
			while playstr.next_row(): pass

	if tracker_obj.use_starttempo and playstr.first_speed:
		convproj_obj.params.add('bpm', playstr.first_speed, 'float')

	playstr.auto_tempo.to_cvpj(convproj_obj, ['main','bpm'])
	playstr.auto_mastervol.to_cvpj(convproj_obj, ['main','vol'])

	for chns in playstr.notestreams: chns.add_pl(-1)

	used_inst = []

	for ch_num, chan_obj in enumerate(tracker_obj.channels):
		playlist_obj = convproj_obj.playlist__add(ch_num, True, False)
		playlist_obj.visual.name = chan_obj.name
		playlist_obj.visual.color = chan_obj.color

		cur_pl_pos = 0
		for tpl in playstr.notestreams[ch_num].placements:
			if tpl[0]:
				for ui in tpl[3]:
					if ui not in used_inst: used_inst.append(ui)

				if tpl[1].notesfound():
					placement_obj = playlist_obj.placements.add_notes()
					placement_obj.time.set_posdur(cur_pl_pos, tpl[0])
					placement_obj.notelist = tpl[1]
					placement_obj.visual.name = tracker_obj.patdata[tpl[2]].name
			cur_pl_pos += tpl[0]

	patlentable = [x[0] for x in playstr.notestreams[0].placements]
	convproj_obj.timemarker__from_patlenlist(patlentable[:-1], -1)

	c = 0
	for p, x in enumerate(patlentable):
		if p in tracker_obj.timepoints:
			timemarker_obj = convproj_obj.timemarker__add()
			timemarker_obj.position = c
			timemarker_obj.visual.name = str(p)
		c += x

	return True