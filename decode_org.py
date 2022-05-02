import _func_instrument
from configparser import ConfigParser
import os
import json

def createfolder(filepath):
    isExist = os.path.exists(filepath)
    if not isExist:
        os.makedirs(filepath)

def createfile(filepath):
    isExist = os.path.exists(filepath)
    if not isExist:
        open(filepath, 'a').close()

convertedout = 'orgout'

orgfile = open('GRAVITY', 'rb')

file_header_orgtype = orgfile.read(6)
orgtype = 0
if orgtype == b'Org-02':
    orgtype = 2
    print("Organya Type: 2")
elif orgtype == b'Org-03':
    orgtype = 3
    print("Organya Type: 3")
tempo = int.from_bytes(orgfile.read(2), "little")
print("Tempo: " + str(tempo))
Steps_Per_Bar = int.from_bytes(orgfile.read(1), "little")
print("Steps Per Bar: " + str(Steps_Per_Bar))
Beats_per_Step = int.from_bytes(orgfile.read(1), "little")
print("Beats per Step: " + str(Beats_per_Step))
notetime = Steps_Per_Bar / Beats_per_Step
loop_beginning = int.from_bytes(orgfile.read(4), "little")
print("Loop Beginning: " + str(loop_beginning))
loop_end = int.from_bytes(orgfile.read(4), "little")
print("Loop End: " + str(loop_end))
org_instrumentinfotable = []

for x in range(16):
    pitch = int.from_bytes(orgfile.read(2), "little")
    Instrument = int.from_bytes(orgfile.read(1), "little")
    disable_sustaining_notes = int.from_bytes(orgfile.read(1), "little")
    number_of_notes = int.from_bytes(orgfile.read(2), "little")
    print("pitch = " + str(pitch), end=" ")
    print("| Instrument = " + str(Instrument), end=" ")
    print("| disable_sustaining_notes = " + str(disable_sustaining_notes), end=" ")
    print("| number_of_notes = " + str(number_of_notes))
    org_instrumentinfotable.append([pitch,Instrument,disable_sustaining_notes,number_of_notes])
def parse_orgtrack(instrumentinfotable_input, trackid):
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

orgnotestable_note1 = parse_orgtrack(org_instrumentinfotable, 0)
orgnotestable_note2 = parse_orgtrack(org_instrumentinfotable, 1)
orgnotestable_note3 = parse_orgtrack(org_instrumentinfotable, 2)
orgnotestable_note4 = parse_orgtrack(org_instrumentinfotable, 3)
orgnotestable_note5 = parse_orgtrack(org_instrumentinfotable, 4)
orgnotestable_note6 = parse_orgtrack(org_instrumentinfotable, 5)
orgnotestable_note7 = parse_orgtrack(org_instrumentinfotable, 6)
orgnotestable_note8 = parse_orgtrack(org_instrumentinfotable, 7)
orgnotestable_perc1 = parse_orgtrack(org_instrumentinfotable, 8)
orgnotestable_perc2 = parse_orgtrack(org_instrumentinfotable, 9)
orgnotestable_perc3 = parse_orgtrack(org_instrumentinfotable, 10)
orgnotestable_perc4 = parse_orgtrack(org_instrumentinfotable, 11)
orgnotestable_perc5 = parse_orgtrack(org_instrumentinfotable, 12)
orgnotestable_perc6 = parse_orgtrack(org_instrumentinfotable, 13)
orgnotestable_perc7 = parse_orgtrack(org_instrumentinfotable, 14)
orgnotestable_perc8 = parse_orgtrack(org_instrumentinfotable, 15)


def orgnl2outnl(orgnotelist):
    notelist = []
    for currentnote in range(len(orgnotelist)):
        orgnote = orgnotelist[currentnote]
        position = (orgnote[0] / 4) * notetime

        pre_note = orgnote[1]
        if 0 <= pre_note <= 95:
            note = pre_note
        duration = (orgnote[2] / 4) * notetime
        pre_volume = orgnote[3]
        if 0 <= pre_volume <= 254:
            volume = pre_volume / 254
        pre_pan = orgnote[4]
        if 0 <= pre_pan <= 12:
            pan = (pre_pan - 6) / 6
        notelist.append([position, duration, note, volume, pan, {}])
    return notelist

def parsetrack(notelist, trackid):
    trackdata_json = {}
    if notelist != []:
        trackdata_json = _func_instrument.init_instrument_trackdataCONVPROJ()
        trackdata_json['notelist'] = _func_instrument.notelistTABLE_to_notelistCONVPROJ(notelist)
        trackdata_json['name'] = trackid
        tracklist.append(trackdata_json)
    return trackdata_json

tracklist = []
parsetrack(orgnl2outnl(orgnotestable_note1), 'note1')
parsetrack(orgnl2outnl(orgnotestable_note2), 'note2')
parsetrack(orgnl2outnl(orgnotestable_note3), 'note3')
parsetrack(orgnl2outnl(orgnotestable_note4), 'note4')
parsetrack(orgnl2outnl(orgnotestable_note5), 'note5')
parsetrack(orgnl2outnl(orgnotestable_note6), 'note6')
parsetrack(orgnl2outnl(orgnotestable_note7), 'note7')
parsetrack(orgnl2outnl(orgnotestable_note8), 'note8')
parsetrack(orgnl2outnl(orgnotestable_perc1), 'perc1')
parsetrack(orgnl2outnl(orgnotestable_perc2), 'perc2')
parsetrack(orgnl2outnl(orgnotestable_perc3), 'perc3')
parsetrack(orgnl2outnl(orgnotestable_perc4), 'perc4')
parsetrack(orgnl2outnl(orgnotestable_perc5), 'perc5')
parsetrack(orgnl2outnl(orgnotestable_perc6), 'perc6')
parsetrack(orgnl2outnl(orgnotestable_perc7), 'perc7')
parsetrack(orgnl2outnl(orgnotestable_perc8), 'perc8')

json_root = {}
json_root['datatype'] = 'otsn'
json_root['mastervol'] = 1.0
json_root['timesig_numerator'] = 4
json_root['timesig_denominator'] = 4
json_root['bpm'] = tempo
json_root['tracks'] = tracklist

with open('proj.conv_otsn', 'w') as outfile:
        outfile.write(json.dumps(json_root, indent=2))
