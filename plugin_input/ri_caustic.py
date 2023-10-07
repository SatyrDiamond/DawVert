# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin import format_caustic
from functions import audio_wav
from functions import auto
from functions import data_bytes
from functions import idvals
from functions import note_data
from functions import plugins
from functions import placements
from functions import song
from functions_tracks import tracks_ri
from functions_tracks import fxslot
from functions_tracks import auto_data
from functions_tracks import auto_nopl
from functions_tracks import trackfx
from functions_tracks import tracks_master
import plugin_input
import os.path
import json
import struct

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
caustic_fxtype[9] = 'parameq'
caustic_fxtype[10] = 'limiter'
caustic_fxtype[11] = 'vinylsim'
caustic_fxtype[12] = 'comb'
caustic_fxtype[14] = 'cabsim'
caustic_fxtype[16] = 'staticflanger'
caustic_fxtype[17] = 'filter'
caustic_fxtype[18] = 'octaver'
caustic_fxtype[19] = 'vibrato'
caustic_fxtype[20] = 'tremolo'
caustic_fxtype[21] = 'autopan'

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
            key = causticnote[6]
            if key != 0: 
                notedata = note_data.rx_makenote(causticnote[2]*4, causticnote[3]*4, key-60, causticnote[14], None)
                notelist.append(notedata)
    return notelist

def loopmode_cvpj(wavdata): 
    lm = wavdata['mode']
    data_end = wavdata['end']
    if lm == 0 or lm == 1 or lm == 2 or lm == 3: data_start = wavdata['start']
    if lm == 4 or lm == 5: data_start = 0

    if lm == 0: data_trigger = 'normal'
    else: data_trigger = 'oneshot'

    loopdata = {}
    if lm == 2 or lm == 3 or lm == 4 or lm == 5:
        loopdata['enabled'] = 1
        loopdata['points'] = [wavdata['start'], wavdata['end']]
    if lm == 0 or lm == 1: loopdata['enabled'] = 0
    if lm == 2 or lm == 4: loopdata['mode'] = "normal"
    if lm == 3 or lm == 5: loopdata['mode'] = "pingpong"
    return data_start, data_end, data_trigger, loopdata

def tp2cvpjp(twopoints):
    return auto.twopoints2cvpjpoints(twopoints, 4, 'normal', 0)

