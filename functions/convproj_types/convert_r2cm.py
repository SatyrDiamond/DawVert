# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import copy
import logging

logger_project = logging.getLogger('project')

channelcount = -1
def get_unused_chan():
	global channelcount
	channelcount += 1
	if channelcount == 9: channelcount += 1
	if channelcount == 16: channelcount = 0
	return channelcount

def convert(convproj_obj):
	logger_project.info('ProjType Convert: Regular > ClassicalSingle')

	convproj_obj.change_timings(960)

	for trackid, track_obj in convproj_obj.track__iter():

		if track_obj.type == 'instrument':
			midievents_obj = track_obj.placements.midievents

			midievents_obj.has_duration = True

			if track_obj.midi.out_enabled:
				channel = track_obj.midi.out_chanport.chan
			else:
				channel = get_unused_chan()

			for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_autopack in track_obj.placements.notelist.iter():
				for t_key in t_keys:
					outnote = t_key+60
					if 127>outnote>=0:
						midievents_obj.add_note_dur(t_pos, channel, outnote, min(int(t_vol*127), 127), t_dur)
			track_obj.type = 'midi'

	convproj_obj.type = 'cm'