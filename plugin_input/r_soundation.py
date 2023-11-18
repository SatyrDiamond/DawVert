# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions import plugins
from functions import xtramath
from functions import note_data
from functions import placement_data
from functions import data_dataset
from functions import song
from functions_tracks import auto_nopl
from functions_tracks import auto_data
from functions_tracks import fxslot
from functions_tracks import tracks_r
from functions_tracks import tracks_master
import plugin_input
import struct
import json
import math



def get_paramval(i_params, i_name):
    outval = 0
    automation = []
    if i_name in i_params:
        if 'value' in i_params[i_name]: outval = i_params[i_name]['value']
        if 'automation' in i_params[i_name]: automation = i_params[i_name]['automation']
    return outval, automation

def get_param(i_name, plugindata, i_params):
    value_out, automation = get_paramval(i_params, i_name)
    plugindata.param_add(i_name, value_out, 'float', i_name)
    return automation

def get_asdr(pluginid, plugindata, sound_instdata):
    asdr_a = get_paramval(sound_instdata, 'attack')[0]
    asdr_s = get_paramval(sound_instdata, 'sustain')[0]
    asdr_d = get_paramval(sound_instdata, 'decay')[0]
    asdr_r = get_paramval(sound_instdata, 'release')[0]
    plugindata.asdr_env_add('vol', 0, asdr_a, 0, asdr_d, asdr_s, asdr_r, 1)

def parse_clip_notes(sndstat_clip):
    cvpj_notelist = []
    sndstat_clip_position = sndstat_clip['position']/ticksdiv
    sndstat_clip_duration = sndstat_clip['length']/ticksdiv
    sndstat_clip_contentPosition = sndstat_clip['contentPosition']/ticksdiv
    sndstat_clip_loopcount = sndstat_clip['loopcount']

    sndstat_clip_loopduration = sndstat_clip_duration*sndstat_clip_loopcount

    cvpj_pldata = {}
    if 'color' in sndstat_clip: 
        if isinstance(sndstat_clip['color'],str): 
            clipcolor = colors.hex_to_rgb_float(sndstat_clip['color'])
        else: 
            clipcolor = struct.unpack("4B", struct.pack("i", sndstat_clip["color"]))
            clipcolor = [clipcolor[2]/255, clipcolor[1]/255, clipcolor[0]/255]
            clipcolor = colors.darker(clipcolor, 0.3)

        cvpj_pldata["color"] = clipcolor

    cvpj_pldata["position"] = sndstat_clip_position
    cvpj_pldata["duration"] = sndstat_clip_loopduration
    cvpj_pldata['cut'] = placement_data.cutloopdata(-sndstat_clip_contentPosition, -sndstat_clip_contentPosition, sndstat_clip_duration)

    cvpj_notelist = note_data.notelist(ticksdiv*4, None)
    for sndstat_note in sndstat_clip['notes']: cvpj_notelist.add_r(sndstat_note['position'], sndstat_note['length'], sndstat_note['note']-60, sndstat_note['velocity'], None)
    cvpj_pldata["notelist"] = cvpj_notelist.to_cvpj()
    placement_data.unminus(cvpj_pldata)
    return cvpj_pldata

