# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in__midi_notes, out__midi_notes, out_type, dawvert_intent):

	if convproj_obj.type == 'r': 

		if in__midi_notes == True and out__midi_notes == False and out_type not in ['cm', 'cs']:
			for cvpj_trackid, track_obj in convproj_obj.track__iter(): 
				for midpl in track_obj.placements.pl_midi:
					midievents_obj = midpl.midievents
					midievents_obj.add_note_durs()
					notes_pl = track_obj.placements.pl_notes.make_base_from_midi(midpl)
					notelist_obj = notes_pl.notelist
					notelist_obj.time_ppq = midievents_obj.ppq
					for x in midievents_obj.iter_events():
						etype = x[1]
						if etype == 'NOTE_DUR':
							channel = int(x[2])
							ext = {'channel': channel} if channel else None
							notelist_obj.add_r(int(x[0]), int(x[5]), int(x[3])-60, int(x[4])/127, ext)
					notelist_obj.change_timings(midpl.time_ppq)
					notelist_obj.mod_transpose(midpl.pitch)
				track_obj.placements.pl_midi.data = []

			return True

		elif in__midi_notes == False and out__midi_notes == True and out_type not in ['rm']:
			for cvpj_trackid, track_obj in convproj_obj.track__iter(): 

				pll = [track_obj.placements]+[x[1].placements for x in track_obj.lanes.items()]

				for tpl in pll:
					for notespl_obj in tpl.pl_notes:
						notespl_obj.notelist.mod_limit(-60, 67)
						notespl_obj.notelist.change_timings(960)
						midi_pl = tpl.pl_midi.make_base_from_notes(notespl_obj)
						midievents_obj = midi_pl.midievents
						midievents_obj.ppq = 960
						for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_autopack in notespl_obj.notelist.iter():
							for t_key in t_keys:
								if t_extra is not None:
									channel = t_extra['channel'] if 'channel' in t_extra else 0
								else:
									channel = 0
								midievents_obj.add_note_dur(t_pos, channel, t_key+60, min(127, t_vol*127), t_dur)
						midievents_obj.has_duration = True
						midievents_obj.del_note_durs()
					tpl.pl_notes.data = []
			return True

		else: 
			return False

	else: return False
	