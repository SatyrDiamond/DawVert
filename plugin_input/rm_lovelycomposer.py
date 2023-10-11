# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import os.path
import struct
from functions import placements
from functions import placement_data
from functions import plugins
from functions import auto
from functions import note_data
from functions import data_bytes
from functions import data_values
from functions import song
from functions_tracks import tracks_rm
from functions_tracks import auto_data

#               Name,              Type, FadeIn, FadeOut, PitchMod, Slide, Vib, Color
lc_instlist = {}
lc_instlist[ 2] = ['Square Wave'     ,'Square'    ,0  ,0  ,0  ,False ,False]
lc_instlist[ 1] = ['Triangle Wave'   ,'Triangle'  ,0  ,0  ,0  ,False ,False]
lc_instlist[ 0] = ['Pulse Wave'      ,'Pulse25'   ,0  ,0  ,0  ,False ,False]
lc_instlist[16] = ['SawTooth Wave'   ,'Saw'       ,0  ,0  ,0  ,False ,False]
lc_instlist[20] = ['Sine Wave'       ,'Sine'      ,0  ,0  ,0  ,False ,False]
lc_instlist[ 3] = ['Noise'           ,'Noise'     ,0  ,0  ,0  ,False ,False]
lc_instlist[ 4] = ['Piano Like'      ,'Pulse25'   ,0  ,1  ,0  ,False ,False]
lc_instlist[17] = ['Synth Piano'     ,'Saw'       ,0  ,1  ,0  ,False ,False]
lc_instlist[ 5] = ['Xylophone Like'  ,'Triangle'  ,0  ,1  ,0  ,False ,False]
lc_instlist[ 6] = ['Ice'             ,'Square'    ,0  ,1  ,0  ,False ,False]
lc_instlist[21] = ['Orgel Like'      ,'Sine'      ,0  ,1  ,0  ,False ,False]
lc_instlist[ 7] = ['Drum Like'       ,'Drum'      ,0  ,1  ,0  ,False ,False]
lc_instlist[ 8] = ['Strings Like'    ,'Pulse25'   ,0  ,0  ,0  ,False ,True ]
lc_instlist[ 9] = ['Vocal Like'      ,'Triangle'  ,0  ,0  ,0  ,False ,True ]
lc_instlist[10] = ['UFO'             ,'Square'    ,0  ,0  ,0  ,False ,True ]
lc_instlist[18] = ['Brass Like'      ,'Saw'       ,0  ,0  ,0  ,False ,True ]
lc_instlist[22] = ['Ghost'           ,'Sine'      ,0  ,0  ,0  ,False ,True ]

lc_instlist[14] = ['Glide Square'    ,'Square'    ,0  ,0  ,0  ,True  ,False]
lc_instlist[13] = ['Glide Triangle'  ,'Triangle'  ,0  ,0  ,0  ,True  ,False]
lc_instlist[12] = ['Glide Pulse'     ,'Pulse25'   ,0  ,0  ,0  ,True  ,False]
lc_instlist[19] = ['Glide SawTooth'  ,'Saw'       ,0  ,0  ,0  ,True  ,False]
lc_instlist[23] = ['Glide Sine'      ,'Sine'      ,0  ,0  ,0  ,True  ,False]
lc_instlist[15] = ['Glide Noise'     ,'Noise'     ,0  ,0  ,0  ,True  ,False]
lc_instlist[24] = ['Fish'            ,'Noise'     ,1  ,0  ,0  ,False ,False]
lc_instlist[25] = ['Flute Like'      ,'Triangle'  ,1  ,0  ,0  ,False ,False]
lc_instlist[26] = ['Slow String Like','Pulse25'   ,1  ,0  ,0  ,False ,False]
lc_instlist[27] = ['Saxophone Like'  ,'Saw'       ,1  ,0  ,0  ,False ,False]
lc_instlist[28] = ['Ocarina Like'    ,'Sine'      ,1  ,0  ,0  ,False ,False]
lc_instlist[29] = ['Seashore Like'   ,'Noise'     ,1  ,0  ,0  ,False ,False]
lc_instlist[30] = ['Stomp'           ,'Stomp'     ,0  ,1  ,-1 ,False ,False]
lc_instlist[31] = ['Twin Stomp'      ,'Stomp'     ,0  ,1  ,-1 ,False ,False]
lc_instlist[32] = ['Twin Drum'       ,'Drum'      ,0  ,2  ,0  ,False ,False]
lc_instlist[33] = ['Punch'           ,'Punch'     ,0  ,1  ,1  ,False ,False]
lc_instlist[34] = ['Orchestra Hit'   ,'OrchHit'   ,0  ,0  ,0  ,False ,False]

