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
from functions import colors
from functions import xtramath

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
           

def make_automation(autoid, trackid, autoname, stripdevice, trackdevice, autopoints, color, istrack):
    if istrack == True: 
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
    else:
        wt_autoid_AutoTrack = 'DawVert-Master-AutoTrack-'+autoname
        wt_autoid_AutoRec = 'DawVert-Master-AutoRec-'+autoname
        wt_autoid_AutoStrip = 'DawVert-Master-AutoStrip-'+autoname
        wt_autoid_AutoPortalIn = 'DawVert-Master-AutoPortalIn-'+autoname
        wt_autoid_AutoPortalOut = 'DawVert-Master-AutoPortalOut-'+autoname
        wt_autoid_ChanStrip = 'DawVert-Master-ChanStrip-'+autoname
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

    for point in autopoints.iter():
        wt_points.append({"time": point.pos, "value": point.value, "exponent": 1, "lifted": False})

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




def add_fx_device(prev_port, wt_devices, wt_deviceRouting, fxid, fxname, wt_trackid, fxnum, cvpj_fxid, wt_trackid_Instrument):
    wt_fxname = 'DawVert-FX-'+cvpj_fxid
    adddevice_d(wt_devices, wt_fxname, fxname, 'JS', fxid, wt_trackid, 330, 10+(fxnum*100))
    prev_out = wt_deviceRouting[prev_port+'.input']
    wt_deviceRouting[prev_port+'.input'] = wt_fxname+'.output'
    wt_deviceRouting[wt_fxname+'.input'] = wt_trackid_Instrument+'.output'
    return wt_fxname







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
    def getsupportedplugformats(self): return []
    def getsupportedplugins(self): return ['sampler:single']
    def getfileextension(self): return 'zip'
    def parse(self, convproj_obj, output_file):
        global audio_id
        global wt_deviceRouting
        global wt_devices

        convproj_obj.change_timings(1, True)

        audio_id = {}

        wt_tracks = []
        wt_devices = {}
        wt_deviceRouting = {}

        zip_bio = io.BytesIO()
        zip_wt = zipfile.ZipFile(zip_bio, mode='w')

        bpm = convproj_obj.params.get('bpm',120).value
        bpmmul = (bpm/120)

        adddevice_a(wt_devices, 'master', 'Master Out', 'PortalIn', 'Stereo', 'master', 910, 35.75)
        adddevice_b(wt_devices, 'masterBus', 'Master Bus', 'JS', '66cff321-ae21-444d-a5dc-7c428a4fba25', 'master', 10, 10)
        adddevice_b(wt_devices, 'metronome', 'Metronome', 'JS', '2bfdb690-b27e-441e-a2eb-f820b907f78e', 'master', 320, 110)
        adddevice_b(wt_devices, 'masterFader', 'Master Fader', 'JS', '0c1291d9-cc0a-4d2f-949c-81e1c3e25106', 'master', 310, 10)
        wt_devices['masterFader']['inputs'] = {"gain": convproj_obj.track_master.params.get('vol', 1).value}
        adddevice_b(wt_devices, 'auxSum', 'Aux Sum', 'JS', 'ec86ba8c-4336-4856-8a70-cf0a74a4b423', 'master', 610, 10)
        
        wt_deviceRouting["master.input"] = "auxSum.output"
        wt_deviceRouting["masterFader.input"] = "masterBus.output"
        wt_deviceRouting["auxSum.inputs[0]"] = "masterFader.output"
        wt_deviceRouting["auxSum.inputs[1]"] = "metronome.output"

        #for cvpj_trackid, s_trackdata, track_placements in tracks_r.iter(convproj_obj):
        for cvpj_trackid, track_obj in convproj_obj.iter_track():
            wt_trackid = 'DawVert-Track-'+cvpj_trackid
            wt_trackid_MIDIRec = 'DawVert-MIDIRec-'+cvpj_trackid
            wt_trackid_AudioRec = 'DawVert-AudioRec-'+cvpj_trackid
            wt_trackid_ChanStrip = 'DawVert-ChanStrip-'+cvpj_trackid
            wt_trackid_Instrument = 'DawVert-Instrument-'+cvpj_trackid
            wt_trackid_BusSend = 'DawVert-BusSend-'+cvpj_trackid

            if track_obj.type in ['instrument', 'audio']:
                wt_track = {}
                wt_track['id'] = wt_trackid
                wt_track["armed"] = False
                if track_obj.type == 'instrument': wt_track["type"] = "MIDI"
                if track_obj.type == 'audio': wt_track["type"] = "Audio"
                wt_track["name"] = track_obj.visual.name if track_obj.visual.name else ''
                if track_obj.type == 'instrument': wt_track["height"] = 125
                if track_obj.type == 'audio': wt_track["height"] = 160
                wt_track["hasTimelineSelection"] = False
                wt_track["hasHeaderSelection"] = True
                wt_track["gain"] = track_obj.params.get('vol', 1.0).value
                wt_track["balance"] = track_obj.params.get('pan', 0).value
                trackcolor = colors.rgb_float_to_hex(track_obj.visual.color if track_obj.visual.color else [0.6,0.6,0.6])
                if trackcolor == '000000': trackcolor = 'AAAAAA'
                wt_track["color"] = '#'+trackcolor

                print('[output-wavtool] '+wt_track["type"]+' Track: '+wt_track["name"])
                if track_obj.type == 'instrument':
                    adddevice_c(wt_devices, wt_trackid_MIDIRec, 'Track MIDI', 'PortalOut', 'MIDI', wt_trackid, 10, 35.75)
                    adddevice_e(wt_devices, wt_trackid_ChanStrip, 'Channel Strip', 'JS', 'a19792b0-326f-4b82-93a8-2422ffe215b5', wt_trackid, 540, 10, 0.5011872336272722)
                    pluginid = track_obj.inst_pluginid
                    middlenote = track_obj.datavals.get('middlenote', 0)+60


                    inst_supported = False
                    plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)

                    if plugin_found:
                        adsr_obj = plugin_obj.env_asdr_get('vol')

                        if plugin_obj.check_match('sampler', 'single'):
                            inst_supported = True
                            ref_found, sampleref_obj = plugin_obj.sampleref_fileref('sample', convproj_obj)
                            filename = sampleref_obj.fileref.get_path(None, True)

                            if os.path.exists(filename):
                                audiouuid = addsample(zip_wt, filename, True)
                                adddevice_d(wt_devices, wt_trackid_Instrument, 'MonoSampler', 'JS', 'c4888b49-3a72-4b0a-bd4a-a06e9937000a', wt_trackid, 160, 10)
                                adsr_obj = plugin_obj.env_asdr_get('vol')
                                wt_devices[wt_trackid_Instrument]['inputs'] = {
                                          "decay": xtramath.clamp(adsr_obj.decay, 0.001, 32)*48000,
                                          "gain": 1,
                                          "attack": xtramath.clamp(adsr_obj.attack, 0.001, 32)*48000,
                                          "sustain": adsr_obj.sustain,
                                          "release": xtramath.clamp(adsr_obj.release, 0.001, 32)*48000}
                                wt_devices[wt_trackid_Instrument]['constants'] = {'sample1Pitch': middlenote, 'sample1All': audiouuid}

                    if inst_supported == False: 
                        adddevice_d(wt_devices, wt_trackid_Instrument, 'Simple Synth', 'JS', 'd694ef91-e624-404d-8e34-829d9c1c04b3', wt_trackid, 160, 10)
                        if plugin_found:
                            wt_devices[wt_trackid_Instrument]['inputs'] = {
                                  "decay": xtramath.clamp(adsr_obj.decay, 0.001, 32)*48000,
                                  "attack": xtramath.clamp(adsr_obj.attack, 0.001, 32)*48000,
                                  "sustain": adsr_obj.sustain,
                                  "release": xtramath.clamp(adsr_obj.release, 0.001, 32)*48000}

                    adddevice_f(wt_devices, wt_trackid_BusSend, 'Master Bus', 'PortalIn', 'Stereo', wt_trackid, 730, 35.75)
                    wt_deviceRouting[wt_trackid_MIDIRec+'.input'] = wt_trackid+'.output'
                    wt_deviceRouting['masterBus.inputs['+wt_trackid+']'] = wt_trackid_BusSend+'.output'
                    wt_deviceRouting[wt_trackid_ChanStrip+'.input'] = wt_trackid_Instrument+'.output'
                    wt_deviceRouting[wt_trackid_BusSend+'.input'] = wt_trackid_ChanStrip+'.output'
                    wt_deviceRouting[wt_trackid_Instrument+'.input'] = wt_trackid_MIDIRec+'.output'

                if track_obj.type == 'audio':
                    adddevice_c(wt_devices, wt_trackid_AudioRec, 'Track Audio', 'PortalOut', 'Stereo', wt_trackid, 10, 35.75)
                    adddevice_g(wt_devices, wt_trackid_ChanStrip, 'Channel Strip', 'JS', 'a19792b0-326f-4b82-93a8-2422ffe215b5', wt_trackid, 540, 10)
                    adddevice_f(wt_devices, wt_trackid_BusSend, 'Master Bus', 'PortalIn', 'Stereo', wt_trackid, 730, 35.75)
                    wt_deviceRouting[wt_trackid_AudioRec+'.input'] = wt_trackid+'.output'
                    wt_deviceRouting[wt_trackid_ChanStrip+'.input'] = wt_trackid_AudioRec+'.output'
                    wt_deviceRouting[wt_trackid_BusSend+'.input'] = wt_trackid_ChanStrip+'.output'
                    wt_deviceRouting['masterBus.inputs['+wt_trackid+']'] = wt_trackid_BusSend+'.output'
                
                #prev_port = wt_trackid_ChanStrip
                #if 'chain_fx_audio' in s_trackdata: 
                #    numplugs = len(s_trackdata['chain_fx_audio'])
                #    for index, pluginid in enumerate(reversed(s_trackdata['chain_fx_audio'])):
                #        cvpj_plugindata = plugins.cvpj_plugin('cvpj', convproj_obj, pluginid)
                #        prev_port = add_fx_device(
                #            prev_port, wt_devices, wt_deviceRouting, "c2fc8823-c5a4-44c9-ae3f-29e132081462", 
                #            "EQ Band", wt_trackid, (numplugs-index)-1, pluginid, wt_trackid_Instrument
                #            )


                wt_clips = []

                if track_obj.type == 'instrument':
                    for notespl_obj in track_obj.placements.iter_notes():
                        wt_clip = {}
                        wt_clip["name"] = notespl_obj.visual.name if notespl_obj.visual.name else ''
                        wt_clip["color"] = '#'+colors.rgb_float_to_hex(notespl_obj.visual.color) if notespl_obj.visual.color else trackcolor
                        wt_clip["lifted"] = False
                        wt_notes = []
                        for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
                            for t_key in t_keys:
                                if 0 <= t_key+60 <= 128:
                                    wt_note = {}
                                    wt_note['pitch'] = t_key+60
                                    wt_note['start'] = t_pos
                                    wt_note['end'] = t_pos+t_dur
                                    wt_note['lifted'] = False
                                    wt_note['velocity'] = t_vol
                                    wt_notes.append(wt_note)
                        wt_clip["notes"] = wt_notes
                        wt_clip["ccs"] = {}
                        wt_clip["timelineStart"] = notespl_obj.position
                        wt_clip["timelineEnd"] = notespl_obj.position+notespl_obj.duration
                        wt_clip["readStart"] = 0
                        wt_clip["loopStart"] = 0
                        wt_clip["loopEnd"] = notespl_obj.duration

                        if notespl_obj.cut_type != 'none': wt_clip["readStart"] = notespl_obj.cut_data['start'] if 'start' in notespl_obj.cut_data else 0
                        if notespl_obj.cut_type in ['loop', 'loop_off', 'loop_adv']: 
                            wt_clip["loopStart"] = notespl_obj.cut_data['loopstart'] if 'loopstart' in notespl_obj.cut_data else 0
                            wt_clip["loopEnd"] = notespl_obj.cut_data['loopend'] if 'loopend' in notespl_obj.cut_data else notespl_obj.duration
                        if notespl_obj.cut_type == 'cut': wt_clip["loopEnd"] = (notespl_obj.cut_data['start']+notespl_obj.duration)

                        #for x in ["timelineStart", "timelineEnd", "readStart", "loopStart", "loopEnd"]: wt_clip[x] /= 2

                        wt_clip["type"] = "MIDI"
                        wt_clips.append(wt_clip)

                if track_obj.type == 'audio':
                    for audiopl_obj in track_obj.placements.iter_audio():
                        wt_clip = {}
                        wt_clip["name"] = audiopl_obj.visual.name if audiopl_obj.visual.name else ''
                        wt_clip["color"] = '#'+colors.rgb_float_to_hex(audiopl_obj.visual.color) if audiopl_obj.visual.color else trackcolor
                        wt_clip["lifted"] = False
                        wt_clip["ccs"] = {}
                        wt_clip["timelineStart"] = audiopl_obj.position
                        wt_clip["timelineEnd"] = audiopl_obj.position+audiopl_obj.duration
                        wt_clip["readStart"] = 0
                        wt_clip["loopStart"] = 0
                        wt_clip["loopEnd"] = audiopl_obj.duration

                        loopEnabled = False
                        if audiopl_obj.cut_type != 'none': wt_clip["readStart"] = audiopl_obj.cut_data['start'] if 'start' in audiopl_obj.cut_data else 0
                        wt_clip["readStart"] = audiopl_obj.cut_data['start'] if 'start' in audiopl_obj.cut_data else 0
                        if audiopl_obj.cut_type in ['loop', 'loop_off', 'loop_adv']: 
                            loopEnabled = True
                            wt_clip["loopStart"] = audiopl_obj.cut_data['loopstart'] if 'loopstart' in audiopl_obj.cut_data else 0
                            wt_clip["loopEnd"] = audiopl_obj.cut_data['loopend'] if 'loopend' in audiopl_obj.cut_data else audiopl_obj.duration
                        if audiopl_obj.cut_type == 'cut': wt_clip["loopEnd"] = (audiopl_obj.cut_data['start']+audiopl_obj.duration)

                        wt_clip["type"] = "Audio"
                        transpose = 0

                        audiofilename = ''
                        ref_found, sampleref_obj = convproj_obj.get_sampleref(audiopl_obj.sampleref)
                        if ref_found: audiofilename = sampleref_obj.fileref.get_path(None, True)

                        audioBufferId = addsample(zip_wt, audiofilename, False)
                        wt_clip["audioBufferId"] = audioBufferId

                        cvpj_pitch = audiopl_obj.pitch

                        if not audiopl_obj.stretch.is_warped:
                            warprate = audiopl_obj.stretch.rate_tempo if audiopl_obj.stretch.use_tempo else audiopl_obj.stretch.rate
                            if audiopl_obj.stretch.algorithm == 'resample':
                                transpose = (math.log2(warprate)*12)
                            else:
                                dur_seconds = sampleref_obj.dur_sec*warprate
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

                            for warppoint in audiopl_obj.cvpj_audiomod:
                                wt_warp_pos = warppoint[0]/4
                                wt_warp_pos_real = (warppoint[1]/bpmmul)*2
                                warpdata['anchors']["%g" % wt_warp_pos_real] = {"destination": wt_warp_pos, "pinned": False}

                            wt_clip["warp"] = warpdata

                        wt_clip["loopEnabled"] = loopEnabled
                        wt_clip["transpose"] = float(transpose)

                        wt_clips.append(wt_clip)



                wt_track["clips"] = wt_clips
                wt_track["mute"] = not track_obj.params.get('on', True).value
                wt_track["solo"] = bool(track_obj.params.get('solo', False).value)
                wt_track["channelStripId"] = wt_trackid_ChanStrip
                wt_track["monitorInput"] = 1
                
                if track_obj.type == 'instrument': wt_track["input"] = None
                wt_tracks.append(wt_track)

                for autoname in [['vol','gain'],['pan','balance']]:
                    if_found, autopoints = convproj_obj.get_autopoints(['track',cvpj_trackid,autoname[0]])
                    if if_found: 
                        if autoname[0] == 'pan': autopoints.addmul(1, 0.5)
                        autopoints.remove_instant()
                        wt_trackauto = make_automation(autoname[0], cvpj_trackid, autoname[1], wt_trackid_ChanStrip, wt_trackid, autopoints, trackcolor, True)
                        wt_tracks.append(wt_trackauto)

        if_found, mas_cvpjauto_vol = convproj_obj.get_autopoints(['master','vol'])
        if if_found:
            wt_trackauto = make_automation('vol', 'master', 'gain', 'masterFader', 'master', mas_cvpjauto_vol, 'AAAAAA', False)
            wt_tracks.insert(0, wt_trackauto)

        wt_out = {}
        wt_out["id"] = "DawVertConverted-"+str(uuid.uuid4())
        wt_out["composerHasAuthority"] = False
        wt_out["metronome"] = False
        wt_out["midiOverdub"] = True
        wt_out["loopStart"] = 0
        wt_out["loopEnd"] = 0
        wt_out["loopLifted"] = False
        wt_out["loopEnabled"] = False
        wt_out["bpm"] = bpm
        wt_out["beatNumerator"], wt_out["beatDenominator"] = convproj_obj.timesig
        wt_out["name"] = convproj_obj.metadata.name
        wt_out["arrangementFocusCategory"] = "TrackContent"
        wt_out["tracks"] = wt_tracks
        wt_out["timelineSelectionStart"] = 0
        wt_out["timelineSelectionEnd"] = 36
        wt_out["headerAnchorTrackId"] = ('DawVert-Track-'+convproj_obj.track_order[0]) if convproj_obj.track_order else ''
        wt_out["timelineAnchorTrackId"] = ('DawVert-Track-'+convproj_obj.track_order[0]) if convproj_obj.track_order else ''
        wt_out["devices"] = wt_devices
        wt_out["deviceRouting"] = wt_deviceRouting

        wt_out["focusedSignal"] = None
        wt_out["panelTree"] = {"type": "Auto", "size": 1, "units": "fr", "state": None}
        wt_out["focusedTrackId"] = 'DawVert-Track-'+convproj_obj.track_order[0]
        wt_out["countIn"] = False
        wt_out["selectedDeviceId"] = "metronome"

        wt_out["loopStart"] = convproj_obj.loop_start
        wt_out["loopEnd"] = convproj_obj.loop_end
        wt_out["loopEnabled"] = convproj_obj.loop_active

        zip_wt.writestr('WavTool Project.json', json.dumps(wt_out))
        zip_wt.close()
        open(output_file, 'wb').write(zip_bio.getbuffer())

        #with open('WavTool Project.json', "w") as fileout:
        #    json.dump(wt_out, fileout, indent=2)