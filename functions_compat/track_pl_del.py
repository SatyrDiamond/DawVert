# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import placements
from objects import notelist_splitter

def process(convproj_obj, in__track_nopl, out__track_nopl, out_type, dawvert_intent):

	if in__track_nopl == False and out__track_nopl == True:
		if convproj_obj.type in ['r']: 
			for cvpj_trackid, track_obj in convproj_obj.track__iter():
				notes = []
				for notespl_obj in track_obj.placements.pl_notes:
					track_obj.placements.notelist.merge(notespl_obj.notelist, notespl_obj.time.position)

				track_obj.placements.pl_notes.clear()
			return True

		elif convproj_obj.type in ['cs', 'cm']: 
			for cvpj_trackid, track_obj in convproj_obj.track__iter():
				notes = []
				for midipl_obj in track_obj.placements.pl_midi:
					track_obj.placements.midievents.merge(midipl_obj.midievents, midipl_obj.time.position, midipl_obj.time.duration, 0)

				track_obj.placements.pl_notes.clear()
			return True

		else: 
			return False

	else: return False
	