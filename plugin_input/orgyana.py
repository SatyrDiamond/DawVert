import plugin_input
import json

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
    for x in range(org_numofnotes): #volume
        org_volume = int.from_bytes(orgfile.read(1), "little")
        orgnotelist[x][3] = org_volume
    for x in range(org_numofnotes): #pan
        org_pan = int.from_bytes(orgfile.read(1), "little")
        orgnotelist[x][4] = org_pan
    return orgnotelist

def orgnl2outnl(orgnotelist):
    notelist = []
    for currentnote in range(len(orgnotelist)):
        notejson = {}
        orgnote = orgnotelist[currentnote]
        notejson['position'] = ((orgnote[0] / 4) * notetime) / int(notesizedivision)
        #key = 0
        pre_note = orgnote[1]
        if 0 <= pre_note <= 95:
            key = pre_note + 24
        notejson['key'] = key - 60
        notejson['duration'] = ((orgnote[2] / 4) * notetime) / int(notesizedivision)
        #vol = 1.0
        pre_volume = orgnote[3]
        if 0 <= pre_volume <= 254:
            vol = pre_volume / 254
        notejson['vol'] = vol
        #pan = 0.0
        pre_pan = orgnote[4]
        if 0 <= pre_pan <= 12:
            pan = (pre_pan - 6) / 6
        notejson['pan'] = pan
        notelist.append(notejson)
    return notelist

def parsetrack(notelist, trackid, orginst, orgtypeforname):
    trackdata_json = {}
    if notelist != []:
        trackdata_json = {}
        trackdata_json['type'] = "instrument"
        instrumentdata_json = {}
        instrumentdata_json['plugin'] = "orgyana"
        plugindata_json = {}
        plugindata_json['instrument'] = orginst
        trackdata_json['instrumentdata'] = instrumentdata_json
        trackdata_json['plugindata'] = plugindata_json
        trackdata_json['notelist'] = notelist
        if orgtypeforname == 1:
            trackdata_json['name'] = trackid + ' (' + orgdrumname[orginst] + ')'
        else:
            trackdata_json['name'] = trackid + ' (' + str(orginst) + ')'
        trackdata_json['vol'] = 0.2
        pattern = {}
        pattern['position'] = 0
        pattern['notelist'] = notelist
        trackdata_json['placements'] = [pattern]
        tracklist.append(trackdata_json)
    return trackdata_json

class input_xm(plugin_input.base):
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

    def parse(self, input_file):
        global notetime
        global notesizedivision
        global tracklist
        global orgdrumname
        notesizedivision = 1
        orgfile = open(input_file, 'rb')
        tempomultiply = 1
        file_header_orgtype = orgfile.read(6)
        tempo = (int.from_bytes(orgfile.read(2), "little"))* int(tempomultiply)
        print("Input-OrgMaker | Organya Type: " + str(file_header_orgtype))
        print("Input-OrgMaker | Tempo: " + str(tempo))
        Steps_Per_Bar = int.from_bytes(orgfile.read(1), "little")
        print("Input-OrgMaker | Steps Per Bar: " + str(Steps_Per_Bar))
        Beats_per_Step = int.from_bytes(orgfile.read(1), "little")
        print("Input-OrgMaker | Beats per Step: " + str(Beats_per_Step))
        notetime = Steps_Per_Bar / Beats_per_Step
        loop_beginning = int.from_bytes(orgfile.read(4), "little")
        print("Input-OrgMaker | Loop Beginning: " + str(loop_beginning))
        loop_end = int.from_bytes(orgfile.read(4), "little")
        print("Input-OrgMaker | Loop End: " + str(loop_end))
        org_instrumentinfotable = []
        orgdrumname = ["Bass 1", "Bass 2", "Snare 1", "Snare 2", "Tom 1", "Hi-Hat Close", "Hi-Hat Open", "Crash", "Perc 1", "Perc 2", "Bass 3", "Tom 2"]
        orginsttable = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for x in range(16):
            pitch = int.from_bytes(orgfile.read(2), "little")
            Instrument = int.from_bytes(orgfile.read(1), "little")
            orginsttable[x-1] = Instrument
            disable_sustaining_notes = int.from_bytes(orgfile.read(1), "little")
            number_of_notes = int.from_bytes(orgfile.read(2), "little")
            print("Input-OrgMaker | pitch = " + str(pitch), end=" ")
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
        json_loop = {}
        json_loop['enabled'] = int(1)
        json_loop['start'] = loop_beginning/16
        json_loop['end'] = loop_end/16
        json_root = {}
        json_root['mastervol'] = 1.0
        json_root['timesig_numerator'] = 4
        json_root['timesig_denominator'] = 4
        json_root['bpm'] = tempo
        json_root['tracks'] = tracklist
        json_root['loop'] = json_loop
        json_root['convprojtype'] = 'single'
        return json.dumps(json_root)
