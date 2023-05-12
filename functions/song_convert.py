# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# [ri] --------------\ 
#  |                 |
#  |                 |
#  \/                \/
# [r] <--> [m] <--> [mi]

from functions import placements
from functions import tracks
from functions import data_values
from functions import notelist_data
from functions import xtramath
import json

# --------------------------------------------------------------------

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

    t_s_track_order = cvpj_proj['track_order']
    t_s_trackdata = cvpj_proj['track_data']

    if 'track_placements' in cvpj_proj: 
        t_s_trackplacements = cvpj_proj['track_placements']
        del cvpj_proj['track_placements']
    else: t_s_trackplacements = {}

    del cvpj_proj['track_data']
    del cvpj_proj['track_order']

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

                    if 'laned' in pltrack: 
                        if pltrack['laned'] == 1: 
                            singletrack_laned = 1

                    if singletrack_laned == 0: 
                        print('[song-convert] r2m: inst non-laned:', trackid)
                        singletrack_pl = pltrack['notes']
                        r2m_makeplaylistrow(cvpj_proj, plnum, trackid, singletrack_pl, m_name, m_color, None, None)
                    else:
                        print('[song-convert] r2m: inst laned:', trackid)
                        t_laneorder = pltrack['laneorder']
                        t_lanedata = pltrack['lanedata']
                        for laneid in t_laneorder:
                            lane_data = t_lanedata[laneid]
                            l_name = None
                            l_color = None
                            if 'name' in lane_data: l_name = lane_data['name']
                            if 'color' in lane_data: l_color = lane_data['color']
                            if 'notes' in lane_data:
                                r2m_makeplaylistrow(cvpj_proj, plnum, trackid, lane_data['notes'], m_name, m_color, l_name, l_color)
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

                    if 'laned' in pldata: 
                        if pldata['laned'] == 1: 
                            singletrack_laned = 1
    
                    if singletrack_laned == 0: 
                        print('[song-convert] ri2mi: inst non-laned:', trackid)
                        singletrack_pl = pldata['notes']
                        ri2mi_index_nliid(singletrack_pl, trackid)
                        r2m_makeplaylistrow(cvpj_proj, plnum, trackid, singletrack_pl, m_name, m_color, None, None)
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
                                ri2mi_index_nliid(lane_data['notes'], trackid)
                                r2m_makeplaylistrow(cvpj_proj, plnum, trackid, lane_data['notes'], m_name, m_color, l_name, l_color)
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
    print('[song-convert] Converting from RegularIndexed > Regular')
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

                singletrack_laned = 0

                if 'laned' in trkpldata: 
                    if trkpldata['laned'] == 1: 
                        singletrack_laned = 1
    
                if singletrack_laned == 0: 
                    placements = trkpldata['notes']
                    for s_pl in placements:
                        ri2r_fromindex2notelist(s_pl, notelistindex)
                else:
                    t_laneorder = trkpldata['laneorder']
                    t_lanedata = trkpldata['lanedata']
                    for laneid in t_laneorder:
                        placements = trkpldata['lanedata'][laneid]['notes']
                        for s_pl in placements:
                            ri2r_fromindex2notelist(s_pl, notelistindex)

            del singletrack_data['notelistindex']

    return json.dumps(cvpj_proj)

# ---------------------------------- Multiple to Regular ----------------------------------

def lanefit_checkoverlap(new_placementdata, placements_table, num):
    not_overlapped = True
    p_pl_pos = new_placementdata['position']
    p_pl_dur = new_placementdata['duration']
    p_pl_end = p_pl_pos+p_pl_dur
    #print('----------------------------')
    for lanepl in placements_table[num]:
        e_pl_pos = lanepl['position']
        e_pl_dur = lanepl['duration']
        e_pl_end = e_pl_pos+e_pl_dur
        if bool(xtramath.overlap(p_pl_pos, p_pl_end, e_pl_pos, e_pl_end)) == True: not_overlapped = False
    return not_overlapped

