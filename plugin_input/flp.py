# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import math
import base64
import struct
from functions import format_flp_dec
from functions import note_mod

class input_flp(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'flp'
    def getname(self): return 'FL Studio'
    def gettype(self): return 'mi'
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

        ppq = FL_Main['ppq']

        rootJ = {}
        rootJ['vol'] = 1
        if 'MainPitch' in FL_Main:
            rootJ['pitch'] = struct.unpack('h', struct.pack('H', FL_Main['MainPitch']))[0]
        rootJ['timesig_numerator'] = FL_Main['Numerator']
        rootJ['timesig_denominator'] = FL_Main['Denominator']
        rootJ['bpm'] = FL_Main['Tempo']
        rootJ['shuffle'] = FL_Main['Shuffle']/128

        instrumentsJ = {}
        instrumentsorder = []
        notelistindexJ = {}
        fxrackJ = {}
        playlistJ = {}
        timemarkersJ = []

        id_inst = {}
        id_pat = {}

        for instrument in FL_Channels:
            channeldata = FL_Channels[instrument]
            #print(channeldata)
            instdata = {}
            if channeldata['type'] == 0 or channeldata['type'] == 2:
                singleinstdata = {}
                singleinstdata['instdata'] = {}
                singleinstdata['enabled'] = channeldata['enabled']
                singleinstdata['fxrack_channel'] = channeldata['fxchannel']
                middlenote = 0
                if 'middlenote' in channeldata: middlenote = channeldata['middlenote'] - 60
                singleinstdata['instdata']['notefx'] = {}
                singleinstdata['instdata']['notefx']['pitch'] = {}
                singleinstdata['instdata']['notefx']['pitch']['semitones'] = middlenote
                singleinstdata['instdata']['pitch'] = channeldata['pitch']
                singleinstdata['instdata']['usemasterpitch'] = channeldata['main_pitch']
                if 'name' in channeldata: singleinstdata['name'] = channeldata['name']
                else: singleinstdata['name'] = ''
                singleinstdata['pan'] = channeldata['pan']
                singleinstdata['vol'] = channeldata['volume']
                color = channeldata['color'].to_bytes(4, "little")
                singleinstdata['color'] = [color[0]/255,color[1]/255,color[2]/255]
                if channeldata['type'] == 0:
                    singleinstdata['instdata']['plugin'] = "sampler"
                    singleinstdata['instdata']['plugindata'] = {}
                    if 'samplefilename' in channeldata: singleinstdata['instdata']['plugindata']['file'] = channeldata['samplefilename']
                    else: singleinstdata['instdata']['plugindata']['file'] = ''
                if channeldata['type'] == 2:
                    singleinstdata['instdata']['plugin'] = "native-fl"
                    singleinstdata['instdata']['plugindata'] = {}
                    if 'plugin' in channeldata: singleinstdata['instdata']['plugindata']['name'] = channeldata['plugin']
                    if 'pluginparams' in channeldata: singleinstdata['instdata']['plugindata']['data'] = base64.b64encode(channeldata['pluginparams']).decode('ascii')

                singleinstdata['poly'] = {}
                singleinstdata['poly']['max'] = channeldata['polymax']

                instrumentsJ['FLInst' + str(instrument)] = singleinstdata
                instrumentsorder.append('FLInst' + str(instrument))
                id_inst[str(instrument)] = 'FLInst' + str(instrument)

        for pattern in FL_Patterns:
            patterndata = FL_Patterns[pattern]
            notesJ = []
            if 'FLPat' + str(pattern) not in notelistindexJ:
                notelistindexJ['FLPat' + str(pattern)] = {}
            if 'notes' in patterndata:
                slidenotes = []
                for flnote in patterndata['notes']:
                    noteJ = {}
                    noteJ['position'] = (flnote['pos']/ppq)*4
                    if str(flnote['rack']) in id_inst: noteJ['instrument'] = id_inst[str(flnote['rack'])]
                    else: noteJ['instrument'] = ''
                    noteJ['duration'] = (flnote['dur']/ppq)*4
                    noteJ['key'] = flnote['key']-60
                    noteJ['finepitch'] = (flnote['finep']-120)*10
                    noteJ['release'] = flnote['rel']/128
                    noteJ['pan'] = (flnote['pan']-64)/64
                    noteJ['vol'] = flnote['velocity']/100
                    noteJ['cutoff'] = flnote['mod_x']/255
                    noteJ['reso'] = flnote['mod_y']/255
                    noteJ['notemod'] = {}
                    is_slide = bool(flnote['flags'] & 0b000000000001000)

                    if is_slide == True: 
                        slidenotes.append(noteJ)
                    else: 
                        noteJ['notemod']['slide'] = []
                        notesJ.append(noteJ)
                for slidenote in slidenotes:
                    sn_pos = slidenote['position']
                    sn_dur = slidenote['duration']
                    sn_inst = slidenote['instrument']
                    for noteJ in notesJ:
                        nn_pos = noteJ['position']
                        nn_dur = noteJ['duration']
                        nn_inst = noteJ['instrument']
                        if nn_pos <= sn_pos <= nn_pos+nn_dur and sn_inst == nn_inst:
                            slidenote['position'] = sn_pos - nn_pos 
                            slidenote['key'] -= noteJ['key'] 
                            noteJ['notemod']['slide'].append(slidenote)
                for noteJ in notesJ:
                    note_mod.notemod_conv(noteJ)

                notelistindexJ['FLPat' + str(pattern)]['notelist'] = notesJ
                id_pat[str(pattern)] = 'FLPat' + str(pattern)
            if 'color' in patterndata:
                color = patterndata['color'].to_bytes(4, "little")
                if color != b'HQV\x00':
                    notelistindexJ['FLPat' + str(pattern)]['color'] = [color[0]/255,color[1]/255,color[2]/255]
            if 'name' in patterndata: notelistindexJ['FLPat' + str(pattern)]['name'] = patterndata['name']

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
            if str(playlistline) not in playlistJ:
                playlistJ[str(playlistline)] = {}
                playlistJ[str(playlistline)]['placements'] = []
            playlistJ[str(playlistline)]['placements'].append(arrangementitemJ)

        FL_Tracks = FL_Arrangement['tracks']

        for track in FL_Tracks:
            if str(track) not in playlistJ:
                playlistJ[str(track)] = {}
            if 'color' in FL_Tracks[track]:
                color = FL_Tracks[track]['color'].to_bytes(4, "little")
            playlistJ[str(track)]['color'] = [color[0]/255,color[1]/255,color[2]/255]
            if 'name' in FL_Tracks[track]:
                playlistJ[str(track)]['name'] = FL_Tracks[track]['name']

        for fxchannel in FL_Mixer:
            fl_fxhan = FL_Mixer[str(fxchannel)]
            fxrackJ[fxchannel] = {}
            fxdata = fxrackJ[fxchannel]
            fxdata["fxenabled"] = 1
            fxdata["fxchain_audio"] = []
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
            timemarkersJ.append(timemarkerJ)

        rootJ['use_fxrack'] = True
        rootJ['instrumentsorder'] = instrumentsorder
        rootJ['instruments'] = instrumentsJ
        rootJ['notelistindex'] = notelistindexJ
        rootJ['playlist'] = playlistJ
        rootJ['fxrack'] = fxrackJ
        rootJ['timemarkers'] = timemarkersJ

        rootJ['info'] = {}
        rootJ['info']['title'] = FL_Main['Title']
        rootJ['info']['author'] = FL_Main['Author']
        rootJ['info']['genre'] = FL_Main['Genre']
        if 'URL' in FL_Main: rootJ['info']['url'] = FL_Main['URL']
        
        rootJ['info']['message'] = {}
        rootJ['info']['message']['type'] = 'text'
        rootJ['info']['message']['text'] = FL_Main['Comment']

        return json.dumps(rootJ, indent=2)