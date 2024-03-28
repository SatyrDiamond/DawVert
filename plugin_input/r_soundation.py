# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions import xtramath
from objects import dv_dataset
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

def get_param(i_name, plugin_obj, i_params):
    value_out, automation = get_paramval(i_params, i_name)
    plugin_obj.params.add(i_name, value_out, 'float')
    return automation

def get_asdr(plugin_obj, sound_instdata):
    asdr_a = get_paramval(sound_instdata, 'attack')[0]
    asdr_s = get_paramval(sound_instdata, 'sustain')[0]
    asdr_d = get_paramval(sound_instdata, 'decay')[0]
    asdr_r = get_paramval(sound_instdata, 'release')[0]
    plugin_obj.env_asdr_add('vol', 0, asdr_a, 0, asdr_d, asdr_s, asdr_r, 1)

def parse_auto(convproj_obj, cvpj_autoloc, autopoints):
    autopl_obj = convproj_obj.automation.add_pl_points(cvpj_autoloc, 'float')
    for autopoint in autopoints:
        autopl_obj.duration = autopoint['pos']
        autopl_obj.points.add_point(autopoint['pos'], float(autopoint['value']), 'normal', 0)
    return autopl_obj

def autoall_sng_to_cvpj(convproj_obj, pluginid, sng_device, plugin_obj, fxpluginname):
    paramlist = dataset.params_list('plugin', fxpluginname)
    if paramlist:
        for paramid in paramlist:
            outval, outauto = get_paramval(sng_device, paramid)
            plugin_obj.add_from_dset(paramid, outval, dataset, 'plugin', fxpluginname)
            if outauto not in [None, []]: 
                parse_auto(convproj_obj, ['plugin',pluginid,paramid], outauto)

