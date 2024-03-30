# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from objects_file import proj_wavtool
import plugin_input
import json
import os
import zipfile

def extract_audio(audioname):
    audio_filename = None
    for s_file in zip_data.namelist():
        if audioname in s_file:
            audio_filename = samplefolder+s_file
            if os.path.exists(samplefolder+s_file) == False:
                zip_data.extract(s_file, path=samplefolder, pwd=None)
                break
    return audio_filename

class input_wavtool(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'wavtool'
    def gettype(self): return 'r'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Wavtool'
        dawinfo_obj.file_ext = 'zip'
        dawinfo_obj.placement_cut = True
        dawinfo_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
        dawinfo_obj.audio_stretch = ['warp']
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, dv_config):
        global samplefolder
        global zip_data
        global wavtool_obj

        convproj_obj.type = 'r'
        convproj_obj.set_timings(1, True)

        zip_data = zipfile.ZipFile(input_file, 'r')
        json_filename = None
        samplefolder = dv_config.path_samples_extracted
        for jsonname in zip_data.namelist():
            if '.json' in jsonname: json_filename = jsonname
        t_wavtool_project = zip_data.read(json_filename)
        wt_proj = json.loads(t_wavtool_project)
        wavtool_obj = proj_wavtool.wavtool_project(wt_proj)

        for trackid, wavtool_track in wavtool_obj.tracks.items(): 
            trackcolor = colors.hex_to_rgb_float(wavtool_track.color)

            print('[input-wavtool] '+wavtool_track.type+' Track: '+wavtool_track.name)
            if wavtool_track.type == 'MIDI':
                track_obj = convproj_obj.add_track(trackid, 'instrument', 1, False)
                track_obj.visual.name = wavtool_track.name
                track_obj.visual.color = trackcolor
                track_obj.params.add('vol', wavtool_track.gain, 'float')
                track_obj.params.add('pan', wavtool_track.balance, 'float')
                track_obj.params.add('enabled', int(not wavtool_track.mute), 'bool')
                for wavtool_clip in wavtool_track.clips:
                    placement_obj = track_obj.placements.add_notes()
                    placement_obj.visual.color = colors.hex_to_rgb_float(wavtool_clip.color)
                    placement_obj.visual.name = wavtool_clip.name
                    placement_obj.position = wavtool_clip.timelineStart
                    placement_obj.duration = wavtool_clip.timelineEnd - wavtool_clip.timelineStart
                    placement_obj.cut_loop_data(wavtool_clip.readStart, wavtool_clip.loopStart, wavtool_clip.loopEnd)
                    for note in wavtool_clip.notes:
                        placement_obj.notelist.add_r(note['start'], note['end']-note['start'], note['pitch']-60, note['velocity'], {})

            if wavtool_track.type == 'Audio':
                track_obj = convproj_obj.add_track(trackid, 'audio', 1, False)
                track_obj.visual.name = wavtool_track.name
                track_obj.visual.color = trackcolor
                track_obj.params.add('vol', wavtool_track.gain, 'float')
                track_obj.params.add('pan', wavtool_track.balance, 'float')
                track_obj.params.add('enabled', int(not wavtool_track.mute), 'bool')
                for wavtool_clip in wavtool_track.clips:
                    placement_obj = track_obj.placements.add_audio()
                    placement_obj.visual.color = colors.hex_to_rgb_float(wavtool_clip.color)
                    placement_obj.visual.name = wavtool_clip.name
                    placement_obj.position = wavtool_clip.timelineStart
                    placement_obj.duration = wavtool_clip.timelineEnd - wavtool_clip.timelineStart
                    if wavtool_clip.loopEnabled:
                        placement_obj.cut_loop_data(wavtool_clip.readStart, wavtool_clip.loopStart, wavtool_clip.loopEnd)

                    placement_obj.fade_in['duration'] = wavtool_clip.fadeIn
                    placement_obj.fade_out['duration'] = wavtool_clip.fadeOut

                    if wavtool_clip.warp != {}:
                        placement_obj.stretch.use_tempo = wavtool_clip.warp['enabled']
                        placement_obj.stretch.is_warped = wavtool_clip.warp['enabled']
                        sourcebpm = wavtool_clip.warp['sourceBPM']/120
                        for anchor in wavtool_clip.warp['anchors']: 
                            placement_obj.stretch.warp.append([
                                wavtool_clip.warp['anchors'][anchor]['destination']*4 ,(float(anchor)/sourcebpm)/2])
                    else: placement_obj.stretch.set_rate_speed(wavtool_obj.bpm, 1, False)

                    placement_obj.stretch.algorithm = 'beats'
                    placement_obj.pitch = wavtool_clip.transpose
                    placement_obj.stretch.rate = pow(2, wavtool_clip.transpose/12)*(120/wavtool_obj.bpm)

                    audio_filename = extract_audio(wavtool_clip.audioBufferId)
                    convproj_obj.add_sampleref(wavtool_clip.audioBufferId, audio_filename)
                    placement_obj.sampleref = wavtool_clip.audioBufferId

        convproj_obj.track_master.visual.name = 'Master'
        convproj_obj.track_master.visual.color = [0.14, 0.14, 0.14]
        convproj_obj.track_master.params.add('vol', 1, 'float')

        convproj_obj.timesig = [wavtool_obj.beatNumerator, wavtool_obj.beatDenominator]
        convproj_obj.params.add('bpm', wavtool_obj.bpm, 'float')

        convproj_obj.metadata.name = wavtool_obj.name