# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
import mido
from mido import MidiFile
from functions import note_convert
from functions import values

MIDIDrumNames = {0:'Drums', 8:'Room Drums', 16:'Power Drums', 24:'Elec Drums', 25:'TR808 Drums', 32:'Jazz Drums', 40:'Brush Drums', 48:'Orchestra Drums', 56:'Sound FX', 127:'MT-32 Drums'}
MIDIControllerName = {}
MIDIControllerName[0] = "Bank Select"
MIDIControllerName[1] = "Modulation Wheel"
MIDIControllerName[2] = "Breath Controller"
MIDIControllerName[3] = "_undefined"
MIDIControllerName[4] = "Foot Pedal"
MIDIControllerName[5] = "Portamento/Glide Time"
MIDIControllerName[6] = "Data Entry (MSB)"
MIDIControllerName[7] = "MIDI Volume"
MIDIControllerName[8] = "Stereo Balance"
MIDIControllerName[9] = "_undefined"
MIDIControllerName[10] = "Pan"
MIDIControllerName[11] = "Expression Pedal"
MIDIControllerName[12] = "Effect Controller 1"
MIDIControllerName[13] = "Effect Controller 2"
MIDIControllerName[14] = "_undefined"
MIDIControllerName[15] = "_undefined"
MIDIControllerName[16] = "General Purpose Controller 1"
MIDIControllerName[17] = "General Purpose Controller 2"
MIDIControllerName[18] = "General Purpose Controller 3"
MIDIControllerName[19] = "General Purpose Controller 4"
MIDIControllerName[20] = "_undefined"
MIDIControllerName[21] = "_undefined"
MIDIControllerName[22] = "_undefined"
MIDIControllerName[23] = "_undefined"
MIDIControllerName[24] = "_undefined"
MIDIControllerName[25] = "_undefined"
MIDIControllerName[26] = "_undefined"
MIDIControllerName[27] = "_undefined"
MIDIControllerName[28] = "_undefined"
MIDIControllerName[29] = "_undefined"
MIDIControllerName[30] = "_undefined"
MIDIControllerName[31] = "_undefined"
MIDIControllerName[32] = "Bank Select"
MIDIControllerName[33] = "Modulation Wheel"
MIDIControllerName[34] = "Breath Controller"
MIDIControllerName[35] = "_undefined"
MIDIControllerName[36] = "Foot Pedal"
MIDIControllerName[37] = "Portamento/Glide Time"
MIDIControllerName[38] = "Data Entry"
MIDIControllerName[39] = "Volume"
MIDIControllerName[40] = "Balance"
MIDIControllerName[41] = "_undefined"
MIDIControllerName[42] = "Pan Position"
MIDIControllerName[43] = "Expression"
MIDIControllerName[44] = "Effect Control 1"
MIDIControllerName[45] = "Effect Control 2"
MIDIControllerName[46] = "_undefined"
MIDIControllerName[47] = "_undefined"
MIDIControllerName[48] = "_undefined"
MIDIControllerName[49] = "_undefined"
MIDIControllerName[50] = "_undefined"
MIDIControllerName[51] = "_undefined"
MIDIControllerName[52] = "_undefined"
MIDIControllerName[53] = "_undefined"
MIDIControllerName[54] = "_undefined"
MIDIControllerName[55] = "_undefined"
MIDIControllerName[56] = "_undefined"
MIDIControllerName[57] = "_undefined"
MIDIControllerName[58] = "_undefined"
MIDIControllerName[59] = "_undefined"
MIDIControllerName[60] = "_undefined"
MIDIControllerName[61] = "_undefined"
MIDIControllerName[62] = "_undefined"
MIDIControllerName[63] = "_undefined"
MIDIControllerName[64] = "Sustain Pedal On/Off"
MIDIControllerName[65] = "Portamento/Glide On/Off Switch"
MIDIControllerName[66] = "Sostenuto On/Off Switch"
MIDIControllerName[67] = "Soft Pedal On/Off Switch"
MIDIControllerName[68] = "Legato On/Off Switch"
MIDIControllerName[69] = "Hold Pedal 2"
MIDIControllerName[70] = "Sound Controller 1"
MIDIControllerName[71] = "Sound Controller 2 - Filter Resonance"
MIDIControllerName[72] = "Sound Controller 3 - Amp Envelope Decay"
MIDIControllerName[73] = "Sound Controller 4 - Amp Envelope Attack"
MIDIControllerName[74] = "Sound Controller 5 - Filter Cutoff"
MIDIControllerName[75] = "Sound Controller 6"
MIDIControllerName[76] = "Sound Controller 7"
MIDIControllerName[77] = "Sound Controller 8"
MIDIControllerName[78] = "Sound Controller 9"
MIDIControllerName[79] = "Sound Controller 10"
MIDIControllerName[80] = "General Purpose"
MIDIControllerName[81] = "General Purpose"
MIDIControllerName[82] = "General Purpose"
MIDIControllerName[83] = "General Purpose"
MIDIControllerName[84] = "_undefined"
MIDIControllerName[85] = "_undefined"
MIDIControllerName[86] = "_undefined"
MIDIControllerName[87] = "_undefined"
MIDIControllerName[88] = "_undefined"
MIDIControllerName[89] = "_undefined"
MIDIControllerName[90] = "_undefined"
MIDIControllerName[91] = "Effect 1 Amount (Reverb)"
MIDIControllerName[92] = "Effect 2 Amount (Tremelo)"
MIDIControllerName[93] = "Effect 3 Amount (Chorus)"
MIDIControllerName[94] = "Effect 4 Amount (Detuning)"
MIDIControllerName[95] = "Effect 5 Amount (Phaser)"
MIDIControllerName[96] = "Data Bound Increment (+1)"
MIDIControllerName[97] = "Data Bound Decrement (-1)"
MIDIControllerName[98] = "NRPN LSB"
MIDIControllerName[99] = "NRPN MSB"
MIDIControllerName[100] = "RPN LSB"
MIDIControllerName[101] = "RPN MSB"
MIDIControllerName[102] = "_undefined"
MIDIControllerName[103] = "_undefined"
MIDIControllerName[104] = "_undefined"
MIDIControllerName[105] = "_undefined"
MIDIControllerName[106] = "_undefined"
MIDIControllerName[107] = "_undefined"
MIDIControllerName[108] = "_undefined"
MIDIControllerName[109] = "_undefined"
MIDIControllerName[110] = "_undefined"
MIDIControllerName[111] = "_undefined"
MIDIControllerName[112] = "_undefined"
MIDIControllerName[113] = "_undefined"
MIDIControllerName[114] = "_undefined"
MIDIControllerName[115] = "_undefined"
MIDIControllerName[116] = "_undefined"
MIDIControllerName[117] = "_undefined"
MIDIControllerName[118] = "_undefined"
MIDIControllerName[119] = "_undefined"
MIDIControllerName[120] = "Channel Mute / Sound Off"
MIDIControllerName[121] = "Reset All Controllers"
MIDIControllerName[122] = "Local Keyboard On/Off Switch"
MIDIControllerName[123] = "All MIDI Notes OFF"
MIDIControllerName[124] = "OMNI Mode OFF"
MIDIControllerName[125] = "OMNI Mode ON"
MIDIControllerName[126] = "Mono Mode"
MIDIControllerName[127] = "Poly Mode"

MIDIInstColors = values.getlist_gm_colors()
MIDIInstNames = values.getlist_gm_names()

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

                        if inst in MIDIDrumNames and midi_trackname == None:
                            cvpj_trackdata["name"] = MIDIDrumNames[inst]+' [Trk'+str(t_tracknum)+']'
                        if inst not in MIDIDrumNames and midi_trackname == None:
                            cvpj_trackdata["name"] = 'Drums [Trk'+str(t_tracknum)+']'

                        if inst in MIDIDrumNames and midi_trackname != None:
                            cvpj_trackdata["name"] = midi_trackname+' ('+MIDIDrumNames[inst]+') [Trk'+str(t_tracknum)+']'
                        if inst not in MIDIDrumNames and midi_trackname != None:
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

        cvpj_l['use_fxrack'] = True
        cvpj_l['timemarkers'] = cvpj_l_timemarkers
        cvpj_l['timesig_numerator'] = midi_numerator
        cvpj_l['timesig_denominator'] = midi_denominator
        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = midi_bpm

        return json.dumps(cvpj_l)
