# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from functions_song import convert_r2m

def index_nliid(singletrack_pl, trackid):
    for placement in singletrack_pl:
        placement['fromindex'] = trackid+'_'+placement['fromindex']

def convert(song):
    print('[song-convert] Converting from RegularIndexed > MultipleIndexed')
    cvpj_proj = json.loads(song)
    if 'track_order' not in cvpj_proj: print('[error] track_order not found')

    t_s_track_order = cvpj_proj['track_order']
    t_s_trackdata = cvpj_proj['track_data']
    t_s_trackplacements = cvpj_proj['track_placements']
    del cvpj_proj['track_data']
    del cvpj_proj['track_order']
    del cvpj_proj['track_placements']

    cvpj_proj['instruments_data'] = {}
    cvpj_proj['instruments_order'] = []
    cvpj_proj['playlist'] = {}
    cvpj_proj['notelistindex'] = {}

    plnum = 1
    for trackid in t_s_track_order:
        if trackid in t_s_trackdata:
            singletrack_data = t_s_trackdata[trackid]
            m_name = None
            m_color = None
            if 'name' in singletrack_data: m_name = singletrack_data['name']
            if 'color' in singletrack_data: m_color = singletrack_data['color']
  
            if singletrack_data['type'] == 'instrument':
                singletrack_laned = 0
                cvpj_proj['instruments_order'].append(trackid)
                cvpj_proj['instruments_data'][trackid] = singletrack_data

                for nle_id in singletrack_data['notelistindex']:
                    nle_data = singletrack_data['notelistindex'][nle_id]
                    if 'name' not in nle_data: nle_data['name'] = nle_id

                    if 'notelist' in nle_data: 
                        for cvpj_note in nle_data['notelist']:
                            cvpj_note['instrument'] = trackid

                    if m_name != None: nle_data['name'] += ' ('+m_name+')' 
                    nle_data['name'] += ' ['+trackid+']'

                    cvpj_proj['notelistindex'][trackid+'_'+nle_id] = nle_data
                    if m_color != None: cvpj_proj['notelistindex'][trackid+'_'+nle_id]['color'] = m_color
                del singletrack_data['notelistindex']

                if trackid in t_s_trackplacements:
                    pldata = t_s_trackplacements[trackid]

                    singletrack_laned = pldata['laned'] if 'laned' in pldata else 0

                    if singletrack_laned == 0: 
                        print('[song-convert] ri2mi: inst non-laned:', trackid)
                        singletrack_pl = pldata['notes']
                        index_nliid(singletrack_pl, trackid)
                        convert_r2m.makeplaylistrow(cvpj_proj, plnum, trackid, singletrack_pl, m_name, m_color, None, None)
                    else:
                        print('[song-convert] ri2mi: inst laned:', trackid)
                        t_laneorder = pldata['laneorder']
                        t_lanedata = pldata['lanedata']
                        for laneid in t_laneorder:
                            lane_data = t_lanedata[laneid]
                            l_name = None
                            l_color = None
                            if 'name' in lane_data: l_name = lane_data['name']
                            if 'color' in lane_data: l_color = lane_data['color']
                            if 'notes' in lane_data:
                                index_nliid(lane_data['notes'], trackid)
                                convert_r2m.makeplaylistrow(cvpj_proj, plnum, trackid, lane_data['notes'], m_name, m_color, l_name, l_color)
                                plnum += 1
                    if singletrack_laned == 0: plnum += 1

    return json.dumps(cvpj_proj)
