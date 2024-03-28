# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import io
import os
import zipfile
import math
import lxml.etree as ET
from functions import data_values
from functions import xtramath
from objects import counter
from functions_plugin import synth_nonfree_values

audioidnum = 0

def amped_makeparam(i_id, i_name, i_value): return {"id": i_id, "name": i_name, "value": i_value}

def amped_makeregion(position, duration, offset): 
    amped_region = {}
    amped_region["id"] = counter_id.get()
    amped_region["position"] = position/4
    amped_region["length"] = duration/4
    amped_region["offset"] = offset/4
    amped_region["loop"] = 0
    amped_region["clips"] = []
    amped_region["midi"] = {"notes": [], "events": [], "chords": []}
    amped_region["name"] = ""
    amped_region["color"] = "mint"
    return amped_region

def amped_maketrack(): 
    amped_trackdata = {}
    amped_trackdata["id"] = counter_id.get()
    amped_trackdata["name"] = ""
    amped_trackdata["color"] = "mint"
    amped_trackdata["pan"] = 0
    amped_trackdata["volume"] = 1
    amped_trackdata["mute"] = False
    amped_trackdata["solo"] = False
    amped_trackdata["armed"] = {"mic": False, "keys": False}
    amped_trackdata["regions"] = []
    amped_trackdata["devices"] = []
    amped_trackdata["automations"] = []
    return amped_trackdata

def amped_makedevice(className, label): 
    amped_device = {}
    amped_device["id"] = counter_devid.get()
    amped_device["className"] = className
    amped_device["label"] = label
    amped_device["params"] = []
    amped_device["preset"] = {}
    amped_device["bypass"] = False
    return amped_device

def cvpjauto_to_ampedauto(autopoints, i_min, i_max):
    ampedauto = []
    for autopoint in autopoints.iter():
        value = xtramath.between_to_one(i_min, i_max, autopoint.value)
        ampedauto.append({"pos": autopoint.pos/4, "value": value})
    return ampedauto

def create_autodata(deviceid, paramid, cvpj_points, paramtype, minval, maxval):
    amped_param = {}
    amped_param['param'] = {"deviceId": deviceid, "name": paramid}
    amped_param['points'] = cvpjauto_to_ampedauto(cvpj_points, minval, maxval)
    if paramtype == 'float': amped_param['spec'] = {"type": "numeric", "min": minval, "max": maxval, "curve": 0, "step": 0}
    if paramtype == 'int': amped_param['spec'] = {"type": "numeric", "min": minval, "max": maxval, "curve": 0, "step": 1}
    return amped_param

def do_idparams(convproj_obj, plugin_obj, pluginid, deviceid, amped_auto):
    paramout = []
    paramlist = plugin_obj.params.list()
    for paramnum in range(len(paramlist)):
        paramid = paramlist[paramnum]
        ampedpid = paramid.replace('__', '/')
        param_obj = plugin_obj.params.get(ampedpid, 0)

        ap_f, ap_d = convproj_obj.automation.get(['plugin', pluginid, paramid], 'float')
        if ap_f: print(ap_d)
        if ap_f: 
            if ap_d.u_nopl_points:
                amped_auto.append(create_autodata(deviceid, ampedpid, ap_d.nopl_points, ampedpid, param_obj.min, param_obj.max))

        paramout.append({"id": paramnum, "name": ampedpid, "value": param_obj.value})
    return paramout

