# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import os.path
from functions import audio_wav
from functions import data_bytes

def pmddecodenotes(pmdfile, recordspertrack, pitch):
    notelist = []
    placements = []
    splitnotes = 16
    splitcurrent = 0
    placementpos = 0
    currentpan = 0
    for pmdpos in range(recordspertrack):
        splitcurrent += 1

        bitnotes = bin(int.from_bytes(pmdfile.read(3), "little"))[2:].zfill(24)
        pan = int.from_bytes(pmdfile.read(1), "little")
        if pan != 0: currentpan = (pan-4)/3

        notenum = 11
        for bitnote in bitnotes:
            if bitnote == '1':
                noteJ = {}
                noteJ['position'] = pmdpos - placementpos
                noteJ['key'] = notenum + pitch
                noteJ['duration'] = 1
                noteJ['pan'] = currentpan
                noteJ['vol'] = 1.0
                notelist.append(noteJ)
            notenum -= 1
        if splitnotes == splitcurrent:
            patJ = {}
            patJ['position'] = placementpos
            patJ['notelist'] = notelist
            if notelist != []:
                placements.append(patJ)
            notelist = []
            splitcurrent = 0
            placementpos += splitnotes
    return placements

def parsetrack(placements, trackname, vol, samplefolder, wavid):
    trkJ = {}
    instJ = {}
    if wavid != None:
        instJ['plugin'] = "sampler"
        instJ['plugindata'] = {}
        instJ['plugindata']['file'] = samplefolder + '/' + str(wavid) + '.wav'
    else :
        instJ['plugin'] = "none"
    trkJp = {}
    if wavid == 1: trkJ['color'] = [0.25, 0.38, 0.49]
    if wavid == 2: trkJ['color'] = [0.36, 0.43, 0.46]
    if wavid == 3: trkJ['color'] = [0.51, 0.57, 0.47]
    if wavid == None: trkJ['color'] = [0.58, 0.64, 0.40]
    trkJ['type'] = "instrument"
    trkJ['instrument'] = trackname
    trkJ['plugindata'] = trkJp
    trkJ['name'] = trackname
    trkJ['vol'] = vol
    trkJ['placements'] = placements
    trackordering.append(trackname)
    trkJ['instdata'] = instJ
    tracklist[trackname] = trkJ

class input_pms(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'piyopiyo'
    def getname(self): return 'PiyoPiyo'
    def gettype(self): return 'r'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(3)
        if bytesdata == b'PMD': return True
        else: return False
        bytestream.seek(0)
    def parse(self, input_file, extra_param):
        global tracklist
        global trackordering
        global instruments
        pmdfile = open(input_file, 'rb')
        header = pmdfile.read(4)
        trackdatapos = int.from_bytes(pmdfile.read(4), "little")
        musicwait = int.from_bytes(pmdfile.read(4), "little")
        bpm = (120/musicwait)*120
        print("[input-piyopiyo] MusicWait: " + str(musicwait))
        loopstart = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Loop Beginning: " + str(loopstart))
        loopend = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Loop End: " + str(loopend))
        recordspertrack = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Records Per Track: " + str(recordspertrack))

        file_name = os.path.splitext(os.path.basename(input_file))[0]
        if 'samplefolder' in extra_param:
            samplefolder = extra_param['samplefolder'] + file_name + '/'
        else:
            samplefolder = os.getcwd() + '/samples/' + file_name + '/'
            os.makedirs(os.getcwd() + '/samples/', exist_ok=True)
        os.makedirs(samplefolder, exist_ok=True)

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
            wave_path = samplefolder + str(tracknum+1) + '.wav'
            audio_wav.generate(wave_path, data_bytes.unsign_8(trk_waveform), 1, 67000, 8, {'loop':[0, 256]})
            pmdtrackdata.append([(trk_octave-2)*12, trk_icon, trk_length, trk_volume, trk_waveform, trk_envelope])

        TrackPVol = int.from_bytes(pmdfile.read(4), "little")

        pmdfile.seek(trackdatapos)
        notes1 = pmddecodenotes(pmdfile, recordspertrack, pmdtrackdata[0][0])
        notes2 = pmddecodenotes(pmdfile, recordspertrack, pmdtrackdata[1][0])
        notes3 = pmddecodenotes(pmdfile, recordspertrack, pmdtrackdata[2][0])
        notesP = pmddecodenotes(pmdfile, recordspertrack, 0)
        tracklist = {}
        trackordering = []
        instruments = {}
        parsetrack(notes1, 'Note #1', pmdtrackdata[0][3]/250, samplefolder, 1)
        parsetrack(notes2, 'Note #2', pmdtrackdata[1][3]/250, samplefolder, 2)
        parsetrack(notes3, 'Note #3', pmdtrackdata[2][3]/250, samplefolder, 3)
        parsetrack(notesP, 'Drums', TrackPVol/250, samplefolder, None)
        loopJ = {}
        loopJ['enabled'] = 1
        loopJ['start'] = loopstart/16
        loopJ['end'] = loopend/16
        rootJ = {}
        rootJ['bpm'] = bpm
        rootJ['trackdata'] = tracklist
        rootJ['trackordering'] = trackordering
        rootJ['instruments'] = instruments
        rootJ['loop'] = loopJ
        return json.dumps(rootJ)

