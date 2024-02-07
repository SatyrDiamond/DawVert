# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from objects import dv_dataset
from functions import data_values
from functions import xtramath
from functions import audio_wav
import xml.etree.ElementTree as ET
import plugin_input
import json
import os
import struct
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

def get_dev_auto(amped_autodata, devid, paramsdata): 
    out = []
    if devid in amped_autodata:
        devauto = amped_autodata[devid]
        for param in paramsdata:
            if 'name' in param:
                if param['name'] in devauto:
                    out.append([param['name'], devauto[param['name']]])
    return out

def eq_calc_q(band_type, q_val):
    if band_type in ['low_pass', 'high_pass']: q_val = xtramath.logpowmul(q_val, 2) if q_val != 0 else 1
    if band_type in ['peak']: q_val = xtramath.logpowmul(q_val, -1) if q_val != 0 else 1
    return q_val

def do_idparams(paramsdata, plugin_obj, pluginname):
    for param in paramsdata:
        plugin_obj.add_from_dset(param['name'], param['value'], dataset, 'plugin', pluginname)

def do_idauto(convproj_obj, amped_autodata, devid, amped_auto, pluginid):
    if amped_autodata:
        for s_amped_auto in get_dev_auto(amped_autodata, devid, amped_auto):
            autoloc = ['plugin',pluginid,s_amped_auto[0].replace('/', '__')]
            for point in s_amped_auto[1]:
                convproj_obj.add_autopoint(autoloc, 'float', point[0], point[1], 'normal')

def get_contentGuid(contentGuid):
    if isinstance(contentGuid, dict): return str(contentGuid['userAudio']['exportedId'])
    else: return contentGuid

