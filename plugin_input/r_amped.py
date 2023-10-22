# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import song
from functions import colors
from functions import note_data
from functions import plugins
from functions import notelist_data
from functions import placement_data
from functions import data_values
from functions import xtramath
from functions import audio_wav
from functions_plugin import synth_nonfree_values
from functions_tracks import auto_data
from functions_tracks import auto_nopl
from functions_tracks import fxslot
from functions_tracks import trackfx
from functions_tracks import tracks_master
from functions_tracks import tracks_r
import xml.etree.ElementTree as ET
import plugin_input
import json
import os
import struct
import rpp
import base64
import zipfile

amped_colors = {
                'mint': [0.20, 0.80, 0.63],
                'lime': [0.54, 0.92, 0.16],
                'yellow': [0.97, 0.91, 0.11],
                'amber': [1.00, 0.76, 0.33],
                'orange': [0.98, 0.61, 0.38],
                'red': [0.96, 0.38, 0.43],
                'magenta': [0.87, 0.44, 0.96],
                'purple': [0.64, 0.48, 0.96],
                'blue': [0.13, 0.51, 0.96],
                'cyan': [0.20, 0.80, 0.63]
                }

def reaper_color_to_cvpj_color(i_color, isreversed): 
    bytecolors = struct.pack('i', i_color)
    if isreversed == True: return colors.rgb_int_to_rgb_float([bytecolors[0],bytecolors[1],bytecolors[2]])
    else: return colors.rgb_int_to_rgb_float([bytecolors[2],bytecolors[1],bytecolors[0]])

def getsamplefile(filename):
    localpath = os.path.join(projpath, filename)
    if os.path.exists(filename): return filename
    else: return localpath

def do_idparams(paramsdata, pluginid):
    for param in paramsdata:
        plugins.add_plug_param(cvpj_l, pluginid, param['name'], param['value'], 'float', param['name'])

def get_contentGuid(contentGuid):
    if isinstance(contentGuid, dict):
        return os.path.join(samplefolder,amped_filenames[str(contentGuid['userAudio']['exportedId'])])
    else:
        return contentGuid

