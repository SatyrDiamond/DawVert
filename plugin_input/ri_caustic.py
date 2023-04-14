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
import itertools

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
caustic_fxtype[0] = 'delay'
caustic_fxtype[1] = 'reverb'
caustic_fxtype[2] = 'distortion'
caustic_fxtype[3] = 'compresser'
caustic_fxtype[4] = 'bitcrush'
caustic_fxtype[5] = 'flanger'
caustic_fxtype[6] = 'phaser'
caustic_fxtype[7] = 'chorus'
caustic_fxtype[8] = 'auto_wah'
caustic_fxtype[9] = 'param_eq'
caustic_fxtype[10] = 'limiter'
caustic_fxtype[11] = 'vinyl_sim'
caustic_fxtype[12] = 'comb'
caustic_fxtype[14] = 'cabsim'
caustic_fxtype[16] = 'static_flanger'
caustic_fxtype[17] = 'filter'
caustic_fxtype[18] = 'octaver'
caustic_fxtype[19] = 'vibrato'
caustic_fxtype[20] = 'tremolo'
caustic_fxtype[21] = 'auto_pan'

master_idnames = {}

master_idnames[1] = ['delay', 'time']
master_idnames[2] = ['delay', 'feedback']
master_idnames[3] = ['delay', 'damping']
master_idnames[4] = ['delay', 'wet']
master_idnames[5] = ['delay', 'pan1']
master_idnames[6] = ['delay', 'pan2']
master_idnames[7] = ['delay', 'pan3']
master_idnames[8] = ['delay', 'pan4']
master_idnames[9] = ['delay', 'pan5']

master_idnames[16] = ['reverb', 'predelay']
master_idnames[17] = ['reverb', 'room_size']
master_idnames[18] = ['reverb', 'hf_damping']
master_idnames[19] = ['reverb', 'diffuse']
master_idnames[20] = ['reverb', 'dither_echoes']
master_idnames[21] = ['reverb', 'early_reflect']
master_idnames[22] = ['reverb', 'er_decay']
master_idnames[23] = ['reverb', 'stereo_delay']
master_idnames[24] = ['reverb', 'stereo_spread']
master_idnames[25] = ['reverb', 'wet']

master_idnames[30] = ['eq', 'low']
master_idnames[31] = ['eq', 'freq_lowmid']
master_idnames[32] = ['eq', 'mid']
master_idnames[33] = ['eq', 'freq_midhigh']
master_idnames[34] = ['eq', 'high']

master_idnames[35] = ['limiter', 'pre']
master_idnames[36] = ['limiter', 'attack']
master_idnames[37] = ['limiter', 'release']
master_idnames[38] = ['limiter', 'post']
master_idnames[39] = ['main', 'master']
master_idnames[40] = ['delay', 'muted']
master_idnames[41] = ['reverb', 'muted']
master_idnames[42] = ['eq', 'muted']
master_idnames[43] = ['limiter', 'muted']

patletters = ['A','B','C','D']

def parse_notelist(causticpattern, machid): 
    notelist = []
    causticnotes = causticpattern['notes']
    for causticnote in causticnotes:

        if causticnote[1] != 4294967295:
            notedata = {}
            notedata['position'] = causticnote[2]*4
            key = causticnote[6]
            notedata['key'] = key-60
            notedata['duration'] = causticnote[3]*4
            notedata['vol'] = causticnote[14]
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

def tp2cvpjp(twopoints):
    return auto.twopoints2cvpjpoints(twopoints, 4, 'normal', 0)

def make_fxslot(fx_type, fx_data, auto_id):
    fxslotdata = {}
    fxslotdata['pluginautoid'] = auto_id
    fxslotdata['slotautoid'] = auto_id
    fxslotdata['plugin'] = 'native-caustic'
    fxslotdata['plugindata'] = {}
    fxslotdata['plugindata']['name'] = fx_type
    fxslotdata['plugindata']['data'] = fx_data
    return fxslotdata