lc_instlist[35] = ['Short Freq Noise','FreqNoise' ,0  ,0  ,0  ,False ,False]
lc_instlist[36] = ['Hammer'          ,'FreqNoise' ,0  ,1  ,0  ,False ,False]
lc_instlist[37] = ['Robot'           ,'FreqNoise' ,1  ,0  ,0  ,False ,False]
lc_instlist[38] =['Glide S-Freq Noise','FreqNoise',0  ,0  ,0  ,False ,True ]
lc_instlist[39] = ['12.5% Pulse'     ,'Pulse125'  ,0  ,0  ,0  ,False ,False]
lc_instlist[46] = ['Pulse Brass'     ,'Pulse125'  ,0  ,0  ,0  ,False ,True ]
lc_instlist[40] = ['Lo-Fi Piano'     ,'Pulse125'  ,0  ,1  ,0  ,False ,False]
lc_instlist[41] = ['Fiddle'          ,'Pulse125'  ,1  ,0  ,0  ,False ,False]
lc_instlist[42] = ['Glide 12.5% Pulse','Pulse125' ,0  ,0  ,0  ,True  ,False]
lc_instlist[43] = ['Dog'             ,'Dog'       ,0  ,0  ,-1 ,False ,False]
lc_instlist[45] = ['Robo Stomp'      ,'RoboStomp' ,0  ,0  ,-1 ,False ,False]
lc_instlist[47] =['Low-Reso Triangle','LowResoTri',0  ,0  ,0  ,False ,False]
lc_instlist[48] =['Low-Reso Xylophone','LowResoTri',0 ,1  ,0  ,False ,False]
lc_instlist[49] = ['Low-Reso Vocal'  ,'LowResoTri',0  ,0  ,0  ,False ,True ]
lc_instlist[50] = ['Glide L-Triangle','LowResoTri',0  ,0  ,0  ,True  ,False]
lc_instlist[51] = ['Low-Reso Flute'  ,'LowResoTri',1  ,0  ,0  ,True  ,False]
lc_instlist[52] = ['Tilted Sawtooth' ,'TiltedSaw' ,1  ,0  ,0  ,False ,False]

#                  Name,             Type,        FadeIn, FadeOut, PitchMod, Slide, Vib, Color

