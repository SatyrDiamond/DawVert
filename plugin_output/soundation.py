# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import os
import struct
import math
from functions import xtramath
from functions import colors
from functions import data_values
from functions import data_dataset
from functions import plugins
from functions import idvals
from functions import notelist_data
from functions import params
from functions import auto
from functions import song
from functions_compat import trackfx_to_numdata
from functions_plugin import soundation_values
from functions_tracks import auto_nopl
from functions_tracks import tracks_r

def makechannel(i_type): 
    return {
      "name": 'noname',
      "type": i_type,
      "color": "#444444",
      "mute": False,
      "solo": False,
      "volume": 1,
      "pan": 0.5,
      "volumeAutomation": [],
      "panAutomation": [],
      "effects": [],
    }

def set_asdr(sng_instparams, asdr_a, asdr_s, asdr_d, asdr_r):
    add_sndinstparam(sng_instparams, 'attack', asdr_a, [])
    add_sndinstparam(sng_instparams, 'sustain', asdr_s, [])
    add_sndinstparam(sng_instparams, 'decay', asdr_d, [])
    add_sndinstparam(sng_instparams, 'release', asdr_r, [])

def add_sndinstparam(i_dict, i_name, i_value, i_auto): 
    if i_auto != None: i_dict[i_name] = {"value": i_value, "automation": i_auto}
    else: i_dict[i_name] = {"value": i_value}

def cvpjidata_to_sngparam(cvpj_plugindata, i_dict, pluginid, i_name, i_fallback): 
    value = cvpj_plugindata.dataval_get(i_name, i_fallback)
    add_sndinstparam(i_dict, i_name, value, None)

def cvpjiparam_to_sngparam(cvpj_plugindata, i_dict, pluginid, i_name, i_fallback, i_auto): 
    value = cvpj_plugindata.param_get(i_name, i_fallback)[0]
    add_sndinstparam(i_dict, i_name, value, i_auto)


def add_fx(sng_trkdata, s_trackdata):
    sng_fxchain = sng_trkdata['effects']
    if 'chain_fx_audio' in s_trackdata:
        chainfxdata = s_trackdata['chain_fx_audio']
        for fxpluginid in chainfxdata:
            fx_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, fxpluginid)
            plugtype = fx_plugindata.type_get()
            fx_on, fx_wet = fx_plugindata.fxdata_get()

            if plugtype[0] == 'native-soundation' and plugtype[1] != 'com.soundation.send':
                fxpluginname = plugtype[1]
                sng_fxdata = {}
                sng_fxdata['identifier'] = fxpluginname
                sng_fxdata['bypass'] = not fx_on

                paramlist = dataset.params_list('plugin', fxpluginname)

                for snd_param in paramlist:
                    autodata = auto_nopl.getpoints(cvpj_l, ['plugin',fxpluginid,snd_param])
                    if autodata != None: autodata = cvpjauto_to_sngauto(autodata, ticksdiv)
                    else: autodata = []
                    cvpjiparam_to_sngparam(fx_plugindata, sng_fxdata, fxpluginid, snd_param, 0, autodata)

                sng_fxchain.append(sng_fxdata)

def cvpjauto_to_sngauto(autopoints, ticks):
    sngauto = []
    for autopoint in autopoints:
        sngauto.append({"pos": autopoint['position']*ticks, "value": autopoint['value']})
    return sngauto

def add_send(senddata, sng_trkdata, tomaster):
    if senddata[0] != -1:
        sendeffectdata = {}
        sendeffectdata['identifier'] = "com.soundation.send"
        sendeffectdata['bypass'] = False
        sendeffectdata['channelIndex'] = senddata[0]+1
        sendeffectdata['pan'] = {"value": 0.5, "automation": []}
        sendeffectdata['output'] = {"value": tomaster, "automation": []}

        sendauto = []
        if senddata[2] != None:
            cvpjauto_amt = auto_nopl.getpoints(cvpj_l, ['send',senddata[2],'amount'])
            if cvpjauto_amt != None: sendauto = cvpjauto_to_sngauto(auto.remove_instant(cvpjauto_vol, 0, False), ticksdiv)
        sendeffectdata['send'] = {"value": senddata[1], "automation": sendauto}

        sng_trkdata['effects'].append(sendeffectdata)

