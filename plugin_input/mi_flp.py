# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import math
import base64
import struct
import av
import os.path
from pathlib import Path

from functions import format_flp_dec
from functions import note_mod
from functions import data_bytes
from functions import colors
from functions import notelist_data
from functions import data_values
from functions import song
from functions import audio


filename_len = {}


def getsamplefile(jsontag, channeldata, flppath):
    if 'samplefilename' in channeldata: 
        pathout = channeldata['samplefilename']
        samepath = os.path.join(os.path.dirname(flppath), os.path.basename(pathout))
        if os.path.exists(samepath): pathout = samepath

        jsontag['file'] = ''
        if pathout != None: 
            jsontag['file'] = pathout
            audioinfo = audio.get_audiofile_info(pathout)
            filename_len[pathout] = audioinfo
        return pathout
    else:
        return ''

class input_flp(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'flp'
    def getname(self): return 'FL Studio'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'track_lanes': True,
        'placement_cut': True,
        'placement_audio_stretch': ['rate', 'rate_ignoretempo']
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'FLhd': return True
        else: return False
    def parse(self, input_file, extra_param):
        FLP_Data = format_flp_dec.parse(input_file)
        #print(FLP_Data['FL_Main'])

        FL_Main = FLP_Data['FL_Main']
        FL_Patterns = FLP_Data['FL_Patterns']
        FL_Channels = FLP_Data['FL_Channels']
        FL_Mixer = FLP_Data['FL_Mixer']
        FL_Arrangements = FLP_Data['FL_Arrangements']
        FL_TimeMarkers = FLP_Data['FL_TimeMarkers']
        FL_FilterGroups = FLP_Data['FL_FilterGroups']

        ppq = FL_Main['ppq']

        cvpj_l = {}
        cvpj_l['vol'] = 1
        if 'MainPitch' in FL_Main: cvpj_l['pitch'] = struct.unpack('h', struct.pack('H', FL_Main['MainPitch']))[0]
        if 'Numerator' in FL_Main: cvpj_l['timesig_numerator'] = FL_Main['Numerator']
        else: cvpj_l['timesig_numerator'] = 4
        if 'Numerator' in FL_Main: cvpj_l['timesig_denominator'] = FL_Main['Numerator']
        else: cvpj_l['timesig_denominator'] = 4
        if 'Tempo' in FL_Main: cvpj_l['bpm'] = FL_Main['Tempo']
        else: cvpj_l['bpm'] = 120
        if 'Shuffle' in FL_Main: cvpj_l['shuffle'] = FL_Main['Shuffle']/128

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

        for instrument in FL_Channels:
            channeldata = FL_Channels[instrument]
            instdata = {}
            if channeldata['type'] in [0,2]:
                cvpj_inst = {}
                cvpj_inst['enabled'] = channeldata['enabled']
                cvpj_inst['chain_fx_note'] = []
                cvpj_inst['instdata'] = {}
                if 'middlenote' in channeldata: 
                    cvpj_inst['instdata']['middlenote'] = channeldata['middlenote'] - 60
                cvpj_inst['instdata']['pitch'] = channeldata['pitch']
                cvpj_inst['instdata']['usemasterpitch'] = channeldata['main_pitch']

                if 'name' in channeldata: cvpj_inst['name'] = channeldata['name']
                else: cvpj_inst['name'] = ''
                cvpj_inst['pan'] = channeldata['pan']
                cvpj_inst['vol'] = channeldata['volume']
                color = channeldata['color'].to_bytes(4, "little")
                cvpj_inst['color'] = [color[0]/255,color[1]/255,color[2]/255]
                cvpj_inst['fxrack_channel'] = channeldata['fxchannel']

                if channeldata['type'] == 0:
                    cvpj_inst['instdata']['plugin'] = "sampler"
                    cvpj_inst['instdata']['plugindata'] = {}
                    getsamplefile(cvpj_inst['instdata']['plugindata'], channeldata, input_file)
                if channeldata['type'] == 2:
                    cvpj_inst['instdata']['plugin'] = "native-fl"
                    cvpj_inst['instdata']['plugindata'] = {}
                    if 'plugin' in channeldata: cvpj_inst['instdata']['plugindata']['name'] = channeldata['plugin']
                    if 'pluginparams' in channeldata: cvpj_inst['instdata']['plugindata']['data'] = base64.b64encode(channeldata['pluginparams']).decode('ascii')
                cvpj_inst['poly'] = {}
                cvpj_inst['poly']['max'] = channeldata['polymax']

                cvpj_l_instrument_data['FLInst' + str(instrument)] = cvpj_inst
                cvpj_l_instrument_order.append('FLInst' + str(instrument))
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
                filename_sample = getsamplefile(cvpj_s_sample, channeldata, input_file)

                sampleinfo[instrument] = audio.get_audiofile_info(filename_sample)
                if filename_sample in filename_len: ald = filename_len[filename_sample]
                stretchbpm = (ald['dur_sec']*(cvpj_l['bpm']/120))

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

                if t_stretchingtime != 0:
                    cvpj_audiomod['stretch_method'] = 'rate_ignoretempo'
                    cvpj_audiomod['stretch_data'] = {}
                    cvpj_audiomod['stretch_data']['rate'] = (ald['dur_sec']/t_stretchingtime)/t_stretchingmultiplier
                    samplestretch[instrument] = (ald['dur_sec']/t_stretchingtime)*t_stretchingmultiplier

                elif t_stretchingtime == 0:
                    cvpj_audiomod['stretch_method'] = 'rate'
                    cvpj_audiomod['stretch_data'] = {}
                    cvpj_audiomod['stretch_data']['rate'] = 1/t_stretchingmultiplier
                    samplestretch[instrument] = 1*t_stretchingmultiplier

                else:
                    samplestretch[instrument] = 1

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
                        if nn_pos <= sn_pos <= nn_pos+nn_dur and sn_inst == nn_inst:
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
                    if 'startoffset' in item or 'endoffset' in item:
                        arrangementitemJ['cut'] = {}
                        arrangementitemJ['cut']['type'] = 'cut'

                        pl_stretch = samplestretch[str(item['itemindex'])]

                        if 'startoffset' in item: 
                            data_values.time_from_steps(arrangementitemJ['cut'], 'start', False, item['startoffset'], pl_stretch)

                        if 'endoffset' in item: 
                            data_values.time_from_steps(arrangementitemJ['cut'], 'end', False, item['endoffset'], pl_stretch)

                        #print(arrangementitemJ)

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
                        fxslotdata = {}
                        fxslotdata['enabled'] = 1
                        fxslotdata['plugin'] = 'native-fl'
                        if 'color' in fl_fxslotdata:
                            color = fl_fxslotdata['color'].to_bytes(4, "little")
                            fxslotdata['color'] = [color[0]/255,color[1]/255,color[2]/255]
                        fxslotdata['plugindata'] = {}
                        fxslotdata['plugindata']['plugin'] = fl_fxslotdata['plugin']
                        fxslotdata['plugindata']['data'] = base64.b64encode(fl_fxslotdata['pluginparams']).decode('ascii')
                        fxdata["chain_fx_audio"].append(fxslotdata)

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

        cvpj_l['instruments_order'] = cvpj_l_instrument_order
        cvpj_l['instruments_data'] = cvpj_l_instrument_data
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['playlist'] = cvpj_l_playlist
        #cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['timemarkers'] = cvpj_l_timemarkers
        cvpj_l['sampleindex'] = cvpj_l_samples

        if 'Title' in FL_Main: song.add_info(cvpj_l, 'title', FL_Main['Title'])
        if 'Author' in FL_Main: song.add_info(cvpj_l, 'author', FL_Main['Author'])
        if 'Genre' in FL_Main: song.add_info(cvpj_l, 'genre', FL_Main['Genre'])
        if 'URL' in FL_Main: song.add_info(cvpj_l, 'url', FL_Main['URL'])
        if 'Comment' in FL_Main: song.add_info_msg(cvpj_l, 'text', FL_Main['Comment'])

        return json.dumps(cvpj_l, indent=2)