lc_instlist[53] = ['Organ Like Wave' ,'Organ'     ,0  ,0  ,0  ,False ,False]
lc_instlist[54] = ['Phaser Triangle' ,'PhaserTri' ,0  ,0  ,0  ,False ,False]
lc_instlist[55] = ['Plucked String'  ,'TiltedSaw' ,0  ,1  ,0  ,False ,False]
lc_instlist[56] = ['Bell'            ,'Organ'     ,0  ,1  ,0  ,False ,False]
lc_instlist[57] = ['Star'            ,'PhaserTri' ,0  ,1  ,0  ,False ,False]
lc_instlist[58] = ['Oboe'            ,'TiltedSaw' ,0  ,0  ,0  ,False ,True ]
lc_instlist[59] = ['Opera Choir'     ,'Organ'     ,0  ,0  ,0  ,False ,True ]
lc_instlist[60] = ['Country String'  ,'TiltedSaw' ,1  ,0  ,0  ,False ,False]
lc_instlist[61] = ['Accordian'       ,'Organ'     ,1  ,0  ,0  ,False ,False]
lc_instlist[62] = ['Planet'          ,'PhaserTri' ,1  ,0  ,0  ,False ,False]
lc_instlist[63] = ['Bubble'          ,'LowResoTri',0  ,0  ,1  ,False ,False]
lc_instlist[64] = ['Glide Organ'     ,'Organ'     ,0  ,0  ,0  ,True  ,False]
lc_instlist[65] = ['Glide Tilted Saw','TiltedSaw' ,0  ,0  ,0  ,True  ,False]
lc_instlist[66] = ['Alien'           ,'LowResoTri',0  ,0  ,-.5,False ,False]
lc_instlist[67] = ['Melodic Tom'     ,'Triangle'  ,0  ,0  ,-.5,False ,False]

lc_instlist[68] = ['FastArp Square'  ,'FA-Square' ,0  ,0  ,0  ,False ,False]
lc_instlist[69] = ['FastArp Pulse25' ,'FA-Pul25'  ,0  ,0  ,0  ,False ,False]
lc_instlist[70] = ['FastArp Pulse125','FA-Pul125' ,0  ,0  ,0  ,False ,False]
lc_instlist[71] = ['FastArp Triangle','FA-Tri'    ,0  ,0  ,0  ,False ,False]
lc_instlist[72] = ['FastArp Sine'    ,'FA-Sine'   ,0  ,0  ,0  ,False ,False]
lc_instlist[73] =['FastArp TiltedSaw','FA-TiltSaw',0  ,0  ,0  ,False ,False]
lc_instlist[74] = ['FastArp Noise'   ,'FA-Noise'  ,0  ,0  ,0  ,False ,False]

lc_instlist[128]= ['_EXT'            ,'_EXT'      ,0  ,0  ,0  ,False ,False]
lc_instlist[129]= ['_EXT_E'          ,'_EXT'      ,0  ,1  ,0  ,False ,False]

used_instruments = []

def decode_pan(panbyte):
    if panbyte == 8: return 0
    elif panbyte == 15: return 1
    elif panbyte == 1: return -1
    else: return 0

def chord_parser(chordbytes_chord, chordbytes_seven, chordbytes_nine):
    chordtype = chordbytes_chord-1
    if chordtype == 0: output_val = None
    else: 
        if chordbytes_chord == 2: output_val = [0, 4, 7]
        if chordbytes_chord == 3: output_val = [0, 3, 7]
        if chordbytes_chord == 6: output_val = [0, 3, 6]
        if chordbytes_chord == 5: output_val = [0, 4, 8]
        if chordbytes_chord == 4: output_val = [0, 5, 7]
        if chordbytes_seven == 4: output_val.append(10)
        if chordbytes_seven == 8: output_val.append(11)
        if chordbytes_nine == 1: output_val.append(14)
        if chordbytes_nine == 2: output_val.append(13)
    return output_val

def lc_parse_voice_chords(sl_json, length, currentchord):
    position = 0

    dictdata = []
    for notenum in range(length):
        lc_notedata = sl_json[notenum]

        chordbytes = None
        if lc_notedata['id'] != None: 
            chordbytes_parts = struct.unpack("BBBB", lc_notedata['id'].to_bytes(4, 'little'))
            chordbytes_first = chordbytes_parts[3]
            chordbytes_second, chordbytes_third = data_bytes.splitbyte(chordbytes_parts[2])
            chorddata = chord_parser(chordbytes_third, chordbytes_second, chordbytes_first)
            if chorddata == None: currentchord = None
            else: currentchord = [lc_notedata['n']]+chorddata
        dictdata.append(currentchord)

        position += 1

    cvpj_notelist = []

    chords = data_values.dict_findrepeat(dictdata)
    notepos = 0
    for chord in chords:
        if chord[0] != None:
            key = chord[0][0]-60
            for chordnote in chord[0][1:]:
                cvpj_notelist.append(
                    note_data.mx_makenote('chord', notepos, chord[1], key+chordnote, None, None)
                    )
        notepos += chord[1]

    return cvpj_notelist, currentchord

