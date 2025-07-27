# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import placements
from objects import notelist_splitter

def process(convproj_obj, in__track_nopl, out__track_nopl, out_type, dawvert_intent):

	if in__track_nopl == False and out__track_nopl == True:

		if convproj_obj.type in ['r']: 
			for cvpj_trackid, track_obj in convproj_obj.track__iter():
				for notespl_obj in track_obj.placements.pl_notes:
					track_obj.placements.notelist.merge(notespl_obj.notelist, notespl_obj.time.get_pos())

				track_obj.placements.pl_notes.clear()
			convproj_obj.calc_pl_tempo()
			return True

		elif convproj_obj.type in ['cs', 'cm']: 
			for cvpj_trackid, track_obj in convproj_obj.track__iter():
				track_obj.placements.midievents.change_ppq(convproj_obj.time_ppq)

				for midipl_obj in track_obj.placements.pl_midi:

					scale = convproj_obj.time_ppq/midipl_obj.midievents.ppq

					pos = int(midipl_obj.time.get_pos())
					dur = int(midipl_obj.time.get_dur())

					track_obj.placements.midievents.merge(midipl_obj.midievents, pos, dur, 0)
					midipl_obj.midievents.change_ppq(convproj_obj.time_ppq)

				track_obj.placements.pl_notes.clear()
				track_obj.placements.pl_midi.clear()

			convproj_obj.calc_pl_tempo()
			return True

	return False
	