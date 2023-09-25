# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

def fromindex2notelist(placement, notelistindex):
    fromindex = placement['fromindex']
    if fromindex in notelistindex:
        nle_data = notelistindex[fromindex]
        placement['notelist'] = nle_data['notelist']
        if 'name' in nle_data: placement['name'] = nle_data['name']
        if 'color' in nle_data: placement['color'] = nle_data['color']
        del placement['fromindex']
    else:
        placement['notelist'] = []

def convert(song):
    print('[song-convert] Converting from RegularIndexed > Regular')
    cvpj_proj = json.loads(song)
    t_s_trackdata = cvpj_proj['track_data']
    t_s_trackplacements = cvpj_proj['track_placements']

    for trackid in t_s_trackdata:
        singletrack_data = t_s_trackdata[trackid]
        notelistindex = singletrack_data['notelistindex'] if 'notelistindex' in singletrack_data else {}
        if trackid in t_s_trackplacements:
            trkpldata = t_s_trackplacements[trackid]

            singletrack_laned = trkpldata['laned'] if 'laned' in trkpldata else 0

            if singletrack_laned == 0: 
                placements = trkpldata['notes']
                for s_pl in placements:
                    fromindex2notelist(s_pl, notelistindex)
            else:
                t_laneorder = trkpldata['laneorder']
                t_lanedata = trkpldata['lanedata']
                for laneid in t_laneorder:
                    placements = trkpldata['lanedata'][laneid]['notes']
                    for s_pl in placements:
                        fromindex2notelist(s_pl, notelistindex)

        if 'notelistindex' in singletrack_data: del singletrack_data['notelistindex']

    return json.dumps(cvpj_proj)
