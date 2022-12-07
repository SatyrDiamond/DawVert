# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import os.path
from functions import placements

#               Name,              Type, FadeIn, FadeOut, PitchMod, Slide, Vib, Color
lc_instlist = {}
lc_instlist[ 2] = ['Square Wave'     ,'Square'    ,0  ,0  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[ 1] = ['Triangle Wave'   ,'Triangle'  ,0  ,0  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[ 0] = ['Pulse Wave'      ,'Pulse25'   ,0  ,0  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[16] = ['SawTooth Wave'   ,'Saw'       ,0  ,0  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[20] = ['Sine Wave'       ,'Sine'      ,0  ,0  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[ 3] = ['Noise'           ,'Noise'     ,0  ,0  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[ 4] = ['Piano Like'      ,'Pulse25'   ,0  ,1  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[17] = ['Synth Piano'     ,'Saw'       ,0  ,1  ,0  ,False ,False ,[0.22, 0.36, 0.60]]
lc_instlist[ 5] = ['Xylophone Like'  ,'Triangle'  ,0  ,1  ,0  ,False ,False ,[0.83, 0.52, 0.25]]
lc_instlist[ 6] = ['Ice'             ,'Square'    ,0  ,1  ,0  ,False ,False ,[0.66, 0.76, 1.00]]
lc_instlist[21] = ['Orgel Like'      ,'Sine'      ,0  ,1  ,0  ,False ,False ,[0.91, 0.76, 0.36]]
lc_instlist[ 7] = ['Drum Like'       ,'Drum'      ,0  ,1  ,0  ,False ,False ,[0.64, 0.64, 0.64]]
lc_instlist[ 8] = ['Strings Like'    ,'Pulse25'   ,0  ,0  ,0  ,False ,True  ,[0.83, 0.52, 0.25]]
lc_instlist[ 9] = ['Vocal Like'      ,'Triangle'  ,0  ,0  ,0  ,False ,True  ,[0.49, 0.13, 0.45]]
lc_instlist[10] = ['UFO'             ,'Square'    ,0  ,0  ,0  ,False ,True  ,[0.64, 0.64, 0.64]]
lc_instlist[18] = ['Brass Like'      ,'Saw'       ,0  ,0  ,0  ,False ,True  ,[0.91, 0.76, 0.36]]
lc_instlist[22] = ['Ghost'           ,'Sine'      ,0  ,0  ,0  ,False ,True  ,[0.93, 0.93, 0.93]]

lc_instlist[14] = ['Glide Square'    ,'Square'    ,0  ,0  ,0  ,True  ,False ,[0.17, 0.20, 0.37]]
lc_instlist[13] = ['Glide Triangle'  ,'Triangle'  ,0  ,0  ,0  ,True  ,False ,[0.17, 0.20, 0.37]]
lc_instlist[12] = ['Glide Pulse'     ,'Pulse25'   ,0  ,0  ,0  ,True  ,False ,[0.17, 0.20, 0.37]]
lc_instlist[19] = ['Glide SawTooth'  ,'Saw'       ,0  ,0  ,0  ,True  ,False ,[0.17, 0.20, 0.37]]
lc_instlist[23] = ['Glide Sine'      ,'Sine'      ,0  ,0  ,0  ,True  ,False ,[0.17, 0.20, 0.37]]
lc_instlist[15] = ['Glide Noise'     ,'Noise'     ,0  ,0  ,0  ,True  ,False ,[0.17, 0.20, 0.37]]
lc_instlist[24] = ['Fish'            ,'Noise'     ,1  ,0  ,0  ,False ,False ,[0.22, 0.36, 0.60]]
lc_instlist[25] = ['Flute Like'      ,'Triangle'  ,1  ,0  ,0  ,False ,False ,[0.44, 0.78, 0.66]]
lc_instlist[26] = ['Slow String Like','Pulse25'   ,1  ,0  ,0  ,False ,False ,[0.83, 0.52, 0.25]]
lc_instlist[27] = ['Saxophone Like'  ,'Saw'       ,1  ,0  ,0  ,False ,False ,[0.91, 0.76, 0.36]]
lc_instlist[28] = ['Ocarina Like'    ,'Sine'      ,1  ,0  ,0  ,False ,False ,[0.66, 0.76, 1.00]]
lc_instlist[29] = ['Seashore Like'   ,'Noise'     ,1  ,0  ,0  ,False ,False ,[0.22, 0.36, 0.60]]
lc_instlist[30] = ['Stomp'           ,'Stomp'     ,0  ,1  ,-1 ,False ,False ,[0.83, 0.09, 0.42]]
lc_instlist[31] = ['Twin Stomp'      ,'Stomp'     ,0  ,1  ,-1 ,False ,False ,[0.83, 0.09, 0.42]]
lc_instlist[32] = ['Twin Drum'       ,'Drum'      ,0  ,2  ,0  ,False ,False ,[0.64, 0.64, 0.64]]
lc_instlist[33] = ['Punch'           ,'Punch'     ,0  ,1  ,1  ,False ,False ,[0.99, 0.88, 0.80]]
lc_instlist[34] = ['Orchestra Hit'   ,'OrchHit'   ,0  ,0  ,0  ,False ,False ,[0.00, 0.00, 0.00]]

lc_instlist[35] = ['Short Freq Noise','FreqNoise' ,0  ,0  ,0  ,False ,False ,[0.93, 0.93, 0.93]]
lc_instlist[36] = ['Hammer'          ,'FreqNoise' ,0  ,1  ,0  ,False ,False ,[0.35, 0.35, 0.35]]
lc_instlist[37] = ['Robot'           ,'FreqNoise' ,1  ,0  ,0  ,False ,False ,[0.64, 0.64, 0.64]]
lc_instlist[38] =['Glide S-Freq Noise','FreqNoise',0  ,0  ,0  ,False ,True  ,[0.17, 0.20, 0.37]]
lc_instlist[39] = ['12.5% Pulse'     ,'Pulse125'  ,0  ,0  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[46] = ['Pulse Brass'     ,'Pulse125'  ,0  ,0  ,0  ,False ,True  ,[0.78, 0.78, 0.78]]
lc_instlist[40] = ['Lo-Fi Piano'     ,'Pulse125'  ,0  ,1  ,0  ,False ,False ,[0.66, 0.76, 1.00]]
lc_instlist[41] = ['Fiddle'          ,'Pulse125'  ,1  ,0  ,0  ,False ,False ,[0.83, 0.52, 0.25]]
lc_instlist[42] = ['Glide 12.5% Pulse','Pulse125' ,0  ,0  ,0  ,True  ,False ,[0.17, 0.20, 0.37]]
lc_instlist[43] = ['Dog'             ,'Dog'       ,0  ,0  ,-1 ,False ,False ,[0.91, 0.76, 0.36]]
lc_instlist[45] = ['Robo Stomp'      ,'RoboStomp' ,0  ,0  ,-1 ,False ,False ,[0.35, 0.35, 0.35]]
lc_instlist[47] =['Low-Reso Triangle','LowResoTri',0  ,0  ,0  ,False ,False ,[0.17, 0.20, 0.37]]
lc_instlist[48] =['Low-Reso Xylophone','LowResoTri',0 ,1  ,0  ,False ,False ,[0.83, 0.52, 0.25]]
lc_instlist[49] = ['Low-Reso Vocal'  ,'LowResoTri',0  ,0  ,0  ,False ,True , [0.99, 0.88, 0.80]]
lc_instlist[50] = ['Glide L-Triangle','LowResoTri',0  ,0  ,0  ,True  ,False ,[0.17, 0.20, 0.37]]
lc_instlist[50] = ['Low-Reso Flute'  ,'LowResoTri',1  ,0  ,0  ,True  ,False ,[0.44, 0.78, 0.66]]

used_instruments = []

def lc_parse_voice(sl_json, length, partnum):
    global used_instruments
    notelist = []
    previnst = None
    position = 0
    for notenum in range(length):
        lc_notedata = sl_json[notenum]
        lc_inst = lc_notedata['id']
        if lc_inst != None:
            lc_note_p = lc_notedata['n']
            if lc_note_p != None:
                lc_note = lc_note_p-60
                notelist.append({'position': position, 'key': lc_note, 'instrument': lc_instlist[lc_inst][1]+'_'+str(partnum), 'duration': 1, 'vol': lc_notedata['x']/15})
                if lc_instlist[lc_inst][1]+'_'+str(partnum) not in used_instruments:
                    used_instruments.append(lc_instlist[lc_inst][1]+'_'+str(partnum))
        position += 1
    return notelist

def lc_parse_placements(sl_json, partnum):
    global patternpos
    global patternlen
    patternpos = []
    patternlen = []
    placements = []
    position = 0
    for sle in sl_json:
        length = sle['play_notes']
        lc_notes = sle['vl']
        placement = {}
        placement['type'] = 'instruments'
        placement['duration'] = length
        notelist = lc_parse_voice(lc_notes, length, partnum)
        placement['notelist'] = notelist
        placement['position'] = position
        if notelist != []:
            placements.append(placement)
        patternpos.append(position)
        patternlen.append(length)
        position += length
    return placements

class input_lc(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'lovelycomposer'
    def getname(self): return 'Lovely Composer'
    def gettype(self): return 'm'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        lc_f_stream = open(input_file, 'r')
        lc_f_lines = lc_f_stream.readlines()
        lc_l_info = json.loads(lc_f_lines[0])
        lc_l_song = json.loads(lc_f_lines[1])

        lc_channels = lc_l_song['channels']["channels"]
        lc_ch_p1 = lc_channels[0]["sl"]
        lc_ch_p2 = lc_channels[1]["sl"]
        lc_ch_p3 = lc_channels[2]["sl"]
        lc_ch_p4 = lc_channels[3]["sl"]

        lc_enable_loop = lc_l_song['enable_loop']
        lc_loop_end_bar = lc_l_song['loop_end_bar']
        lc_loop_start_bar = lc_l_song['loop_start_bar']
        lc_pages = lc_l_song['pages']
        lc_speed = lc_l_song['speed']

        cvpj_l = {}
        cvpj_l_playlist = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []

        cvpj_l_playlist['1'] = {}
        cvpj_l_playlist['1']['name'] = "Part 1"
        cvpj_l_playlist['1']['color'] = [0.83, 0.09, 0.42]
        cvpj_l_playlist['1']['placements'] = lc_parse_placements(lc_ch_p1, 1)
        cvpj_l_playlist['2'] = {}
        cvpj_l_playlist['2']['name'] = "Part 2"
        cvpj_l_playlist['2']['color'] = [0.91, 0.76, 0.36]
        cvpj_l_playlist['2']['placements'] = lc_parse_placements(lc_ch_p2, 2)
        cvpj_l_playlist['3'] = {}
        cvpj_l_playlist['3']['name'] = "Part 3"
        cvpj_l_playlist['3']['color'] = [0.22, 0.36, 0.60]
        cvpj_l_playlist['3']['placements'] = lc_parse_placements(lc_ch_p3, 3)
        cvpj_l_playlist['4'] = {}
        cvpj_l_playlist['4']['name'] = "Part 4"
        cvpj_l_playlist['4']['color'] = [0.44, 0.78, 0.66]
        cvpj_l_playlist['4']['placements'] = lc_parse_placements(lc_ch_p4, 4)
        cvpj_l_playlist['5'] = {}
        cvpj_l_playlist['5']['name'] = "Chord"
        cvpj_l_playlist['5']['color'] = [0.64, 0.64, 0.64]
        cvpj_l_playlist['5']['placements'] = []

        for used_instrument in used_instruments:
            cvpj_inst = {}
            cvpj_inst["instdata"] = {}
            if used_instrument == 'Sine':
                cvpj_inst["instdata"]['plugin'] = 'shape-sine'
                cvpj_inst["instdata"]['plugindata'] = {}
            elif used_instrument == 'Square':
                cvpj_inst["instdata"]['plugin'] = 'shape-square'
                cvpj_inst["instdata"]['plugindata'] = {}
            elif used_instrument == 'Triangle':
                cvpj_inst["instdata"]['plugin'] = 'shape-triangle'
                cvpj_inst["instdata"]['plugindata'] = {}
            elif used_instrument == 'Saw':
                cvpj_inst["instdata"]['plugin'] = 'shape-saw'
                cvpj_inst["instdata"]['plugindata'] = {}
            elif used_instrument == 'Noise':
                cvpj_inst["instdata"]['plugin'] = 'retro-noise'
                cvpj_inst["instdata"]['plugindata'] = {'type': '4bit'}
            elif used_instrument == 'FreqNoise':
                cvpj_inst["instdata"]['plugin'] = 'retro-noise'
                cvpj_inst["instdata"]['plugindata'] = {'type': '1bit_short'}
            elif used_instrument == 'Pulse25':
                cvpj_inst["instdata"]['plugin'] = 'shape-pulse'
                cvpj_inst["instdata"]['plugindata'] = {'duty': 0.25}
            elif used_instrument == 'Pulse125':
                cvpj_inst["instdata"]['plugin'] = 'shape-pulse'
                cvpj_inst["instdata"]['plugindata'] = {'duty': 0.125}
            else:
                cvpj_inst["instdata"]['plugin'] = 'lovelycomposer'
                cvpj_inst["instdata"]['plugindata'] = {'inst': used_instrument}
            cvpj_inst["name"] = used_instrument
            cvpj_l_instruments[used_instrument] = cvpj_inst
            cvpj_l_instrumentsorder.append(used_instrument)

        startinststr = 'lc_instlist_'

        cvpj_l['timemarkers'] = placements.make_timemarkers([4, 4], patternlen, lc_loop_start_bar)
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = (3614.75409836/lc_speed)/2

        #with open('testout.json', "w") as fileout:
        #    json.dump(lc_l_song, fileout, indent=4, sort_keys=True)
        return json.dumps(cvpj_l)



