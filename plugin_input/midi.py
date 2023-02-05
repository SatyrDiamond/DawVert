# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
import mido
from mido import MidiFile
from functions import note_convert
from functions import format_midi_out

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

        num_tracks = len(midifile.tracks)
        cvpj_songname = None
        cvpj_copyright = None

        format_midi_out.song_start(16, ppq)

        for track in midifile.tracks:
            format_midi_out.track_start(16)
            midi_trackname = None
            timepos = 0

            for msg in track:
                timepos += msg.time
                print(msg)
                if msg.type == 'note_on':
                    if msg.velocity != 0: format_midi_out.note_on(timepos, msg.note-60, msg.channel, msg.velocity)
                    else: format_midi_out.note_off(timepos, msg.note-60, msg.channel)
                if msg.type == 'note_off': format_midi_out.note_off(timepos, msg.note-60, msg.channel)
                if msg.type == 'program_change': format_midi_out.program_change(timepos, msg.channel, msg.program)
                if msg.type == 'control_change': format_midi_out.control_change(timepos, msg.channel, msg.control, msg.value)
                if msg.type == 'set_tempo': format_midi_out.tempo(timepos, msg.tempo)
                if msg.type == 'track_name': format_midi_out.track_name(timepos, msg.name)
                if msg.type == 'time_signature': format_midi_out.time_signature(timepos, msg.numerator, msg.denominator)
                if msg.type == 'marker': format_midi_out.marker(timepos, msg.text)

            format_midi_out.track_end(16)

        cvpj_l = format_midi_out.song_end()

        return json.dumps(cvpj_l)
