# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import bisect
from mido import MidiFile
from objects import midi_in

class input_midi(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'midi'
    def gettype(self): return 'rm'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'MIDI'
        dawinfo_obj.file_ext = 'mid'
        dawinfo_obj.fxtype = 'rack'
        dawinfo_obj.fxrack_params = ['vol','pan','pitch']
        dawinfo_obj.auto_types = ['nopl_ticks']
        dawinfo_obj.track_nopl = True
        dawinfo_obj.plugin_included = ['midi']
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'MThd': return True
        else: return False
    def parse(self, convproj_obj, input_file, dv_config):
        midifile = MidiFile(input_file, clip=True)
        ppq = midifile.ticks_per_beat
        print("[input-midi] PPQ: " + str(ppq))
        convproj_obj.type = 'rm'
        convproj_obj.set_timings(midifile.ticks_per_beat, False)
        midiobj = midi_in.midi_in()
        midiobj.song_start(16, ppq, 120, [4,4])
        for track in midifile.tracks:
            midicmds = []
            for msg in track:
                midicmds.append(['rest', msg.time])
                if msg.type == 'note_on':
                    if msg.velocity != 0: midicmds.append(['note_on', msg.channel, msg.note, msg.velocity])
                    else: midicmds.append(['note_off', msg.channel, msg.note])
                elif msg.type == 'note_off': midicmds.append(['note_off', msg.channel, msg.note])
                elif msg.type == 'pitchwheel': midicmds.append(['pitchwheel', msg.channel, (msg.pitch/4096)])
                elif msg.type == 'program_change': midicmds.append(['program_change', msg.channel, msg.program])
                elif msg.type == 'control_change': midicmds.append(['control_change', msg.channel, msg.control, msg.value])
                elif msg.type == 'set_tempo': midicmds.append(['tempo', 60000000/msg.tempo])
                elif msg.type == 'time_signature': midicmds.append(['timesig', msg.numerator, msg.denominator])
                elif msg.type == 'marker': midicmds.append(['marker', msg.text])
                elif msg.type == 'text': midicmds.append(['text', msg.text])
                elif msg.type == 'sysex': midicmds.append(['sysex', msg.data])
                elif msg.type == 'key_signature': midicmds.append(['key_signature', msg.key])
                elif msg.type == 'track_name': midicmds.append(['track_name', msg.name])
                elif msg.type == 'sequencer_specific': midicmds.append(['sequencer_specific', msg.data])
                elif msg.type == 'copyright': midicmds.append(['copyright', msg.text])
                #elif msg.type == 'end_of_track': midicmds.append(['end_of_track'])
            midiobj.add_track(0, midicmds)
        midiobj.song_end(convproj_obj)

        for global_miditrack in midiobj.global_miditracks:
            if not global_miditrack[6] and global_miditrack[1] != None:
                convproj_obj.metadata.comment_text += global_miditrack[1]+'\n'

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        #convproj_obj.do_actions.append('do_sorttracks')

