# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import io
import os
import zipfile
import math
import lxml.etree as ET
from functions import placements
from functions import plugins
from functions import data_values
from functions import params
from functions import audio
from functions import auto
from functions import notelist_data
from functions import song
from functions import xtramath
from functions_plugin import synth_nonfree_values
from functions_tracks import auto_nopl
from functions_tracks import tracks_r

id_out_num = 10000
devid_out_num = 30000
audioidnum = 0

def getid(): 
    global id_out_num
    id_out_num += 1
    return id_out_num

def device_getid(): 
    global devid_out_num
    devid_out_num += 1
    return devid_out_num

def addsample(zip_amped, filepath): 
    global audioidnum
    global audio_id
    outnum = None
    filebasename = os.path.basename(filepath)
    if filebasename not in audio_id:
        audio_id[filebasename] = audioidnum
        if os.path.exists(filepath):
            filetype = filebasename.split('.')[1]
            if filetype in ['wav']: zip_amped.write(filepath, str(audioidnum))
            else: zip_amped.writestr(str(audioidnum), audio.convert_to_wav(filepath))
            outnum = audioidnum
            audioidnum += 1
    else:
        outnum = audio_id[filebasename]
    return outnum

def eq_calc_q(band_type, q_val):
    if band_type in ['low_pass', 'high_pass']: q_val = xtramath.logpowmul(q_val, 0.5) if q_val != 0 else q_val
    if band_type in ['peak']: q_val = xtramath.logpowmul(q_val, -1) if q_val != 0 else q_val
    return q_val

def amped_maketrack(): 
    amped_trackdata = {}
    amped_trackdata["id"] = getid()
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

def amped_makeregion(position, duration, offset): 
    amped_region = {}
    amped_region["id"] = getid()
    amped_region["position"] = position/4
    amped_region["length"] = duration/4
    amped_region["offset"] = offset/4
    amped_region["loop"] = 0
    amped_region["clips"] = []
    amped_region["midi"] = {"notes": [], "events": [], "chords": []}
    amped_region["name"] = ""
    amped_region["color"] = "mint"
    return amped_region

def amped_makedevice(className, label): 
    amped_device = {}
    amped_device["id"] = device_getid()
    amped_device["className"] = className
    amped_device["label"] = label
    amped_device["params"] = []
    amped_device["preset"] = {}
    amped_device["bypass"] = False
    return amped_device

def copyauto_cvpj_to_amped(deviceid, paramid, autoloc, paramtype, minval, maxval):
    cvpj_data = auto_nopl.getpoints(cvpj_l, autoloc)
    out_auto = []
    if cvpj_data: out_auto += [create_autodata(deviceid, paramid, cvpj_data, paramtype, minval, maxval)]
    return out_auto

def copyauto_cvpj_to_amped_addmul(deviceid, paramid, autoloc, paramtype, minval, maxval, addval, mulval):
    cvpj_data = auto_nopl.getpoints(cvpj_l, autoloc)
    out_auto = []
    if cvpj_data: 
        for point in cvpj_data: point['value'] = (point['value']+addval)*mulval
        out_auto += [create_autodata(deviceid, paramid, cvpj_data, paramtype, minval, maxval)]
    return out_auto

def create_autodata(deviceid, paramid, cvpj_points, paramtype, minval, maxval):
    amped_param = {}
    amped_param['param'] = {"deviceId": deviceid, "name": paramid}
    amped_param['points'] = cvpjauto_to_ampedauto(cvpj_points, minval, maxval)
    if paramtype == 'float': 
        amped_param['spec'] = {"type": "numeric", "min": minval, "max": maxval, "curve": 0, "step": 0}
    if paramtype == 'int': 
        amped_param['spec'] = {"type": "numeric", "min": minval, "max": maxval, "curve": 0, "step": 1}
    return amped_param


def do_idparams(cvpj_plugindata, pluginid, deviceid, amped_auto):
    paramout = []
    paramlist = cvpj_plugindata.param_list()
    for paramnum in range(len(paramlist)):
        paramid = paramlist[paramnum]
        paramdata = cvpj_plugindata.param_get_minmax(paramid, 0)
        ampedpid = paramid.replace('__', '/')
        cvpj_autodata = auto_nopl.getpoints(cvpj_l, ['plugin', pluginid, paramid])
        if cvpj_autodata != None:
            amped_auto.append(
                create_autodata(deviceid, ampedpid, cvpj_autodata, ampedpid, paramdata[3], paramdata[4])
                )

        paramout.append({"id": paramnum, "name": ampedpid, "value": paramdata[0]})
    return paramout