class output_soundation(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Soundation'
    def getshortname(self): return 'soundation'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': ['loop'],
        'auto_nopl': True
        }
    def getsupportedplugformats(self): return ['midi']
    def getsupportedplugins(self): return []
    def getfileextension(self): return 'sng'
    def parse(self, convproj_json, output_file):
        global cvpj_l
        global ticksdiv
        global dataset

        dataset = data_dataset.dataset('./data_dset/soundation.dset')
        dataset_synth_nonfree = data_dataset.dataset('./data_dset/synth_nonfree.dset')

        cvpj_l = json.loads(convproj_json)
        bpm = params.get(cvpj_l, [], 'bpm', 120)[0]

        sng_output = {}
        sng_output["version"] = 2.3
        sng_output["studio"] = "3.10.7"
        sng_output["bpm"] = int(bpm)
        beatNumerator, beatDenominator = song.get_timesig(cvpj_l)
        sng_output["timeSignature"] = str(beatNumerator)+'/'+str(beatDenominator)

        loop_on, loop_start, loop_end = song.get_loopdata(cvpj_l, 'r')
        sng_output["looping"] = loop_on
        sng_output["loopStart"] = loop_start/4
        sng_output["loopEnd"] = loop_end/4

        sng_channels = sng_output["channels"] = []

        idvals_inst_gm2 = idvals.parse_idvalscsv('data_idvals/soundation_gm_inst.csv')

        bpmdiv = 120/bpm
        ticksdiv = 5512*bpmdiv

        sng_master = makechannel("master")
        sng_master['name'] = "Master Channel"
        if 'track_master' in cvpj_l: 
            cvpj_master = cvpj_l['track_master']
            sng_master['name'] = data_values.get_value(cvpj_master, 'name', 'Master Channel')
            sng_master['volume'] = data_values.get_value(cvpj_master, 'vol', 1.0)
            add_fx(sng_master, cvpj_master)
        sng_channels.append(sng_master)

        mas_cvpjauto_vol = auto_nopl.getpoints(cvpj_l, ['master','vol'])
        if mas_cvpjauto_vol != None:
            mas_cvpjauto_vol = auto.remove_instant(mas_cvpjauto_vol, 0, False)
            sng_master['volumeAutomation'] = cvpjauto_to_sngauto(mas_cvpjauto_vol, ticksdiv)
        mas_cvpjauto_pan = auto_nopl.getpoints(cvpj_l, ['master','pan'])
        if mas_cvpjauto_pan != None:
            mas_cvpjauto_pan = auto.remove_instant(mas_cvpjauto_pan, 0, False)
            sng_master['panAutomation'] = cvpjauto_to_sngauto(auto.multiply_nopl(mas_cvpjauto_pan, 1, 0.5), ticksdiv)

        if 'timesig' in cvpj_l: 
            ts_numerator, ts_denominator = cvpj_l['timesig']
            sng_output["timeSignature"] = str(ts_numerator)+'/'+str(ts_denominator)

        output_ids = trackfx_to_numdata.trackfx_to_numdata(cvpj_l, 0)

        return_datas = {}

        if 'track_master' in cvpj_l:
            track_master_data = cvpj_l['track_master']
            if 'returns' in track_master_data:
                for returnid in track_master_data['returns']:
                    return_datas[returnid] = track_master_data['returns'][returnid]

        cvpj_track_placements = cvpj_l['track_placements'] if 'track_placements' in cvpj_l else {}
        cvpj_track_order = cvpj_l['track_order'] if 'track_order' in cvpj_l else []
        cvpj_track_data = cvpj_l['track_data'] if 'track_data' in cvpj_l else {}

        for output_id in output_ids:

            if output_id[1] == 'return':
                return_data = return_datas[output_id[2]]
                trackcolor = data_values.get_value(return_data, 'color', [0.5,0.5,0.5])
                trackcolor_hex = colors.rgb_float_to_hex(trackcolor) 
                sng_trkdata = makechannel("effect")
                sng_trkdata['name'] = '[R] '+data_values.get_value(return_data, 'name', 'noname')
                sng_trkdata['color'] = '#'+trackcolor_hex.upper()
                sng_trkdata['volume'] = params.get(return_data, [], 'vol', 1)[0]
                sng_trkdata['pan'] = 0.5 + params.get(return_data, [], 'pan', 0)[0]/2
                muteddata = params.get(return_data, [], 'enabled', True)[0]
                if muteddata != None: sng_trkdata['mute'] = not muteddata

                cvpjauto_vol = auto_nopl.getpoints(cvpj_l, ['return',output_id[2],'vol'])
                if cvpjauto_vol != None: sng_trkdata['volumeAutomation'] = cvpjauto_to_sngauto(auto.remove_instant(cvpjauto_vol, 0, False), ticksdiv)
                cvpjauto_pan = auto_nopl.getpoints(cvpj_l, ['return',output_id[2],'pan'])
                if cvpjauto_pan != None: sng_trkdata['panAutomation'] = cvpjauto_to_sngauto(auto.multiply_nopl(auto.remove_instant(cvpjauto_pan, 0, False), 1, 0.5), ticksdiv)

                add_fx(sng_trkdata, return_data)
                for sendpart in output_id[4]:
                    add_send(sendpart, sng_trkdata, 1)
                add_send(output_id[3], sng_trkdata, 0)
                sng_channels.append(sng_trkdata)

            if output_id[1] == 'group':
                group_data = cvpj_l['groups'][output_id[2]]
                trackcolor = data_values.get_value(group_data, 'color', [0.5,0.5,0.5])
                trackcolor_hex = colors.rgb_float_to_hex(trackcolor) 
                sng_trkdata = makechannel("effect")
                sng_trkdata['name'] = '[G] '+data_values.get_value(group_data, 'name', 'noname')
                sng_trkdata['color'] = '#'+trackcolor_hex.upper()
                sng_trkdata['volume'] = params.get(group_data, [], 'vol', 1)[0]
                sng_trkdata['pan'] = 0.5 + params.get(group_data, [], 'pan', 0)[0]/2
                muteddata = params.get(group_data, [], 'enabled', True)[0]
                if muteddata != None: sng_trkdata['mute'] = not muteddata

                cvpjauto_vol = auto_nopl.getpoints(cvpj_l, ['group',output_id[2],'vol'])
                if cvpjauto_vol != None: sng_trkdata['volumeAutomation'] = cvpjauto_to_sngauto(auto.remove_instant(cvpjauto_vol, 0, False), ticksdiv)
                cvpjauto_pan = auto_nopl.getpoints(cvpj_l, ['group',output_id[2],'pan'])
                if cvpjauto_pan != None: sng_trkdata['panAutomation'] = cvpjauto_to_sngauto(auto.multiply_nopl(auto.remove_instant(cvpjauto_pan, 0, False), 1, 0.5), ticksdiv)

                add_fx(sng_trkdata, group_data)
                for sendpart in output_id[4]:
                    add_send(sendpart, sng_trkdata, 1)
                add_send(output_id[3], sng_trkdata, 0)
                sng_channels.append(sng_trkdata)

            if output_id[1] == 'track':
                cvpj_trackid = output_id[2]
                s_trackdata = cvpj_track_data[output_id[2]] if output_id[2] in cvpj_track_data else {}
                track_placements = cvpj_track_placements[output_id[2]] if output_id[2] in cvpj_track_placements else {}

                tracktype = s_trackdata['type']

                trackcolor = data_values.get_value(s_trackdata, 'color', [0.5,0.5,0.5])
                trackcolor_hex = colors.rgb_float_to_hex(trackcolor) 

                sng_trkdata = makechannel("instrument")
                sng_trkdata['name'] = data_values.get_value(s_trackdata, 'name', 'noname')
                sng_trkdata['color'] = '#'+trackcolor_hex.upper()
                sng_trkdata['volume'] = params.get(s_trackdata, [], 'vol', 1)[0]
                sng_trkdata['pan'] = 0.5 + params.get(s_trackdata, [], 'pan', 0)[0]/2
                muteddata = params.get(s_trackdata, [], 'enabled', True)[0]
                if muteddata != None: sng_trkdata['mute'] = not muteddata
                sng_trkdata['solo'] = params.get(s_trackdata, [], 'solo', 0)[0]

                cvpjauto_vol = auto_nopl.getpoints(cvpj_l, ['track',cvpj_trackid,'vol'])
                if cvpjauto_vol != None: sng_trkdata['volumeAutomation'] = cvpjauto_to_sngauto(auto.remove_instant(cvpjauto_vol, 0, False), ticksdiv)
                cvpjauto_pan = auto_nopl.getpoints(cvpj_l, ['track',cvpj_trackid,'pan'])
                if cvpjauto_pan != None: sng_trkdata['panAutomation'] = cvpjauto_to_sngauto(auto.multiply_nopl(auto.remove_instant(cvpjauto_pan, 0, False), 1, 0.5), ticksdiv)

                if tracktype == 'instrument':
                    sng_instparams = sng_trkdata['instrument'] = {"identifier": "com.soundation.GM-2"}

                    inst_supported = False

                    pluginid = data_values.nested_dict_get_value(s_trackdata, ['instdata', 'pluginid'])

                    if pluginid != None:
                        cvpj_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)
                        plugtype = cvpj_plugindata.type_get()
                        a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = cvpj_plugindata.asdr_env_get('vol')

                        if plugtype == ['synth-nonfree', 'europa']:
                            inst_supported = True
                            sng_instparams['identifier'] = 'com.soundation.europa'

                            europaparamlist = dataset_synth_nonfree.params_list('plugin', 'europa')
                            for paramname in europaparamlist:
                                param = dataset_synth_nonfree.params_i_get('plugin', 'europa', paramname)

                                if not param[0]:
                                    eur_value_value = cvpj_plugindata.param_get(paramname, 0)[0]
                                else:
                                    eur_value_value = cvpj_plugindata.dataval_get(paramname, 0)
                                    if paramname in ['Curve1','Curve2','Curve3','Curve4','Curve']: 
                                        eur_value_value = ','.join([str(x).zfill(2) for x in eur_value_value])

                                add_sndinstparam(sng_instparams, "/custom_properties/"+paramname, eur_value_value, [])
                            add_sndinstparam(sng_instparams, "/soundation/sample", None, [])

                        elif plugtype[0] == 'native-soundation':
                            inst_supported = True
                            sng_instparams['identifier'] = plugtype[1]
                            if plugtype[1] == 'com.soundation.GM-2':
                                cvpjidata_to_sngparam(cvpj_plugindata, sng_instparams, pluginid, 'sample_pack', '2_0_Bright_Yamaha_Grand.smplpck')
                                a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = cvpj_plugindata.asdr_env_get('vol')
                                set_asdr(sng_instparams, a_attack, a_sustain, a_decay, a_release)

                            elif plugtype[1] == 'com.soundation.SAM-1':
                                sample_pack = cvpj_plugindata.dataval_get('sample_pack', None)
                                sng_instparams['sample_pack'] = sample_pack
                                a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = cvpj_plugindata.asdr_env_get('vol')
                                set_asdr(sng_instparams, a_attack, a_sustain, a_decay, a_release)

                            elif plugtype[1] == 'com.soundation.simple':

                                for oscnum in range(4):
                                    for paramtype in ['detune','pitch','type','vol']:
                                        cvpjiparam_to_sngparam(cvpj_plugindata, sng_instparams, pluginid, 'osc_'+str(oscnum)+'_'+paramtype, 0, [])

                                f_predelay, f_attack, f_hold, f_decay, f_sustain, f_release, f_amount = cvpj_plugindata.asdr_env_get('cutoff')
                                add_sndinstparam(sng_instparams, 'filter_attack', f_attack, [])
                                add_sndinstparam(sng_instparams, 'filter_decay', f_decay, [])
                                add_sndinstparam(sng_instparams, 'filter_sustain', f_sustain, [])
                                add_sndinstparam(sng_instparams, 'filter_release', f_release, [])
                                add_sndinstparam(sng_instparams, 'filter_int', f_amount, [])

                                f_enabled, f_cutoff, f_reso, f_type, f_subtype = cvpj_plugindata.filter_get()
                                add_sndinstparam(sng_instparams, 'filter_cutoff', xtramath.between_to_one(20, 7500, f_cutoff), [])
                                add_sndinstparam(sng_instparams, 'filter_resonance', f_reso, [])

                                for snd_param in ['noise_vol', 'noise_color']:
                                    cvpjiparam_to_sngparam(cvpj_plugindata, sng_instparams, pluginid, snd_param, 0, [])

                            elif plugtype[1] == 'com.soundation.supersaw':
                                set_asdr(sng_instparams, a_attack, a_sustain, a_decay, a_release)
                                for snd_param in ["detune", "spread"]:
                                    cvpjiparam_to_sngparam(cvpj_plugindata, sng_instparams, pluginid, snd_param, 0, [])

                            elif plugtype[1] == 'com.soundation.noiser':
                                set_asdr(sng_instparams, a_attack, a_sustain, a_decay, a_release)

                            elif plugtype[1] == 'com.soundation.drummachine':
                                for paramname in ["gain_2", "hold_1", "pitch_6", "gain_1", "decay_5", "gain_5", "hold_0", "hold_2", "pitch_7", "gain_0", "decay_6", "gain_3", "hold_5", "pitch_3", "decay_4", "pitch_4", "gain_6", "decay_7", "pitch_2", "hold_6", "decay_1", "decay_3", "decay_0", "decay_2", "gain_7", "pitch_0", "pitch_5", "hold_3", "pitch_1", "hold_4", "hold_7", "gain_4"]:
                                    cvpjiparam_to_sngparam(cvpj_plugindata, sng_instparams, pluginid, paramname, 0, [])
                                cvpjidata_to_sngparam(cvpj_plugindata, sng_instparams, pluginid, 'kit_name', '')

                            elif plugtype[1] == 'com.soundation.spc':
                                for paramname in soundation_values.spc_vals():
                                    cvpjiparam_to_sngparam(cvpj_plugindata, sng_instparams, pluginid, paramname, 0, [])
                                for dataname in ['cuts','envelopes']:
                                    sng_instparams[dataname] = cvpj_plugindata.dataval_get(dataname, '')

                            elif plugtype[1] in ['com.soundation.va_synth','com.soundation.fm_synth','com.soundation.the_wub_machine','com.soundation.mono']:
                                if plugtype[1] == 'com.soundation.va_synth': snd_params = ["aatt", "adec", "arel", "asus", "fatt", "fdec", "fdyn", "feg", "ffreq", "frel", "fres", "fsus", "glide_bend", "glide_mode", "glide_rate", "lfolpf", "lfoosc", "lforate", "octave", "osc_2_fine", "osc_2_mix", "osc_2_noise", "osc_2_octave", "tune"]
                                elif plugtype[1] == 'com.soundation.fm_synth': snd_params = ['p'+str(x) for x in range(137)]
                                elif plugtype[1] == 'com.soundation.mono': snd_params = ['filter_int','cutoff','resonance','pw','filter_decay','mix','amp_decay','glide']
                                elif plugtype[1] == 'com.soundation.the_wub_machine': snd_params = ['filter_cutoff','filter_drive','filter_resonance','filter_type','filth_active','filth_amount','lfo_depth','lfo_keytracking','lfo_loop','lfo_phase','lfo_retrigger','lfo_speed','lfo_type','msl_amount','osc1_gain','osc1_glide','osc1_pan','osc1_pitch','osc1_shape','osc1_type','osc2_gain','osc2_glide','osc2_pan','osc2_pitch','osc2_shape','osc2_type','osc_sub_bypass_filter','osc_sub_gain','osc_sub_glide','osc_sub_shape','osc_sub_volume_lfo','reese_active','unison_active','unison_amount','unison_count']
                                for snd_param in snd_params:
                                    cvpjiparam_to_sngparam(cvpj_plugindata, sng_instparams, pluginid, snd_param, 0, [])

                        elif plugtype[0] == 'midi':
                            inst_supported = True
                            midibank = cvpj_plugindata.dataval_get('bank', 0)
                            midiinst = cvpj_plugindata.dataval_get('inst', 0)+1
                            gm2_samplepack = idvals.get_idval(idvals_inst_gm2, str(midiinst)+'_'+str(midibank), 'url')
                            if gm2_samplepack == None and midibank not in [0, 128]:
                                gm2_samplepack = idvals.get_idval(idvals_inst_gm2, str(midiinst)+'_0', 'url')
                            add_sndinstparam(sng_instparams, 'sample_pack', gm2_samplepack, None)
                            add_sndinstparam(sng_instparams, 'attack', 0, [])
                            add_sndinstparam(sng_instparams, 'decay', 0, [])
                            add_sndinstparam(sng_instparams, 'sustain', 1, [])
                            add_sndinstparam(sng_instparams, 'release', 0, [])

                        elif plugtype[0] == 'retro':
                            if plugtype[1] == 'sine': gm2_samplepack = '81_8_Sine_Wave.smplpck'
                            if plugtype[1] == 'square': gm2_samplepack = '81_0_Square_Lead.smplpck'
                            if plugtype[1] == 'triangle': gm2_samplepack = '85_0_Charang.smplpck'
                            if plugtype[1] == 'saw': gm2_samplepack = '82_0_Saw_Wave.smplpck'
                            add_sndinstparam(sng_instparams, 'attack', 0, [])
                            add_sndinstparam(sng_instparams, 'decay', 0, [])
                            add_sndinstparam(sng_instparams, 'sustain', 1, [])
                            add_sndinstparam(sng_instparams, 'release', 0, [])

                    if inst_supported == False: 
                        add_sndinstparam(sng_instparams, 'sample_pack', '2_0_Bright_Yamaha_Grand.smplpck', False)
                        if pluginid != None:
                            add_sndinstparam(sng_instparams, 'attack', a_attack, [])
                            add_sndinstparam(sng_instparams, 'decay', a_decay, [])
                            add_sndinstparam(sng_instparams, 'sustain', a_sustain, [])
                            add_sndinstparam(sng_instparams, 'release', a_release, [])
                        else:
                            add_sndinstparam(sng_instparams, 'attack', 0, [])
                            add_sndinstparam(sng_instparams, 'decay', 0, [])
                            add_sndinstparam(sng_instparams, 'sustain', 1, [])
                            add_sndinstparam(sng_instparams, 'release', 0, [])

                    sng_trkdata['userSetName'] = data_values.get_value(s_trackdata, 'name', '')
                    sng_trkdata['regions'] = []
                    if 'notes' in track_placements:
                        cvpj_clips = notelist_data.sort(track_placements['notes'])
                        for cvpj_clip in cvpj_clips:
                            sng_region = {}
                            intcolor = cvpj_clip['color'] if 'color' in cvpj_clip else trackcolor
                            sng_region["color"] = int.from_bytes(struct.pack("3B", *colors.rgb_float_to_rgb_int(intcolor)), "little")
                            sng_region["position"] = int(cvpj_clip['position']*ticksdiv)
                            sng_region["length"] = int(cvpj_clip['duration']*ticksdiv)
                            sng_region["loopcount"] = 1
                            sng_region["contentPosition"] = 0

                            if 'cut' in cvpj_clip:
                                cvpj_clip_cutdata = cvpj_clip['cut']

                                if cvpj_clip_cutdata['type'] in ['loop', 'loop_off']: 
                                    sng_region["length"] = cvpj_clip_cutdata['loopend']*ticksdiv
                                    sng_region["loopcount"] = cvpj_clip['duration']/cvpj_clip_cutdata['loopend']
                                    if cvpj_clip_cutdata['type'] == 'loop_off':
                                        sng_region["contentPosition"] = -(cvpj_clip_cutdata['start']*ticksdiv)
                                if cvpj_clip_cutdata['type'] == 'cut': 
                                    sng_region["contentPosition"] = -(cvpj_clip_cutdata['start']*ticksdiv)

                            sng_region["type"] = 2
                            sng_region["notes"] = []
                            if 'notelist' in cvpj_clip:
                                for cvpj_note in cvpj_clip['notelist']:
                                    if 0 <= cvpj_note['key']+60 <= 128:
                                        sng_note = {}
                                        sng_note["note"] = int(cvpj_note['key']+60)
                                        sng_note["velocity"] = data_values.get_value(cvpj_note, 'vol', 1)
                                        sng_note["position"] = int(cvpj_note['position']*ticksdiv)
                                        sng_note["length"] = int(cvpj_note['duration']*ticksdiv)
                                        sng_region["notes"].append(sng_note)

                            sng_trkdata['regions'].append(sng_region)

                add_fx(sng_trkdata, s_trackdata)
                for sendpart in output_id[4]:
                    add_send(sendpart, sng_trkdata, 1)
                add_send(output_id[3], sng_trkdata, 0)
                sng_channels.append(sng_trkdata)


        if 'timemarkers' in cvpj_l:
            for timemarkdata in cvpj_l['timemarkers']:
                if 'type' in timemarkdata:
                    if timemarkdata['type'] == 'loop_area':
                        sng_output["looping"] = True
                        sng_output["loopStart"] = int(timemarkdata['position']*ticksdiv)
                        sng_output["loopEnd"] = int(timemarkdata['end']*ticksdiv)

        with open(output_file, "w") as fileout:
            json.dump(sng_output, fileout, indent=4)