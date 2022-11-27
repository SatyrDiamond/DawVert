# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
from functions import notemod

def parse_orgtrack(orgfile, instrumentinfotable_input, trackid):
    org_numofnotes = instrumentinfotable_input[trackid][3]
    orgnotelist = []
    for x in range(org_numofnotes):
        orgnotelist.append([0,0,0,0,0])
    for x in range(org_numofnotes): #position
        org_outnote = int.from_bytes(orgfile.read(4), "little")
        orgnotelist[x][0] = org_outnote 
    for x in range(org_numofnotes): #note
        org_note = int.from_bytes(orgfile.read(1), "little")
        orgnotelist[x][1] = org_note 
    for x in range(org_numofnotes): #duration
        org_duration = int.from_bytes(orgfile.read(1), "little")
        orgnotelist[x][2] = org_duration
    for x in range(org_numofnotes): #vol
        org_vol = int.from_bytes(orgfile.read(1), "little")
        orgnotelist[x][3] = org_vol
    for x in range(org_numofnotes): #pan
        org_pan = int.from_bytes(orgfile.read(1), "little")
        orgnotelist[x][4] = org_pan
    return orgnotelist

def orgnl2outnl(orgnotelist):
    notelist = []
    for currentnote in range(len(orgnotelist)):
        noteJ = {}
        orgnote = orgnotelist[currentnote]
        noteJ['position'] = orgnote[0]/4
        #key = 0
        pre_note = orgnote[1]
        if 0 <= pre_note <= 95:
            key = pre_note + 24
        noteJ['key'] = key - 72
        noteJ['duration'] = orgnote[2]/4
        #vol = 1.0
        pre_vol = orgnote[3]
        if 0 <= pre_vol <= 254:
            vol = pre_vol / 254
        noteJ['vol'] = vol
        #pan = 0.0
        pre_pan = orgnote[4]
        if 0 <= pre_pan <= 12:
            pan = (pre_pan - 6) / 6
        noteJ['pan'] = pan
        notelist.append(noteJ)
    return notelist

def parsetrack(notelist, trackid, orginst, orgtypeforname):
    trkJ = {}
    if notelist != []:
        trkJ = {}
        trkJ['type'] = "instrument"
        trkJi = {}
        trkJi['plugin'] = "orgyana"
        trkJp = {}
        trkJp['instrument'] = orginst
        trkJ['instrumentdata'] = trkJi
        trkJ['plugindata'] = trkJp
        trkJ['notelist'] = notelist
        if orgtypeforname == 1:
            trkJ['name'] = trackid + ' (' + orgdrumname[orginst] + ')'
            trkJ['id'] = 'perc'+str(trackid)
        else:
            trkJ['name'] = trackid + ' (' + str(orginst) + ')'
            trkJ['id'] = 'note'+str(trackid)
        trkJ['vol'] = 1
        patJ = {}
        patJ['position'] = 0
        patJ['duration'] = notemod.getduration(notelist)
        patJ['notelist'] = notelist
        trkJ['placements'] = [patJ]
        tracklist.append(trkJ)
    return trkJ

