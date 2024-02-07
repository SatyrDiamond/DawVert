# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import os.path
import struct
from functions import colors
from functions import data_bytes
from functions import data_values
from objects import dv_dataset

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

def decode_tempo(inpit_val): return (3614.75409836/inpit_val)/2

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

def lc_parse_voice_chords(cvpj_notelist, sl_json, length, currentchord):
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

    chords = data_values.list_findrepeat(dictdata)
    notepos = 0
    for chord in chords:
        if chord[0] != None:
            key = chord[0][0]-60
            for chordnote in chord[0][1:]:
                cvpj_notelist.add_m('chord', notepos, chord[1], key+chordnote, 1, {})
        notepos += chord[1]

    return currentchord


def get_valauto(val_def, valtable):
    out_val = val_def
    out_auto = []
    if None not in valtable and len(valtable) != 0:
        if len(valtable) == 1:
            val_def = valtable[0]
        elif len(valtable) > 1:
            if len(set(valtable)) == 1:
                val_def = valtable[0]
            else:
                val_def = max(valtable)/15
                for pos, value in enumerate(valtable): out_auto.append([pos, value])
    return val_def, out_auto

def lc_parse_voice(cvpj_notelist, sl_json, tracknum, length):
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

    for t_note in t_notelist:
        cvpj_instid = str(tracknum)+'_'+t_note[1]

        note_vol, cvpj_n_vol = get_valauto(1, t_note[5])
        note_pan, cvpj_n_pan = get_valauto(0, t_note[6])

        if note_vol == 0: note_vol = 15

        cvpj_notelist.add_m(cvpj_instid, t_note[0], t_note[4], t_note[2], note_vol/15, {'pan': note_pan})

        for ad in cvpj_n_vol: 
            autopoint_obj = cvpj_notelist.last_add_auto('gain')
            autopoint_obj.pos = ad[0]
            autopoint_obj.value = ad[1]*(15/note_vol)

        for ad in cvpj_n_pan: 
            autopoint_obj = cvpj_notelist.last_add_auto('pan')
            autopoint_obj.pos = ad[0]
            autopoint_obj.value = ad[1]

        if [tracknum, t_note[1]] not in used_instruments: used_instruments.append([tracknum, t_note[1]])

    return cvpj_notelist.to_cvpj()

def lc_do_track(convproj_obj, sl_json, tracknum, pl_color, ischord):
    global patternlen
    patternlen = []
    position = 0
    currentchord = None
    track_obj = convproj_obj.add_track(str(tracknum), 'instruments', 1, False)
    for sle in sl_json:
        length = sle['play_notes'] if 'play_notes' in sle else 32
        lc_notes = sle['vl']
        placement_obj = track_obj.placements.add_notes()
        placement_obj.position = position
        placement_obj.duration = length
        placement_obj.visual.color = pl_color
        if ischord == False: lc_parse_voice(placement_obj.notelist, lc_notes, tracknum, length)
        else: currentchord = lc_parse_voice_chords(placement_obj.notelist, lc_notes, length, currentchord)
        patternlen.append(length)
        position += length
    return track_obj

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
    def parse(self, convproj_obj, input_file, extra_param):
        convproj_obj.type = 'rm'
        convproj_obj.set_timings(4, False)

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

        dataset = dv_dataset.dataset('./data_dset/lovelycomposer.dset')
        colordata = colors.colorset(dataset.colorset_e_list('track', 'main'))

        for num in range(5):
            track_obj = lc_do_track(convproj_obj, lc_channels[num]["sl"], num, colordata.getcolornum(num), num == 4)
            track_obj.visual.name = "Part "+str(num+1) if num != 4 else "Chord"

        for used_instrument in used_instruments:
            cvpj_instid = str(used_instrument[0])+'_'+used_instrument[1]

            plugin_obj, pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
            osc_data = plugin_obj.osc_add()

            inst_obj = convproj_obj.add_instrument(cvpj_instid)
            inst_obj.pluginid = pluginid
            inst_obj.visual.name = used_instrument[1]
            inst_obj.visual.color = colordata.getcolornum(used_instrument[0])

            if used_instrument[1] == 'Sine': 
                osc_data.shape = 'sine'
            elif used_instrument[1] == 'Square': 
                osc_data.shape = 'square'
                osc_data.params['pulse_width'] = 1/2
            elif used_instrument[1] == 'Triangle':
                osc_data.shape = 'triangle'
            elif used_instrument[1] == 'Saw': 
                osc_data.shape = 'saw'
            elif used_instrument[1] == 'Noise': 
                osc_data.shape = 'noise'
                osc_data.params['noise_type'] = '4bit'
            elif used_instrument[1] == 'FreqNoise': 
                osc_data.shape = 'noise'
                osc_data.params['noise_type'], '1bit_short'
            elif used_instrument[1] == 'Pulse25': 
                osc_data.shape = 'square'
                osc_data.params['pulse_width'] = 1/4
            elif used_instrument[1] == 'Pulse125': 
                osc_data.shape = 'square'
                osc_data.params['pulse_width'] = 1/8
            #else: 
            #    inst_plugindata = plugins.cvpj_plugin('deftype', 'lovelycomposer', used_instrument[1])

        inst_obj = convproj_obj.add_instrument('chord')
        inst_obj.visual.name = 'Chord'
        inst_obj.visual.color = colordata.getcolornum(4)

        startinststr = 'lc_instlist_'

        tempoauto = []
        position = 0
        prevtempo = 0
        for chandata in lc_channels[0]["sl"]:
            duration = chandata['play_notes'] if 'play_notes' in chandata else 32

            bpm = decode_tempo(chandata['play_speed'] if 'play_speed' in chandata else lc_speed)

            if prevtempo != bpm:
                autopl_obj = convproj_obj.add_automation_pl('main/bpm', 'float')
                autopl_obj.position = position
                autopl_obj.duration = duration
                autopoint_obj = autopl_obj.data.add_point()
                autopoint_obj.value = bpm
                prevtempo = bpm

            position += duration

        convproj_obj.patlenlist_to_timemarker(patternlen, lc_loop_start_bar)
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.params.add('bpm', decode_tempo(lc_speed), 'float')


