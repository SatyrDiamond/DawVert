# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json

def pmddecodenotes(pmdfile, recordspertrack, pitch):
    notelist = []
    currentpan = 0
    for pmdpos in range(recordspertrack):
        note_position = pmdpos/4
        bitnotes = bin(int.from_bytes(pmdfile.read(3), "little"))[2:].zfill(24)
        pan = int.from_bytes(pmdfile.read(1), "little")
        if pan != 0:
            currentpan = (pan-4)/3
        notenum = 11
        for bitnote in bitnotes:
            if bitnote == '1':
                noteJ = {}
                noteJ['position'] = note_position
                noteJ['key'] = notenum + pitch
                noteJ['duration'] = 1/4
                noteJ['pan'] = currentpan
                noteJ['vol'] = 1.0
                notelist.append(noteJ)
            notenum -= 1
    return notelist

def parsetrack(notelist, trackname):
    trkJ = {}
    trkJi = {}
    trkJi['plugin'] = "none"
    trkJp = {}
    trkJ['type'] = "instrument"
    trkJ['instrumentdata'] = trkJi
    trkJ['plugindata'] = trkJp
    trkJ['notelist'] = notelist
    trkJ['name'] = trackname
    trkJ['vol'] = 1
    patJ = {}
    patJ['position'] = 0
    patJ['notelist'] = notelist
    trkJ['placements'] = [patJ]
    return trkJ

class input_pmd(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'PiyoPiyo'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(3)
        if bytesdata == b'PMD':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        pmdfile = open(input_file, 'rb')
        header = pmdfile.read(4)
        trackdatapos = int.from_bytes(pmdfile.read(4), "little")
        musicwait = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] MusicWait: " + str(musicwait))
        loopstart = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Loop Beginning: " + str(loopstart))
        loopend = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Loop End: " + str(loopend))
        recordspertrack = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Records Per Track: " + str(recordspertrack))

        pmdtrackdata = []
        for tracknum in range(3):
            print("[input-piyopiyo] Track " + str(tracknum+1), end=",")
            trk_octave = int.from_bytes(pmdfile.read(1), "little")
            print(" Oct:" + str(trk_octave), end=",")
            trk_icon = int.from_bytes(pmdfile.read(1), "little")
            print(" Icon:" + str(trk_icon), end=",")
            trk_unk = pmdfile.read(2)
            trk_length = int.from_bytes(pmdfile.read(4), "little")
            print(" Len:" + str(trk_length), end=",")
            trk_volume = int.from_bytes(pmdfile.read(4), "little")
            print(" Vol:" + str(trk_volume))
            trk_unk2 = pmdfile.read(8)
            trk_waveform = pmdfile.read(256)
            trk_envelope = pmdfile.read(64)
            pmdtrackdata.append([(trk_octave-2)*12, trk_icon, trk_length, trk_volume, trk_waveform, trk_envelope])

        TrackPVol = int.from_bytes(pmdfile.read(4), "little")

        pmdfile.seek(trackdatapos)
        notes1 = pmddecodenotes(pmdfile, recordspertrack, pmdtrackdata[0][0])
        notes2 = pmddecodenotes(pmdfile, recordspertrack, pmdtrackdata[1][0])
        notes3 = pmddecodenotes(pmdfile, recordspertrack, pmdtrackdata[2][0])
        notesP = pmddecodenotes(pmdfile, recordspertrack, 0)
        tracklist = []
        tracklist.append(parsetrack(notes1, 'note1'))
        tracklist.append(parsetrack(notes2, 'note2'))
        tracklist.append(parsetrack(notes3, 'note3'))
        tracklist.append(parsetrack(notesP, 'drums'))
        loopJ = {}
        loopJ['enabled'] = 1
        loopJ['start'] = loopstart/16
        loopJ['end'] = loopend/16
        rootJ = {}
        rootJ['bpm'] = 140
        rootJ['tracks'] = tracklist
        rootJ['loop'] = loopJ
        rootJ['cvpjtype'] = 'single'
        return json.dumps(rootJ)

