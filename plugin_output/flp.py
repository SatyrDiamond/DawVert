# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later  

import plugin_output
import json
import math
import base64
import struct
from bs4 import BeautifulSoup
from functions_plugin import format_flp_enc
from functions_plugin import flp_enc_plugins
from functions import note_mod
from functions import data_values
from functions import audio
from functions import notelist_data
from functions import xtramath
from functions import plugins
from functions import params
from functions import song
from functions_tracks import tracks_mi

filename_len = {}

def decode_color(color):
    return int.from_bytes(bytes([int(color[0]*255), int(color[1]*255), int(color[2]*255)]), "little")

class output_cvpjs(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getshortname(self): return 'flp'
    def getname(self): return 'FL Studio'
    def gettype(self): return 'mi'
    def plugin_archs(self): return ['amd64', 'i386']
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'fxrack_params': ['enabled','vol','pan'],
        'track_lanes': True,
        'placement_cut': True,
        'placement_audio_stretch': ['rate', 'rate_ignoretempo']
        }
    def getsupportedplugformats(self): return ['vst2', 'vst3']
    def getsupportedplugins(self): return ['sampler:single', 'soundfont2']
    def getfileextension(self): return 'flp'
    def parse(self, convproj_json, output_file):
        cvpj_l = json.loads(convproj_json)

        FLP_Data = {}

        FLP_Data['FL_Main'] = {}
        FL_Main = FLP_Data['FL_Main']

        FLP_Data['FL_Channels'] = {}
        FL_Channels = FLP_Data['FL_Channels']
        instrumentsorder = cvpj_l['instruments_order'] if 'instruments_order' in cvpj_l else []
        CVPJ_Instruments = cvpj_l['instruments_data'] if 'instruments_data' in cvpj_l else {}
        CVPJ_Samples = {}
        if 'sampleindex' in cvpj_l: CVPJ_Samples = cvpj_l['sampleindex']

        FLP_Data['FL_Patterns'] = {}
        FL_Patterns = FLP_Data['FL_Patterns']
        CVPJ_NotelistIndex = cvpj_l['notelistindex']

        FLP_Data['FL_Arrangements'] = {}
        FL_Arrangements = FLP_Data['FL_Arrangements']

        FLP_Data['FL_TimeMarkers'] = {}
        FL_TimeMarkers = FLP_Data['FL_TimeMarkers']

        FLP_Data['FL_Tracks'] = {}
        FL_Tracks = FLP_Data['FL_Tracks']
        CVPJ_playlist = cvpj_l['playlist']

        FLP_Data['FL_Mixer'] = {}
        FL_Mixer = FLP_Data['FL_Mixer']

        FLP_Data['FL_FilterGroups'] = []
        FL_FilterGroups = FLP_Data['FL_FilterGroups']

        ppq = 960
        FL_Main['ppq'] = ppq
        
        FL_Main['ShowInfo'] = 0

        sampleinfo = {}
        samplestretch = {}

        if 'info' in cvpj_l: 
            infoJ = cvpj_l['info']
            FL_Main['ShowInfo'] = 1
            if 'title' in infoJ: 
                if 'title' not in ['', None]: FL_Main['Title'] = infoJ['title']
            else: FL_Main['Title'] = ''

            if 'author' in infoJ: 
                if 'author' not in ['', None]:  FL_Main['Author'] = infoJ['author']
            else: FL_Main['Author'] = ''

            if 'url' in infoJ: 
                if 'url' not in ['', None]:  FL_Main['URL'] = infoJ['url']
            else: FL_Main['URL'] = ''

            if 'genre' in infoJ: 
                if 'genre' not in ['', None]:  FL_Main['Genre'] = infoJ['genre']
            else: FL_Main['Genre'] = ''

            if 'message' in infoJ: 
                if infoJ['message']['type'] == 'html':
                    bst = BeautifulSoup(infoJ['message']['text'], "html.parser")
                    FL_Main['Comment'] = bst.get_text().replace("\n", "\r")
                if infoJ['message']['type'] == 'text':
                    FL_Main['Comment'] = infoJ['message']['text'].replace("\r\n", "\r").replace("\n", "\r")
            else: 
                FL_Main['Comment'] = ''
        else: 
            FL_Main['Title'] = ''
            FL_Main['Author'] = ''
            FL_Main['Genre'] = ''
            FL_Main['Comment'] = ''

        FL_Main['ProjectDataPath'] = ''

        FL_Main['Numerator'], FL_Main['Denominator'] = song.get_timesig(cvpj_l)
        FL_Main['Tempo'] = params.get(cvpj_l, [], 'bpm', 140)[0]
        FL_Main['MainPitch'] = struct.unpack('H', struct.pack('h', int(params.get(cvpj_l, [], 'pitch', 0)[0])))[0]
        FL_Main['Shuffle'] = params.get(cvpj_l, [], 'shuffle', 0)[0]*128

        tempomul = (120/FL_Main['Tempo'])

        samples_id = {}
        inst_id = {}
        inst_id_count = 0

        for instentry in instrumentsorder:
            inst_id[instentry] = str(inst_id_count)
            inst_id_count += 1

        for sampleentry in CVPJ_Samples:
            inst_id[sampleentry] = str(inst_id_count)
            samples_id[sampleentry] = str(inst_id_count)
            inst_id_count += 1

        for CVPJ_Entry in CVPJ_Instruments:
            T_Main = {}
            CVPJ_Data = CVPJ_Instruments[CVPJ_Entry]

            T_Main['volume'] = params.get(CVPJ_Data, [], 'vol', 1)[0]
            T_Main['pan'] = params.get(CVPJ_Data, [], 'pan', 0)[0]
            T_Main['enabled'] = int(params.get(CVPJ_Data, [], 'enabled', True)[0])
            T_Main['pitch'] = params.get(CVPJ_Data, [], 'pitch', 0)[0]
            T_Main['main_pitch'] = int(params.get(CVPJ_Data, [], 'usemasterpitch', True)[0])

            middlenote = data_values.nested_dict_get_value(CVPJ_Data, ['instdata', 'middlenote'])
            if middlenote == None: middlenote = 0

            T_Main['middlenote'] = middlenote+60

            if 'name' in CVPJ_Data: T_Main['name'] = CVPJ_Data['name'] if CVPJ_Data['name'] != None else ''

            T_Main['fxchannel'] = tracks_mi.inst_fxrackchan_get(cvpj_l, CVPJ_Entry)

            T_Main['type'] = 0
            T_Main['plugin'] = ''

            if 'instdata' in CVPJ_Data:
                CVPJ_Inst = CVPJ_Data['instdata']

                if 'pluginid' in CVPJ_Inst:
                    pluginid = CVPJ_Inst['pluginid']
                    plugintype = plugins.get_plug_type(cvpj_l, pluginid)

                    fl_plugin, fl_pluginparams = flp_enc_plugins.setparams(cvpj_l, pluginid)

                    if plugintype == ['sampler', 'single']:
                        T_Main['type'] = 0
                        T_Main['plugin'] = ''
                        cvpj_plugindata = plugins.get_plug_data(cvpj_l, pluginid)
                        T_Main['samplefilename'] = data_values.get_value(cvpj_plugindata, 'file', '')

                    elif fl_plugin != None:
                        fl_plugindata = b'\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00Q\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        fl_plugindata += b'\x00\x00\x00\x00'*4
                        T_Main['plugindata'] = fl_plugindata
                        T_Main['type'] = 2
                        T_Main['plugin'] = fl_plugin
                        T_Main['pluginparams'] = fl_pluginparams

            if 'poly' in CVPJ_Data: 
                if 'max' in CVPJ_Data['poly']: 
                    T_Main['polymax'] = CVPJ_Data['poly']['max']
            if 'color' in CVPJ_Data: 
                T_Main['color'] = decode_color(CVPJ_Data['color'])

            FL_Channels[inst_id[CVPJ_Entry]] = T_Main


        for CVPJ_Entry in CVPJ_Samples:
            T_Main = {}
            CVPJ_Data = CVPJ_Samples[CVPJ_Entry]
            T_Main['type'] = 4

            samplefilename = ""

            if 'vol' in CVPJ_Data: T_Main['volume'] = CVPJ_Data['vol']
            if 'pan' in CVPJ_Data: T_Main['pan'] = CVPJ_Data['pan']
            if 'name' in CVPJ_Data: T_Main['name'] = CVPJ_Data['name']
            if 'enabled' in CVPJ_Data: T_Main['enabled'] = CVPJ_Data['enabled']
            if 'fxrack_channel' in CVPJ_Data: T_Main['fxchannel'] = CVPJ_Data['fxrack_channel']
            if 'color' in CVPJ_Data:  T_Main['color'] = decode_color(CVPJ_Data['color'])
            if 'file' in CVPJ_Data: 
                T_Main['samplefilename'] = CVPJ_Data['file'] 
                samplefilename = CVPJ_Data['file']
                sampleinfo[CVPJ_Entry] = audio.get_audiofile_info(samplefilename)
                audioinfo = sampleinfo[CVPJ_Entry]

            audiorate = 1

            if 'audiomod' in CVPJ_Data: 

                cvpj_audiomod = CVPJ_Data['audiomod']

                if 'stretch_algorithm' in cvpj_audiomod: 
                    if cvpj_audiomod['stretch_algorithm'] == 'resample': T_Main['stretchingmode'] = 0
                    elif cvpj_audiomod['stretch_algorithm'] == 'elastique_v3': T_Main['stretchingmode'] = 1
                    elif cvpj_audiomod['stretch_algorithm'] == 'elastique_v3_mono': T_Main['stretchingmode'] = 2
                    elif cvpj_audiomod['stretch_algorithm'] == 'slice_stretch': T_Main['stretchingmode'] = 3
                    elif cvpj_audiomod['stretch_algorithm'] == 'auto': T_Main['stretchingmode'] = 4
                    elif cvpj_audiomod['stretch_algorithm'] == 'slice_map': T_Main['stretchingmode'] = 5
                    elif cvpj_audiomod['stretch_algorithm'] == 'elastique_v2': T_Main['stretchingmode'] = 6
                    elif cvpj_audiomod['stretch_algorithm'] == 'elastique_v2_transient': T_Main['stretchingmode'] = 7
                    elif cvpj_audiomod['stretch_algorithm'] == 'elastique_v2_mono': T_Main['stretchingmode'] = 8
                    elif cvpj_audiomod['stretch_algorithm'] == 'elastique_v2_speech': T_Main['stretchingmode'] = 9
                    else: T_Main['stretchingmode'] = -1
                else: T_Main['stretchingmode'] = -1

                if 'pitch' in cvpj_audiomod: T_Main['stretchingpitch'] = int(cvpj_audiomod['pitch']*100)

                if 'stretch_data' in cvpj_audiomod:
                    timedata = cvpj_audiomod['stretch_data']

                    if cvpj_audiomod['stretch_method'] == 'rate_tempo':
                        audiorate = timedata['rate']
                        samplestretch[CVPJ_Entry] = ['rate_tempo', audiorate]
                        T_Main['stretchingtime'] = int(  (audioinfo['dur_sec']*384)/audiorate     )

                    if cvpj_audiomod['stretch_method'] == 'rate_ignoretempo':
                        audiorate = timedata['rate']
                        samplestretch[CVPJ_Entry] = ['rate_ignoretempo', audiorate]
                        T_Main['stretchingtime'] = int(  ((audioinfo['dur_sec']*384)/audiorate)/tempomul     )

                    if cvpj_audiomod['stretch_method'] == 'rate_speed':
                        audiorate = timedata['rate']
                        samplestretch[CVPJ_Entry] = ['rate_speed', audiorate]
                        T_Main['stretchingmultiplier'] = int(  math.log2(1/audiorate)*10000  )

                else:
                    samplestretch[CVPJ_Entry] = ['normal', 1]

            else:
                samplestretch[CVPJ_Entry] = ['normal', 1]

            FL_Channels[inst_id[CVPJ_Entry]] = T_Main



        pat_id = {}
        pat_id_count = 1
        patternssorder = []

        for CVPJ_NotelistEntry in CVPJ_NotelistIndex:
            pat_id[CVPJ_NotelistEntry] = pat_id_count
            pat_id_count += 1
        #print(pat_id)

        for pat_entry in pat_id:
            FL_Patterns[str(pat_id[pat_entry])] = {}
            FL_Pattern = FL_Patterns[str(pat_id[pat_entry])]
            T_Pattern = CVPJ_NotelistIndex[pat_entry]
            if 'color' in T_Pattern: FL_Pattern['color'] = decode_color(T_Pattern['color'])
            if 'name' in T_Pattern: FL_Pattern['name'] = T_Pattern['name']
            if 'notelist' in T_Pattern:
                T_Notelist = notelist_data.sort(T_Pattern['notelist'])
                FL_Pattern['notes'] = []
                slidenotes = []
                for note in T_Notelist:
                    if note['instrument'] in inst_id:
                        #print(note)
                        FL_Note = {}
                        FL_Note['rack'] = int(inst_id[note['instrument']])
                        M_FL_Note_Key = int(note['key'])+60
                        M_FL_Note_Pos = int((note['position']*ppq)/4)
                        M_FL_Note_Dur = int((note['duration']*ppq)/4)
                        if 'finepitch' in note: FL_Note['finep'] = int((note['finepitch']/10)+120)
                        if 'release' in note: FL_Note['rel'] = int(xtramath.clamp(note['release'],0,1)*128)
                        if 'vol' in note: FL_Note['velocity'] = int(xtramath.clamp(note['vol'],0,1)*100)
                        if 'cutoff' in note: FL_Note['mod_x'] = int(xtramath.clamp(note['cutoff'],0,1)*255)
                        if 'reso' in note: FL_Note['mod_y'] = int(xtramath.clamp(note['reso'],0,1)*255)
                        if 'pan' in note: FL_Note['pan'] = int((xtramath.clamp(float(note['pan']),-1,1)*64)+64)
                        FL_Note['pos'] = M_FL_Note_Pos
                        FL_Note['dur'] = M_FL_Note_Dur
                        FL_Note['key'] = M_FL_Note_Key
                        FL_Pattern['notes'].append(FL_Note)

                        if 'notemod' in note: 
                            note_mod.notemod_conv(note)
                            if 'slide' in note['notemod']: 
                                for slidenote in note['notemod']['slide']:
                                    FL_Note = {}
                                    FL_Note['rack'] = int(inst_id[note['instrument']])
                                    FL_Note['key'] = int(slidenote['key'] + note['key'])+60
                                    FL_Note['pos'] = M_FL_Note_Pos + int((slidenote['position']*ppq)/4)
                                    FL_Note['dur'] = int((slidenote['duration']*ppq)/4)
                                    FL_Note['flags'] = 16392
                                    if 'finepitch' in slidenote: FL_Note['finep'] = int((slidenote['finepitch']/10)+120)
                                    if 'release' in slidenote: FL_Note['rel'] = int(xtramath.clamp(slidenote['release'],0,1)*128)
                                    if 'vol' in slidenote: FL_Note['velocity'] = int(xtramath.clamp(slidenote['vol'],0,1)*100)
                                    elif 'vol' in note: FL_Note['velocity'] = int(xtramath.clamp(note['vol'],0,1)*100)
                                    if 'cutoff' in slidenote: FL_Note['mod_x'] = int(xtramath.clamp(slidenote['cutoff'],0,1)*255)
                                    if 'reso' in slidenote: FL_Note['mod_y'] = int(xtramath.clamp(slidenote['reso'],0,1)*255)
                                    if 'pan' in slidenote: FL_Note['pan'] = int((xtramath.clamp(float(slidenote['pan']),-1,1)*64)+64)
                                    FL_Pattern['notes'].append(FL_Note)
                            

        if len(FL_Patterns) > 999:
            print('[error] FLP patterns over 999 is unsupported.')
            exit()

        if len(FL_Channels) > 256:
            print('[error] FLP channels over 256 is unsupported.')
            exit()

        FL_Playlist_BeforeSort = {}
        FL_Playlist_Sorted = {}
        FL_Playlist = []
        for CVPJ_playlistrow in CVPJ_playlist:
            CVPJ_playlistitem = CVPJ_playlist[CVPJ_playlistrow]


            if 'placements_notes' in CVPJ_playlistitem:
                for CVPJ_Placement in CVPJ_playlistitem['placements_notes']:
                    if CVPJ_Placement['fromindex'] in pat_id:
                        FL_playlistitem = {}
                        FL_playlistitem['position'] = int((CVPJ_Placement['position']*ppq)/4)
                        FL_playlistitem['patternbase'] = 20480
                        FL_playlistitem['itemindex'] = int(pat_id[CVPJ_Placement['fromindex']] + FL_playlistitem['patternbase'])
                        if 'duration' in CVPJ_Placement:
                            FL_playlistitem['length'] = int((CVPJ_Placement['duration']*ppq)/4)
                            if CVPJ_Placement != 0:
                                FL_playlistitem['startoffset'] = 0
                                FL_playlistitem['endoffset'] = int((CVPJ_Placement['duration']*ppq)/4)
                        else:
                            FL_playlistitem['length'] = notelist_data.getduration(CVPJ_NotelistIndex[CVPJ_Placement['fromindex']]['notelist'])
                        FL_playlistitem['unknown1'] = 120
                        FL_playlistitem['unknown2'] = 25664
                        FL_playlistitem['unknown3'] = 32896
                        FL_playlistitem['flags'] = 64
                        FL_playlistitem['trackindex'] = (-500 + int(CVPJ_playlistrow))*-1
                        if 'muted' in CVPJ_Placement:
                            if CVPJ_Placement['muted'] == True:
                                FL_playlistitem['flags'] = 12352
                        if 'cut' in CVPJ_Placement:
                            if 'type' in CVPJ_Placement['cut']:
                                if CVPJ_Placement['cut']['type'] == 'cut':
                                    if 'start' in CVPJ_Placement['cut']: FL_playlistitem['startoffset'] = int((CVPJ_Placement['cut']['start']*ppq)/4)
                                    if 'end' in CVPJ_Placement['cut']: FL_playlistitem['endoffset'] = int((CVPJ_Placement['cut']['end']*ppq)/4)
                        if FL_playlistitem['position'] not in FL_Playlist_BeforeSort:
                            FL_Playlist_BeforeSort[FL_playlistitem['position']] = []
                        FL_Playlist_BeforeSort[FL_playlistitem['position']].append(FL_playlistitem)


            if 'placements_audio' in CVPJ_playlistitem:
                for CVPJ_Placement in CVPJ_playlistitem['placements_audio']:
                    if CVPJ_Placement['fromindex'] in samples_id:

                        if CVPJ_Placement['fromindex'] in samplestretch:
                            pl_stretch = samplestretch[CVPJ_Placement['fromindex']]
                        else: pl_stretch = [None, 1]

                        sampleid = samples_id[CVPJ_Placement['fromindex']]
                        FL_playlistitem = {}
                        FL_playlistitem['position'] = int((CVPJ_Placement['position']*ppq)/4)
                        FL_playlistitem['patternbase'] = 20480
                        FL_playlistitem['itemindex'] = sampleid
                        FL_playlistitem['length'] = int((CVPJ_Placement['duration']*ppq)/4)

                        FL_playlistitem['unknown1'] = 120
                        FL_playlistitem['unknown2'] = 25664
                        FL_playlistitem['unknown3'] = 32896
                        FL_playlistitem['flags'] = 64
                        FL_playlistitem['trackindex'] = (-500 + int(CVPJ_playlistrow))*-1
                        if 'muted' in CVPJ_Placement:
                            if CVPJ_Placement['muted'] == True:
                                FL_playlistitem['flags'] = 12352

                        if 'cut' in CVPJ_Placement:
                            if 'type' in CVPJ_Placement['cut']:
                                cutdata = CVPJ_Placement['cut']
                                if cutdata['type'] == 'cut':
                                    if pl_stretch[0] == 'rate_tempo':
                                        if 'start' in cutdata: 
                                            FL_playlistitem['startoffset'] = cutdata['start']*pl_stretch[1]
                                            FL_playlistitem['endoffset'] = CVPJ_Placement['duration']*pl_stretch[1] + FL_playlistitem['startoffset']
                                    elif pl_stretch[0] == 'rate_ignoretempo':
                                        if 'start' in cutdata: 
                                            FL_playlistitem['startoffset'] = cutdata['start']*tempomul
                                            FL_playlistitem['endoffset'] = CVPJ_Placement['duration']*tempomul + FL_playlistitem['startoffset']
                                    elif pl_stretch[0] == 'rate_speed':
                                        if 'start' in cutdata: 
                                            FL_playlistitem['startoffset'] = (cutdata['start']*tempomul)*pl_stretch[1]
                                            FL_playlistitem['endoffset'] = (CVPJ_Placement['duration']*tempomul)*pl_stretch[1] + FL_playlistitem['startoffset']
                                    else:
                                        if 'start' in cutdata: 
                                            FL_playlistitem['startoffset'] = cutdata['start']
                                            FL_playlistitem['endoffset'] = cutdata['start']+FL_playlistitem['length']

                        #for value in ['startoffset', 'endoffset']:
                        #    outprint = None
                        #    if value in FL_playlistitem: outprint = round(FL_playlistitem[value], 6)
                        #    print(str(outprint).ljust(13), end=' ')
                        #print(pl_stretch)

                        if FL_playlistitem['position'] not in FL_Playlist_BeforeSort:
                            FL_Playlist_BeforeSort[FL_playlistitem['position']] = []
                        FL_Playlist_BeforeSort[FL_playlistitem['position']].append(FL_playlistitem)


            if str(CVPJ_playlistrow) not in FL_Tracks:
                FL_Tracks[str(CVPJ_playlistrow)] = {}
            if 'color' in CVPJ_playlistitem:
                FL_Tracks[str(CVPJ_playlistrow)]['color'] = decode_color(CVPJ_playlistitem['color'])
            if 'name' in CVPJ_playlistitem:
                FL_Tracks[str(CVPJ_playlistrow)]['name'] = CVPJ_playlistitem['name']
            if 'size' in CVPJ_playlistitem:
                FL_Tracks[str(CVPJ_playlistrow)]['height'] = CVPJ_playlistitem['size']
            if 'enabled' in CVPJ_playlistitem:
                FL_Tracks[str(CVPJ_playlistrow)]['enabled'] = CVPJ_playlistitem['enabled']
        FL_Playlist_Sorted = dict(sorted(FL_Playlist_BeforeSort.items(), key=lambda item: item[0]))

        for itemposition in FL_Playlist_Sorted:
            playlistposvalues = FL_Playlist_Sorted[itemposition]
            for itemrow in playlistposvalues:
                FL_Playlist.append(itemrow)

        if 'timemarkers' in cvpj_l:
            CVPJ_TimeMarkers = cvpj_l['timemarkers']
            markernum = 0
            for timemarker in CVPJ_TimeMarkers:
                markernum += 1
                FL_TimeMarker = {}
                if 'name' in timemarker: FL_TimeMarker['name'] = timemarker['name']
                else: FL_TimeMarker['name'] = ""
                FL_TimeMarker['pos'] = int((timemarker['position']*ppq)/4)
                if 'type' in timemarker:
                    if timemarker['type'] == 'start': FL_TimeMarker['type'] = 5
                    elif timemarker['type'] == 'loop': FL_TimeMarker['type'] = 4
                    elif timemarker['type'] == 'loop_area': 
                        FL_TimeMarkers[str(markernum)] = {'name': "", 'type':2, 'pos':int((timemarker['end']*ppq)/4)}
                        FL_TimeMarker['type'] = 1
                        markernum += 1
                    elif timemarker['type'] == 'markerloop': FL_TimeMarker['type'] = 1
                    elif timemarker['type'] == 'markerskip': FL_TimeMarker['type'] = 2
                    elif timemarker['type'] == 'pause': FL_TimeMarker['type'] = 3
                    elif timemarker['type'] == 'timesig': 
                        FL_TimeMarker['type'] = 8
                        FL_TimeMarker['numerator'] = timemarker['numerator']
                        FL_TimeMarker['denominator'] = timemarker['denominator']
                    elif timemarker['type'] == 'punchin': FL_TimeMarker['type'] = 9
                    elif timemarker['type'] == 'punchout': FL_TimeMarker['type'] = 10
                    else: FL_TimeMarker['type'] = 0
                else: FL_TimeMarker['type'] = 0
                FL_TimeMarkers[str(markernum)] = FL_TimeMarker

        if 'fxrack' in cvpj_l:
            for cvpj_fx in cvpj_l['fxrack']:
                cvpj_fxdata = cvpj_l['fxrack'][cvpj_fx]
                FL_Mixer[cvpj_fx] = {}
                if 'name' in cvpj_fxdata:
                    FL_Mixer[cvpj_fx]['name'] = cvpj_fxdata['name']
                if 'color' in cvpj_fxdata:
                    FL_Mixer[cvpj_fx]['color'] = decode_color(cvpj_fxdata['color'])

                if 'chain_fx_audio' in cvpj_fxdata:
                    slotnum = 0
                    FL_Mixer[cvpj_fx]['slots'] = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}

                    for pluginid in cvpj_fxdata['chain_fx_audio']:

                        fl_plugin, fl_pluginparams = flp_enc_plugins.setparams(cvpj_l, pluginid)
                        if fl_plugin != None:
                            FL_Mixer[cvpj_fx]['slots'][slotnum] = {}
                            slotdata = FL_Mixer[cvpj_fx]['slots'][slotnum]
                            slotdata['plugin'] = fl_plugin
                            slotdata['pluginparams'] = fl_pluginparams
                            fx_name, fx_color = plugins.get_plug_fxvisual(cvpj_l, fl_plugin)

                            if fx_name: slotdata['name'] = fx_name
                            if fx_color: slotdata['color'] = decode_color(fx_color)


                        slotnum += 1
                        if slotnum == 10: break

        FL_Arrangements['0'] = {}
        FL_Arrangements['0']['items'] = FL_Playlist
        FL_Arrangements['0']['name'] = 'Arrangement'
        FL_Arrangements['0']['tracks'] = FL_Tracks
        FL_Arrangements['0']['timemarkers'] = FL_TimeMarkers

            

        format_flp_enc.make(FLP_Data, output_file)