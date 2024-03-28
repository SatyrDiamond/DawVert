# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_compat import timesigblocks
from functions_compat import split_single_notelist
from objects_convproj import placements
from objects import notelist_splitter
from objects import findrepeats

def process(convproj_obj, in__track_nopl, out__track_nopl):

    if in__track_nopl == True and out__track_nopl == False:
        if convproj_obj.type in ['r']: 
            splitpoints, splitts, timesigposs = timesigblocks.create_points_cut(convproj_obj, 0)

            if 'do_singlenotelistcut' in convproj_obj.do_actions:

                npsplit = notelist_splitter.cvpj_notelist_splitter(splitpoints, splitts, convproj_obj.time_ppq, 0)

                for cvpj_trackid, track_obj in convproj_obj.iter_track():
                    npsplit.add_nl(track_obj.placements)

                npsplit.process()

                return True
        else: return False

    elif in__track_nopl == False and out__track_nopl == True:
        if convproj_obj.type in ['r']: 
            for cvpj_trackid, track_obj in convproj_obj.iter_track():
                notes = []
                for notespl_obj in track_obj.placements.pl_notes:
                    for n in notespl_obj.notelist.nl:
                        n[0] += notespl_obj.position
                        track_obj.placements.notelist.nl += [n]

                track_obj.placements.pl_notes.clear()

            return True

    else: return False
    