def amped_parse_effects(fxchain_audio, amped_auto):
    outdata = []
    for pluginid in fxchain_audio:
        cvpj_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)
        plugtype = cvpj_plugindata.type_get()
        fx_on, fx_wet = cvpj_plugindata.fxdata_get()

        fx_on = not fx_on

        out_auto = []

        if plugtype == ['universal', 'delay-c']:
            d_time_type = cvpj_plugindata.dataval_get('time_type', 'seconds')
            d_time = cvpj_plugindata.dataval_get('time', 1)
            d_wet = cvpj_plugindata.dataval_get('wet', fx_wet)
            d_feedback = cvpj_plugindata.dataval_get('feedback', 0.0)
            devicedata = amped_makedevice('Delay', 'Delay')

            device_params = []
            if d_time_type == 'seconds':
                device_params.append({'id': 0, 'name': 'time', 'value': d_time})

            if d_time_type == 'steps':
                device_params.append({'id': 0, 'name': 'time', 'value': (d_time/8)*((amped_bpm)/120) })

            device_params.append({'id': 1, 'name': 'fb', 'value': d_feedback})
            device_params.append({'id': 2, 'name': 'mix', 'value': d_wet})
            device_params.append({'id': 3, 'name': 'damp', 'value': 0})
            device_params.append({'id': 4, 'name': 'cross', 'value': 0})
            device_params.append({'id': 5, 'name': 'offset', 'value': 0})
            devicedata['bypass'] = fx_on
            devicedata['params'] = device_params
            outdata.append(devicedata)

        elif plugtype[0] == 'native-amped':

            if plugtype[1] in ["Amp Sim Utility", 'Clean Machine', 'Distortion Machine', 'Metal Machine']:
                devicedata = amped_makedevice('WAM', 'Amp Sim Utility')
                devicedata['bypass'] = fx_on
                if plugtype[1] == "Amp Sim Utility": wamClassName = "WASABI_SC.Utility"
                if plugtype[1] == "Clean Machine": wamClassName = 'WASABI_SC.CleanMachine'
                if plugtype[1] == "Distortion Machine": wamClassName = 'WASABI_SC.DistoMachine'
                if plugtype[1] == "Metal Machine": wamClassName = 'WASABI_SC.MetalMachine'
                devicedata['wamClassName'] = wamClassName
                devicedata['wamPreset'] = cvpj_plugindata.dataval_get('data', '{}')
                outdata.append(devicedata)

            elif plugtype[1] in ['BitCrusher', 'Chorus', 
        'CompressorMini', 'Delay', 'Distortion', 'Equalizer', 
        'Flanger', 'Gate', 'Limiter', 'LimiterMini', 'Phaser', 
        'Reverb', 'Tremolo', 'Vibrato', 'Compressor', 'Expander', 'EqualizerPro']:
                classname = plugtype[1]
                classlabel = plugtype[1]
                if classname == 'CompressorMini': classlabel = 'Equalizer Mini'
                if classname == 'Equalizer': classlabel = 'Equalizer Mini'
                if classname == 'LimiterMini': classlabel = 'Limiter Mini'
                if classname == 'EqualizerPro': classlabel = 'Equalizer'
                devicedata = amped_makedevice(classname, classlabel)
                deviceid = devicedata['id']

                devicedata['bypass'] = fx_on
                devicedata['params'] = do_idparams(cvpj_plugindata, pluginid, deviceid, out_auto)
                outdata.append(devicedata)
        
        if amped_auto != None: amped_auto += out_auto

    return outdata

def amped_makeparam(i_id, i_name, i_value):
    return {"id": i_id, "name": i_name, "value": i_value}

def cvpjauto_to_ampedauto(autopoints, i_min, i_max):
    ampedauto = []
    for autopoint in autopoints:
        value = xtramath.between_to_one(i_min, i_max, autopoint['value'])
        ampedauto.append({"pos": autopoint['position']/4, "value": value})
    return ampedauto

