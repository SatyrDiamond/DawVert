# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import colors
from functions import plugins
from functions import xtramath
from functions import note_data
from functions import placement_data
from functions import song
import plugin_input
import struct
import json

def get_paramval(i_params, i_name):
    outval = 0
    if i_name in i_params:
        if 'value' in i_params[i_name]:
            outval = i_params[i_name]['value']
    return outval

def get_param(i_name, i_plugid, i_params):
    plugins.add_plug_param(cvpj_l, i_plugid, i_name, get_paramval(i_params, i_name), 'float', i_name)

def get_asdr(pluginid, sound_instdata):
    asdr_a = get_paramval(sound_instdata, 'attack')
    asdr_s = get_paramval(sound_instdata, 'sustain')
    asdr_d = get_paramval(sound_instdata, 'decay')
    asdr_r = get_paramval(sound_instdata, 'release')
    plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, asdr_a, 0, asdr_d, asdr_s, asdr_r, 1)

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

    for sndstat_note in sndstat_clip['notes']:
        cvpj_notelist.append(
            note_data.rx_makenote(
                sndstat_note['position']/ticksdiv, 
                sndstat_note['length']/ticksdiv, 
                sndstat_note['note']-60, 
                sndstat_note['velocity'], 
                None)
            )

    cvpj_pldata["notelist"] = cvpj_notelist
    placement_data.unminus(cvpj_pldata)
    return cvpj_pldata