def lanefit_addpl(new_placementdata, placements_table):
    lanenum = 0
    placement_placed = False
    while placement_placed == False:
        not_overlapped = lanefit_checkoverlap(new_placementdata, placements_table, lanenum)
        #print(lanenum, not_overlapped)
        if not_overlapped == True:
            placement_placed = True
            placements_table[lanenum].append(new_placementdata)
        if not_overlapped == False:
            placements_table.append([])
            lanenum += 1


def r_lanefit(projJ):
    if 'do_lanefit' in projJ:
        if projJ['do_lanefit'] == True:
            trackplacements = projJ['track_placements']
            for trackid in trackplacements:
                if 'laned' in trackplacements[trackid]:
                    if trackplacements[trackid]['laned'] == True:
                        old_lanedata = trackplacements[trackid]['lanedata']
                        old_laneordering = trackplacements[trackid]['laneorder']
                        print('[song-convert] LaneFit: '+ trackid+': '+str(len(old_laneordering))+' > ', end='')
                        new_lanedata = {}
                        new_laneordering = []

                        new_pltable = [[]]
                        for laneid in old_laneordering:
                            old_lanedata_data = old_lanedata[laneid]
                            old_lanedata_pl = old_lanedata_data['notes']
                            for old_lanedata_pl_s in old_lanedata_pl:
                                lanefit_addpl(old_lanedata_pl_s, new_pltable)

                        for plnum in range(len(new_pltable)):
                            if new_pltable[plnum] != []:
                                newlaneid = '_lanefit_'+str(plnum)
                                new_lanedata[newlaneid] = {}
                                new_lanedata[newlaneid]['notes'] = new_pltable[plnum]
                                new_laneordering.append(newlaneid)

                        print(str(len(new_laneordering)))
                        trackplacements[trackid]['lanedata'] = new_lanedata
                        trackplacements[trackid]['laneorder'] = new_laneordering


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
                total_overlap += xtramath.overlap(e_pla_s, e_pla_e, pla_s, pla_e)
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
            trackdata = cvpjm_instruments[instrument]
            cvpj_trackdata[instrument] = trackdata
            trackdata['type'] = 'instrument'
            cvpj_trackplacements[instrument]['laned'] = 1
            cvpj_trackplacements[instrument]['lanedata'] = {}
            cvpj_trackplacements[instrument]['laneorder'] = []
            
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
                        lanedata = cvpj_trackplacements[instrument]['lanedata']
                        if playlistentry not in lanedata:
                            lanedata[playlistentry] = {}
                            if 'name' in playlist[playlistentry]: lanedata[playlistentry]['name'] = playlist[playlistentry]['name']
                            if 'color' in playlist[playlistentry]: lanedata[playlistentry]['color'] = playlist[playlistentry]['color']
                            cvpj_trackplacements[instrument]['laneorder'].append(playlistentry)
                            lanedata[playlistentry]['notes'] = []
                        cvpj_trackplacements[instrument]['lanedata'][playlistentry]['notes'].append(splitted_insts[instrument])

        if 'placements_audio' in plrow:
            placements = plrow['placements_audio']
            fxrack_sep_placements = {}
            for placement in placements:
                fxrack = -1
                if 'fxrack_channel' in placement:
                    fxrack = placement['fxrack_channel']
                    del placement['fxrack_channel']
                    data_values.nested_dict_add_to_list(fxrack_sep_placements, [fxrack], placement)

            for fxrack_sep_placement in fxrack_sep_placements:
                cvpj_audiotrackid = 'm2r_audiotrack_'+str(playlistentry)+'_'+str(fxrack_sep_placement)
                cvpj_trackdata[cvpj_audiotrackid] = {}
                trackdata = cvpj_trackdata[cvpj_audiotrackid]
                trackdata['type'] = 'audio'
                cvpj_trackorder.insert(0, cvpj_audiotrackid)
                cvpj_trackplacements[cvpj_audiotrackid] = {}
                cvpj_trackplacements[cvpj_audiotrackid]['audio'] = []

                if 'name' in playlist[playlistentry]: trackdata['name'] = playlist[playlistentry]['name']
                if 'color' in playlist[playlistentry]: trackdata['color'] = playlist[playlistentry]['color']

                if fxrack_sep_placement != -1: trackdata['fxrack_channel'] = fxrack_sep_placement
                for placement in fxrack_sep_placements[fxrack_sep_placement]:
                    cvpj_trackplacements[cvpj_audiotrackid]['audio'].append(placement)
            



    cvpj_proj['track_data'] = cvpj_trackdata
    cvpj_proj['track_order'] = cvpj_trackorder
    cvpj_proj['track_placements'] = cvpj_trackplacements

    r_lanefit(cvpj_proj)
    
    return json.dumps(cvpj_proj)

