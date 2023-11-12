# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin import format_caustic
from functions import audio_wav
from functions import auto
from functions import data_bytes
from functions import data_dataset
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

#master_idnames[39] = ['main', 'master']
#master_idnames[40] = ['delay', 'muted']
#master_idnames[41] = ['reverb', 'muted']
#master_idnames[42] = ['eq', 'muted']
#master_idnames[43] = ['limiter', 'muted']

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

def add_caustic_fx(cvpj_l, autoloc, CausticFXData, start_plugid):
    for slotnum in CausticFXData:
        if CausticFXData[slotnum] != {}: 
            slot_fxslotdata = CausticFXData[slotnum]['controls']
            fxpluginid = start_plugid+'_slot'+str(slotnum)

            fxtype = caustic_fxtype[CausticFXData[slotnum]['type']]
            slotfx_plugindata = plugins.cvpj_plugin('deftype', 'native-caustic', fxtype)
            slotfx_plugindata.fxdata_add(bool(not int(slot_fxslotdata[5])), 1)
            fx_name, fx_color = dataset.object_get_name_color('plugin_fx', fxtype)
            slotfx_plugindata.fxvisual_add(fx_name, fx_color)

            paramlist = dataset.params_list('plugin_fx', fxtype)

            if paramlist != None:
                for paramid in paramlist: 
                    if paramid != '5':
                        paramid = int(paramid)
                        paramval = slot_fxslotdata[paramid] if paramid in slot_fxslotdata else None
                        slotfx_plugindata.param_add_dset(str(paramid), paramval, dataset, 'plugin_fx', fxtype)

            slotfx_plugindata.to_cvpj(cvpj_l, fxpluginid)

            fxslot.insert(cvpj_l, autoloc, 'audio', fxpluginid)