def encode_devices(amped_tr_devices, trackid):
    for amped_tr_device in amped_tr_devices:
        pluginid = str(amped_tr_device['id'])
        devicetype = [amped_tr_device['className'], amped_tr_device['label']]

        is_instrument = False

        plugins.add_plug_fxvisual(cvpj_l, pluginid, devicetype[1], None)

        if devicetype[0] == 'WAM' and devicetype[1] in ['Augur', 'OBXD', 'Dexed']: 
            is_instrument = True
            plugins.add_plug(cvpj_l, pluginid, 'native-amped', devicetype[1])
            plugins.add_plug_data(cvpj_l, pluginid, 'data', amped_tr_device['wamPreset'])

        elif devicetype[0] == 'WAM' and devicetype[1] == 'Europa': 
            is_instrument = True
            plugins.add_plug(cvpj_l, pluginid, 'synth-nonfree', 'Europa')
            wampreset = amped_tr_device['wamPreset']
            wampreset = json.loads(wampreset)
            europa_xml = ET.fromstring(wampreset['settings'])
            europa_xml_prop = europa_xml.findall('Properties')[0]

            for xmlsub in europa_xml_prop:
                if xmlsub.tag == 'Object':
                    object_name = xmlsub.get('name')
                    for objsub in xmlsub:
                        if objsub.tag == 'Value':
                            value_name = objsub.get('property')
                            value_type = objsub.get('type')
                            value_value = float(objsub.text) if value_type == 'number' else objsub.text

                            cvpj_val_type_name = europa_vals[value_name]
                            if cvpj_val_type_name[0] == 'number': 
                                plugins.add_plug_param(cvpj_l, pluginid, cvpj_val_type_name[1], float(value_value), 'float', value_name)
                            else:
                                if value_name in ['Curve1','Curve2','Curve3','Curve4','Curve']: 
                                    value_value = list(bytes.fromhex(value_value))

                                plugins.add_plug_data(cvpj_l, pluginid, cvpj_val_type_name[1], value_value)

            if 'encodedSampleData' in wampreset:
                europa_sampledata = wampreset['encodedSampleData']
                plugins.add_plug_data(cvpj_l, pluginid, 'encodedSampleData', europa_sampledata)

        elif devicetype == ['Drumpler', 'Drumpler']:
            is_instrument = True
            plugins.add_plug(cvpj_l, pluginid, 'native-amped', 'Drumpler')
            plugins.add_plug_data(cvpj_l, pluginid, 'kit', amped_tr_device['kit'])
            do_idparams(amped_tr_device['params'], pluginid)

        elif devicetype == ['SF2', 'GM Player']:
            is_instrument = True
            value_patch = 0
            value_bank = 0
            value_gain = 0.75
            for param in amped_tr_device['params']:
                paramname, paramval = param['name'], param['value']
                if paramname == 'patch': value_patch = paramval
                if paramname == 'bank': value_bank = paramval
                if paramname == 'gain': value_gain = paramval
            plugins.add_plug_gm_midi(cvpj_l, pluginid, value_bank, value_patch)
            plugins.add_plug_param(cvpj_l, pluginid, 'gain', paramval, 'float', 'Gain')

        elif devicetype == ['Granny', 'Granny']:
            is_instrument = True
            plugins.add_plug(cvpj_l, pluginid, 'native-amped', 'Granny')
            do_idparams(amped_tr_device['params'], pluginid)
            plugins.add_plug_data(cvpj_l, pluginid, 'grannySampleGuid', amped_tr_device['grannySampleGuid'])
            plugins.add_plug_data(cvpj_l, pluginid, 'grannySampleName', amped_tr_device['grannySampleName'])

        elif devicetype == ['Volt', 'VOLT']:
            is_instrument = True
            plugins.add_plug(cvpj_l, pluginid, 'native-amped', 'VOLT')
            do_idparams(amped_tr_device['params'], pluginid)

        elif devicetype == ['VoltMini', 'VOLT Mini']:
            is_instrument = True
            plugins.add_plug(cvpj_l, pluginid, 'native-amped', 'VoltMini')
            do_idparams(amped_tr_device['params'], pluginid)

        elif devicetype == ['Sampler', 'Sampler']:
            is_instrument = True
            samplerdata = {}
            for param in amped_tr_device['params']:
                data_values.nested_dict_add_value(samplerdata, param['name'].split('/'), param['value'])

            amped_tr_device['zonefile'] = {}
            for param in amped_tr_device['samplerZones']:
                amped_tr_device['zonefile'][str(param['id'])] = param['contentGuid']

            plugins.add_plug_multisampler(cvpj_l, pluginid)
            plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "percent")

            samplerdata_voiceLimit = samplerdata['voiceLimit']
            samplerdata_filter = samplerdata['filter']
            samplerdata_eg = samplerdata['eg']
            samplerdata_zone = samplerdata['zone']
            samplerdata_zonefile = amped_tr_device['zonefile']
            
            for samplerdata_zp in samplerdata_zone:
                amped_samp_part = samplerdata_zone[samplerdata_zp]
                cvpj_region = {}
                cvpj_region['file'] = get_contentGuid(samplerdata_zonefile[samplerdata_zp])
                cvpj_region['reverse'] = 0
                cvpj_region['loop'] = {}
                cvpj_region['loop']['enabled'] = 0
                cvpj_region['loop']['points'] = [amped_samp_part['looping']['startPositionNorm'], amped_samp_part['looping']['endPositionNorm']]
                cvpj_region['middlenote'] = amped_samp_part['key']['root']-60
                cvpj_region['r_key'] = [int(amped_samp_part['key']['min'])-60, int(amped_samp_part['key']['max'])-60]
                plugins.add_plug_multisampler_region(cvpj_l, pluginid, cvpj_region)

        elif devicetype == ['EqualizerPro', 'Equalizer']:
            plugins.add_plug(cvpj_l, pluginid, 'universal', 'eq-bands')
            plugins.add_plug_fxdata(cvpj_l, pluginid, not amped_tr_device['bypass'], 1)
            eqdata = {}
            for param in amped_tr_device['params']:
                data_values.nested_dict_add_value(eqdata, param['name'].split('/'), param['value'])

            for bandnum in eqdata['filter']:
                banddata = eqdata['filter'][bandnum]
                bandtype = banddata['type']
                band_res = banddata['q']

                if bandtype == 0: eq_bandtype = 'peak'
                if bandtype == 2: eq_bandtype = 'low_pass'
                if bandtype == 1: eq_bandtype = 'high_pass'
                if bandtype == 3: eq_bandtype = 'low_shelf'
                if bandtype == 4: eq_bandtype = 'high_shelf'
                if eq_bandtype in ['low_pass', 'high_pass']: 
                    band_res = xtramath.logpowmul(band_res, 2) if band_res != 0 else 1
                if eq_bandtype in ['peak']: 
                    band_res = xtramath.logpowmul(band_res, -1) if band_res != 0 else 1

                plugins.add_eqband(cvpj_l, pluginid, int(banddata['active']), banddata['freq'], banddata['gain'], eq_bandtype, band_res, None)

            plugins.add_plug_param(cvpj_l, pluginid, 'gain_out', eqdata['postGain'], 'float', 'Out Gain')

        elif devicetype[0] in ['Compressor', 'Expander']:
            if devicetype[0] == 'Compressor': plugins.add_plug(cvpj_l, pluginid, 'universal', 'compressor')
            if devicetype[0] == 'Expander': plugins.add_plug(cvpj_l, pluginid, 'universal', 'expander')
            plugins.add_plug_fxdata(cvpj_l, pluginid, not amped_tr_device['bypass'], 1)
            for param in amped_tr_device['params']:

                paramname = param['name']
                paramvalue = param['value']
                if paramname == 'preGainDB': plugins.add_plug_param(cvpj_l, pluginid, 'pregain', paramvalue, 'float', 'pregain')
                if paramname == 'ratio': plugins.add_plug_param(cvpj_l, pluginid, 'ratio', paramvalue, 'float', 'ratio')
                if paramname == 'thresholdDB': plugins.add_plug_param(cvpj_l, pluginid, 'threshold', paramvalue, 'float', 'threshold')
                if paramname == 'attackTimeMS': plugins.add_plug_param(cvpj_l, pluginid, 'attack', paramvalue/1000, 'float', 'attack')
                if paramname == 'releaseTimeMS': plugins.add_plug_param(cvpj_l, pluginid, 'release', paramvalue/1000, 'float', 'release')
                if paramname == 'postGainDB': plugins.add_plug_param(cvpj_l, pluginid, 'postgain', paramvalue, 'float', 'postgain')
                if paramname == 'lookaheadTimeMS': plugins.add_plug_param(cvpj_l, pluginid, 'lookahead', paramvalue/1000, 'float', 'lookahead')
                if paramname == 'softKneeWidth': plugins.add_plug_param(cvpj_l, pluginid, 'knee', paramvalue*6, 'float', 'knee')

                if paramname == 'detectMode': plugins.add_plug_data(cvpj_l, pluginid, 'detect_mode', ('rms' if paramvalue == 1 else 'peak') )
                if paramname == 'circuitMode': plugins.add_plug_data(cvpj_l, pluginid, 'circuit_mode', ('digital' if paramvalue == 1 else 'analog') )

                filter_enabled = False
                filter_cutoff = 44100
                filter_reso = 0
                filter_type = 'lowpass'
                filter_subtype = None

                if paramname == 'filterGainDB': plugins.add_plug_data(cvpj_l, pluginid, 'filter_gain', paramvalue)

                if paramname == 'filterFrequency': filter_cutoff = paramvalue
                if paramname == 'filterQ': filter_reso = paramvalue
                if paramname == 'filterActive': filter_enabled = bool(paramvalue)

                if paramname == 'filterMode':
                    if paramvalue == 0: filter_type = 'lowpass'
                    if paramvalue == 1: filter_type = 'highpass'
                    if paramvalue == 2: filter_type = 'bandpass'

                plugins.add_filter(cvpj_l, pluginid, filter_enabled, filter_cutoff, filter_reso, filter_type, filter_subtype)

        elif devicetype[0] == 'Vibrato':
            plugins.add_plug(cvpj_l, pluginid, 'universal', 'vibrato')
            plugins.add_plug_fxdata(cvpj_l, pluginid, not amped_tr_device['bypass'], 1)
            for param in amped_tr_device['params']:
                paramname = param['name']
                paramvalue = param['value']
                if paramname == 'delayLfoRateHz': plugins.add_plug_param(cvpj_l, pluginid, 'freq', paramvalue, 'float', 'freq')
                if paramname == 'delayLfoDepth': plugins.add_plug_param(cvpj_l, pluginid, 'depth', paramvalue, 'float', 'depth')

        elif devicetype[0] == 'Tremolo':
            plugins.add_plug(cvpj_l, pluginid, 'universal', 'tremolo')
            plugins.add_plug_fxdata(cvpj_l, pluginid, not amped_tr_device['bypass'], 1)
            for param in amped_tr_device['params']:
                paramname = param['name']
                paramvalue = param['value']
                if paramname == 'lfoARateHz': plugins.add_plug_param(cvpj_l, pluginid, 'freq', paramvalue, 'float', 'freq')
                if paramname == 'lfoADepth': plugins.add_plug_param(cvpj_l, pluginid, 'depth', paramvalue, 'float', 'depth')

        elif devicetype[0] == 'BitCrusher':
            plugins.add_plug(cvpj_l, pluginid, 'universal', 'bitcrush')
            fx_wet = 1
            for param in amped_tr_device['params']:
                paramname = param['name']
                paramvalue = param['value']
                if paramname == 'bits': plugins.add_plug_param(cvpj_l, pluginid, 'bits', paramvalue, 'float', 'freq')
                if paramname == 'down': 
                    bits_hz = 100 * 2**(paramvalue*10)
                    plugins.add_plug_param(cvpj_l, pluginid, 'freq', bits_hz, 'float', 'depth')
                if paramname == 'mix': fx_wet = paramvalue
            plugins.add_plug_fxdata(cvpj_l, pluginid, not amped_tr_device['bypass'], fx_wet)



        elif devicetype[0] in ['Chorus',  
        'CompressorMini', 'Delay', 'Distortion', 'Equalizer', 
        'Flanger', 'Gate', 'Limiter', 'LimiterMini', 'Phaser', 
        'Reverb', 'Tremolo']:
            plugins.add_plug(cvpj_l, pluginid, 'native-amped', devicetype[0])
            do_idparams(amped_tr_device['params'], pluginid)

        if is_instrument == True: tracks_r.track_inst_pluginid(cvpj_l, trackid, pluginid)
        else:
            if trackid == None: fxslot.insert(cvpj_l, ['master'], 'audio', pluginid)
            else: fxslot.insert(cvpj_l, ['track', trackid], 'audio', pluginid)