def lc_parse_voice(sl_json, tracknum, length):
    global used_instruments
    position = 0

    curinst = None
    prev_notetable = None
    t_notelist = []

    for notenum in range(length):
        lc_notedata = sl_json[notenum]
        lc_inst = lc_notedata['id']

        out_pos = position

        if lc_inst in lc_instlist: 
            out_inst = lc_instlist[lc_inst][1]
            out_fadeout = int(not lc_instlist[lc_inst][3])
        else: 
            out_inst = None
            out_fadeout = 0

        out_key = lc_notedata['n'] if 'n' in lc_notedata else None
        if out_key != None: out_key -= 60
        out_vol = lc_notedata['x'] if 'x' in lc_notedata else 14
        out_pan = decode_pan(lc_notedata['p'] if 'p' in lc_notedata else 8)

        if out_inst != '_EXT': curinst = out_inst
        out_notetable = [out_pos, curinst, out_key, out_fadeout, 1, [], []]
        useappend = True
        if out_notetable[1] != None: 

            if len(t_notelist) != 0 and prev_notetable != None:
                extend_cont_pos = prev_notetable[0] == out_notetable[0]-1
                extend_cont_key = prev_notetable[2] == out_notetable[2]
                extend_cont_end = prev_notetable[4] == 1
                #print( extend_cont_pos and extend_cont_key and extend_cont_end, end=' ')
                if (extend_cont_pos and extend_cont_key and extend_cont_end) == True:
                    useappend = False
            if useappend == True and out_notetable[2] != None: 
                t_notelist.append(out_notetable)
            if len(t_notelist) != 0 and useappend == False: 
                t_notelist[-1][4] += 1 
                t_notelist[-1][5].append(out_vol)
                t_notelist[-1][6].append(out_pan)

        prev_notetable = out_notetable

        position += 1

    cvpj_notelist = []

    for t_note in t_notelist:
        cvpj_instid = str(tracknum)+'_'+t_note[1]
        cvpj_notedata = note_data.mx_makenote(cvpj_instid, t_note[0], t_note[4], t_note[2], None, None)

        if None not in t_note[5] and len(t_note[5]) != 0:
            auto_vals = auto.values2points(t_note[5], [0, 15])
            cvpj_notedata['vol'] = max(t_note[5])/15
            data_values.nested_dict_add_value(cvpj_notedata, ['notemod','auto','gain'], auto_vals)

        if None not in t_note[6]:
            if len(t_note[6]) == 1:
                cvpj_notedata['pan'] = t_note[6][0]
            elif len(t_note[6]) != 0:
                auto_vals = auto.values2points(t_note[6], None)
                data_values.nested_dict_add_value(cvpj_notedata, ['notemod','auto','pan'], auto_vals)

        cvpj_notelist.append(cvpj_notedata)

        if [tracknum, t_note[1]] not in used_instruments:
            used_instruments.append([tracknum, t_note[1]])

    return cvpj_notelist

def lc_parse_placements(sl_json, tracknum, pl_color, ischord):
    global patternpos
    global patternlen
    patternpos = []
    patternlen = []
    placements = []
    position = 0
    currentchord = None
    for sle in sl_json:
        if 'play_notes' in sle: length = sle['play_notes']
        else: length = 32
        lc_notes = sle['vl']

        if ischord == False: notelist = lc_parse_voice(lc_notes, tracknum, length)
        else: notelist, currentchord = lc_parse_voice_chords(lc_notes, length, currentchord)

        placement = placement_data.makepl_n(position, length, notelist)
        placement['color'] = pl_color
        if notelist != []: placements.append(placement)
        patternpos.append(position)
        patternlen.append(length)
        position += length
    return placements