def loopmode_cvpj(wavdata): 
    lm = wavdata['mode']
    data_end = wavdata['end']
    if lm in [0,1,2,3]: data_start = wavdata['start']
    if lm in [4,5]: data_start = 0

    data_trigger = 'normal' if lm == 0 else 'oneshot'

    loopdata = {}
    if lm in [2,3,4,5]: loopdata = {'enabled': 1, 'points': [wavdata['start'], wavdata['end']]}
    if lm in [0,1]: loopdata['enabled'] = 0
    if lm in [2,4]: loopdata['mode'] = "normal"
    if lm in [3,5]: loopdata['mode'] = "pingpong"
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
        global dataset
        CausticData = format_caustic.deconstruct_main(input_file)
        machines = CausticData['Machines']
        SEQN = CausticData['SEQN']
        SEQN_tempo = CausticData['SEQN_tempo']
        EFFX = CausticData['EFFX']
        MSTR = CausticData['MSTR']
        AUTO_data = CausticData['AUTO']

        dataset = data_dataset.dataset('./data_dset/caustic.dset')

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

            dset_name, cvpj_trackcolor = dataset.object_get_name_color('plugin_inst', machine['id'])
            cvpj_trackname = machine['name'] if 'name' in machine else dset_name

            cvpj_notelistindex = {}

            pluginid = 'machine'+machid
            cvpj_trackid = 'MACH'+machid
            cvpj_instdata = {'pluginid': pluginid}

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

                    inst_plugindata = plugins.cvpj_plugin('sampler', wave_path, None)
                    inst_plugindata.dataval_add('length', singlewav['samp_len'])
                    inst_plugindata.dataval_add('point_value_type', "samples")
                    data_start, data_end, data_trigger, data_loopdata = loopmode_cvpj(singlewav)
                    inst_plugindata.dataval_add('start', data_start)
                    inst_plugindata.dataval_add('end', data_end)
                    inst_plugindata.dataval_add('trigger', data_trigger)
                    inst_plugindata.dataval_add('loop', data_loopdata)

                else:
                    inst_plugindata = plugins.cvpj_plugin('multisampler', None, None)
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
                        regionparams['start'], regionparams['end'], regionparams['trigger'], regionparams['loop'] = loopmode_cvpj(singlewav)
                        inst_plugindata.region_add(regionparams)
                        samplecount += 1

                pcms_c = machine['controls']

                middlenote += int(pcms_c[1]*12)
                middlenote += int(pcms_c[2])

                tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'pitch', pcms_c[3], 'float')
                tracks_ri.track_dataval_add(cvpj_l, cvpj_trackid, None, 'middlenote', -middlenote)

                inst_plugindata.asdr_env_add('volume', 0, pcms_c[5], 0, pcms_c[6], pcms_c[7], pcms_c[8], 1)
                inst_plugindata.to_cvpj(cvpj_l, pluginid)

            # -------------------------------- BeatBox --------------------------------
            elif machine['id'] == 'BBOX':
                tracks_ri.track_param_add(cvpj_l, cvpj_trackid, 'usemasterpitch', False, 'bool')
                inst_plugindata = plugins.cvpj_plugin('multisampler', None, None)
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
                    inst_plugindata.region_add(regionparams)
                    samplecount += 1
                    bbox_key += 1
                inst_plugindata.to_cvpj(cvpj_l, pluginid)
            elif machine['id'] == 'NULL':
                pass
            else:
                inst_plugindata = plugins.cvpj_plugin('deftype', 'native-caustic', machine['id'])
                if 'controls' in machine: 
                    paramlist = dataset.params_list('plugin', machine['id'])
                    for paramid in paramlist:
                        paramdata = params_i_get('plugin', machine['id'], paramid)
                        inst_plugindata.param_add_dset(str(paramid), machine['controls'][int(paramid)], dataset, 'plugin_inst', machine['id'])

                if 'customwaveform1' in machine: inst_plugindata.wave_add('customwaveform1', list(struct.unpack("<"+("h"*660), machine['customwaveform1'])), -157, 157)
                if 'customwaveform2' in machine: inst_plugindata.wave_add('customwaveform2', list(struct.unpack("<"+("h"*660), machine['customwaveform2'])), -157, 157)
                inst_plugindata.to_cvpj(cvpj_l, pluginid)

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

            if machnum in CausticData['EFFX']: add_caustic_fx(cvpj_l, ['track', cvpj_trackid], CausticData['EFFX'][machnum], 'machine'+str(machnum))

            slot_mixereqfxslotdata = {}
            slot_mixereqfxslotdata['bass'] = mach_mixer_eq_low[machnum-1]
            slot_mixereqfxslotdata['mid'] = mach_mixer_eq_mid[machnum-1]
            slot_mixereqfxslotdata['high'] = mach_mixer_eq_high[machnum-1]

            trackfx.send_add(cvpj_l, cvpj_trackid, 'master_delay', mach_mixer_send_delay[machnum-1], cvpj_trackid+'_send_delay')
            trackfx.send_add(cvpj_l, cvpj_trackid, 'master_reverb', mach_mixer_send_reverb[machnum-1], cvpj_trackid+'_send_reverb')

            mixereq_plugid = 'machine'+str(machnum)+'_eq'
            mixereq_plugindata = plugins.cvpj_plugin('deftype', 'native-caustic', 'mixer_eq')
            mixereq_plugindata.fxvisual_add('Mixer EQ', [0.67, 0.67, 0.67])

            mixereq_plugindata.param_add_minmax('bass', mach_mixer_eq_low[machnum-1], 'float', 'bass', [0,2])
            mixereq_plugindata.param_add_minmax('mid', mach_mixer_eq_mid[machnum-1], 'float', 'mid', [0,2])
            mixereq_plugindata.param_add_minmax('high', mach_mixer_eq_high[machnum-1], 'float', 'high', [0,2])
            mixereq_plugindata.to_cvpj(cvpj_l, mixereq_plugid)
            fxslot.insert(cvpj_l, ['track', cvpj_trackid], 'audio', mixereq_plugid)

            width_plugid = 'machine'+str(machnum)+'_width'
            width_plugindata = plugins.cvpj_plugin('deftype', 'native-caustic', 'width')
            width_plugindata.fxvisual_add('Width', [0.66, 0.61, 0.76])
            width_plugindata.param_add_minmax('width', mach_mixer_width[machnum-1], 'float', 'width', [-1,1])
            width_plugindata.to_cvpj(cvpj_l, width_plugid)
            fxslot.insert(cvpj_l, ['track', cvpj_trackid], 'audio', width_plugid)
            
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
                if machnum in AUTO_data[mixerid]: auto_nopl.twopoints(['track', 'MACH'+str(auto_machid), 'vol'], 'float', AUTO_data[mixerid][machnum], 4, 'normal')
                if (machnum*2)+8 in AUTO_data[mixerid]: auto_nopl.twopoints(['send', 'MACH'+str(auto_machid)+'_send_delay', 'amount'], 'float', AUTO_data[mixerid][(machnum*2)+8], 4, 'normal')
                if (machnum*2)+9 in AUTO_data[mixerid]: auto_nopl.twopoints(['send', 'MACH'+str(auto_machid)+'_send_reverb', 'amount'], 'float', AUTO_data[mixerid][(machnum*2)+9], 4, 'normal')
                if machnum+24 in AUTO_data[mixerid]: auto_nopl.twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'bass'], 'float', AUTO_data[mixerid][machnum+24], 4, 'normal')
                if machnum+32 in AUTO_data[mixerid]: auto_nopl.twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'mid'], 'float', AUTO_data[mixerid][machnum+32], 4, 'normal')
                if machnum+40 in AUTO_data[mixerid]: auto_nopl.twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'high'], 'float', AUTO_data[mixerid][machnum+40], 4, 'normal')
                if machnum+64 in AUTO_data[mixerid]: auto_nopl.twopoints(['track', 'MACH'+str(auto_machid), 'pan'], 'float', auto.twopoints_addmul(AUTO_data[mixerid][machnum+64],-0.5,2), 4, 'normal')
                if machnum+72 in AUTO_data[mixerid]: auto_nopl.twopoints(['plugin', 'machine'+str(auto_machid)+'_width', 'width'], 'float', AUTO_data[mixerid][machnum+72], 4, 'normal')

        for mixernum in range(2):
            mixerid = 'FX_'+str(mixernum+1)
            for autonum in AUTO_data[mixerid]:
                autofx_num = (autonum//16)
                autofx_slot = (autonum//8)-(autofx_num*2)
                autofx_ctrl = autonum-(autofx_slot*8)-(autofx_num*16)
                cvpj_fx_autoid = 'machine'+str(autofx_num+1+(mixernum*7))+'_slot'+str(autofx_slot+1)

                if autofx_ctrl == 5: auto_nopl.twopoints(['slot', cvpj_fx_autoid, 'enabled'], 'bool', auto.twopoints_addmul(AUTO_data[mixerid][autonum],-1,-1), 4, 'normal')
                else: auto_nopl.twopoints(['plugin', cvpj_fx_autoid, str(autofx_ctrl)], 'float', AUTO_data[mixerid][autonum], 4, 'normal')

        master_fxchaindata = []

        if 'EFFX' in MSTR: add_caustic_fx(cvpj_l, ['master'], MSTR['EFFX'], 'master_slot')

        for fxid in ['master_delay','master_reverb','master_eq','master_limiter']:
            mfx_name, mfx_color = dataset.object_get_name_color('plugin_master_fx', fxid)

            if fxid in ['master_delay','master_reverb']:
                trackfx.return_add(cvpj_l, ['master'], fxid)
                trackfx.return_visual(cvpj_l, ['master'], fxid, name=mfx_name, color=mfx_color)
                fxslot.insert(cvpj_l, ['return', None, fxid], 'audio', fxid)
            else:
                fxslot.insert(cvpj_l, ['master'], 'audio', fxid)

            masterfx_plugindata = plugins.cvpj_plugin('deftype', 'native-caustic', fxid)
            masterfx_plugindata.fxvisual_add(mfx_name, mfx_color)

            if fxid == 'master_delay': masterfx_plugindata.fxdata_add(not bool(MSTR['CCOL'][40]), 1)
            if fxid == 'master_reverb': masterfx_plugindata.fxdata_add(not bool(MSTR['CCOL'][41]), 1)
            if fxid == 'master_eq': masterfx_plugindata.fxdata_add(not bool(MSTR['CCOL'][42]), 1)
            if fxid == 'master_limiter': masterfx_plugindata.fxdata_add(not bool(MSTR['CCOL'][43]), 1)

            paramlist = dataset.params_list('plugin_master_fx', fxid)
            if paramlist != None:
                for paramid in paramlist: 
                    paramid = int(paramid)
                    paramval = MSTR['CCOL'][paramid] if paramid in MSTR['CCOL'] else None
                    masterfx_plugindata.param_add_dset(str(paramid), paramval, dataset, 'plugin_master_fx', fxid)
            masterfx_plugindata.to_cvpj(cvpj_l, fxid)

        for autonum in AUTO_data['MASTER']:
            if autonum in MSTR['CCOL']:
                t_fxtypeparam = MSTR['CCOL'][autonum]
                defparams = dataset.params_i_get('plugin_master_fx', fxid, str(autonum))
                if 1 <= autonum <= 9: auto_nopl.twopoints(['plugin', 'master_limiter', str(autonum)], defparams[1], AUTO_data['MASTER'][autonum], 4, 'normal')
                if 16 <= autonum <= 25: auto_nopl.twopoints(['plugin', 'master_reverb', str(autonum)], defparams[1], AUTO_data['MASTER'][autonum], 4, 'normal')
                if 30 <= autonum <= 34: auto_nopl.twopoints(['plugin', 'master_eq', str(autonum)], defparams[1], AUTO_data['MASTER'][autonum], 4, 'normal')
                if 35 <= autonum <= 38: auto_nopl.twopoints(['plugin', 'master_limiter', str(autonum)], defparams[1], AUTO_data['MASTER'][autonum], 4, 'normal')
                elif autonum == 39: auto_nopl.twopoints(['master', 'vol'], 'float', AUTO_data['MASTER'][autonum], 4, 'normal')
                #elif autonum == 40: auto_nopl.twopoints(['slot', 'master_delay'], 'bool', AUTO_data['MASTER'][autonum], 4, 'normal')
                #elif autonum == 41: auto_nopl.twopoints(['slot', 'master_reverb'], 'bool', AUTO_data['MASTER'][autonum], 4, 'normal')
                #elif autonum == 42: auto_nopl.twopoints(['slot', 'master_eq'], 'bool', AUTO_data['MASTER'][autonum], 4, 'normal')
                #elif autonum == 43: auto_nopl.twopoints(['slot', 'master_limiter'], 'bool', AUTO_data['MASTER'][autonum], 4, 'normal')

            elif autonum >= 64:
                autonum_calc = autonum - 64
                autofx_slot = (autonum_calc//8)
                autofx_ctrl = autonum-(autofx_slot*8)
                cvpj_fx_autoid = 'master_slot'+str(autofx_slot+1)

                if autofx_ctrl-64 == 5:
                    auto_nopl.twopoints(['slot', cvpj_fx_autoid, 'enabled'], 'bool', auto.twopoints_addmul(AUTO_data['MASTER'][autonum],-1,-1), 4, 'normal')
                else: 
                    auto_nopl.twopoints(['plugin', cvpj_fx_autoid, str(autofx_ctrl-64)], 'float', AUTO_data['MASTER'][autonum], 4, 'normal')

        tracks_master.create(cvpj_l, MSTR['CCOL'][39])
        tracks_master.visual(cvpj_l, name='Master', color=[0.52, 0.52, 0.52])
        auto_nopl.to_cvpj(cvpj_l)

        cvpj_l['do_addloop'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        song.add_param(cvpj_l, 'bpm', CausticData['Tempo'])
        song.add_timesig(cvpj_l, CausticData['Numerator'], 4)
        return json.dumps(cvpj_l)

