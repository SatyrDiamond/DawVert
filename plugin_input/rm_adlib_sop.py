# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import struct
import os.path

from functions_plugparams import opl_sbi
from functions import audio_wav
from functions import data_bytes
from functions import placement_data
from functions import tracks
from functions import plugins
from functions import song
from functions import note_data
from functions import params

def add_point(i_list, time, value):
    if time not in i_list: i_list[time] = []
    i_list[time].append(value)

def decode_events(song_file):
    sop_eventdata = []
    track_numEvents = int.from_bytes(song_file.read(2), "little")
    track_dataSize = int.from_bytes(song_file.read(4), "little")
    for _ in range(track_numEvents):
        sop_event_pos = int.from_bytes(song_file.read(2), "little")
        sop_event_code = song_file.read(1)[0]
        if sop_event_code == 1: 
            sop_eventdata.append([sop_event_pos, 'SPECIAL', song_file.read(1)[0]])
        elif sop_event_code == 2: 
            note_pitch = song_file.read(1)[0]
            note_length = int.from_bytes(song_file.read(2), "little")
            sop_eventdata.append([sop_event_pos, 'NOTE', note_pitch, note_length])
        elif sop_event_code == 3: 
            sop_eventdata.append([sop_event_pos, 'TEMPO', song_file.read(1)[0]])
        elif sop_event_code == 4: 
            sop_eventdata.append([sop_event_pos, 'VOL', song_file.read(1)[0]])
        elif sop_event_code == 5: 
            sop_eventdata.append([sop_event_pos, 'PITCH', song_file.read(1)[0]])
        elif sop_event_code == 6: 
            sop_eventdata.append([sop_event_pos, 'INST', song_file.read(1)[0]])
        elif sop_event_code == 7: 
            sop_eventdata.append([sop_event_pos, 'PAN', song_file.read(1)[0]])
        elif sop_event_code == 8: 
            sop_eventdata.append([sop_event_pos, 'GVOL', song_file.read(1)[0]])
        else:
            print('[error] unknown event code:', sop_event_code)
            exit()
    return sop_eventdata