def pat_auto_place_part(pl_position, pl_duration, auto_smooth, auto_points):
    auto_curpoint = 0
    cvpj_placement_points = []
    auto_duration = int(len(auto_points))
    for _ in range((int(pl_duration)*2)-1):
        point_value = auto_points[auto_curpoint]
        if auto_smooth == 0.0: 
            cvpj_placement_points.append([auto_curpoint/2, point_value, 'instant'])
            #print(auto_curpoint/2, point_value, 'instant')
        else:
            cvpj_placement_points.append([auto_curpoint/2, point_value, 'normal'])
            #print(auto_curpoint/2, point_value, 'normal', end=' | ')
            if auto_smooth != 1.0: 
                cvpj_placement_points.append([(auto_curpoint/2)+(auto_smooth/2), point_value, 'normal'])
                #print((auto_curpoint/2)+(auto_smooth/2), point_value, 'normal')
            #else: print()
        auto_curpoint += 1
        if auto_curpoint == auto_duration: 
            auto_curpoint = 0
            cvpj_placements.append(cvpj_placement_points)
            #print(cvpj_placement_points)

    out_autopl = {}
    out_autopl['position'] = pl_position
    out_autopl['duration'] = pl_duration
    out_autopl['points'] = []

    for t_ap in cvpj_placement_points:
        out_autopl['points'].append({"position": t_ap[0], "value": t_ap[1], "type": t_ap[2]})

    return out_autopl