def sngauto_to_cvpjauto(autopoints):
    sngauto = []
    for autopoint in autopoints:
        sngauto.append({"position": autopoint['pos']//ticksdiv, "value": float(autopoint['value'])})
    return sngauto

def autoall_cvpj_to_sng(sng_device, cvpj_plugindata, fxpluginname):
    paramlist = dataset.params_list('plugin', fxpluginname)
    if paramlist:
        for paramid in paramlist:
            outval, outauto = get_paramval(sng_device, paramid)
            cvpj_plugindata.param_add_dset(paramid, outval, dataset, 'plugin', fxpluginname)
            if outauto not in [None, []]: auto_data.add_pl(cvpj_l, 'float', ['plugin',fxpluginid,paramid], auto_nopl.to_pl(sngauto_to_cvpjauto(outauto)))

def eq_calc_q(band_type, q_val):
    if band_type in ['low_pass', 'high_pass']:
        q_val = q_val*math.log(162)
        q_val = 0.1 * math.exp(q_val)
        q_val = xtramath.logpowmul(q_val, 0.5)
    elif band_type in ['low_shelf', 'high_shelf']:
        q_val = q_val*math.log(162)
        q_val = 0.1 * math.exp(q_val)
    else:
        q_val = q_val*math.log(162)
        #q_val = 0.1 * math.exp(q_val)
        q_val = xtramath.logpowmul(q_val, -1)
    return q_val

class input_soundation(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'soundation'
    def getname(self): return 'Soundation'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': ['loop', 'loop_off']
        }
    def parse(self, input_file, extra_param):
        global cvpj_l
        global ticksdiv
        global dataset

        bytestream = open(input_file, 'r')
        sndstat_data = json.load(bytestream)

        cvpj_l = {}

        dataset = data_dataset.dataset('./data_dset/soundation.dset')
        dataset_synth_nonfree = data_dataset.dataset('./data_dset/synth_nonfree.dset')

        timeSignaturesplit = sndstat_data['timeSignature'].split('/')
        song.add_timesig(cvpj_l, int(timeSignaturesplit[0]), int(timeSignaturesplit[1]))
        bpm = sndstat_data['bpm']
        song.add_param(cvpj_l, 'bpm', bpm)
        bpmdiv = 120/bpm
        sndstat_chans = sndstat_data['channels']

        ticksdiv = 5512*bpmdiv

        tracknum = 0
        for sndstat_chan in sndstat_chans:

            tracknum_hue = (tracknum/-11) - 0.2
            tracknum += 1
            sound_chan_type = sndstat_chan['type']
            trackid = 'soundation'+str(tracknum)
            trackcolor = colors.hex_to_rgb_float(sndstat_chan['color']) if 'color' in sndstat_chan else colors.hsv_to_rgb(tracknum_hue, 0.7, 0.7)

            ismaster = False
            if sound_chan_type == 'master':
                ismaster = True
                tracks_master.create(cvpj_l, sndstat_chan['volume'])
                tracks_master.visual(cvpj_l, name=sndstat_chan['name'])
                tracks_master.param_add(cvpj_l, 'pan', (sndstat_chan['pan']-0.5)*2, 'float')
                tracks_master.param_add(cvpj_l, 'enabled', int(not sndstat_chan['mute']), 'bool')
                tracks_master.param_add(cvpj_l, 'solo', int(sndstat_chan['solo']), 'bool')

                for autoname in [['vol','volumeAutomation'],['pan','panAutomation']]:
                    if sndstat_chan[autoname[1]] != []:
                        autodata = sngauto_to_cvpjauto(sndstat_chan[autoname[1]])
                        if autoname[0] == 'pan': autodata = auto.multiply_nopl(autodata, -1, 2)
                        auto_data.add_pl(cvpj_l, 'float', ['master',autoname[0]], auto_nopl.to_pl(autodata))

            if sound_chan_type == 'instrument':
                trackname = sndstat_chan['userSetName'] if 'userSetName' in sndstat_chan else sndstat_chan['name']
                tracks_r.track_create(cvpj_l, trackid, 'instrument')
                tracks_r.track_visual(cvpj_l, trackid, name=trackname, color=[trackcolor[0], trackcolor[1], trackcolor[2]])
                tracks_r.track_param_add(cvpj_l, trackid, 'vol', sndstat_chan['volume'], 'float')
                tracks_r.track_param_add(cvpj_l, trackid, 'pan', (sndstat_chan['pan']-0.5)*2, 'float')
                tracks_r.track_param_add(cvpj_l, trackid, 'enabled', int(not sndstat_chan['mute']), 'bool')
                tracks_r.track_param_add(cvpj_l, trackid, 'solo', int(sndstat_chan['solo']), 'bool')

                for autoname in [['vol','volumeAutomation'],['pan','panAutomation']]:
                    if sndstat_chan[autoname[1]] != []:
                        autodata = sngauto_to_cvpjauto(sndstat_chan[autoname[1]])
                        if autoname[0] == 'pan': autodata = auto.multiply_nopl(autodata, -1, 2)
                        auto_data.add_pl(cvpj_l, 'float', ['track',trackid,autoname[0]], auto_nopl.to_pl(autodata))

                sound_instdata = sndstat_chan['instrument']

                for sndstat_region in sndstat_chan['regions']:
                    tracks_r.add_pl(cvpj_l, trackid, 'notes', parse_clip_notes(sndstat_region))

                pluginid = plugins.get_id()
                tracks_r.track_inst_pluginid(cvpj_l, trackid, pluginid)
                if 'identifier' in sound_instdata:
                    instpluginname = sound_instdata['identifier']
                    inst_plugindata = None

                    if instpluginname == 'com.soundation.simple-sampler':
                        inst_plugindata = plugins.cvpj_plugin('sampler', '', None)

                        get_asdr(pluginid, inst_plugindata, sound_instdata)

                        v_gain = get_paramval(sound_instdata, 'gain')[0]
                        inst_plugindata.dataval_add('gain', v_gain)

                        v_start = get_paramval(sound_instdata, 'start')[0]
                        v_end = get_paramval(sound_instdata, 'end')[0]
                        inst_plugindata.dataval_add('start', v_start)
                        inst_plugindata.dataval_add('end', v_end)

                        v_loop_mode = get_paramval(sound_instdata, 'loop_mode')[0]
                        v_loop_start = get_paramval(sound_instdata, 'loop_start')[0]
                        v_loop_end = get_paramval(sound_instdata, 'loop_end')[0]

                        cvpj_loopdata = {}
                        if v_loop_mode != 0 :
                            cvpj_loopdata['enabled'] = 1
                            cvpj_loopdata['mode'] = "normal"
                            cvpj_loopdata['points'] = [v_loop_start, v_loop_end]
                        else: cvpj_loopdata['enabled'] = 0
                        inst_plugindata.dataval_add('loop', cvpj_loopdata)
                        inst_plugindata.dataval_add('point_value_type', "percent")

                        v_coarse = (get_paramval(sound_instdata, 'coarse')[0]-0.5)*2
                        v_fine = (get_paramval(sound_instdata, 'fine')[0]-0.5)*2
                        v_root_note = get_paramval(sound_instdata, 'root_note')[0]

                        tracks_r.track_param_add(cvpj_l, trackid, 'pitch', v_coarse*48 + v_fine, 'float')
                        tracks_r.track_dataval_add(cvpj_l, trackid, 'instdata', 'middlenote', v_root_note-60)

                        v_crossfade = get_paramval(sound_instdata, 'crossfade')[0]
                        v_playback_direction = get_paramval(sound_instdata, 'playback_direction')[0]
                        v_interpolation_mode = get_paramval(sound_instdata, 'interpolation_mode')[0]
                        v_release_mode = get_paramval(sound_instdata, 'release_mode')[0]
                        v_portamento_time = get_paramval(sound_instdata, 'portamento_time')[0]

                        if v_interpolation_mode == 0: cvpj_interpolation = "none"
                        if v_interpolation_mode == 1: cvpj_interpolation = "linear"
                        if v_interpolation_mode > 1: cvpj_interpolation = "sinc"
                        inst_plugindata.dataval_add('interpolation', cvpj_interpolation)

                    elif instpluginname == 'com.soundation.drummachine':
                        inst_plugindata = plugins.cvpj_plugin('deftype', 'native-soundation', instpluginname)
                        kit_name = get_paramval(sound_instdata, 'kit_name')[0]
                        for paramname in ["gain_2", "hold_1", "pitch_6", "gain_1", "decay_5", "gain_5", "hold_0", "hold_2", "pitch_7", "gain_0", "decay_6", "gain_3", "hold_5", "pitch_3", "decay_4", "pitch_4", "gain_6", "decay_7", "pitch_2", "hold_6", "decay_1", "decay_3", "decay_0", "decay_2", "gain_7", "pitch_0", "pitch_5", "hold_3", "pitch_1", "hold_4", "hold_7", "gain_4"]:
                            get_param(paramname, inst_plugindata, sound_instdata)
                        inst_plugindata.dataval_add('kit_name', kit_name)

                    elif instpluginname == 'com.soundation.europa':
                        inst_plugindata = plugins.cvpj_plugin('deftype', 'synth-nonfree', 'europa')
                        paramlist = dataset_synth_nonfree.params_list('plugin', 'europa')
                        for paramid in paramlist:
                            outval = None
                            param = dataset_synth_nonfree.params_i_get('plugin', 'europa', paramid)
                            sng_paramid = "/custom_properties/"+param[5]
                            if sng_paramid in sound_instdata:
                                if 'value' in sound_instdata[sng_paramid]: outval = sound_instdata[sng_paramid]['value']
                            inst_plugindata.param_add_dset(paramid, outval, dataset_synth_nonfree, 'plugin', 'europa')

                    elif instpluginname == 'com.soundation.GM-2':
                        inst_plugindata = plugins.cvpj_plugin('deftype', 'native-soundation', instpluginname)
                        get_asdr(pluginid, inst_plugindata, sound_instdata)
                        if 'value' in sound_instdata['sample_pack']:
                            sample_pack = get_paramval(sound_instdata, 'sample_pack')[0]
                            inst_plugindata.dataval_add('sample_pack', sample_pack)

                    elif instpluginname == 'com.soundation.noiser':
                        inst_plugindata = plugins.cvpj_plugin('deftype', 'native-soundation', instpluginname)
                        get_asdr(pluginid, inst_plugindata, sound_instdata)
                            
                    elif instpluginname == 'com.soundation.SAM-1':
                        inst_plugindata = plugins.cvpj_plugin('deftype', 'native-soundation', instpluginname)
                        get_asdr(pluginid, inst_plugindata, sound_instdata)
                        sound_instdata['sample_pack'] = inst_plugindata.dataval_add('sample_pack', None)

                    elif instpluginname in ['com.soundation.fm_synth', 'com.soundation.mono', 'com.soundation.spc', 'com.soundation.supersaw', 'com.soundation.the_wub_machine', 'com.soundation.va_synth']:
                        inst_plugindata = plugins.cvpj_plugin('deftype', 'native-soundation', instpluginname)
                        paramlist = dataset.params_list('plugin', instpluginname)
                        for paramid in paramlist:
                            outval = None
                            if paramid in sound_instdata:
                                if 'value' in sound_instdata[paramid]: outval = sound_instdata[paramid]['value']
                            inst_plugindata.param_add_dset(paramid, outval, dataset, 'plugin', instpluginname)

                        if instpluginname == 'com.soundation.spc':
                            inst_plugindata.dataval_add('cuts', sound_instdata['cuts'])
                            inst_plugindata.dataval_add('envelopes', sound_instdata['envelopes'])

                        if instpluginname == 'com.soundation.supersaw':
                            get_asdr(pluginid, inst_plugindata, sound_instdata)

                    elif instpluginname == 'com.soundation.simple':
                        inst_plugindata = plugins.cvpj_plugin('deftype', 'native-soundation', instpluginname)
                        get_asdr(pluginid, inst_plugindata, sound_instdata)
                        asdrf_a = get_paramval(sound_instdata, 'filter_attack')[0]
                        asdrf_s = get_paramval(sound_instdata, 'filter_decay')[0]
                        asdrf_d = get_paramval(sound_instdata, 'filter_sustain')[0]
                        asdrf_r = get_paramval(sound_instdata, 'filter_release')[0]
                        asdrf_i = get_paramval(sound_instdata, 'filter_int')[0]
                        inst_plugindata.asdr_env_add('cutoff', 0, asdrf_a, 0, asdrf_d, asdrf_s, asdrf_r, asdrf_i)
                        filter_cutoff = xtramath.between_from_one(20, 7500, get_paramval(sound_instdata, 'filter_cutoff')[0])
                        filter_reso = get_paramval(sound_instdata, 'filter_resonance')
                        inst_plugindata.filter_add(True, filter_cutoff, filter_reso, 'lowpass', None)
                        for oscnum in range(4):
                            for paramtype in ['detune','pitch','type','vol']: get_param('osc_'+str(oscnum)+'_'+paramtype, inst_plugindata, sound_instdata)
                        for snd_param in ['noise_vol', 'noise_color']: get_param(snd_param, inst_plugindata, sound_instdata)

                    inst_plugindata.to_cvpj(cvpj_l, pluginid)

            sound_chan_effects = sndstat_chan['effects']
            for sound_chan_effect in sound_chan_effects:
                fxpluginid = plugins.get_id()
                fxpluginname = sound_chan_effect['identifier']
                fxenabled = not sound_chan_effect['bypass']
                fxslot.insert(cvpj_l, ['master'] if ismaster else ['track', trackid], 'audio', fxpluginid)

                if fxpluginname == 'com.soundation.parametric-eq':
                    fx_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'eq-bands')
                    fx_plugindata.fxdata_add(fxenabled, 1)

                    bandnum = 1
                    for eqname in ["highshelf","hpf","lowshelf","lpf","peak1","peak2","peak3","peak4"]:

                        eq_bandtype = 'peak'
                        if eqname == 'highshelf': eq_bandtype = 'high_shelf'
                        if eqname == 'hpf': eq_bandtype = 'high_pass'
                        if eqname == 'lowshelf': eq_bandtype = 'low_shelf'
                        if eqname == 'lpf': eq_bandtype = 'low_pass'

                        band_enable, auto_enable = get_paramval(sound_chan_effect, eqname+'_enable')
                        band_freq, auto_freq = get_paramval(sound_chan_effect, eqname+'_freq')
                        band_gain, auto_gain = get_paramval(sound_chan_effect, eqname+'_gain')
                        band_res, auto_res = get_paramval(sound_chan_effect, eqname+'_res')

                        band_freq = 20 * 1000**band_freq
                        band_gain = (band_gain-0.5)*40
                        band_res = eq_calc_q(eq_bandtype, band_res)
                        
                        if auto_enable:
                            auto_data.add_pl(cvpj_l, 'float', ['plugin_eq',fxpluginid,str(bandnum)+'_on'], auto_nopl.to_pl(sngauto_to_cvpjauto(auto_enable)))
                        if auto_freq: 
                            for point in auto_freq: point['value'] = 20 * 1000**point['value']
                            auto_data.add_pl(cvpj_l, 'float', ['plugin_eq',fxpluginid,str(bandnum)+'_freq'], auto_nopl.to_pl(sngauto_to_cvpjauto(auto_freq)))
                        if auto_gain: 
                            for point in auto_gain: point['value'] = (point['value']-0.5)*40
                            auto_data.add_pl(cvpj_l, 'float', ['plugin_eq',fxpluginid,str(bandnum)+'_gain'], auto_nopl.to_pl(sngauto_to_cvpjauto(auto_gain)))
                        if auto_res: 
                            for point in auto_res: point['value'] = eq_calc_q(eq_bandtype, point['value'])
                            auto_data.add_pl(cvpj_l, 'float', ['plugin_eq',fxpluginid,str(bandnum)+'_res'], auto_nopl.to_pl(sngauto_to_cvpjauto(auto_res)))

                        fx_plugindata.eqband_add(int(band_enable), band_freq, band_gain, eq_bandtype, band_res, None)
                        bandnum += 1

                    master_gain = get_paramval(sound_chan_effect, 'master_gain')[0]
                    master_gain = (master_gain-0.5)*40
                    fx_plugindata.param_add('gain_out', master_gain, 'float', 'Out Gain')

                else:
                    fx_plugindata = plugins.cvpj_plugin('deftype', 'native-soundation', fxpluginname)
                    fx_plugindata.fxdata_add(fxenabled, 1)

                    autoall_cvpj_to_sng(sound_chan_effect, fx_plugindata, fxpluginname)

                fx_plugindata.to_cvpj(cvpj_l, fxpluginid)

        return json.dumps(cvpj_l)
