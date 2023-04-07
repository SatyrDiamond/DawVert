# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import format_caustic
from functions import data_bytes
from functions import folder_samples
from functions import audio_wav
from functions import placements
from functions import tracks
from functions import auto
import plugin_input
import os.path
import json
import struct

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

def twopoints2cvpjpoints(twopoints):
    cvpj_points = []
    for twopoint in twopoints:
        cvpj_points.append({"position": twopoint[0]*4, "value": twopoint[1]})
    return [{'position': 0, 'duration': (twopoints[-1][0]*4), 'points': cvpj_points}]

class input_cvpj_r(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'caustic'
    def getname(self): return 'Caustic 3'
    def gettype(self): return 'ri'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': False,
        'placement_warp': False,
        'no_placements': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        CausticData = format_caustic.deconstruct_main(input_file)
        machines = CausticData['Machines']
        SEQN = CausticData['SEQN']
        SEQN_tempo = CausticData['SEQN_tempo']
        EFFX = CausticData['EFFX']
        AUTO_data = CausticData['AUTO']

        cvpj_l = {}
        
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        machnum = 0
        plnum = 0
        for machine in machines:
            machnum += 1
            plnum += 1

            machid = str(machnum)

            if 'name' in machine: cvpj_trackname = machine['name']
            else: cvpj_trackname = caustic_instnames[machine['id']]

            cvpj_notelistindex = {}

            if machine['id'] != 'NULL' and machine['id'] != 'MDLR':
                if 'patterns' in machine:
                    patterns = machine['patterns']
                    for pattern in patterns:
                        patid = pattern
                        causticpattern = patterns[pattern]
                        notelist = parse_notelist(causticpattern, machid)
                        if notelist != []: 
                            cvpj_notelistindex[patid] = {}
                            cvpj_notelistindex[patid]['name'] = pattern
                            cvpj_notelistindex[patid]['notelist'] = notelist

            cvpj_instdata = {}
            cvpj_instdata['plugindata'] = {}
            plugindata = cvpj_instdata['plugindata']

            cvpj_instdata['pluginautoid'] = 'machine'+machid

            # -------------------------------- PCMSynth --------------------------------
            if machine['id'] == 'PCMS':
                middlenote = 0
                cvpj_instdata['usemasterpitch'] = 1
                if len(machine['regions']) == 1:
                    singlewav = machine['regions'][0]
                    if singlewav['key_lo'] == 24 and singlewav['key_hi'] == 108: isMultiSampler = False
                    else: isMultiSampler = True
                else: isMultiSampler = True

                if not isMultiSampler:
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
                    cvpj_instdata['plugindata']['point_value_type'] = "samples"
                    loopmode_cvpj(cvpj_instdata['plugindata'], singlewav)
                else:
                    cvpj_instdata['plugin'] = 'sampler-multi'
                    cvpj_instdata['plugindata']['point_value_type'] = "samples"
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

                middlenote += int(pcms_c[1]*12)
                middlenote += int(pcms_c[2])

                cvpj_instdata['pitch'] = pcms_c[3]
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
                cvpj_instdata['plugin'] = 'native-caustic'
                cvpj_instdata['plugindata'] = {}
                cvpj_instdata['plugindata']['type'] = machine['id']
                cvpj_instdata['plugindata']['data'] = {}
                if 'controls' in machine: 
                    cvpj_instdata['plugindata']['data'] = machine['controls']
                if 'customwaveform1' in machine: 
                    cvpj_instdata['plugindata']['data']['customwaveform1'] = struct.unpack("<"+("i"*330), machine['customwaveform1'])
                if 'customwaveform2' in machine: 
                    cvpj_instdata['plugindata']['data']['customwaveform2'] = struct.unpack("<"+("i"*330), machine['customwaveform2'])

            tracks.ri_addtrack_inst(cvpj_l, 'MACH'+machid, cvpj_notelistindex, cvpj_instdata)
            tracks.r_addtrack_data(cvpj_l, 'MACH'+machid, cvpj_trackname, caustic_instcolors[machine['id']], None, None)

        t_track_placements = {}

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
                pl_placement['fromindex'] = SEQNe_patlet+str(SEQNe_patnum+1)
                if str(SEQNe_mach) not in t_track_placements: t_track_placements[str(SEQNe_mach)] = []
                t_track_placements[str(SEQNe_mach)].append(pl_placement)

        for t_track_placement in t_track_placements:
            tracks.r_addtrackpl(cvpj_l, t_track_placement, t_track_placements[t_track_placement])

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
        automation_plugin = {}
        automation_track = {}

        #'machine'+machid

        for machnum in range(14):
            automation_plugin['machine'+str(machnum+1)] = {}
            automation_track['MACH'+str(machnum+1)] = {}
            machautodata = automation_plugin['machine'+str(machnum+1)]
            for autoname in AUTO_data['MACH_'+str(machnum+1)]:
                machautodata[str(autoname)] = twopoints2cvpjpoints(AUTO_data['MACH_'+str(machnum+1)][autoname])
        
        for machnum in range(7):
            if machnum in AUTO_data['MIXER_1']: 
                automation_track['MACH'+str(machnum+1)]['vol'] = twopoints2cvpjpoints(AUTO_data['MIXER_1'][machnum])
            if machnum+64 in AUTO_data['MIXER_1']: 
                automation_track['MACH'+str(machnum+1)]['pan'] = auto.multiply( twopoints2cvpjpoints(AUTO_data['MIXER_1'][machnum+64]), -0.5, 2)
            if machnum in AUTO_data['MIXER_2']: 
                automation_track['MACH'+str(machnum+8)]['vol'] = twopoints2cvpjpoints(AUTO_data['MIXER_2'][machnum])
            if machnum+64 in AUTO_data['MIXER_2']: 
                automation_track['MACH'+str(machnum+8)]['pan'] = auto.multiply( twopoints2cvpjpoints(AUTO_data['MIXER_2'][machnum+64]), -0.5, 2)

        #for fxnum in EFFX:
        #    for slotnum in EFFX[fxnum]:
        #        print(fxnum, slotnum, EFFX[fxnum][slotnum])

        'machine'+machid

        cvpj_l['do_addwrap'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['automation'] = {}
        cvpj_l['automation']['main'] = automation_main
        cvpj_l['automation']['plugin'] = automation_plugin
        cvpj_l['automation']['track'] = automation_track

        cvpj_l['bpm'] = CausticData['Tempo']
        cvpj_l['timesig_numerator'] = CausticData['Numerator']
        cvpj_l['timesig_denominator'] = 4
        return json.dumps(cvpj_l)

