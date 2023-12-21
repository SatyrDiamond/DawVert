# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

def pl_addinst(placements, trackid):
    t_placements = placements.copy()
    for placement in placements:
        if 'notelist' in placement:
            for t_note in placement['notelist']:
                t_note['instrument'] = trackid
    return placements

def makeplaylistrow(cvpjJ, plnum, trackid, placements_notes, m_name, m_color, l_name, l_color):
    cvpjJ['playlist'][str(plnum)] = {}
    playlistrow = cvpjJ['playlist'][str(plnum)]
    playlistrow['placements_notes'] = pl_addinst(placements_notes, trackid)
    if m_name != None and l_name == None: playlistrow['name'] = m_name
    elif m_name != None and l_name != None: playlistrow['name'] = m_name+' ['+l_name+']'
    if m_color != None: playlistrow['color'] = m_color
    elif l_color != None: playlistrow['color'] = l_color

def makeplaylistrow_audio(cvpjJ, plnum, trackid, placements_audio, t_name, t_color):
    cvpjJ['playlist'][str(plnum)] = {}
    playlistrow = cvpjJ['playlist'][str(plnum)]
    playlistrow['placements_audio'] = placements_audio
    if t_name != None: playlistrow['name'] = t_name
    if t_color != None: playlistrow['color'] = t_color

def convert(song):
    print('[song-convert] Converting from Regular > Multiple')
    cvpj_proj = json.loads(song)
    if 'track_order' not in cvpj_proj:
        print('[error] track_order not found')

    if 'track_order' in cvpj_proj:
        t_s_track_order = cvpj_proj['track_order']
        del cvpj_proj['track_order']
    else:
        t_s_track_order = []

    if 'track_data' in cvpj_proj:
        t_s_trackdata = cvpj_proj['track_data']
        del cvpj_proj['track_data']
    else:
        t_s_trackdata = {}

    if 'track_placements' in cvpj_proj:
        t_s_trackplacements = cvpj_proj['track_placements']
        del cvpj_proj['track_placements']
    else:
        t_s_trackplacements = {}

    cvpj_proj['instruments_data'] = {}
    cvpj_proj['instruments_order'] = []
    cvpj_proj['playlist'] = {}

    plnum = 1
    for trackid in t_s_track_order:
        if trackid in t_s_trackdata:
            singletrack_data = t_s_trackdata[trackid]

            m_name = singletrack_data['name'] if 'name' in singletrack_data else None
            m_color = singletrack_data['color'] if 'color' in singletrack_data else None
  
            ishybrid = True if singletrack_data['type'] == 'hybrid' else False
            singletrack_laned = 0

            if singletrack_data['type'] == 'instrument':
                cvpj_proj['instruments_order'].append(trackid)
                cvpj_proj['instruments_data'][trackid] = singletrack_data

            if singletrack_data['type'] == 'instrument':
                if trackid in t_s_trackplacements:
                    pltrack = t_s_trackplacements[trackid]

                    singletrack_laned = pldata['laned'] if 'laned' in pltrack else 0

                    if singletrack_laned == 0: 
                        print('[song-convert] r2m: inst non-laned:', trackid)
                        singletrack_pl = pltrack['notes'] if 'notes' in pltrack else []
                        makeplaylistrow(cvpj_proj, plnum, trackid, singletrack_pl, m_name, m_color, None, None)
                    else:
                        print('[song-convert] r2m: inst laned:', trackid)
                        t_laneorder = pltrack['laneorder']
                        t_lanedata = pltrack['lanedata']
                        for laneid in t_laneorder:
                            lane_data = t_lanedata[laneid]
                            l_name = lane_data['name'] if 'name' in lane_data else None
                            l_color = lane_data['color'] if 'color' in lane_data else None
                            if 'notes' in lane_data:
                                makeplaylistrow(cvpj_proj, plnum, trackid, lane_data['notes'], m_name, m_color, l_name, l_color)
                                plnum += 1
                    if singletrack_laned == 0 and ishybrid == False: plnum += 1

            if singletrack_data['type'] == 'audio':
                if trackid in t_s_trackplacements:
                    pltrack = t_s_trackplacements[trackid]
                    print('[song-convert] r2m: audio non-laned:', trackid)
                    singletrack_pl = pltrack['audio'] if 'audio' in pltrack else []
                    makeplaylistrow_audio(cvpj_proj, plnum, trackid, singletrack_pl, m_name, m_color)
                    plnum += 1

    return json.dumps(cvpj_proj)