# ---------------------------------- Multiple to MultipleIndexed ----------------------------------

def m2mi_checkdup(cvpj_notelistindex, nledata):
    for pattern in cvpj_notelistindex:
        patterndat = cvpj_notelistindex[pattern]
        if patterndat == nledata:
            return pattern
    else:
        return None

m2mi_sample_names = ['file', 'name', 'color', 'stretch', 'vol', 'pan', 'fxrack_channel']

def m2mi(song):
    print('[song-convert] Converting from Multiple > MultipleIndexed')
    global cvpj_proj
    cvpj_proj = json.loads(song)
    cvpj_playlist = cvpj_proj['playlist']

    pattern_number = 1
    cvpj_notelistindex = {}
    for cvpj_playlistentry in cvpj_playlist:
        cvpj_playlistentry_data = cvpj_playlist[cvpj_playlistentry]
        if 'placements_notes' not in cvpj_playlistentry_data: cvpj_placements_notes = []
        else: cvpj_placements_notes = cvpj_playlistentry_data['placements_notes']
        for cvpj_placement in cvpj_placements_notes:
            cvpj_notelist = cvpj_placement['notelist']
            temp_nle = {}
            temp_nle['notelist'] = cvpj_notelist.copy()
            checksamenl = m2mi_checkdup(cvpj_notelistindex, temp_nle)
            if checksamenl != None: cvpj_placement['fromindex'] = checksamenl
            else:
                cvpj_notelistindex['m2mi_' + str(pattern_number)] = temp_nle
                cvpj_placement['fromindex'] = 'm2mi_' + str(pattern_number)
                del cvpj_placement['notelist']
            pattern_number += 1
    cvpj_proj['notelistindex'] = cvpj_notelistindex

    sample_number = 1
    cvpj_sampleindex = {}
    existingsamples = []
    for cvpj_playlistentry in cvpj_playlist:
        cvpj_playlistentry_data = cvpj_playlist[cvpj_playlistentry]
        if 'placements_audio' not in cvpj_playlistentry_data: cvpj_placements_audio = []
        else: cvpj_placements_audio = cvpj_playlistentry_data['placements_audio']
        for cvpj_placement in cvpj_placements_audio:
            sampledata = [None, None, None, None, None, None, None, None]

            for num in range(7):
                if m2mi_sample_names[num] in cvpj_placement:
                    sampledata[num] = cvpj_placement[m2mi_sample_names[num]]
                    del cvpj_placement[m2mi_sample_names[num]]

            if sampledata not in existingsamples:
                existingsamples.append(sampledata)
            
            fromindexnum = existingsamples.index(sampledata)
            cvpj_placement['fromindex'] = 'm2mi_audio_' + str(fromindexnum+1)

    sample_number = 1
    for existingsample in existingsamples:

        cvpj_sampledata = {}
        for num in range(7):
            if existingsample[num] != None:
                cvpj_sampledata[m2mi_sample_names[num]] = existingsample[num]

        cvpj_sampleindex['m2mi_audio_' + str(sample_number)] = cvpj_sampledata
        sample_number += 1


    cvpj_proj['sampleindex'] = cvpj_sampleindex

            
    return json.dumps(cvpj_proj)

