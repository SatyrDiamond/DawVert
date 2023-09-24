# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

def convert(song, extra_json):
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