def ampedauto_to_cvpjauto(autopoints):
    ampedauto = []
    for autopoint in autopoints:
        ampedauto.append({"position": autopoint['pos']*4, "value": autopoint['value']})
    return ampedauto

class input_amped(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'amped'
    def getname(self): return 'Amped Studio'
    def gettype(self): return 'r'
    def supported_autodetect(self): return True
    def detect(self, input_file): 
        try:
            zip_data = zipfile.ZipFile(input_file, 'r')
            if 'amped-studio-project.json' in zip_data.namelist(): return True
            else: return False
        except:
            return False
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': [],
        'track_hybrid': True,
        'placement_audio_stretch': ['rate'],
        'placement_audio_nested': True
        }
    def parse(self, input_file, extra_param):
        global cvpj_l
        global samplefolder
        global amped_filenames
        global europa_vals

        europa_vals = synth_nonfree_values.europa_valnames()

        cvpj_l = {}
        samplefolder = extra_param['samplefolder']
        zip_data = zipfile.ZipFile(input_file, 'r')
        amped_project = json.loads(zip_data.read('amped-studio-project.json'))
        amped_filenames = json.loads(zip_data.read('filenames.json'))

        amped_tracks = amped_project['tracks']
        amped_masterTrack = amped_project['masterTrack']
        #encode_devices(amped_masterTrack['devices'], None)
        amped_looping = amped_project['looping']
        amped_tempo = amped_project['tempo']
        amped_timeSignature = amped_project['timeSignature']

        song.add_param(cvpj_l, 'bpm', amped_tempo)
        song.add_timesig(cvpj_l, amped_timeSignature['num'], amped_timeSignature['den'])

        for amped_filename in amped_filenames:
            realfilename = amped_filenames[amped_filename]
            old_file = os.path.join(samplefolder,amped_filename)
            new_file = os.path.join(samplefolder,realfilename)
            if os.path.exists(new_file) == False:
                zip_data.extract(amped_filename, path=samplefolder, pwd=None)
                os.rename(old_file,new_file)

        for amped_track in amped_tracks:
            amped_tr_id = str(amped_track['id'])
            amped_tr_name = amped_track['name']
            amped_tr_color = amped_track['color'] if 'color' in amped_track else 'lime'
            amped_tr_pan = amped_track['pan']
            amped_tr_volume = amped_track['volume']
            amped_tr_mute = amped_track['mute']
            amped_tr_solo = amped_track['solo']
            amped_tr_regions = amped_track['regions']
            amped_tr_devices = amped_track['devices']
            amped_tr_automations = amped_track['automations']

            for amped_tr_automation in amped_tr_automations:
                autoname = amped_tr_automation['param']
                autopoints = auto_nopl.to_pl(ampedauto_to_cvpjauto(amped_tr_automation['points']))
                if autoname == 'volume': auto_data.add_pl(cvpj_l, 'float', ['track',amped_tr_id,'vol'], autopoints)
                if autoname == 'pan': auto_data.add_pl(cvpj_l, 'float', ['track',amped_tr_id,'pan'], autopoints)
                
            tracks_r.track_create(cvpj_l, amped_tr_id, 'hybrid')
            tracks_r.track_visual(cvpj_l, amped_tr_id, name=amped_tr_name, color=amped_colors[amped_tr_color])
            tracks_r.track_param_add(cvpj_l, amped_tr_id, 'vol', amped_tr_volume, 'float')
            tracks_r.track_param_add(cvpj_l, amped_tr_id, 'pan', amped_tr_pan, 'float')
            tracks_r.track_param_add(cvpj_l, amped_tr_id, 'enabled', int(not amped_tr_mute), 'bool')
            tracks_r.track_param_add(cvpj_l, amped_tr_id, 'solo', int(amped_tr_solo), 'bool')
            encode_devices(amped_tr_devices, amped_tr_id)
            for amped_reg in amped_tr_regions:
                amped_reg_position = amped_reg['position']*4
                amped_reg_length = amped_reg['length']*4
                amped_reg_offset = amped_reg['offset']*4
                amped_reg_clips = amped_reg['clips']
                amped_reg_midi = amped_reg['midi']
                amped_reg_name = amped_reg['name']
                amped_reg_color = amped_reg['color'] if 'color' in amped_reg else 'lime'
                cvpj_placement_base = {}
                cvpj_placement_base['position'] = amped_reg_position
                cvpj_placement_base['duration'] = amped_reg_length
                cvpj_placement_base['name'] = amped_reg['name']
                cvpj_placement_base['color'] = amped_colors[amped_reg_color]
                cvpj_placement_base['cut'] = {'type': 'cut', 'start':amped_reg_offset, 'end': amped_reg_length+amped_reg_offset}

                if amped_reg_midi != {'notes': [], 'events': [], 'chords': []}: 
                    cvpj_placement_notes = cvpj_placement_base.copy()
                    cvpj_placement_notes['notelist'] = []
                    for amped_note in amped_reg_midi['notes']:
                        cvpj_note = note_data.rx_makenote(amped_note['position']*4, amped_note['length']*4, amped_note['key']-60,  amped_note['velocity']/127, None)
                        cvpj_placement_notes['notelist'].append(cvpj_note)
                    tracks_r.add_pl(cvpj_l, amped_tr_id, 'notes', cvpj_placement_notes)

                if amped_reg_clips != []:
                    cvpj_placement_audionested = cvpj_placement_base.copy()
                    clip_events = []

                    for amped_reg_clip in amped_reg_clips:
                        temp_pl = {}
                        temp_pl['file'] = get_contentGuid(amped_reg_clip['contentGuid'])
                        temp_pl['position'] = (amped_reg_clip['position']*4)
                        temp_pl['duration'] = (amped_reg_clip['length']*4)
                        temp_pl['vol'] = amped_reg_clip['gain']
                        temp_pl['audiomod'] = {}
                        temp_pl['audiomod']['stretch_algorithm'] = 'stretch'
                        temp_pl['audiomod']['stretch_method'] = 'rate_speed'
                        temp_pl['audiomod']['stretch_data'] = {'rate': 1/amped_reg_clip['stretch']}

                        amped_reg_clip_offset = amped_reg_clip['offset']*4
                        if amped_reg_clip_offset != 0:
                            temp_pl['cut'] = {'type': 'cut', 'start':amped_reg_clip_offset}
                        clip_events.append(temp_pl)

                    cvpj_placement_audionested['events'] = clip_events
                    tracks_r.add_pl(cvpj_l, amped_tr_id, 'audio_nested', cvpj_placement_audionested)



        return json.dumps(cvpj_l)
