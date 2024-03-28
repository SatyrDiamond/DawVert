# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import math
import struct
import av
import os.path
import varint
from pathlib import Path

from functions import data_bytes
from functions import data_values
from functions import xtramath
from functions_plugin import flp_dec_plugins
from objects import dv_datadef
from objects import dv_dataset
from objects_file import proj_flp

filename_len = {}

stretch_algorithms = ['resample','elastique_v3','elastique_v3_mono','slice_stretch','auto','slice_map','elastique_v2','elastique_v2_transient','elastique_v2_mono','elastique_v2_speech']

chordids = [None,"major","sus2","sus4","majb5","minor","mb5","aug","augsus4","7ri","6","6sus4","6add9","m6","m6add9","7","7sus4","7#5","7b5","7#9","7b9","7#5#9","7#5b9","7b5b9","7add","7add13","7#11","maj7","maj7b5","maj7#5","maj7#11","maj7add13","m7","m7b5","m7b9","m7add11","m7add13","m-maj7","m-maj7add11","m-maj7add13","9","9sus4","add9","9#5","9b5","9#11","9b13","maj9","maj9sus4","maj9#5","maj9#11","m9","madd9","m9b5","m9-maj7","11","11b9","maj11","m11","m-maj11","13","13#9","13b9","13b5b9","maj13","m13","m-maj13","full_major","major_pentatonic","major_bebop","minor_harmonic","minor_melodic","minor_pentatonic","aeolian","minor_neapolitan","minor_hungarian","whole_tone","diminished","dominant_bebop","jap_in_sen","blues","arabic","enigmatic","neapolitan","dorian","phrygian","lydian","mixolydian","locrian"]

filtertype = [
['low_pass', None],
['low_pass', None],
['band_pass', None], 
['high_pass', None],
['notch', None],  
['low_pass','double'],
['low_pass','sv'],
['low_pass','sv'],
]

def calc_time(input_val):
    return ((((input_val/65535)*3.66)**4.5)/8)**0.6

def conv_color(b_color):
    color = b_color.to_bytes(4, "little")
    cvpj_inst_color = [color[0]/255,color[1]/255,color[2]/255]
    return cvpj_inst_color


def flpauto_to_cvpjauto(i_value):
    out = [None, 0, 1]

    if i_value[0] == 'main':
        if i_value[1] == 'tempo': out = [['main', 'bpm'], 0, 1000]
        if i_value[1] == 'pitch': out = [['main', 'pitch'], 0, 100]
    if i_value[0] == 'fx':
        if i_value[2] == 'param':
            if i_value[3] == 'vol': out = [['fxmixer', i_value[1], 'vol'], 0, 16000]
            if i_value[3] == 'pan': out = [['fxmixer', i_value[1], 'pan'], 0, 6400]
        if i_value[2] == 'slot':
            if i_value[4] == 'wet': out = [['slot', 'FLPlug_F_'+i_value[1]+'_'+i_value[3], 'wet'], 0, 12800]
            if i_value[4] == 'on': out = [['slot', 'FLPlug_F_'+i_value[1]+'_'+i_value[3], 'enabled'], 0, 1]
        if i_value[2] == 'route':
            out = [['send', 'send_'+str(i_value[1])+'_'+str(i_value[3]), 'amount'], 0, 12800]

    return out


def get_sample(i_value):
    if i_value != None:
        if i_value[0:21] == "%FLStudioFactoryData%":
            restpath = i_value[21:]
            for t in [
            'C:\\Program Files\\Image-Line\\FL Studio 21\\', 
            'C:\\Program Files (x86)\\Image-Line\\FL Studio 21\\', 
            'C:\\Program Files (x86)\\Image-Line\\FL Studio 20\\'
            ]:
                if os.path.exists(t+restpath): return t+restpath
            return restpath
        else:
            return i_value
    else:
        return ''

