# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# [ri] --------------\ 
#  |                 |
#  |                 |
#  \/                \/
# [r] <--> [m] <--> [mi]

from functions import placements
import json

# --------------------------------------------------------------------

def trackfx2fxrack(cvpj_l, cvpjtype):
    if cvpj_l['use_fxrack'] == False:
        cvpj_l['fxrack'] = {}
        fxnum = 1
        if cvpjtype == 's':
            c_orderingdata = cvpj_l['track_order']
            c_trackdata = cvpj_l['track_data']
        if cvpjtype == 'm':
            c_orderingdata = cvpj_l['instruments_order']
            c_trackdata = cvpj_l['instruments_data']
        if 'track_master' in cvpj_l:
            cvpj_l['fxrack']['0'] = cvpj_l['track_master']

        for trackid in c_orderingdata:
            trackdata = c_trackdata[trackid]
            trackdata['fxrack_channel'] = fxnum
            fxtrack = {}
            fxtrack['name'] = trackdata['name']
            if 'color' in trackdata: fxtrack['color'] = trackdata['color']
            if 'fxchain_audio' in trackdata: 
                fxtrack['fxchain_audio'] = trackdata['fxchain_audio']
                del trackdata['fxchain_audio']
            cvpj_l['fxrack'][str(fxnum)] = fxtrack
            fxnum += 1

def instrack2singleinst(cvpj_l, cvpjtype):
    if cvpj_l['use_instrack'] == True:
        fxnum = 1
        if cvpjtype == 's':
            c_orderingdata = cvpj_l['track_order']
            c_trackdata = cvpj_l['track_data']
        if cvpjtype == 'm':
            c_orderingdata = cvpj_l['instruments_order']
            c_trackdata = cvpj_l['instruments_data']

        for trackid in c_trackdata:
            chain_inst = c_trackdata[trackid]['chain_inst']
            c_trackdata[trackid]["instdata"] = {}
            if len(chain_inst) == 0:
                c_trackdata[trackid]["instdata"]["plugin"] = "none"
                c_trackdata[trackid]["instdata"]["plugindata"] = {}
            elif len(chain_inst) == 1:
                c_trackdata[trackid]["instdata"] = chain_inst[0]
                if 'vol' in chain_inst[0]: 
                    if 'vol' in c_trackdata[trackid]:
                        c_trackdata[trackid]['vol'] = c_trackdata[trackid]['vol'] * chain_inst[0]['vol']
                    else:
                        c_trackdata[trackid]['vol'] = chain_inst[0]['vol']
            else:
                c_trackdata[trackid]["instdata"]["plugin"] = "none"
                c_trackdata[trackid]["instdata"]["plugindata"] = {}
        cvpj_l['use_instrack'] == False

# ---------------------------------- Regular to Multiple ----------------------------------

def r2m_pl_addinst(placements, trackid):
    t_placements = placements.copy()
    for placement in placements:
        if 'notelist' in placement:
            for t_note in placement['notelist']:
                t_note['instrument'] = trackid
    return placements

def r2m_makeplaylistrow(cvpjJ, plnum, trackid, placements_notes, m_name, m_color, l_name, l_color):
    cvpjJ['playlist'][str(plnum)] = {}
    playlistrow = cvpjJ['playlist'][str(plnum)]
    playlistrow['placements_notes'] = r2m_pl_addinst(placements_notes, trackid)
    if m_name != None and l_name == None: playlistrow['name'] = m_name
    elif m_name != None and l_name != None: playlistrow['name'] = m_name+' ['+l_name+']'
    if m_color != None: playlistrow['color'] = m_color
    elif l_color != None: playlistrow['color'] = l_color