class output_cvpj_f(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Amped Studio'
    def getshortname(self): return 'amped'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'track_hybrid': True,
        'auto_nopl': True,
        'placement_audio_stretch': ['rate']
        }
    def getsupportedplugformats(self): return ['vst2', 'midi']
    def getsupportedplugins(self): return ['sampler:single', 'midi']
    def getfileextension(self): return 'zip'
    def parse(self, convproj_json, output_file):
        global audio_id
        global cvpj_l
        global amped_bpm
        global europa_vals

        europa_vals = synth_nonfree_values.europa_valnames()

        cvpj_l = json.loads(convproj_json)
        audio_id = {}

        zip_bio = io.BytesIO()
        zip_amped = zipfile.ZipFile(zip_bio, mode='w', compresslevel=None)

        amped_bpm = int(params.get(cvpj_l, [], 'bpm', 120)[0])
        amped_numerator, amped_denominator = song.get_timesig(cvpj_l)

        amped_tracks = []
        amped_filenames = {}

        for cvpj_trackid, cvpj_trackdata, track_placements in tracks_r.iter(cvpj_l):
            amped_trackdata = amped_maketrack()
            amped_trackdata["name"] = cvpj_trackdata['name'] if 'name' in cvpj_trackdata else ''
            amped_trackdata["pan"] = params.get(cvpj_trackdata, [], 'pan', 0)[0]
            amped_trackdata["volume"] = params.get(cvpj_trackdata, [], 'vol', 1.0)[0]
            amped_trackdata["mute"] = not params.get(cvpj_trackdata, [], 'on', True)[0]
            amped_trackdata["solo"] = bool(params.get(cvpj_trackdata, [], 'solo', False)[0])

            inst_supported = False

            if 'instdata' in cvpj_trackdata:
                cvpj_instadata = cvpj_trackdata['instdata']
                pluginid = cvpj_instadata['pluginid'] if 'pluginid' in cvpj_instadata else None
                if pluginid != None:
                    cvpj_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)
                    plugtype = cvpj_plugindata.type_get()

                    if plugtype[0] == 'native-amped':

                        if plugtype[1] in ['Augur', 'OBXD', 'Dexed']:
                            inst_supported = True
                            devicedata = amped_makedevice('WAM', plugtype[1])
                            if plugtype[1] == "Augur": wamClassName = 'AUGUR'
                            if plugtype[1] == "OBXD": wamClassName = 'OBXD'
                            if plugtype[1] == "Dexed": wamClassName = 'DEXED'
                            devicedata['wamClassName'] = wamClassName
                            devicedata['wamPreset'] = cvpj_plugindata.dataval_get('data', '{}')
                            amped_trackdata["devices"].append(devicedata)

                        if plugtype[1] in ['Volt', 'VoltMini', 'Granny']:
                            inst_supported = True
                            if plugtype[1] == "Volt": devicedata = amped_makedevice('Volt', 'VOLT')
                            if plugtype[1] == "VoltMini": devicedata = amped_makedevice('VoltMini', 'VOLT Mini')
                            if plugtype[1] == "Granny": devicedata = amped_makedevice('Granny', 'Granny')
                            deviceid = devicedata['id']
                            devicedata['params'] = do_idparams(cvpj_plugindata, pluginid, deviceid, amped_trackdata["automations"])
                            amped_trackdata["devices"].append(devicedata)

                    if plugtype == ['synth-nonfree', 'Europa']:
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
                                eur_value_value = cvpj_plugindata.param_get(cvpj_val_name, 0)[0]
                            else:
                                eur_value_value = cvpj_plugindata.dataval_get(cvpj_val_name, 0)
                                if eur_value_name in ['Curve1','Curve2','Curve3','Curve4','Curve']: eur_value_value = bytes(eur_value_value).hex().upper()

                            europa_value_obj = ET.SubElement(europa_obj, "Value")
                            europa_value_obj.set('property',eur_value_name)
                            europa_value_obj.set('type',eur_value_type)
                            europa_value_obj.text = str(eur_value_value)
                        wamPreset['settings'] = ET.tostring(europa_patch).decode()
                        wamPreset['encodedSampleData'] = cvpj_plugindata.dataval_get('encodedSampleData', [])

                        europa_data['wamPreset'] = json.dumps(wamPreset)

                        amped_trackdata["devices"].append(europa_data)

                    elif plugtype[0] == 'midi':
                        inst_supported = True
                        midi_bank = cvpj_plugindata.dataval_get('bank', 0)
                        midi_patch = cvpj_plugindata.dataval_get('inst', 0)
                        sf2data = amped_makedevice('SF2','GM Player')
                        sf2params = []
                        sf2params.append(amped_makeparam(0, 'patch', 0))
                        sf2params.append(amped_makeparam(1, 'bank', midi_bank))
                        sf2params.append(amped_makeparam(2, 'preset', midi_patch))
                        sf2params.append(amped_makeparam(3, 'gain', 0.75))
                        sf2params.append(amped_makeparam(4, 'omni', 1))
                        sf2data['params'] = sf2params
                        sf2data['sf2Preset'] = {"bank": midi_bank, "preset": midi_patch, "name": ""}
                        amped_trackdata["devices"].append(sf2data)

                    elif plugtype == ['vst2', 'win']:
                        inst_supported = True
                        vstcondata = amped_makedevice('VSTConnection',"VST/Remote Beta")
                        vstdatatype = cvpj_plugindata.dataval_get('datatype', '')
                        if vstdatatype == 'chunk':
                            vstcondata['pluginPath'] = cvpj_plugindata.dataval_get('path', 'path')
                            vstcondata['pluginState'] = cvpj_plugindata.rawdata_get_b64()
                        amped_trackdata["devices"].append(vstcondata)

            if inst_supported == False:
                sf2data = amped_makedevice('SF2','GM Player')
                sf2params = []
                sf2params.append(amped_makeparam(0, 'patch', 0))
                sf2params.append(amped_makeparam(1, 'bank', 0))
                sf2params.append(amped_makeparam(2, 'preset', 0))
                sf2params.append(amped_makeparam(3, 'gain', 0.75))
                sf2params.append(amped_makeparam(4, 'omni', 1))
                sf2data['params'] = sf2params
                sf2data['sf2Preset'] = {"bank": 0, "preset": 0, "name": ""}
                amped_trackdata["devices"].append(sf2data)

                    #if plugtype == ['sampler', 'single']:
                    #    samplerdata = amped_makedevice('Sampler',"Sampler")
                    #    samplerdata['samplerZones'] = []
                    #    a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = plugins.get_asdr_env(cvpj_l, pluginid, 'vol')

                    #    filepath = cvpj_plugindata.dataval_get('file', '')
                    #    audioid = addsample(zip_amped, filepath)

                    #    samplervalues = {}
                    #    samplervalues["voiceLimit"] = 64
                    #    samplervalues["filter/frequencyHz/min"] = 2600
                    #    samplervalues["filter/frequencyHz/max"] = 20000
                    #    samplervalues["filter/resonanceNorm/min"] = 0.35
                    #    samplervalues["filter/resonanceNorm/max"] = 0.67
                    #    samplervalues["eg/0/attackDurationNorm"] = a_attack/10
                    #    samplervalues["eg/0/attackCurve"] = 0
                    #    samplervalues["eg/0/decayDurationNorm"] = a_decay/10
                    #    samplervalues["eg/0/decayCurve"] = 0
                    #    samplervalues["eg/0/sustainLevelNorm"] = a_sustain
                    #    samplervalues["eg/0/releaseCurve"] = 0
                    #    samplervalues["eg/0/releaseDurationNorm"] = a_release/10
                    #    samplervalues["eg/0/tracksVelocity"] = 1
                    #    samplervalues["eg/0/velocityTracker/input/min"] = 0
                    #    samplervalues["eg/0/velocityTracker/input/max"] = 127

                    #    samplervalues["zone/1/key/max"] = 127
                    #    samplervalues["zone/1/key/root"] = 60
                    #    samplervalues["zone/1/key/min"] = 0
                    #    samplervalues["zone/1/velocity/min"] = 0
                    #    samplervalues["zone/1/velocity/max"] = 127
                    #    samplervalues["zone/1/eg/0/velocityTracker/gain/amount"] = 1
                    #    samplervalues["zone/1/looping/mode"] = 0
                    #    samplervalues["zone/1/looping/release"] = 2
                    #    samplervalues["zone/1/looping/startPositionNorm"] = 0
                    #    samplervalues["zone/1/looping/endPositionNorm"] = 1
                    #    samplervalues["zone/1/looping/crossfadeWidthNorm"] = 0
                    #    samplervalues["zone/1/looping/crossfadeCurve"] = 0

                    #    samplerparams = []
                    #    paramnum = 0
                    #    for name in samplervalues: 
                    #        samplerparams.append(amped_makeparam(paramnum, name, samplervalues[name]))
                    #        paramnum += 1

                    #    samplerdata['params'] = samplerparams
                    #    samplercontentGuid = {}
                    #    samplercontentGuid['userAudio'] = {"exportedId": str(audioid)}
                    #    samplerdata['samplerZones'].append({"id": 1, "contentGuid": samplercontentGuid})
                    #    samplerdata['nextZoneId'] = 1
                    #    amped_trackdata["devices"].append(samplerdata)

            if 'notes' in track_placements: 
                cvpj_noteclips = notelist_data.sort(track_placements['notes'])
                for cvpj_noteclip in cvpj_noteclips:
                    amped_position = cvpj_noteclip['position']
                    amped_duration = cvpj_noteclip['duration']
                    amped_offset = 0
                    if 'cut' in cvpj_noteclip:
                        cutdata = cvpj_noteclip['cut']
                        cuttype = cutdata['type']
                        if cuttype == 'cut': 
                            amped_offset = cutdata['start']/4 if 'start' in cutdata else 0
                    amped_region = amped_makeregion(amped_position, amped_duration, amped_offset*4)

                    amped_notes = []

                    if 'notelist' in cvpj_noteclip:
                        for cvpj_note in cvpj_noteclip['notelist']:
                            if 0 <= cvpj_note['key']+60 <= 128:
                                amped_notes.append({
                                    "position": cvpj_note['position']/4, 
                                    "length": cvpj_note['duration']/4, 
                                    "key": int(cvpj_note['key']+60),
                                    "velocity": cvpj_note['vol']*100 if 'vol' in cvpj_note else 100, 
                                    "channel": 0
                                    })

                    amped_region["midi"]['notes'] = amped_notes

                    amped_trackdata["regions"].append(amped_region)

            if 'audio' in track_placements:
                cvpj_audioclips = notelist_data.sort(track_placements['audio'])
                for cvpj_audioclip in cvpj_audioclips:
                    amped_position = cvpj_audioclip['position']
                    amped_duration = cvpj_audioclip['duration']
                    amped_offset = 0

                    rate = 1

                    if 'cut' in cvpj_audioclip:
                        cutdata = cvpj_audioclip['cut']
                        cuttype = cutdata['type']
                        if cuttype == 'cut': 
                            amped_offset = cutdata['start']/4 if 'start' in cutdata else 0

                    amped_audclip = {}
                    
                    if 'audiomod' in cvpj_audioclip:
                        cvpj_audiomod = cvpj_audioclip['audiomod']
                        amped_audclip['pitchShift'] = int(cvpj_audiomod['pitch']) if 'pitch' in cvpj_audiomod else 0
                        stretch_method = cvpj_audiomod['stretch_method'] if 'stretch_method' in cvpj_audiomod else None
                        stretch_data = cvpj_audiomod['stretch_data'] if 'stretch_data' in cvpj_audiomod else {'rate': 1.0}
                        stretch_rate = stretch_data['rate'] if 'rate' in stretch_data else 1
                        if stretch_method == 'rate_speed': rate = stretch_rate
                        if stretch_method == 'rate_ignoretempo': rate = stretch_rate
                        if stretch_method == 'rate_tempo': rate = stretch_rate*(amped_bpm/120)

                    audioid = None
                    if 'file' in cvpj_audioclip:
                        audioid = addsample(zip_amped, cvpj_audioclip['file'])
                    amped_audclip['contentGuid'] = {}
                    if audioid != None: amped_audclip['contentGuid']['userAudio'] = {"exportedId": audioid}
                    amped_audclip['position'] = 0
                    amped_audclip['gain'] = cvpj_audioclip['vol'] if 'vol' in cvpj_audioclip else 1
                    amped_audclip['length'] = amped_duration+amped_offset
                    amped_audclip['offset'] = amped_offset
                    amped_audclip['stretch'] = 1/rate
                    amped_audclip['reversed'] = False

                    fadeinval = data_values.nested_dict_get_value(cvpj_audioclip, ['fade', 'in', 'duration'])
                    amped_audclip["fadeIn"] = fadeinval if fadeinval != None else 0

                    amped_region = amped_makeregion(amped_position, amped_duration, 0)
                    amped_region["clips"] = [amped_audclip]
                    amped_trackdata["regions"].append(amped_region)

                for autoname in [['vol','volume'], ['pan','pan']]:
                    autopoints = auto_nopl.getpoints(cvpj_l, ['track',cvpj_trackid,autoname[0]])
                    if autopoints != None: 
                        ampedauto = cvpjauto_to_ampedauto(auto.remove_instant(autopoints, 0, False), 0, 1)
                        amped_trackdata["automations"].append({"param": autoname[1], "points": ampedauto})

            if 'chain_fx_audio' in cvpj_trackdata:
                amped_effects = amped_parse_effects(cvpj_trackdata['chain_fx_audio'], amped_trackdata["automations"])
                for amped_effect in amped_effects:
                    amped_trackdata["devices"].append(amped_effect)

            amped_tracks.append(amped_trackdata)

        for aid in audio_id:
            amped_filenames[audio_id[aid]] = aid

        amped_out = {}
        amped_out["fileFormat"] = "AMPED SONG v1.3"
        amped_out["createdWith"] = "nothing"
        amped_out["settings"] = {"deviceDelayCompensation": True}
        amped_out["tracks"] = amped_tracks
        amped_out["masterTrack"] = {}
        amped_out["masterTrack"]['volume'] = 1
        amped_out["masterTrack"]['devices'] = []

        master_volume = 1
        if 'track_master' in cvpj_l: 
            cvpj_master = cvpj_l['track_master']
            amped_out["masterTrack"]['volume'] = data_values.get_value(cvpj_master, 'vol', 1.0)
            if 'chain_fx_audio' in cvpj_master:
                amped_out["masterTrack"]['devices'] = amped_parse_effects(cvpj_master['chain_fx_audio'], None)

        amped_out["workspace"] = {"library":False,"libraryWidth":300,"trackPanelWidth":160,"trackHeight":80,"beatWidth":24,"contentEditor":{"active":False,"trackId":5,"mode":"noteEditor","beatWidth":48,"noteEditorKeyHeight":10,"velocityPanelHeight":90,"velocityPanel":False,"audioEditorVerticalZoom":1,"height":400,"scroll":{"left":0,"top":0},"quantizationValue":0.25,"chordCreator":{"active":False,"scale":{"key":"C","mode":"Major"}}},"trackInspector":True,"trackInspectorTrackId":5,"arrangementScroll":{"left":0,"top":0},"activeTool":"arrow","timeDisplayInBeats":False,"openedDeviceIds":[],"virtualKeyboard":{"active":False,"height":187,"keyWidth":30,"octave":5,"scrollPositions":{"left":0,"top":0}},"xybeatz":{"active":False,"height":350,"zones":[{"genre":"Caribbean","beat":{"bpm":100,"name":"Zouk Electro 2"}},{"genre":"Soul Funk","beat":{"bpm":120,"name":"Defunkt"}},{"genre":"Greatest Breaks","beat":{"bpm":100,"name":"Walk This Way"}},{"genre":"Brazil","beat":{"bpm":95,"name":"Samba Partido Alto 1"}}],"parts":[{"x":0.75,"y":0.75,"gain":1},{"x":0.9,"y":0.2,"gain":1},{"x":0.8,"y":0.45,"gain":1},{"x":0.7,"y":0.7,"gain":1},{"x":0.7,"y":1,"gain":1},{"x":0.5,"y":0.5,"gain":1}],"partId":5,"fullKit":True,"soloPartId":-1,"complexity":50,"zoneId":0,"lastPartId":1},"displayedAutomations":{}}
        
        loop_on, loop_start, loop_end = song.get_loopdata(cvpj_l, 'r')
        amped_out["looping"] = {"active": loop_on, "start": loop_start/4, "end": loop_end/4}
        amped_out["tempo"] = amped_bpm
        amped_out["timeSignature"] = {"num": amped_numerator, "den": amped_denominator}
        amped_out["metronome"] = {"active": False, "level": 1}
        amped_out["playheadPosition"] = 0

        if 'timemarkers' in cvpj_l:
            for timemarkdata in cvpj_l['timemarkers']:
                if 'type' in timemarkdata:
                    if timemarkdata['type'] == 'loop_area':
                        amped_out["looping"] = {"active": True, "start": timemarkdata['position']/4, "end": timemarkdata['end']/4}

        zip_amped.writestr('amped-studio-project.json', json.dumps(amped_out))
        zip_amped.writestr('filenames.json', json.dumps(amped_filenames))
        zip_amped.close()
        open(output_file, 'wb').write(zip_bio.getbuffer())