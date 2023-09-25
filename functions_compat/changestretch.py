# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import audio
from functions import data_values
from functions import params

def warp2rate(cvpj_placements, tempo):
    new_placements = []
    tempomul = (120/tempo)
    for cvpj_placement in cvpj_placements:
        audiorate = 1
        minus_offset = 0
        plus_offset = 0
        if 'audiomod' in cvpj_placement:
            old_audiomod = cvpj_placement['audiomod']
            new_audiomod = {}
            new_audiomod['stretch_data'] = {}
            new_audiomod['stretch_method'] = None
            new_audiomod['stretch_algorithm'] = 'stretch'
            if 'pitch' in old_audiomod: new_audiomod['pitch'] = old_audiomod['pitch']

            if 'stretch_method' in old_audiomod: 
                if old_audiomod['stretch_method'] == 'warp':
                    t_warpmarkers = old_audiomod['stretch_data']

                    if t_warpmarkers[0]['pos'] != 0: 
                        minuswarppos = t_warpmarkers[0]['pos']
                        if t_warpmarkers[0]['pos'] < 0: minus_offset -= minuswarppos
                        if t_warpmarkers[0]['pos'] > 0: plus_offset += minuswarppos
                        for t_warpmarker in t_warpmarkers:
                            t_warpmarker['pos'] -= minuswarppos

                    audio_info = audio.get_audiofile_info(cvpj_placement['file'])
                    audio_dur_sec_steps = audio_info['dur_sec']*8

                    if 'stretch_algorithm' in old_audiomod: new_audiomod['stretch_algorithm'] = old_audiomod['stretch_algorithm']

                    if len(t_warpmarkers) >= 2:
                        t_warpmarker_last = t_warpmarkers[-1]
                        new_audiomod['stretch_method'] = 'rate_tempo'
                        audiorate = (1/((t_warpmarker_last['pos']/8)/t_warpmarkers[-1]['pos_real']))
                        new_audiomod['stretch_data']['rate'] = audiorate

            cvpj_placement['audiomod'] = new_audiomod

        if 'cut' in cvpj_placement:
            cutdata = cvpj_placement['cut']

            if audiorate != 1:
                if cutdata['type'] == 'loop':
                    data_values.time_from_steps(cutdata, 'start', True, cutdata['start']+minus_offset, audiorate)
                    data_values.time_from_steps(cutdata, 'loopstart', True, cutdata['loopstart']+minus_offset, audiorate)
                    data_values.time_from_steps(cutdata, 'loopend', True, cutdata['loopend']+minus_offset, audiorate )
                    cvpj_placement['position'] += plus_offset
                    cvpj_placement['duration'] -= plus_offset
                    cvpj_placement['duration'] += minus_offset

                if cutdata['type'] == 'cut':
                    data_values.time_from_steps(cutdata, 'start', True, cutdata['start']+minus_offset, (1/audiorate)*tempomul )
                    data_values.time_from_steps(cutdata, 'end', True, cutdata['end']+minus_offset-plus_offset, (1/audiorate)*tempomul )

    return cvpj_placements

