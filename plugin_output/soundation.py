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
from objects import dv_dataset
from objects import idvals
from functions_compat import trackfx_to_numdata
from functions_plugin import soundation_values

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

def set_asdr(sng_instparams, plugin_obj):
    adsr_obj = plugin_obj.env_asdr_get('vol')
    add_sndinstparam(sng_instparams, 'attack', adsr_obj.attack, [])
    add_sndinstparam(sng_instparams, 'sustain', adsr_obj.sustain, [])
    add_sndinstparam(sng_instparams, 'decay', adsr_obj.decay, [])
    add_sndinstparam(sng_instparams, 'release', adsr_obj.release, [])

def add_sndinstparam(i_dict, i_name, i_value, i_auto): 
    if i_auto != None: i_dict[i_name] = {"value": i_value, "automation": i_auto}
    else: i_dict[i_name] = {"value": i_value}

def cvpjidata_to_sngparam(plugin_obj, i_dict, pluginid, i_name, i_fallback): 
    value = plugin_obj.datavals.get(i_name, i_fallback)
    add_sndinstparam(i_dict, i_name, value, None)

def cvpjiparam_to_sngparam(plugin_obj, i_dict, pluginid, i_name, i_fallback, i_auto): 
    value = plugin_obj.params.get(i_name, i_fallback).value
    add_sndinstparam(i_dict, i_name, value, i_auto)


def add_fx(convproj_obj, sng_trkdata, fxchain_audio):
    sng_fxchain = sng_trkdata['effects']
    for pluginid in fxchain_audio:
        plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
        if plugin_found: 
            if plugin_obj.check_wildmatch('native-soundation', None):
                fx_on, fx_wet = plugin_obj.fxdata_get()
                sng_fxdata = {}
                sng_fxdata['identifier'] = plugin_obj.plugin_subtype
                sng_fxdata['bypass'] = not fx_on
                paramlist = dataset.params_list('plugin', plugin_obj.plugin_subtype)
                if paramlist:
                    for snd_param in paramlist:
                        ap_f, ap_d = convproj_obj.automation.get_autopoints(['plugin',pluginid,snd_param])
                        autodata = cvpjauto_to_sngauto(autodata, ticksdiv) if ap_f else []
                        cvpjiparam_to_sngparam(plugin_obj, sng_fxdata, pluginid, snd_param, 0, autodata)
                sng_fxchain.append(sng_fxdata)


def cvpjauto_to_sngauto(autopoints):
    return [{"pos": autopoint.pos, "value": autopoint.value} for autopoint in autopoints.iter()]

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

def trackparams(track_obj, sng_trkdata, visual_obj, params_obj, start_str, fallbackname):
    trackcolor = colors.rgb_float_to_hex(visual_obj.color if visual_obj.color else [0.5,0.5,0.5]) 
    sng_trkdata['name'] = start_str+(visual_obj.name if visual_obj.name else fallbackname)
    sng_trkdata['color'] = '#'+trackcolor.upper()
    sng_trkdata['volume'] = params_obj.get('vol', 1).value
    sng_trkdata['pan'] = 0.5 + params_obj.get('pan', 0).value/2
    muteddata = params_obj.get('enabled', True).value
    if muteddata != None: sng_trkdata['mute'] = not muteddata


def auto_volpan(convproj_obj, sng_trkdata, autoloc):
    v_ap_f, v_ap_d = convproj_obj.automation.get_autopoints(autoloc+['vol'])
    p_ap_f, p_ap_d = convproj_obj.automation.get_autopoints(autoloc+['pan'])
    if v_ap_f:
        v_ap_d.remove_instant()
        sng_trkdata['volumeAutomation'] = cvpjauto_to_sngauto(v_ap_d)
    if p_ap_f:
        p_ap_d.remove_instant()
        p_ap_d.addmul(1, 0.5)
        sng_trkdata['panAutomation'] = cvpjauto_to_sngauto(p_ap_d)

