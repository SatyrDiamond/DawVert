# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

# [a]
#  /\
#   ⎸
#  \/
# [r] <--> [m] <--> [mi]
#  /\                /\
#   ⎸                 ⎸
#   ⎸                /
# [ri]--------------/

import json

def overlap(start1, end1, start2, end2):
    return max(max((end2-start1), 0) - max((end2-end1), 0) - max((start2-start1), 0), 0)

# ---------------------------------- Regular to Any ----------------------------------

def a2r(song):
    cvpj_proj = json.loads(song)

    cvpj_proj['fxrack'] = {}
    cvpj_trackdata = cvpj_proj['trackdata']
    cvpj_trackordering = cvpj_proj['trackordering']
    cvpj_track_fx = cvpj_proj['track_fx']

    cvpj_proj['fxrack']['0'] = cvpj_proj['track_master']
    del cvpj_proj['track_master']

    print(len(cvpj_trackordering))

    fxracknum = 1

    for trackid in cvpj_trackordering:
        cvpj_proj['fxrack'][str(fxracknum)] = {}
        s_fx = cvpj_proj['fxrack'][str(fxracknum)]
        if trackid in cvpj_trackdata:
            s_trk = cvpj_trackdata[trackid]
            if 'name' in s_trk: s_fx['name'] = s_trk['name']
            if 'sends_audio' in s_trk:
                print(s_trk['sends_audio'])
            if 'color' in s_trk: 
                s_fx['color'] = s_trk['color']
            if 'fxchain' in s_trk: 
                s_fx['fxchain'] = s_trk['fxchain']
                del s_trk['fxchain']
            if 'pan' in s_trk: 
                s_fx['pan'] = s_trk['pan']
                del s_trk['pan']
            if 'vol' in s_trk: 
                s_fx['vol'] = s_trk['vol']
                del s_trk['vol']
        fxracknum += 1

    return json.dumps(cvpj_proj)

def r2a(song):
    print('[song-convert] Converting from Regular > Any')
    cvpj_proj = json.loads(song)
    cvpj_proj['track_master'] = {}
    cvpj_proj['track_fx'] = {}
    cvpj_mastertrack = cvpj_proj['track_master']
    cvpj_fxtrack = cvpj_proj['track_fx']
    if 'mastervol' in cvpj_proj:
        cvpj_mastertrack['vol'] = cvpj_proj['mastervol']
        del cvpj_proj['mastervol']
    else:
        cvpj_mastertrack['vol'] = 1.0
    if 'fxrack' in cvpj_proj:
        cvpj_fxrack = cvpj_proj['fxrack']
        cvpj_trackdata = cvpj_proj['trackdata']
        cvpj_trackordering = cvpj_proj['trackordering']

        if '0' in cvpj_fxrack:
            masterfx = cvpj_fxrack['0']
            if 'name' in masterfx: cvpj_mastertrack['name'] = masterfx['name']
            if 'muted' in masterfx: cvpj_mastertrack['muted'] = masterfx['muted']
            if 'vol' in masterfx: cvpj_mastertrack['vol'] = masterfx['vol'] * cvpj_mastertrack['vol']
            if 'fxenabled' in masterfx: cvpj_mastertrack['fxenabled'] = masterfx['fxenabled']
            if 'color' in masterfx: cvpj_mastertrack['color'] = masterfx['color']
            if 'fxchain' in masterfx: cvpj_mastertrack['fxchain'] = masterfx['fxchain']
        track_fxslot = {}

        for s_track in cvpj_trackdata:
            sd_track = cvpj_trackdata[s_track]
            if 'fxrack_channel' in sd_track:
                fxrack_channel = sd_track['fxrack_channel']
                if fxrack_channel not in track_fxslot:
                    track_fxslot[fxrack_channel] = []
                track_fxslot[fxrack_channel].append(s_track)
                del sd_track['fxrack_channel']


        fxtrknum = 1
        for fxnum in track_fxslot:
            trkfxdata = track_fxslot[fxnum]
            if fxnum != 0:

                if len(trkfxdata) == 1:
                    trackid = trkfxdata[0]
                    print('[song-convert] r2a: FX '+str(fxnum)+' effects moved to '+trackid)
                    if str(fxnum) in cvpj_fxrack:
                        if trackid in cvpj_trackdata:
                            fxi_data = cvpj_fxrack[str(fxnum)]
                            track_data = cvpj_trackdata[trackid]
                            track_data['audio_tomaster'] = 1
                            track_data['audio_fx_sends'] = []
                            if 'fxchain' not in track_data: track_data['fxchain'] = []
                            fxc_fx = fxi_data['fxchain']
                            fxc_track = track_data['fxchain']
                            for slot in fxc_fx:
                                fxc_track.append(slot)

        del cvpj_proj['fxrack']

    return json.dumps(cvpj_proj)

# ---------------------------------- Regular to Multiple ----------------------------------

