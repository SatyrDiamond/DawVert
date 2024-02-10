# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_compat import timesigblocks
from functions_compat import split_single_notelist
from objects_convproj import notelist_splitted
from objects import convproj_placements
from objects import findrepeats

def process(convproj_obj, in__track_nopl, out__track_nopl):
    if in__track_nopl == True and out__track_nopl == False:
        if convproj_obj.type in ['r']: 
            splitpoints, timesigposs = timesigblocks.create_points_cut(convproj_obj)
            if 'do_singlenotelistcut' in convproj_obj.do_actions:
                for cvpj_trackid, track_obj in convproj_obj.iter_track():
                    nl_found = False
                    for notespl_obj in track_obj.placements.iter_notes():
                        notespl_obj.notelist.sort()
                        nls_obj = notelist_splitted.cvpj_notelist_splitted()
                        nls_obj.do_split(splitpoints, notespl_obj.notelist, 0)
                        nl_found = True
                    if nl_found: 
                        nls_obj.to_pl(track_obj.placements)
                        track_obj.placements.uses_placements = True
                return True
        else: return False

    elif in__track_nopl == False and out__track_nopl == True:
        if convproj_obj.type in ['r']: 
            for cvpj_trackid, track_obj in convproj_obj.iter_track():
                notes = []
                for notespl_obj in track_obj.placements.iter_notes():
                    for n in notespl_obj.notelist.nl:
                        n[0] += notespl_obj.position
                        notes.append(n)

                if notes:
                    notespl_obj = convproj_placements.cvpj_placement_notes(track_obj.time_ppq, track_obj.time_float)
                    notespl_obj.notelist.nl = notes
                    notespl_obj.duration = notespl_obj.notelist.get_dur()
                    track_obj.placements.data_notes = [notespl_obj]
                    
                track_obj.placements.uses_placements = False
            return True

    else: return False
    