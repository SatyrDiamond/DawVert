# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from functions import data_values
import plugin_input
import json
import os
import zipfile

# -------------------------------------------- notes --------------------------------------------

def parse_clip_notes(placement_obj, j_wvtl_trackclip):
    j_wvtl_trc_type = j_wvtl_trackclip['type']
    j_wvtl_trc_loopStart = j_wvtl_trackclip['loopStart']
    j_wvtl_trc_loopEnd = j_wvtl_trackclip['loopEnd']
    j_wvtl_trc_timelineStart = j_wvtl_trackclip['timelineStart']
    j_wvtl_trc_timelineEnd = j_wvtl_trackclip['timelineEnd']
    j_wvtl_trc_readStart = j_wvtl_trackclip['readStart']

    if 'color' in j_wvtl_trackclip: placement_obj.visual.color = colors.hex_to_rgb_float(j_wvtl_trackclip['color'])
    if 'name' in j_wvtl_trackclip: placement_obj.visual.name = j_wvtl_trackclip['name']
    placement_obj.position = j_wvtl_trc_timelineStart
    placement_obj.duration = j_wvtl_trc_timelineEnd - j_wvtl_trc_timelineStart
    placement_obj.cut_loop_data(j_wvtl_trc_readStart, j_wvtl_trc_loopStart, j_wvtl_trc_loopEnd)

    if j_wvtl_trc_type == 'MIDI':
        if 'notes' in j_wvtl_trackclip:
            for j_wvtl_n in j_wvtl_trackclip['notes']:
                placement_obj.notelist.add_r(j_wvtl_n['start'], j_wvtl_n['end']-j_wvtl_n['start'], j_wvtl_n['pitch']-60, j_wvtl_n['velocity'], {})

# -------------------------------------------- audio --------------------------------------------

def extract_audio(audioname):
    audio_filename = None
    for s_file in zip_data.namelist():
        if audioname in s_file:
            audio_filename = samplefolder+s_file
            if os.path.exists(samplefolder+s_file) == False:
                zip_data.extract(s_file, path=samplefolder, pwd=None)
                break
    return audio_filename

def parse_clip_audio(convproj_obj, placement_obj, j_wvtl_trackclip):
    j_wvtl_trc_type = j_wvtl_trackclip['type']
    j_wvtl_trc_loopStart = j_wvtl_trackclip['loopStart']
    j_wvtl_trc_loopEnd = j_wvtl_trackclip['loopEnd']
    j_wvtl_trc_timelineStart = j_wvtl_trackclip['timelineStart']
    j_wvtl_trc_timelineEnd = j_wvtl_trackclip['timelineEnd']
    j_wvtl_trc_readStart = j_wvtl_trackclip['readStart']
    j_wvtl_trc_transpose = data_values.get_value(j_wvtl_trackclip, 'transpose', 0)
    j_wvtl_trc_warp = data_values.get_value(j_wvtl_trackclip, 'warp', {})
    if j_wvtl_trc_warp == None: j_wvtl_trc_warp = {}

    if j_wvtl_trc_warp != {}:
        placement_obj.stretch.method = 'warp' if j_wvtl_trc_warp['enabled'] else 'rate_tempo'
        sourcebpm = j_wvtl_trc_warp['sourceBPM']/120
        for anchor in j_wvtl_trc_warp['anchors']: placement_obj.stretch.warp.append([j_wvtl_trc_warp['anchors'][anchor]['destination']*4, (float(anchor)/sourcebpm)/2])
    else: 
        placement_obj.stretch.set_rate(j_wvtl_bpm, 1)

    if 'color' in j_wvtl_trackclip: placement_obj.visual.color = colors.hex_to_rgb_float(j_wvtl_trackclip['color'])
    if 'name' in j_wvtl_trackclip: placement_obj.visual.name = j_wvtl_trackclip['name']
    if 'fadeIn' in j_wvtl_trackclip: placement_obj.fade_in['duration'] = j_wvtl_trackclip['fadeIn']
    if 'fadeOut' in j_wvtl_trackclip: placement_obj.fade_out['duration'] = j_wvtl_trackclip['fadeOut']

    placement_obj.position = j_wvtl_trc_timelineStart
    placement_obj.duration = j_wvtl_trc_timelineEnd - j_wvtl_trc_timelineStart
    placement_obj.cut_loop_data(j_wvtl_trc_readStart, j_wvtl_trc_loopStart, j_wvtl_trc_loopEnd)

    placement_obj.stretch.algorithm = 'beats'
    placement_obj.pitch = j_wvtl_trc_transpose
    placement_obj.stretch.rate = pow(2, j_wvtl_trc_transpose/12)*(120/j_wvtl_bpm)

    if 'audioBufferId' in j_wvtl_trackclip: 
        audio_filename = extract_audio(j_wvtl_trackclip['audioBufferId'])
        convproj_obj.add_sampleref(j_wvtl_trackclip['audioBufferId'], audio_filename)
        placement_obj.sampleref = j_wvtl_trackclip['audioBufferId']

