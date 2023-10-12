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
from functions import plugins
from functions import idvals
from functions import notelist_data
from functions import params
from functions import auto
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
    add_sndinstparam(sng_instparams, 'attack', asdr_a, True)
    add_sndinstparam(sng_instparams, 'sustain', asdr_s, True)
    add_sndinstparam(sng_instparams, 'decay', asdr_d, True)
    add_sndinstparam(sng_instparams, 'release', asdr_r, True)

def add_sndinstparam(i_dict, i_name, i_value, i_auto): 
    if i_auto == True: i_dict[i_name] = {"value": i_value, "automation": []}
    else: i_dict[i_name] = {"value": i_value}

def cvpjidata_to_sngparam(i_dict, pluginid, i_name, i_fallback): 
    value = plugins.get_plug_dataval(cvpj_l, pluginid, i_name, i_fallback)
    add_sndinstparam(i_dict, i_name, value, False)

def cvpjiparam_to_sngparam(i_dict, pluginid, i_name, i_fallback, i_auto): 
    value = plugins.get_plug_param(cvpj_l, pluginid, i_name, i_fallback)[0]
    add_sndinstparam(i_dict, i_name, value, i_auto)

def add_fx(sng_trkdata, s_trackdata):
    sng_fxchain = sng_trkdata['effects']
    if 'chain_fx_audio' in s_trackdata:
        chainfxdata = s_trackdata['chain_fx_audio']
        for fxpluginid in chainfxdata:
            plugtype = plugins.get_plug_type(cvpj_l, fxpluginid)
            fxdata = data_values.nested_dict_get_value(cvpj_l, ['plugins', fxpluginid])
            fx_on, fx_wet = plugins.get_plug_fxdata(cvpj_l, fxpluginid)

            if plugtype == ['universal', 'eq-bands']:
                sng_fxdata = {}
                sng_fxdata['identifier'] = 'com.soundation.parametric-eq'
                sng_fxdata['bypass'] = not fx_on

                data_LP =        [False,0,0,0,0]
                data_Lowshelf =  [False,0,0,0,0]
                data_Peaks =     [[False,0,0,0,0],[False,0,0,0,0],[False,0,0,0,0],[False,0,0,0,0]]
                data_HighShelf = [False,0,0,0,0]
                data_HP =        [False,0,0,0,0]

                banddata = plugins.get_eqband(cvpj_l, fxpluginid, None)

                for s_band in banddata:
                    bandtype = s_band['type']

                    band_on = float(s_band['on'])
                    band_freq = s_band['freq']
                    band_gain = s_band['gain']
                    band_res = s_band['var']

                    band_freq = math.log(band_freq / 20) / math.log(1000)
                    band_gain = (band_gain/40)+0.5
                    band_res = math.log(band_res / 0.1) / math.log(162)

                    part = [True, band_on, band_freq, band_gain, band_res]

                    if bandtype == 'low_pass' and band_on: data_LP = part
                    if bandtype == 'low_shelf' and band_on: data_Lowshelf = part
                    if bandtype == 'peak' and band_on: 
                        for peaknum in range(4):
                            peakdata = data_Peaks[peaknum]
                            if peakdata[0] == False: 
                                data_Peaks[peaknum] = part
                                break
                    if bandtype == 'high_shelf' and band_on: data_HighShelf = part
                    if bandtype == 'high_pass' and band_on: data_HP = part

                gain_out = plugins.get_plug_param(cvpj_l, fxpluginid, 'gain_out', 0)[0]

                add_sndinstparam(sng_fxdata, 'highshelf_enable', data_HighShelf[1], True)
                add_sndinstparam(sng_fxdata, 'highshelf_freq', data_HighShelf[2], True)
                add_sndinstparam(sng_fxdata, 'highshelf_gain', data_HighShelf[3], True)
                add_sndinstparam(sng_fxdata, 'highshelf_res', data_HighShelf[4], True)

                add_sndinstparam(sng_fxdata, 'hpf_enable', data_HP[1], True)
                add_sndinstparam(sng_fxdata, 'hpf_freq', data_HP[2], True)
                add_sndinstparam(sng_fxdata, 'hpf_res', data_HP[4], True)
                add_sndinstparam(sng_fxdata, 'hpf_slope', 1.0, True)

                add_sndinstparam(sng_fxdata, 'lowshelf_enable', data_Lowshelf[1], True)
                add_sndinstparam(sng_fxdata, 'lowshelf_freq', data_Lowshelf[2], True)
                add_sndinstparam(sng_fxdata, 'lowshelf_gain', data_Lowshelf[3], True)
                add_sndinstparam(sng_fxdata, 'lowshelf_res', data_Lowshelf[4], True)

                add_sndinstparam(sng_fxdata, 'lpf_enable', data_LP[1], True)
                add_sndinstparam(sng_fxdata, 'lpf_freq', data_LP[2], True)
                add_sndinstparam(sng_fxdata, 'lpf_res', data_LP[4], True)
                add_sndinstparam(sng_fxdata, 'lpf_slope', 1.0, True)

                add_sndinstparam(sng_fxdata, 'master_gain', (gain_out/40)+0.5, True)

                for peaknum in range(4):
                    peakstr = str(peaknum+1)
                    add_sndinstparam(sng_fxdata, 'peak'+peakstr+'_enable', data_Peaks[peaknum][1], True)
                    add_sndinstparam(sng_fxdata, 'peak'+peakstr+'_freq', data_Peaks[peaknum][2], True)
                    add_sndinstparam(sng_fxdata, 'peak'+peakstr+'_gain', data_Peaks[peaknum][3], True)
                    add_sndinstparam(sng_fxdata, 'peak'+peakstr+'_res', data_Peaks[peaknum][4], True)

                sng_fxchain.append(sng_fxdata)


            if plugtype[0] == 'native-soundation':
                fxpluginname = plugtype[1]
                sng_fxdata = {}
                sng_fxdata['identifier'] = fxpluginname
                sng_fxdata['bypass'] = not fx_on

                if fxpluginname == 'com.soundation.compressor': snd_params = ['gain','release','ratio','threshold','attack']
                elif fxpluginname == 'com.soundation.degrader': snd_params = ['gain','rate','reduction','mix']
                elif fxpluginname == 'com.soundation.delay': snd_params = ['dry','feedback','feedback_filter','timeBpmSync','timeL','timeLSynced','timeR','timeRSynced','wet']
                elif fxpluginname == 'com.soundation.distortion': snd_params = ['gain','volume','mode']
                elif fxpluginname == 'com.soundation.equalizer': snd_params = ['low','mid','high']
                elif fxpluginname == 'com.soundation.fakie': snd_params = ['attack','hold','release','depth']
                elif fxpluginname == 'com.soundation.filter': snd_params = ['cutoff','resonance','mode']
                elif fxpluginname == 'com.soundation.limiter': snd_params = ['attack','gain','release','threshold']
                elif fxpluginname == 'com.soundation.parametric-eq': snd_params = ["highshelf_enable", "highshelf_freq", "highshelf_gain", "highshelf_res", "hpf_enable", "hpf_freq", "hpf_res", "hpf_slope", "lowshelf_enable", "lowshelf_freq", "lowshelf_gain", "lowshelf_res", "lpf_enable", "lpf_freq", "lpf_res", "lpf_slope", "master_gain", "peak1_enable", "peak1_freq", "peak1_gain", "peak1_res", "peak2_enable", "peak2_freq", "peak2_gain", "peak2_res", "peak3_enable", "peak3_freq", "peak3_gain", "peak3_res", "peak4_enable", "peak4_freq", "peak4_gain", "peak4_res"]
                elif fxpluginname == 'com.soundation.phaser': snd_params = ['rateBpmSync','rateSynced','feedback','rate','range','freq','wet','dry']
                elif fxpluginname == 'com.soundation.reverb': snd_params = ['size','damp','width','wet','dry']
                elif fxpluginname == 'com.soundation.tremolo': snd_params = ['speed','depth','phase']
                elif fxpluginname == 'com.soundation.wubfilter': snd_params = ['type','cutoff','resonance','drive','lfo_type','lfo_speed','lfo_depth']

                for snd_param in snd_params:
                    cvpjiparam_to_sngparam(sng_fxdata, fxpluginid, snd_param, 0, True)

                sng_fxchain.append(sng_fxdata)

