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
from functions import note_mod
from functions import data_bytes
from functions import colors
from functions import notelist_data
from functions import data_values
from functions import song
from functions import audio
from functions import plugins
from functions import params
from functions_tracks import tracks_mi
from functions_tracks import fxrack
from functions_tracks import fxslot

filename_len = {}

def getsamplefile(channeldata, flppath):

    if 'samplefilename' in channeldata: 
        pathout = channeldata['samplefilename']
        samepath = os.path.join(os.path.dirname(flppath), os.path.basename(pathout))
        if os.path.exists(samepath): pathout = samepath

        if pathout != None and pathout.split('.')[-1] not in ['SYN', 'syn']:
            audioinfo = audio.get_audiofile_info(pathout)
            filename_len[pathout] = audioinfo
        return pathout
    else:
        return ''


def conv_color(b_color):
    color = b_color.to_bytes(4, "little")
    cvpj_inst_color = [color[0]/255,color[1]/255,color[2]/255]
    return cvpj_inst_color


def calc_time(i_value):
    oneval = i_value/65535
    outval = math.log10(oneval)

    for val in [i_value, oneval, outval]:
        print(str(val).rjust(24), end=' ')
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
    def parse(self, input_file, extra_param):
        global cvpj_l
        FLP_Data = format_flp_dec.parse(input_file)

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

        cvpj_l = {}
        timesig_Numerator = FL_Main['Numerator'] if 'Numerator' in FL_Main else 4
        timesig_Denominator = FL_Main['Denominator'] if 'Denominator' in FL_Main else 4
        song.add_timesig(cvpj_l, timesig_Numerator, timesig_Denominator)

        if 'MainPitch' in FL_Main: song.add_param(cvpj_l, 'pitch', struct.unpack('h', struct.pack('H', FL_Main['MainPitch']))[0]/100)
        if 'Tempo' in FL_Main: song.add_param(cvpj_l, 'bpm', FL_Main['Tempo'])
        if 'Shuffle' in FL_Main: song.add_param(cvpj_l, 'shuffle', FL_Main['Shuffle']/128)
        song.add_param(cvpj_l, 'vol', 1)

        tempomul = (120/FL_Main['Tempo'])
        tempomulmin = (FL_Main['Tempo']/120)

        cvpj_l_instrument_data = {}
        cvpj_l_instrument_order = []
        cvpj_l_samples = {}
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}
        cvpj_l_timemarkers = []

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

                tracks_mi.inst_create(cvpj_l, cvpj_instid)
                cvpj_inst_name = channeldata['name'] if 'name' in channeldata else ''
                cvpj_inst_color = conv_color(channeldata['color'])
                tracks_mi.inst_visual(cvpj_l, cvpj_instid, name=cvpj_inst_name, color=cvpj_inst_color)

                tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'enabled', channeldata['enabled'], 'bool')

                if 'middlenote' in channeldata: 
                    tracks_mi.inst_dataval_add(cvpj_l, cvpj_instid, 'instdata', 'middlenote', channeldata['middlenote']-60)

                tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'pitch', channeldata['pitch']/100, 'float')
                tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'usemasterpitch', channeldata['main_pitch'], 'bool')
                tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'pan', channeldata['pan'], 'float')
                tracks_mi.inst_param_add(cvpj_l, cvpj_instid, 'vol', channeldata['volume'], 'float')
                tracks_mi.inst_fxrackchan_add(cvpj_l, cvpj_instid, channeldata['fxchannel'])

                pluginid = plugins.get_id()

                if channeldata['type'] == 0:
                    tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)
                    inst_plugindata = plugins.cvpj_plugin('sampler', getsamplefile(channeldata, input_file), None)

                    inst_plugindata.dataval_add('remove_dc', channeldata['remove_dc'])
                    inst_plugindata.dataval_add('normalize', channeldata['normalize'])
                    inst_plugindata.dataval_add('reversepolarity', channeldata['reversepolarity'])

                    cvpj_loopdata = {}
                    if 'sampleflags' in channeldata:
                        fl_sampleflags = data_bytes.to_bin(channeldata['sampleflags'], 8)
                        cvpj_loopdata['enabled'] = fl_sampleflags[4]
                        interpolation = "none"
                        if fl_sampleflags[7] == 1: interpolation = "sinc"
                        inst_plugindata.dataval_add('interpolation', interpolation)

                    if 'looptype' in channeldata:
                        cvpj_loopdata['mode'] = "normal" if channeldata['looptype'] == 0 else "pingpong"

                    inst_plugindata.dataval_add('loop', cvpj_loopdata)
                    inst_plugindata.to_cvpj(cvpj_l, pluginid)
                    
                if channeldata['type'] == 2:
                    tracks_mi.inst_pluginid(cvpj_l, cvpj_instid, pluginid)
                    filename_sample = getsamplefile(channeldata, input_file)

                    flpluginname = channeldata['plugin'] if 'plugin' in channeldata else None
                    flplugindata = channeldata['plugindata'] if 'plugindata' in channeldata else None
                    flpluginparams = channeldata['pluginparams'] if 'pluginparams' in channeldata else b''

                    plug_exists = None

                    if flplugindata != None:

                        window_detatched = flplugindata[16]&4
                        window_active = flplugindata[16]&1
                        window_data = struct.unpack('iiii', flplugindata[36:52])
                        window_size = window_data[2:4] if window_active else None
                        song.add_visual_window(cvpj_l, 'plugin', pluginid, window_data[0:2], window_size, bool(window_active), False)

                    if flpluginname != None: 
                        inst_plugindata = flp_dec_plugins.getparams(cvpj_l, pluginid, flpluginname, flpluginparams, samplefolder)
                        inst_plugindata.fileref_add('audiofile', filename_sample)
                        inst_plugindata.to_cvpj(cvpj_l, pluginid)


                    #if plug_exists == True:
                    #    print(channeldata['plugin'])

                tracks_mi.inst_dataval_add(cvpj_l, cvpj_instid, 'poly', 'max', channeldata['polymax'])

                id_inst[str(instrument)] = 'FLInst' + str(instrument)

            if channeldata['type'] == 4:
                cvpj_s_sample = {}
                if 'name' in channeldata: cvpj_s_sample['name'] = channeldata['name']
                else: cvpj_s_sample['name'] = ''
                cvpj_s_sample['pan'] = channeldata['pan']
                cvpj_s_sample['vol'] = channeldata['volume']
                cvpj_s_sample['color'] = conv_color(channeldata['color'])
                cvpj_s_sample['fxrack_channel'] = channeldata['fxchannel']
                filename_sample = getsamplefile(channeldata, input_file)
                cvpj_s_sample['file'] = filename_sample

                ald = None
                sampleinfo[instrument] = audio.get_audiofile_info(filename_sample)
                if filename_sample in filename_len: ald = filename_len[filename_sample]
                if ald != None: stretchbpm = ald['dur_sec']*tempomulmin

                cvpj_audiomod = cvpj_s_sample['audiomod'] = {}

                t_stretchingmode = 0
                t_stretchingtime = 0
                t_stretchingmultiplier = 1
                t_stretchingpitch = 0
                cvpj_audiomod['stretch_method'] = None

                if 'stretchingpitch' in channeldata: t_stretchingpitch += channeldata['stretchingpitch']/100
                if 'middlenote' in channeldata: t_stretchingpitch += (channeldata['middlenote']-60)*-1
                if 'pitch' in channeldata: t_stretchingpitch += channeldata['pitch']/100
                cvpj_audiomod['pitch'] = t_stretchingpitch

                if 'stretchingtime' in channeldata: t_stretchingtime = channeldata['stretchingtime']/384
                if 'stretchingmode' in channeldata: t_stretchingmode = channeldata['stretchingmode']
                if 'stretchingmultiplier' in channeldata: t_stretchingmultiplier = pow(2, channeldata['stretchingmultiplier']/10000)

                if t_stretchingmode == -1: cvpj_audiomod['stretch_algorithm'] = 'stretch'
                if t_stretchingmode == 0: cvpj_audiomod['stretch_algorithm'] = 'resample'
                if t_stretchingmode == 1: cvpj_audiomod['stretch_algorithm'] = 'elastique_v3'
                if t_stretchingmode == 2: cvpj_audiomod['stretch_algorithm'] = 'elastique_v3_mono'
                if t_stretchingmode == 3: cvpj_audiomod['stretch_algorithm'] = 'slice_stretch'
                if t_stretchingmode == 5: cvpj_audiomod['stretch_algorithm'] = 'auto'
                if t_stretchingmode == 4: cvpj_audiomod['stretch_algorithm'] = 'slice_map'
                if t_stretchingmode == 6: cvpj_audiomod['stretch_algorithm'] = 'elastique_v2'
                if t_stretchingmode == 7: cvpj_audiomod['stretch_algorithm'] = 'elastique_v2_transient'
                if t_stretchingmode == 8: cvpj_audiomod['stretch_algorithm'] = 'elastique_v2_mono'
                if t_stretchingmode == 9: cvpj_audiomod['stretch_algorithm'] = 'elastique_v2_speech'

                #if t_stretchingtime != 0 or t_stretchingmultiplier != 1 or t_stretchingpitch != 0:

                if ald != None:
                    if t_stretchingtime != 0:
                        cvpj_audiomod['stretch_method'] = 'rate_tempo'
                        cvpj_audiomod['stretch_data'] = {}
                        cvpj_audiomod['stretch_data']['rate'] = (ald['dur_sec']/t_stretchingtime)/t_stretchingmultiplier
                        samplestretch[instrument] = ['rate_tempo', (ald['dur_sec']/t_stretchingtime)/t_stretchingmultiplier]

                    elif t_stretchingtime == 0:
                        cvpj_audiomod['stretch_method'] = 'rate_speed'
                        cvpj_audiomod['stretch_data'] = {}
                        cvpj_audiomod['stretch_data']['rate'] = 1/t_stretchingmultiplier
                        samplestretch[instrument] = ['rate_speed', 1/t_stretchingmultiplier]

                    else:
                        samplestretch[instrument] = ['rate_speed', 1]

                cvpj_l_samples['FLSample' + str(instrument)] = cvpj_s_sample


        for pattern in FL_Patterns:
            patterndata = FL_Patterns[pattern]
            notesJ = []
            if 'FLPat' + str(pattern) not in cvpj_l_notelistindex:
                cvpj_l_notelistindex['FLPat' + str(pattern)] = {}
            if 'notes' in patterndata:
                slidenotes = []
                for flnote in patterndata['notes']:
                    cvpj_note = {}
                    cvpj_note['position'] = (flnote['pos']/ppq)*4
                    if str(flnote['rack']) in id_inst: cvpj_note['instrument'] = id_inst[str(flnote['rack'])]
                    else: cvpj_note['instrument'] = ''
                    cvpj_note['duration'] = (flnote['dur']/ppq)*4
                    cvpj_note['key'] = flnote['key']-60
                    cvpj_note['finepitch'] = (flnote['finep']-120)*10
                    cvpj_note['release'] = flnote['rel']/128
                    cvpj_note['pan'] = (flnote['pan']-64)/64
                    cvpj_note['vol'] = flnote['velocity']/100
                    cvpj_note['cutoff'] = flnote['mod_x']/255
                    cvpj_note['reso'] = flnote['mod_y']/255
                    cvpj_note['channel'] = data_bytes.splitbyte(flnote['midich'])[1]+1
                    cvpj_note['notemod'] = {}
                    is_slide = bool(flnote['flags'] & 0b000000000001000)

                    if is_slide == True: 
                        slidenotes.append(cvpj_note)
                    else: 
                        cvpj_note['notemod']['slide'] = []
                        notesJ.append(cvpj_note)
                for slidenote in slidenotes:
                    sn_pos = slidenote['position']
                    sn_dur = slidenote['duration']
                    sn_inst = slidenote['instrument']
                    for cvpj_note in notesJ:
                        nn_pos = cvpj_note['position']
                        nn_dur = cvpj_note['duration']
                        nn_inst = cvpj_note['instrument']
                        if nn_pos <= sn_pos < nn_pos+nn_dur and sn_inst == nn_inst:
                            slidenote['position'] = sn_pos - nn_pos 
                            slidenote['key'] -= cvpj_note['key'] 
                            cvpj_note['notemod']['slide'].append(slidenote)
                for cvpj_note in notesJ:
                    note_mod.notemod_conv(cvpj_note)

                cvpj_l_notelistindex['FLPat' + str(pattern)]['notelist'] = notesJ
                id_pat[str(pattern)] = 'FLPat' + str(pattern)
            if 'color' in patterndata:
                color = patterndata['color'].to_bytes(4, "little")
                if color != b'HQV\x00':
                    cvpj_l_notelistindex['FLPat' + str(pattern)]['color'] = [color[0]/255,color[1]/255,color[2]/255]
            if 'name' in patterndata: cvpj_l_notelistindex['FLPat' + str(pattern)]['name'] = patterndata['name']

        if len(FL_Arrangements) != 0:
            FL_Arrangement = FL_Arrangements['0']
            for item in FL_Arrangement['items']:

                arrangementitemJ = {}
                arrangementitemJ['position'] = item['position']/ppq*4
                arrangementitemJ['duration'] = item['length']/ppq*4
                playlistline = (item['trackindex']*-1)+500
                arrangementitemJ['muted'] = bool(item['flags'] & 0b0001000000000000)

                if str(playlistline) not in cvpj_l_playlist:
                    cvpj_l_playlist[str(playlistline)] = {}
                    cvpj_l_playlist[str(playlistline)]['placements_notes'] = []
                    cvpj_l_playlist[str(playlistline)]['placements_audio'] = []

                if item['itemindex'] > item['patternbase']:
                    arrangementitemJ['fromindex'] = 'FLPat' + str(item['itemindex'] - item['patternbase'])
                    cvpj_l_playlist[str(playlistline)]['placements_notes'].append(arrangementitemJ)
                    if 'startoffset' in item or 'endoffset' in item:
                        arrangementitemJ['cut'] = {}
                        arrangementitemJ['cut']['type'] = 'cut'
                        if 'startoffset' in item: arrangementitemJ['cut']['start'] = item['startoffset']/ppq*4
                        if 'endoffset' in item: arrangementitemJ['cut']['end'] = item['endoffset']/ppq*4


                else:
                    arrangementitemJ['fromindex'] = 'FLSample' + str(item['itemindex'])
                    cvpj_l_playlist[str(playlistline)]['placements_audio'].append(arrangementitemJ)

                    if str(item['itemindex']) in samplestretch: pl_stretch = samplestretch[str(item['itemindex'])]
                    else: pl_stretch = ['rate_speed', 1.0]

                    if 'startoffset' in item or 'endoffset' in item:
                        arrangementitemJ['cut'] = {}
                        arrangementitemJ['cut']['type'] = 'cut'

                        #print(pl_stretch)
  
                        if pl_stretch[0] == 'rate_speed':
                            if 'startoffset' in item: arrangementitemJ['cut']['start'] = (item['startoffset']/pl_stretch[1])/tempomul
                            if 'endoffset' in item: arrangementitemJ['cut']['end'] = (item['endoffset']/pl_stretch[1])/tempomul
                        if pl_stretch[0] == 'rate_tempo':
                            if 'startoffset' in item: arrangementitemJ['cut']['start'] = (item['startoffset']/pl_stretch[1])
                            if 'endoffset' in item: arrangementitemJ['cut']['end'] = (item['endoffset']/pl_stretch[1])
                        if 'startoffset' not in item: arrangementitemJ['cut']['start'] = 0

                    #for value in ['startoffset', 'endoffset']:
                    #    outprint = None
                    #    if value in item: outprint = round(item[value], 6)
                    #    print(str(outprint).ljust(13), end=' ')
                    #print(pl_stretch)

            FL_Tracks = FL_Arrangement['tracks']

            if len(FL_Tracks) != 0:
                for track in FL_Tracks:
                    #print(track, FL_Tracks[track])
                    if str(track) not in cvpj_l_playlist:
                        cvpj_l_playlist[str(track)] = {}
                    if 'color' in FL_Tracks[track]:
                        cvpj_l_playlist[str(track)]['color'] = conv_color(FL_Tracks[track]['color'])
                    if 'name' in FL_Tracks[track]:
                        cvpj_l_playlist[str(track)]['name'] = FL_Tracks[track]['name']
                    if 'height' in FL_Tracks[track]:
                        cvpj_l_playlist[str(track)]['size'] = FL_Tracks[track]['height']
                    if 'enabled' in FL_Tracks[track]:
                        cvpj_l_playlist[str(track)]['enabled'] = FL_Tracks[track]['enabled']


        #for hexnum in FL_InitFXVals:
        #    print(hexnum, FL_InitFXVals[test][0])


        for fxchannel in FL_Mixer:
            fl_fx_chan = FL_Mixer[str(fxchannel)]

            fx_name = fl_fx_chan["name"] if "name" in fl_fx_chan else None

            fx_color = None
            if 'color' in fl_fx_chan:
                if fl_fx_chan['color'] != None: fx_color = conv_color(fl_fx_chan['color'])

            #print(fxchannel)
            #for hexnum in fl_fxdata_initvals:
            #    print(hexnum, int.from_bytes(fl_fxdata_initvals[hexnum], "little", signed=True) )

            fx_volume = 1
            fx_pan = 0

            if FL_InitFXVals_exists == True and int(fxchannel) in FL_InitFXVals:
                fl_fxdata_initvals = FL_InitFXVals[int(fxchannel)][0]
                fx_volume = struct.unpack('i', fl_fxdata_initvals[b'\x1f\xc0'])[0]/12800 if b'\x1f\xc0' in fl_fxdata_initvals else 1
                fx_pan = struct.unpack('i', fl_fxdata_initvals[b'\x1f\xc1'])[0]/6400 if b'\x1f\xc1' in fl_fxdata_initvals else 0

            fxrack.add(cvpj_l, fxchannel, fx_volume, fx_pan, name=fx_name, color=fx_color)

            if 'routing' in fl_fx_chan:
                for route in fl_fx_chan['routing']:
                    fxrack.addsend(cvpj_l, fxchannel, route, 1, None)

            if 'slots' in fl_fx_chan:
                for fl_fxslotnum in range(10):
                    if fl_fxslotnum in fl_fx_chan['slots']:
                        fl_fxslotdata = fl_fx_chan['slots'][fl_fxslotnum]

                        if fl_fxslotdata != None and 'plugin' in fl_fxslotdata:
                            fxslotid = plugins.get_id()

                            flpluginname = fl_fxslotdata['plugin'] if 'plugin' in fl_fxslotdata else None

                            fx_plugindata = None
                            if 'pluginparams' in fl_fxslotdata: 
                                fx_plugindata = flp_dec_plugins.getparams(cvpj_l, fxslotid, flpluginname, fl_fxslotdata['pluginparams'], samplefolder)

                            if fx_plugindata != None:
                                v_name = fl_fxslotdata["name"] if "name" in fl_fxslotdata else None
                                v_color = None
                                if 'color' in fl_fxslotdata: v_color = conv_color(fl_fxslotdata['color'])
                                fx_plugindata.fxvisual_add(v_name, v_color)
                                fxslot.insert(cvpj_l, ['fxrack', fxchannel], 'audio', fxslotid)

                                if FL_InitFXVals_exists == True:
                                    fl_fxslot_initvals = FL_InitFXVals[int(fxchannel)][fl_fxslotnum]
                                    fx_slot_on = struct.unpack('i', fl_fxslot_initvals[b'\x1f\x00'])[0] if b'\x1f\x00' in fl_fxslot_initvals else 1
                                    fx_slot_wet = struct.unpack('i', fl_fxslot_initvals[b'\x1f\x01'])[0]/12800 if b'\x1f\x01' in fl_fxslot_initvals else 0
                                    fx_plugindata.fxdata_add(fx_slot_on, fx_slot_wet)
                                fx_plugindata.to_cvpj(cvpj_l, fxslotid)

        for timemarker in FL_TimeMarkers:
            tm_pos = FL_TimeMarkers[timemarker]['pos']/ppq*4
            tm_type = FL_TimeMarkers[timemarker]['type']
            timemarkerJ = {}
            timemarkerJ['name'] = FL_TimeMarkers[timemarker]['name']
            timemarkerJ['position'] = FL_TimeMarkers[timemarker]['pos']/ppq*4
            if tm_type == 5: timemarkerJ['type'] = 'start'
            if tm_type == 4: timemarkerJ['type'] = 'loop'
            if tm_type == 1: timemarkerJ['type'] = 'markerloop'
            if tm_type == 2: timemarkerJ['type'] = 'markerskip'
            if tm_type == 3: timemarkerJ['type'] = 'pause'
            if tm_type == 8: 
                timemarkerJ['type'] = 'timesig'
                timemarkerJ['numerator'] = FL_TimeMarkers[timemarker]['numerator']
                timemarkerJ['denominator'] = FL_TimeMarkers[timemarker]['denominator']
            if tm_type == 9: timemarkerJ['type'] = 'punchin'
            if tm_type == 10: timemarkerJ['type'] = 'punchout'
            cvpj_l_timemarkers.append(timemarkerJ)

        if len(FL_Arrangements) == 0 and len(FL_Patterns) == 1 and len(FL_Channels) == 0:
            fst_chan_notelist = [[] for x in range(16)]
            for cvpj_notedata in cvpj_l_notelistindex['FLPat0']['notelist']:
                cvpj_notedata['instrument'] = 'FST' + str(cvpj_notedata['channel'])
                fst_chan_notelist[cvpj_notedata['channel']-1].append(cvpj_notedata)

            for channum in range(16):
                cvpj_inst = {}
                cvpj_inst['name'] = 'Channel '+str(channum+1)
                cvpj_l_instrument_data['FST' + str(channum+1)] = cvpj_inst
                cvpj_l_instrument_order.append('FST' + str(channum+1))

                arrangementitemJ = {}
                arrangementitemJ['position'] = 0
                arrangementitemJ['duration'] = notelist_data.getduration(cvpj_l_notelistindex['FLPat0']['notelist'])
                arrangementitemJ['fromindex'] = 'FLPat0'

                cvpj_l_playlist["1"] = {}
                cvpj_l_playlist["1"]['placements_notes'] = []
                cvpj_l_playlist["1"]['placements_notes'].append(arrangementitemJ)

        cvpj_l['do_addloop'] = True

        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['timemarkers'] = cvpj_l_timemarkers
        cvpj_l['sampleindex'] = cvpj_l_samples

        if 'Title' in FL_Main: song.add_info(cvpj_l, 'title', FL_Main['Title'])
        if 'Author' in FL_Main: song.add_info(cvpj_l, 'author', FL_Main['Author'])
        if 'Genre' in FL_Main: song.add_info(cvpj_l, 'genre', FL_Main['Genre'])
        if 'URL' in FL_Main: song.add_info(cvpj_l, 'url', FL_Main['URL'])
        if 'Comment' in FL_Main: song.add_info_msg(cvpj_l, 'text', FL_Main['Comment'])

        return json.dumps(cvpj_l, indent=2)