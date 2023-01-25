# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
from functions import placements
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
    for x in range(org_numofnotes): 
        org_notelist[x][0] = int.from_bytes(bio_org.read(4), "little") #position
    for x in range(org_numofnotes): 
        pre_note = bio_org.read(1)[0] #note
        if 0 <= pre_note <= 95: cur_note = pre_note
        org_notelist[x][1] = cur_note
    for x in range(org_numofnotes): 
        org_notelist[x][2] = bio_org.read(1)[0] #duration
    for x in range(org_numofnotes): 
        pre_vol = bio_org.read(1)[0] #vol
        if 0 <= pre_vol <= 254: cur_vol = pre_vol
        org_notelist[x][3] = cur_vol
    for x in range(org_numofnotes): 
        pre_pan = bio_org.read(1)[0] #pan
        if 0 <= pre_pan <= 12: cur_pan = pre_pan
        org_notelist[x][4] = cur_pan

    org_l_nl = {}
    for org_note in org_notelist: org_l_nl[org_note[0]] = org_note[1:5]
    org_l_nl = dict(sorted(org_l_nl.items(), key=lambda item: item[0]))

    cvpj_nl = []

    endnote = None
    notedur = 0
    #print('DATA              |POS  |END  |INSID|')
    for org_l_n in org_l_nl:
        notedata = org_l_nl[org_l_n]

        if endnote != None: 
            if org_l_n >= endnote: endnote = None

        if notedata[1] != 1: 
            notedur = notedata[1]
            endnote = org_l_n+notedur

        if endnote != None: 
            if endnote-org_l_n == notedur: isinsidenote = False
            else: isinsidenote = True
        else: isinsidenote = False

        #print(str(notedata).ljust(19),end='')
        #print(str(org_l_n).ljust(6),end='')
        #print(str(endnote).ljust(6),end='')
        #print(str(isinsidenote).ljust(6),end='')
        #print()

        if isinsidenote == False:
            cvpj_note = {}
            cvpj_note['position'] = org_l_n
            cvpj_note['key'] = notedata[0] - 60
            cvpj_note['duration'] = notedata[1]
            cvpj_note['vol'] = notedata[2] / 254
            cvpj_note['pan'] = (notedata[3] - 6) / 6
            cvpj_nl.append(cvpj_note)
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
        cvpj_l_trackdata = {}
        cvpj_l_trackordering = []
        cvpj_l_timemarkers = []
        cvpj_l_fxrack = {}

        bio_org = open(input_file, 'rb')
        org_type = bio_org.read(6)
        org_tempo = (int.from_bytes(bio_org.read(2), "little"))
        print("[input-orgmaker] Organya Type: " + str(org_type))
        print("[input-orgmaker] Tempo: " + str(org_tempo))
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
            print("[input-orgmaker] pitch = " + str(pitch), end=" ")
            print("| Inst = " + str(Instrument), end=" ")
            print("| NoSustainingNotes = " + str(disable_sustaining_notes), end=" ")
            print("| #notes = " + str(number_of_notes))
            org_instrumentinfotable.append([pitch,Instrument,disable_sustaining_notes,number_of_notes])
        t_cvpj_nl = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        t_cvpj_nl[0] = read_orgtrack(bio_org, org_instrumentinfotable, 0)
        t_cvpj_nl[1] = read_orgtrack(bio_org, org_instrumentinfotable, 1)
        t_cvpj_nl[2] = read_orgtrack(bio_org, org_instrumentinfotable, 2)
        t_cvpj_nl[3] = read_orgtrack(bio_org, org_instrumentinfotable, 3)
        t_cvpj_nl[4] = read_orgtrack(bio_org, org_instrumentinfotable, 4)
        t_cvpj_nl[5] = read_orgtrack(bio_org, org_instrumentinfotable, 5)
        t_cvpj_nl[6] = read_orgtrack(bio_org, org_instrumentinfotable, 6)
        t_cvpj_nl[7] = read_orgtrack(bio_org, org_instrumentinfotable, 7)
        t_cvpj_nl[8] = read_orgtrack(bio_org, org_instrumentinfotable, 8)
        t_cvpj_nl[9] = read_orgtrack(bio_org, org_instrumentinfotable, 9)
        t_cvpj_nl[10] = read_orgtrack(bio_org, org_instrumentinfotable, 10)
        t_cvpj_nl[11] = read_orgtrack(bio_org, org_instrumentinfotable, 11)
        t_cvpj_nl[12] = read_orgtrack(bio_org, org_instrumentinfotable, 12)
        t_cvpj_nl[13] = read_orgtrack(bio_org, org_instrumentinfotable, 13)
        t_cvpj_nl[14] = read_orgtrack(bio_org, org_instrumentinfotable, 14)
        t_cvpj_nl[15] = read_orgtrack(bio_org, org_instrumentinfotable, 15)
        for tracknum in range(16):
            s_cvpj_nl = t_cvpj_nl[tracknum]
            if len(t_cvpj_nl[tracknum]) != 0:
                if tracknum < 8: trackname = "Melody "+str(tracknum+1)
                else: trackname = l_drum_name[org_insttable[tracknum]]

                cvpj_placement = {}
                cvpj_placement['position'] = 0
                cvpj_placement['duration'] = note_mod.getduration(s_cvpj_nl)
                cvpj_placement['notelist'] = s_cvpj_nl

                #placements.resize_nl(cvpj_placement)

                cvpj_inst = {}
                cvpj_inst['type'] = 'instrument'
                cvpj_inst['name'] = trackname
                cvpj_inst['color'] = l_org_colors[tracknum]
                cvpj_inst["vol"] = 1.0
                cvpj_inst['instdata'] = {}
                cvpj_inst['instdata']['plugin'] = 'none'
                cvpj_inst['placements'] = [cvpj_placement]
                cvpj_l_trackdata['org_'+str(tracknum)] = cvpj_inst
                cvpj_l_trackordering.append('org_'+str(tracknum))

        cvpj_l = {}
        cvpj_l['use_fxrack'] = False
        cvpj_l['trackdata'] = cvpj_l_trackdata
        cvpj_l['trackordering'] = cvpj_l_trackordering
        cvpj_l['bpm'] = (1/(org_tempo/120))*120
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['timesig_numerator'] = 4
        return json.dumps(cvpj_l)
