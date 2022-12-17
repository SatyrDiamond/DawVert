# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

caustic_instnames = {}
caustic_instnames['NULL'] = 'None'
caustic_instnames['SSYN'] = 'SubSynth'
caustic_instnames['PCMS'] = 'PCMSynth'
caustic_instnames['BLNE'] = 'BassLine'
caustic_instnames['BBOX'] = 'BeatBox'
caustic_instnames['PADS'] = 'PadSynth'
caustic_instnames['8SYN'] = '8BitSynth'
caustic_instnames['MDLR'] = 'Modular'
caustic_instnames['ORGN'] = 'Organ'
caustic_instnames['VCDR'] = 'Vocoder'
caustic_instnames['FMSN'] = 'FMSynth'
caustic_instnames['KSSN'] = 'KSSynth'
caustic_instnames['SAWS'] = 'SawSynth'

caustic_instcolors = {}
caustic_instcolors['NULL'] = [0.10, 0.10, 0.10]
caustic_instcolors['SSYN'] = [0.79, 0.82, 0.91]
caustic_instcolors['PCMS'] = [0.78, 0.84, 0.65]
caustic_instcolors['BLNE'] = [0.99, 0.99, 0.99]
caustic_instcolors['BBOX'] = [0.66, 0.51, 0.36]
caustic_instcolors['PADS'] = [0.99, 0.99, 0.69]
caustic_instcolors['8SYN'] = [0.82, 0.78, 0.63]
caustic_instcolors['MDLR'] = [0.45, 0.45, 0.45]
caustic_instcolors['ORGN'] = [0.68, 0.30, 0.03]
caustic_instcolors['VCDR'] = [0.74, 0.35, 0.35]
caustic_instcolors['FMSN'] = [0.29, 0.78, 0.76]
caustic_instcolors['KSSN'] = [0.55, 0.57, 0.44]
caustic_instcolors['SAWS'] = [0.99, 0.60, 0.25]

patletters = ['A','B','C','D']

from functions import format_caustic
from functions import data_bytes
import plugin_input
import json

def parse_notelist(causticpattern, machid): 
    notelist = []
    causticnotes = causticpattern['notes']
    for causticnote in causticnotes:
        if causticnote[1] != 4294967295:
            notedata = {}
            notedata['position'] = causticnote[2]*4
            key = causticnote[6]
            if key > 65535: key -= 65535
            notedata['key'] = key-60
            notedata['duration'] = causticnote[3]*4
            notedata['vol'] = causticnote[13]
            notedata['instrument'] = machid
            if key != 0: notelist.append(notedata)
    return notelist

class input_cvpj_r(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'caustic'
    def getname(self): return 'Caustic 3'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        CausticData = format_caustic.deconstruct_main(input_file)
        machines = CausticData['Machines']
        SEQN = CausticData['SEQN']

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}
        cvpj_l_fxrack = {}

        machnum = 0
        plnum = 0
        for machine in machines:
            machnum += 1
            plnum += 1

            machid = 'Mach'+str(machnum)

            if machine['id'] != 'NULL' and machine['id'] != 'MDLR':
                patterns = machine['patterns']
                for pattern in patterns:
                    patid = 'Caustic_'+machid+'_'+pattern
                    causticpattern = patterns[pattern]
                    notelist = parse_notelist(causticpattern, machid)
                    if notelist != []: 
                        cvpj_l_notelistindex[patid] = {}
                        cvpj_l_notelistindex[patid]['name'] = machid+' '+pattern
                        cvpj_l_notelistindex[patid]['color'] = caustic_instcolors[machine['id']]
                        cvpj_l_notelistindex[patid]['notelist'] = notelist

            cvpj_inst = {}
            cvpj_inst["enabled"] = 1
            cvpj_inst["instdata"] = {}
            cvpj_instdata = cvpj_inst["instdata"]
            cvpj_instdata['plugin'] = 'none'
            cvpj_instdata['usemasterpitch'] = 1
            cvpj_inst["name"] = caustic_instnames[machine['id']]
            cvpj_inst["color"] = caustic_instcolors[machine['id']]
            cvpj_inst["pan"] = 0.0
            cvpj_inst["vol"] = 1.0
            cvpj_l_instruments[machid] = cvpj_inst
            cvpj_l_instrumentsorder.append(machid)
            cvpj_l_fxrack[str(machnum)] = {}
            cvpj_l_fxrack[str(machnum)]["name"] = caustic_instnames[machine['id']]
            cvpj_l_playlist[str(plnum)] = {}
            cvpj_l_playlist[str(plnum)]["name"] = caustic_instnames[machine['id']]
            cvpj_l_playlist[str(plnum)]["color"] = caustic_instcolors[machine['id']]
            cvpj_l_playlist[str(plnum)]["placements"] = []

        for SEQNe in SEQN:
            #print(SEQNe)
            SEQNe_mach = SEQNe[0]+1
            SEQNe_type = SEQNe[1]
            SEQNe_pos = SEQNe[2]*4
            SEQNe_len = SEQNe[3]*4
            SEQNe_patnum = SEQNe[6]

            hundreds = int(SEQNe_patnum/100)
            SEQNe_patnum -= hundreds*100
            SEQNe_patlet = patletters[hundreds]

            if SEQNe_type == 2:
                pl_placement = {}
                pl_placement['position'] = SEQNe_pos
                pl_placement['duration'] = SEQNe_len
                pl_placement['type'] = 'instruments'
                pl_placement['fromindex'] = 'Caustic_Mach'+str(SEQNe_mach)+'_'+SEQNe_patlet+str(SEQNe_patnum+1)
                cvpj_l_playlist[str(SEQNe_mach)]["placements"].append(pl_placement)



        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = 140
        return json.dumps(cvpj_l)

