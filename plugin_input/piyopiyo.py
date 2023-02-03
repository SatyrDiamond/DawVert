# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import os.path
from functions import audio_wav
from functions import data_bytes
from functions import folder_samples

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
        pan = pmdfile.read(1)[0]
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
            patJ['duration'] = splitnotes
            patJ['notelist'] = notelist
            if notelist != []:
                placements.append(patJ)
            notelist = []
            splitcurrent = 0
            placementpos += splitnotes
    return placements

def parsetrack(placements, trackid, trackname, vol, samplefolder, wavid):
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
    cvpj_l_trackordering.append(trackid)
    trkJ['instdata'] = instJ
    cvpj_l_trackdata[trackid] = trkJ

class input_pms(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
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
        global cvpj_l_trackdata
        global cvpj_l_trackordering
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
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        pmdtrackdata = []
        for tracknum in range(3):
            print("[input-piyopiyo] Track " + str(tracknum+1), end=",")
            trk_octave = pmdfile.read(1)[0]
            print(" Oct:" + str(trk_octave), end=",")
            trk_icon = pmdfile.read(1)[0]
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
        cvpj_l_trackdata = {}
        cvpj_l_trackordering = []
        parsetrack(notes1, 'piyopiyo_note1', 'Note #1', pmdtrackdata[0][3]/250, samplefolder, 1)
        parsetrack(notes2, 'piyopiyo_note2', 'Note #2', pmdtrackdata[1][3]/250, samplefolder, 2)
        parsetrack(notes3, 'piyopiyo_note3', 'Note #3', pmdtrackdata[2][3]/250, samplefolder, 3)
        parsetrack(notesP, 'piyopiyo_perc', 'Drums', TrackPVol/250, samplefolder, None)
        cvpj_l = {}
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['bpm'] = bpm
        cvpj_l['track_data'] = cvpj_l_trackdata
        cvpj_l['track_order'] = cvpj_l_trackordering
        cvpj_l['timemarkers'] = []
        cvpj_l['timemarkers'].append({'name': 'Loop', 'position': loopstart, 'end': loopend, 'type': 'loop'})
        return json.dumps(cvpj_l)