def amped_parse_effects(convproj_obj, fxchain_audio, amped_auto):
    outdata = []
    for pluginid in fxchain_audio:
        out_auto = []
        plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
        if plugin_found: 
            fx_on, fx_wet = plugin_obj.fxdata_get()
            fx_on = not fx_on
            if plugin_obj.check_match('universal', 'delay-c'):
                d_time_type = plugin_obj.datavals.get('time_type', 'seconds')
                d_time = plugin_obj.datavals.get('time', 1)
                d_wet = plugin_obj.datavals.get('wet', fx_wet)
                d_feedback = plugin_obj.datavals.get('feedback', 0.0)
                devicedata = amped_makedevice('Delay', 'Delay')

                device_params = []
                if d_time_type == 'seconds': device_params.append({'id': 0, 'name': 'time', 'value': d_time})
                if d_time_type == 'steps': device_params.append({'id': 0, 'name': 'time', 'value': (d_time/8)*((amped_bpm)/120) })
                device_params.append({'id': 1, 'name': 'fb', 'value': d_feedback})
                device_params.append({'id': 2, 'name': 'mix', 'value': d_wet})
                device_params.append({'id': 3, 'name': 'damp', 'value': 0})
                device_params.append({'id': 4, 'name': 'cross', 'value': 0})
                device_params.append({'id': 5, 'name': 'offset', 'value': 0})
                devicedata['bypass'] = fx_on
                devicedata['params'] = device_params
                outdata.append(devicedata)

            if plugin_obj.check_matchmulti('native-amped', ["Amp Sim Utility", 'Clean Machine', 'Distortion Machine', 'Metal Machine']):
                devicedata = amped_makedevice('WAM', 'Amp Sim Utility')
                devicedata['bypass'] = fx_on
                if plugin_obj.plugin_subtype == "Amp Sim Utility": wamClassName = "WASABI_SC.Utility"
                if plugin_obj.plugin_subtype == "Clean Machine": wamClassName = 'WASABI_SC.CleanMachine'
                if plugin_obj.plugin_subtype == "Distortion Machine": wamClassName = 'WASABI_SC.DistoMachine'
                if plugin_obj.plugin_subtype == "Metal Machine": wamClassName = 'WASABI_SC.MetalMachine'
                devicedata['wamClassName'] = wamClassName
                devicedata['wamPreset'] = plugin_obj.datavals.get('data', '{}')
                outdata.append(devicedata)

            if plugin_obj.check_matchmulti('native-amped', ['BitCrusher', 'Chorus', 
        'CompressorMini', 'Delay', 'Distortion', 'Equalizer', 
        'Flanger', 'Gate', 'Limiter', 'LimiterMini', 'Phaser', 
        'Reverb', 'Tremolo', 'Vibrato', 'Compressor', 'Expander', 'EqualizerPro']):
                classname = plugin_obj.plugin_subtype
                classlabel = plugin_obj.plugin_subtype
                if classname == 'CompressorMini': classlabel = 'Equalizer Mini'
                if classname == 'Equalizer': classlabel = 'Equalizer Mini'
                if classname == 'LimiterMini': classlabel = 'Limiter Mini'
                if classname == 'EqualizerPro': classlabel = 'Equalizer'
                devicedata = amped_makedevice(classname, classlabel)
                deviceid = devicedata['id']

                devicedata['bypass'] = fx_on
                devicedata['params'] = do_idparams(convproj_obj, plugin_obj, pluginid, deviceid, out_auto)
                outdata.append(devicedata)
        
        if amped_auto != None: amped_auto += out_auto

    return outdata