lc_colors = [[0.83, 0.09, 0.42],[0.91, 0.76, 0.36],[0.22, 0.36, 0.60],[0.44, 0.78, 0.66],[0.64, 0.64, 0.64]]

class input_lc(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'lovelycomposer'
    def getname(self): return 'Lovely Composer'
    def gettype(self): return 'rm'
    def getdawcapabilities(self): 
        return {
        'track_lanes': True
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        lc_f_stream = open(input_file, 'r')
        lc_f_lines = lc_f_stream.readlines()
        lc_l_info = json.loads(lc_f_lines[0])
        lc_l_song = json.loads(lc_f_lines[1])

        lc_channels = lc_l_song['channels']["channels"]

        lc_enable_loop = lc_l_song['enable_loop']
        lc_loop_end_bar = lc_l_song['loop_end_bar']
        lc_loop_start_bar = lc_l_song['loop_start_bar']
        #lc_pages = lc_l_song['pages']
        lc_speed = lc_l_song['speed']

        cvpj_l = {}

        for num in range(5):
            cvpj_placements = lc_parse_placements(lc_channels[num]["sl"], num, lc_colors[num], num == 4)
            cvpj_plname = "Part "+str(num+1) if num != 4 else "Chord"
            tracks_rm.track_create(cvpj_l, str(num), 'instruments')
            tracks_rm.track_visual(cvpj_l, str(num), name=cvpj_plname)
            tracks_rm.add_pl(cvpj_l, str(num), 'notes', cvpj_placements)

        for used_instrument in used_instruments:
            pluginid = plugins.get_id()

            cvpj_instid = str(used_instrument[0])+'_'+used_instrument[1]

            cvpj_instdata = {}
            if used_instrument[1] == 'Sine': 
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'sine')
            elif used_instrument[1] == 'Square': 
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 0)
            elif used_instrument[1] == 'Triangle':
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'triangle')
            elif used_instrument[1] == 'Saw': 
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'saw')
            elif used_instrument[1] == 'Noise': 
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'noise')
                plugins.add_plug_data(cvpj_l, pluginid, 'type', '4bit')
            elif used_instrument[1] == 'FreqNoise': 
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'noise')
                plugins.add_plug_data(cvpj_l, pluginid, 'type', '1bit_short')
            elif used_instrument[1] == 'Pulse25': 
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 1)
            elif used_instrument[1] == 'Pulse125': 
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 2)
            else: 
                plugins.add_plug(cvpj_l, pluginid, 'lovelycomposer', used_instrument[1])
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 2)

            tracks_rm.inst_create(cvpj_l, cvpj_instid)
            tracks_rm.inst_visual(cvpj_l, cvpj_instid, name=used_instrument[1], color=lc_colors[used_instrument[0]])
            tracks_rm.inst_pluginid(cvpj_l, cvpj_instid, pluginid)

        tracks_rm.inst_create(cvpj_l, 'chord')
        tracks_rm.inst_visual(cvpj_l, 'chord', name='Chord', color=lc_colors[4])

        startinststr = 'lc_instlist_'

        tempoauto = []
        position = 0
        prevtempo = 0
        for chandata in lc_channels[0]["sl"]:
            duration = chandata['play_notes'] if 'play_notes' in chandata else 32
            bpm = (3614.75409836/chandata['play_speed'])/2 if 'play_speed' in chandata else 120
            tempopldata = auto.makepl(position, duration, [{"position": 0, "value": bpm}])
            if prevtempo != bpm:
                auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], tempopldata)
                prevtempo = bpm
            position += duration

        placements.make_timemarkers(cvpj_l, [4, 4], patternlen, lc_loop_start_bar)

        cvpj_l['do_addloop'] = True
        
        song.add_param(cvpj_l, 'bpm', (3614.75409836/lc_speed)/2)

        return json.dumps(cvpj_l)