def parse_envlfo(envlfo, pluginid, envtype):
    bio_envlfo = data_bytes.to_bytesio(envlfo)

    envlfo_flags = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_enabled = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_predelay = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_attack = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_hold = calc_time(int.from_bytes(bio_envlfo.read(4), "little"))
    el_env_decay = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_sustain = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_release = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_aomunt = int.from_bytes(bio_envlfo.read(4), "little")
    envlfo_lfo_predelay = int.from_bytes(bio_envlfo.read(4), "little")
    envlfo_lfo_attack = int.from_bytes(bio_envlfo.read(4), "little")
    envlfo_lfo_amount = int.from_bytes(bio_envlfo.read(4), "little")
    envlfo_lfo_speed = int.from_bytes(bio_envlfo.read(4), "little")
    envlfo_lfo_shape = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_attack_tension = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_decay_tension = int.from_bytes(bio_envlfo.read(4), "little")
    el_env_release_tension = int.from_bytes(bio_envlfo.read(4), "little")

    #plugins.add_asdr_env(cvpj_l, pluginid, envtype, el_env_predelay, el_env_attack, el_env_hold, el_env_decay, el_env_sustain, el_env_release, el_env_aomunt)
    #plugins.add_asdr_env_tension(cvpj_l, pluginid, envtype, el_env_attack_tension, el_env_decay_tension, el_env_release_tension)



