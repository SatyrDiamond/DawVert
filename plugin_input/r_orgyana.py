# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
from functions import placements
from functions import tracks
from functions import song
from functions import note_data
import plugin_input
import json

l_drum_name = ["Bass 1", "Bass 2", "Snare 1", "Snare 2", "Tom 1", "Hi-Hat Close", "Hi-Hat Open", "Crash", "Perc 1", "Perc 2", "Bass 3", "Tom 2"]

l_org_colors = [[0.23, 0.30, 0.99],
[0.62, 0.11, 0.12],
[0.62, 0.16, 0.87],
[0.14, 0.45, 0.26],
[0.13, 0.46, 0.57],
[0.67, 0.50, 0.11],
[0.59, 0.64, 0.71],
[0.58, 0.53, 0.49],
[0.23, 0.30, 0.99],
[0.62, 0.11, 0.12],
[0.62, 0.16, 0.87],
[0.14, 0.45, 0.26],
[0.13, 0.46, 0.57],
[0.67, 0.50, 0.11],
[0.59, 0.64, 0.71],
[0.58, 0.53, 0.49]
]

def read_orgtrack(bio_org, instrumentinfotable_input, trackid):
    global cur_note
    global cur_vol
    global cur_pan
    org_numofnotes = instrumentinfotable_input[trackid][3]
    org_notelist = []
    for x in range(org_numofnotes): org_notelist.append([0,0,0,0,0])
    for x in range(org_numofnotes): #position
        org_notelist[x][0] = int.from_bytes(bio_org.read(4), "little")
    for x in range(org_numofnotes): #note
        pre_note = bio_org.read(1)[0]
        if 0 <= pre_note <= 95: cur_note = pre_note
        org_notelist[x][1] = cur_note
    for x in range(org_numofnotes): #duration
        org_notelist[x][2] = bio_org.read(1)[0]
    for x in range(org_numofnotes): #vol
        pre_vol = bio_org.read(1)[0]
        if 0 <= pre_vol <= 254: cur_vol = pre_vol
        org_notelist[x][3] = cur_vol
    for x in range(org_numofnotes): #pan
        pre_pan = bio_org.read(1)[0]
        if 0 <= pre_pan <= 12: cur_pan = pre_pan
        org_notelist[x][4] = cur_pan
    org_l_nl = {}
    for org_note in org_notelist: org_l_nl[org_note[0]] = org_note[1:5]
    org_l_nl = dict(sorted(org_l_nl.items(), key=lambda item: item[0]))
    cvpj_nl = []
    endnote = None
    notedur = 0
    for org_l_n in org_l_nl:
        notedata = org_l_nl[org_l_n]
        if endnote != None: if org_l_n >= endnote: endnote = None
        if notedata[1] != 1:
            notedur = notedata[1]
            endnote = org_l_n+notedur
        if endnote != None:
            if endnote-org_l_n == notedur: isinsidenote = False
            else: isinsidenote = True
        else: isinsidenote = False
        if isinsidenote == False: cvpj_nl.append(note_data.rx_makenote(org_l_n, notedata[1], notedata[0]-48, notedata[2]/254, (notedata[3]-6)/6))
    return cvpj_nl

class input_orgyana(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'orgyana'
    def getname(self): return 'orgyana'
    def gettype(self): return 'r'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(6)
        if bytesdata == b'Org-02' or bytesdata == b'Org-03': return True
        else: return False
    def parse(self, input_file, extra_param):
        cvpj_l = {}

        bio_org = open(input_file, 'rb')
        org_type = bio_org.read(6)
        org_wait = int.from_bytes(bio_org.read(2), "little")
        print("[input-orgmaker] Organya Type: " + str(org_type))
        print("[input-orgmaker] NoteWait: " + str(org_wait))
        org_stepsperbar = int.from_bytes(bio_org.read(1), "little")
        print("[input-orgmaker] Steps Per Bar: " + str(org_stepsperbar))
        org_beatsperstep = int.from_bytes(bio_org.read(1), "little")
        print("[input-orgmaker] Beats per Step: " + str(org_beatsperstep))
        org_loop_beginning = int.from_bytes(bio_org.read(4), "little")
        print("[input-orgmaker] Loop Beginning: " + str(org_loop_beginning))
        org_loop_end = int.from_bytes(bio_org.read(4), "little")
        print("[input-orgmaker] Loop End: " + str(org_loop_end))
        org_instrumentinfotable = []
        org_insttable = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for x in range(16):
            pitch = int.from_bytes(bio_org.read(2), "little")
            Instrument = int.from_bytes(bio_org.read(1), "little")
            org_insttable[x-1] = Instrument
            disable_sustaining_notes = int.from_bytes(bio_org.read(1), "little")
            number_of_notes = int.from_bytes(bio_org.read(2), "little")
            print("[input-orgmaker] Pitch: " + str(pitch), end=", ")
            print("Inst: " + str(Instrument), end=", ")
            print("NoSustain: " + str(disable_sustaining_notes), end=", ")
            print("#Notes: " + str(number_of_notes))
            org_instrumentinfotable.append([pitch,Instrument,disable_sustaining_notes,number_of_notes])

        for tracknum in range(16):
            s_cvpj_nl = read_orgtrack(bio_org, org_instrumentinfotable, tracknum)
            if len(s_cvpj_nl) != 0:
                org_pitch = org_instrumentinfotable[tracknum][0]
                if tracknum < 8: trackname = "Melody "+str(tracknum+1)
                else: trackname = l_drum_name[org_insttable[tracknum]]
                idval = 'org_'+str(tracknum)
                tracks.r_addtrack_inst(cvpj_l, idval, {'pitch': (org_pitch-1000)/18})
                tracks.r_addtrack_data(cvpj_l, idval, trackname, l_org_colors[tracknum], 1.0, None)
                tracks.r_addtrackpl(cvpj_l, idval, placements.nl2pl(s_cvpj_nl))

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
       
        cvpj_l['bpm'] = (1/(org_wait/122))*122
        cvpj_l['timesig_denominator'] = org_stepsperbar
        cvpj_l['timesig_numerator'] = org_beatsperstep
       
        if org_loop_beginning != 0: song.add_timemarker_looparea(cvpj_l, None, org_loop_beginning, org_loop_end)
        return json.dumps(cvpj_l)
