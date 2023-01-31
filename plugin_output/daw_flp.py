# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later  

import plugin_output
import json
import math
import base64
import struct
from bs4 import BeautifulSoup
from functions import format_flp_enc
from functions import song_convert
from functions import note_mod

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def decode_color(color):
    return int.from_bytes(bytes([int(color[0]*255), int(color[1]*255), int(color[2]*255)]), "little")

class output_cvpjs(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getshortname(self): return 'flp'
    def getname(self): return 'FL Studio'
    def gettype(self): return 'mi'
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)

        song_convert.trackfx2fxrack(projJ, 'm')

        FLP_Data = {}

        FLP_Data['FL_Main'] = {}
        FL_Main = FLP_Data['FL_Main']

        FLP_Data['FL_Channels'] = {}
        FL_Channels = FLP_Data['FL_Channels']
        CVPJ_Instruments = projJ['instruments']

        FLP_Data['FL_Patterns'] = {}
        FL_Patterns = FLP_Data['FL_Patterns']
        CVPJ_NotelistIndex = projJ['notelistindex']

        FLP_Data['FL_Arrangements'] = {}
        FL_Arrangements = FLP_Data['FL_Arrangements']

        FLP_Data['FL_TimeMarkers'] = {}
        FL_TimeMarkers = FLP_Data['FL_TimeMarkers']

        FLP_Data['FL_Tracks'] = {}
        FL_Tracks = FLP_Data['FL_Tracks']
        CVPJ_playlist = projJ['playlist']

        FLP_Data['FL_Mixer'] = {}
        FL_Mixer = FLP_Data['FL_Mixer']

        FLP_Data['FL_FilterGroups'] = []
        FL_FilterGroups = FLP_Data['FL_FilterGroups']


        ppq = 960
        FL_Main['ppq'] = ppq
        
        FL_Main['ShowInfo'] = 0

        if 'info' in projJ: 
            infoJ = projJ['info']
            FL_Main['ShowInfo'] = 1
            if 'title' in infoJ: 
                if 'title' != '': FL_Main['Title'] = infoJ['title']
            else: FL_Main['Title'] = ''

            if 'author' in infoJ: 
                if 'author' != '':  FL_Main['Author'] = infoJ['author']
            else: FL_Main['Author'] = ''

            if 'url' in infoJ: 
                if 'url' != '':  FL_Main['URL'] = infoJ['url']
            else: FL_Main['URL'] = ''

            if 'genre' in infoJ: 
                if 'genre' != '':  FL_Main['Genre'] = infoJ['genre']
            else: FL_Main['Genre'] = ''

            if 'message' in infoJ: 
                if infoJ['message']['type'] == 'html':
                    bst = BeautifulSoup(infoJ['message']['text'], "html.parser")
                    FL_Main['Comment'] = bst.get_text().replace("\n", "\r")
                if infoJ['message']['type'] == 'text':
                    FL_Main['Comment'] = infoJ['message']['text'].replace("\n", "\r")
            else: 
                FL_Main['Comment'] = ''
        else: 
            FL_Main['Title'] = ''
            FL_Main['Author'] = ''
            FL_Main['Genre'] = ''
            FL_Main['Comment'] = ''

        filtergroups_id_count = 0
        filtergroups_id = {}

        #print(FL_FilterGroups)

        #if 'filtergroups' in projJ:
        #    for filtergroup in projJ['filtergroups']:
        #        filtergroups_id[filtergroup] = filtergroups_id_count
        #        if 'name' in projJ['filtergroups'][filtergroup]:
        #            FL_FilterGroups.append(projJ['filtergroups'][filtergroup]['name'])
        #        else:
        #            FL_FilterGroups.append('noname')
        #        filtergroups_id_count += 1
        
        FL_Main['ProjectDataPath'] = ''

        if 'shuffle' in projJ: FL_Main['Shuffle'] = int(projJ['shuffle']*128)
        else: FL_Main['Shuffle'] = 0
        if 'timesig_numerator' in projJ: FL_Main['Numerator'] = projJ['timesig_numerator']
        if 'timesig_denominator' in projJ: FL_Main['Denominator'] = projJ['timesig_denominator']
        if 'bpm' in projJ: FL_Main['Tempo'] = projJ['bpm']
        if 'pitch' in projJ: FL_Main['MainPitch'] = struct.unpack('H', struct.pack('h', int(projJ['pitch'])))[0]

        instrumentsorder = projJ['instrumentsorder']

        inst_id = {}
        inst_id_count = 0
        for instentry in instrumentsorder:
            inst_id[instentry] = str(inst_id_count)
            inst_id_count += 1

        for CVPJ_Entry in CVPJ_Instruments:
            T_Main = {}
            CVPJ_Data = CVPJ_Instruments[CVPJ_Entry]
            if 'vol' in CVPJ_Data: T_Main['volume'] = CVPJ_Data['vol']
            if 'pan' in CVPJ_Data: T_Main['pan'] = CVPJ_Data['pan']
            if 'name' in CVPJ_Data: T_Main['name'] = CVPJ_Data['name']
            if 'enabled' in CVPJ_Data: T_Main['enabled'] = CVPJ_Data['enabled']
            if 'chain_fx_audio' in CVPJ_Data: T_Main['fxchannel'] = CVPJ_Data['chain_fx_audio']
            if 'filtergroup' in CVPJ_Data:
                if CVPJ_Data['filtergroup'] in filtergroups_id:
                    T_Main['filtergroup'] = filtergroups_id[CVPJ_Data['filtergroup']]

            if 'instdata' in CVPJ_Data:
                CVPJ_Inst = CVPJ_Data['instdata']
                if 'notefx' in CVPJ_Inst:
                    if 'pitch' in CVPJ_Inst['notefx']:
                        if 'semitones' in CVPJ_Inst['notefx']['pitch']: 
                            T_Main['middlenote'] = CVPJ_Inst['notefx']['pitch']['semitones']+60
                if 'pitch' in CVPJ_Inst: T_Main['pitch'] = CVPJ_Inst['pitch']
                if 'usemasterpitch' in CVPJ_Inst: T_Main['main_pitch'] = CVPJ_Inst['usemasterpitch']
            if 'poly' in CVPJ_Data: 
                if 'max' in CVPJ_Data['poly']: 
                    T_Main['polymax'] = CVPJ_Data['poly']['max']
            if 'color' in CVPJ_Data: 
                T_Main['color'] = decode_color(CVPJ_Data['color'])

            #print(CVPJ_Inst['plugin'])
            #if CVPJ_Inst['plugin'] == 'native-fl':
            #    T_Main['type'] = 2
            #    flnativedata = CVPJ_Inst['plugindata'] 
            #    T_Main['plugin'] = flnativedata['name']
            #    pdata = flnativedata['data'].encode('ascii')
            #    pdataxs = base64.b64decode(pdata)
            #    T_Main['pluginparams'] = pdataxs
            #    T_Main['plugindata'] = b'\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00&\x00\x00\x00z\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            if CVPJ_Inst['plugin'] == 'sampler':
                T_Main['type'] = 0
                T_Main['plugin'] = ''
                if 'plugindata' in CVPJ_Inst:
                    samplerdata = CVPJ_Inst['plugindata'] 
                    if 'file' in samplerdata: T_Main['samplefilename'] = samplerdata['file'] 
            else:
                T_Main['type'] = 0
                T_Main['plugin'] = ''

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
                T_Notelist = note_mod.sortnotes(T_Pattern['notelist'])
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
                        if 'release' in note: FL_Note['rel'] = int(clamp(note['release'],0,1)*128)
                        if 'vol' in note: FL_Note['velocity'] = int(clamp(note['vol'],0,1)*100)
                        if 'cutoff' in note: FL_Note['mod_x'] = int(clamp(note['cutoff'],0,1)*255)
                        if 'reso' in note: FL_Note['mod_y'] = int(clamp(note['reso'],0,1)*255)
                        if 'pan' in note: FL_Note['pan'] = int((clamp(float(note['pan']),-1,1)*64)+64)
                        FL_Note['pos'] = M_FL_Note_Pos
                        FL_Note['dur'] = M_FL_Note_Dur
                        FL_Note['key'] = M_FL_Note_Key
                        FL_Pattern['notes'].append(FL_Note)
                        if 'notemod' in note: 
                            if 'slide' in note['notemod']: 
                                for slidenote in note['notemod']['slide']:
                                    FL_Note = {}
                                    FL_Note['rack'] = int(inst_id[note['instrument']])
                                    FL_Note['key'] = int(slidenote['key'] + note['key'])+60
                                    FL_Note['pos'] = M_FL_Note_Pos + int((slidenote['position']*ppq)/4)
                                    FL_Note['dur'] = int((slidenote['duration']*ppq)/4)
                                    FL_Note['flags'] = 16392
                                    if 'finepitch' in slidenote: FL_Note['finep'] = int((slidenote['finepitch']/10)+120)
                                    if 'release' in slidenote: FL_Note['rel'] = int(clamp(slidenote['release'],0,1)*128)
                                    if 'vol' in slidenote: FL_Note['velocity'] = int(clamp(slidenote['vol'],0,1)*100)
                                    if 'cutoff' in slidenote: FL_Note['mod_x'] = int(clamp(slidenote['cutoff'],0,1)*255)
                                    if 'reso' in slidenote: FL_Note['mod_y'] = int(clamp(slidenote['reso'],0,1)*255)
                                    if 'pan' in slidenote: FL_Note['pan'] = int((clamp(float(slidenote['pan']),-1,1)*64)+64)
                                    FL_Pattern['notes'].append(FL_Note)
                            note_mod.notemod_conv(note['notemod'])

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
            #print(CVPJ_playlistrow, CVPJ_playlist[CVPJ_playlistrow])
            if 'placements' in CVPJ_playlistitem:
                #print(CVPJ_playlist[CVPJ_playlistrow])
                for CVPJ_Placement in CVPJ_playlistitem['placements']:
                    if CVPJ_Placement['fromindex'] in pat_id:
                        FL_playlistitem = {}
                        FL_playlistitem['position'] = int((CVPJ_Placement['position']*ppq)/4)
                        FL_playlistitem['patternbase'] = 20480
                        FL_playlistitem['itemindex'] = int(pat_id[CVPJ_Placement['fromindex']] + FL_playlistitem['patternbase'])
                        if 'duration' in CVPJ_Placement:
                            FL_playlistitem['length'] = int((CVPJ_Placement['duration']*ppq)/4)
                        else:
                            FL_playlistitem['length'] = note_mod.getduration(CVPJ_NotelistIndex[CVPJ_Placement['fromindex']]['notelist'])
                        FL_playlistitem['unknown1'] = 120
                        FL_playlistitem['unknown2'] = 25664
                        FL_playlistitem['unknown3'] = 32896
                        FL_playlistitem['flags'] = 4
                        FL_playlistitem['trackindex'] = (-500 + int(CVPJ_playlistrow))*-1
                        if 'cut' in CVPJ_Placement:
                            if 'type' in CVPJ_Placement['cut']:
                                if CVPJ_Placement['cut']['type'] == 'cut':
                                    if 'start' in CVPJ_Placement['cut']:
                                        FL_playlistitem['startoffset'] = int((CVPJ_Placement['cut']['start']*ppq)/4)
                                    if 'end' in CVPJ_Placement['cut']:
                                        FL_playlistitem['endoffset'] = int((CVPJ_Placement['cut']['end']*ppq)/4)
                            FL_playlistitem['flags'] = 64
                        if FL_playlistitem['position'] not in FL_Playlist_BeforeSort:
                            FL_Playlist_BeforeSort[FL_playlistitem['position']] = []
                        FL_Playlist_BeforeSort[FL_playlistitem['position']].append(FL_playlistitem)
            if 'color' in CVPJ_playlistitem:
                if str(CVPJ_playlistrow) not in FL_Tracks:
                    FL_Tracks[str(CVPJ_playlistrow)] = {}
                FL_Tracks[str(CVPJ_playlistrow)]['color'] = decode_color(CVPJ_playlistitem['color'])
            if 'name' in CVPJ_playlistitem:
                if str(CVPJ_playlistrow) not in FL_Tracks:
                    FL_Tracks[str(CVPJ_playlistrow)] = {}
                FL_Tracks[str(CVPJ_playlistrow)]['name'] = CVPJ_playlistitem['name']

        FL_Playlist_Sorted = dict(sorted(FL_Playlist_BeforeSort.items(), key=lambda item: item[0]))

        for itemposition in FL_Playlist_Sorted:
            playlistposvalues = FL_Playlist_Sorted[itemposition]
            for itemrow in playlistposvalues:
                FL_Playlist.append(itemrow)

        if 'timemarkers' in projJ:
            CVPJ_TimeMarkers = projJ['timemarkers']
            markernum = 0
            for timemarker in CVPJ_TimeMarkers:
                markernum += 1
                FL_TimeMarker = {}
                FL_TimeMarker['name'] = timemarker['name']
                FL_TimeMarker['pos'] = int((timemarker['position']*ppq)/4)
                if 'type' in timemarker:
                    if timemarker['type'] == 'start': FL_TimeMarker['type'] = 5
                    elif timemarker['type'] == 'loop': FL_TimeMarker['type'] = 4
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
                FL_TimeMarkers[str(markernum)] = FL_TimeMarker

        if 'fxrack' in projJ:
            for cvpj_fx in projJ['fxrack']:
                cvpj_fxdata = projJ['fxrack'][cvpj_fx]
                FL_Mixer[cvpj_fx] = {}
                if 'name' in cvpj_fxdata:
                    FL_Mixer[cvpj_fx]['name'] = cvpj_fxdata['name']
                if 'color' in cvpj_fxdata:
                    FL_Mixer[cvpj_fx]['color'] = decode_color(cvpj_fxdata['color'])

        FL_Arrangements['0'] = {}
        FL_Arrangements['0']['items'] = FL_Playlist
        FL_Arrangements['0']['name'] = 'Arrangement'
        FL_Arrangements['0']['tracks'] = FL_Tracks
        FL_Arrangements['0']['timemarkers'] = FL_TimeMarkers

            

        format_flp_enc.make(FLP_Data, output_file)