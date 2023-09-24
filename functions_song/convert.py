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

def rx_track_iter(cvpj_track_placements, cvpj_track_order, cvpj_track_data):
    for trackid in cvpj_track_order:
        track_placements_pre = cvpj_track_placements[trackid] if trackid in cvpj_track_placements else {}
        track_placements_notes = track_placements_pre['notes'] if 'notes' in track_placements_pre else []
        track_placements_audio = track_placements_pre['audio'] if 'audio' in track_placements_pre else []
        track_data = cvpj_track_data[trackid] if trackid in cvpj_track_data else {}
        yield trackid, track_data, track_placements_notes, track_placements_audio

# ---------------------------------- Cloned to Regular ----------------------------------

def c2r(song):
    print('[song-convert] Converting from Cloned > Regular')
    cvpj_proj = json.loads(song)
    if 'track_order' not in cvpj_proj:
        print('[error] track_order not found')

    cvpj_instruments_data = cvpj_proj['instruments_data']
    del cvpj_proj['instruments_data']
    cvpj_track_order = cvpj_proj['track_order']
    del cvpj_proj['track_order']
    cvpj_track_data = cvpj_proj['track_data']
    del cvpj_proj['track_data']
    cvpj_plugins = cvpj_proj['plugins']
    del cvpj_proj['plugins']

    if 'track_placements' in cvpj_proj: 
        cvpj_track_placements = cvpj_proj['track_placements']
        del cvpj_proj['track_placements']
    else: cvpj_track_placements = {}

    cvpj_proj['track_placements'] = {}
    cvpj_proj['track_order'] = []
    cvpj_proj['track_data'] = {}
    cvpj_proj['plugins'] = {}

    usedinst = {}

    for trackid, track_data, track_placements_notes, track_placements_audio in rx_track_iter(cvpj_track_placements, cvpj_track_order, cvpj_track_data):

        if track_data['type'] == 'instruments':
            track_data['type'] = 'instrument'

            used_insts = []
            for c_track_placement in track_placements_notes:
                c_track_placement_base = c_track_placement.copy()
                del c_track_placement_base['notelist']
                m_notelist = {}
                if 'notelist' in c_track_placement:
                    for cvpj_note in c_track_placement['notelist']:
                        noteinst = cvpj_note['instrument']
                        if noteinst not in m_notelist: m_notelist[noteinst] = []
                        cvpj_note['instrument'] += '_'+trackid
                        m_notelist[noteinst].append(cvpj_note)
                        if noteinst not in used_insts: used_insts.append(noteinst)

                for m_inst in m_notelist:
                    r_trackid = m_inst+'_'+trackid
                    c_track_placement_single = c_track_placement_base.copy()
                    c_track_placement_single['notelist'] = m_notelist[m_inst]
                    data_values.nested_dict_add_to_list(
                        cvpj_proj, 
                        ['track_placements', r_trackid, 'notes'], 
                        c_track_placement_single)

            for used_inst in used_insts:
                cvpj_instrument = cvpj_instruments_data[used_inst].copy() if used_inst in cvpj_instruments_data else {}
                pluginid = data_values.nested_dict_get_value(cvpj_instrument, ['instdata', 'pluginid'])
                if pluginid != None and pluginid not in cvpj_proj['plugins']:
                    cvpj_proj['plugins'][pluginid] = cvpj_plugins[pluginid]

                #cvpj_plugins
                temp_track_data = track_data.copy()

                if 'name' in cvpj_instrument: 
                    instname = cvpj_instrument['name']
                    del cvpj_instrument['name']
                else:
                    instname = used_inst

                if 'name' in temp_track_data: temp_track_data['name'] = instname+' ('+temp_track_data['name']+')'
                else: temp_track_data['name'] = instname

                temp_track_data |= cvpj_instrument

                r_trackid = used_inst+'_'+trackid
                cvpj_proj['track_order'].append(r_trackid)
                cvpj_proj['track_data'][r_trackid] = temp_track_data

        if track_data['type'] == 'audio':
            cvpj_proj['track_order'].append(trackid)
            cvpj_proj['track_data'][trackid] = track_data
            data_values.nested_dict_add_to_list(
                cvpj_proj, 
                ['track_placements', trackid, 'audio'], 
                track_placements_audio)


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
            notelistindex = data_values.get_value(singletrack_data, 'notelistindex', {})
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

            if 'notelistindex' in singletrack_data: del singletrack_data['notelistindex']

    return json.dumps(cvpj_proj)

# ---------------------------------- Multiple to MultipleIndexed ----------------------------------

m2mi_sample_names = ['file', 'name', 'color', 'audiomod', 'vol', 'pan', 'fxrack_channel']
m2mi_notes_names = ['id', 'notelist', 'name', 'color']

def m2mi(song):
    print('[song-convert] Converting from Multiple > MultipleIndexed')
    global cvpj_proj
    cvpj_proj = json.loads(song)
    cvpj_playlist = cvpj_proj['playlist']

    pattern_number = 1
    cvpj_notelistindex = {}
    existingpatterns = []
    for cvpj_playlistentry in cvpj_playlist:
        cvpj_playlistentry_data = cvpj_playlist[cvpj_playlistentry]
        if 'placements_notes' not in cvpj_playlistentry_data: cvpj_placements_notes = []
        else: cvpj_placements_notes = cvpj_playlistentry_data['placements_notes']
        for cvpj_placement in cvpj_placements_notes:
            nle_data = [None, None, None]

            nle_data[0] = cvpj_placement['notelist'].copy() if 'notelist' in cvpj_placement else []
            if 'name' in cvpj_placement: nle_data[1] = cvpj_placement['name']
            if 'color' in cvpj_placement: nle_data[2] = cvpj_placement['color']

            dupepatternfound = None
            for existingpattern in existingpatterns:
                if existingpattern[1] == nle_data: 
                    dupepatternfound = existingpattern[0]
                    break

            if dupepatternfound == None:
                patid = 'm2mi_' + str(pattern_number)
                existingpatterns.append([patid, nle_data])
                dupepatternfound = patid
                pattern_number += 1

            cvpj_placement['fromindex'] = dupepatternfound

    for existingpattern in existingpatterns:
        tracks.m_add_nle(cvpj_proj, existingpattern[0], existingpattern[1][0])
        tracks.m_add_nle_info(cvpj_proj, existingpattern[0], existingpattern[1][1], existingpattern[1][2])

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

    if 'notelistindex' not in cvpj_proj: cvpj_proj['notelistindex'] = {}

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
        print('[song-convert] Unused NotelistIndexes:', ', '.join(unused_notelistindex))

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
                            if 'audiomod' in index_pl_data: pldata['audiomod'] = index_pl_data['audiomod']
                            if 'fxrack_channel' in index_pl_data: pldata['fxrack_channel'] = index_pl_data['fxrack_channel']
        del cvpj_proj['sampleindex']


    return json.dumps(cvpj_proj)