def r2m_pl_addinst(placements, trackid):
    t_placements = placements.copy()
    for placement in placements:
        placement['type'] = 'instruments'
        if 'notelist' in placement:
            for t_note in placement['notelist']:
                t_note['instrument'] = trackid
    return placements

def r2m_makeplaylistrow(cvpjJ, plnum, trackid, placements, m_name, m_color, l_name, l_color):
    cvpjJ['playlist'][str(plnum)] = {}
    playlistrow = cvpjJ['playlist'][str(plnum)]
    playlistrow['placements'] = r2m_pl_addinst(placements, trackid)
    if m_name != None and l_name == None: playlistrow['name'] = m_name
    elif m_name != None and l_name != None: playlistrow['name'] = m_name+' ['+l_name+']'
    if m_color != None: playlistrow['color'] = m_color
    elif l_color != None: playlistrow['color'] = l_color

def r2m(song):
    print('[song-convert] Converting from Regular > Multiple')
    cvpj_proj = json.loads(song)
    if 'trackordering' not in cvpj_proj:
        print('[error] trackordering not found')

    t_s_trackordering = cvpj_proj['trackordering']
    t_s_trackdata = cvpj_proj['trackdata']
    del cvpj_proj['trackdata']
    del cvpj_proj['trackordering']

    cvpj_proj['instruments'] = {}
    cvpj_proj['instrumentsorder'] = []
    cvpj_proj['playlist'] = {}

    plnum = 1
    for trackid in t_s_trackordering:
        if trackid in t_s_trackdata:
            singletrack_data = t_s_trackdata[trackid]
            m_name = None
            m_color = None
            if 'name' in singletrack_data: m_name = singletrack_data['name']
            if 'color' in singletrack_data: m_color = singletrack_data['color']
  
            if singletrack_data['type'] == 'instrument':
                singletrack_laned = 0
                cvpj_proj['instrumentsorder'].append(trackid)
                cvpj_proj['instruments'][trackid] = singletrack_data

                if 'laned' in singletrack_data: 
                    if singletrack_data['laned'] == 1: 
                        singletrack_laned = 1

                if singletrack_laned == 0: 
                    print('[song-convert] r2m: inst non-laned:', trackid)
                    singletrack_pl = singletrack_data['placements']
                    del singletrack_data['placements']
                    r2m_makeplaylistrow(cvpj_proj, plnum, trackid, singletrack_pl, m_name, m_color, None, None)
                else:
                    print('[song-convert] r2m: inst laned:', trackid)
                    t_laneordering = singletrack_data['laneordering']
                    t_lanedata = singletrack_data['lanedata']
                    for laneid in t_laneordering:
                        lane_data = t_lanedata[laneid]
                        l_name = None
                        l_color = None
                        if 'name' in lane_data: l_name = lane_data['name']
                        if 'color' in lane_data: l_color = lane_data['color']
                        if 'placements' in lane_data:
                            r2m_makeplaylistrow(cvpj_proj, plnum, trackid, lane_data['placements'], m_name, m_color, l_name, l_color)
                            plnum += 1
                if singletrack_laned == 0: plnum += 1
    return json.dumps(cvpj_proj)

# ---------------------------------- Multiple to Regular ----------------------------------

def m2r_split_insts(placement):
    del placement['type']
    out_inst_pl = {}
    if 'notelist' in placement:
        pl_nl = placement['notelist']
        del placement['notelist']
        pl_base = placement
        splitted_instnotes = {}
        for note in pl_nl:
            note_inst = note['instrument']
            del note['instrument']
            if note_inst not in splitted_instnotes:
                splitted_instnotes[note_inst] = []
            splitted_instnotes[note_inst].append(note)
        for inst in splitted_instnotes:
            out_pl = {}
            out_pl['notelist'] = splitted_instnotes[inst]
            if inst not in out_inst_pl: out_inst_pl[inst] = pl_base | out_pl
    return out_inst_pl

def m2r_addplacements(placements):
    for placement in placements:
        mpl_num = 0
        success = 0
        pla_s = placement['position']
        pla_e = pla_s + placement['duration']
        multiplacements = [[]]
        while success == 0:
            total_overlap = 0
            for e_pla in multiplacements[mpl_num]:
                e_pla_s = e_pla['position']
                e_pla_e = e_pla_s + e_pla['duration']
                total_overlap += overlap(e_pla_s, e_pla_e, pla_s, pla_e)
            if total_overlap == 0:
                multiplacements[mpl_num].append(placement)
                success = 1
                break
            else:
                multiplacements.append([])
                mpl_num += 1
    return multiplacements