# ---------------------------------- MultipleIndexed to Multiple ----------------------------------

def mi2m(song, extra_json):
    print('[song-convert] Converting from MultipleIndexed > Multiple')
    cvpj_proj = json.loads(song)
    t_s_playlist = cvpj_proj['playlist']


    if 'notelistindex' in cvpj_proj:
        t_s_notelistindex = cvpj_proj['notelistindex']
        unused_notelistindex = list(t_s_notelistindex)
        for pl_row in t_s_playlist:
            pl_row_data = t_s_playlist[pl_row]
            if 'placements_notes' in pl_row_data:
                pl_row_placements = pl_row_data['placements_notes']
                for pldata in pl_row_placements:
                    if 'fromindex' in pldata:
                        fromindex = pldata['fromindex']
                        if fromindex in t_s_notelistindex:
                            index_pl_data = t_s_notelistindex[fromindex]
                            if fromindex in unused_notelistindex:
                                unused_notelistindex.remove(fromindex)
                            del pldata['fromindex']
                            if 'notelist' in index_pl_data:
                                pldata['notelist'] = index_pl_data['notelist']
                                if 'name' in index_pl_data: pldata['name'] = index_pl_data['name']
                                if 'color' in index_pl_data: pldata['color'] = index_pl_data['color']

        del cvpj_proj['notelistindex']
        print('[song-convert] Unused NotelistIndexes:', unused_notelistindex)

        output_unused_patterns = False
        if 'mi2m-output-unused-nle' in extra_json:
            output_unused_patterns = extra_json['mi2m-output-unused-nle']

        if output_unused_patterns == True:
            unusedplrowfound = None
            plrow = 300
            while unusedplrowfound == None:
                if str(plrow) not in t_s_playlist: unusedplrowfound = True
                else: unusedplrowfound = str(plrow)
                plrow += 1
                if plrow == 2000: break
            if unusedplrowfound != None:
                tracks.m_playlist_pl(cvpj_proj, unusedplrowfound, '__UNUSED__', None, None)

                unused_placement_data_pos = 0
                for unused_notelistindex_e in unused_notelistindex:
                    unused_placement_data = {}
                    unused_placement_data = unused_placement_data | t_s_notelistindex[unused_notelistindex_e]
                    unused_placement_data['position'] = unused_placement_data_pos
                    unused_placement_data_dur = notelist_data.getduration(unused_placement_data['notelist'])
                    unused_placement_data['duration'] = unused_placement_data_dur
                    unused_placement_data['muted'] = True
                    unused_placement_data_pos += unused_placement_data_dur
                    tracks.m_playlist_pl_add(cvpj_proj, unusedplrowfound, unused_placement_data)

    else:
        print('[song-convert] notelistindex not found.')


    if 'sampleindex' in cvpj_proj:
        t_s_samplesindex = cvpj_proj['sampleindex']
        for pl_row in t_s_playlist:
            pl_row_data = t_s_playlist[pl_row]
            if 'placements_audio' in pl_row_data:
                pl_row_placements = pl_row_data['placements_audio']
                for pldata in pl_row_placements:
                    if 'fromindex' in pldata:
                        fromindex = pldata['fromindex']
                        if fromindex in t_s_samplesindex:
                            index_pl_data = t_s_samplesindex[fromindex]
                            del pldata['fromindex']
                            if 'name' in index_pl_data: pldata['name'] = index_pl_data['name']
                            if 'color' in index_pl_data: pldata['color'] = index_pl_data['color']
                            if 'pan' in index_pl_data: pldata['pan'] = index_pl_data['pan']
                            if 'vol' in index_pl_data: pldata['vol'] = index_pl_data['vol']
                            if 'file' in index_pl_data: pldata['file'] = index_pl_data['file']
                            if 'fxrack_channel' in index_pl_data: pldata['fxrack_channel'] = index_pl_data['fxrack_channel']
        del cvpj_proj['sampleindex']


    return json.dumps(cvpj_proj)
