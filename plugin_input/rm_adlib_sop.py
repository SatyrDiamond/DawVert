# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import struct
import os.path

from functions import data_bytes
from functions_plugin_cvpj import params_fm

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
        if sop_event_code == 1: sop_eventdata.append([sop_event_pos, 'SPECIAL', song_file.read(1)[0]])
        elif sop_event_code == 2: 
            note_pitch = song_file.read(1)[0]
            note_length = int.from_bytes(song_file.read(2), "little")
            sop_eventdata.append([sop_event_pos, 'NOTE', note_pitch, note_length])
        elif sop_event_code == 3: sop_eventdata.append([sop_event_pos, 'TEMPO', song_file.read(1)[0]])
        elif sop_event_code == 4: sop_eventdata.append([sop_event_pos, 'VOL', song_file.read(1)[0]])
        elif sop_event_code == 5: sop_eventdata.append([sop_event_pos, 'PITCH', song_file.read(1)[0]])
        elif sop_event_code == 6: sop_eventdata.append([sop_event_pos, 'INST', song_file.read(1)[0]])
        elif sop_event_code == 7: sop_eventdata.append([sop_event_pos, 'PAN', song_file.read(1)[0]])
        elif sop_event_code == 8: sop_eventdata.append([sop_event_pos, 'GVOL', song_file.read(1)[0]])
        else:
            print('[error] unknown event code:', sop_event_code)
            exit()
    return sop_eventdata


class input_sop(plugin_input.base):
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
    def parse(self, convproj_obj, input_file, extra_param):
        song_file = open(input_file, 'rb')

        convproj_obj.type = 'rm'
        
        sop_signature = song_file.read(7)
        sop_majorVersion = song_file.read(1)[0]
        sop_minorVersion = song_file.read(1)[0]
        song_file.read(1)
        sop_fileName = data_bytes.readstring_fixedlen(song_file, 13, None)
        print('[input-sop] File Name:', sop_fileName)
        sop_title = data_bytes.readstring_fixedlen(song_file, 31, None)
        print('[input-sop] Title:', sop_title)
        sop_opl_rhythm = song_file.read(1)[0]
        song_file.read(1)
        sop_tickBeat = song_file.read(1)[0]
        convproj_obj.set_timings(sop_tickBeat, False)
        song_file.read(1)
        sop_beatMeasure = song_file.read(1)[0]
        sop_basicTempo = song_file.read(1)[0]
        print('[input-sop] BPM:', sop_basicTempo)
        sop_comment = data_bytes.readstring_fixedlen(song_file, 13, None)
        print('[input-sop] Comment:', sop_comment)
        sop_num_tracks = song_file.read(1)[0]
        sop_num_insts = song_file.read(1)[0]
        song_file.read(1)

        convproj_obj.metadata.name = sop_title
        convproj_obj.metadata.comment_text = sop_comment
        convproj_obj.params.add('bpm', sop_basicTempo, 'float')

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

            inst_obj = convproj_obj.add_instrument(cvpj_instname)
            inst_obj.pluginid = cvpj_instname
            inst_obj.visual.name = instname
            inst_obj.visual.color = [0.39, 0.16, 0.78]

            if sop_data_s_inst[0] in [1,6,7,8,9,10]:
                fmdata = params_fm.fm_data('opl2')
                sbidata = sop_data_s_inst[3]
                iMod = [sbidata[0], sbidata[1], sbidata[2], sbidata[3], sbidata[4]]
                iFeedback = sbidata[5]
                iCar = [sbidata[6], sbidata[7], sbidata[8], sbidata[9], sbidata[10]]
                fmdata.opl_sbi_part_op(0, iMod, False)
                fmdata.opl_sbi_part_op(1, iCar, False)
                fmdata.opl_sbi_part_fbcon(iFeedback, 'feedback', 'fm')
                fmdata.to_cvpj(convproj_obj, cvpj_instname)

            if sop_data_s_inst[0] == 0:
                fmdata = params_fm.fm_data('opl3')
                fouropdata = sop_data_s_inst[3]
                op1_data = [fouropdata[0], fouropdata[1], fouropdata[2], fouropdata[3], fouropdata[4]]
                op12_fbcon = fouropdata[5]
                op2_data = [fouropdata[6], fouropdata[7], fouropdata[8], fouropdata[9], fouropdata[10]]
                op3_data = fouropdata[11:16]
                op34_fbcon = fouropdata[16]
                op4_data = fouropdata[17:22]
                fmdata.opl_sbi_part_op(0, op1_data, False)
                fmdata.opl_sbi_part_fbcon(op12_fbcon, 'feedback_12', 'con_12')
                fmdata.opl_sbi_part_op(1, op2_data, False)
                fmdata.opl_sbi_part_op(2, op3_data, False)
                fmdata.opl_sbi_part_fbcon(op34_fbcon, 'feedback_34', 'con_34')
                fmdata.opl_sbi_part_op(3, op4_data, False)
                fmdata.to_cvpj(convproj_obj, cvpj_instname)

        all_notepos = None

        for tracknum in range(sop_num_tracks):
            sop_data_track = sop_data_tracks[tracknum]

            if sop_data_chanmodes[tracknum] == 0: trackname_endtext = ''
            if sop_data_chanmodes[tracknum] == 1: trackname_endtext = '4OP (YMF-262M)'
            if sop_data_chanmodes[tracknum] == 2: trackname_endtext = '2OP (YM-3812)'

            cvpj_trackid = str(tracknum)
            curinst = 0
            curtick = 0

            firstnotepos = None


            track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 0, False)
            track_obj.visual.name = '#'+str(cvpj_trackid)+' '+str()+trackname_endtext
            track_obj.visual.color = [0.39, 0.16, 0.78]
            placement_obj = track_obj.placements.add_notes()

            for sop_track_cmd in sop_data_track:
                curtick += sop_track_cmd[0]

                if sop_track_cmd[1] == 'VOL': convproj_obj.add_autotick(['track', cvpj_trackid, 'vol'], curtick, sop_track_cmd[2])

                if sop_track_cmd[1] == 'INST': curinst = sop_track_cmd[2]

                if sop_track_cmd[1] == 'NOTE': 
                    if firstnotepos == None: firstnotepos = curtick
                    elif curtick < firstnotepos: firstnotepos = curtick

                    if all_notepos == None: all_notepos = curtick
                    elif curtick < all_notepos: all_notepos = curtick

                    placement_obj.notelist.add_m(str(curinst), curtick, sop_track_cmd[3], sop_track_cmd[2]-48, 1, {})

        auto_bpm = {}
        for sop_track_cmd in sop_data_ctrltrack:
            curtick += sop_track_cmd[0]
            if sop_track_cmd[1] == 'TEMPO': convproj_obj.add_autotick(['main', 'bpm'], curtick, sop_track_cmd[2])

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')