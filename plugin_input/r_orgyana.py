# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from objects import dv_dataset
import plugin_input
import json

cur_val = 0

def org_stream(bio_org, org_numofnotes, maxchange, org_notelist, tnum):
    global cur_val
    for x in range(org_numofnotes):
        pre_val = bio_org.read(1)[0]
        if maxchange != None:
            if 0 <= pre_val <= maxchange: cur_val = pre_val
            org_notelist[x][tnum] = cur_val
        else:
            org_notelist[x][tnum] = pre_val


def read_orgtrack(bio_org, instrumentinfotable_input, trackid):
    global cur_val
    org_numofnotes = instrumentinfotable_input[trackid][3]
    org_notelist = []
    for x in range(org_numofnotes): org_notelist.append([0,0,0,0,0])
    for x in range(org_numofnotes): #position
        org_notelist[x][0] = int.from_bytes(bio_org.read(4), "little")

    org_stream(bio_org, org_numofnotes, 95, org_notelist, 1) #note
    org_stream(bio_org, org_numofnotes, 256, org_notelist, 2) #duration
    org_stream(bio_org, org_numofnotes, 254, org_notelist, 3) #vol
    org_stream(bio_org, org_numofnotes, 12, org_notelist, 4) #pan

    org_l_nl = {}
    for org_note in org_notelist: org_l_nl[org_note[0]] = org_note[1:5]
    org_l_nl = dict(sorted(org_l_nl.items(), key=lambda item: item[0]))
    endnote = None
    notedur = 0
    org_notelist = []
    for org_l_n in org_l_nl:
        notedata = org_l_nl[org_l_n]
        if endnote != None: 
            if org_l_n >= endnote: endnote = None
        if notedata[1] != 1:
            notedur = notedata[1]
            endnote = org_l_n+notedur
        if endnote != None: isinsidenote = False if endnote-org_l_n == notedur else True
        else: isinsidenote = False
        if isinsidenote == False: org_notelist.append([org_l_n, notedata[1], notedata[0]-48, notedata[2]/254, {'pan': (notedata[3]-6)/6}])
    return org_notelist

class input_orgyana(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'orgyana'
    def gettype(self): return 'r'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Orgyana'
        dawinfo_obj.file_ext = 'org'
        dawinfo_obj.auto_types = ['nopl_points']
        dawinfo_obj.track_nopl = True
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(6)
        if bytesdata == b'Org-02' or bytesdata == b'Org-03': return True
        else: return False

    def parse(self, convproj_obj, input_file, dv_config):
        convproj_obj.type = 'r'
        convproj_obj.set_timings(4, True)

        dataset = dv_dataset.dataset('./data_dset/orgyana.dset')
        colordata = colors.colorset(dataset.colorset_e_list('track', 'orgmaker_2'))

        bio_org = open(input_file, 'rb')
        org_type = bio_org.read(6)
        org_wait = int.from_bytes(bio_org.read(2), "little")
        print("[input-orgmaker] Organya Type: " + str(org_type))
        print("[input-orgmaker] NoteWait: " + str(org_wait))
        org_stepsperbar = bio_org.read(1)[0]
        print("[input-orgmaker] Steps Per Bar: " + str(org_stepsperbar))
        org_beatsperstep = bio_org.read(1)[0]
        print("[input-orgmaker] Beats per Step: " + str(org_beatsperstep))
        org_loop_beginning = int.from_bytes(bio_org.read(4), "little")
        print("[input-orgmaker] Loop Beginning: " + str(org_loop_beginning))
        org_loop_end = int.from_bytes(bio_org.read(4), "little")
        print("[input-orgmaker] Loop End: " + str(org_loop_end))
        org_instrumentinfotable = []
        org_insttable = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for x in range(16):
            pitch = int.from_bytes(bio_org.read(2), "little")
            Instrument = bio_org.read(1)[0]
            org_insttable[x-1] = Instrument
            disable_sustaining_notes = bio_org.read(1)[0]
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
                trackname = "Melody "+str(tracknum+1) if tracknum < 8 else dataset.object_get_name_color('drums', str(org_insttable[tracknum]))[0]
                idval = 'org_'+str(tracknum)

                track_obj = convproj_obj.add_track(idval, 'instrument', 0, False)
                track_obj.visual.name = trackname
                track_obj.visual.color = colordata.getcolornum(tracknum)
                track_obj.params.add('pitch', (org_pitch-1000)/1800, 'float')
                for n_pos, n_dur, n_note, n_vol, n_extra in s_cvpj_nl: track_obj.placements.notelist.add_r(n_pos, n_dur, n_note, n_vol, n_extra)

        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        convproj_obj.params.add('bpm', (1/(org_wait/122))*122, 'float')
        convproj_obj.timesig = [org_stepsperbar, org_beatsperstep]

        if org_loop_beginning != 0: 
            convproj_obj.loop_active = True
            convproj_obj.loop_start = org_loop_beginning
            convproj_obj.loop_end = org_loop_end