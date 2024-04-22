# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions import xtramath
from objects import dv_dataset
from objects_proj import proj_soundation
import plugin_input
import struct
import json
import math



def get_param(soundation_device, plugin_obj, i_name, cvpj_autoloc, add_to_param):
    global convproj_obj
    sndparam_obj = soundation_device.params.get(i_name)
    if plugin_obj: plugin_obj.params.add(i_name, sndparam_obj.value, 'float')
    if cvpj_autoloc: autopoints_set(cvpj_autoloc, sndparam_obj.automation, 0, 1)
    return sndparam_obj

def get_paramval(soundation_device, i_name):
    sndparam_obj = soundation_device.params.get(i_name)
    return sndparam_obj.value

def get_asdr(plugin_obj, soundation_device):
    asdr_a = get_paramval(soundation_device, 'attack')
    asdr_s = get_paramval(soundation_device, 'sustain')
    asdr_d = get_paramval(soundation_device, 'decay')
    asdr_r = get_paramval(soundation_device, 'release')
    plugin_obj.env_asdr_add('vol', 0, asdr_a, 0, asdr_d, asdr_s, asdr_r, 1)

def autoall_sng_to_cvpj(convproj_obj, pluginid, soundation_device, plugin_obj, fxpluginname):
    paramlist = dataset.params_list('plugin', fxpluginname)
    if paramlist:
        for paramid in paramlist:
            sndparam_obj = get_param(soundation_device, plugin_obj, paramid, ['plugin', pluginid, paramid], True)
            plugin_obj.add_from_dset(paramid, sndparam_obj.value, dataset, 'plugin', fxpluginname)