def r2m(song):
    print('[song-convert] Converting from Regular > Multiple')
    cvpj_proj = json.loads(song)
    if 'track_order' not in cvpj_proj:
        print('[error] track_order not found')

    placements.r_split_single_notelist(cvpj_proj)

    t_s_track_order = cvpj_proj['track_order']
    t_s_trackdata = cvpj_proj['track_data']
    t_s_trackplacements = cvpj_proj['track_placements']
    del cvpj_proj['track_data']
    del cvpj_proj['track_order']
    del cvpj_proj['track_placements']

    cvpj_proj['instruments_data'] = {}
    cvpj_proj['instruments_order'] = []
    cvpj_proj['playlist'] = {}

    plnum = 1
    for trackid in t_s_track_order:
        if trackid in t_s_trackdata:
            singletrack_data = t_s_trackdata[trackid]
            m_name = None
            m_color = None
            if 'name' in singletrack_data: m_name = singletrack_data['name']
            if 'color' in singletrack_data: m_color = singletrack_data['color']
  
            singletrack_laned = 0

            if singletrack_data['type'] == 'instrument':
                cvpj_proj['instruments_order'].append(trackid)
                cvpj_proj['instruments_data'][trackid] = singletrack_data

            if singletrack_data['type'] == 'instrument':
                if trackid in t_s_trackplacements:
                    pltrack = t_s_trackplacements[trackid]

                    if 'notes_laned' in pltrack: 
                        if pltrack['notes_laned'] == 1: 
                            singletrack_laned = 1

                    if singletrack_laned == 0: 
                        print('[song-convert] r2m: inst non-laned:', trackid)
                        singletrack_pl = pltrack['notes']
                        r2m_makeplaylistrow(cvpj_proj, plnum, trackid, singletrack_pl, m_name, m_color, None, None)
                    else:
                        print('[song-convert] r2m: inst laned:', trackid)
                        t_laneorder = pltrack['notes_laneorder']
                        t_lanedata = pltrack['notes_lanedata']
                        for laneid in t_laneorder:
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

# ---------------------------------- RegularIndexed to MultipleIndexed ----------------------------------

def ri2mi_index_nliid(singletrack_pl, trackid):
    for placement in singletrack_pl:
        placement['fromindex'] = trackid+'_'+placement['fromindex']

def ri2mi(song):
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

                    if 'notes_laned' in pldata: 
                        if pldata['notes_laned'] == 1: 
                            singletrack_laned = 1
    
                    if singletrack_laned == 0: 
                        print('[song-convert] ri2mi: inst non-laned:', trackid)
                        singletrack_pl = pldata['notes']
                        ri2mi_index_nliid(singletrack_pl, trackid)
                        r2m_makeplaylistrow(cvpj_proj, plnum, trackid, singletrack_pl, m_name, m_color, None, None)
                    else:
                        print('[song-convert] ri2mi: inst laned:', trackid)
                        t_laneorder = pldata['notes_laneorder']
                        t_lanedata = pldata['notes_lanedata']
                        for laneid in t_laneorder:
                            lane_data = t_lanedata[laneid]
                            l_name = None
                            l_color = None
                            if 'name' in lane_data: l_name = lane_data['name']
                            if 'color' in lane_data: l_color = lane_data['color']
                            if 'placements' in lane_data:
                                ri2mi_index_nliid(lane_data['placements'], trackid)
                                r2m_makeplaylistrow(cvpj_proj, plnum, trackid, lane_data['placements'], m_name, m_color, l_name, l_color)
                                plnum += 1
                    if singletrack_laned == 0: plnum += 1

    return json.dumps(cvpj_proj)

# ---------------------------------- RegularIndexed to Regular ----------------------------------
def ri2r_fromindex2notelist(placement, notelistindex):
    fromindex = placement['fromindex']
    if fromindex in notelistindex:
        nle_data = notelistindex[fromindex]
        placement['notelist'] = nle_data['notelist']
        if 'name' in nle_data: placement['name'] = nle_data['name']
        if 'color' in nle_data: placement['color'] = nle_data['color']
        del placement['fromindex']
    else:
        placement['notelist'] = []