def encode_devices(convproj_obj, amped_tr_devices, track_obj, amped_autodata):
    for amped_tr_device in amped_tr_devices:
        devid = amped_tr_device['id']
        pluginid = str(devid)
        devicetype = [amped_tr_device['className'], amped_tr_device['label']]

        if devicetype[0] == 'WAM' and devicetype[1] in ['Augur', 'OBXD', 'Dexed']: 
            track_obj.inst_pluginid = pluginid
            plugin_obj = convproj_obj.add_plugin(pluginid, 'native-amped', devicetype[1])
            plugin_obj.datavals.add('data', amped_tr_device['wamPreset'])

        elif devicetype[0] == 'WAM' and devicetype[1] == 'Europa': 
            track_obj.inst_pluginid = pluginid
            plugin_obj = convproj_obj.add_plugin(pluginid, 'synth-nonfree', 'Europa')

            wampreset = amped_tr_device['wamPreset']
            wampreset = json.loads(wampreset)
            europa_xml = ET.fromstring(wampreset['settings'])
            europa_xml_prop = europa_xml.findall('Properties')[0]

            europa_params = {}

            for xmlsub in europa_xml_prop:
                if xmlsub.tag == 'Object':
                    object_name = xmlsub.get('name')
                    for objsub in xmlsub:
                        if objsub.tag == 'Value':
                            value_name = objsub.get('property')
                            value_type = objsub.get('type')
                            value_value = float(objsub.text) if value_type == 'number' else objsub.text
                            europa_params[value_name] = [value_type, value_value]

            paramlist = dataset_synth_nonfree.params_list('plugin', 'europa')
            for paramname in paramlist:
                dset_paramdata = dataset_synth_nonfree.params_i_get('plugin', 'europa', paramname)
                if dset_paramdata[5] in europa_params:
                    param_type, param_value = europa_params[dset_paramdata[5]]

                    if param_type == 'number':
                        plugin_obj.add_from_dset(paramname, param_value, dataset_synth_nonfree, 'plugin', 'europa')
                    else:
                        if dset_paramdata[5] in ['Curve1','Curve2','Curve3','Curve4','Curve']: 
                            param_value = list(bytes.fromhex(param_value))
                        plugin_obj.datavals.add(paramname, param_value)

            if 'encodedSampleData' in wampreset:
                plugin_obj.datavals.add('encodedSampleData', wampreset['encodedSampleData'])

        elif devicetype[0] == 'WAM' and devicetype[1] in ['Amp Sim Utility']: 
            plugin_obj = convproj_obj.add_plugin(pluginid, 'native-amped', devicetype[1])
            plugin_obj.datavals.add('data', amped_tr_device['wamPreset'])
            track_obj.fxslots_audio.append(pluginid)

        elif devicetype == ['Drumpler', 'Drumpler']:
            track_obj.inst_pluginid = pluginid
            plugin_obj = convproj_obj.add_plugin(pluginid, 'native-amped', 'Drumpler')
            plugin_obj.datavals.add('kit', amped_tr_device['kit'])
            do_idparams(amped_tr_device['params'], plugin_obj, devicetype[0])

        elif devicetype == ['SF2', 'GM Player']:
            track_obj.inst_pluginid = pluginid
            value_patch = 0
            value_bank = 0
            value_drum = 0
            value_gain = 0.75
            for param in amped_tr_device['params']:
                paramname, paramval = param['name'], param['value']
                if paramname == 'patch': value_patch = paramval
                if paramname == 'bank': value_bank = paramval
                if paramname == 'gain': value_gain = paramval

            if value_bank >= 128: 
                value_bank -= 128
                value_drum = True

            plugin_obj = convproj_obj.add_plugin_midi(pluginid, value_bank, value_patch, value_drum)
            param_obj = plugin_obj.params.add('gain', paramval, 'float')
            param_obj.visual.name = 'Gain'

        elif devicetype == ['Granny', 'Granny']:
            track_obj.inst_pluginid = pluginid
            plugin_obj = convproj_obj.add_plugin(pluginid, 'native-amped', 'Granny')

            sampleuuid = amped_tr_device['grannySampleGuid']
            sampleref_obj = convproj_obj.add_sampleref(sampleuuid, '')
            sampleref_obj.visual.name = amped_tr_device['grannySampleName']
            plugin_obj.samplerefs['sample'] = sampleuuid
            do_idparams(amped_tr_device['params'], plugin_obj, devicetype[0])
            do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device['params'], pluginid)

        elif devicetype == ['Volt', 'VOLT']:
            track_obj.inst_pluginid = pluginid
            plugin_obj = convproj_obj.add_plugin(pluginid, 'native-amped', 'Volt')
            do_idparams(amped_tr_device['params'], plugin_obj, devicetype[0])
            do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device['params'], pluginid)

        elif devicetype == ['VoltMini', 'VOLT Mini']:
            track_obj.inst_pluginid = pluginid
            plugin_obj = convproj_obj.add_plugin(pluginid, 'native-amped', 'VoltMini')
            do_idparams(amped_tr_device['params'], plugin_obj, devicetype[0])
            do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device['params'], pluginid)

        elif devicetype == ['Sampler', 'Sampler']:
            track_obj.inst_pluginid = pluginid
            samplerdata = {}
            for param in amped_tr_device['params']: data_values.nested_dict_add_value(samplerdata, param['name'].split('/'), param['value'])

            amped_tr_device['zonefile'] = {}
            for param in amped_tr_device['samplerZones']: amped_tr_device['zonefile'][str(param['id'])] = param['contentGuid']

            plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'multi')
            plugin_obj.datavals.add('point_value_type', "percent")

            samplerdata_voiceLimit = samplerdata['voiceLimit']
            samplerdata_filter = samplerdata['filter']
            samplerdata_eg = samplerdata['eg']
            samplerdata_zone = samplerdata['zone']
            samplerdata_zonefile = amped_tr_device['zonefile']
            
            for samplerdata_zp in samplerdata_zone:
                amped_samp_part = samplerdata_zone[samplerdata_zp]
                cvpj_region = {}
                cvpj_region['sampleref'] = get_contentGuid(samplerdata_zonefile[samplerdata_zp])
                cvpj_region['loop'] = {}
                cvpj_region['loop']['enabled'] = 0
                cvpj_region['loop']['points'] = [amped_samp_part['looping']['startPositionNorm'], amped_samp_part['looping']['endPositionNorm']]
                cvpj_region['middlenote'] = amped_samp_part['key']['root']-60
                plugin_obj.regions.add(int(amped_samp_part['key']['min'])-60, int(amped_samp_part['key']['max'])-60, cvpj_region)

        elif devicetype == ['EqualizerPro', 'Equalizer']:
            track_obj.fxslots_audio.append(pluginid)
            plugin_obj = convproj_obj.add_plugin(pluginid, 'native-amped', 'EqualizerPro')
            do_idparams(amped_tr_device['params'], plugin_obj, devicetype[0])
            do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device['params'], pluginid)

        elif devicetype[0] in ['Chorus',  
        'CompressorMini', 'Delay', 'Distortion', 'Equalizer', 
        'Flanger', 'Gate', 'Limiter', 'LimiterMini', 'Phaser', 
        'Reverb', 'Tremolo', 'BitCrusher', 'Tremolo', 'Vibrato', 'Compressor', 'Expander']:
            track_obj.fxslots_audio.append(pluginid)
            plugin_obj = convproj_obj.add_plugin(pluginid, 'native-amped', devicetype[0])
            do_idparams(amped_tr_device['params'], plugin_obj, devicetype[0])
            do_idauto(convproj_obj, amped_autodata, devid, amped_tr_device['params'], pluginid)