def cvpjauto_to_sngauto(autopoints, ticks):
    sngauto = []
    for autopoint in autopoints:
        sngauto.append({"pos": autopoint['position']*ticks, "value": autopoint['value']})
    return sngauto

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
        cvpj_l = json.loads(convproj_json)
        bpm = params.get(cvpj_l, [], 'bpm', 120)[0]

        sng_output = {}
        sng_output["version"] = 2.3
        sng_output["studio"] = "3.10.7"
        sng_output["bpm"] = int(bpm)
        sng_output["timeSignature"] = "4/4"
        if 'timesig' in cvpj_l: 
            beatNumerator, beatDenominator = cvpj_l['timesig']
            sng_output["timeSignature"] = str(beatNumerator)+'/'+str(beatDenominator)
        sng_output["looping"] = False
        sng_output["loopStart"] = 0
        sng_output["loopEnd"] = 0
        sng_channels = sng_output["channels"] = []

        idvals_inst_gm2 = idvals.parse_idvalscsv('data_idvals/soundation_gm_inst.csv')

        bpmdiv = 120/bpm
        ticksdiv = 5512*bpmdiv

        #sng_master = makechannel("master")
        #sng_master['name'] = "Master Channel"
        #if 'track_master' in cvpj_l: 
        #    cvpj_master = cvpj_l['track_master']
        #    sng_master['name'] = data_values.get_value(cvpj_master, 'name', 'Master Channel')
        #    sng_master['volume'] = data_values.get_value(cvpj_master, 'vol', 1.0)
        #    add_fx(sng_master, cvpj_master)
        #sng_channels.append(sng_master)

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

        for cvpj_trackid, s_trackdata, track_placements in tracks_r.iter(cvpj_l):
            tracktype = s_trackdata['type']
            if tracktype == 'instrument':
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

                sng_instparams = sng_trkdata['instrument'] = {"identifier": "com.soundation.GM-2"}

                cvpjauto_vol = auto_nopl.getpoints(cvpj_l, ['track',cvpj_trackid,'vol'])
                if cvpjauto_vol != None:
                    cvpjauto_vol = auto.remove_instant(cvpjauto_vol, 0, False)
                    sng_trkdata['volumeAutomation'] = cvpjauto_to_sngauto(cvpjauto_vol, ticksdiv)
                cvpjauto_pan = auto_nopl.getpoints(cvpj_l, ['track',cvpj_trackid,'pan'])
                if cvpjauto_pan != None:
                    cvpjauto_pan = auto.remove_instant(cvpjauto_pan, 0, False)
                    sng_trkdata['panAutomation'] = cvpjauto_to_sngauto(auto.multiply_nopl(cvpjauto_pan, 1, 0.5), ticksdiv)

                inst_supported = False

                pluginid = data_values.nested_dict_get_value(s_trackdata, ['instdata', 'pluginid'])

                if pluginid != None:
                    plugtype = plugins.get_plug_type(cvpj_l, pluginid)
                    a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = plugins.get_asdr_env(cvpj_l, pluginid, 'vol')

                    if plugtype[0] == 'native-soundation':
                        inst_supported = True
                        sng_instparams['identifier'] = plugtype[1]
                        if plugtype[1] == 'com.soundation.GM-2':
                            cvpjidata_to_sngparam(sng_instparams, pluginid, 'sample_pack', '2_0_Bright_Yamaha_Grand.smplpck')
                            a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = plugins.get_asdr_env(cvpj_l, pluginid, 'vol')
                            set_asdr(sng_instparams, a_attack, a_sustain, a_decay, a_release)

                        elif plugtype[1] == 'com.soundation.SAM-1':
                            sample_pack = plugins.get_plug_dataval(cvpj_l, pluginid, 'sample_pack', None)
                            sng_instparams['sample_pack'] = sample_pack
                            a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = plugins.get_asdr_env(cvpj_l, pluginid, 'vol')
                            set_asdr(sng_instparams, a_attack, a_sustain, a_decay, a_release)

                        elif plugtype[1] == 'com.soundation.simple':

                            for oscnum in range(4):
                                for paramtype in ['detune','pitch','type','vol']:
                                    cvpjiparam_to_sngparam(sng_instparams, pluginid, 'osc_'+str(oscnum)+'_'+paramtype, 0, True)

                            f_predelay, f_attack, f_hold, f_decay, f_sustain, f_release, f_amount = plugins.get_asdr_env(cvpj_l, pluginid, 'cutoff')
                            add_sndinstparam(sng_instparams, 'filter_attack', f_attack, True)
                            add_sndinstparam(sng_instparams, 'filter_decay', f_decay, True)
                            add_sndinstparam(sng_instparams, 'filter_sustain', f_sustain, True)
                            add_sndinstparam(sng_instparams, 'filter_release', f_release, True)
                            add_sndinstparam(sng_instparams, 'filter_int', f_amount, True)

                            f_enabled, f_cutoff, f_reso, f_type, f_subtype = plugins.get_filter(cvpj_l, pluginid)
                            add_sndinstparam(sng_instparams, 'filter_cutoff', xtramath.between_to_one(20, 7500, f_cutoff), True)
                            add_sndinstparam(sng_instparams, 'filter_resonance', f_reso, True)

                            for snd_param in ['noise_vol', 'noise_color']:
                                cvpjiparam_to_sngparam(sng_instparams, pluginid, snd_param, 0, True)

                        elif plugtype[1] == 'com.soundation.supersaw':
                            set_asdr(sng_instparams, a_attack, a_sustain, a_decay, a_release)
                            for snd_param in ["detune", "spread"]:
                                cvpjiparam_to_sngparam(sng_instparams, pluginid, snd_param, 0, True)

                        elif plugtype[1] == 'com.soundation.noiser':
                            set_asdr(sng_instparams, a_attack, a_sustain, a_decay, a_release)

                        elif plugtype[1] == 'com.soundation.drummachine':
                            for paramname in ["gain_2", "hold_1", "pitch_6", "gain_1", "decay_5", "gain_5", "hold_0", "hold_2", "pitch_7", "gain_0", "decay_6", "gain_3", "hold_5", "pitch_3", "decay_4", "pitch_4", "gain_6", "decay_7", "pitch_2", "hold_6", "decay_1", "decay_3", "decay_0", "decay_2", "gain_7", "pitch_0", "pitch_5", "hold_3", "pitch_1", "hold_4", "hold_7", "gain_4"]:
                                cvpjiparam_to_sngparam(sng_instparams, pluginid, paramname, 0, True)
                            cvpjidata_to_sngparam(sng_instparams, pluginid, 'kit_name', '')

                        elif plugtype[1] == 'com.soundation.spc':
                            for paramname in soundation_values.spc_vals():
                                cvpjiparam_to_sngparam(sng_instparams, pluginid, paramname, 0, True)
                            for dataname in ['cuts','envelopes']:
                                sng_instparams[dataname] = plugins.get_plug_dataval(cvpj_l, pluginid, dataname, '')

                        elif plugtype[1] == 'com.soundation.europa':
                            for paramname in soundation_values.europa_vals():
                                value = plugins.get_plug_dataval(cvpj_l, pluginid, paramname, '')
                                add_sndinstparam(sng_instparams, "/custom_properties/"+paramname, value, True)
                            add_sndinstparam(sng_instparams, "/soundation/sample", None, True)

                        elif plugtype[1] in ['com.soundation.va_synth','com.soundation.fm_synth','com.soundation.the_wub_machine','com.soundation.mono']:
                            if plugtype[1] == 'com.soundation.va_synth': snd_params = ["aatt", "adec", "arel", "asus", "fatt", "fdec", "fdyn", "feg", "ffreq", "frel", "fres", "fsus", "glide_bend", "glide_mode", "glide_rate", "lfolpf", "lfoosc", "lforate", "octave", "osc_2_fine", "osc_2_mix", "osc_2_noise", "osc_2_octave", "tune"]
                            elif plugtype[1] == 'com.soundation.fm_synth': snd_params = ['p'+str(x) for x in range(137)]
                            elif plugtype[1] == 'com.soundation.mono': snd_params = ['filter_int','cutoff','resonance','pw','filter_decay','mix','amp_decay','glide']
                            elif plugtype[1] == 'com.soundation.the_wub_machine': snd_params = ['filter_cutoff','filter_drive','filter_resonance','filter_type','filth_active','filth_amount','lfo_depth','lfo_keytracking','lfo_loop','lfo_phase','lfo_retrigger','lfo_speed','lfo_type','msl_amount','osc1_gain','osc1_glide','osc1_pan','osc1_pitch','osc1_shape','osc1_type','osc2_gain','osc2_glide','osc2_pan','osc2_pitch','osc2_shape','osc2_type','osc_sub_bypass_filter','osc_sub_gain','osc_sub_glide','osc_sub_shape','osc_sub_volume_lfo','reese_active','unison_active','unison_amount','unison_count']
                            for snd_param in snd_params:
                                cvpjiparam_to_sngparam(sng_instparams, pluginid, snd_param, 0, True)

                    elif plugtype[0] == 'midi':
                        inst_supported = True
                        midibank = plugins.get_plug_dataval(cvpj_l, pluginid, 'bank', 0)
                        midiinst = plugins.get_plug_dataval(cvpj_l, pluginid, 'inst', 0)+1
                        gm2_samplepack = idvals.get_idval(idvals_inst_gm2, str(midiinst)+'_'+str(midibank), 'url')
                        if gm2_samplepack == None and midibank not in [0, 128]:
                            gm2_samplepack = idvals.get_idval(idvals_inst_gm2, str(midiinst)+'_0', 'url')
                        add_sndinstparam(sng_instparams, 'sample_pack', gm2_samplepack, False)
                        add_sndinstparam(sng_instparams, 'attack', 0, True)
                        add_sndinstparam(sng_instparams, 'decay', 0, True)
                        add_sndinstparam(sng_instparams, 'sustain', 1, True)
                        add_sndinstparam(sng_instparams, 'release', 0, True)

                    elif plugtype[0] == 'retro':
                        if plugtype[1] == 'sine': gm2_samplepack = '81_8_Sine_Wave.smplpck'
                        if plugtype[1] == 'square': gm2_samplepack = '81_0_Square_Lead.smplpck'
                        if plugtype[1] == 'triangle': gm2_samplepack = '85_0_Charang.smplpck'
                        if plugtype[1] == 'saw': gm2_samplepack = '82_0_Saw_Wave.smplpck'
                        add_sndinstparam(sng_instparams, 'attack', 0, True)
                        add_sndinstparam(sng_instparams, 'decay', 0, True)
                        add_sndinstparam(sng_instparams, 'sustain', 1, True)
                        add_sndinstparam(sng_instparams, 'release', 0, True)

                if inst_supported == False: 
                    add_sndinstparam(sng_instparams, 'sample_pack', '2_0_Bright_Yamaha_Grand.smplpck', False)
                    if pluginid != None:
                        add_sndinstparam(sng_instparams, 'attack', a_attack, True)
                        add_sndinstparam(sng_instparams, 'decay', a_decay, True)
                        add_sndinstparam(sng_instparams, 'sustain', a_sustain, True)
                        add_sndinstparam(sng_instparams, 'release', a_release, True)
                    else:
                        add_sndinstparam(sng_instparams, 'attack', 0, True)
                        add_sndinstparam(sng_instparams, 'decay', 0, True)
                        add_sndinstparam(sng_instparams, 'sustain', 1, True)
                        add_sndinstparam(sng_instparams, 'release', 0, True)

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


                sng_channels.append(sng_trkdata)

                add_fx(sng_trkdata, s_trackdata)

        if 'timemarkers' in cvpj_l:
            for timemarkdata in cvpj_l['timemarkers']:
                if 'type' in timemarkdata:
                    if timemarkdata['type'] == 'loop_area':
                        sng_output["looping"] = True
                        sng_output["loopStart"] = int(timemarkdata['position']*ticksdiv)
                        sng_output["loopEnd"] = int(timemarkdata['end']*ticksdiv)

        with open(output_file, "w") as fileout:
            json.dump(sng_output, fileout, indent=2)