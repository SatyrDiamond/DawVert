# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import numpy as np
import struct

logger_project = logging.getLogger('project')

def convert(convproj_obj):
	import objects.midi_modernize.midi_modernize as midi_modernize
	from objects.convproj import midievents

	logger_project.info('ProjType Convert: ClassicalMultiple > RegularMultiple')

	modernize_obj = midi_modernize.midi_modernize(convproj_obj.midi.num_channels)

	for trackid, track_obj in convproj_obj.track__iter():
		modernize_obj.memory__add_count(track_obj.placements.midievents)
		for pl_midi in track_obj.placements.pl_midi:
			modernize_obj.memory__add_count(pl_midi.midievents)

	modernize_obj.memory__alloc()
	modernize_obj.from_cvpj__add_tracks(convproj_obj)

	for n, trackid, track_obj in convproj_obj.track__iter_num():

		if track_obj.type == 'midi':
			logger_project.debug('cm2rm: Track '+trackid)
			modernize_obj.init_patchchan(track_obj.midi)

			midievents_obj = track_obj.placements.midievents
			midievents_obj.add_note_durs()
	
			modernize_obj.add_track_visual(n, track_obj.visual)

			portnum = midievents_obj.port
			usedchans = list(midievents_obj.get_channums())

			for pn, pl_midi in enumerate(track_obj.placements.pl_midi):
				for x in pl_midi.midievents.get_channums():
					if x not in usedchans: usedchans.append(x)
				startpos = pl_midi.time.get_pos()
				durpos = pl_midi.time.get_dur()
				offset = pl_midi.time.get_offset()

				modernize_obj.do_notes(convproj_obj, pl_midi.midievents, startpos, durpos, offset, pn+1, portnum, n)

			modernize_obj.visual_chan(n, portnum, usedchans)
			modernize_obj.do_notes(convproj_obj, midievents_obj, 0, -1, 0, 0, portnum, n)

	logger_project.debug('cm2rm: SysEX')
	modernize_obj.instchange_from_sysex()

	modernize_obj.sort()

	logger_project.debug('cm2rm: Instruments')
	modernize_obj.do_instruments()

	logger_project.debug('cm2rm: Controls and FX')
	modernize_obj.do_fx_ctrls(convproj_obj)

	logger_project.debug('cm2rm: Automation')
	modernize_obj.do_automation(convproj_obj)

	logger_project.debug('cm2rm: Pitch Automation')
	modernize_obj.do_pitch_automation(convproj_obj)

	logger_project.debug('cm2rm: Tempo')
	modernize_obj.do_tempo(convproj_obj)

	logger_project.debug('cm2rm: TimeSig')
	modernize_obj.do_timesig(convproj_obj)

	logger_project.debug('cm2rm: Instruments')
	modernize_obj.to_cvpj_inst_visual(convproj_obj)

	logger_project.debug('cm2rm: Out Tracks')
	modernize_obj.output_tracks(convproj_obj)

	if convproj_obj.transport.loop_start and not convproj_obj.transport.loop_end:
		convproj_obj.transport.loop_end = convproj_obj.get_dur()

	convproj_obj.type = 'rm'
