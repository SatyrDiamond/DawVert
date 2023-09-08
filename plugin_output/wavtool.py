# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import io
import zipfile
import uuid
import lxml.etree as ET
import os
import math
import av
from functions import xtramath
from functions import colors
from functions import data_values
from functions import plugins
from functions import notelist_data
from functions import params
from functions import tracks
from functions import audio
from functions import auto

def adddevice_a(i_dict, i_id, i_name, i_type, i_portalType, i_trackId, i_x, i_y): 
    i_dict[i_id] = {'id': i_id, 'name': i_name, 'type': i_type, 'portalType': i_portalType, 'trackId': i_trackId, 'x': i_x, 'y': i_y}

def adddevice_b(i_dict, i_id, i_name, i_type, i_sourceId, i_trackId, i_x, i_y): 
    i_dict[i_id] = {'id': i_id, 'name': i_name, 'sourceId': i_sourceId, 'trackId': i_trackId, 'x': i_x, 'y': i_y, 'type': i_type}

def adddevice_c(i_dict, i_id, i_name, i_type, i_portalType, i_trackId, i_x, i_y): 
    i_dict[i_id] = {'id': i_id, 'name': i_name, 'type': i_type, 'portalType': i_portalType, 'x': i_x, 'y': i_y, 'trackId': i_trackId}

def adddevice_d(i_dict, i_id, i_name, i_type, i_sourceId, i_trackId, i_x, i_y): 
    i_dict[i_id] = {'name': i_name, 'x': i_x, 'y': i_y, 'id': i_id, 'trackId': i_trackId, 'type': i_type, 'sourceId': i_sourceId}

def adddevice_e(i_dict, i_id, i_name, i_type, i_sourceId, i_trackId, i_x, i_y, ingain): 
    i_dict[i_id] = {'id': i_id, 'name': i_name, 'sourceId': i_sourceId, 'type': i_type, 'x': i_x, 'y': i_y, 'trackId': i_trackId, 'inputs': {'gain': ingain}}

def adddevice_f(i_dict, i_id, i_name, i_type, i_portalType, i_trackId, i_x, i_y): 
    i_dict[i_id] = {'id': i_id, 'name': i_name, 'type': i_type, 'portalType': i_portalType, 'x': i_x, 'y': i_y, 'trackId': i_trackId}

def adddevice_g(i_dict, i_id, i_name, i_type, i_sourceId, i_trackId, i_x, i_y): 
    i_dict[i_id] = {'id': i_id, 'name': i_name, 'sourceId': i_sourceId, 'type': i_type, 'x': i_x, 'y': i_y, 'trackId': i_trackId}

def addsample(zip_wt, filepath, alredyexists): 
    global audio_id
    datauuid = str(uuid.uuid4())
    if alredyexists == False:
        if filepath not in audio_id:
            audio_id[filepath] = datauuid
            if os.path.exists(filepath):
                filename, filetype = os.path.basename(filepath).split('.')

                if datauuid not in zip_wt.namelist():
                    if filetype in ['wav', 'mp3']:
                        zip_wt.write(filepath, datauuid+'.'+filetype)
                    else:
                        zip_wt.writestr(datauuid+'.wav', audio.convert_to_wav(filepath))

                zip_wt.write(filepath, datauuid+'.'+filetype)
            datauuid = audio_id[filepath]
        else:
            datauuid = audio_id[filepath]
    else:
        if os.path.exists(filepath):
            filetype = os.path.basename(filepath).split('.')[1]
            zip_wt.write(filepath, datauuid+'.'+filetype)

    return datauuid
            
