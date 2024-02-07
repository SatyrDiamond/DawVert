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

from functions_plugin import flp_dec_plugins
from functions_plugin import format_flp_dec
from functions import data_bytes
from functions import data_values

from objects import dv_datadef
from objects import dv_dataset

filename_len = {}

stretch_algorithms = ['resample','elastique_v3','elastique_v3_mono','slice_stretch','auto','slice_map','elastique_v2','elastique_v2_transient','elastique_v2_mono','elastique_v2_speech']


def getsamplefile(channeldata):
    if 'samplefilename' in channeldata:  return channeldata['samplefilename']
    else: return ''


def conv_color(b_color):
    color = b_color.to_bytes(4, "little")
    cvpj_inst_color = [color[0]/255,color[1]/255,color[2]/255]
    return cvpj_inst_color


def calc_time(i_value):
    oneval = i_value/65535
    outval = math.log10(oneval)

    for val in [i_value, oneval, outval]: print(str(val).rjust(24), end=' ')
    print()

    return oneval

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
    def getname(self): return 'FL Studio'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'fxrack': True,
        'fxrack_params': ['enabled','vol','pan'],
        'track_lanes': True,
        'placement_cut': True,
        'placement_audio_stretch': ['rate']
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'FLhd': return True
        else: return False
    def parse(self, convproj_obj, input_file, extra_param):

        convproj_obj.type = 'mi'


        FLP_Data = format_flp_dec.parse(input_file)

        datadef = dv_datadef.datadef('./data_ddef/fl_studio.ddef')
        dataset = dv_dataset.dataset('./data_dset/fl_studio.dset')

        FL_Main = FLP_Data['FL_Main']
        FL_Patterns = FLP_Data['FL_Patterns']
        FL_Channels = FLP_Data['FL_Channels']
        FL_Mixer = FLP_Data['FL_Mixer']

        FL_Arrangements = FLP_Data['FL_Arrangements']
        FL_TimeMarkers = FLP_Data['FL_TimeMarkers']
        FL_FilterGroups = FLP_Data['FL_FilterGroups']
        FL_InitFXVals = FLP_Data['FL_InitFXVals']

        FL_InitFXVals_exists = True if FL_InitFXVals != {} else False

        ppq = FL_Main['ppq']
        convproj_obj.set_timings(ppq, False)

        convproj_obj.timesig[0] = FL_Main['Numerator'] if 'Numerator' in FL_Main else 4
        convproj_obj.timesig[1] = FL_Main['Denominator'] if 'Denominator' in FL_Main else 4

        tempo = 120
        if 'MainPitch' in FL_Main: convproj_obj.params.add('pitch', struct.unpack('h', struct.pack('H', FL_Main['MainPitch']))[0]/100, 'float')
        if 'Tempo' in FL_Main: 
            convproj_obj.params.add('bpm', FL_Main['Tempo'], 'float')
            tempo = FL_Main['Tempo']
        if 'Shuffle' in FL_Main: convproj_obj.params.add('shuffle', FL_Main['Shuffle']/128, 'float')
        convproj_obj.params.add('vol', 1, 'float')

        id_inst = {}
        id_pat = {}
        sampleinfo = {}
        samplestretch = {}
        samplefolder = extra_param['samplefolder']

        for instrument in FL_Channels:
            channeldata = FL_Channels[instrument]
            instdata = {}
            if channeldata['type'] in [0,1,2,3]:
                cvpj_instid = 'FLInst' + str(instrument)

                inst_obj = convproj_obj.add_instrument(cvpj_instid)
                inst_obj.visual.name = channeldata['name'] if 'name' in channeldata else ''
                inst_obj.visual.color = conv_color(channeldata['color'])
                if 'middlenote' in channeldata: inst_obj.datavals.add('middlenote', channeldata['middlenote']-60)
                inst_obj.params.add('enabled', channeldata['enabled'], 'bool')
                inst_obj.params.add('pitch', channeldata['pitch']/100, 'float')
                inst_obj.params.add('usemasterpitch', channeldata['main_pitch'], 'bool')
                inst_obj.params.add('pan', channeldata['pan'], 'float')
                inst_obj.params.add('vol', channeldata['volume'], 'float')
                inst_obj.fxrack_channel = channeldata['fxchannel']

                if channeldata['type'] == 0:
                    plugin_obj, pluginid, sampleref_obj = convproj_obj.add_plugin_sampler_genid(getsamplefile(channeldata))
                    inst_obj.pluginid = pluginid

                    plugin_obj.datavals.add('remove_dc', channeldata['remove_dc'])
                    plugin_obj.datavals.add('normalize', channeldata['normalize'])
                    plugin_obj.datavals.add('reversepolarity', channeldata['reversepolarity'])

                    cvpj_loopdata = {}
                    if 'sampleflags' in channeldata:
                        fl_sampleflags = data_bytes.to_bin(channeldata['sampleflags'], 8)
                        cvpj_loopdata['enabled'] = fl_sampleflags[4]
                        interpolation = "none"
                        if fl_sampleflags[7] == 1: interpolation = "sinc"
                        plugin_obj.datavals.add('interpolation', interpolation)

                    if 'looptype' in channeldata:
                        cvpj_loopdata['mode'] = "normal" if channeldata['looptype'] == 0 else "pingpong"

                    plugin_obj.datavals.add('loop', cvpj_loopdata)
                    
                if channeldata['type'] == 2:
                    filename_sample = getsamplefile(channeldata)

                    flpluginname = channeldata['plugin'] if 'plugin' in channeldata else None
                    flplugindata = channeldata['plugindata'] if 'plugindata' in channeldata else None
                    flpluginparams = channeldata['pluginparams'] if 'pluginparams' in channeldata else b''

                    plug_exists = None


                    if flpluginname != None: 
                        plugin_obj, pluginid = flp_dec_plugins.getparams(convproj_obj, flpluginname, flpluginparams, samplefolder, datadef, dataset)

                        inst_obj.pluginid = pluginid

                        if flplugindata != None:
                            window_detatched = flplugindata[16]&4
                            window_active = flplugindata[16]&1
                            window_data = struct.unpack('iiii', flplugindata[36:52])
                            window_size = window_data[2:4] if window_active else None
                            windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
                            windata_obj.pos_x, pos_y = window_data[0:2]
                            if window_size: windata_obj.size_x, windata_obj.size_y = window_size
                            windata_obj.open = bool(window_active)
                            windata_obj.detatched = bool(window_detatched)

                        convproj_obj.add_sampleref(filename_sample, filename_sample)
                        plugin_obj.samplerefs['audiofile'] = filename_sample

                inst_obj.datavals.add('poly_max', channeldata['polymax'])

                id_inst[str(instrument)] = 'FLInst' + str(instrument)

            if channeldata['type'] == 4:
                filename_sample = getsamplefile(channeldata)

                sampleref_obj = convproj_obj.add_sampleref(filename_sample, filename_sample)

                sle_obj = convproj_obj.add_sampleindex('FLSample' + str(instrument))
                sle_obj.visual.name = channeldata['name'] if 'name' in channeldata else ''
                sle_obj.visual.color = conv_color(channeldata['color'])
                sle_obj.pan = channeldata['pan']
                sle_obj.vol = channeldata['volume']
                sle_obj.enabled = bool(channeldata['enabled'])
                sle_obj.fxrack_channel = channeldata['fxchannel']
                sle_obj.sampleref = filename_sample

                t_stretchingmode = 0
                t_stretchingtime = 0
                t_stretchingmultiplier = 1
                t_stretchingpitch = 0

                if 'stretchingpitch' in channeldata: t_stretchingpitch += channeldata['stretchingpitch']/100
                if 'middlenote' in channeldata: t_stretchingpitch += (channeldata['middlenote']-60)*-1
                if 'pitch' in channeldata: t_stretchingpitch += channeldata['pitch']/100
                sle_obj.pitch = t_stretchingpitch

                if 'stretchingtime' in channeldata: t_stretchingtime = channeldata['stretchingtime']/384
                if 'stretchingmode' in channeldata: t_stretchingmode = channeldata['stretchingmode']
                if 'stretchingmultiplier' in channeldata: t_stretchingmultiplier = pow(2, channeldata['stretchingmultiplier']/10000)

                sle_obj.stretch.algorithm = 'stretch' if t_stretchingmode == -1 else stretch_algorithms[t_stretchingmode]

                #if t_stretchingtime != 0 or t_stretchingmultiplier != 1 or t_stretchingpitch != 0:

                if sampleref_obj.found:
                    if t_stretchingtime != 0:
                        sle_obj.stretch.use_tempo = True
                        sle_obj.stretch.set_rate(tempo, (sampleref_obj.dur_sec/t_stretchingtime)/t_stretchingmultiplier)

                    elif t_stretchingtime == 0:
                        sle_obj.stretch.use_tempo = False
                        sle_obj.stretch.rate_tempo = 1/t_stretchingmultiplier
                        sle_obj.stretch.rate = 1/t_stretchingmultiplier

                    samplestretch[instrument] = sle_obj.stretch

        for pattern in FL_Patterns:
            patterndata = FL_Patterns[pattern]

            nle_obj = convproj_obj.add_notelistindex('FLPat' + str(pattern))

            if 'notes' in patterndata:
                slidenotes = []
                for flnote in patterndata['notes']:
                    note_inst = id_inst[str(flnote['rack'])] if str(flnote['rack']) in id_inst else ''
                    note_pos = flnote['pos']
                    note_dur = flnote['dur']
                    note_key = flnote['key']-60
                    note_vol = flnote['velocity']/100

                    note_extra = {}
                    note_extra['finepitch'] = (flnote['finep']-120)*10
                    note_extra['release'] = flnote['rel']/128
                    note_extra['pan'] = (flnote['pan']-64)/64
                    note_extra['cutoff'] = flnote['mod_x']/255
                    note_extra['reso'] = flnote['mod_y']/255
                    note_extra['channel'] = data_bytes.splitbyte(flnote['midich'])[1]+1

                    is_slide = bool(flnote['flags'] & 0b000000000001000)

                    if is_slide == True: slidenotes.append([note_inst, note_pos, note_dur, note_key, note_vol, note_extra])
                    else: nle_obj.notelist.add_m(note_inst, note_pos, note_dur, note_key, note_vol, note_extra)

                for sn in slidenotes: nle_obj.notelist.auto_add_slide(sn[0], sn[1], sn[2], sn[3], sn[4], sn[5])
                nle_obj.notelist.notemod_conv()

                id_pat[str(pattern)] = 'FLPat' + str(pattern)

            if 'color' in patterndata:
                color = patterndata['color'].to_bytes(4, "little")
                if color != b'HQV\x00': nle_obj.visual.color = [color[0]/255,color[1]/255,color[2]/255]
            if 'name' in patterndata: nle_obj.visual.name = patterndata['name']

        temp_pl_track = {}

        if len(FL_Arrangements) != 0:
            FL_Arrangement = FL_Arrangements['0']
            for item in FL_Arrangement['items']:
                playlistline = (item['trackindex']*-1)+500

                if playlistline not in temp_pl_track: 
                    temp_pl_track[playlistline] = convproj_obj.add_playlist(playlistline-1, 1, True)

                if item['itemindex'] > item['patternbase']:
                    placement_obj = temp_pl_track[playlistline].placements.add_notes()
                    placement_obj.position = item['position']
                    placement_obj.duration = item['length']
                    placement_obj.muted = bool(item['flags'] & 0b0001000000000000)
                    placement_obj.fromindex = 'FLPat' + str(item['itemindex'] - item['patternbase'])
                    if 'startoffset' in item:
                        placement_obj.cut_type = 'cut'
                        placement_obj.cut_data['start'] = item['startoffset']

                else:
                    placement_obj = temp_pl_track[playlistline].placements.add_audio()
                    placement_obj.position = item['position']
                    placement_obj.duration = item['length']

                    placement_obj.muted = bool(item['flags'] & 0b0001000000000000)
                    placement_obj.fromindex = 'FLSample' + str(item['itemindex'])
                    stretch_obj = samplestretch[str(item['itemindex'])] if str(item['itemindex']) in samplestretch else ['rate_speed', 1.0]

                    out_is_speed, out_rate = stretch_obj.get(tempo, True)
                    #print(out_is_speed, out_rate, end=' | ')
                    #print(placement_obj.duration/ppq, end=' | ')

                    placement_obj.cut_type = 'cut'

                    placement_obj.cut_data['start'] = 0
                    if 'startoffset' in item: 
                        posdata = item['startoffset']/4
                        #print(posdata, end=' -S- ')
                        #print(posdata/out_rate, end=' | ')
                        placement_obj.cut_data['start'] = (posdata/out_rate)*ppq
                    if 'endoffset' in item: 
                        posdata = item['endoffset']/4
                        #print(posdata, end=' -E- ')
                        #print(posdata/out_rate, end=' | ')
                        placement_obj.cut_data['end'] = (posdata/out_rate)*ppq
                    #print()

            FL_Tracks = FL_Arrangement['tracks']

            if len(FL_Tracks) != 0:
                for track in FL_Tracks:
                    if track in convproj_obj.playlist:
                        if track not in temp_pl_track: temp_pl_track[track] = convproj_obj.add_playlist(track, True, True)
                        if 'color' in FL_Tracks[track]: temp_pl_track[track].visual.color = conv_color(FL_Tracks[track]['color'])
                        if 'name' in FL_Tracks[track]: temp_pl_track[track].visual.name = FL_Tracks[track]['name']
                        if 'height' in FL_Tracks[track]: temp_pl_track[track].visual_ui.height = FL_Tracks[track]['height']
                        if 'enabled' in FL_Tracks[track]: temp_pl_track[track].params.add('enabled', FL_Tracks[track]['enabled'], 'bool')


        #exit()

        for fxchannel in FL_Mixer:
            fl_fx_chan = FL_Mixer[str(fxchannel)]

            fxchannel_obj = convproj_obj.add_fxchan(int(fxchannel))
            if "name" in fl_fx_chan: fxchannel_obj.visual.name = fl_fx_chan["name"]

            fx_color = None
            if 'color' in fl_fx_chan:
                if fl_fx_chan['color'] != None: fxchannel_obj.visual.color = conv_color(fl_fx_chan['color'])

            #print(fxchannel)
            #for hexnum in fl_fxdata_initvals:
            #    print(hexnum, int.from_bytes(fl_fxdata_initvals[hexnum], "little", signed=True) )

            if FL_InitFXVals_exists == True and int(fxchannel) in FL_InitFXVals:
                fl_fxdata_initvals = FL_InitFXVals[int(fxchannel)][0]
                fx_volume = struct.unpack('i', fl_fxdata_initvals[b'\x1f\xc0'])[0]/12800 if b'\x1f\xc0' in fl_fxdata_initvals else 1
                fx_pan = struct.unpack('i', fl_fxdata_initvals[b'\x1f\xc1'])[0]/6400 if b'\x1f\xc1' in fl_fxdata_initvals else 0
                fxchannel_obj.params.add('vol', fx_volume, 'float')
                fxchannel_obj.params.add('pan', fx_pan, 'float')

            if 'routing' in fl_fx_chan:
                for route in fl_fx_chan['routing']:
                    fxchannel_obj.sends.add(route, None, 1)

            if 'slots' in fl_fx_chan:
                for fl_fxslotnum in range(10):
                    if fl_fxslotnum in fl_fx_chan['slots']:
                        fl_fxslotdata = fl_fx_chan['slots'][fl_fxslotnum]

                        if fl_fxslotdata != None and 'plugin' in fl_fxslotdata:
                            flpluginname = fl_fxslotdata['plugin'] if 'plugin' in fl_fxslotdata else None
                            fxparams = fl_fxslotdata['pluginparams'] if 'pluginparams' in fl_fxslotdata else b''
                            plugin_obj, pluginid = flp_dec_plugins.getparams(convproj_obj, flpluginname, fxparams, samplefolder, datadef, dataset)
                            if "name" in fl_fxslotdata: plugin_obj.visual.name = fl_fxslotdata["name"] 
                            if 'color' in fl_fxslotdata: plugin_obj.visual.color = conv_color(fl_fxslotdata['color'])
                            fxchannel_obj.fxslots_audio.append(pluginid)
                            if FL_InitFXVals_exists == True:
                                fl_fxslot_initvals = FL_InitFXVals[int(fxchannel)][fl_fxslotnum]
                                fx_slot_on = struct.unpack('i', fl_fxslot_initvals[b'\x1f\x00'])[0] if b'\x1f\x00' in fl_fxslot_initvals else 1
                                fx_slot_wet = struct.unpack('i', fl_fxslot_initvals[b'\x1f\x01'])[0]/12800 if b'\x1f\x01' in fl_fxslot_initvals else 0
                                plugin_obj.fxdata_add(fx_slot_on, fx_slot_wet)

        for timemarker in FL_TimeMarkers:
            tm_pos = FL_TimeMarkers[timemarker]['pos']
            tm_type = FL_TimeMarkers[timemarker]['type']

            if tm_type == 8:
                convproj_obj.timesig_auto.add_point(tm_pos, [FL_TimeMarkers[timemarker]['numerator'], FL_TimeMarkers[timemarker]['denominator']])
            else:
                timemarker_obj = convproj_obj.add_timemarker()
                timemarker_obj.visual.name = FL_TimeMarkers[timemarker]['name']
                timemarker_obj.position = tm_pos
                if tm_type == 5: timemarker_obj.type = 'start'
                if tm_type == 4: timemarker_obj.type = 'loop'
                if tm_type == 1: timemarker_obj.type = 'markerloop'
                if tm_type == 2: timemarker_obj.type = 'markerskip'
                if tm_type == 3: timemarker_obj.type = 'pause'
                if tm_type == 9: timemarker_obj.type = 'punchin'
                if tm_type == 10: timemarker_obj.type = 'punchout'

        #if len(FL_Arrangements) == 0 and len(FL_Patterns) == 1 and len(FL_Channels) == 0:
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

        convproj_obj.do_actions.append('do_addloop')

        if 'Title' in FL_Main: convproj_obj.metadata.name = FL_Main['Title']
        if 'Author' in FL_Main: convproj_obj.metadata.author = FL_Main['Author']
        if 'Genre' in FL_Main: convproj_obj.metadata.genre = FL_Main['Genre']
        if 'URL' in FL_Main: convproj_obj.metadata.url = FL_Main['URL']
        if 'Comment' in FL_Main: convproj_obj.metadata.comment_text = FL_Main['Comment']