def autopoints_set(autoloc, points, add, mul):
    for point in points:
        convproj_obj.automation.add_autopoint(autoloc, 'float', point['pos'], (point['value']+add)*mul, 'normal')

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

    def parse(self, i_convproj_obj, input_file, dv_config):
        global dataset
        global convproj_obj

        convproj_obj = i_convproj_obj

        bytestream = open(input_file, 'r')
        sndstat_data = json.load(bytestream)

        soundation_obj = proj_soundation.soundation_project(sndstat_data)

        convproj_obj.type = 'r'
        dataset = dv_dataset.dataset('./data_dset/soundation.dset')
        dataset_synth_nonfree = dv_dataset.dataset('./data_dset/synth_nonfree.dset')

        timeSignaturesplit = soundation_obj.timeSignature.split('/')
        soundation_channels = soundation_obj.channels

        timing = 22050*(120/soundation_obj.bpm)
        convproj_obj.set_timings(timing, False)

        convproj_obj.timesig = [int(timeSignaturesplit[0]), int(timeSignaturesplit[1])]
        convproj_obj.params.add('bpm', soundation_obj.bpm, 'float')

        convproj_obj.loop_active = soundation_obj.looping
        convproj_obj.loop_start = soundation_obj.loopStart
        convproj_obj.loop_end = soundation_obj.loopEnd

        tracknum = 0
        for soundation_channel in soundation_obj.channels:
            tracknum_hue = (tracknum/-11) - 0.2
            tracknum += 1
            sound_chan_type = soundation_channel.type
            trackid = 'soundation'+str(tracknum)
            if soundation_channel.color: trackcolor = colors.hex_to_rgb_float(soundation_channel.color)

            if sound_chan_type == 'master':
                track_obj = convproj_obj.track_master
                convproj_obj.track_master.visual.name = soundation_channel.name
                convproj_obj.track_master.params.add('vol', soundation_channel.volume, 'float')
                convproj_obj.track_master.params.add('pan', (soundation_channel.pan-0.5)*2, 'float')
                convproj_obj.track_master.params.add('enabled', bool(int(not soundation_channel.mute)), 'bool')
                convproj_obj.track_master.params.add('solo', int(soundation_channel.solo), 'bool')
                autopoints_set(['master','vol'], soundation_channel.volumeAutomation, 0, 1)
                autopoints_set(['master','pan'], soundation_channel.panAutomation, -1, 2)

            if sound_chan_type in ['instrument', 'effect', 'audio']:
                if sound_chan_type == 'instrument': track_type = 'instrument'
                if sound_chan_type == 'effect': track_type = 'fx'
                if sound_chan_type == 'audio': track_type = 'audio'
                track_obj = convproj_obj.add_track(trackid, track_type, 1, False)
                track_obj.visual.name = soundation_channel.userSetName if soundation_channel.userSetName else soundation_channel.name
                if soundation_channel.color: track_obj.visual.color = [trackcolor[0], trackcolor[1], trackcolor[2]]

                track_obj.params.add('vol', soundation_channel.volume, 'float')
                track_obj.params.add('pan', (soundation_channel.pan-0.5)*2, 'float')
                track_obj.params.add('enabled', bool(int(not soundation_channel.mute)), 'bool')
                track_obj.params.add('solo', int(soundation_channel.solo), 'bool')

                autopoints_set(['track',trackid,'vol'], soundation_channel.volumeAutomation, 0, 1)
                autopoints_set(['track',trackid,'pan'], soundation_channel.panAutomation, -1, 2)

                for soundation_region in soundation_channel.regions:
                    if sound_chan_type == 'instrument': placement_obj = track_obj.placements.add_notes()
                    if sound_chan_type == 'audio': placement_obj = track_obj.placements.add_audio()
                    placement_obj.position = soundation_region.position
                    clip_length = round(soundation_region.length/timing, 3)*timing
                    clip_contentPosition = soundation_region.contentPosition
                    clip_loopcount = round(soundation_region.loopcount, 3)
                    placement_obj.duration = clip_length*clip_loopcount

                    if isinstance(soundation_region.color,str): 
                        clipcolor = colors.hex_to_rgb_float(soundation_region.color)
                    else: 
                        clipcolor = struct.unpack("4B", struct.pack("i", soundation_region.color))
                        clipcolor = [clipcolor[2]/255, clipcolor[1]/255, clipcolor[0]/255]
                        clipcolor = colors.darker(clipcolor, 0.3)
                    placement_obj.visual.color = clipcolor

                    placement_obj.cut_loop_data(-clip_contentPosition, -clip_contentPosition, clip_length)

                    if sound_chan_type == 'instrument':
                        for sndstat_note in soundation_region.notes: 
                            placement_obj.notelist.add_r(sndstat_note['position'], sndstat_note['length'], sndstat_note['note']-60, sndstat_note['velocity'], {})
                        placement_obj.antiminus()

                    #if sound_chan_type == 'audio':
                    #    if 'file' in soundation_region:
                    #        snd_file = soundation_region.file
                    #        url_data = snd_file['url']
                    #        convproj_obj.add_sampleref(url_data, url_data)
                    #        placement_obj.sampleref = url_data

                if sound_chan_type == 'instrument':
                    soundation_inst = soundation_channel.instrument

                    instpluginname = soundation_inst.identifier

                    if instpluginname == 'com.soundation.simple-sampler':
                        plugin_obj, pluginid = convproj_obj.add_plugin_genid('sampler', 'single')
                        plugin_obj.role = 'synth'
                        track_obj.inst_pluginid = pluginid

                        get_asdr(plugin_obj, soundation_inst)

                        plugin_obj.params.add('gain', get_paramval(soundation_inst, 'gain'), 'float')
                        plugin_obj.datavals.add('start', get_paramval(soundation_inst, 'start'))
                        plugin_obj.datavals.add('end', get_paramval(soundation_inst, 'end'))

                        v_loop_mode = get_paramval(soundation_inst, 'loop_mode')
                        v_loop_start = get_paramval(soundation_inst, 'loop_start')
                        v_loop_end = get_paramval(soundation_inst, 'loop_end')

                        cvpj_loopdata = {}
                        if v_loop_mode != 0 :
                            cvpj_loopdata['enabled'] = 1
                            cvpj_loopdata['mode'] = "normal"
                            cvpj_loopdata['points'] = [v_loop_start, v_loop_end]
                        else: cvpj_loopdata['enabled'] = 0
                        plugin_obj.datavals.add('loop', cvpj_loopdata)
                        plugin_obj.datavals.add('point_value_type', "percent")

                        v_coarse = (get_paramval(soundation_inst, 'coarse')-0.5)*2
                        v_fine = (get_paramval(soundation_inst, 'fine')-0.5)*2
                        v_root_note = get_paramval(soundation_inst, 'root_note')

                        track_obj.params.add('pitch', v_coarse*48 + v_fine, 'float')
                        track_obj.datavals.add('middlenote', v_root_note-60)

                        v_crossfade = get_paramval(soundation_inst, 'crossfade')
                        v_playback_direction = get_paramval(soundation_inst, 'playback_direction')
                        v_interpolation_mode = get_paramval(soundation_inst, 'interpolation_mode')
                        v_release_mode = get_paramval(soundation_inst, 'release_mode')
                        v_portamento_time = get_paramval(soundation_inst, 'portamento_time')

                        if v_interpolation_mode == 0: cvpj_interpolation = "none"
                        if v_interpolation_mode == 1: cvpj_interpolation = "linear"
                        if v_interpolation_mode > 1: cvpj_interpolation = "sinc"
                        plugin_obj.datavals.add('interpolation', cvpj_interpolation)

                    elif instpluginname == 'com.soundation.drummachine':
                        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                        plugin_obj.role = 'synth'
                        track_obj.inst_pluginid = pluginid

                        kit_name = get_paramval(soundation_inst, 'kit_name')
                        for paramid in ["gain_2", "hold_1", "pitch_6", "gain_1", "decay_5", "gain_5", "hold_0", "hold_2", "pitch_7", "gain_0", "decay_6", "gain_3", "hold_5", "pitch_3", "decay_4", "pitch_4", "gain_6", "decay_7", "pitch_2", "hold_6", "decay_1", "decay_3", "decay_0", "decay_2", "gain_7", "pitch_0", "pitch_5", "hold_3", "pitch_1", "hold_4", "hold_7", "gain_4"]:
                            get_param(soundation_inst, plugin_obj, paramid, ['plugin', pluginid, paramid], True)
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
                                outval = get_paramval(soundation_inst, sng_paramid)
                                plugin_obj.add_from_dset(paramid, outval, dataset_synth_nonfree, 'plugin', 'europa')

                    elif instpluginname == 'com.soundation.GM-2':
                        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                        plugin_obj.role = 'synth'
                        track_obj.inst_pluginid = pluginid
                        get_asdr(plugin_obj, soundation_inst)
                        if 'sample_pack' in soundation_inst.params.data:
                            sample_pack = get_paramval(soundation_inst, 'sample_pack')
                            plugin_obj.datavals.add('sample_pack', sample_pack)
                            sv = sample_pack.split('_')
                            try:
                                if len(sv) > 1: plugin_obj.midi.from_sf2(int(sv[1]), int(sv[0])-1)
                            except:
                                pass

                    elif instpluginname == 'com.soundation.noiser':
                        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                        plugin_obj.role = 'synth'
                        track_obj.inst_pluginid = pluginid
                        get_asdr(plugin_obj, soundation_inst)
                            
                    elif instpluginname == 'com.soundation.SAM-1':
                        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                        plugin_obj.role = 'synth'
                        track_obj.inst_pluginid = pluginid
                        get_asdr(plugin_obj, soundation_inst)
                        if 'sample_pack' in soundation_inst.params.data:
                            sample_pack = get_paramval(soundation_inst, 'sample_pack')
                            plugin_obj.datavals.add('sample_pack', sample_pack)

                    elif instpluginname in ['com.soundation.fm_synth', 'com.soundation.mono', 'com.soundation.spc', 'com.soundation.supersaw', 'com.soundation.the_wub_machine', 'com.soundation.va_synth']:
                        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                        plugin_obj.role = 'synth'
                        track_obj.inst_pluginid = pluginid
                        paramlist = dataset.params_list('plugin', instpluginname)

                        if paramlist:
                            for paramid in paramlist:
                                outval = None
                                outval = get_paramval(soundation_inst, paramid)
                                plugin_obj.add_from_dset(paramid, outval, dataset, 'plugin', instpluginname)

                        if instpluginname == 'com.soundation.spc':
                            plugin_obj.datavals.add('cuts', soundation_inst.data['cuts'])
                            plugin_obj.datavals.add('envelopes', soundation_inst.data['envelopes'])

                        if instpluginname == 'com.soundation.supersaw':
                            get_asdr(plugin_obj, soundation_inst)

                    elif instpluginname == 'com.soundation.simple':
                        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', instpluginname)
                        plugin_obj.role = 'synth'
                        track_obj.inst_pluginid = pluginid
                        get_asdr(plugin_obj, soundation_inst)
                        asdrf_a = get_paramval(soundation_inst, 'filter_attack')
                        asdrf_s = get_paramval(soundation_inst, 'filter_decay')
                        asdrf_d = get_paramval(soundation_inst, 'filter_sustain')
                        asdrf_r = get_paramval(soundation_inst, 'filter_release')
                        asdrf_i = get_paramval(soundation_inst, 'filter_int')
                        plugin_obj.env_asdr_add('cutoff', 0, asdrf_a, 0, asdrf_d, asdrf_s, asdrf_r, asdrf_i)
                        filter_cutoff = xtramath.between_from_one(20, 7500, get_paramval(soundation_inst, 'filter_cutoff'))
                        filter_reso = get_paramval(soundation_inst, 'filter_resonance')
                        plugin_obj.filter.on = True
                        plugin_obj.filter.type = 'low_pass'
                        plugin_obj.filter.freq = filter_cutoff
                        plugin_obj.filter.q = filter_reso

                        for oscnum in range(4):
                            for paramtype in ['detune','pitch','type','vol']: 
                                paramid = 'osc_'+str(oscnum)+'_'+paramtype
                                get_param(soundation_inst, plugin_obj, paramid, ['plugin', pluginid, paramid], True)
                        for paramid in ['noise_vol', 'noise_color']: 
                            get_param(soundation_inst, plugin_obj, paramid, ['plugin', pluginid, paramid], True)

            for soundation_effect in soundation_channel.effects:
                plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-soundation', soundation_effect.identifier)
                plugin_obj.role = 'effect'
                plugin_obj.fxdata_add(not soundation_effect.bypass, 1)
                track_obj.fxslots_audio.append(pluginid)
                autoall_sng_to_cvpj(convproj_obj, pluginid, soundation_effect, plugin_obj, soundation_effect.identifier)