def pat_auto_place(pl_position, pl_duration, autodata):
    auto_smooth = autodata['smooth']
    auto_points = autodata['data']


    #print('------------- POINT START ----------------', pl_duration,'/',auto_duration)

    auto_duration = int(len(auto_points))

    print('LEN', pl_duration/(auto_duration/2), pl_duration, auto_duration/2)

    remainingloops = pl_duration

    out_autopls = []

    looppos = 0
    while remainingloops > 0:
        loopsize = min(1, remainingloops/(auto_duration/2))
        print(looppos, loopsize)
        remainingloops -= auto_duration/2
        out_autopls.append(pat_auto_place_part(pl_position+looppos, (auto_duration/2)*loopsize, auto_smooth, auto_points))
        looppos += auto_duration/2

    return out_autopls

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
        'placement_cut': True,
        'placement_warp': True,
        'no_pl_auto': False,
        'no_placements': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        CausticData = format_caustic.deconstruct_main(input_file)
        machines = CausticData['Machines']
        SEQN = CausticData['SEQN']
        SEQN_tempo = CausticData['SEQN_tempo']
        EFFX = CausticData['EFFX']
        MSTR = CausticData['MSTR']
        AUTO_data = CausticData['AUTO']

        cvpj_l = {}
        
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        mach_mixer_vol = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        mach_mixer_pan = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        mach_mixer_send_reverb = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        mach_mixer_send_delay = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        mach_mixer_eq_low = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        mach_mixer_eq_mid = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        mach_mixer_eq_high = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        mach_mixer_width = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        mach_mixer_mute = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        mach_mixer_solo = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        for mixerpartnum in range(2):
            if mixerpartnum in CausticData['MIXR']:
                CausticMixerDataPart = CausticData['MIXR'][mixerpartnum]

                for paramnum in range(7): 
                    paramnumid = paramnum+(mixerpartnum*7)
                    mach_mixer_vol[paramnumid] = CausticMixerDataPart[paramnum]
                    mach_mixer_pan[paramnumid] = (CausticMixerDataPart[paramnum+64]-0.5)*2
                    mach_mixer_width[paramnumid] = CausticMixerDataPart[paramnum+72]
                    mach_mixer_send_delay[paramnumid] = CausticMixerDataPart[(paramnum*2)+8]
                    mach_mixer_send_reverb[paramnumid] = CausticMixerDataPart[(paramnum*2)+9]
                    mach_mixer_eq_low[paramnumid] = CausticMixerDataPart[paramnum+24]
                    mach_mixer_eq_mid[paramnumid] = CausticMixerDataPart[paramnum+32]
                    mach_mixer_eq_high[paramnumid] = CausticMixerDataPart[paramnum+40]
                    mach_mixer_mute[paramnumid] = CausticMixerDataPart['solomute'][paramnum*2]
                    mach_mixer_solo[paramnumid] = CausticMixerDataPart['solomute'][(paramnum*2)+1]

        machnum = 0
        plnum = 0
        for machine in machines:
            machnum += 1
            plnum += 1

            machid = str(machnum)

            if 'name' in machine: cvpj_trackname = machine['name']
            else: cvpj_trackname = caustic_instnames[machine['id']]

            cvpj_notelistindex = {}

            if machine['id'] != 'NULL':
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
            elif machine['id'] == 'NULL':
                cvpj_instdata['plugin'] = 'none'
                cvpj_instdata['plugindata'] = {}
            else:
                cvpj_instdata['plugin'] = 'native-caustic'
                cvpj_instdata['plugindata'] = {}
                cvpj_instdata['plugindata']['type'] = machine['id']
                cvpj_instdata['plugindata']['data'] = {}
                if 'controls' in machine: cvpj_instdata['plugindata']['data'] = machine['controls']
                if 'customwaveform1' in machine: cvpj_instdata['plugindata']['data']['customwaveform1'] = struct.unpack("<"+("i"*330), machine['customwaveform1'])
                if 'customwaveform2' in machine: cvpj_instdata['plugindata']['data']['customwaveform2'] = struct.unpack("<"+("i"*330), machine['customwaveform2'])

            tracks.ri_create_inst(cvpj_l, 'MACH'+machid, cvpj_notelistindex, cvpj_instdata)
            tracks.r_basicdata(cvpj_l, 'MACH'+machid, cvpj_trackname, caustic_instcolors[machine['id']], mach_mixer_vol[machnum-1], mach_mixer_pan[machnum-1])
            tracks.r_param(cvpj_l, 'MACH'+machid, 'enabled', int(not bool(mach_mixer_mute[machnum-1])))
            tracks.r_param(cvpj_l, 'MACH'+machid, 'solo', mach_mixer_solo[machnum-1])

            cvpj_fxchaindata = []

            if machnum in CausticData['EFFX']:
                CausticFXData = CausticData['EFFX'][machnum]
                for slotnum in CausticFXData:
                    if CausticFXData[slotnum] != {}: 
                        slot_fxslotdata = CausticFXData[slotnum]['controls']
                        cvpj_fxslot = make_fxslot(
                                caustic_fxtype[CausticFXData[slotnum]['type']], 
                                slot_fxslotdata, 
                                'machine'+str(machnum)+'_slot'+str(slotnum))
                        cvpj_fxslot['enabled'] = int(not int(slot_fxslotdata[5]))
                        cvpj_fxchaindata.append(cvpj_fxslot)

            slot_mixereqfxslotdata = {}
            slot_mixereqfxslotdata['bass'] = mach_mixer_eq_low[machnum-1]
            slot_mixereqfxslotdata['mid'] = mach_mixer_eq_mid[machnum-1]
            slot_mixereqfxslotdata['high'] = mach_mixer_eq_high[machnum-1]

            cvpj_fxchaindata.append(make_fxslot('mixer_eq', slot_mixereqfxslotdata, 'machine'+machid+'_eq'))
            cvpj_fxchaindata.append(make_fxslot('width', {'width': mach_mixer_width[machnum-1]}, 'machine'+machid+'_width'))

            tracks.r_fx_audio(cvpj_l, 'MACH'+machid, cvpj_fxchaindata)


        t_track_placements = {}

        for SEQNe in SEQN:
            SEQNe_mach = SEQNe[0]+1
            SEQNe_type = SEQNe[1]
            SEQNe_pos = SEQNe[2]*4
            SEQNe_len = SEQNe[3]*4
            SEQNe_patnum = SEQNe[6]

            hundreds = int(SEQNe_patnum/100)
            SEQNe_patnum -= hundreds*100

            SEQNe_patlet = patletters[hundreds]
            t_patid = SEQNe_patlet+str(SEQNe_patnum+1)

            if 'patterns' in machines[SEQNe[0]]:
                patmeasures = machines[SEQNe[0]]['patterns'][t_patid]['measures']*16
            else:
                patmeasures = 16

            if SEQNe_type == 2:
                pl_placement = {}
                pl_placement['position'] = SEQNe_pos
                pl_placement['duration'] = SEQNe_len
                if patmeasures != 0:
                    pl_placement['cut'] = {'type': 'warp', 'start': 0, 'loopstart': 0, 'loopend': patmeasures}
                pl_placement['fromindex'] = t_patid
                if str(SEQNe_mach) not in t_track_placements: t_track_placements[str(SEQNe_mach)] = []
                t_track_placements[str(SEQNe_mach)].append(pl_placement)

                if 'patterns' in machines[SEQNe[0]]:
                    autodata = machines[SEQNe[0]]['patterns'][t_patid]['auto']

                    for autoid in autodata:
                        single_patautodata = autodata[autoid]
                        ctrlpatautopl = pat_auto_place(SEQNe_pos, SEQNe_len, single_patautodata)
                        for s_apl in ctrlpatautopl:
                            tracks.a_add_auto_pl(cvpj_l, 'plugin', 'machine'+str(SEQNe_mach), str(autoid), s_apl)


        for t_track_placement in t_track_placements:
            tracks.r_pl_notes(cvpj_l, 'MACH'+str(t_track_placement), t_track_placements[t_track_placement])

        tempo_placement = {"position": 0}

        tempo_placement_dur = 0
        tempo_points = []
        for point in SEQN_tempo:
            if tempo_placement_dur > point[0]*4: tempo_placement_dur = point[0]*4
            tempo_points.append({"position": point[0]*4, "value": point[1]})
        tempo_placement['duration'] = tempo_placement_dur
        tempo_placement['points'] = tempo_points

        tracks.a_add_auto_pl(cvpj_l, 'main', None, 'bpm', [tempo_placement])

        #'machine'+machid

        for machnum in range(14):
            for autoname in AUTO_data['MACH_'+str(machnum+1)]:
                tracks.a_add_auto_pl(cvpj_l, 'plugin', 'machine'+str(machnum+1), str(autoname), tp2cvpjp(AUTO_data['MACH_'+str(machnum+1)][autoname]))

        for mixernum in range(2):
            mixerid = 'MIXER_'+str(mixernum+1)
            for machnum in range(7):
                auto_machid = machnum+1+(mixernum*7)
                if machnum in AUTO_data[mixerid]: tracks.a_add_auto_pl(cvpj_l, 'track', 'MACH'+str(auto_machid), 'vol', tp2cvpjp(AUTO_data[mixerid][machnum]))
                if machnum+24 in AUTO_data[mixerid]: tracks.a_add_auto_pl(cvpj_l, 'plugin', 'machine'+str(auto_machid)+'_eq', 'bass', tp2cvpjp(AUTO_data[mixerid][machnum+24]))
                if machnum+32 in AUTO_data[mixerid]: tracks.a_add_auto_pl(cvpj_l, 'plugin', 'machine'+str(auto_machid)+'_eq', 'mid', tp2cvpjp(AUTO_data[mixerid][machnum+32]))
                if machnum+40 in AUTO_data[mixerid]: tracks.a_add_auto_pl(cvpj_l, 'plugin', 'machine'+str(auto_machid)+'_eq', 'high', tp2cvpjp(AUTO_data[mixerid][machnum+40]))
                if machnum+64 in AUTO_data[mixerid]: tracks.a_add_auto_pl(cvpj_l, 'track', 'MACH'+str(auto_machid), 'pan', auto.multiply(tp2cvpjp(AUTO_data[mixerid][machnum+64]),-0.5,2))
                if machnum+72 in AUTO_data[mixerid]: tracks.a_add_auto_pl(cvpj_l, 'plugin', 'machine'+str(auto_machid)+'_width', 'width', tp2cvpjp(AUTO_data[mixerid][machnum+72]))

        for mixernum in range(2):
            mixerid = 'FX_'+str(mixernum+1)
            for autonum in AUTO_data[mixerid]:
                autofx_num = (autonum//16)
                autofx_slot = (autonum//8)-(autofx_num*2)
                autofx_ctrl = autonum-(autofx_slot*8)-(autofx_num*16)
                cvpj_fx_autoid = 'machine'+str(autofx_num+1+(mixernum*7))+'_slot'+str(autofx_slot+1)

                cvpj_auto_pl = tp2cvpjp(AUTO_data[mixerid][autonum])

                if autofx_ctrl == 5: 
                    cvpj_auto_type = 'slot'
                    cvpj_auto_ctrl = 'enabled'
                    cvpj_auto_pl = auto.multiply(cvpj_auto_pl, -1, -1)
                else: 
                    cvpj_auto_type = 'plugin'
                    cvpj_auto_ctrl = str(autofx_ctrl)

                tracks.a_add_auto_pl(cvpj_l, cvpj_auto_type, cvpj_fx_autoid, cvpj_auto_ctrl, cvpj_auto_pl)

        master_params = {}

        for causticidnum in MSTR['CCOL']:
            if causticidnum in master_idnames:
                t_fxtypeparam = master_idnames[causticidnum]
                if t_fxtypeparam[0] not in master_params: master_params[t_fxtypeparam[0]] = {}
                master_params[t_fxtypeparam[0]][t_fxtypeparam[1]] = MSTR['CCOL'][causticidnum]

        master_fxchaindata = []

        if 'EFFX' in MSTR:
            CausticFXData = MSTR['EFFX']
            for slotnum in CausticFXData:
                if CausticFXData[slotnum] != {}: 
                    slot_fxslotdata = CausticFXData[slotnum]['controls']

                    cvpj_fxslot = make_fxslot(
                        caustic_fxtype[CausticFXData[slotnum]['type']], 
                        slot_fxslotdata, 
                        'master_slot'+str(slotnum))
                    cvpj_fxslot['enabled'] = int(not int(slot_fxslotdata[5]))
                    master_fxchaindata.append(cvpj_fxslot)

        cvpj_fxslot_eq = make_fxslot('master_eq', master_params['eq'], 'master_eq')
        cvpj_fxslot_eq['enabled'] = int(not int(master_params['eq']['muted']))
        cvpj_fxslot_limiter = make_fxslot('master_limiter', master_params['limiter'], 'master_limiter')
        cvpj_fxslot_limiter['enabled'] = int(not int(master_params['limiter']['muted']))

        master_fxchaindata.append(cvpj_fxslot_eq)
        master_fxchaindata.append(cvpj_fxslot_limiter)

        #print(AUTO_data)

        for autonum in AUTO_data['MASTER']:
            if autonum in master_idnames:
                t_fxtypeparam = master_idnames[autonum]
                if t_fxtypeparam[0] in ['eq', 'limiter']:
                    print(t_fxtypeparam)
                    tracks.a_add_auto_pl(cvpj_l, 'plugin', 'master_'+t_fxtypeparam[0], t_fxtypeparam[1], tp2cvpjp(AUTO_data['MASTER'][autonum]))
                if t_fxtypeparam == ['main', 'master']:
                    print(t_fxtypeparam)
                    tracks.a_add_auto_pl(cvpj_l, 'main', None, 'vol', tp2cvpjp(AUTO_data['MASTER'][autonum]))
            elif autonum >= 64:
                autonum_calc = autonum - 64
                autofx_slot = (autonum_calc//8)
                autofx_ctrl = autonum-(autofx_slot*8)

                cvpj_auto_pl = tp2cvpjp(AUTO_data['MASTER'][autonum])

                if autofx_ctrl-64 == 5: 
                    cvpj_auto_type = 'slot'
                    cvpj_auto_ctrl = 'enabled'
                    cvpj_auto_pl = auto.multiply(cvpj_auto_pl, -1, -1)
                else: 
                    cvpj_auto_type = 'plugin'
                    cvpj_auto_ctrl = str(autofx_ctrl-64)

                cvpj_fx_autoid = 'master_slot'+str(autofx_slot+1)
                tracks.a_add_auto_pl(cvpj_l, cvpj_auto_type, cvpj_fx_autoid, cvpj_auto_ctrl, cvpj_auto_pl)

        tracks.a_addtrack_master(cvpj_l, 'Master', master_params['main']['master'], [0.52, 0.52, 0.52])

        tracks.a_fx_audio_master(cvpj_l, master_fxchaindata)

        cvpj_l['do_addwrap'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['bpm'] = CausticData['Tempo']
        cvpj_l['timesig_numerator'] = CausticData['Numerator']
        cvpj_l['timesig_denominator'] = 4
        return json.dumps(cvpj_l)

