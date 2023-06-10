# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import colors
from functions import audio
from functions import data_values

import xml.etree.ElementTree as ET
import plugin_input
import json
import gzip 


colorlist = ['FF94A6','FFA529','CC9927','F7F47C','BFFB00','1AFF2F','25FFA8','5CFFE8','8BC5FF','5480E4','92A7FF','D86CE4','E553A0','FFFFFF','FF3636','F66C03','99724B','FFF034','87FF67','3DC300','00BFAF','19E9FF','10A4EE','007DC0','886CE4','B677C6','FF39D4','D0D0D0','E2675A','FFA374','D3AD71','EDFFAE','D2E498','BAD074','9BC48D','D4FDE1','CDF1F8','B9C1E3','CDBBE4','AE98E5','E5DCE1','A9A9A9','C6928B','B78256','99836A','BFBA69','A6BE00','7DB04D','88C2BA','9BB3C4','85A5C2','8393CC','A595B5','BF9FBE','BC7196','7B7B7B','AF3333','A95131','724F41','DBC300','85961F','539F31','0A9C8E','236384','1A2F96','2F52A2','624BAD','A34BAD','CC2E6E','3C3C3C']
colorlist_one = [colors.hex_to_rgb_float(color) for color in colorlist]


def get_value(xmldata, varname, fallback): 
    if len(xmldata.findall(varname)) != 0:
        xml_e = xmldata.findall(varname)[0]
        return xml_e.get('Value')
    else:
        return fallback

def get_param(xmldata, varname, vartype, fallback): 
    if len(xmldata.findall(varname)) != 0:
        param_data = xmldata.findall(varname)[0]
        out_value = get_value(param_data, 'Manual', fallback)
        if vartype == 'string': return out_value
        if vartype == 'float': return float(out_value)
        if vartype == 'int': return int(out_value)
        if vartype == 'bool': return ['false','true'].index(out_value)
    else:
        return fallback

def get_sampleref(xmldata):
    x_sampleref = xmldata.findall('SampleRef')[0]
    x_fileref = x_sampleref.findall('FileRef')[0]
    out_data = {}
    out_data['file'] = get_value(x_fileref, 'Path', '')
    out_data['samples'] = float(get_value(x_sampleref, 'DefaultDuration', 1))
    out_data['rate'] = float(get_value(x_sampleref, 'DefaultSampleRate', 1))
    out_data['seconds'] = out_data['samples'] / out_data['rate']
    return out_data