def make_automation(autoid, trackid, autoname, stripdevice, trackdevice, autopoints, color): 
    endtext = autoid+'-'+trackid
    wt_autoid_AutoTrack = 'DawVert-AutoTrack-'+endtext
    wt_autoid_AutoRec = 'DawVert-AutoRec-'+endtext
    wt_autoid_AutoStrip = 'DawVert-AutoStrip-'+endtext
    wt_autoid_AutoPortalIn = 'DawVert-AutoPortalIn-'+endtext
    wt_autoid_AutoPortalOut = 'DawVert-AutoPortalOut-'+endtext
    wt_autoid_ChanStrip = 'DawVert-ChanStrip-'+trackid
    adddevice_c(wt_devices, wt_autoid_AutoRec, 'Track Automation', 'PortalOut', 'Mono', wt_autoid_AutoTrack, 10, 35.75)
    adddevice_g(wt_devices, wt_autoid_AutoStrip, 'Channel Strip', 'JS', '689d5a16-8812-4b98-989a-1444069cded3', wt_autoid_AutoTrack, 210, 10)
    adddevice_a(wt_devices, wt_autoid_AutoPortalIn, 'Gain', 'PortalIn', 'Mono', wt_autoid_AutoTrack, 590, 35.75)
    adddevice_a(wt_devices, wt_autoid_AutoPortalOut, 'Gain', 'PortalOut', 'Mono', trackdevice, 10, 85.75)

    wt_deviceRouting[wt_autoid_AutoRec+".input"] = wt_autoid_AutoTrack+".output"
    wt_deviceRouting[wt_autoid_AutoStrip+".input"] = wt_autoid_AutoRec+".output"
    wt_deviceRouting[wt_autoid_AutoPortalOut+".input"] = wt_autoid_AutoPortalIn+".output"
    wt_deviceRouting[stripdevice+"."+autoname] = wt_autoid_AutoPortalOut+".output"
    wt_deviceRouting[wt_autoid_AutoPortalIn+".input"] = wt_autoid_AutoStrip+".output"

    wt_points = []

    for point in autopoints:
        wt_points.append({"time": point['position']/4, "value": point['value'], "exponent": 1, "lifted": False})

    print('[output-wavtool] Automation Track: '+autoname)
    wt_track = {}
    wt_track["id"] = wt_autoid_AutoTrack
    wt_track["armed"] = False
    wt_track["type"] = "Automation"
    wt_track["name"] = autoname
    wt_track["height"] = 60
    wt_track["hasTimelineSelection"] = True
    wt_track["hasHeaderSelection"] = True
    wt_track["gain"] = 1
    wt_track["balance"] = 0
    wt_track["color"] = "#"+color
    wt_track["points"] = wt_points
    wt_track["clips"] = []
    wt_track["mute"] = False
    wt_track["solo"] = False
    wt_track["channelStripId"] = wt_autoid_AutoStrip
    wt_track["monitorInput"] = 0
    wt_track["input"] = None
    wt_track["setting"] = 0
    return wt_track
    #adddevice_c(wt_devices, wt_trackid_AudioRec, 'Track Audio', 'PortalOut', 'Stereo', wt_trackid, 10, 35.75)