#
#        #if devicetype != ['VSTConnection', 'VST/Remote Beta']:
#        #    device_plugindata.fxvisual_add(devicetype[1], None)
#        #    device_plugindata.to_cvpj(cvpj_l, pluginid)
#
def ampedauto_to_cvpjauto_specs(autopoints, autospecs):
    v_min = 0
    v_max = 1
    if autospecs['type'] == 'numeric':
        v_min = autospecs['min']
        v_max = autospecs['max']

    ampedauto = []
    for autopoint in autopoints: ampedauto.append([autopoint['pos'], xtramath.between_from_one(v_min, v_max, autopoint['value'])])
    return ampedauto

def ampedauto_to_cvpjauto(autopoints):
    for autopoint in autopoints: yield autopoint['pos'], autopoint['value']

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
        'auto_nopl': True,
        'track_hybrid': True,
        'placement_audio_stretch': ['rate'],
        'placement_audio_nested': True
        }

    def parse(self, convproj_obj, input_file, extra_param):
        global samplefolder
        global europa_vals
        global dataset
        global dataset_synth_nonfree

        convproj_obj.type = 'r'
        convproj_obj.set_timings(1, True)

        dataset = dv_dataset.dataset('./data_dset/amped.dset')
        dataset_synth_nonfree = dv_dataset.dataset('./data_dset/synth_nonfree.dset')

        samplefolder = extra_param['samplefolder']
        zip_data = zipfile.ZipFile(input_file, 'r')
        amped_project = json.loads(zip_data.read('amped-studio-project.json'))

        amped_looping = amped_project['looping']

        bpm = amped_project['tempo']
        convproj_obj.params.add('bpm', bpm, 'float')

        amped_timeSignature = amped_project['timeSignature']
        convproj_obj.timesig = [amped_timeSignature['num'], amped_timeSignature['den']]

        amped_filenames = json.loads(zip_data.read('filenames.json'))
        for amped_filename, realfilename in amped_filenames.items():
            old_file = os.path.join(samplefolder,amped_filename)
            new_file = os.path.join(samplefolder,realfilename)
            if os.path.exists(new_file) == False:
                zip_data.extract(amped_filename, path=samplefolder, pwd=None)
                os.rename(old_file,new_file)
            sampleref_obj = convproj_obj.add_sampleref(amped_filename, new_file)

        amped_masterTrack = amped_project['masterTrack']
        convproj_obj.track_master.params.add('vol', amped_masterTrack['volume'], 'float')

        encode_devices(convproj_obj, amped_masterTrack['devices'], convproj_obj.track_master, None)

        amped_tracks = amped_project['tracks']
        for amped_track in amped_tracks:
            amped_tr_id = str(amped_track['id'])

            amped_tr_regions = amped_track['regions']
            amped_tr_devices = amped_track['devices']
            amped_tr_automations = amped_track['automations']

            track_obj = convproj_obj.add_track(amped_tr_id, 'hybrid', 1, False)
            track_obj.visual.name = amped_track['name']
            track_obj.visual.color = amped_colors[amped_track['color'] if 'color' in amped_track else 'lime']
            track_obj.params.add('vol', amped_track['volume'], 'float')
            track_obj.params.add('pan', amped_track['pan'], 'float')
            track_obj.params.add('enabled', bool(not amped_track['mute']), 'bool')
            track_obj.params.add('solo', bool(amped_track['solo']), 'bool')

            for amped_tr_automation in amped_tr_automations:
                autoname = amped_tr_automation['param']
                autoloc = None

                if autoname == 'volume': autoloc = ['track', amped_tr_id, 'vol']
                if autoname == 'pan': autoloc = ['track', amped_tr_id, 'pan']
                if autoloc: 
                    for p, v in ampedauto_to_cvpjauto(amped_tr_automation['points']):
                        convproj_obj.add_autopoint(autoloc, 'float', p, v, 'normal')

            amped_autodata = {}
            for amped_tr_automation in amped_tr_automations:
                auto_param = amped_tr_automation['param']
                if 'deviceId' in auto_param:
                    amped_tr_autoparam = amped_tr_automation['param']
                    devid = amped_tr_autoparam['deviceId']
                    autoname = amped_tr_autoparam['name']
                    if devid not in amped_autodata: amped_autodata[devid] = {}
                    amped_autodata[devid][autoname] = ampedauto_to_cvpjauto_specs(amped_tr_automation['points'], amped_tr_automation['spec'])

            encode_devices(convproj_obj, amped_tr_devices, track_obj, amped_autodata)

            for amped_reg in amped_tr_regions:
                amped_reg_position = amped_reg['position']
                amped_reg_length = amped_reg['length']
                amped_reg_offset = amped_reg['offset']
                amped_reg_midi = amped_reg['midi']
                amped_reg_name = amped_reg['name']
                amped_reg_color = amped_reg['color'] if 'color' in amped_reg else 'lime'

                amped_reg_notes = amped_reg_midi['notes']
                if amped_reg_notes != []: 
                    placement_obj = track_obj.placements.add_notes()
                    placement_obj.position = amped_reg_position
                    placement_obj.duration = amped_reg_length
                    placement_obj.visual.name = amped_reg['name']
                    placement_obj.visual.color = amped_colors[amped_reg_color]
                    placement_obj.cut_type = 'cut'
                    placement_obj.cut_data['start'] = amped_reg_offset
                    for amped_note in amped_reg_notes:
                        placement_obj.notelist.add_r(amped_note['position'], amped_note['length'], amped_note['key']-60, amped_note['velocity']/127, {})

                amped_reg_clips = amped_reg['clips'] if 'clips' in amped_reg else []
                if amped_reg_clips != []: 
                    placement_obj = track_obj.placements.add_nested_audio()
                    placement_obj.position = amped_reg_position
                    placement_obj.duration = amped_reg_length
                    placement_obj.visual.name = amped_reg['name']
                    placement_obj.visual.color = amped_colors[amped_reg_color]
                    placement_obj.cut_type = 'cut'
                    placement_obj.cut_data['start'] = amped_reg_offset

                    for amped_reg_clip in amped_reg_clips:
                        apl_obj = placement_obj.add()
                        apl_obj.position = amped_reg_clip['position']
                        apl_obj.duration = amped_reg_clip['length']
                        apl_obj.vol = amped_reg_clip['gain']
                        apl_obj.pitch = amped_reg_clip['pitchShift'] if 'pitchShift' in amped_reg_clip else 0
                        apl_obj.sampleref = get_contentGuid(amped_reg_clip['contentGuid'])
                        apl_obj.stretch.use_tempo = False
                        apl_obj.stretch.rate = 1/amped_reg_clip['stretch']

                        amped_reg_clip_offset = amped_reg_clip['offset']
                        if amped_reg_clip_offset != 0:
                            apl_obj.cut_type = 'cut'
                            apl_obj.cut_data['start'] = amped_reg_clip_offset*(120/bpm)
 