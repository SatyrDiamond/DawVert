# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

from functions import tracks

m2mi_sample_names = ['file', 'name', 'color', 'audiomod', 'vol', 'pan', 'fxrack_channel']
m2mi_notes_names = ['id', 'notelist', 'name', 'color']

def convert(song):
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