class input_soundation(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'soundation'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Soundation'
        dawinfo_obj.file_ext = 'sng'
        dawinfo_obj.placement_cut = True
        dawinfo_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
        dawinfo_obj.plugin_included = ['sampler:single','synth-nonfree:europa','native-soundation']

    def parse(self, convproj_obj, input_file, dv_config):
        global dataset
        bytestream = open(input_file, 'r')
        sndstat_data = json.load(bytestream)

        timing = 22050

        convproj_obj.type = 'r'
        dataset = dv_dataset.dataset('./data_dset/soundation.dset')
        dataset_synth_nonfree = dv_dataset.dataset('./data_dset/synth_nonfree.dset')

        timeSignaturesplit = sndstat_data['timeSignature'].split('/')
        bpm = sndstat_data['bpm']
        sndstat_chans = sndstat_data['channels']

        timing = 22050*(120/bpm)
        convproj_obj.set_timings(timing, False)

        convproj_obj.timesig = [int(timeSignaturesplit[0]), int(timeSignaturesplit[1])]
        convproj_obj.params.add('bpm', bpm, 'float')

        bpmdiv = 120/bpm

        tracknum = 0
        for sndstat_chan in sndstat_chans:
            tracknum_hue = (tracknum/-11) - 0.2
            tracknum += 1
            sound_chan_type = sndstat_chan['type']
            trackid = 'soundation'+str(tracknum)
            trackcolor = colors.hex_to_rgb_float(sndstat_chan['color']) if 'color' in sndstat_chan else colors.hsv_to_rgb(tracknum_hue, 0.7, 0.7)

            if sound_chan_type == 'master':
                track_obj = convproj_obj.track_master
                convproj_obj.track_master.visual.name = sndstat_chan['name']
                convproj_obj.track_master.params.add('vol', sndstat_chan['volume'], 'float')
                convproj_obj.track_master.params.add('pan', (sndstat_chan['pan']-0.5)*2, 'float')
                convproj_obj.track_master.params.add('enabled', bool(int(not sndstat_chan['mute'])), 'bool')
                convproj_obj.track_master.params.add('solo', int(sndstat_chan['solo']), 'bool')

                for autoname in [['vol','volumeAutomation'],['pan','panAutomation']]:
                    if sndstat_chan[autoname[1]] != []:
                        autodata = sngauto_to_cvpjauto(sndstat_chan[autoname[1]])
                        if autoname[0] == 'pan': autodata = auto.multiply_nopl(autodata, -1, 2)
                        auto_data.add_pl(cvpj_l, 'float', ['master',autoname[0]], auto_nopl.to_pl(autodata))

            if sound_chan_type in ['instrument', 'audio']:
                track_obj = convproj_obj.add_track(trackid, 'instrument', 1, False)
                track_obj.visual.name = sndstat_chan['userSetName'] if 'userSetName' in sndstat_chan else sndstat_chan['name']
                track_obj.visual.color = [trackcolor[0], trackcolor[1], trackcolor[2]]

                track_obj.params.add('vol', sndstat_chan['volume'], 'float')
                track_obj.params.add('pan', (sndstat_chan['pan']-0.5)*2, 'float')
                track_obj.params.add('enabled', bool(int(not sndstat_chan['mute'])), 'bool')
                track_obj.params.add('solo', int(sndstat_chan['solo']), 'bool')

                for autoname in [['vol','volumeAutomation'],['pan','panAutomation']]:
                    if sndstat_chan[autoname[1]] != []:
                        autopl_obj = parse_auto(['track',trackid,autoname[0]], sndstat_chan[autoname[1]])
                        if autoname[0] == 'pan': autopl_obj.points.addmul(-1, 2)

                for snd_clip in sndstat_chan['regions']:
                    if sound_chan_type == 'instrument': placement_obj = track_obj.placements.add_notes()
                    if sound_chan_type == 'audio': placement_obj = track_obj.placements.add_audio()
                    placement_obj.position = snd_clip['position']
                    clip_length = snd_clip['length']
                    clip_contentPosition = snd_clip['contentPosition']
                    clip_loopcount = snd_clip['loopcount']
                    placement_obj.duration = clip_length*clip_loopcount

                    if 'color' in snd_clip: 
                        if isinstance(snd_clip['color'],str): 
                            clipcolor = colors.hex_to_rgb_float(snd_clip['color'])
                        else: 
                            clipcolor = struct.unpack("4B", struct.pack("i", snd_clip["color"]))
                            clipcolor = [clipcolor[2]/255, clipcolor[1]/255, clipcolor[0]/255]
                            clipcolor = colors.darker(clipcolor, 0.3)
                        placement_obj.visual.color = clipcolor

                    placement_obj.cut_loop_data(-clip_contentPosition, -clip_contentPosition, clip_length)

                    if sound_chan_type == 'instrument':
                        for sndstat_note in snd_clip['notes']: 
                            placement_obj.notelist.add_r(sndstat_note['position'], sndstat_note['length'], sndstat_note['note']-60, sndstat_note['velocity'], {})
                        placement_obj.antiminus()

                    if sound_chan_type == 'audio':
                        if 'file' in snd_clip:
                            snd_file = snd_clip['file']
                            url_data = snd_file['url']
                            convproj_obj.add_sampleref(url_data, url_data)
                            placement_obj.sampleref = url_data

                if sound_chan_type == 'instrument':
                    sound_instdata = sndstat_chan['instrument']

                    if 'identifier' in sound_instdata:
                        instpluginname = sound_instdata['identifier']

                        if instpluginname == 'com.soundation.simple-sampler':
                            plugin_obj, pluginid = convproj_obj.add_plugin_genid('sampler', 'single')
                            plugin_obj.role = 'synth'
                            track_obj.inst_pluginid = pluginid

                            get_asdr(plugin_obj, sound_instdata)

                            plugin_obj.params.add('gain', get_paramval(sound_instdata, 'gain')[0], 'float')
                            plugin_obj.datavals.add('start', get_paramval(sound_instdata, 'start')[0])
                            plugin_obj.datavals.add('end', get_paramval(sound_instdata, 'end')[0])

                            v_loop_mode = get_paramval(sound_instdata, 'loop_mode')[0]
                            v_loop_start = get_paramval(sound_instdata, 'loop_start')[0]
                            v_loop_end = get_paramval(sound_instdata, 'loop_end')[0]

                            cvpj_loopdata = {}
                            if v_loop_mode != 0 :
                                cvpj_loopdata['enabled'] = 1
                                cvpj_loopdata['mode'] = "normal"
                                cvpj_loopdata['points'] = [v_loop_start, v_loop_end]
                            else: cvpj_loopdata['enabled'] = 0
                            plugin_obj.datavals.add('loop', cvpj_loopdata)
                            plugin_obj.datavals.add('point_value_type', "percent")

                            v_coarse = (get_paramval(sound_instdata, 'coarse')[0]-0.5)*2
                            v_fine = (get_paramval(sound_instdata, 'fine')[0]-0.5)*2
                            v_root_note = get_paramval(sound_instdata, 'root_note')[0]

                            track_obj.params.add('pitch', v_coarse*48 + v_fine, 'float')
                            track_obj.datavals.add('middlenote', v_root_note-60)

                            v_crossfade = get_paramval(sound_instdata, 'crossfade')[0]
                            v_playback_direction = get_paramval(sound_instdata, 'playback_direction')[0]
                            v_interpolation_mode = get_paramval(sound_instdata, 'interpolation_mode')[0]
                            v_release_mode = get_paramval(sound_instdata, 'release_mode')[0]
                            v_portamento_time = get_paramval(sound_instdata, 'portamento_time')[0]

                            if v_interpolation_mode == 0: cvpj_interpolation = "none"
                            if v_interpolation_mode == 1: cvpj_interpolation = "linear"
                            if v_interpolation_mode > 1: cvpj_interpolation = "sinc"
                            plugin_obj.datavals.add('interpolation', cvpj_interpolation)

                        elif instpluginname == 'com.soundation.drummachine':
                            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                            plugin_obj.role = 'synth'
                            track_obj.inst_pluginid = pluginid

                            kit_name = get_paramval(sound_instdata, 'kit_name')[0]
                            for paramname in ["gain_2", "hold_1", "pitch_6", "gain_1", "decay_5", "gain_5", "hold_0", "hold_2", "pitch_7", "gain_0", "decay_6", "gain_3", "hold_5", "pitch_3", "decay_4", "pitch_4", "gain_6", "decay_7", "pitch_2", "hold_6", "decay_1", "decay_3", "decay_0", "decay_2", "gain_7", "pitch_0", "pitch_5", "hold_3", "pitch_1", "hold_4", "hold_7", "gain_4"]:
                                get_param(paramname, plugin_obj, sound_instdata)
                            plugin_obj.datavals.add('kit_name', kit_name)

                        elif instpluginname == 'com.soundation.europa':
                            plugin_obj, pluginid = convproj_obj.add_plugin_genid('synth-nonfree', 'europa')
                            plugin_obj.role = 'synth'
                            track_obj.inst_pluginid = pluginid

                            paramlist = dataset_synth_nonfree.params_list('plugin', 'europa')
                            if paramlist:
                                for paramid in paramlist:
                                    outval = None
                                    param = dataset_synth_nonfree.params_i_get('plugin', 'europa', paramid)
                                    sng_paramid = "/custom_properties/"+param[5]
                                    if sng_paramid in sound_instdata:
                                        if 'value' in sound_instdata[sng_paramid]: outval = sound_instdata[sng_paramid]['value']
                                    plugin_obj.add_from_dset(paramid, outval, dataset_synth_nonfree, 'plugin', 'europa')

                        elif instpluginname == 'com.soundation.GM-2':
                            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                            plugin_obj.role = 'synth'
                            track_obj.inst_pluginid = pluginid
                            get_asdr(plugin_obj, sound_instdata)
                            if 'value' in sound_instdata['sample_pack']:
                                sample_pack = get_paramval(sound_instdata, 'sample_pack')[0]
                                plugin_obj.datavals.add('sample_pack', sample_pack)

                        elif instpluginname == 'com.soundation.noiser':
                            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                            plugin_obj.role = 'synth'
                            track_obj.inst_pluginid = pluginid
                            get_asdr(plugin_obj, sound_instdata)
                                
                        elif instpluginname == 'com.soundation.SAM-1':
                            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                            plugin_obj.role = 'synth'
                            track_obj.inst_pluginid = pluginid
                            get_asdr(plugin_obj, sound_instdata)
                            sound_instdata['sample_pack'] = plugin_obj.datavals.add('sample_pack', None)

                        elif instpluginname in ['com.soundation.fm_synth', 'com.soundation.mono', 'com.soundation.spc', 'com.soundation.supersaw', 'com.soundation.the_wub_machine', 'com.soundation.va_synth']:
                            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                            plugin_obj.role = 'synth'
                            track_obj.inst_pluginid = pluginid
                            paramlist = dataset.params_list('plugin', instpluginname)

                            if paramlist:
                                for paramid in paramlist:
                                    outval = None
                                    if paramid in sound_instdata:
                                        if 'value' in sound_instdata[paramid]: outval = sound_instdata[paramid]['value']
                                    plugin_obj.add_from_dset(paramid, outval, dataset, 'plugin', instpluginname)

                            if instpluginname == 'com.soundation.spc':
                                plugin_obj.datavals.add('cuts', sound_instdata['cuts'])
                                plugin_obj.datavals.add('envelopes', sound_instdata['envelopes'])

                            if instpluginname == 'com.soundation.supersaw':
                                get_asdr(plugin_obj, sound_instdata)

                        elif instpluginname == 'com.soundation.simple':
                            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                            plugin_obj.role = 'synth'
                            track_obj.inst_pluginid = pluginid
                            get_asdr(plugin_obj, sound_instdata)
                            asdrf_a = get_paramval(sound_instdata, 'filter_attack')[0]
                            asdrf_s = get_paramval(sound_instdata, 'filter_decay')[0]
                            asdrf_d = get_paramval(sound_instdata, 'filter_sustain')[0]
                            asdrf_r = get_paramval(sound_instdata, 'filter_release')[0]
                            asdrf_i = get_paramval(sound_instdata, 'filter_int')[0]
                            plugin_obj.env_asdr_add('cutoff', 0, asdrf_a, 0, asdrf_d, asdrf_s, asdrf_r, asdrf_i)
                            filter_cutoff = xtramath.between_from_one(20, 7500, get_paramval(sound_instdata, 'filter_cutoff')[0])
                            filter_reso = get_paramval(sound_instdata, 'filter_resonance')
                            plugin_obj.filter.on = True
                            plugin_obj.filter.type = 'low_pass'
                            plugin_obj.filter.freq = filter_cutoff
                            plugin_obj.filter.q = filter_reso

                            for oscnum in range(4):
                                for paramtype in ['detune','pitch','type','vol']: get_param('osc_'+str(oscnum)+'_'+paramtype, plugin_obj, sound_instdata)
                            for snd_param in ['noise_vol', 'noise_color']: get_param(snd_param, plugin_obj, sound_instdata)

            sound_chan_effects = sndstat_chan['effects']
            for sound_chan_effect in sound_chan_effects:
                fxpluginname = sound_chan_effect['identifier']
                plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', fxpluginname)
                plugin_obj.role = 'effect'
                plugin_obj.fxdata_add(not sound_chan_effect['bypass'], 1)
                track_obj.fxslots_audio.append(pluginid)
                autoall_sng_to_cvpj(convproj_obj, pluginid, sound_chan_effect, plugin_obj, fxpluginname)