class input_flp(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'flp'
    def gettype(self): return 'mi'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'FL Studio'
        dawinfo_obj.file_ext = 'flp'
        dawinfo_obj.auto_types = ['pl_ticks']
        dawinfo_obj.track_lanes = True
        dawinfo_obj.placement_cut = True
        dawinfo_obj.fxrack = True
        dawinfo_obj.fxrack_params = ['enabled','vol','pan']
        dawinfo_obj.audio_stretch = ['rate']
        dawinfo_obj.audio_filetypes = ['wav','flac','ogg','mp3','wv','ds']
        dawinfo_obj.plugin_included = ['sampler:single','universal:arpeggiator','native-flstudio','soundfont2']
        dawinfo_obj.fxchain_mixer = True
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'FLhd': return True
        else: return False
    def parse(self, convproj_obj, input_file, dv_config):

        convproj_obj.type = 'mi'

        flp_obj = proj_flp.flp_project()
        flp_obj.read(input_file)

        datadef = dv_datadef.datadef('./data_ddef/fl_studio.ddef')
        dataset = dv_dataset.dataset('./data_dset/fl_studio.dset')

        convproj_obj.set_timings(flp_obj.ppq, False)
        convproj_obj.timesig[0] = flp_obj.numerator
        convproj_obj.timesig[1] = flp_obj.denominator

        convproj_obj.params.add('pitch', flp_obj.mainpitch/100, 'float')
        convproj_obj.params.add('bpm', flp_obj.tempo, 'float')
        convproj_obj.params.add('shuffle', flp_obj.shuffle/128, 'float')

        convproj_obj.params.add('vol', flp_obj.initfxvals.initvals['main/vol']/12800 if 'main/vol' in flp_obj.initfxvals.initvals else 1, 'float')

        id_inst = {}
        id_pat = {}
        sampleinfo = {}
        samplestretch = {}
        samplefolder = dv_config.path_samples_extracted

        for instrument, channelnum in enumerate(flp_obj.channels):
            fl_channel_obj = flp_obj.channels[channelnum]
            instdata = {}

            if fl_channel_obj.type in [0,1,2,3]:
                cvpj_instid = 'FLInst' + str(instrument)

                inst_obj = convproj_obj.add_instrument(cvpj_instid)
                inst_obj.visual.name = fl_channel_obj.name if fl_channel_obj.name else ''
                inst_obj.visual.color = conv_color(fl_channel_obj.color)

                inst_obj.datavals.add('middlenote', fl_channel_obj.middlenote-60)
                inst_obj.params.add('enabled', fl_channel_obj.enabled, 'bool')
                inst_obj.params.add('pitch', fl_channel_obj.basicparams.pitch/100, 'float')
                inst_obj.params.add('usemasterpitch', fl_channel_obj.params.main_pitch, 'bool')
                inst_obj.params.add('pan', fl_channel_obj.basicparams.pan, 'float')
                inst_obj.params.add('vol', fl_channel_obj.basicparams.volume**1.5, 'float')
                inst_obj.fxrack_channel = fl_channel_obj.fxchannel

                plugin_obj = None
                if fl_channel_obj.type == 0:
                    inst_obj.pluginid = 'FLPlug_G_'+str(channelnum)
                    plugin_obj, sampleref_obj = convproj_obj.add_plugin_sampler(inst_obj.pluginid, get_sample(fl_channel_obj.samplefilename))

                    plugin_obj.datavals.add('remove_dc', fl_channel_obj.params.remove_dc)
                    plugin_obj.datavals.add('normalize', fl_channel_obj.params.normalize)
                    plugin_obj.datavals.add('reversepolarity', fl_channel_obj.params.reversepolarity)
                    plugin_obj.datavals.add('interpolation', "sinc" if (fl_channel_obj.sampleflags & 1) else "none")

                    if sampleref_obj.fileref.extension.lower() != 'ds':
                        cvpj_loopdata = {}
                        cvpj_loopdata['enabled'] = bool(fl_channel_obj.sampleflags & 8)
                        cvpj_loopdata['mode'] = "normal" if fl_channel_obj.looptype == 0 else "pingpong"
                        plugin_obj.datavals.add('loop', cvpj_loopdata)
                  
                if fl_channel_obj.type == 2:
                    filename_sample = get_sample(fl_channel_obj.samplefilename)

                    plug_exists = None

                    if fl_channel_obj.plugin.name != None: 
                        inst_obj.pluginid = 'FLPlug_G_'+str(channelnum)
                        plugin_obj = flp_dec_plugins.getparams(convproj_obj, inst_obj.pluginid, fl_channel_obj.plugin, samplefolder, datadef, dataset)
                        convproj_obj.add_sampleref(filename_sample, filename_sample)
                        plugin_obj.samplerefs['audiofile'] = filename_sample

                if plugin_obj:
                    fl_asdr_obj_vol = fl_channel_obj.env_lfo[1]
                    fl_asdr_obj_cut = fl_channel_obj.env_lfo[2]

                    vol_enabled = bool(fl_asdr_obj_vol.el_env_enabled)

                    if vol_enabled:
                        adsr_obj = plugin_obj.env_asdr_add('vol', 
                            calc_time(fl_asdr_obj_vol.el_env_predelay), 
                            calc_time(fl_asdr_obj_vol.el_env_attack), 
                            calc_time(fl_asdr_obj_vol.el_env_hold), 
                            calc_time(fl_asdr_obj_vol.el_env_decay), 
                            fl_asdr_obj_vol.el_env_sustain/128, 
                            calc_time(fl_asdr_obj_vol.el_env_release), 
                            int(vol_enabled)
                            )

                        adsr_obj.attack_tension = fl_asdr_obj_vol.el_env_attack_tension
                        adsr_obj.decay_tension = fl_asdr_obj_vol.el_env_decay_tension
                        adsr_obj.release_tension = fl_asdr_obj_vol.el_env_release_tension

                    elif fl_channel_obj.type == 0 and (not fl_channel_obj.sampleflags&8 or sampleref_obj.fileref.extension.lower() == 'ds'):
                        plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 20, 1)

                    fcalc = 0
                    if fl_channel_obj.basicparams.mod_type == 0: fcalc = 1

                    if fl_channel_obj.basicparams.mod_x != 1:
                        plugin_obj.filter.on = True
                        plugin_obj.filter.freq = xtramath.midi_filter(fl_channel_obj.basicparams.mod_x)
                        if fcalc == 0: plugin_obj.filter.freq *= 2.7
                        plugin_obj.filter.q = 1+(fl_channel_obj.basicparams.mod_y*6)
                        plugin_obj.filter.type, plugin_obj.filter.subtype = filtertype[fl_channel_obj.basicparams.mod_type]

                    envf_amount = xtramath.midi_filter(fl_asdr_obj_cut.el_env_aomunt/128)
                    if fcalc == 0: envf_amount *= 2.7

                    adsr_obj = plugin_obj.env_asdr_add('cutoff', 
                        calc_time(fl_asdr_obj_cut.el_env_predelay), 
                        calc_time(fl_asdr_obj_cut.el_env_attack), 
                        calc_time(fl_asdr_obj_cut.el_env_hold), 
                        calc_time(fl_asdr_obj_cut.el_env_decay), 
                        fl_asdr_obj_cut.el_env_sustain/128, 
                        calc_time(fl_asdr_obj_cut.el_env_release), 
                        envf_amount
                        )

                    adsr_obj.attack_tension = fl_asdr_obj_cut.el_env_attack_tension
                    adsr_obj.decay_tension = fl_asdr_obj_cut.el_env_decay_tension
                    adsr_obj.release_tension = fl_asdr_obj_cut.el_env_release_tension

                    plugin_obj.poly['max'] = fl_channel_obj.poly.max
                    plugin_obj.poly['slide_time_type'] = 'step'
                    plugin_obj.poly['slide_time_speed'] = (fl_channel_obj.poly.slide/1024)**(16/4)
                    plugin_obj.poly['mono'] = bool(fl_channel_obj.poly.flags&1)
                    plugin_obj.poly['porta'] = bool(fl_channel_obj.poly.flags&2)
                    plugin_obj.role = 'synth'

                notefx_pluginid = 'FLPlug_GA_'+str(channelnum)
                plugin_obj = convproj_obj.add_plugin(notefx_pluginid, 'universal', 'arpeggiator')
                plugin_obj.fxdata_add(fl_channel_obj.params.arpdirection, None)
                plugin_obj.role = 'notefx'
                inst_obj.fxslots_notes.append(notefx_pluginid)

                if fl_channel_obj.params.arpdirection:
                    plugin_obj.datavals.add('gate', fl_channel_obj.params.arpgate/48)
                    plugin_obj.datavals.add('range', fl_channel_obj.params.arprange)
                    plugin_obj.datavals.add('repeat', fl_channel_obj.params.arprepeat)
                    plugin_obj.datavals.add('slide', bool(fl_channel_obj.params.arpslide))
                    plugin_obj.datavals.add('direction', ['up','up','down','up_down','up_down','random'][fl_channel_obj.params.arpdirection])
                    if fl_channel_obj.params.arpdirection == 4:
                        plugin_obj.datavals.add('direction_mode', 'sticky')

                    chord_obj = plugin_obj.chord_add('main')
                    if fl_channel_obj.params.arpchord < 89:
                        chord_obj.find_by_id(0, chordids[fl_channel_obj.params.arpchord])
                    else:
                        if fl_channel_obj.params.arpchord == 4294967294:
                            plugin_obj.datavals.add('mode', 'sort')
                        if fl_channel_obj.params.arpchord == 4294967295:
                            plugin_obj.datavals.add('mode', 'sort')
                            plugin_obj.datavals.add('mode_sub', 'sustain')

                timing_obj = plugin_obj.timing_add('main')
                timing_obj.set_steps((fl_channel_obj.params.arptime/1024)**4, convproj_obj)

                id_inst[str(instrument)] = 'FLInst' + str(instrument)

            if fl_channel_obj.type == 4:
                filename_sample = get_sample(fl_channel_obj.samplefilename)

                sampleref_obj = convproj_obj.add_sampleref(filename_sample, filename_sample)

                sle_obj = convproj_obj.add_sampleindex('FLSample' + str(instrument))
                sle_obj.visual.name = fl_channel_obj.name
                sle_obj.visual.color = conv_color(fl_channel_obj.color)
                sle_obj.pan = fl_channel_obj.basicparams.pan
                sle_obj.vol = fl_channel_obj.basicparams.volume
                sle_obj.enabled = bool(fl_channel_obj.enabled)
                sle_obj.fxrack_channel = fl_channel_obj.fxchannel
                sle_obj.sampleref = filename_sample

                t_stretchingmode = 0
                t_stretchingtime = 0
                t_stretchingmultiplier = 1
                t_stretchingpitch = 0

                t_stretchingpitch += fl_channel_obj.params.stretchingpitch/100
                t_stretchingpitch += (fl_channel_obj.middlenote-60)*-1
                t_stretchingpitch += fl_channel_obj.basicparams.pitch/100
                sle_obj.pitch = t_stretchingpitch

                t_stretchingtime = fl_channel_obj.params.stretchingtime/384
                t_stretchingmode = fl_channel_obj.params.stretchingmode
                t_stretchingmultiplier = pow(2, fl_channel_obj.params.stretchingmultiplier/10000)


                sle_obj.stretch.algorithm = 'stretch' if t_stretchingmode == -1 else stretch_algorithms[t_stretchingmode]

                #if t_stretchingtime != 0 or t_stretchingmultiplier != 1 or t_stretchingpitch != 0:

                if sampleref_obj.found:
                    if t_stretchingtime != 0:
                        sle_obj.stretch.set_rate_tempo(flp_obj.tempo, (sampleref_obj.dur_sec/t_stretchingtime)/t_stretchingmultiplier, False)

                    elif t_stretchingtime == 0:
                        sle_obj.stretch.set_rate_speed(flp_obj.tempo, 1/t_stretchingmultiplier, False)

                    samplestretch[instrument] = sle_obj.stretch

        autoticks_pat = {}
        autoticks_pl = {}

        for pattern, fl_pattern in flp_obj.patterns.items():

            nle_obj = convproj_obj.add_notelistindex('FLPat' + str(pattern))

            autoticks_pat[pattern] = fl_pattern.automation

            if fl_pattern.notes:
                slidenotes = []
                for fl_note in fl_pattern.notes:
                    note_inst = id_inst[str(fl_note.rack)] if str(fl_note.rack) in id_inst else ''
                    note_pos = fl_note.pos
                    note_dur = fl_note.dur
                    note_key = fl_note.key-60
                    note_vol = fl_note.velocity/100

                    note_extra = {}
                    note_extra['finepitch'] = (fl_note.finep-120)*10
                    note_extra['release'] = fl_note.rel/128
                    note_extra['pan'] = (fl_note.pan-64)/64
                    note_extra['cutoff'] = fl_note.mod_x/255
                    note_extra['reso'] = fl_note.mod_y/255
                    note_extra['channel'] = data_bytes.splitbyte(fl_note.midich)[1]+1

                    is_slide = bool(fl_note.flags & 0b000000000001000)

                    if is_slide == True: 
                        slidenotes.append([note_inst, note_pos, note_dur, note_key, note_vol, note_extra])
                    else: 
                        nle_obj.notelist.add_m(note_inst, note_pos, note_dur, note_key, note_vol, note_extra)

                for sn in slidenotes: 
                    nle_obj.notelist.auto_add_slide(sn[0], sn[1], sn[2], sn[3], sn[4], sn[5])
                nle_obj.notelist.notemod_conv()

                id_pat[str(pattern)] = 'FLPat' + str(pattern)

            if fl_pattern.color:
                color = fl_pattern.color.to_bytes(4, "little")
                if color != b'HQV\x00': nle_obj.visual.color = [color[0]/255,color[1]/255,color[2]/255]
            if fl_pattern.name: nle_obj.visual.name = fl_pattern.name

        temp_pl_track = {}

        if len(flp_obj.arrangements) != 0:
            fl_arrangement = flp_obj.arrangements[0]

            used_tracks = []

            #for track_id, track_obj in fl_arrangement.tracks.items():
            #    if track_id in used_tracks:
            #        playlist_obj = convproj_obj.add_playlist(str(track_id), True, True)
            #        if track_obj.color: playlist_obj.visual.color = conv_color(track_obj.color)
            #        if track_obj.name: playlist_obj.visual.name = track_obj.name
            #        playlist_obj.visual_ui.height = track_obj.height
            #        playlist_obj.params.add('enabled', track_obj.enabled, 'bool')

            for item in fl_arrangement.items:
                playlistline = (item.trackindex*-1)+500
                if playlistline not in used_tracks: used_tracks.append(playlistline)

                if playlistline not in temp_pl_track: 
                    temp_pl_track[playlistline] = convproj_obj.add_playlist(playlistline-1, 1, True)

                if item.itemindex > item.patternbase:
                    placement_obj = temp_pl_track[playlistline].placements.add_notes_indexed()
                    placement_obj.position = item.position
                    placement_obj.duration = item.length
                    placement_obj.muted = bool(item.flags & 0b0001000000000000)
                    patnum = item.itemindex - item.patternbase
                    placement_obj.fromindex = 'FLPat' + str(patnum)
                    offset = item.startoffset if item.startoffset not in [4294967295, 3212836864] else 0

                    placement_obj.cut_type = 'cut'
                    placement_obj.cut_data['start'] = offset

                    placement_obj.duration += offset

                    if patnum in autoticks_pat:
                        tickdata = autoticks_pat[patnum]
                        autodata = [placement_obj.position, placement_obj.duration, offset]
                        autod = autoticks_pat
                        for autoid, autodata in tickdata.items():
                            autoloc, aadd, adiv = flpauto_to_cvpjauto(autoid.split('/'))

                            if autoloc == ['main','pitch']:
                                for x in autodata: x[1] = struct.unpack('i', struct.pack('I', x[1]))[0]

                            if autoloc: 
                                autopl_obj = convproj_obj.automation.add_pl_ticks(autoloc, 'float')
                                autopl_obj.position = placement_obj.position
                                autopl_obj.duration = placement_obj.duration
                                autopl_obj.cut_type = 'cut'
                                autopl_obj.cut_data['start'] = offset

                                for pos, val in autodata: autopoint_obj = autopl_obj.data.add_point(pos, val/adiv)

                else:
                    placement_obj = temp_pl_track[playlistline].placements.add_audio_indexed()
                    placement_obj.position = item.position
                    placement_obj.duration = item.length

                    placement_obj.muted = bool(item.flags & 0b0001000000000000)
                    placement_obj.fromindex = 'FLSample' + str(item.itemindex)
                    stretch_obj = samplestretch[item.itemindex] if item.itemindex in samplestretch else None

                    out_rate = stretch_obj.calc_tempo_speed if stretch_obj else 1
                    placement_obj.cut_type = 'cut'

                    startoffset = 0
                    if item.startoffset not in [4294967295, 3212836864]:  
                        posdata = item.startoffset/4
                        startoffset = (posdata/out_rate)*flp_obj.ppq

                    placement_obj.cut_data['start'] = startoffset

            for fl_timemark in fl_arrangement.timemarkers:
                if fl_timemark.type == 8:
                    convproj_obj.timesig_auto.add_point(fl_timemark.pos, [fl_timemark.numerator, fl_timemark.denominator])
                else:
                    timemarker_obj = convproj_obj.add_timemarker()
                    timemarker_obj.visual.name = fl_timemark.name
                    timemarker_obj.position = fl_timemark.pos
                    if fl_timemark.type == 5: timemarker_obj.type = 'start'
                    if fl_timemark.type == 4: timemarker_obj.type = 'loop'
                    if fl_timemark.type == 1: timemarker_obj.type = 'markerloop'
                    if fl_timemark.type == 2: timemarker_obj.type = 'markerskip'
                    if fl_timemark.type == 3: timemarker_obj.type = 'pause'
                    if fl_timemark.type == 9: timemarker_obj.type = 'punchin'
                    if fl_timemark.type == 10: timemarker_obj.type = 'punchout'

        
        #print(flp_obj.initfxvals.initvals)
        #exit()

        for mixer_id, mixer_obj in flp_obj.mixer.items():

            fxchannel_obj = convproj_obj.add_fxchan(mixer_id)
            if mixer_obj.name: fxchannel_obj.visual.name = mixer_obj.name
            if mixer_obj.color: fxchannel_obj.visual.color = conv_color(mixer_obj.color)

            if mixer_obj.docked_center: dockedpos = 0
            else: dockedpos = -1 if not mixer_obj.docked_pos else 1
            fxchannel_obj.visual_ui.other['docked'] = dockedpos

            autoloctxt_vol = 'fx/'+str(mixer_id)+'/param/vol'
            autoloctxt_pan = 'fx/'+str(mixer_id)+'/param/pan'
            fx_vol = flp_obj.initfxvals.initvals[autoloctxt_vol]/12800 if autoloctxt_vol in flp_obj.initfxvals.initvals else 1
            fx_pan = flp_obj.initfxvals.initvals[autoloctxt_pan]/6400 if autoloctxt_pan in flp_obj.initfxvals.initvals else 0

            fxchannel_obj.params.add('vol', fx_vol, 'float')
            fxchannel_obj.params.add('pan', fx_pan, 'float')

            for route in mixer_obj.routing:
                autoloctxt_route = 'fx/'+str(mixer_id)+'/route/'+str(route)
                route_val = flp_obj.initfxvals.initvals[autoloctxt_route]/12800 if autoloctxt_route in flp_obj.initfxvals.initvals else 1
                fxchannel_obj.sends.add(route, 'send_'+str(mixer_id)+'_'+str(route), route_val)

            for slot_id, slot_obj in enumerate(mixer_obj.slots):
                autoloctxt_on = 'fx/'+str(mixer_id)+'/slot/'+str(slot_id)+'/on'
                autoloctxt_wet = 'fx/'+str(mixer_id)+'/slot/'+str(slot_id)+'/wet'
                route_on = flp_obj.initfxvals.initvals[autoloctxt_on] if autoloctxt_on in flp_obj.initfxvals.initvals else 1
                route_wet = flp_obj.initfxvals.initvals[autoloctxt_wet]/12800 if autoloctxt_wet in flp_obj.initfxvals.initvals else 1

                if slot_obj:
                    pluginid = 'FLPlug_F_'+str(mixer_id)+'_'+str(slot_id)
                    plugin_obj = flp_dec_plugins.getparams(convproj_obj, pluginid, slot_obj.plugin, samplefolder, datadef, dataset)
                    plugin_obj.fxdata_add(bool(route_on), route_wet)
                    plugin_obj.role = 'effect'
                    if slot_obj.name: plugin_obj.visual.name = slot_obj.name
                    if slot_obj.color: plugin_obj.visual.color = conv_color(slot_obj.color)
                    fxchannel_obj.fxslots_audio.append(pluginid)

            eq_fxid = 'FLPlug_ME_'+str(mixer_id)

            mixer_eq = []

            for eqnum in range(3):
                autoloctxt_level = 'fx/'+str(mixer_id)+'/param/eq'+str(eqnum+1)+'_level'
                autoloctxt_freq = 'fx/'+str(mixer_id)+'/param/eq'+str(eqnum+1)+'_freq'

                eq_level = flp_obj.initfxvals.initvals[autoloctxt_level] if autoloctxt_level in flp_obj.initfxvals.initvals else 0
                eq_freq = flp_obj.initfxvals.initvals[autoloctxt_freq] if autoloctxt_freq in flp_obj.initfxvals.initvals else 0

                mixer_eq.append([eq_freq, eq_level])

            if mixer_eq != [[5777, 0], [33145, 0], [55825, 0]]:
                plugin_obj = convproj_obj.add_plugin(eq_fxid, 'universal', 'eq-bands')
                for n, e in enumerate(mixer_eq):
                    eq_freq, eq_level = e
                    eq_freq /= 100
                    eq_level /= 65536

                    eq_freq = (eq_freq**0.575)
                    eq_freq = 10 * 1600**eq_freq

                    filter_obj = plugin_obj.eq_add()
                    filter_obj.freq = eq_freq
                    filter_obj.type = ['low_shelf','peak','high_shelf'][n]
                    filter_obj.gain = eq_level
                fxchannel_obj.fxslots_mixer.append(eq_fxid)

        #if len(flp_obj.arrangements) == 0 and len(FL_Patterns) == 1 and len(FL_Channels) == 0:
        #    fst_chan_notelist = [[] for x in range(16)]
        #    for cvpj_notedata in cvpj_l_notelistindex['FLPat0']['notelist']:
        #        cvpj_notedata['instrument'] = 'FST' + str(cvpj_notedata['channel'])
        #        fst_chan_notelist[cvpj_notedata['channel']-1].append(cvpj_notedata)

        #    for channum in range(16):
        #        cvpj_inst = {}
        #        cvpj_inst['name'] = 'Channel '+str(channum+1)
        #        cvpj_l_instrument_data['FST' + str(channum+1)] = cvpj_inst
        #        cvpj_l_instrument_order.append('FST' + str(channum+1))

        #        arrangementitemJ = {}
        #        arrangementitemJ['position'] = 0
        #        arrangementitemJ['duration'] = notelist_data.getduration(cvpj_l_notelistindex['FLPat0']['notelist'])
        #        arrangementitemJ['fromindex'] = 'FLPat0'

        #        cvpj_l_playlist["1"] = {}
        #        cvpj_l_playlist["1"]['placements_notes'] = []
        #        cvpj_l_playlist["1"]['placements_notes'].append(arrangementitemJ)

        convproj_obj.do_actions.append('do_lanefit')
        convproj_obj.do_actions.append('do_addloop')

        if flp_obj.title: convproj_obj.metadata.name = flp_obj.title
        if flp_obj.author: convproj_obj.metadata.author = flp_obj.author
        if flp_obj.genre: convproj_obj.metadata.genre = flp_obj.genre
        if flp_obj.url: convproj_obj.metadata.url = flp_obj.url
        if flp_obj.comment: convproj_obj.metadata.comment_text = flp_obj.comment
