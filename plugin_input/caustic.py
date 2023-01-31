# SPDX-FileCopyrightText: 2023 SatyrDiamond
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

caustic_fxtype = {}
caustic_fxtype[0] = 'Delay'
caustic_fxtype[1] = 'Reverb'
caustic_fxtype[2] = 'Distortion'
caustic_fxtype[3] = 'Compresser'
caustic_fxtype[4] = 'Bitcrush'
caustic_fxtype[5] = 'Flanger'
caustic_fxtype[6] = 'Phaser'
caustic_fxtype[7] = 'Chorus'
caustic_fxtype[8] = 'AutoWah'
caustic_fxtype[9] = 'Param EQ'
caustic_fxtype[10] = 'Limiter'
caustic_fxtype[11] = 'VInylSim'
caustic_fxtype[12] = 'Comb'
caustic_fxtype[14] = 'Cab Sim'
caustic_fxtype[16] = 'StaticFlanger'
caustic_fxtype[17] = 'Filter'
caustic_fxtype[18] = 'Octaver'
caustic_fxtype[19] = 'Vibrato'
caustic_fxtype[20] = 'Tremolo'
caustic_fxtype[21] = 'AutoPan'

patletters = ['A','B','C','D']

from functions import format_caustic
from functions import data_bytes
from functions import folder_samples
from functions import audio_wav
import plugin_input
import os.path
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

def loopmode_cvpj(cvpjdata, wavdata): 
    lm = wavdata['mode']
    cvpjdata['end'] = wavdata['end']
    if lm == 0 or lm == 1 or lm == 2 or lm == 3: cvpjdata['start'] = wavdata['start']
    if lm == 4 or lm == 5: cvpjdata['start'] = 0

    if lm == 0: cvpjdata['trigger'] = 'normal'
    else: cvpjdata['trigger'] = 'oneshot'

    if lm == 2 or lm == 3 or lm == 4 or lm == 5:
        cvpjdata['loop']['enabled'] = 1
        cvpjdata['loop']['points'] = [wavdata['start'], wavdata['end']]
    if lm == 0 or lm == 1: cvpjdata['loop']['enabled'] = 0
    if lm == 2 or lm == 4: cvpjdata['loop']['mode'] = "normal"
    if lm == 3 or lm == 5: cvpjdata['loop']['mode'] = "pingpong"