def sngauto_to_cvpjauto(autopoints):
    sngauto = []
    for autopoint in autopoints:
        sngauto.append({"position": autopoint['pos']/ticksdiv, "value": autopoint['value']})
    return sngauto

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

        bytestream = open(input_file, 'r')
        sndstat_data = json.load(bytestream)

        cvpj_l = {}

        timeSignaturesplit = sndstat_data['timeSignature'].split('/')
        cvpj_l['timesig'] = [int(timeSignaturesplit[0]), int(timeSignaturesplit[1])]
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
            trackcolor = colors.hsv_to_rgb(tracknum_hue, 0.7, 0.7)

            ismaster = False
            if sound_chan_type == 'master':
                ismaster = True
                tracks.a_addtrack_master(cvpj_l, sndstat_chan['name'], sndstat_chan['volume'], None)
                tracks.a_addtrack_master_param(cvpj_l, 'pan', (sndstat_chan['pan']-0.5)*2, 'float')
                tracks.a_addtrack_master_param(cvpj_l, 'enabled', int(not sndstat_chan['mute']), 'bool')
                tracks.a_addtrack_master_param(cvpj_l, 'solo', int(sndstat_chan['solo']), 'bool')

            if sound_chan_type == 'instrument':
                pluginid = plugins.get_id()
                tracks.r_create_track(cvpj_l, 'instrument', trackid, name=sndstat_chan['name'], color=[trackcolor[0], trackcolor[1], trackcolor[2]])
                tracks.r_track_pluginid(cvpj_l, trackid, pluginid)
                tracks.r_add_param(cvpj_l, trackid, 'vol', sndstat_chan['volume'], 'float')
                tracks.r_add_param(cvpj_l, trackid, 'pan', (sndstat_chan['pan']-0.5)*2, 'float')
                tracks.r_add_param(cvpj_l, trackid, 'enabled', int(not sndstat_chan['mute']), 'bool')
                tracks.r_add_param(cvpj_l, trackid, 'solo', int(sndstat_chan['solo']), 'bool')

                for autoname in [['vol','volumeAutomation'],['pan','panAutomation']]:
                    if sndstat_chan[autoname[1]] != []:
                        autodata = sngauto_to_cvpjauto(sndstat_chan[autoname[1]])
                        if autoname[0] == 'pan': autodata = auto.multiply_nopl(autodata, -1, 2)
                        tracks.a_add_auto_pl(cvpj_l, 'float', ['track',trackid,autoname[0]], tracks.a_auto_nopl_to_pl(autodata))

                sound_instdata = sndstat_chan['instrument']

                for sndstat_region in sndstat_chan['regions']:
                    tracks.r_pl_notes(cvpj_l, trackid, parse_clip_notes(sndstat_region))

                if 'identifier' in sound_instdata:
                    instpluginname = sound_instdata['identifier']

                    plugins.add_plug(cvpj_l, pluginid, 'native-soundation', instpluginname)

                    if instpluginname == 'com.soundation.GM-2':
                        get_asdr(pluginid, sound_instdata)
                        if 'value' in sound_instdata['sample_pack']:
                            sample_pack = get_paramval(sound_instdata, 'sample_pack')
                            plugins.add_plug_data(cvpj_l, pluginid, 'sample_pack', sample_pack)

                    elif instpluginname == 'com.soundation.simple':
                        get_asdr(pluginid, sound_instdata)
                        asdrf_a = get_paramval(sound_instdata, 'filter_attack')
                        asdrf_s = get_paramval(sound_instdata, 'filter_decay')
                        asdrf_d = get_paramval(sound_instdata, 'filter_sustain')
                        asdrf_r = get_paramval(sound_instdata, 'filter_release')
                        asdrf_i = get_paramval(sound_instdata, 'filter_int')
                        plugins.add_asdr_env(cvpj_l, pluginid, 'cutoff', 0, asdrf_a, 0, asdrf_d, asdrf_s, asdrf_r, asdrf_i)
                        filter_cutoff = xtramath.between_from_one(20, 7500, get_paramval(sound_instdata, 'filter_cutoff'))
                        filter_reso = get_paramval(sound_instdata, 'filter_resonance')
                        plugins.add_filter(cvpj_l, pluginid, True, filter_cutoff, filter_reso, 'lowpass', None)
                        for snd_param in ['noise_vol', 'noise_color']:
                            get_param(snd_param, pluginid, sound_instdata)
                        for oscnum in range(4):
                            for paramtype in ['detune','pitch','type','vol']:
                                get_param('osc_'+str(oscnum)+'_'+paramtype, pluginid, sound_instdata)

                    elif instpluginname == 'com.soundation.supersaw':
                        get_asdr(pluginid, sound_instdata)

                    elif instpluginname == 'com.soundation.noiser':
                        get_asdr(pluginid, sound_instdata)
                        
                    elif instpluginname == 'com.soundation.drummachine':
                        kit_name = get_paramval(sound_instdata, 'kit_name')
                        plugins.add_plug_data(cvpj_l, pluginid, 'kit_name', kit_name)
                        for num in range(8):
                            for paramtype in ['decay','gain','hold','pitch']:
                                get_param(paramtype+'_'+str(num), pluginid, sound_instdata)

                    elif instpluginname == 'com.soundation.spc':
                        get_param('bite', pluginid, sound_instdata)
                        get_param('msl', pluginid, sound_instdata)
                        get_param('punch', pluginid, sound_instdata)
                        plugins.add_plug_data(cvpj_l, pluginid, 'cuts', sound_instdata['cuts'])
                        plugins.add_plug_data(cvpj_l, pluginid, 'envelopes', sound_instdata['envelopes'])
                        plugins.add_plug_data(cvpj_l, pluginid, 'pack', sound_instdata['pack'])
                        for num in range(16):
                            for paramtype in ['gain','pan','pitch']:
                                get_param(paramtype+'_'+str(num), pluginid, sound_instdata)

                    else:
                        snd_params = []
                        if instpluginname == 'com.soundation.va_synth': snd_params = ["aatt", "adec", "arel", "asus", "fatt", "fdec", "fdyn", "feg", "ffreq", "frel", "fres", "fsus", "glide_bend", "glide_mode", "glide_rate", "lfolpf", "lfoosc", "lforate", "octave", "osc_2_fine", "osc_2_mix", "osc_2_noise", "osc_2_octave", "tune"]
                        elif instpluginname == 'com.soundation.supersaw': snd_params = ["detune", "spread"]
                        elif instpluginname == 'com.soundation.fm_synth': snd_params = ['p'+str(x) for x in range(137)]
                        elif instpluginname == 'com.soundation.mono': snd_params = ['filter_int','cutoff','resonance','pw','filter_decay','mix','amp_decay','glide']
                        elif instpluginname == 'com.soundation.the_wub_machine': snd_params = ['filter_cutoff','filter_drive','filter_resonance','filter_type','filth_active','filth_amount','lfo_depth','lfo_keytracking','lfo_loop','lfo_phase','lfo_retrigger','lfo_speed','lfo_type','msl_amount','osc1_gain','osc1_glide','osc1_pan','osc1_pitch','osc1_shape','osc1_type','osc2_gain','osc2_glide','osc2_pan','osc2_pitch','osc2_shape','osc2_type','osc_sub_bypass_filter','osc_sub_gain','osc_sub_glide','osc_sub_shape','osc_sub_volume_lfo','reese_active','unison_active','unison_amount','unison_count']
                        for snd_param in snd_params:
                            get_param(snd_param, pluginid, sound_instdata)

            sound_chan_effects = sndstat_chan['effects']
            for sound_chan_effect in sound_chan_effects:
                fxpluginid = plugins.get_id()
                fxpluginname = sound_chan_effect['identifier']
                fxenabled = not sound_chan_effect['bypass']
                plugins.add_plug(cvpj_l, fxpluginid, 'native-soundation', fxpluginname)
                plugins.add_plug_fxdata(cvpj_l, fxpluginid, fxenabled, 1)
                if ismaster: tracks.insert_fxslot(cvpj_l, ['master'], 'audio', fxpluginid)
                else: tracks.insert_fxslot(cvpj_l, ['track', trackid], 'audio', fxpluginid)
                
                snd_params = []

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
                    get_param(snd_param, fxpluginid, sound_chan_effect)

        return json.dumps(cvpj_l)