def rate2warp(cvpj_placements, tempo):
    new_placements = []
    tempomul = (120/tempo)

    for cvpj_placement in cvpj_placements:
        audiorate = 1
        ratetempo = 1

        if 'audiomod' in cvpj_placement:
            old_audiomod = cvpj_placement['audiomod']
            new_audiomod = {}

            if 'stretch_method' in old_audiomod: 
                if old_audiomod['stretch_method'] in ['rate_tempo', 'rate_speed', 'rate_ignoretempo']:
                    audio_info = audio.get_audiofile_info(cvpj_placement['file'])
                    audio_dur_sec = audio_info['dur_sec']

                    t_stretch_data = old_audiomod['stretch_data']

                    new_audiomod = {}
                    new_audiomod['stretch_method'] = 'warp'
                    new_audiomod['stretch_algorithm'] = 'stretch'
                    if 'stretch_algorithm' in old_audiomod: new_audiomod['stretch_algorithm'] = old_audiomod['stretch_algorithm']
                    if 'pitch' in old_audiomod: new_audiomod['pitch'] = old_audiomod['pitch']

                    audiorate = t_stretch_data['rate']
                    ratetempo = 1/(audiorate/tempomul)

                    if old_audiomod['stretch_method'] == 'rate_ignoretempo':
                        new_audiomod['stretch_data'] = [
                            {'pos': 0.0, 'pos_real': 0.0}, 
                            {'pos': audio_dur_sec*8, 'pos_real': (audio_dur_sec*audiorate)/tempomul}
                        ]

                    if old_audiomod['stretch_method'] == 'rate_tempo':
                        new_audiomod['stretch_data'] = [
                            {'pos': 0.0, 'pos_real': 0.0}, 
                            {'pos': audio_dur_sec*8, 'pos_real': (audio_dur_sec*audiorate)}
                        ]

                    if old_audiomod['stretch_method'] == 'rate_speed':
                        new_audiomod['stretch_data'] = [
                            {'pos': 0.0, 'pos_real': 0.0}, 
                            {'pos': audio_dur_sec*8, 'pos_real': (audio_dur_sec*audiorate)*tempomul}
                        ]

                    cvpj_placement['audiomod'] = new_audiomod

    return cvpj_placements

def process_r(projJ, stretchtype):
    tempo = params.get(projJ, [], 'bpm', 120)[0]
    if 'track_placements' in projJ:
        for track_placements_id in projJ['track_placements']:
            track_placements_data = projJ['track_placements'][track_placements_id]
            not_laned = True
            if 'laned' in track_placements_data:
                print('[compat] warp2rate: laned: '+track_placements_id)
                if track_placements_data['laned'] == 1:
                    not_laned = False
                    s_lanedata = track_placements_data['lanedata']
                    s_laneordering = track_placements_data['laneorder']
                    for t_lanedata in s_lanedata:
                        tj_lanedata = s_lanedata[t_lanedata]
                        if 'audio' in tj_lanedata:
                            if stretchtype == 'rate': 
                                print('[compat] warp2rate: laned: '+track_placements_id)
                                tj_lanedata['audio'] = warp2rate(tj_lanedata['audio'], tempo)
                            if stretchtype == 'warp': 
                                print('[compat] rate2warp: laned: '+track_placements_id)
                                tj_lanedata['audio'] = rate2warp(tj_lanedata['audio'], tempo)

            if not_laned == True:
                if 'audio' in track_placements_data:
                    if stretchtype == 'rate': 
                        print('[compat] warp2rate: non-laned: '+track_placements_id)
                        track_placements_data['audio'] = warp2rate(track_placements_data['audio'], tempo)
                    if stretchtype == 'warp': 
                        print('[compat] rate2warp: non-laned: '+track_placements_id)
                        track_placements_data['audio'] = rate2warp(track_placements_data['audio'], tempo)
    return True

def process_m(projJ, stretchtype):
    tempo = params.get(projJ, [], 'bpm', 120)[0]
    for playlist_id in projJ['playlist']:
        playlist_id_data = projJ['playlist'][playlist_id]
        if 'placements_audio' in playlist_id_data:
            if stretchtype == 'rate': playlist_id_data['placements_audio'] = warp2rate(playlist_id_data['placements_audio'], tempo)
            if stretchtype == 'warp': playlist_id_data['placements_audio'] = rate2warp(playlist_id_data['placements_audio'], tempo)
    return True

def process(cvpj_proj, cvpj_type, in__placement_audio_stretch, out__placement_audio_stretch):
    if 'warp' in in__placement_audio_stretch and 'warp' not in out__placement_audio_stretch:
        if cvpj_type == 'm': return process_m(cvpj_proj, 'rate')
        elif cvpj_type in ['r', 'ri', 'rm']: return process_r(cvpj_proj, 'rate')
        else: return False

    elif 'rate' in in__placement_audio_stretch and 'rate' not in out__placement_audio_stretch:
        if cvpj_type == 'm': return process_m(cvpj_proj, 'warp')
        elif cvpj_type in ['r', 'ri', 'rm']: return process_r(cvpj_proj, 'warp')
        else: return False

    else: return False