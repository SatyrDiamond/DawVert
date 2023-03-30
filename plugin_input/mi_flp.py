# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import math
import base64
import struct
from functions import format_flp_dec
from functions import note_mod
from functions import colors
from functions import notelist_data

def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

class input_flp(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'flp'
    def getname(self): return 'FL Studio'
    def gettype(self): return 'mi'
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'r_track_lanes': True,
        'placement_cut': True,
        'placement_warp': False,
        'no_placements': False
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
        cvpj_l_notelistindex = {}
        cvpj_l_fxrack = {}
        cvpj_l_playlist = {}
        cvpj_l_timemarkers = []

        id_inst = {}
        id_pat = {}

        for instrument in FL_Channels:
            channeldata = FL_Channels[instrument]
            #print(channeldata)
            instdata = {}
            if channeldata['type'] == 0 or channeldata['type'] == 2:
                cvpj_inst = {}
                cvpj_inst['instdata'] = {}
                cvpj_inst['enabled'] = channeldata['enabled']
                cvpj_inst['fxrack_channel'] = channeldata['fxchannel']
                #cvpj_inst['filtergroup'] = 'FLFilterGroup_'+str(channeldata['filtergroup'])
                cvpj_inst['chain_fx_note'] = []
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
                if channeldata['type'] == 0:
                    cvpj_inst['instdata']['plugin'] = "sampler"
                    cvpj_inst['instdata']['plugindata'] = {}
                    if 'samplefilename' in channeldata: cvpj_inst['instdata']['plugindata']['file'] = channeldata['samplefilename']
                    else: cvpj_inst['instdata']['plugindata']['file'] = ''
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
                    cvpj_note['channel'] = splitbyte(flnote['midich'])[1]+1
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
                arrangementitemJ['type'] = 'instruments'
                arrangementitemJ['fromindex'] = 'FLPat' + str(item['itemindex'] - item['patternbase'])
                if 'startoffset' in item or 'endoffset' in item:
                    arrangementitemJ['cut'] = {}
                    arrangementitemJ['cut']['type'] = 'cut'
                    if 'startoffset' in item: arrangementitemJ['cut']['start'] = item['startoffset']/ppq*4
                    if 'endoffset' in item: arrangementitemJ['cut']['end'] = item['endoffset']/ppq*4
                playlistline = (item['trackindex']*-1)+500
                length = item['length']
                arrangementitemJ['muted'] = bool(item['flags'] & 0b0001000000000000)
                if str(playlistline) not in cvpj_l_playlist:
                    cvpj_l_playlist[str(playlistline)] = {}
                    cvpj_l_playlist[str(playlistline)]['placements_notes'] = []
                cvpj_l_playlist[str(playlistline)]['placements_notes'].append(arrangementitemJ)

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
                    cvpj_l_playlist[str(track)]['size'] = FL_Tracks[track]['height']
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
                    if fl_fxslotdata != None:
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
                arrangementitemJ['type'] = 'instruments'
                arrangementitemJ['fromindex'] = 'FLPat0'

                cvpj_l_playlist["1"] = {}
                cvpj_l_playlist["1"]['placements_notes'] = []
                cvpj_l_playlist["1"]['placements_notes'].append(arrangementitemJ)

        cvpj_l['do_addwrap'] = True

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = True
        
        cvpj_l['instruments_order'] = cvpj_l_instrument_order
        cvpj_l['instruments_data'] = cvpj_l_instrument_data
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['timemarkers'] = cvpj_l_timemarkers
        cvpj_l['filtergroups'] = {}

        for filtergroupnum in range(len(FL_FilterGroups)):
            cvpj_l['filtergroups']['FLFilterGroup_'+str(filtergroupnum)] = {}
            cvpj_l['filtergroups']['FLFilterGroup_'+str(filtergroupnum)]['name'] = FL_FilterGroups[filtergroupnum]

        cvpj_l['info'] = {}
        if 'Title' in FL_Main: cvpj_l['info']['title'] = FL_Main['Title']
        if 'Author' in FL_Main: cvpj_l['info']['author'] = FL_Main['Author']
        if 'Genre' in FL_Main: cvpj_l['info']['genre'] = FL_Main['Genre']
        if 'URL' in FL_Main: cvpj_l['info']['url'] = FL_Main['URL']

        if 'Comment' in FL_Main:
            cvpj_l['info']['message'] = {}
            cvpj_l['info']['message']['type'] = 'text'
            cvpj_l['info']['message']['text'] = FL_Main['Comment']

        return json.dumps(cvpj_l, indent=2)