# -------------------------------------------- track --------------------------------------------

def parse_track(j_wvtl_track, convproj_obj):
    j_wvtl_tracktype = j_wvtl_track['type']
    j_wvtl_trackname = j_wvtl_track['name']
    j_wvtl_trackid = j_wvtl_track['id']
    j_wvtl_trackcolor = colors.hex_to_rgb_float(j_wvtl_track['color'])
    j_wvtl_trackclips = j_wvtl_track['clips']
    j_wvtl_gain = j_wvtl_track['gain']
    j_wvtl_balance = j_wvtl_track['balance']
    j_wvtl_mute = j_wvtl_track['mute']
    
    print('[input-wavtool] '+j_wvtl_tracktype+' Track: '+j_wvtl_trackname)

    if j_wvtl_tracktype == 'MIDI':
        track_obj = convproj_obj.add_track(j_wvtl_trackid, 'instrument', 1, False)
        track_obj.visual.name = j_wvtl_trackname
        track_obj.visual.color = j_wvtl_trackcolor
        track_obj.params.add('vol', j_wvtl_gain, 'float')
        track_obj.params.add('pan', j_wvtl_balance, 'float')
        track_obj.params.add('enabled', int(not j_wvtl_mute), 'bool')

        for j_wvtl_trackclip in j_wvtl_trackclips:
            placement_obj = track_obj.placements.add_notes()
            parse_clip_notes(placement_obj, j_wvtl_trackclip)

    if j_wvtl_tracktype == 'Audio':
        track_obj = convproj_obj.add_track(j_wvtl_trackid, 'audio', True, False)
        track_obj.visual.name = j_wvtl_trackname
        track_obj.visual.color = j_wvtl_trackcolor
        track_obj.params.add('vol', j_wvtl_gain, 'float')
        track_obj.params.add('pan', j_wvtl_balance, 'float')
        track_obj.params.add('enabled', int(not j_wvtl_mute), 'bool')
        for j_wvtl_trackclip in j_wvtl_trackclips:
            placement_obj = track_obj.placements.add_audio()
            parse_clip_audio(convproj_obj, placement_obj, j_wvtl_trackclip)

# -------------------------------------------- main --------------------------------------------

class input_wavtool(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'wavtool'
    def getname(self): return 'wavtool'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'placement_cut': True,
        'placement_loop': ['loop', 'loop_off', 'loop_adv'],
        'placement_audio_stretch': ['rate']
        }
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, extra_param):
        global samplefolder
        global zip_data
        global j_wvtl_bpm

        convproj_obj.type = 'r'
        convproj_obj.set_timings(1, True)

        zip_data = zipfile.ZipFile(input_file, 'r')
        json_filename = None
        samplefolder = extra_param['samplefolder']
        for jsonname in zip_data.namelist():
            if '.json' in jsonname: json_filename = jsonname
        t_wavtool_project = zip_data.read(json_filename)
        j_wvtl_project = json.loads(t_wavtool_project)
        if 'debug' in extra_param:
            with open('testout.json', "w") as fileout:
                json.dump(j_wvtl_project, fileout, indent=4, sort_keys=True)
        j_wvtl_bpm = j_wvtl_project['bpm']
        j_wvtl_beatDenominator = j_wvtl_project['beatDenominator']
        j_wvtl_beatNumerator = j_wvtl_project['beatNumerator']
        j_wvtl_tracks = j_wvtl_project['tracks']
        for j_wvtl_track in j_wvtl_tracks: parse_track(j_wvtl_track, convproj_obj)

        convproj_obj.track_master.visual.name = 'Master'
        convproj_obj.track_master.visual.color = [0.14, 0.14, 0.14]
        convproj_obj.track_master.params.add('vol', 1, 'float')

        convproj_obj.timesig = [j_wvtl_beatNumerator, j_wvtl_beatDenominator]
        convproj_obj.params.add('bpm', j_wvtl_bpm, 'float')