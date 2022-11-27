# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later
import plugin_input
import mido
from mido import MidiFile
from functions import noteconv
import json
import chardet

def addtoalltables(contents):
    global TimedNoteChTable
    for TimedNoteChannel in TimedNoteChTable:
        TimedNoteChannel.append(contents)

class input_midi(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'MIDI'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'MThd':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        midifile = MidiFile(input_file, clip=True)

        ppq = midifile.ticks_per_beat
        print("[input-midi] PPQ: " + str(ppq))

        outputplaylist = []
        outputfx = []
        outputinsts = []
        
        global TimedNoteChTable
        
        text_trackid = 0

        midi_bpm = 120
        midi_numerator = 4
        midi_denominator = 4

        miditracknum = len(midifile.tracks)

        songname = None
        copyright = None

        table_songmessage = []

        for track in midifile.tracks:
            #print(track)
            text_trackid += 1
            TimedNoteChTable = []
            for _ in range(16):
                TimedNoteChTable.append([])

            FoundNotesTable = []
            for _ in range(16):
                FoundNotesTable.append(0)

            trackname = None
            for msg in track:
                metabeforenote = 1
                addtoalltables('program_change;0')
                TimedNoteChTable[9].append('instrument;' + str(128))

                if msg.type == 'track_name' and metabeforenote == 1:
                    if miditracknum != 1:
                        trackname = msg.name.rstrip().rstrip('\x00')
                    else:
                        songname = msg.name.rstrip().rstrip('\x00')

                if msg.type == 'copyright' and metabeforenote == 1:
                    copyright = msg.text.rstrip()

                if msg.type == 'set_tempo' and metabeforenote == 1:
                    midi_bpm = mido.tempo2bpm(msg.tempo)
                if msg.type == 'time_signature' and metabeforenote == 1:
                    midi_numerator = msg.numerator
                    midi_denominator = msg.denominator
                if msg.type == 'time_signature' and miditracknum == 1:
                    addtoalltables('seperate_safe;')

                if msg.time != 0:
                    addtoalltables('break;' + str(msg.time/ppq))
                if msg.type == 'note_on':
                    metabeforenote = 0
                    FoundNotesTable[msg.channel] = 1
                    if msg.velocity == 0:
                        TimedNoteChTable[msg.channel].append('note_off;' + str(msg.note-60))
                    else:
                        TimedNoteChTable[msg.channel].append('note_on;' + str(msg.note-60) + ',' + str(msg.velocity/127))
                if msg.type == 'note_off':
                    FoundNotesTable[msg.channel] = 1
                    TimedNoteChTable[msg.channel].append('note_off;' + str(msg.note-60))
                if msg.type == 'program_change':
                    if msg.channel == 9:
                        TimedNoteChTable[msg.channel].append('instrument;' + str(128))
                    else:
                        TimedNoteChTable[msg.channel].append('instrument;' + str(msg.program+1))

            for MIDIChannel in range(16):
                if FoundNotesTable[MIDIChannel] == 1:
                    print("[input-midi] Track " + str(text_trackid) + ", Channel " + str(MIDIChannel+1))
                    noteconv.timednotes2notelistplacement_track_start()
                    singletrack = {}
                    if miditracknum != 1:
                        trackname_from = "Trk" + str(text_trackid) + "Ch" + str(MIDIChannel+1)
                        singletrack['id'] = "Trk" + str(text_trackid) + "Ch" + str(MIDIChannel+1)
                    else:
                        trackname_from = "Ch" + str(MIDIChannel+1)
                        singletrack['id'] = "Ch" + str(MIDIChannel+1)
                    if trackname != None:
                        print("[input-midi] Track Name: " + trackname)
                        singletrack['mi2s_nameordering'] = 'track_inst'
                        singletrack['name'] = trackname + ' (' + trackname_from + ')'
                    else:
                        singletrack['mi2s_nameordering'] = 'inst_track'
                        singletrack['name'] = trackname_from
                    singletrack['placements'] = noteconv.timednotes2notelistplacement_parse_timednotes(TimedNoteChTable[MIDIChannel])
                    singletrack['fxrack_channel'] = MIDIChannel+1
                    outputplaylist.append(singletrack)

            allzero = all(v == 0 for v in FoundNotesTable)
            if allzero == True and trackname != None:
                print("[input-midi] Track " + str(text_trackid) + ", Message Track: " + trackname)
                table_songmessage.append(trackname.rstrip('\x00'))


        trkJp = {}
        trkJp['plugin'] = "none"
        trkJp['basenote'] = 0
        trkJp['pitch'] = 0
        trkJp['usemasterpitch'] = 1
        trkJ = {}
        trkJ['associd'] = 0
        trkJ['vol'] = 1.0
        trkJ['name'] = 'NoName'
        trkJ['instrumentdata'] = trkJp
        outputinsts.append(trkJ)

        MIDIInstNames = ["Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavi", "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer", "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion", "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar harmonics", "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2", "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani", "String Ensemble 1", "String Ensemble 2", "SynthStrings 1", "SynthStrings 2", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit", "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "SynthBrass 1", "SynthBrass 2", "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet", "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina", "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)", "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)", "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)", "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)", "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bag pipe", "Fiddle", "Shanai", "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal", "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"]

        MIDIDrumNames = [[1,'Drums'],[9,'Room Drums'],[17,'Power Drums'],[25,'Elec Drums'],[26,'TR808 Drums'],[33,'Jazz Drums'],[41,'Brush Drums'],[49,'Orchestra Drums'],[57,'Sound FX'],[128,'MT-32 Drums']]

        for InstNumber in range(128):
            trkJp = {}
            trkJp['plugin'] = "none"
            trkJp['basenote'] = 0
            trkJp['pitch'] = 0
            trkJp['usemasterpitch'] = 1
            trkJ = {}
            trkJ['associd'] = InstNumber+1
            trkJ['vol'] = 1.0
            trkJ['name'] = MIDIInstNames[InstNumber]
            trkJ['instrumentdata'] = trkJp
            outputinsts.append(trkJ)
        
        for MIDIDrumName in MIDIDrumNames:
            trkJp = {}
            trkJp['plugin'] = "none"
            trkJp['basenote'] = 60
            trkJp['pitch'] = 0
            trkJp['usemasterpitch'] = 1
            trkJ = {}
            trkJ['associd'] = MIDIDrumName[0]+127
            trkJ['vol'] = 1.0
            trkJ['name'] = MIDIDrumName[1]
            trkJ['instrumentdata'] = trkJp
            outputinsts.append(trkJ)
        
        for current_channelnum in range(16):
            fxJ = {}
            fxJ['name'] = "Ch" + str(current_channelnum+1)
            fxJ['num'] = current_channelnum+1
            outputfx.append(fxJ)
        
        songmessage = ''

        if miditracknum == 1:
            if songname != None:
                songmessage += '"' + songname + '"' + '\n'
        if copyright != None:
            songmessage += '(C) ' + copyright + '\n'

        for msg in table_songmessage:
            songmessage += msg + '\n'

        bytes_songmessage = bytes(songmessage,"latin-1")
        songmessage_encoding = chardet.detect(bytes_songmessage)['encoding']

        if songmessage_encoding != None:
            songmessage_out = bytes_songmessage.decode(songmessage_encoding)
        else:
            songmessage_out = songmessage

        rootJ = {}
        rootJ['mastervol'] = 1.0
        rootJ['masterpitch'] = 0.0
        rootJ['timesig_numerator'] = 4
        rootJ['timesig_denominator'] = 4
        rootJ['bpm'] = midi_bpm
        rootJ['playlist'] = outputplaylist
        rootJ['fxrack'] = outputfx
        rootJ['instruments'] = outputinsts
        if songname != None:
            rootJ['title'] = songname
        if songmessage_out != '':
            rootJ['message'] = songmessage_out
        rootJ['cvpjtype'] = 'multiple'
        return json.dumps(rootJ)