class input_ableton(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'ableton'
    def getname(self): return 'Ableton Live 11'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': True,
        'placement_audio_stretch': ['warp'],
        }
    def parse(self, input_file, extra_param):

        xmlstring = ""

        with open(input_file, 'rb') as alsbytes:
            if alsbytes.read(2) == b'\x1f\x8b': 
                alsbytes.seek(0)
                xmlstring = gzip.decompress(alsbytes.read())
            else:
                alsbytes.seek(0)
                xmlstring = alsbytes.read().decode()

        root = ET.fromstring(xmlstring)

        abletonversion = root.get('MinorVersion').split('.')[0]
        if abletonversion != '11':
            print('[error] Ableton version '+abletonversion+' is not supported.')
            exit()

        x_LiveSet = root.findall('LiveSet')[0]
        x_Tracks = x_LiveSet.findall('Tracks')[0]
        x_MasterTrack = x_LiveSet.findall('MasterTrack')[0]

        cvpj_l = {}

        x_mastertrack_Name = x_MasterTrack.findall('Name')[0]
        mastertrack_name = get_value(x_mastertrack_Name, 'EffectiveName', '')
        mastertrack_color = colorlist_one[int(get_value(x_MasterTrack, 'Color', 'test'))]
        track_vol = get_param(x_MasterTrack, 'Volume', 'float', 0)
        tracks.a_addtrack_master(cvpj_l, mastertrack_name, track_vol, mastertrack_color)
        x_mastertrack_DeviceChain = x_MasterTrack.findall('DeviceChain')[0]
        x_mastertrack_Mixer = x_mastertrack_DeviceChain.findall('Mixer')[0]
        cvpj_l['bpm'] = get_param(x_mastertrack_Mixer, 'Tempo', 'float', 140)
        tempo = cvpj_l['bpm']

        returnid = 0

        for x_track_data in list(x_Tracks):
            tracktype = x_track_data.tag

            x_track_DeviceChain = x_track_data.findall('DeviceChain')[0]
            x_track_Mixer = x_track_DeviceChain.findall('Mixer')[0]

            x_track_Name = x_track_data.findall('Name')[0]

            track_id = x_track_data.get('Id')
            track_name = get_value(x_track_Name, 'EffectiveName', '')
            track_color = colorlist_one[int(get_value(x_track_data, 'Color', 'test'))]
            track_vol = get_param(x_track_Mixer, 'Volume', 'float', 0)
            track_pan = get_param(x_track_Mixer, 'Pan', 'float', 0)

            track_sends = x_track_Mixer.findall('Sends')[0]
            track_sendholders = track_sends.findall('TrackSendHolder')

            if tracktype == 'MidiTrack':
                tracks.r_create_inst(cvpj_l, track_id, {})
                tracks.r_basicdata(cvpj_l, track_id, track_name, track_color, track_vol, track_pan)
                tracks.r_pl_notes(cvpj_l, track_id, [])

                x_track_MainSequencer = x_track_DeviceChain.findall('MainSequencer')[0]
                x_track_ClipTimeable = x_track_MainSequencer.findall('ClipTimeable')[0]
                x_track_ArrangerAutomation = x_track_ClipTimeable.findall('ArrangerAutomation')[0]
                x_track_Events = x_track_ArrangerAutomation.findall('Events')[0]
                x_track_MidiClips = x_track_Events.findall('MidiClip')
                for x_track_MidiClip in x_track_MidiClips:
                    note_placement_pos = float(get_value(x_track_MidiClip, 'CurrentStart', 0))*4
                    note_placement_dur = float(get_value(x_track_MidiClip, 'CurrentEnd', 0))*4 - note_placement_pos
                    note_placement_name = get_value(x_track_MidiClip, 'Name', '')
                    note_placement_color = colorlist_one[int(get_value(x_track_MidiClip, 'Color', 0))]
                    note_placement_muted = ['false','true'].index(get_value(x_track_MidiClip, 'Disabled', 'false'))

                    cvpj_placement = {}
                    cvpj_placement['position'] = note_placement_pos
                    cvpj_placement['duration'] = note_placement_dur
                    cvpj_placement['name'] = note_placement_name
                    cvpj_placement['color'] = note_placement_color
                    cvpj_placement['muted'] = note_placement_muted

                    x_track_MidiClip_loop = x_track_MidiClip.findall('Loop')[0]
                    note_placement_loop_l_start = float(get_value(x_track_MidiClip_loop, 'LoopStart', 0))*4
                    note_placement_loop_l_end = float(get_value(x_track_MidiClip_loop, 'LoopEnd', 1))*4
                    note_placement_loop_start = float(get_value(x_track_MidiClip_loop, 'StartRelative', 0))*4
                    note_placement_loop_on = ['false','true'].index(get_value(x_track_MidiClip_loop, 'LoopOn', 'false'))

                    if note_placement_loop_on == 1:
                        cvpj_placement['cut'] = {}
                        cvpj_placement['cut']['type'] = 'loop'
                        cvpj_placement['cut']['start'] = note_placement_loop_start
                        cvpj_placement['cut']['loopstart'] = note_placement_loop_l_start
                        cvpj_placement['cut']['loopend'] = note_placement_loop_l_end
                    else:
                        cvpj_placement['cut'] = {}
                        cvpj_placement['cut']['type'] = 'cut'
                        cvpj_placement['cut']['start'] = note_placement_loop_l_start
                        cvpj_placement['cut']['end'] = note_placement_loop_l_end

                    cvpj_placement['notelist'] = []

                    x_track_MidiClip_Notes = x_track_MidiClip.findall('Notes')[0]
                    x_track_MidiClip_KT = x_track_MidiClip_Notes.findall('KeyTracks')[0]

                    t_notes = {}

                    for x_track_MidiClip_KT_KT_s in x_track_MidiClip_KT.findall('KeyTrack'):
                        t_ableton_note_key = int(get_value(x_track_MidiClip_KT_KT_s, 'MidiKey', 60))-60
                        x_track_MidiClip_KT_KT_Notes = x_track_MidiClip_KT_KT_s.findall('Notes')[0]
                        for x_track_MidiClip_MNE in x_track_MidiClip_KT_KT_Notes.findall('MidiNoteEvent'):
                            t_note_data = {}
                            t_note_data['key'] = t_ableton_note_key
                            t_note_data['position'] = float(x_track_MidiClip_MNE.get('Time'))*4
                            t_note_data['duration'] = float(x_track_MidiClip_MNE.get('Duration'))*4
                            t_note_data['vol'] = float(x_track_MidiClip_MNE.get('Velocity'))/100
                            t_note_data['off_vol'] = float(x_track_MidiClip_MNE.get('OffVelocity'))/100
                            t_note_data['probability'] = float(x_track_MidiClip_MNE.get('Probability'))
                            t_note_data['enabled'] = ['false','true'].index(x_track_MidiClip_MNE.get('IsEnabled'))
                            note_id = int(x_track_MidiClip_MNE.get('NoteId'))
                            t_notes[note_id] = t_note_data

                    x_track_MidiClip_NES = x_track_MidiClip_Notes.findall('PerNoteEventStore')[0]
                    x_track_MidiClip_NES_EL = x_track_MidiClip_NES.findall('EventLists')[0]

                    for x_note_nevent in x_track_MidiClip_NES_EL.findall('PerNoteEventList'):
                        auto_note_id = int(x_note_nevent.get('NoteId'))
                        auto_note_cc = int(x_note_nevent.get('CC'))
                        t_notes[auto_note_id]['notemod'] = {}
                        t_notes[auto_note_id]['notemod']['auto'] = {}

                        if auto_note_cc == -2:
                            t_notes[auto_note_id]['notemod']['auto']['pitch'] = []
                            cvpj_noteauto_pitch = t_notes[auto_note_id]['notemod']['auto']['pitch']
                            x_note_nevent_ev = x_note_nevent.findall('Events')[0]

                            for ableton_point in x_note_nevent_ev.findall('PerNoteEvent'):
                                ap_pos = float(ableton_point.get('TimeOffset'))*4
                                ap_val = float(ableton_point.get('Value'))/170
                                cvpj_noteauto_pitch.append({'position': ap_pos, 'value': ap_val})

                    for t_note in t_notes:
                        cvpj_placement['notelist'].append(t_notes[t_note])

                    #for value in ["CurrentStart", "CurrentEnd", "StartRelative", "LoopStart", "LoopEnd"]:
                    #    print(get_value(x_track_MidiClip, 'CurrentEnd', 0).ljust(20), end=' ')
                    #print()

                    tracks.r_pl_notes(cvpj_l, track_id, cvpj_placement)  

            if tracktype == 'AudioTrack':
                tracks.r_create_audio(cvpj_l, track_id, {})
                tracks.r_basicdata(cvpj_l, track_id, track_name, track_color, track_vol, track_pan)
                tracks.r_pl_audio(cvpj_l, track_id, [])
                x_track_MainSequencer = x_track_DeviceChain.findall('MainSequencer')[0]
                x_track_Sample = x_track_MainSequencer.findall('Sample')[0]
                x_track_ArrangerAutomation = x_track_Sample.findall('ArrangerAutomation')[0]
                x_track_Events = x_track_ArrangerAutomation.findall('Events')[0]
                x_track_AudioClips = x_track_Events.findall('AudioClip')
                audiorate = 1
                for x_track_AudioClip in x_track_AudioClips:

                    t_CurrentStart = float(get_value(x_track_AudioClip, 'CurrentStart', 0))
                    t_CurrentEnd = float(get_value(x_track_AudioClip, 'CurrentEnd', 0))

                    audio_placement_pos = t_CurrentStart*4
                    audio_placement_dur = (t_CurrentEnd-t_CurrentStart)*4
                    audio_placement_name = get_value(x_track_AudioClip, 'Name', '')
                    audio_placement_color = colorlist_one[int(get_value(x_track_AudioClip, 'Color', 0))]
                    audio_placement_muted = ['false','true'].index(get_value(x_track_AudioClip, 'Disabled', 'false'))
                    audio_placement_vol = float(get_value(x_track_AudioClip, 'SampleVolume', 0))

                    audio_placement_warp_on = ['false','true'].index(get_value(x_track_AudioClip, 'IsWarped', 'false'))
                    audio_placement_warp_mode = int(get_value(x_track_AudioClip, 'WarpMode', 0))

                    audio_sampleref = get_sampleref(x_track_AudioClip)
                    audio_sampleref_steps = audio_sampleref['seconds']*8

                    cvpj_placement = {}
                    cvpj_placement['position'] = audio_placement_pos
                    cvpj_placement['duration'] = audio_placement_dur
                    cvpj_placement['name'] = audio_placement_name
                    cvpj_placement['color'] = audio_placement_color
                    cvpj_placement['muted'] = audio_placement_muted
                    cvpj_placement['vol'] = audio_placement_vol

                    cvpj_placement['file'] = audio_sampleref['file']
                    aud_sampledata = audio.get_audiofile_info(audio_sampleref['file'])

                    x_track_AudioClip_loop = x_track_AudioClip.findall('Loop')[0]

                    t_LoopStart = float(get_value(x_track_AudioClip_loop, 'LoopStart', 0))
                    t_LoopEnd = float(get_value(x_track_AudioClip_loop, 'LoopEnd', 0))
                    t_StartRelative = float(get_value(x_track_AudioClip_loop, 'StartRelative', 0))

                    audio_placement_loop_l_start = t_LoopStart*4
                    audio_placement_loop_l_end = t_LoopEnd*4
                    audio_placement_loop_start = t_StartRelative*4
                    audio_placement_loop_on = ['false','true'].index(get_value(x_track_AudioClip_loop, 'LoopOn', 'test'))

                    audio_placement_Fade = ['false','true'].index(get_value(x_track_AudioClip, 'Fade', 'false'))
                    x_track_AudioClip_fades = x_track_AudioClip.findall('Fades')[0]

                    if audio_placement_Fade == 1:
                        cvpj_placement['fade'] = {}
                        cvpj_placement['fade']['in'] = {}
                        cvpj_placement['fade']['in']['duration'] = float(get_value(x_track_AudioClip_fades, 'FadeInLength', 0))*8
                        cvpj_placement['fade']['in']['skew'] = float(get_value(x_track_AudioClip_fades, 'FadeInCurveSkew', 0))
                        cvpj_placement['fade']['in']['slope'] = float(get_value(x_track_AudioClip_fades, 'FadeInCurveSlope', 0))
                        cvpj_placement['fade']['out'] = {}
                        cvpj_placement['fade']['out']['duration'] = float(get_value(x_track_AudioClip_fades, 'FadeOutLength', 0))*8
                        cvpj_placement['fade']['out']['skew'] = float(get_value(x_track_AudioClip_fades, 'FadeOutCurveSkew', 0))
                        cvpj_placement['fade']['out']['slope'] = float(get_value(x_track_AudioClip_fades, 'FadeOutCurveSlope', 0))

                    cvpj_placement['audiomod'] = {}
                    cvpj_audiomod = cvpj_placement['audiomod']

                    if audio_placement_warp_on == 1:
                        cvpj_audiomod['stretch_method'] = 'warp'
                        cvpj_audiomod['stretch_params'] = {}
                        if audio_placement_warp_mode == 0:
                            cvpj_audiomod['stretch_algorithm'] = 'ableton_beats'
                            cvpj_audiomod['stretch_params']['TransientResolution'] = int(get_value(x_track_AudioClip, 'TransientResolution', 6))
                            cvpj_audiomod['stretch_params']['TransientLoopMode'] = int(get_value(x_track_AudioClip, 'TransientLoopMode', 2))
                            cvpj_audiomod['stretch_params']['TransientEnvelope'] = int(get_value(x_track_AudioClip, 'TransientEnvelope', 100))
                        if audio_placement_warp_mode == 1:
                            cvpj_audiomod['stretch_algorithm'] = 'ableton_tones'
                            cvpj_audiomod['stretch_params']['GranularityTones'] = float(get_value(x_track_AudioClip, 'GranularityTones', 30))
                        if audio_placement_warp_mode == 2:
                            cvpj_audiomod['stretch_algorithm'] = 'ableton_texture'
                            cvpj_audiomod['stretch_params']['GranularityTexture'] = float(get_value(x_track_AudioClip, 'GranularityTexture', 71.328125))
                            cvpj_audiomod['stretch_params']['FluctuationTexture'] = float(get_value(x_track_AudioClip, 'FluctuationTexture', 27.34375))
                        if audio_placement_warp_mode == 3:
                            cvpj_audiomod['stretch_algorithm'] = 'resample'
                        if audio_placement_warp_mode == 4:
                            cvpj_audiomod['stretch_algorithm'] = 'ableton_complex'
                        if audio_placement_warp_mode == 6:
                            cvpj_audiomod['stretch_algorithm'] = 'stretch_complexpro'
                            cvpj_audiomod['stretch_params']['ComplexProFormants'] = float(get_value(x_track_AudioClip, 'ComplexProFormants', 100))
                            cvpj_audiomod['stretch_params']['ComplexProEnvelope'] = int(get_value(x_track_AudioClip, 'ComplexProEnvelope', 120))

                        x_track_AudioClip_WarpMarkers_bef = x_track_AudioClip.findall('WarpMarkers')[0]
                        x_track_AudioClip_WarpMarkers = x_track_AudioClip_WarpMarkers_bef.findall('WarpMarker')
                        t_warpmarkers = []
                        for x_track_AudioClip_WarpMarker in x_track_AudioClip_WarpMarkers:
                            t_warpmarker = {}
                            t_warpmarker['pos'] = float(x_track_AudioClip_WarpMarker.get('BeatTime'))*4
                            t_warpmarker['pos_real'] = float(x_track_AudioClip_WarpMarker.get('SecTime'))
                            onedur = t_warpmarker['pos_real']/audio_sampleref['seconds']
                            t_warpmarkers.append(t_warpmarker)
                        
                        cvpj_audiomod['stretch_data'] = t_warpmarkers
                        
                        #cvpj_stretch['time'] = {}
                        #cvpj_stretch['time']['type'] = 'none'
                        #cvpj_stretch['time']['data'] = {}

                        #if len(t_warpmarkers) == 2:
                        #    t_warpmarker_last = t_warpmarkers[-1]
                        #    cvpj_stretch['time']['type'] = 'rate_timed'
                        #    audiorate = ((t_warpmarker_last['pos']/8)/t_warpmarker_last['pos_real'])*(120/tempo)
                        #    cvpj_stretch['time']['data']['rate'] = audiorate

                        #if len(t_warpmarkers) >= 3:
                        #    del t_warpmarkers[-1] 
                        #    t_warpmarker_last = t_warpmarkers[-1]
                        #    cvpj_stretch['time']['type'] = 'rate_timed'
                        #    audiorate = (t_warpmarker_last['pos']/audio_sampleref_steps)*(120/tempo)
                        #    cvpj_stretch['time']['data']['rate'] = audiorate

                        #print(cvpj_stretch['time']['data']['rate'])

                    else:
                        cvpj_audiomod['stretch_method'] = None

                    audio_placement_PitchCoarse = float(get_value(x_track_AudioClip, 'PitchCoarse', 0))
                    audio_placement_PitchFine = float(get_value(x_track_AudioClip, 'PitchFine', 0))
                    cvpj_audiomod['pitch'] = audio_placement_PitchCoarse + audio_placement_PitchFine/100

                    #for value in ["CurrentStart", "CurrentEnd", "StartRelative", "LoopStart", "LoopEnd"]:
                    #    print(str(get_value(x_track_AudioClip, value, 0)).ljust(20), end=' ')
                    #print()

                    if audio_placement_warp_on == False:
                        if audio_placement_loop_on == 0:
                            cvpj_placement['cut'] = {}
                            cvpj_placement['cut']['type'] = 'cut'
                            data_values.time_from_seconds(cvpj_placement['cut'], 'start', False, audio_placement_loop_l_start/4, 1)
                            data_values.time_from_seconds(cvpj_placement['cut'], 'end', False, audio_placement_loop_l_end/4, 1)
                    else:
                        if audio_placement_loop_on == 0:
                            cvpj_placement['cut'] = {}
                            cvpj_placement['cut']['type'] = 'cut'
                            data_values.time_from_seconds(cvpj_placement['cut'], 'start', True, audio_placement_loop_l_start/8, 1)
                            data_values.time_from_seconds(cvpj_placement['cut'], 'end', True, audio_placement_loop_l_end/8, 1)
                        else:
                            cvpj_placement['cut'] = {}
                            cvpj_placement['cut']['type'] = 'loop'
                            data_values.time_from_steps(cvpj_placement['cut'], 'start', False, audio_placement_loop_start, 1)
                            data_values.time_from_steps(cvpj_placement['cut'], 'loopstart', False, audio_placement_loop_l_start, 1)
                            data_values.time_from_steps(cvpj_placement['cut'], 'loopend', False, audio_placement_loop_l_end, 1)

                    #print(cvpj_placement['cut'])

                    #if 'cut' in cvpj_placement:
                    #    print(cvpj_placement['cut'])

                    tracks.r_pl_audio(cvpj_l, track_id, cvpj_placement)  

            sendcount = 1
            for track_sendholder in track_sendholders:
                sendid = track_sendholder.get('Id')
                sendlevel = get_param(track_sendholder, 'Send', 'float', 0)
                tracks.r_add_send(cvpj_l, track_id, 'return_'+str(sendid), sendlevel, None)
                sendcount += 1

            if tracktype == 'ReturnTrack':
                cvpj_returntrackid = 'return_'+str(returnid)
                tracks.r_add_return(cvpj_l, ['master'], cvpj_returntrackid)
                tracks.r_add_return_basicdata(cvpj_l, ['master'], cvpj_returntrackid, track_name, track_color, track_vol, track_pan)
                returnid += 1

        return json.dumps(cvpj_l)

