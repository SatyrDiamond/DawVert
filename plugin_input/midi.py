# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
import mido
from mido import MidiFile
from functions import note_convert
from functions import values

MIDIControllerName = values.getlist_gm_ctrl_names()
MIDIInstColors = values.getlist_gm_colors()
MIDIInstNames = values.getlist_gm_names()
MIDIDrumSetNames = values.getlist_gm_drumset_names()

def addtoalltables(contents):
    global t_chan_timednote
    for TimedNoteChannel in t_chan_timednote:
        TimedNoteChannel.append(contents)

class input_midi(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'midi'
    def getname(self): return 'MIDI'
    def gettype(self): return 'm'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'MThd': return True
        else: return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        midifile = MidiFile(input_file, clip=True)
        ppq = midifile.ticks_per_beat
        print("[input-midi] PPQ: " + str(ppq))
        midi_bpm = 120
        midi_numerator = 4
        midi_denominator = 4
        num_tracks = len(midifile.tracks)

        cvpj_songname = None
        cvpj_copyright = None

        t_tracknum = 0
        t_playlistnum = 0

        cvpj_l = {}
        cvpj_l_playlist = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_timemarkers = []
        cvpj_l_fxrack = {}

        global t_chan_timednote

        midichanneltype = [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0]

        for track in midifile.tracks:
            midi_trackname = None

            t_tracknum += 1
            cmd_before_note = True
            cmd_before_program = True


            t_chan_used = []
            for _ in range(16): t_chan_used.append(0)

            t_chan_timednote = []
            for _ in range(16): t_chan_timednote.append([])

            t_chan_usedinst = []
            for _ in range(16): t_chan_usedinst.append([])

            t_chan_auto = []
            for _ in range(16): t_chan_auto.append([])


            t_chan_initial = []
            for _ in range(16): t_chan_initial.append({})



            for midi_channum in range(16):
                t_chan_timednote[midi_channum].append('instrument;' + str(0))

            time_signature_pos = 0
            sysex_pos = 0

            for msg in track:

                #if msg.type == 'sequencer_specific' and cmd_before_note == 1:
                #    #midi_sysex.sequencer_specific_decode(msg)
                
                if msg.type == 'track_name' and cmd_before_note == 1:
                    if num_tracks != 1: midi_trackname = msg.name.rstrip().rstrip('\x00')
                    else: cvpj_songname = msg.name.rstrip().rstrip('\x00')

                if msg.type == 'copyright' and cmd_before_note == 1:
                    cvpj_copyright = msg.text.rstrip()

                if msg.type == 'set_tempo' and cmd_before_note == 1:
                    midi_bpm = mido.tempo2bpm(msg.tempo)

                if msg.type == 'time_signature':
                    time_signature_pos += msg.time
                    timemarker = {}
                    timemarker['position'] = (time_signature_pos/ppq)*4
                    timemarker['name'] = str(msg.numerator)+'/'+str(msg.denominator)
                    timemarker['type'] = 'timesig'
                    timemarker['numerator'] = msg.numerator
                    timemarker['denominator'] = msg.denominator
                    cvpj_l_timemarkers.append(timemarker)

                if msg.time != 0:
                    addtoalltables('break;' + str((msg.time/ppq)*4))

                if msg.type == 'note_on':
                    cmd_before_note = 0
                    t_chan_used[msg.channel] = 1
                    if cmd_before_program == True: 
                        t_chan_usedinst[msg.channel].append(0)
                        cmd_before_program = False
                    if msg.velocity == 0: 
                        t_chan_timednote[msg.channel].append('note_off;' + str(msg.note-60))
                    else: 
                        t_chan_timednote[msg.channel].append('note_on;' + str(msg.note-60) + ',' + str(msg.velocity/127))

                if msg.type == 'note_off':
                    t_chan_used[msg.channel] = 1
                    t_chan_timednote[msg.channel].append('note_off;' + str(msg.note-60))

                if msg.type == 'program_change':
                    cmd_before_program = False
                    if msg.program+1 not in t_chan_usedinst[msg.channel]: t_chan_usedinst[msg.channel].append(msg.program)
                    t_chan_timednote[msg.channel].append('instrument;' + str(msg.program))

                if msg.type == 'control_change':
                    #print('used:', t_chan_used[msg.channel], ' ctrl:', msg.channel, msg.control, msg.value)
                    if t_chan_used[msg.channel] == 0:
                        t_chan_initial[msg.channel][msg.control] = msg.value

                #if msg.type == 'sysex':
                #    #midi_sysex.parse_sysex(msg, msg.time)

            for midi_channum in range(16):
                s_chan_initial = t_chan_initial[midi_channum]
                for controllerid in s_chan_initial:
                    print('[input-midi] Initial Controller Value, Ch:', midi_channum, ',Controller:', str(controllerid)+'/'+MIDIControllerName[controllerid])


            for midi_channum in range(16):
                t_instlist = t_chan_usedinst[midi_channum]
                if t_chan_used[midi_channum] == 1:
                    print("[input-midi] Track " + str(t_tracknum) + ", Channel " + str(midi_channum+1))
                    note_convert.timednotes2notelistplacement_track_start()

                    t_playlistnum += 1
                    playlistrowdata = {}
                    placements = note_convert.timednotes2notelistplacement_parse_timednotes(t_chan_timednote[midi_channum], 't'+str(t_tracknum)+'_c'+str(midi_channum+1)+'_i')

                    if midi_trackname != None:
                        playlistrowdata['name'] = str(midi_trackname)+' [Ch'+str(midi_channum+1)+']'
                    else:
                        playlistrowdata['name'] = '[Ch'+str(midi_channum+1)+']'
                    playlistrowdata['color'] = [0.3, 0.3, 0.3]
                    playlistrowdata['placements'] = placements
                    cvpj_l_playlist[str(t_playlistnum)] = playlistrowdata

                for inst in t_instlist:
                    cvpj_trackid = 't'+str(t_tracknum)+'_c'+str(midi_channum+1)+'_i'+str(inst)
                    cvpj_l_instruments[cvpj_trackid] = {}
                    cvpj_trackdata = cvpj_l_instruments[cvpj_trackid]
                    cvpj_trackdata["instdata"] = {}

                    if midichanneltype[midi_channum] == 1: cvpj_trackdata["instdata"]['usemasterpitch'] = 0
                    else: cvpj_trackdata["instdata"]['usemasterpitch'] = 1

                    cvpj_trackdata['fxrack_channel'] = midi_channum+1
                    cvpj_instdata = cvpj_trackdata["instdata"]
                    cvpj_instdata['plugin'] = 'general-midi'
                    if midichanneltype[midi_channum] != 1:
                        cvpj_instdata['plugindata'] = {'bank':0, 'inst':inst}
                        if midi_trackname != None:
                            cvpj_trackdata["name"] = midi_trackname+' ('+MIDIInstNames[inst]+')'+' [Trk'+str(t_tracknum)+' Ch'+str(midi_channum+1)+']'
                        else:
                            cvpj_trackdata["name"] = MIDIInstNames[inst]+' [Trk'+str(t_tracknum)+' Ch'+str(midi_channum+1)+']'
                        cvpj_trackdata["color"] = MIDIInstColors[inst]
                    else:
                        cvpj_instdata['plugindata'] = {'bank':128, 'inst':inst}

                        if inst in MIDIDrumSetNames and midi_trackname == None:
                            cvpj_trackdata["name"] = MIDIDrumSetNames[inst]+' [Trk'+str(t_tracknum)+']'
                        if inst not in MIDIDrumSetNames and midi_trackname == None:
                            cvpj_trackdata["name"] = 'Drums [Trk'+str(t_tracknum)+']'

                        if inst in MIDIDrumSetNames and midi_trackname != None:
                            cvpj_trackdata["name"] = midi_trackname+' ('+MIDIDrumSetNames[inst]+') [Trk'+str(t_tracknum)+']'
                        if inst not in MIDIDrumSetNames and midi_trackname != None:
                            cvpj_trackdata["name"] = midi_trackname+'(Drums) [Trk'+str(t_tracknum)+']'
                    if cvpj_trackid not in cvpj_l_instrumentsorder:
                        cvpj_l_instruments[cvpj_trackid] = cvpj_trackdata
                        cvpj_l_instrumentsorder.append(cvpj_trackid)


        #print(midi_sysex.get_sysexvals())

        cvpj_l_fxrack["0"] = {}
        cvpj_l_fxrack["0"]["name"] = "Master"

        for midi_channum in range(16):
            cvpj_l_fxrack[str(midi_channum+1)] = {}

            s_chan_initial = t_chan_initial[midi_channum]

            fxdata = cvpj_l_fxrack[str(midi_channum+1)]
            fxdata["fxenabled"] = 1

            if 7 in s_chan_initial: fxdata["vol"] = s_chan_initial[7]/127
            else: fxdata["vol"] = 1.0

            if 10 in s_chan_initial: fxdata["pan"] = ((s_chan_initial[10]/127)-0.5)*2
            else: fxdata["pan"] = 1.0

            fxdata['color'] = [0.3, 0.3, 0.3]
            fxdata["name"] = "Channel "+str(midi_channum+1)

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = True
        cvpj_l['timemarkers'] = cvpj_l_timemarkers
        cvpj_l['timesig_numerator'] = midi_numerator
        cvpj_l['timesig_denominator'] = midi_denominator
        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['instruments_data'] = cvpj_l_instruments
        cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = midi_bpm

        return json.dumps(cvpj_l)