class input_piyopiyo(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'adlib_sop'
    def getname(self): return 'Note Sequencer'
    def gettype(self): return 'rm'
    def getdawcapabilities(self): 
        return {
        'auto_nopl': True,
        'track_nopl': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(7)
        if bytesdata == b'sopepos': return True
        else: return False
    def parse(self, input_file, extra_param):
        song_file = open(input_file, 'rb')
        cvpj_l = {}
        
        cvpj_l['plugins'] = {}

        sop_signature = song_file.read(7)
        sop_majorVersion = song_file.read(1)[0]
        sop_minorVersion = song_file.read(1)[0]
        song_file.read(1)
        sop_fileName = data_bytes.readstring_fixedlen(song_file, 13, None)
        print('[input-sop] File Name:', sop_fileName)
        sop_title = data_bytes.readstring_fixedlen(song_file, 31, None)
        print('[input-sop] Title:', sop_title)
        song.add_info(cvpj_l, 'title', sop_title)
        sop_opl_rhythm = song_file.read(1)[0]
        song_file.read(1)
        sop_tickBeat = song_file.read(1)[0]
        sop_tickStep = sop_tickBeat/4
        song_file.read(1)
        sop_beatMeasure = song_file.read(1)[0]
        sop_basicTempo = song_file.read(1)[0]
        print('[input-sop] BPM:', sop_basicTempo)
        sop_comment = data_bytes.readstring_fixedlen(song_file, 13, None)
        print('[input-sop] Comment:', sop_comment)
        sop_num_tracks = song_file.read(1)[0]
        sop_num_insts = song_file.read(1)[0]
        song_file.read(1)

        song.add_info(cvpj_l, 'title', sop_title)
        song.add_info_msg(cvpj_l, 'text', sop_comment)
        params.add(cvpj_l, [], 'bpm', sop_basicTempo, 'float')


        # Channel modes
        sop_data_chanmodes = []
        for _ in range(sop_num_tracks):
            sop_data_chanmodes.append(song_file.read(1)[0])
        
        # Instruments
        sop_data_inst = []
        for _ in range(sop_num_insts):
            sop_instdata = [None,'','',[]]
            insttype = song_file.read(1)[0]
            sop_instdata[0] = insttype
            sop_instdata[1] = data_bytes.readstring_fixedlen(song_file, 8, "latin-1")
            sop_instdata[2] = data_bytes.readstring_fixedlen(song_file, 19, "latin-1")
            if insttype in [0]: sop_instdata[3] = song_file.read(22)
            if insttype in [1,6,7,8,9,10]: sop_instdata[3] = song_file.read(11)
            sop_data_inst.append(sop_instdata)
  
        # Sequenced tracks
        sop_data_tracks = []
        for _ in range(sop_num_tracks):
            sop_data_tracks.append(decode_events(song_file))
        
        # Control track
        sop_data_ctrltrack = decode_events(song_file)

        # Output
        for instnum in range(len(sop_data_inst)):
            sop_data_s_inst = sop_data_inst[instnum]
            instname = sop_data_s_inst[2] if sop_data_s_inst[2] != '' else sop_data_s_inst[1]
            cvpj_instname = str(instnum)
            tracks.c_inst_create(cvpj_l, cvpj_instname, name=instname, color=[0.39, 0.16, 0.78])

            #print(sop_data_s_inst, instname)

            #if sop_data_s_inst[0] in [1,6,7,8,9,10]:
            #    tracks.c_inst_pluginid(cvpj_l, cvpj_instname, cvpj_instname)
            #    plugins.add_plug(cvpj_l, cvpj_instname, 'fm', 'opl2')

            #    sbidata = sop_data_s_inst[3]
            #    iModChar = sbidata[0]
            #    iModScale = sbidata[1]
            #    iModAttack = sbidata[2]
            #    iModSustain = sbidata[3]
            #    iModWaveSel = sbidata[4]
            #    iFeedback = sbidata[5]
            #    iCarChar = sbidata[6]
            #    iCarScale = sbidata[7]
            #    iCarAttack = sbidata[8]
            #    iCarSustain = sbidata[9]
            #    iCarWaveSel = sbidata[10]

            #    opl_sbi.opl2sbi_plugin(cvpj_l, cvpj_instname, 
            #        iModChar, iCarChar, iModScale, iCarScale, 
            #        iModAttack, iCarAttack, iModSustain, iCarSustain, 
            #        iModWaveSel, iCarWaveSel, iFeedback)

            #if sop_data_s_inst[0] == 0:
            #    tracks.c_inst_pluginid(cvpj_l, cvpj_instname, cvpj_instname)
            #    plugins.add_plug(cvpj_l, cvpj_instname, 'fm', 'opl3')
            #    fouropdata = sop_data_s_inst[3]
            #    op1_data = fouropdata[0:5]
            #    op12_fbcon = fouropdata[5]
            #    op2_data = fouropdata[6:11]
            #    op3_data = fouropdata[11:16]
            #    op34_fbcon = fouropdata[16]
            #    op4_data = fouropdata[17:22]
            #    for opnum, opdata in [['m1',op1_data],['c1',op2_data],['m2',op3_data],['c2',op4_data]]:
            #        iOpChar = opdata[0]

            #        iOpScale = opdata[1]
            #        iOpAttack = opdata[2]
            #        iOpSustain = opdata[3]

            #        iOpWaveSel = opdata[4]
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_waveform", iOpWaveSel, 'int', "")

            #        out_kls = iOpScale >> 6
            #        out_lvl = iOpScale & 0x3F
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_level", (out_lvl*-1)+63, 'int', "")
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_ksr", out_kls, 'int', "")

            #        out_att, out_dec = data_bytes.splitbyte(iOpAttack)
            #        out_sus, out_rel = data_bytes.splitbyte(iOpSustain)
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_env_attack", (out_att*-1)+15, 'int', "")
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_env_sustain", (out_sus*-1)+15, 'int', "")
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_env_decay", (out_dec*-1)+15, 'int', "")
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_env_release", (out_rel*-1)+15, 'int', "")

            #        out_flags, out_mul = data_bytes.splitbyte(iOpChar)
            #        out_trem, out_vib, out_sust, out_krs = data_bytes.to_bin(out_flags, 4)
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_freqmul", out_mul, 'int', "")
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_tremolo", out_trem, 'int', "")
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_vibrato", out_vib, 'int', "")
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_ksr", out_krs, 'int', "")
            #        plugins.add_plug_param(cvpj_l, cvpj_instname, opnum+"_sust", out_sust, 'int', "")

        all_notepos = None

        for tracknum in range(sop_num_tracks):
            sop_data_track = sop_data_tracks[tracknum]

            cvpj_trackid = str(tracknum)
            cvpj_notelist = []
            curinst = 0
            curtick = 0

            firstnotepos = None

            auto_vol = {}
            #add_point(i_list, time, value):
            for sop_track_cmd in sop_data_track:
                curtick += sop_track_cmd[0]

                if sop_track_cmd[1] == 'VOL': auto_vol[curtick] = sop_track_cmd[2]

                if sop_track_cmd[1] == 'INST': curinst = sop_track_cmd[2]

                if sop_track_cmd[1] == 'NOTE': 
                    if firstnotepos == None: firstnotepos = curtick
                    elif curtick < firstnotepos: firstnotepos = curtick

                    if all_notepos == None: all_notepos = curtick
                    elif curtick < all_notepos: all_notepos = curtick

                    cvpj_notelist.append(
                        note_data.mx_makenote(
                            str(curinst), curtick/sop_tickStep, sop_track_cmd[3]/sop_tickStep, sop_track_cmd[2]-48, None, None
                            ))

            out_param = tracks.a_auto_nopl_paramauto(['track', cvpj_trackid, 'vol'], 'float', auto_vol, sop_tickStep, firstnotepos, 127, 127, 0)
            tracks.r_add_param(cvpj_l, cvpj_trackid, 'vol', out_param, 'float')

            placementdata = placement_data.nl2pl(cvpj_notelist)
            tracks.c_create_track(cvpj_l, 'instruments', cvpj_trackid, name=cvpj_trackid)
            tracks.c_pl_notes(cvpj_l, cvpj_trackid, placementdata)

        auto_bpm = {}
        for sop_track_cmd in sop_data_ctrltrack:
            curtick += sop_track_cmd[0]
            if sop_track_cmd[1] == 'TEMPO': auto_bpm[curtick] = sop_track_cmd[2]


        param_tempo = tracks.a_auto_nopl_paramauto(['main', 'bpm'], 'float', auto_bpm, sop_tickStep, all_notepos, 120, 1, 0)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True

        tracks.a_auto_nopl_to_cvpj(cvpj_l)

        return json.dumps(cvpj_l)