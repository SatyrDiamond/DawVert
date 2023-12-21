# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def tracklanename(trackname, lanename, fallback):
    if trackname != None:
        if lanename != None: ntp_name = trackname+' ['+lanename+']'
        if lanename == None: ntp_name = trackname
    if trackname == None:
        if lanename != None: ntp_name = 'none'+' ['+lanename+']'
        if lanename == None: ntp_name = 'none'
    return ntp_name

def process_r(cvpj_l):
    old_trackdata = cvpj_l['track_data'] if 'track_data' in cvpj_l else {}
    old_trackordering = cvpj_l['track_order'] if 'track_data' in cvpj_l else []
    old_trackplacements = cvpj_l['track_placements'] if 'track_data' in cvpj_l else {}
    new_trackdata = {}
    new_trackordering = []
    new_trackplacements = {}

    for trackid in old_trackordering:
        if trackid in old_trackdata:
            print('[compat] RemoveLanes: '+ trackid)
            if trackid in old_trackplacements:

                s_trackdata = old_trackdata[trackid]
                s_pldata = old_trackplacements[trackid]

                if 'name' in s_trackdata: s_trackname = s_trackdata['name']
                else: s_trackname = None
                if 'color' in s_trackdata: s_trackcolor = s_trackdata['color']
                else: s_trackcolor = None
                if 'params' in s_trackdata: s_trackparams = s_trackdata['params']
                else: s_trackparams = None

                not_laned = True

                if 'laned' in s_pldata:
                    if s_pldata['laned'] == 1:
                        not_laned = False

                        s_lanedata = s_pldata['lanedata']
                        s_laneordering = s_pldata['laneorder']

                        if len(s_laneordering) == 0:
                            new_trackdata[trackid] = s_trackdata
                            new_trackplacements[trackid] = {}
                            new_trackplacements[trackid]['notes'] = []
                            new_trackordering.append(trackid)

                        if len(s_laneordering) == 1:
                            new_trackdata[trackid] = s_trackdata
                            new_trackplacements[trackid] = {}
                            new_trackplacements[trackid]['notes'] = s_lanedata[s_laneordering[0]]['notes']

                            if 'color' in s_lanedata[s_laneordering[0]]:
                                s_trackcolor = s_lanedata[s_laneordering[0]]['color']

                            new_trackordering.append(trackid)

                        if len(s_laneordering) > 1:
                            for laneid in s_laneordering:

                                splitnameid = trackid+'_Lane'+laneid

                                s_d_lanedata = s_lanedata[laneid]
                                if 'name' in s_d_lanedata: s_lanename = s_d_lanedata['name']
                                else: s_lanename = None

                                septrackname = tracklanename(s_trackname, s_lanename, 'noname')

                                new_trackdata[splitnameid] = s_trackdata.copy()
                                new_trackdata[splitnameid]['name'] = septrackname
                                if s_trackparams != None: new_trackdata[splitnameid]['params'] = s_trackparams
                                if s_trackcolor != None: new_trackdata[splitnameid]['color'] = s_trackcolor
                                new_trackplacements[splitnameid] = {}
                                new_trackplacements[splitnameid]['notes'] = s_lanedata[laneid]['notes']
                                new_trackordering.append(splitnameid)

                if not_laned == True:
                    new_trackdata[trackid] = s_trackdata
                    new_trackplacements[trackid] = s_pldata
                    new_trackordering.append(trackid)

    cvpj_l['track_data'] = new_trackdata
    cvpj_l['track_order'] = new_trackordering
    cvpj_l['track_placements'] = new_trackplacements
    return True

def process(cvpj_proj, cvpj_type, in__track_lanes, out__track_lanes):
    if in__track_lanes == True and out__track_lanes == False:
        if cvpj_type in ['r', 'ri', 'rm']: return process_r(cvpj_proj)
        else: return False
    else: return False