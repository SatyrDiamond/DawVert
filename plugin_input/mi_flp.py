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

from functions_plugin import flp_dec_pluginparams
from functions import format_flp_dec
from functions import note_mod
from functions import data_bytes
from functions import colors
from functions import notelist_data
from functions import data_values
from functions import song
from functions import audio
from functions import plugins
from functions import tracks

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

    plugins.add_asdr_env(cvpj_l, pluginid, envtype, el_env_predelay, el_env_attack, el_env_hold, el_env_decay, el_env_sustain, el_env_release, el_env_aomunt)
    plugins.add_asdr_env_tension(cvpj_l, pluginid, envtype, el_env_attack_tension, el_env_decay_tension, el_env_release_tension)



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

        ppq = FL_Main['ppq']

        cvpj_l = {}
        cvpj_l['timesig'] = [4, 4]

        if 'Numerator' in FL_Main: cvpj_l['timesig'][0] = FL_Main['Numerator']
        if 'Denominator' in FL_Main: cvpj_l['timesig'][1] = FL_Main['Denominator']
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
        cvpj_l_fxrack = {}
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

                if 'name' in channeldata: cvpj_inst_name = channeldata['name']
                else: cvpj_inst_name = ''

                color = channeldata['color'].to_bytes(4, "little")
                cvpj_inst_color = [color[0]/255,color[1]/255,color[2]/255]

                tracks.m_inst_create(cvpj_l, cvpj_instid, name=cvpj_inst_name, color=cvpj_inst_color)

                tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'enabled', channeldata['enabled'], 'bool')

                if 'middlenote' in channeldata: 
                    tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'middlenote', channeldata['middlenote']-60)

                tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'pitch', channeldata['pitch']/100, 'float')
                tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'usemasterpitch', channeldata['main_pitch'], 'bool')
                tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'pan', channeldata['pan'], 'float')
                tracks.m_inst_add_param(cvpj_l, cvpj_instid, 'vol', channeldata['volume'], 'float')
                tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'fxrack_channel', channeldata['fxchannel'])

                pluginid = plugins.get_id()

                if channeldata['type'] == 0:
                    tracks.m_inst_pluginid(cvpj_l, cvpj_instid, pluginid)
                    plugins.add_plug_sampler_singlefile(cvpj_l, pluginid, getsamplefile(channeldata, input_file))

                    tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'remove_dc', channeldata['remove_dc'])
                    tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'normalize', channeldata['normalize'])
                    tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'reversepolarity', channeldata['reversepolarity'])

                    cvpj_loopdata = {}
                    if 'sampleflags' in channeldata:
                        fl_sampleflags = data_bytes.to_bin(channeldata['sampleflags'], 8)
                        cvpj_loopdata['enabled'] = fl_sampleflags[4]
                        interpolation = "none"
                        if fl_sampleflags[7] == 1: interpolation = "sinc"
                        tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, None, 'interpolation', interpolation)

                    if 'looptype' in channeldata:
                        fl_looptype = channeldata['looptype']
                        if fl_looptype == 0: cvpj_loopdata['mode'] = "normal"
                        else: cvpj_loopdata['mode'] = "pingpong"

                    plugins.add_plug_data(cvpj_l, pluginid, 'loop', cvpj_loopdata)
                    
                if channeldata['type'] == 2:
                    tracks.m_inst_pluginid(cvpj_l, cvpj_instid, pluginid)
                    filename_sample = getsamplefile(channeldata, input_file)
                    plugins.add_fileref(cvpj_l, pluginid, 'audiofile', filename_sample)

                    flpluginname = ''
                    if 'plugin' in channeldata: 
                        plugins.add_plug(cvpj_l, pluginid, 'native-flstudio', channeldata['plugin'])
                    if 'pluginparams' in channeldata: 
                        flp_dec_pluginparams.getparams(cvpj_l, pluginid, channeldata['plugin'], channeldata['pluginparams'], samplefolder)

                #parse_envlfo(channeldata['envlfo_vol'], pluginid, 'vol')

                tracks.m_inst_add_dataval(cvpj_l, cvpj_instid, 'poly', 'max', channeldata['polymax'])

                id_inst[str(instrument)] = 'FLInst' + str(instrument)

            if channeldata['type'] == 4:
                cvpj_s_sample = {}
                if 'name' in channeldata: cvpj_s_sample['name'] = channeldata['name']
                else: cvpj_s_sample['name'] = ''
                cvpj_s_sample['pan'] = channeldata['pan']
                cvpj_s_sample['vol'] = channeldata['volume']
                color = channeldata['color'].to_bytes(4, "little")
                cvpj_s_sample['color'] = [color[0]/255,color[1]/255,color[2]/255]
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
                        color = FL_Tracks[track]['color'].to_bytes(4, "little")
                        cvpj_l_playlist[str(track)]['color'] = [color[0]/255,color[1]/255,color[2]/255]
                    if 'name' in FL_Tracks[track]:
                        cvpj_l_playlist[str(track)]['name'] = FL_Tracks[track]['name']
                    if 'height' in FL_Tracks[track]:
                        cvpj_l_playlist[str(track)]['size'] = FL_Tracks[track]['height']
                    if 'enabled' in FL_Tracks[track]:
                        cvpj_l_playlist[str(track)]['enabled'] = FL_Tracks[track]['enabled']

        for fxchannel in FL_Mixer:
            fl_fxhan = FL_Mixer[str(fxchannel)]
            cvpj_l_fxrack[fxchannel] = {}
            fxdata = cvpj_l_fxrack[fxchannel]
            fxdata["fxenabled"] = 1
            fxdata["chain_fx_audio"] = []
            fxdata["muted"] = 0
            fxdata["sends"] = []
            if 'name' in fl_fxhan:
                fxdata["name"] = fl_fxhan['name']
            if 'color' in fl_fxhan:
                if fl_fxhan['color'] != None:
                    color = fl_fxhan['color'].to_bytes(4, "little")
                    fxdata['color'] = [color[0]/255,color[1]/255,color[2]/255]
            if 'routing' in fl_fxhan:
                for route in fl_fxhan['routing']:
                    fxdata["sends"].append({"amount": 1.0, "channel": route})

            if 'slots' in fl_fxhan:
                for fl_fxslot in fl_fxhan['slots']:
                    fl_fxslotdata = fl_fxhan['slots'][fl_fxslot]
                    if fl_fxslotdata != None and 'plugin' in fl_fxslotdata and 'pluginparams' in fl_fxslotdata:

                        pluginid = plugins.get_id()

                        fxslotdata = {}
                        fxslotdata['pluginid'] = pluginid
                        flpluginname = ''
                        if 'plugin' in fl_fxslotdata: flpluginname = fl_fxslotdata['plugin']
                        plugins.add_plug(cvpj_l, pluginid, 'native-flstudio', flpluginname)
                        if 'pluginparams' in fl_fxslotdata: 
                            flp_dec_pluginparams.getparams(cvpj_l, pluginid, flpluginname, fl_fxslotdata['pluginparams'], samplefolder)

                        v_color = None
                        if 'color' in fl_fxslotdata:
                            color = fl_fxslotdata['color'].to_bytes(4, "little")
                            v_color = [color[0]/255,color[1]/255,color[2]/255]
                        plugins.add_plug_fxvisual(cvpj_l, pluginid, None, v_color)

                        fxdata["chain_fx_audio"].append(pluginid)

            if fxchannel == '100': fxdata["vol"] = 0.0
            elif fxchannel == '101': fxdata["vol"] = 0.0
            elif fxchannel == '102': fxdata["vol"] = 0.0
            elif fxchannel == '103': fxdata["vol"] = 0.0
            else: fxdata["vol"] = 1.0

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
        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['timemarkers'] = cvpj_l_timemarkers
        cvpj_l['sampleindex'] = cvpj_l_samples

        if 'Title' in FL_Main: song.add_info(cvpj_l, 'title', FL_Main['Title'])
        if 'Author' in FL_Main: song.add_info(cvpj_l, 'author', FL_Main['Author'])
        if 'Genre' in FL_Main: song.add_info(cvpj_l, 'genre', FL_Main['Genre'])
        if 'URL' in FL_Main: song.add_info(cvpj_l, 'url', FL_Main['URL'])
        if 'Comment' in FL_Main: song.add_info_msg(cvpj_l, 'text', FL_Main['Comment'])

        return json.dumps(cvpj_l, indent=2)