class input_org(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'Orgyana'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(6)
        if bytesdata == b'Org-02' or bytesdata == b'Org-03':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        global tracklist
        global orgdrumname
        orgfile = open(input_file, 'rb')
        file_header_orgtype = orgfile.read(6)
        tempo = (int.from_bytes(orgfile.read(2), "little"))
        print("[input-orgmaker] Organya Type: " + str(file_header_orgtype))
        print("[input-orgmaker] Tempo: " + str(tempo))
        Steps_Per_Bar = int.from_bytes(orgfile.read(1), "little")
        print("[input-orgmaker] Steps Per Bar: " + str(Steps_Per_Bar))
        Beats_per_Step = int.from_bytes(orgfile.read(1), "little")
        print("[input-orgmaker] Beats per Step: " + str(Beats_per_Step))
        loop_beginning = int.from_bytes(orgfile.read(4), "little")
        print("[input-orgmaker] Loop Beginning: " + str(loop_beginning))
        loop_end = int.from_bytes(orgfile.read(4), "little")
        print("[input-orgmaker] Loop End: " + str(loop_end))
        org_instrumentinfotable = []
        orgdrumname = ["Bass 1", "Bass 2", "Snare 1", "Snare 2", "Tom 1", "Hi-Hat Close", "Hi-Hat Open", "Crash", "Perc 1", "Perc 2", "Bass 3", "Tom 2"]
        orginsttable = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for x in range(16):
            pitch = int.from_bytes(orgfile.read(2), "little")
            Instrument = int.from_bytes(orgfile.read(1), "little")
            orginsttable[x-1] = Instrument
            disable_sustaining_notes = int.from_bytes(orgfile.read(1), "little")
            number_of_notes = int.from_bytes(orgfile.read(2), "little")
            print("[input-orgmaker] pitch = " + str(pitch), end=" ")
            print("| Inst = " + str(Instrument), end=" ")
            print("| NoSustainingNotes = " + str(disable_sustaining_notes), end=" ")
            print("| #notes = " + str(number_of_notes))
            org_instrumentinfotable.append([pitch,Instrument,disable_sustaining_notes,number_of_notes])
        orgnotestable_note1 = parse_orgtrack(orgfile, org_instrumentinfotable, 0)
        orgnotestable_note2 = parse_orgtrack(orgfile, org_instrumentinfotable, 1)
        orgnotestable_note3 = parse_orgtrack(orgfile, org_instrumentinfotable, 2)
        orgnotestable_note4 = parse_orgtrack(orgfile, org_instrumentinfotable, 3)
        orgnotestable_note5 = parse_orgtrack(orgfile, org_instrumentinfotable, 4)
        orgnotestable_note6 = parse_orgtrack(orgfile, org_instrumentinfotable, 5)
        orgnotestable_note7 = parse_orgtrack(orgfile, org_instrumentinfotable, 6)
        orgnotestable_note8 = parse_orgtrack(orgfile, org_instrumentinfotable, 7)
        orgnotestable_perc1 = parse_orgtrack(orgfile, org_instrumentinfotable, 8)
        orgnotestable_perc2 = parse_orgtrack(orgfile, org_instrumentinfotable, 9)
        orgnotestable_perc3 = parse_orgtrack(orgfile, org_instrumentinfotable, 10)
        orgnotestable_perc4 = parse_orgtrack(orgfile, org_instrumentinfotable, 11)
        orgnotestable_perc5 = parse_orgtrack(orgfile, org_instrumentinfotable, 12)
        orgnotestable_perc6 = parse_orgtrack(orgfile, org_instrumentinfotable, 13)
        orgnotestable_perc7 = parse_orgtrack(orgfile, org_instrumentinfotable, 14)
        orgnotestable_perc8 = parse_orgtrack(orgfile, org_instrumentinfotable, 15)
        tracklist = []
        parsetrack(orgnl2outnl(orgnotestable_note1), 'note1', orginsttable[0], 0)
        parsetrack(orgnl2outnl(orgnotestable_note2), 'note2', orginsttable[1], 0)
        parsetrack(orgnl2outnl(orgnotestable_note3), 'note3', orginsttable[2], 0)
        parsetrack(orgnl2outnl(orgnotestable_note4), 'note4', orginsttable[3], 0)
        parsetrack(orgnl2outnl(orgnotestable_note5), 'note5', orginsttable[4], 0)
        parsetrack(orgnl2outnl(orgnotestable_note6), 'note6', orginsttable[5], 0)
        parsetrack(orgnl2outnl(orgnotestable_note7), 'note7', orginsttable[6], 0)
        parsetrack(orgnl2outnl(orgnotestable_note8), 'note8', orginsttable[7], 0)
        parsetrack(orgnl2outnl(orgnotestable_perc1), 'perc1', orginsttable[8], 1)
        parsetrack(orgnl2outnl(orgnotestable_perc2), 'perc2', orginsttable[9], 1)
        parsetrack(orgnl2outnl(orgnotestable_perc3), 'perc3', orginsttable[10], 1)
        parsetrack(orgnl2outnl(orgnotestable_perc4), 'perc4', orginsttable[11], 1)
        parsetrack(orgnl2outnl(orgnotestable_perc5), 'perc5', orginsttable[12], 1)
        parsetrack(orgnl2outnl(orgnotestable_perc6), 'perc6', orginsttable[13], 1)
        parsetrack(orgnl2outnl(orgnotestable_perc7), 'perc7', orginsttable[14], 1)
        parsetrack(orgnl2outnl(orgnotestable_perc8), 'perc8', orginsttable[15], 1)
        loopJ = {}
        loopJ['enabled'] = 1
        loopJ['start'] = loop_beginning/16
        loopJ['end'] = loop_end/16
        rootJ = {}
        rootJ['mastervol'] = 1.0
        rootJ['timesig_numerator'] = Beats_per_Step
        rootJ['timesig_denominator'] = Steps_Per_Bar
        rootJ['bpm'] = tempo
        rootJ['tracks'] = tracklist
        rootJ['loop'] = loopJ
        rootJ['cvpjtype'] = 'single'
        return json.dumps(rootJ)