class output_amped(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Amped Studio'
    def getshortname(self): return 'amped'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Amped Studio'
        dawinfo_obj.file_ext = 'amped'
        dawinfo_obj.track_lanes = True
        dawinfo_obj.audio_filetypes = ['wav', 'mp3', 'ogg', 'flac']
        dawinfo_obj.placement_cut = True
        dawinfo_obj.auto_types = ['nopl_points']
        dawinfo_obj.track_hybrid = True
        dawinfo_obj.audio_stretch = ['rate']
        dawinfo_obj.audio_nested = True
        dawinfo_obj.plugin_included = ['native-amped', 'midi', 'synth-nonfree:europa', 'sampler:multi']
    def parse(self, convproj_obj, output_file):
        global counter_id
        global counter_devid
        global amped_bpm
        global europa_vals

        convproj_obj.change_timings(4, True)

        counter_id = counter.counter(10000, '')
        counter_devid = counter.counter(30000, '')

        europa_vals = synth_nonfree_values.europa_valnames()

        zip_bio = io.BytesIO()
        zip_amped = zipfile.ZipFile(zip_bio, mode='w', compresslevel=None)

        amped_bpm = int(convproj_obj.params.get('bpm', 120).value)
        amped_numerator, amped_denominator = convproj_obj.timesig

        amped_tracks = []

        amped_out = {}
        amped_out["fileFormat"] = "AMPED SONG v1.3"
        amped_out["createdWith"] = "DawVert"
        amped_out["settings"] = {"deviceDelayCompensation": True}
        amped_out["tracks"] = amped_tracks
        amped_out["masterTrack"] = {}
        amped_out["masterTrack"]['volume'] = convproj_obj.track_master.params.get('vol', 1).value
        amped_out["masterTrack"]['devices'] = amped_parse_effects(convproj_obj, convproj_obj.track_master.fxslots_audio, None)

        audio_id = {}
        amped_filenames = {}
        audioidnum = 0

        for sampleref_id, sampleref_obj in convproj_obj.iter_samplerefs():
            audio_id[sampleref_id] = audioidnum
            filepath = sampleref_obj.fileref.get_path(None, True)
            if os.path.exists(filepath): zip_amped.write(filepath, str(audioidnum))
            amped_filenames[audioidnum] = sampleref_obj.fileref.basename
            audioidnum += 1

        for trackid, track_obj in convproj_obj.iter_track():
            amped_trackdata = amped_maketrack()
            amped_trackdata["name"] = track_obj.visual.name if track_obj.visual.name else ''
            amped_trackdata["pan"] = track_obj.params.get('pan', 0).value
            amped_trackdata["volume"] = track_obj.params.get('vol', 1.0).value
            amped_trackdata["mute"] = not track_obj.params.get('on', True).value
            amped_trackdata["solo"] = bool(track_obj.params.get('solo', False).value)

            inst_supported = False
            plugin_found, plugin_obj = convproj_obj.get_plugin(track_obj.inst_pluginid)
            if plugin_found:

                if plugin_obj.check_matchmulti('native-amped', ['Augur', 'OBXD', 'Dexed']):
                    inst_supported = True
                    devicedata = amped_makedevice('WAM', plugin_obj.plugin_subtype)
                    if plugin_obj.plugin_subtype == "Augur": wamClassName = 'AUGUR'
                    if plugin_obj.plugin_subtype == "OBXD": wamClassName = 'OBXD'
                    if plugin_obj.plugin_subtype == "Dexed": wamClassName = 'DEXED'
                    devicedata['wamClassName'] = wamClassName
                    devicedata['wamPreset'] = plugin_obj.datavals.get('data', '{}')
                    amped_trackdata["devices"].append(devicedata)

                if plugin_obj.check_matchmulti('native-amped', ['Volt', 'VoltMini', 'Granny']):
                    inst_supported = True
                    if plugin_obj.plugin_subtype == "Volt": devicedata = amped_makedevice('Volt', 'VOLT')
                    if plugin_obj.plugin_subtype == "VoltMini": devicedata = amped_makedevice('VoltMini', 'VOLT Mini')
                    if plugin_obj.plugin_subtype == "Granny": devicedata = amped_makedevice('Granny', 'Granny')
                    deviceid = devicedata['id']
                    devicedata['params'] = do_idparams(convproj_obj, plugin_obj, track_obj.inst_pluginid, deviceid, amped_trackdata["automations"])
                    amped_trackdata["devices"].append(devicedata)

                if plugin_obj.check_match('synth-nonfree', 'Europa'):
                    inst_supported = True
                    europa_data = amped_makedevice('WAM','Europa')
                    europa_data['params'] = []
                    europa_data['wamClassName'] = 'Europa'
                    wamPreset = {}
                    wamPreset['patch'] = 'DawVert'
                    europa_patch = ET.Element("JukeboxPatch")
                    europa_name = ET.SubElement(europa_patch, "DeviceNameInEnglish")
                    europa_name.text = "Europa Shapeshifting Synthesizer"
                    europa_prop = ET.SubElement(europa_patch, "Properties")
                    europa_prop.set('deviceProductID','se.propellerheads.Europa')
                    europa_prop.set('deviceVersion','2.0.0f')
                    europa_obj = ET.SubElement(europa_prop, "Object")
                    europa_obj.set('name','custom_properties')
                    for eur_value_name in europa_vals:
                        eur_value_type, cvpj_val_name = europa_vals[eur_value_name]
                        if eur_value_type == 'number':
                            eur_value_value = plugin_obj.params.get(cvpj_val_name, 0).value
                        else:
                            eur_value_value = plugin_obj.datavals.get(cvpj_val_name, '')
                            if eur_value_name in ['Curve1','Curve2','Curve3','Curve4','Curve']: 
                                eur_value_value = bytes(eur_value_value).hex().upper()

                        europa_value_obj = ET.SubElement(europa_obj, "Value")
                        europa_value_obj.set('property',eur_value_name)
                        europa_value_obj.set('type',eur_value_type)
                        europa_value_obj.text = str(eur_value_value)
                    wamPreset['settings'] = ET.tostring(europa_patch).decode()
                    wamPreset['encodedSampleData'] = plugin_obj.datavals.get('encodedSampleData', [])
                    europa_data['wamPreset'] = json.dumps(wamPreset)
                    amped_trackdata["devices"].append(europa_data)

                if plugin_obj.check_match('vst2', 'win'):
                    inst_supported = True
                    vstcondata = amped_makedevice('VSTConnection',"VST/Remote Beta")
                    vstdatatype = plugin_obj.datavals.get('datatype', '')
                    if vstdatatype == 'chunk':
                        vstcondata['pluginPath'] = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
                        vstcondata['pluginState'] = plugin_obj.rawdata_get_b64('chunk')
                    amped_trackdata["devices"].append(vstcondata)

            if not inst_supported:
                midi_found, midi_bank, midi_inst, midi_drum = track_obj.get_midi(convproj_obj)
                o_midi_bank = midi_bank if not midi_drum else midi_bank+128
                o_midi_patch = midi_inst
                sf2data = amped_makedevice('SF2','GM Player')
                sf2params = []
                sf2params.append(amped_makeparam(0, 'patch', 0))
                sf2params.append(amped_makeparam(1, 'bank', midi_bank))
                sf2params.append(amped_makeparam(2, 'preset', midi_inst))
                sf2params.append(amped_makeparam(3, 'gain', 0.75))
                sf2params.append(amped_makeparam(4, 'omni', 1))
                sf2data['params'] = sf2params
                sf2data['sf2Preset'] = {"bank": o_midi_bank, "preset": o_midi_patch, "name": ""}
                amped_trackdata["devices"].append(sf2data)

            for notespl_obj in track_obj.placements.pl_notes:
                amped_offset = 0
                if notespl_obj.cut_type == 'cut':
                    if 'start' in notespl_obj.cut_data: amped_offset = notespl_obj.cut_data['start']
                amped_region = amped_makeregion(notespl_obj.position, notespl_obj.duration, amped_offset)

                amped_notes = []
                notespl_obj.notelist.sort()
                for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
                    for t_key in t_keys:
                        if 0 <= t_key+60 <= 128:
                            amped_notes.append({
                                "position": t_pos/4, 
                                "length": t_dur/4, 
                                "key": int(t_key+60),
                                "velocity": t_vol*100, 
                                "channel": 0
                                })

                amped_region["midi"]['notes'] = amped_notes
                amped_trackdata["regions"].append(amped_region)

            for audiopl_obj in track_obj.placements.pl_audio:
                amped_offset = 0
                if audiopl_obj.cut_type == 'cut':
                    if 'start' in audiopl_obj.cut_data: amped_offset = audiopl_obj.cut_data['start']
                amped_region = amped_makeregion(audiopl_obj.position, audiopl_obj.duration, amped_offset)

                amped_audclip = {}
                amped_audclip['contentGuid'] = {}
                if audiopl_obj.sampleref in audio_id:
                    amped_audclip['contentGuid']['userAudio'] = {"exportedId": audio_id[audiopl_obj.sampleref]}
                amped_audclip['position'] = 0
                amped_audclip['gain'] = audiopl_obj.vol
                amped_audclip['length'] = audiopl_obj.duration
                amped_audclip['offset'] = 0
                amped_audclip['stretch'] = audiopl_obj.stretch.calc_tempo_size
                amped_audclip['pitchShift'] = audiopl_obj.pitch
                amped_audclip['reversed'] = False

                amped_region["clips"] = [amped_audclip]
                amped_trackdata["regions"].append(amped_region)



            amped_trackdata["devices"] += amped_parse_effects(convproj_obj, track_obj.fxslots_audio, amped_trackdata["automations"])
            amped_tracks.append(amped_trackdata)








        amped_out["workspace"] = {"library":False,"libraryWidth":300,"trackPanelWidth":160,"trackHeight":80,"beatWidth":24,"contentEditor":{"active":False,"trackId":5,"mode":"noteEditor","beatWidth":48,"noteEditorKeyHeight":10,"velocityPanelHeight":90,"velocityPanel":False,"audioEditorVerticalZoom":1,"height":400,"scroll":{"left":0,"top":0},"quantizationValue":0.25,"chordCreator":{"active":False,"scale":{"key":"C","mode":"Major"}}},"trackInspector":True,"trackInspectorTrackId":5,"arrangementScroll":{"left":0,"top":0},"activeTool":"arrow","timeDisplayInBeats":False,"openedDeviceIds":[],"virtualKeyboard":{"active":False,"height":187,"keyWidth":30,"octave":5,"scrollPositions":{"left":0,"top":0}},"xybeatz":{"active":False,"height":350,"zones":[{"genre":"Caribbean","beat":{"bpm":100,"name":"Zouk Electro 2"}},{"genre":"Soul Funk","beat":{"bpm":120,"name":"Defunkt"}},{"genre":"Greatest Breaks","beat":{"bpm":100,"name":"Walk This Way"}},{"genre":"Brazil","beat":{"bpm":95,"name":"Samba Partido Alto 1"}}],"parts":[{"x":0.75,"y":0.75,"gain":1},{"x":0.9,"y":0.2,"gain":1},{"x":0.8,"y":0.45,"gain":1},{"x":0.7,"y":0.7,"gain":1},{"x":0.7,"y":1,"gain":1},{"x":0.5,"y":0.5,"gain":1}],"partId":5,"fullKit":True,"soloPartId":-1,"complexity":50,"zoneId":0,"lastPartId":1},"displayedAutomations":{}}
        
        amped_out["looping"] = {"active": convproj_obj.loop_active, "start": convproj_obj.loop_start, "end": convproj_obj.loop_end}
        amped_out["tempo"] = amped_bpm
        amped_out["timeSignature"] = {"num": amped_numerator, "den": amped_denominator}
        amped_out["metronome"] = {"active": False, "level": 1}
        amped_out["playheadPosition"] = 0

        zip_amped.writestr('amped-studio-project.json', json.dumps(amped_out))
        zip_amped.writestr('filenames.json', json.dumps(amped_filenames))
        zip_amped.close()
        open(output_file, 'wb').write(zip_bio.getbuffer())