class input_cvpj_r(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'caustic'
    def getname(self): return 'Caustic 3'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        CausticData = format_caustic.deconstruct_main(input_file)
        machines = CausticData['Machines']
        SEQN = CausticData['SEQN']
        SEQN_tempo = CausticData['SEQN_tempo']
        EFFX = CausticData['EFFX']

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}

        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        machnum = 0
        plnum = 0
        for machine in machines:
            machnum += 1
            plnum += 1

            machid = 'Mach'+str(machnum)

            if machine['id'] != 'NULL' and machine['id'] != 'MDLR':
                if 'patterns' in machine:
                    patterns = machine['patterns']
                    for pattern in patterns:
                        patid = 'Caustic_'+machid+'_'+pattern
                        causticpattern = patterns[pattern]
                        notelist = parse_notelist(causticpattern, machid)
                        if notelist != []: 
                            cvpj_l_notelistindex[patid] = {}
                            cvpj_l_notelistindex[patid]['name'] = pattern+' ('+machid+')'
                            cvpj_l_notelistindex[patid]['color'] = caustic_instcolors[machine['id']]
                            cvpj_l_notelistindex[patid]['notelist'] = notelist

            cvpj_inst = {}
            cvpj_inst["enabled"] = 1
            cvpj_inst["instdata"] = {}
            cvpj_instdata = cvpj_inst["instdata"]
            if 'name' in machine: cvpj_inst["name"] = machine['name']
            else: cvpj_inst["name"] = caustic_instnames[machine['id']]
            cvpj_inst["color"] = caustic_instcolors[machine['id']]
            cvpj_inst["pan"] = 0.0
            cvpj_inst["vol"] = 1.0

            cvpj_instdata['plugindata'] = {}
            plugindata = cvpj_instdata['plugindata']

            # -------------------------------- PCMSynth --------------------------------
            if machine['id'] == 'PCMS':
                middlenote = 0
                cvpj_instdata['usemasterpitch'] = 1
                if len(machine['regions']) == 1:
                    singlewav = machine['regions'][0]
                    if singlewav['key_lo'] == 24 and singlewav['key_hi'] == 108: isMultiSampler = False
                    else: isMultiSampler = True
                else: isMultiSampler = True

                if isMultiSampler == False:
                    singlewav = machine['regions'][0]
                    cvpj_instdata['plugin'] = 'sampler'
                    wave_path = samplefolder + machid + '_PCMSynth_0.wav'
                    loopdata = None
                    if singlewav['mode'] != 0 and singlewav['mode'] != 1: loopdata = {'loop':[singlewav['start'], singlewav['end']]}
                    if singlewav['samp_ch'] != 0:
                        audio_wav.generate(wave_path, singlewav['samp_data'], singlewav['samp_ch'], singlewav['samp_hz'], 16, loopdata)

                    middlenote += singlewav['key_root']-60

                    cvpj_instdata['plugindata']['file'] = wave_path
                    cvpj_instdata['plugindata']['length'] = singlewav['samp_len']
                    cvpj_instdata['plugindata']['loop'] = {}
                    loopmode_cvpj(cvpj_instdata['plugindata'], singlewav)
                else:
                    cvpj_instdata['plugin'] = 'sampler-multi'
                    cvpj_instdata['plugindata']['regions'] = []
                    samplecount = 0
                    for singlewav in machine['regions']:
                        loopdata = None
                        if singlewav['mode'] != 0 and singlewav['mode'] != 1: loopdata = {'loop':[singlewav['start'], singlewav['end']]}
                        wave_path = samplefolder + machid + '_PCMSynth_'+str(samplecount)+'.wav'
                        audio_wav.generate(wave_path, singlewav['samp_data'], singlewav['samp_ch'], singlewav['samp_hz'], 16, loopdata)
                        regionparams = {}
                        regionparams['r_key'] = [singlewav['key_lo']-60, singlewav['key_hi']-60]
                        regionparams['middlenote'] = singlewav['key_root']-60
                        regionparams['volume'] = singlewav['volume']
                        regionparams['pan'] = (singlewav['pan']-0.5)*2
                        regionparams['file'] = wave_path
                        regionparams['loop'] = {}
                        loopmode_cvpj(regionparams, singlewav)
                        cvpj_instdata['plugindata']['regions'].append(regionparams)
                        samplecount += 1

                pcms_c = machine['controls']

                #for printpart in pcms_c:
                #    print(pcms_c[printpart])

                middlenote += int(pcms_c[1]*12)
                middlenote += int(pcms_c[2])

                #print(middlenote)

                cvpj_inst["instdata"]['notefx'] = {}
                cvpj_inst["instdata"]['notefx']['pitch'] = {}
                cvpj_inst["instdata"]['notefx']['pitch']['semitones'] = middlenote
                cvpj_inst['instdata']['pitch'] = pcms_c[3]

                plugindata['asdrlfo'] = {}
                plugindata['asdrlfo']['volume'] = {}
                plugindata['asdrlfo']['volume']['envelope'] = {}
                plugindata['asdrlfo']['volume']['envelope']['attack'] = pcms_c[5]
                plugindata['asdrlfo']['volume']['envelope']['hold'] = 0
                plugindata['asdrlfo']['volume']['envelope']['decay'] = pcms_c[6]
                plugindata['asdrlfo']['volume']['envelope']['sustain'] = pcms_c[7]
                plugindata['asdrlfo']['volume']['envelope']['release'] = pcms_c[8]
                plugindata['asdrlfo']['volume']['envelope']['amount'] = 1

            # -------------------------------- BeatBox --------------------------------
            elif machine['id'] == 'BBOX':
                cvpj_instdata['plugin'] = 'sampler-multi'
                cvpj_instdata['usemasterpitch'] = 0
                plugindata['regions'] = []
                bbox_samples = machine['samples']
                samplecount = 0
                bbox_key = -12
                for bbox_sample in bbox_samples:
                    #print(bbox_sample)
                    wave_path = samplefolder + machid + '_BeatBox_'+str(samplecount)+'.wav'
                    if bbox_sample['chan'] != 0 and bbox_sample['hz'] != 0: 
                        audio_wav.generate(wave_path, bbox_sample['data'], bbox_sample['chan'], bbox_sample['hz'], 16, None)
                    regionparams = {}
                    regionparams['r_key'] = [bbox_key, bbox_key]
                    regionparams['middlenote'] = bbox_key
                    regionparams['file'] = wave_path
                    regionparams['start'] = 0
                    regionparams['end'] = bbox_sample['len']
                    regionparams['trigger'] = 'oneshot'
                    regionparams['loop'] = {}
                    regionparams['loop']['enabled'] = 0
                    plugindata['regions'].append(regionparams)
                    samplecount += 1
                    bbox_key += 1

            else:
                cvpj_instdata['plugin'] = 'none'

            cvpj_l_instruments[machid] = cvpj_inst
            cvpj_l_instrumentsorder.append(machid)
            cvpj_l_playlist[str(plnum)] = {}
            cvpj_l_playlist[str(plnum)]["name"] = caustic_instnames[machine['id']]
            cvpj_l_playlist[str(plnum)]["color"] = caustic_instcolors[machine['id']]
            cvpj_l_playlist[str(plnum)]["placements"] = []

        for SEQNe in SEQN:
            SEQNe_mach = SEQNe[0]+1
            SEQNe_type = SEQNe[1]
            SEQNe_pos = SEQNe[2]*4
            SEQNe_len = SEQNe[3]*4
            SEQNe_patnum = SEQNe[6]

            hundreds = int(SEQNe_patnum/100)
            SEQNe_patnum -= hundreds*100

            if SEQNe_type == 2:
                SEQNe_patlet = patletters[hundreds]
                pl_placement = {}
                pl_placement['position'] = SEQNe_pos
                pl_placement['duration'] = SEQNe_len
                pl_placement['type'] = 'instruments'
                pl_placement['fromindex'] = 'Caustic_Mach'+str(SEQNe_mach)+'_'+SEQNe_patlet+str(SEQNe_patnum+1)
                cvpj_l_playlist[str(SEQNe_mach)]["placements"].append(pl_placement)

        tempo_placement = {"position": 0}

        tempo_placement_dur = 0
        tempo_points = []
        for point in SEQN_tempo:
            if tempo_placement_dur > point[0]*4: tempo_placement_dur = point[0]*4
            tempo_points.append({"position": point[0]*4, "value": point[1]})
        tempo_placement['duration'] = tempo_placement_dur
        tempo_placement['points'] = tempo_points

        automation_main = {}
        automation_main['bpm'] = [tempo_placement]

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['automation'] = {}
        cvpj_l['automation']['main'] = automation_main
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = CausticData['Tempo']
        cvpj_l['timesig_numerator'] = CausticData['Numerator']
        cvpj_l['timesig_denominator'] = 4
        return json.dumps(cvpj_l)