def ri2r(song):
    print('[song-convert] Converting from RegularIndexed > MultipleIndexed')
    cvpj_proj = json.loads(song)
    if 'track_order' not in cvpj_proj: print('[error] track_order not found')
    t_s_track_order = cvpj_proj['track_order']
    t_s_trackdata = cvpj_proj['track_data']
    t_s_trackplacements = cvpj_proj['track_placements']

    for trackid in t_s_track_order:
        if trackid in t_s_trackdata:
            singletrack_data = t_s_trackdata[trackid]
            notelistindex = singletrack_data['notelistindex']
            if trackid in t_s_trackplacements:
                trkpldata = t_s_trackplacements[trackid]
                if 'notes_laned' in trkpldata: 
                    if trkpldata['notes_laned'] == 1: 
                        singletrack_laned = 1
    
                if singletrack_laned == 0: 
                    placements = trkpldata['notes']
                    for s_pl in placements:
                        ri2r_fromindex2notelist(s_pl, notelistindex)
                else:
                    t_laneorder = trkpldata['notes_laneorder']
                    t_lanedata = trkpldata['notes_lanedata']
                    for laneid in t_laneorder:
                        placements = trkpldata['notes_lanedata'][laneid]['placements']
                        for s_pl in placements:
                            ri2r_fromindex2notelist(s_pl, notelistindex)

            del singletrack_data['notelistindex']

    return json.dumps(cvpj_proj)

# ---------------------------------- Multiple to Regular ----------------------------------

def m2r_split_insts(placement):
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
    cvpjm_instruments = cvpj_proj['instruments_data']
    cvpjm_instruments_order = cvpj_proj['instruments_order']

    del cvpj_proj['playlist']
    del cvpj_proj['instruments_data']
    del cvpj_proj['instruments_order']

    cvpj_trackdata = {}
    cvpj_trackorder = []
    cvpj_trackplacements = {}

    for instrument in cvpjm_instruments_order:
        if instrument in cvpjm_instruments:
            cvpj_trackplacements[instrument] = {}
            cvpj_trackplacements[instrument]['notes'] = {}
            trackdata = cvpjm_instruments[instrument]
            cvpj_trackdata[instrument] = trackdata
            trackdata['type'] = 'instrument'
            cvpj_trackplacements[instrument]['notes_laned'] = 1
            cvpj_trackplacements[instrument]['notes_lanedata'] = {}
            cvpj_trackplacements[instrument]['notes_laneorder'] = []
            
            cvpj_trackorder.append(instrument)

    for playlistentry in playlist:
        plrow = playlist[playlistentry]
        if 'placements_notes' in plrow:
            placements = plrow['placements_notes']
            if 'name' in playlist[playlistentry]:
                print('[song-convert] m2r: Track ' + playlistentry+' ['+playlist[playlistentry]['name']+']')
            else: print('[song-convert] m2r: Track ' + playlistentry)
            for placement in placements:
                splitted_insts = m2r_split_insts(placement)
                for instrument in splitted_insts:
                    if instrument in cvpj_trackdata:
                        lanedata = cvpj_trackplacements[instrument]['notes_lanedata']
                        if playlistentry not in lanedata:
                            lanedata[playlistentry] = {}
                            if 'name' in playlist[playlistentry]:
                                lanedata[playlistentry]['name'] = playlist[playlistentry]['name']
                            if 'color' in playlist[playlistentry]:
                                lanedata[playlistentry]['color'] = playlist[playlistentry]['color']
                            cvpj_trackplacements[instrument]['notes_laneorder'].append(playlistentry)
                            lanedata[playlistentry]['placements'] = []
                        cvpj_trackplacements[instrument]['notes_lanedata'][playlistentry]['placements'].append(splitted_insts[instrument])

    cvpj_proj['track_data'] = cvpj_trackdata
    cvpj_proj['track_order'] = cvpj_trackorder
    cvpj_proj['track_placements'] = cvpj_trackplacements

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
        if 'placements_notes' not in cvpj_playlistentry_data:
            cvpj_placements = []
        else:
            cvpj_placements = cvpj_playlistentry_data['placements_notes']
        for cvpj_placement in cvpj_placements:
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
        if 'placements_notes' in pl_row_data:
            pl_row_placements = pl_row_data['placements_notes']
            for pldata in pl_row_placements:
                if 'fromindex' in pldata:
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
