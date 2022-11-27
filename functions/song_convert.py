# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

def m2mi(song):
    global cvpj_proj
    cvpj_proj = json.loads(song)
    cvpj_playlist = cvpj_proj['playlist']
    cvpj_notelistindex = {}
    pattern_number = 1
    for cvpj_playlistentry in cvpj_playlist:
        cvpj_playlistentry_data = cvpj_playlist[cvpj_playlistentry]
        cvpj_placements = cvpj_playlistentry_data['placements']
        for cvpj_placement in cvpj_placements:
            if cvpj_placement['type'] == 'instruments':
                cvpj_notelist = cvpj_placement['notelist']
                cvpj_notelistindex['m2mi_' + str(pattern_number)] = {}
                cvpj_notelistindex['m2mi_' + str(pattern_number)]['notelist'] = cvpj_notelist.copy()
                cvpj_placement['fromindex'] = 'm2mi_' + str(pattern_number)
                del cvpj_placement['notelist']
                pattern_number += 1
    cvpj_proj['notelistindex'] = cvpj_notelistindex
    return json.dumps(cvpj_proj)
