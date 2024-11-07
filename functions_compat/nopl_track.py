# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import placements
from objects import notelist_splitter

def process(convproj_obj, in__track_nopl, out__track_nopl, out_type):

	if in__track_nopl == True and out__track_nopl == False:

		if convproj_obj.type in (['r'] if 'r' in out_type else ['r', 'rm']): 
			timesigblocks_obj = notelist_splitter.timesigblocks()
			timesigblocks_obj.create_points_cut(convproj_obj)

			if 'do_singlenotelistcut' in convproj_obj.do_actions:
				npsplit = notelist_splitter.cvpj_notelist_splitter(timesigblocks_obj, convproj_obj.time_ppq, 1)
				for cvpj_trackid, track_obj in convproj_obj.track__iter(): 
					npsplit.add_nl(track_obj.placements)
				npsplit.process()
			else:
				for cvpj_trackid, track_obj in convproj_obj.track__iter(): 
					placement_obj = track_obj.placements.add_notes()
					placement_obj.notelist = track_obj.placements.notelist.__copy__()
					placement_obj.time.duration = track_obj.placements.notelist.get_dur()
					track_obj.placements.notelist.clear()
				return True
		else: return False

	elif in__track_nopl == False and out__track_nopl == True:
		if convproj_obj.type in ['r']: 
			for cvpj_trackid, track_obj in convproj_obj.track__iter():
				notes = []
				for notespl_obj in track_obj.placements.pl_notes:
					track_obj.placements.notelist.merge(notespl_obj.notelist, notespl_obj.time.position)

				track_obj.placements.pl_notes.clear()

			return True

	else: return False
	