def pat_auto_place_part(pl_position, pl_duration, auto_smooth, auto_points):
    auto_curpoint = 0
    cvpj_placement_points = []
    auto_duration = int(len(auto_points))
    for _ in range((int(pl_duration)*2)-1):
        point_value = auto_points[auto_curpoint]
        if auto_smooth == 0.0: cvpj_placement_points.append([auto_curpoint/2, point_value, 'instant'])
        else:
            cvpj_placement_points.append([auto_curpoint/2, point_value, 'normal'])
            if auto_smooth != 1.0: cvpj_placement_points.append([(auto_curpoint/2)+(auto_smooth/2), point_value, 'normal'])
        auto_curpoint += 1
        if auto_curpoint == auto_duration: 
            auto_curpoint = 0
            cvpj_placements.append(cvpj_placement_points)

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
    auto_duration = int(len(auto_points))
    remainingloops = pl_duration
    out_autopls = []
    looppos = 0
    while remainingloops > 0:
        loopsize = min(1, remainingloops/(auto_duration/2))
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
        'samples_inside': True,
        'placement_cut': True,
        'placement_loop': ['loop']
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

        idvals_inst_caustic = idvals.parse_idvalscsv('data_idvals/caustic_inst.csv')
        idvals_fx_caustic = idvals.parse_idvalscsv('data_idvals/caustic_fx.csv')

        cvpj_l = {}
        
        samplefolder = extra_param['samplefolder']

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
            else: cvpj_trackname = idvals.get_idval(idvals_inst_caustic, machine['id'], 'name')

            cvpj_notelistindex = {}

            pluginid = 'machine'+machid
            cvpj_trackid = 'MACH'+machid
            cvpj_instdata = {'pluginid': pluginid}

            cvpj_trackcolor = idvals.get_idval(idvals_inst_caustic, machine['id'], 'color')

            tracks_ri.track_create(cvpj_l, cvpj_trackid, 'instrument')
            tracks_ri.track_visual(cvpj_l, cvpj_trackid, name=cvpj_trackname, color=cvpj_trackcolor)
            tracks_ri.track_inst_pluginid(cvpj_l, cvpj_trackid, pluginid)

            # -------------------------------- PCMSynth --------------------------------
            if machine['id'] == 'PCMS':
                middlenote = 0
                tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'usemasterpitch', True, 'bool')
                if len(machine['regions']) == 1:
                    singlewav = machine['regions'][0]
                    if singlewav['key_lo'] == 24 and singlewav['key_hi'] == 108: isMultiSampler = False
                    else: isMultiSampler = True
                else: isMultiSampler = True

                if not isMultiSampler:
                    singlewav = machine['regions'][0]
                    wave_path = samplefolder+machid+'_PCMSynth_0.wav'

                    loopdata = None
                    if singlewav['mode'] != 0 and singlewav['mode'] != 1: loopdata = {'loop':[singlewav['start'], singlewav['end']]}
                    if singlewav['samp_ch'] != 0: audio_wav.generate(wave_path, singlewav['samp_data'], singlewav['samp_ch'], singlewav['samp_hz'], 16, loopdata)

                    middlenote += singlewav['key_root']-60

                    plugins.add_plug_sampler_singlefile(cvpj_l, pluginid, wave_path)
                    plugins.add_plug_data(cvpj_l, pluginid, 'length', singlewav['samp_len'])
                    plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "samples")
                    data_start, data_end, data_trigger, data_loopdata = loopmode_cvpj(singlewav)
                    plugins.add_plug_data(cvpj_l, pluginid, 'start', data_start)
                    plugins.add_plug_data(cvpj_l, pluginid, 'end', data_end)
                    plugins.add_plug_data(cvpj_l, pluginid, 'trigger', data_trigger)
                    plugins.add_plug_data(cvpj_l, pluginid, 'loop', data_loopdata)

                else:
                    plugins.add_plug_multisampler(cvpj_l, pluginid)
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
                        data_start, data_end, data_trigger, data_loopdata = loopmode_cvpj(singlewav)
                        regionparams['start'] = data_start
                        regionparams['end'] = data_end
                        regionparams['trigger'] = data_trigger
                        regionparams['loop'] = data_loopdata
                        plugins.add_plug_multisampler_region(cvpj_l, pluginid, regionparams)
                        samplecount += 1

                pcms_c = machine['controls']

                middlenote += int(pcms_c[1]*12)
                middlenote += int(pcms_c[2])

                tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'pitch', pcms_c[3], 'float')
                tracks_ri.track_dataval_add(cvpj_l, cvpj_trackid, None, 'middlenote', -middlenote)

                plugins.add_asdr_env(cvpj_l, pluginid, 'volume', 0, pcms_c[5], 0, pcms_c[6], pcms_c[7], pcms_c[8], 1)

            # -------------------------------- BeatBox --------------------------------
            elif machine['id'] == 'BBOX':
                tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'usemasterpitch', False, 'bool')
                plugins.add_plug_multisampler(cvpj_l, pluginid)
                samplecount = 0
                bbox_key = -12
                for bbox_sample in machine['samples']:
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
                    plugins.add_plug_multisampler_region(cvpj_l, pluginid, regionparams)
                    samplecount += 1
                    bbox_key += 1
            elif machine['id'] == 'NULL':
                pass
            else:
                plugins.add_plug(cvpj_l, pluginid, 'native-caustic', machine['id'])
                if 'controls' in machine: 
                    for paramid in machine['controls']:
                        plugins.add_plug_param(cvpj_l, pluginid, str(paramid), machine['controls'][paramid], 'float', str(paramid))
                if 'customwaveform1' in machine: 
                    wavedata = list(struct.unpack("<"+("h"*660), machine['customwaveform1']))
                    plugins.add_plug_data(cvpj_l, pluginid, 'customwaveform1', wavedata)
                if 'customwaveform2' in machine: 
                    wavedata = list(struct.unpack("<"+("h"*660), machine['customwaveform2']))
                    plugins.add_plug_data(cvpj_l, pluginid, 'customwaveform2', wavedata)

            tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'vol', mach_mixer_vol[machnum-1], 'float')
            tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'pan', mach_mixer_pan[machnum-1], 'float')
            tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'enabled', int(not bool(mach_mixer_mute[machnum-1])), 'bool')
            tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'solo', mach_mixer_solo[machnum-1], 'bool')

            if machine['id'] != 'NULL':
                if 'patterns' in machine:
                    patterns = machine['patterns']
                    for pattern in patterns:
                        patid = pattern
                        causticpattern = patterns[pattern]
                        notelist = parse_notelist(causticpattern, machid)
                        if notelist != []: 
                            tracks_ri.notelistindex_add(cvpj_l, patid, cvpj_trackid, notelist)
                            tracks_ri.notelistindex_visual(cvpj_l, patid, cvpj_trackid, name=pattern)

            if machnum in CausticData['EFFX']:
                CausticFXData = CausticData['EFFX'][machnum]
                for slotnum in CausticFXData:
                    if CausticFXData[slotnum] != {}: 
                        slot_fxslotdata = CausticFXData[slotnum]['controls']
                        fxpluginid = 'machine'+str(machnum)+'_slot'+str(slotnum)

                        plugins.add_plug(cvpj_l, fxpluginid, 'native-caustic', caustic_fxtype[CausticFXData[slotnum]['type']])
                        plugins.add_plug_fxdata(cvpj_l, fxpluginid, int(not int(slot_fxslotdata[5])), 1)

                        for paramid in slot_fxslotdata:
                            plugins.add_plug_param(cvpj_l, fxpluginid, str(paramid), slot_fxslotdata[paramid], 'float', str(paramid))

                        fxslot.insert(cvpj_l, ['track', cvpj_trackid], 'audio', fxpluginid)

            slot_mixereqfxslotdata = {}
            slot_mixereqfxslotdata['bass'] = mach_mixer_eq_low[machnum-1]
            slot_mixereqfxslotdata['mid'] = mach_mixer_eq_mid[machnum-1]
            slot_mixereqfxslotdata['high'] = mach_mixer_eq_high[machnum-1]

            trackfx.send_add(cvpj_l, cvpj_trackid, 'master_delay', mach_mixer_send_delay[machnum-1], cvpj_trackid+'_send_delay')
            trackfx.send_add(cvpj_l, cvpj_trackid, 'master_reverb', mach_mixer_send_reverb[machnum-1], cvpj_trackid+'_send_reverb')

            mixereq_plugid = 'machine'+str(machnum)+'_eq'
            plugins.add_plug(cvpj_l, mixereq_plugid, 'native-caustic', 'mixer_eq')
            plugins.add_plug_param(cvpj_l, mixereq_plugid, 'bass', mach_mixer_eq_low[machnum-1], 'float', 'bass')
            plugins.add_plug_param(cvpj_l, mixereq_plugid, 'mid', mach_mixer_eq_mid[machnum-1], 'float', 'mid')
            plugins.add_plug_param(cvpj_l, mixereq_plugid, 'high', mach_mixer_eq_high[machnum-1], 'float', 'high')
            fxslot.insert(cvpj_l, ['track', cvpj_trackid], 'audio', mixereq_plugid)
            plugins.add_plug_fxvisual(cvpj_l, mixereq_plugid, 'Mixer EQ', [0.67, 0.67, 0.67])

            width_plugid = 'machine'+str(machnum)+'_width'
            plugins.add_plug(cvpj_l, width_plugid, 'native-caustic', 'width')
            plugins.add_plug_param(cvpj_l, width_plugid, 'width', mach_mixer_width[machnum-1], 'float', 'width')
            fxslot.insert(cvpj_l, ['track', cvpj_trackid], 'audio', width_plugid)
            plugins.add_plug_fxvisual(cvpj_l, width_plugid, 'Width', [0.66, 0.61, 0.76])

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
                    pl_placement['cut'] = {'type': 'loop', 'loopend': patmeasures}
                pl_placement['fromindex'] = t_patid
                if str(SEQNe_mach) not in t_track_placements: t_track_placements[str(SEQNe_mach)] = []
                t_track_placements[str(SEQNe_mach)].append(pl_placement)

                if 'patterns' in machines[SEQNe[0]]:
                    autodata = machines[SEQNe[0]]['patterns'][t_patid]['auto']

                    for autoid in autodata:
                        single_patautodata = autodata[autoid]
                        ctrlpatautopl = pat_auto_place(SEQNe_pos, SEQNe_len, single_patautodata)
                        for s_apl in ctrlpatautopl:
                            auto_data.add_pl(cvpj_l, 'float', ['plugin', 'machine'+str(SEQNe_mach), str(autoid)], s_apl)

        for t_track_placement in t_track_placements:
            tracks_ri.add_pl(cvpj_l, 'MACH'+str(t_track_placement), 'notes', t_track_placements[t_track_placement])

        tempo_placement = {"position": 0}

        tempo_placement_dur = 0
        tempo_points = []
        for point in SEQN_tempo:
            if tempo_placement_dur > point[0]*4: tempo_placement_dur = point[0]*4
            tempo_points.append({"position": point[0]*4, "value": point[1]})
        tempo_placement['duration'] = tempo_placement_dur
        tempo_placement['points'] = tempo_points

        auto_data.add_pl(cvpj_l, 'float', ['main', 'bpm'], [tempo_placement])

        #'machine'+machid

        for machnum in range(14):
            for autoname in AUTO_data['MACH_'+str(machnum+1)]:
                auto_nopl.twopoints(['plugin', 'machine'+str(machnum+1), str(autoname)], 'float', AUTO_data['MACH_'+str(machnum+1)][autoname], 4, 'normal')

        for mixernum in range(2):
            mixerid = 'MIXER_'+str(mixernum+1)
            for machnum in range(7):
                auto_machid = machnum+1+(mixernum*7)
                if machnum in AUTO_data[mixerid]: 
                    auto_nopl.twopoints(['track', 'MACH'+str(auto_machid), 'vol'], 'float', AUTO_data[mixerid][machnum], 4, 'normal')
                if (machnum*2)+8 in AUTO_data[mixerid]: 
                    auto_nopl.twopoints(['send', 'MACH'+str(auto_machid)+'_send_delay', 'amount'], 'float', AUTO_data[mixerid][(machnum*2)+8], 4, 'normal')
                if (machnum*2)+9 in AUTO_data[mixerid]: 
                    auto_nopl.twopoints(['send', 'MACH'+str(auto_machid)+'_send_reverb', 'amount'], 'float', AUTO_data[mixerid][(machnum*2)+9], 4, 'normal')
                if machnum+24 in AUTO_data[mixerid]: 
                    auto_nopl.twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'bass'], 'float', AUTO_data[mixerid][machnum+24], 4, 'normal')
                if machnum+32 in AUTO_data[mixerid]: 
                    auto_nopl.twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'mid'], 'float', AUTO_data[mixerid][machnum+32], 4, 'normal')
                if machnum+40 in AUTO_data[mixerid]: 
                    auto_nopl.twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'high'], 'float', AUTO_data[mixerid][machnum+40], 4, 'normal')
                if machnum+64 in AUTO_data[mixerid]: 
                    auto_nopl.twopoints(['track', 'MACH'+str(auto_machid), 'pan'], 'float', auto.twopoints_addmul(AUTO_data[mixerid][machnum+64],-0.5,2), 4, 'normal')
                if machnum+72 in AUTO_data[mixerid]: 
                    auto_nopl.twopoints(['plugin', 'machine'+str(auto_machid)+'_width', 'width'], 'float', AUTO_data[mixerid][machnum+72], 4, 'normal')

        for mixernum in range(2):
            mixerid = 'FX_'+str(mixernum+1)
            for autonum in AUTO_data[mixerid]:
                autofx_num = (autonum//16)
                autofx_slot = (autonum//8)-(autofx_num*2)
                autofx_ctrl = autonum-(autofx_slot*8)-(autofx_num*16)
                cvpj_fx_autoid = 'machine'+str(autofx_num+1+(mixernum*7))+'_slot'+str(autofx_slot+1)

                if autofx_ctrl == 5:
                    auto_nopl.twopoints(['slot', cvpj_fx_autoid, 'enabled'], 'bool', auto.twopoints_addmul(AUTO_data[mixerid][autonum],-1,-1), 4, 'normal')
                else: 
                    auto_nopl.twopoints(['plugin', cvpj_fx_autoid, str(autofx_ctrl)], 'float', AUTO_data[mixerid][autonum], 4, 'normal')

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

                    masterslotplugid = 'master_slot'+str(slotnum)

                    fxtype = caustic_fxtype[CausticFXData[slotnum]['type']]
                    cvpj_fx_name = idvals.get_idval(idvals_fx_caustic, fxtype, 'name')
                    cvpj_fx_color = idvals.get_idval(idvals_fx_caustic, fxtype, 'color')

                    plugins.add_plug(cvpj_l, masterslotplugid, 'native-caustic', fxtype)
                    plugins.add_plug_fxdata(cvpj_l, masterslotplugid, not int(slot_fxslotdata[5]), None)
                    plugins.add_plug_fxvisual(cvpj_l, masterslotplugid, cvpj_fx_name, cvpj_fx_color)
                    fxslot.insert(cvpj_l, ['master'], 'audio', masterslotplugid)

                    for paramid in slot_fxslotdata:
                        plugins.add_plug_param(cvpj_l, masterslotplugid, paramid, slot_fxslotdata[paramid], 'float', str(paramid))


        for fxids in [
            ['master_delay', 'delay', 'Delay', [0.64, 0.78, 0.87]],
            ['master_reverb', 'reverb', 'Reverb', [0.83, 0.82, 0.51]]
            ]:
            trackfx.return_add(cvpj_l, ['master'], fxids[0])
            trackfx.return_visual(cvpj_l, ['master'], fxids[0], name=fxids[2], color=fxids[3])
            plugins.add_plug(cvpj_l, fxids[0], 'native-caustic', fxids[0])
            plugins.add_plug_fxdata(cvpj_l, fxids[0], True, master_params[fxids[1]]['wet'])
            fxslot.insert(cvpj_l, ['return', None, fxids[0]], 'audio', fxids[0])
            plugins.add_plug_fxvisual(cvpj_l, fxids[0], fxids[2], fxids[3])
            for paramid in master_params[fxids[1]]:
                plugins.add_plug_param(cvpj_l, fxids[0], paramid, master_params[fxids[1]][paramid], 'float', str(paramid))


        for fxids in [
            ['master_eq', 'eq', 'Equalizer', [0.76, 0.27, 0.27]], 
            ['master_limiter', 'limiter', 'Limiter', [0.62, 0.49, 0.42]]
            ]:
            plugins.add_plug(cvpj_l, fxids[0], 'native-caustic', fxids[0])
            plugins.add_plug_fxdata(cvpj_l, fxids[0], not int(master_params[fxids[1]]['muted']), 1)
            fxslot.insert(cvpj_l, ['master'], 'audio', fxids[0])
            plugins.add_plug_fxvisual(cvpj_l, fxids[0], fxids[2], fxids[3])
            for paramid in master_params[fxids[1]]:
                plugins.add_plug_param(cvpj_l, fxids[0], paramid, master_params[fxids[1]][paramid], 'float', str(paramid))


        #print(AUTO_data)

        for autonum in AUTO_data['MASTER']:
            if autonum in master_idnames:
                t_fxtypeparam = master_idnames[autonum]
                if t_fxtypeparam[0] in ['eq', 'limiter']:
                    auto_nopl.twopoints(['plugin', 'master_'+t_fxtypeparam[0], t_fxtypeparam[1]], 'float', AUTO_data['MASTER'][autonum], 4, 'normal')
                if t_fxtypeparam == ['main', 'master']:
                    auto_nopl.twopoints(['main', 'vol'], 'float', AUTO_data['MASTER'][autonum], 4, 'normal')
            elif autonum >= 64:
                autonum_calc = autonum - 64
                autofx_slot = (autonum_calc//8)
                autofx_ctrl = autonum-(autofx_slot*8)
                cvpj_fx_autoid = 'master_slot'+str(autofx_slot+1)

                if autofx_ctrl-64 == 5:
                    auto_nopl.twopoints(['slot', cvpj_fx_autoid, 'enabled'], 'bool', auto.twopoints_addmul(AUTO_data['MASTER'][autonum],-1,-1), 4, 'normal')
                else: 
                    auto_nopl.twopoints(['plugin', cvpj_fx_autoid, str(autofx_ctrl-64)], 'float', AUTO_data['MASTER'][autonum], 4, 'normal')

        tracks_master.create(cvpj_l, master_params['main']['master'])
        tracks_master.visual(cvpj_l, name='Master', color=[0.52, 0.52, 0.52])
        auto_nopl.to_cvpj(cvpj_l)

        cvpj_l['do_addloop'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        song.add_param(cvpj_l, 'bpm', CausticData['Tempo'])
        cvpj_l['timesig'] = [CausticData['Numerator'], 4]
        return json.dumps(cvpj_l)