class output_wavtool(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Wavtool'
    def getshortname(self): return 'wavtool'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'auto_nopl': True,
        'placement_loop': ['loop', 'loop_off', 'loop_adv'],
        'placement_audio_stretch': ['warp', 'rate']
        }
    def getsupportedplugins(self): return []
    def parse(self, convproj_json, output_file):
        global audio_id
        global wt_deviceRouting
        global wt_devices
        global cvpj_l
        cvpj_l = json.loads(convproj_json)

        cvpj_placements = cvpj_l['track_placements']

        audio_id = {}

        wt_tracks = []
        wt_devices = {}
        wt_deviceRouting = {}

        zip_bio = io.BytesIO()
        zip_wt = zipfile.ZipFile(zip_bio, mode='w')

        bpm = params.get(cvpj_l, [], 'bpm', 120)[0]
        bpmmul = (bpm/120)

        adddevice_a(wt_devices, 'master', 'Master Out', 'PortalIn', 'Stereo', 'master', 910, 35.75)
        adddevice_b(wt_devices, 'masterBus', 'Master Bus', 'JS', '66cff321-ae21-444d-a5dc-7c428a4fba25', 'master', 10, 10)
        adddevice_b(wt_devices, 'metronome', 'Metronome', 'JS', '2bfdb690-b27e-441e-a2eb-f820b907f78e', 'master', 320, 110)
        adddevice_b(wt_devices, 'masterFader', 'Master Fader', 'JS', '0c1291d9-cc0a-4d2f-949c-81e1c3e25106', 'master', 310, 10)
        wt_devices['masterFader']['inputs'] = {"gain": params.get(cvpj_l, [], 'vol', 1)[0]}
        adddevice_b(wt_devices, 'auxSum', 'Aux Sum', 'JS', 'ec86ba8c-4336-4856-8a70-cf0a74a4b423', 'master', 610, 10)
        
        wt_deviceRouting["master.input"] = "auxSum.output"
        wt_deviceRouting["masterFader.input"] = "masterBus.output"
        wt_deviceRouting["auxSum.inputs[0]"] = "masterFader.output"
        wt_deviceRouting["auxSum.inputs[1]"] = "metronome.output"

        if 'track_order' in cvpj_l and 'track_data' in cvpj_l:

            #numtracks = len(cvpj_l['track_order'])
            #print('[output-wavtool] # of Tracks: '+str(numtracks), end=' ')
            #if numtracks <= 6: print('(Free)')
            #else: print('(Pro)')

            for cvpj_trackid in cvpj_l['track_order']:
                s_trackdata = cvpj_l['track_data'][cvpj_trackid]
                tracktype = s_trackdata['type']

                wt_trackid = 'DawVert-Track-'+cvpj_trackid
                wt_trackid_MIDIRec = 'DawVert-MIDIRec-'+cvpj_trackid
                wt_trackid_AudioRec = 'DawVert-AudioRec-'+cvpj_trackid
                wt_trackid_ChanStrip = 'DawVert-ChanStrip-'+cvpj_trackid
                wt_trackid_Instrument = 'DawVert-Instrument-'+cvpj_trackid
                wt_trackid_BusSend = 'DawVert-BusSend-'+cvpj_trackid

                if tracktype in ['instrument', 'audio']:
                    wt_track = {}
                    wt_track['id'] = wt_trackid
                    wt_track["armed"] = False
                    if tracktype == 'instrument': wt_track["type"] = "MIDI"
                    if tracktype == 'audio': wt_track["type"] = "Audio"
                    wt_track["name"] = s_trackdata['name'] if 'name' in s_trackdata else ''
                    if tracktype == 'instrument': wt_track["height"] = 125
                    if tracktype == 'audio': wt_track["height"] = 160
                    wt_track["hasTimelineSelection"] = False
                    wt_track["hasHeaderSelection"] = True
                    wt_track["gain"] = params.get(s_trackdata, [], 'vol', 1.0)[0]
                    wt_track["balance"] = params.get(s_trackdata, [], 'pan', 0)[0]
                    trackcolor = colors.rgb_float_to_hex(s_trackdata['color'] if 'color' in s_trackdata else [0.0,0.0,0.0])
                    if trackcolor == '000000': trackcolor = 'AAAAAA'
                    wt_track["color"] = '#'+trackcolor

                    print('[output-wavtool] '+wt_track["type"]+' Track: '+wt_track["name"])
                    if tracktype == 'instrument':
                        adddevice_c(wt_devices, wt_trackid_MIDIRec, 'Track MIDI', 'PortalOut', 'MIDI', wt_trackid, 10, 35.75)
                        adddevice_e(wt_devices, wt_trackid_ChanStrip, 'Channel Strip', 'JS', 'a19792b0-326f-4b82-93a8-2422ffe215b5', wt_trackid, 350, 10, 0.5011872336272722)
                        pluginid = data_values.nested_dict_get_value(s_trackdata, ['instdata', 'pluginid'])

                        inst_supported = False
                        middlenote = data_values.get_value(s_trackdata, 'middlenote', 0)+60

                        if pluginid != None:
                            plugtype = plugins.get_plug_type(cvpj_l, pluginid)
                            a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = plugins.get_asdr_env(cvpj_l, pluginid, 'vol')
                            if plugtype == ['sampler', 'single']:
                                inst_supported = True
                                filename = plugins.get_plug_dataval(cvpj_l, pluginid, 'file', '')
                                if os.path.exists(filename):
                                    audiouuid = addsample(zip_wt, filename, True)
                                    adddevice_d(wt_devices, wt_trackid_Instrument, 'MonoSampler', 'JS', 'c4888b49-3a72-4b0a-bd4a-a06e9937000a', wt_trackid, 160, 10)
                                    wt_devices[wt_trackid_Instrument]['inputs'] = {
                                              "decay": xtramath.clamp(a_decay, 0.001, 32)*48000,
                                              "gain": 1,
                                              "attack": xtramath.clamp(a_attack, 0.001, 32)*48000,
                                              "sustain": a_sustain,
                                              "release": xtramath.clamp(a_release, 0.001, 32)*48000}
                                    wt_devices[wt_trackid_Instrument]['constants'] = {'sample1Pitch': middlenote, 'sample1All': audiouuid}

                        if inst_supported == False: 
                            adddevice_d(wt_devices, wt_trackid_Instrument, 'Simple Synth', 'JS', 'd694ef91-e624-404d-8e34-829d9c1c04b3', wt_trackid, 160, 10)
                            if pluginid != None:
                                wt_devices[wt_trackid_Instrument]['inputs'] = {
                                      "decay": xtramath.clamp(a_decay, 0.001, 32)*48000,
                                      "attack": xtramath.clamp(a_attack, 0.001, 32)*48000,
                                      "sustain": a_sustain,
                                      "release": xtramath.clamp(a_release, 0.001, 32)*48000}

                        adddevice_f(wt_devices, wt_trackid_BusSend, 'Master Bus', 'PortalIn', 'Stereo', wt_trackid, 530, 35.75)
                        wt_deviceRouting[wt_trackid_MIDIRec+'.input'] = wt_trackid+'.output'
                        wt_deviceRouting['masterBus.inputs['+wt_trackid+']'] = wt_trackid_BusSend+'.output'
                        wt_deviceRouting[wt_trackid_ChanStrip+'.input'] = wt_trackid_Instrument+'.output'
                        wt_deviceRouting[wt_trackid_Instrument+'.input'] = wt_trackid_MIDIRec+'.output'
                        wt_deviceRouting[wt_trackid_BusSend+'.input'] = wt_trackid_ChanStrip+'.output'

                    if tracktype == 'audio':
                        adddevice_c(wt_devices, wt_trackid_AudioRec, 'Track Audio', 'PortalOut', 'Stereo', wt_trackid, 10, 35.75)
                        adddevice_g(wt_devices, wt_trackid_ChanStrip, 'Channel Strip', 'JS', 'a19792b0-326f-4b82-93a8-2422ffe215b5', wt_trackid, 350, 10)
                        adddevice_f(wt_devices, wt_trackid_BusSend, 'Master Bus', 'PortalIn', 'Stereo', wt_trackid, 530, 35.75)
                        wt_deviceRouting[wt_trackid_AudioRec+'.input'] = wt_trackid+'.output'
                        wt_deviceRouting[wt_trackid_ChanStrip+'.input'] = wt_trackid_AudioRec+'.output'
                        wt_deviceRouting[wt_trackid_BusSend+'.input'] = wt_trackid_ChanStrip+'.output'
                        wt_deviceRouting['masterBus.inputs['+wt_trackid+']'] = wt_trackid_BusSend+'.output'

                    wt_clips = []
                    if cvpj_trackid in cvpj_placements and tracktype in ['instrument', 'audio']:
                        if tracktype == 'instrument': cvpj_clips = notelist_data.sort(cvpj_placements[cvpj_trackid]['notes'])
                        if tracktype == 'audio': cvpj_clips = notelist_data.sort(cvpj_placements[cvpj_trackid]['audio'])
                        for cvpj_clip in cvpj_clips:
                            clip_pos = cvpj_clip['position']/4
                            clip_dur = cvpj_clip['duration']/4

                            wt_clip = {}

                            if tracktype == 'instrument':
                                clip_notes = cvpj_clip['notelist']
                                wt_notes = []
                                for clip_note in clip_notes:
                                    wt_note = {}
                                    wt_note['pitch'] = clip_note['key']+60
                                    wt_note['start'] = (clip_note['position'])/4
                                    wt_note['end'] = (clip_note['position']+clip_note['duration'])/4
                                    wt_note['lifted'] = False
                                    wt_note['velocity'] = clip_note['vol'] if 'vol' in clip_note else ''
                                    wt_notes.append(wt_note)

                            loopEnabled = False
                            transpose = 0
                            if tracktype == 'audio':
                                audiofilename = cvpj_clip['file']
                                audioBufferId = addsample(zip_wt, audiofilename, False)
                                wt_clip["audioBufferId"] = audioBufferId

                                if 'audiomod' in cvpj_clip:
                                    cvpj_audiomod = cvpj_clip['audiomod']
                                    stretch_method = cvpj_audiomod['stretch_method'] if 'stretch_method' in cvpj_audiomod else None
                                    stretch_data = cvpj_audiomod['stretch_data'] if 'stretch_data' in cvpj_audiomod else {'rate': 1.0}
                                    stretch_rate = stretch_data['rate'] if 'rate' in stretch_data else 1
                                    stretch_algorithm = cvpj_audiomod['stretch_algorithm'] if 'stretch_algorithm' in cvpj_audiomod else 'resample'
                                    cvpj_pitch = cvpj_audiomod['pitch'] if 'pitch' in cvpj_audiomod else 0

                                    if stretch_method != 'warp':
                                        if stretch_algorithm == 'resample':
                                            if stretch_method == 'rate_speed': transpose = (math.log2(stretch_rate)*12)
                                            if stretch_method == 'rate_tempo': transpose = (math.log2(stretch_rate*bpmmul)*12)
                                        else:
                                            if stretch_method == 'rate_speed': warprate = (stretch_rate)
                                            if stretch_method == 'rate_tempo': warprate = (stretch_rate*bpmmul)
                                            audiodata = audio.get_audiofile_info(audiofilename)
                                            dur_seconds = audiodata['dur_sec']*warprate
                                            warpdata = {}
                                            warpdata['sourceBPM'] = bpm
                                            warpdata['anchors'] = {}
                                            warpdata['enabled'] = True
                                            warpdata['anchors']["0"] = {"destination": 0, "pinned": True}
                                            maxpoints = 32*max(1, math.ceil(dur_seconds/8))

                                            for num in range(int(maxpoints/warprate)):
                                                numpart = (num+1)/maxpoints
                                                warppoint = (dur_seconds*2)*numpart
                                                warpdata['anchors']["%g" % warppoint] = {"destination": warppoint/warprate, "pinned": True}
                                            wt_clip["warp"] = warpdata
                                            transpose = cvpj_pitch

                                    else:
                                        warpdata = {}
                                        warpdata['sourceBPM'] = bpm
                                        warpdata['anchors'] = {}
                                        warpdata['enabled'] = True

                                        for warppoint in stretch_data:
                                            wt_warp_pos = warppoint['pos']/4
                                            wt_warp_pos_real = (warppoint['pos_real']/bpmmul)*2
                                            warpdata['anchors']["%g" % wt_warp_pos_real] = {"destination": wt_warp_pos, "pinned": False}

                                        wt_clip["warp"] = warpdata


                            wt_clip["name"] = cvpj_clip['name'] if 'name' in cvpj_clip else ''
                            plcolor = colors.rgb_float_to_hex(cvpj_clip['color']) if 'color' in cvpj_clip else None
                            if plcolor == None: plcolor = trackcolor
                            wt_clip["color"] = '#'+plcolor
                            wt_clip["lifted"] = False
                            if tracktype == 'instrument': wt_clip["notes"] = wt_notes
                            wt_clip["ccs"] = {}
                            wt_clip["timelineStart"] = clip_pos
                            wt_clip["timelineEnd"] = clip_pos+clip_dur
                            wt_cutnorm = True
                            if 'cut' in cvpj_clip:
                                cutdata = cvpj_clip['cut']
                                cuttype = cutdata['type']
                                if cuttype == 'loop': 
                                    wt_cutnorm = False
                                    wt_clip["readStart"] = cutdata['start']/4 if 'start' in cutdata else 0
                                    wt_clip["loopStart"] = cutdata['loopstart']/4 if 'loopstart' in cutdata else 0
                                    wt_clip["loopEnd"] = cutdata['loopend']/4
                                if cuttype == 'cut': 
                                    wt_cutnorm = False
                                    wt_clip["readStart"] = cutdata['start']/4 if 'start' in cutdata else 0
                                    wt_clip["loopStart"] = 0
                                    wt_clip["loopEnd"] = cutdata['end']/4
                            if wt_cutnorm == True:
                                wt_clip["readStart"] = 0
                                wt_clip["loopStart"] = 0
                                wt_clip["loopEnd"] = clip_dur
                            wt_clip["fadeIn"] = 0
                            wt_clip["fadeOut"] = 0
                            if tracktype == 'instrument': wt_clip["type"] = "MIDI"
                            if tracktype == 'audio': 
                                wt_clip["type"] = "Audio"
                                wt_clip["loopEnabled"] = loopEnabled
                                wt_clip["transpose"] = float(transpose)
                            wt_clips.append(wt_clip)

                    wt_track["clips"] = wt_clips
                    wt_track["mute"] = not params.get(s_trackdata, [], 'on', 1.0)[0]
                    wt_track["solo"] = bool(params.get(s_trackdata, [], 'solo', 1.0)[0])
                    wt_track["channelStripId"] = wt_trackid_ChanStrip
                    wt_track["monitorInput"] = 1
                    
                    if tracktype == 'instrument': wt_track["input"] = None
                    wt_tracks.append(wt_track)

                    for autoname in [['vol','gain'],['pan','balance']]:
                        autopoints = tracks.a_auto_nopl_getpoints(cvpj_l, ['track',cvpj_trackid,autoname[0]])
                        if autopoints != None: 
                            autopoints = auto.remove_instant(autopoints, 0, False)
                            if autoname[0] == 'pan': autopoints = auto.multiply_nopl(autopoints, 1, 0.5)
                            wt_trackauto = make_automation(autoname[0], cvpj_trackid, autoname[1], wt_trackid_ChanStrip, wt_trackid, autopoints, trackcolor)
                            wt_tracks.append(wt_trackauto)


        wt_out = {}
        wt_out["id"] = "projectState-b22f188e-ecb3-4ef5-96af-a41fb18a8660"
        wt_out["composerHasAuthority"] = False
        wt_out["metronome"] = False
        wt_out["midiOverdub"] = True
        wt_out["loopStart"] = 0
        wt_out["loopEnd"] = 0
        wt_out["loopLifted"] = False
        wt_out["loopEnabled"] = False
        wt_out["bpm"] = bpm
        wt_out["beatNumerator"] = cvpj_l['timesig_numerator'] if 'timesig_numerator' in cvpj_l else 4
        wt_out["beatDenominator"] = cvpj_l['timesig_denominator'] if 'timesig_denominator' in cvpj_l else 4
        wt_out["name"] = data_values.nested_dict_get_value(cvpj_l, ['info', 'name'])
        wt_out["arrangementFocusCategory"] = "TrackContent"
        wt_out["tracks"] = wt_tracks
        wt_out["timelineSelectionStart"] = 0
        wt_out["timelineSelectionEnd"] = 36
        wt_out["headerAnchorTrackId"] = 'DawVert-Track-'+cvpj_l['track_order'][0]
        wt_out["timelineAnchorTrackId"] = 'DawVert-Track-'+cvpj_l['track_order'][0]
        wt_out["devices"] = wt_devices
        wt_out["deviceRouting"] = wt_deviceRouting

        wt_out["focusedSignal"] = None
        wt_out["panelTree"] = {"type": "Auto", "size": 1, "units": "fr", "state": None}
        wt_out["focusedTrackId"] = cvpj_l['track_order'][0]
        wt_out["countIn"] = False
        wt_out["selectedDeviceId"] = "metronome"

        if 'timemarkers' in cvpj_l:
            for timemarkdata in cvpj_l['timemarkers']:
                if timemarkdata['type'] == 'loop_area':
                    wt_out["loopStart"] = timemarkdata['position']/4
                    wt_out["loopEnd"] = timemarkdata['end']/4
                    wt_out["loopEnabled"] = True

        zip_wt.writestr('WavTool Project.json', json.dumps(wt_out))
        zip_wt.close()
        open(output_file, 'wb').write(zip_bio.getbuffer())

        #with open('_test.json', "w") as fileout:
        #    json.dump(wt_out, fileout, indent=2)