class output_soundation(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Soundation'
    def getshortname(self): return 'soundation'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Soundation'
        dawinfo_obj.file_ext = 'sng'
        dawinfo_obj.placement_cut = True
        dawinfo_obj.placement_loop = ['loop']
        dawinfo_obj.plugin_included = ['sampler:single','synth-nonfree:europa','native-soundation','midi']
        dawinfo_obj.auto_types = ['nopl_points']
    def parse(self, convproj_obj, output_file):
        global dataset

        convproj_obj.change_timings(20645, False)

        dataset = dv_dataset.dataset('./data_dset/soundation.dset')
        dataset_synth_nonfree = dv_dataset.dataset('./data_dset/synth_nonfree.dset')

        bpm = int(convproj_obj.params.get('bpm', 120).value)

        sng_output = {}
        sng_output["version"] = 2.3
        sng_output["studio"] = "3.10.7"
        sng_output["bpm"] = int(bpm)
        beatNumerator, beatDenominator = convproj_obj.timesig
        sng_output["timeSignature"] = str(beatNumerator)+'/'+str(beatDenominator)

        sng_output["looping"] = convproj_obj.loop_active
        sng_output["loopStart"] = convproj_obj.loop_start
        sng_output["loopEnd"] = convproj_obj.loop_end

        sng_channels = sng_output["channels"] = []

        idvals_inst_gm2 = idvals.idvals('data_idvals/soundation_gm_inst.csv')

        bpmdiv = 120/bpm

        sng_master = makechannel("master")
        sng_master['name'] = convproj_obj.track_master.visual.name if convproj_obj.track_master.visual.name else "Master Channel"
        sng_master['volume'] = convproj_obj.track_master.params.get('vol', 1).value
        add_fx(convproj_obj, sng_master, convproj_obj.track_master.fxslots_audio)
        sng_channels.append(sng_master)

        auto_volpan(convproj_obj, sng_master, ['master'])
        ts_numerator, ts_denominator = convproj_obj.timesig
        sng_output["timeSignature"] = str(ts_numerator)+'/'+str(ts_denominator)

        t2m = trackfx_to_numdata.to_numdata()
        output_ids = t2m.trackfx_to_numdata(convproj_obj, 0)

        return_objs = {}

        for returnid, return_obj in convproj_obj.track_master.returns.items(): 
            return_objs[returnid] = return_obj

        for output_id in output_ids:

            if output_id[1] == 'return':
                return_obj = return_objs[output_id[2]]
                trackcolor = colors.rgb_float_to_hex(return_obj.visual.color if return_obj.visual.color else [0.5,0.5,0.5]) 
                sng_trkdata = makechannel("effect")
                trackparams(return_obj, sng_trkdata, return_obj.visual, return_obj.params, '[R] ', output_id[2])
                add_fx(convproj_obj, sng_trkdata, return_obj.fxslots_audio)
                for sendpart in output_id[4]: add_send(sendpart, sng_trkdata, 1)
                add_send(output_id[3], sng_trkdata, 0)
                sng_channels.append(sng_trkdata)

            if output_id[1] == 'group':
                grp_f, grp_obj = convproj_obj.find_group(output_id[2])

                sng_trkdata = makechannel("effect")
                trackparams(grp_obj, sng_trkdata, grp_obj.visual, grp_obj.params, '[G] ', output_id[2])
                auto_volpan(convproj_obj, sng_trkdata, ['group', output_id[2]])
                add_fx(convproj_obj, sng_trkdata, grp_obj.fxslots_audio)
                for sendpart in output_id[4]: add_send(sendpart, sng_trkdata, 1)
                add_send(output_id[3], sng_trkdata, 0)
                sng_channels.append(sng_trkdata)

            if output_id[1] == 'track':
                track_obj = convproj_obj.track_data[output_id[2]]

                sng_trkdata = makechannel("instrument")
                trackparams(track_obj, sng_trkdata, track_obj.visual, track_obj.params, '', output_id[2])
                sng_trkdata['solo'] = int(track_obj.params.get('solo', False).value)
                add_fx(convproj_obj, sng_trkdata, track_obj.fxslots_audio)
                auto_volpan(convproj_obj, sng_trkdata, ['track', output_id[2]])

                if track_obj.type == 'instrument':
                    sng_instparams = sng_trkdata['instrument'] = {"identifier": "com.soundation.GM-2"}

                    inst_supported = False
                    plugin_found, plugin_obj = convproj_obj.get_plugin(track_obj.inst_pluginid)
                    if plugin_found:
                        vol_adsr_obj = plugin_obj.env_asdr_get('vol')

                        if plugin_obj.check_match('synth-nonfree', 'europa'):
                            inst_supported = True
                            sng_instparams['identifier'] = 'com.soundation.europa'
                            europaparamlist = dataset_synth_nonfree.params_list('plugin', 'europa')
                            if europaparamlist:
                                for paramname in europaparamlist:
                                    param = dataset_synth_nonfree.params_i_get('plugin', 'europa', paramname)
                                    if not param[0]: eur_value_value = plugin_obj.params.get(paramname, 0).value
                                    else:
                                        eur_value_value = plugin_obj.datavals.get(paramname, 0)
                                        if paramname in ['Curve1','Curve2','Curve3','Curve4','Curve']: eur_value_value = ','.join([str(x).zfill(2) for x in eur_value_value])
                                    add_sndinstparam(sng_instparams, "/custom_properties/"+paramname, eur_value_value, [])
                                add_sndinstparam(sng_instparams, "/soundation/sample", None, [])

                        if plugin_obj.check_wildmatch('native-soundation', None):
                            inst_supported = True
                            sng_instparams['identifier'] = plugin_obj.plugin_subtype
                            if plugin_obj.plugin_subtype == 'com.soundation.GM-2':
                                cvpjidata_to_sngparam(plugin_obj, sng_instparams, track_obj.inst_pluginid, 'sample_pack', '2_0_Bright_Yamaha_Grand.smplpck')
                                set_asdr(sng_instparams, plugin_obj)

                            elif plugin_obj.plugin_subtype == 'com.soundation.SAM-1':
                                sample_pack = plugin_obj.datavals.get('sample_pack', None)
                                sng_instparams['sample_pack'] = sample_pack
                                set_asdr(sng_instparams, plugin_obj)

                            elif plugin_obj.plugin_subtype == 'com.soundation.simple':

                                for oscnum in range(4):
                                    for paramtype in ['detune','pitch','type','vol']:
                                        cvpjiparam_to_sngparam(plugin_obj, sng_instparams, track_obj.inst_pluginid, 'osc_'+str(oscnum)+'_'+paramtype, 0, [])

                                filt_adsr_obj = plugin_obj.env_asdr_get('cutoff')
                                add_sndinstparam(sng_instparams, 'filter_attack', filt_adsr_obj.attack, [])
                                add_sndinstparam(sng_instparams, 'filter_decay', filt_adsr_obj.sustain, [])
                                add_sndinstparam(sng_instparams, 'filter_sustain', filt_adsr_obj.decay, [])
                                add_sndinstparam(sng_instparams, 'filter_release', filt_adsr_obj.release, [])
                                add_sndinstparam(sng_instparams, 'filter_int', filt_adsr_obj.amount, [])

                                add_sndinstparam(sng_instparams, 'filter_cutoff', xtramath.between_to_one(20, 7500, plugin_obj.filter.freq), [])
                                add_sndinstparam(sng_instparams, 'filter_resonance', plugin_obj.filter.q, [])

                                for snd_param in ['noise_vol', 'noise_color']:
                                    cvpjiparam_to_sngparam(plugin_obj, sng_instparams, track_obj.inst_pluginid, snd_param, 0, [])

                            elif plugin_obj.plugin_subtype == 'com.soundation.supersaw':
                                set_asdr(sng_instparams, plugin_obj)
                                for snd_param in ["detune", "spread"]:
                                    cvpjiparam_to_sngparam(plugin_obj, sng_instparams, track_obj.inst_pluginid, snd_param, 0, [])

                            elif plugin_obj.plugin_subtype == 'com.soundation.noiser':
                                set_asdr(sng_instparams, plugin_obj)

                            elif plugin_obj.plugin_subtype == 'com.soundation.drummachine':
                                for paramname in ["gain_2", "hold_1", "pitch_6", "gain_1", "decay_5", "gain_5", "hold_0", "hold_2", "pitch_7", "gain_0", "decay_6", "gain_3", "hold_5", "pitch_3", "decay_4", "pitch_4", "gain_6", "decay_7", "pitch_2", "hold_6", "decay_1", "decay_3", "decay_0", "decay_2", "gain_7", "pitch_0", "pitch_5", "hold_3", "pitch_1", "hold_4", "hold_7", "gain_4"]:
                                    cvpjiparam_to_sngparam(plugin_obj, sng_instparams, track_obj.inst_pluginid, paramname, 0, [])
                                cvpjidata_to_sngparam(plugin_obj, sng_instparams, track_obj.inst_pluginid, 'kit_name', '')

                            elif plugin_obj.plugin_subtype == 'com.soundation.spc':
                                for paramname in soundation_values.spc_vals():
                                    cvpjiparam_to_sngparam(plugin_obj, sng_instparams, track_obj.inst_pluginid, paramname, 0, [])
                                for dataname in ['cuts','envelopes']:
                                    sng_instparams[dataname] = plugin_obj.datavals.get(dataname, '')

                            elif plugin_obj.plugin_subtype in ['com.soundation.va_synth','com.soundation.fm_synth','com.soundation.the_wub_machine','com.soundation.mono']:
                                if plugin_obj.plugin_subtype == 'com.soundation.va_synth': snd_params = ["aatt", "adec", "arel", "asus", "fatt", "fdec", "fdyn", "feg", "ffreq", "frel", "fres", "fsus", "glide_bend", "glide_mode", "glide_rate", "lfolpf", "lfoosc", "lforate", "octave", "osc_2_fine", "osc_2_mix", "osc_2_noise", "osc_2_octave", "tune"]
                                elif plugin_obj.plugin_subtype == 'com.soundation.fm_synth': snd_params = ['p'+str(x) for x in range(137)]
                                elif plugin_obj.plugin_subtype == 'com.soundation.mono': snd_params = ['filter_int','cutoff','resonance','pw','filter_decay','mix','amp_decay','glide']
                                elif plugin_obj.plugin_subtype == 'com.soundation.the_wub_machine': snd_params = ['filter_cutoff','filter_drive','filter_resonance','filter_type','filth_active','filth_amount','lfo_depth','lfo_keytracking','lfo_loop','lfo_phase','lfo_retrigger','lfo_speed','lfo_type','msl_amount','osc1_gain','osc1_glide','osc1_pan','osc1_pitch','osc1_shape','osc1_type','osc2_gain','osc2_glide','osc2_pan','osc2_pitch','osc2_shape','osc2_type','osc_sub_bypass_filter','osc_sub_gain','osc_sub_glide','osc_sub_shape','osc_sub_volume_lfo','reese_active','unison_active','unison_amount','unison_count']
                                for snd_param in snd_params:
                                    cvpjiparam_to_sngparam(plugin_obj, sng_instparams, track_obj.inst_pluginid, snd_param, 0, [])

                    if not inst_supported and plugin_obj:
                        if len(plugin_obj.oscs) == 1:
                            s_osc = plugin_obj.oscs[0]
                            if s_osc.shape == 'sine': gm2_samplepack = '81_8_Sine_Wave.smplpck'
                            if s_osc.shape == 'square': gm2_samplepack = '81_0_Square_Lead.smplpck'
                            if s_osc.shape == 'triangle': gm2_samplepack = '85_0_Charang.smplpck'
                            if s_osc.shape == 'saw': gm2_samplepack = '82_0_Saw_Wave.smplpck'
                            add_sndinstparam(sng_instparams, 'sample_pack', gm2_samplepack, None)
                            set_asdr(sng_instparams, plugin_obj)
                        else:
                            midi_found, midi_bank, midi_inst, midi_drum = track_obj.get_midi(convproj_obj)
                            gm2_samplepack = idvals_inst_gm2.get_idval(str(midi_inst+1)+'_'+str(midi_bank), 'url')
                            if midi_drum: gm2_samplepack = idvals_inst_gm2.get_idval(str(midi_bank+127)+'_0', 'url')
                            add_sndinstparam(sng_instparams, 'sample_pack', gm2_samplepack, None)
                            set_asdr(sng_instparams, plugin_obj)
                    else:
                        midi_found, midi_bank, midi_inst, midi_drum = track_obj.get_midi(convproj_obj)
                        gm2_samplepack = idvals_inst_gm2.get_idval(str(midi_inst+1)+'_'+str(midi_bank), 'url')
                        if midi_drum: gm2_samplepack = idvals_inst_gm2.get_idval(str(midi_bank+127)+'_0', 'url')
                        add_sndinstparam(sng_instparams, 'sample_pack', gm2_samplepack, None)

                    if track_obj.visual.name: sng_trkdata['userSetName'] = track_obj.visual.name
                    sng_trkdata['regions'] = []

                    for notespl_obj in track_obj.placements.pl_notes:
                        sng_region = {}
                        if notespl_obj.visual.color: sng_region["color"] = int.from_bytes(struct.pack("3B", *colors.rgb_float_to_rgb_int(notespl_obj.visual.color)), "little")
                        sng_region["position"] = int(notespl_obj.position)
                        sng_region["length"] = int(notespl_obj.duration)
                        sng_region["loopcount"] = 1
                        sng_region["contentPosition"] = 0

                        if notespl_obj.cut_type in ['loop', 'loop_off']:
                            sng_region["length"] = notespl_obj.cut_data['loopend']
                            sng_region["loopcount"] = notespl_obj.duration/notespl_obj.cut_data['loopend']
                            if notespl_obj.cut_type == 'loop_off': 
                                sng_region["contentPosition"] = -(notespl_obj.cut_data['start'])

                        if notespl_obj.cut_type == 'cut': 
                            sng_region["contentPosition"] = -(notespl_obj.cut_data['start'])

                        sng_region["type"] = 2
                        sng_region["notes"] = []
                        notespl_obj.notelist.sort()

                        for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
                            for t_key in t_keys:
                                if 0 <= t_key+60 <= 128:
                                    sng_note = {}
                                    sng_note["note"] = int(t_key+60)
                                    sng_note["velocity"] = t_vol
                                    sng_note["position"] = int(t_pos)
                                    sng_note["length"] = int(t_dur)
                                    sng_region["notes"].append(sng_note)

                        sng_trkdata['regions'].append(sng_region)

                add_fx(convproj_obj, sng_trkdata, track_obj.fxslots_audio)
                for sendpart in output_id[4]: add_send(sendpart, sng_trkdata, 1)
                add_send(output_id[3], sng_trkdata, 0)
                sng_channels.append(sng_trkdata)

        sng_output["looping"] = convproj_obj.loop_active
        sng_output["loopStart"] = int(convproj_obj.loop_start)
        sng_output["loopEnd"] = int(convproj_obj.loop_end)

        with open(output_file, "w") as fileout: json.dump(sng_output, fileout, indent=4)