def m2r(song):
    print('[song-convert] Converting from Multiple > Regular')
    cvpj_proj = json.loads(song)

    playlist = cvpj_proj['playlist']
    cvpjm_instruments = cvpj_proj['instruments']
    cvpjm_instrumentsorder = cvpj_proj['instrumentsorder']

    del cvpj_proj['playlist']
    del cvpj_proj['instruments']
    del cvpj_proj['instrumentsorder']

    cvpj_trackdata = {}
    cvpj_trackorder = []

    for instrument in cvpjm_instrumentsorder:
        if instrument in cvpjm_instruments:
            trackdata = cvpjm_instruments[instrument]
            cvpj_trackdata[instrument] = trackdata
            trackdata['type'] = 'instrument'
            cvpj_trackdata[instrument]['laned'] = 1
            cvpj_trackdata[instrument]['lanedata'] = {}
            cvpj_trackdata[instrument]['laneordering'] = []
            
            cvpj_trackorder.append(instrument)

    for playlistentry in playlist:
        plrow = playlist[playlistentry]
        if 'placements' in plrow:
            placements = plrow['placements']
            if 'name' in playlist[playlistentry]:
                print('[song-convert] m2r: Track ' + playlistentry+' ['+playlist[playlistentry]['name']+']')
            else: print('[song-convert] m2r: Track ' + playlistentry)
            for placement in placements:
                if placement['type'] == 'instruments':
                    splitted_insts = m2r_split_insts(placement)
                    for instrument in splitted_insts:
                        if instrument in cvpj_trackdata:
                            lanedata = cvpj_trackdata[instrument]['lanedata']
                            if playlistentry not in lanedata:
                                lanedata[playlistentry] = {}
                                if 'name' in playlist[playlistentry]:
                                    lanedata[playlistentry]['name'] = playlist[playlistentry]['name']
                                if 'color' in playlist[playlistentry]:
                                    lanedata[playlistentry]['color'] = playlist[playlistentry]['color']
                                cvpj_trackdata[instrument]['laneordering'].append(playlistentry)
                                lanedata[playlistentry]['placements'] = []
                            cvpj_trackdata[instrument]['lanedata'][playlistentry]['placements'].append(splitted_insts[instrument])

    cvpj_proj['trackdata'] = cvpj_trackdata
    cvpj_proj['trackordering'] = cvpj_trackorder

    return json.dumps(cvpj_proj)

# ---------------------------------- Multiple to MultipleIndexed ----------------------------------

def m2mi_checkdup(cvpj_notelistindex, nledata):
    for pattern in cvpj_notelistindex:
        patterndat = cvpj_notelistindex[pattern]
        if patterndat == nledata:
            return pattern
    else:
        return None

def m2mi(song):
    print('[song-convert] Converting from Multiple > MultipleIndexed')
    global cvpj_proj
    cvpj_proj = json.loads(song)
    cvpj_playlist = cvpj_proj['playlist']
    cvpj_notelistindex = {}
    pattern_number = 1
    for cvpj_playlistentry in cvpj_playlist:
        cvpj_playlistentry_data = cvpj_playlist[cvpj_playlistentry]
        if 'placements' not in cvpj_playlistentry_data:
            cvpj_placements = []
        else:
            cvpj_placements = cvpj_playlistentry_data['placements']
        for cvpj_placement in cvpj_placements:
            if cvpj_placement['type'] == 'instruments':
                cvpj_notelist = cvpj_placement['notelist']
                temp_nle = {}
                temp_nle['notelist'] = cvpj_notelist.copy()
                checksamenl = m2mi_checkdup(cvpj_notelistindex, temp_nle)
                if checksamenl != None:
                    cvpj_placement['fromindex'] = checksamenl
                else:
                    cvpj_notelistindex['m2mi_' + str(pattern_number)] = temp_nle
                    cvpj_placement['fromindex'] = 'm2mi_' + str(pattern_number)
                    del cvpj_placement['notelist']
                pattern_number += 1
    cvpj_proj['notelistindex'] = cvpj_notelistindex
    return json.dumps(cvpj_proj)

# ---------------------------------- MultipleIndexed to Multiple ----------------------------------

def mi2m(song):
    print('[song-convert] Converting from MultipleIndexed > Multiple')
    cvpj_proj = json.loads(song)
    t_s_notelistindex = cvpj_proj['notelistindex']
    t_s_playlist = cvpj_proj['playlist']
    for pl_row in t_s_playlist:
        pl_row_data = t_s_playlist[pl_row]
        if 'placements' in pl_row_data:
            pl_row_placements = pl_row_data['placements']
            for pldata in pl_row_placements:
                if 'type' in pldata:
                    if pldata['type'] == 'instruments' and 'fromindex' in pldata:
                        fromindex = pldata['fromindex']
                        if fromindex in t_s_notelistindex:
                            index_pl_data = t_s_notelistindex[fromindex]
                            del pldata['fromindex']
                            if 'notelist' in index_pl_data:
                                pldata['notelist'] = index_pl_data['notelist']
                                if 'name' in index_pl_data: pldata['name'] = index_pl_data['name']
                                if 'color' in index_pl_data: pldata['color'] = index_pl_data['color']
    del cvpj_proj['notelistindex']
    return json.dumps(cvpj_proj)
