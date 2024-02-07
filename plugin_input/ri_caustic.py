# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import audio_wav
from functions import data_bytes
from functions_plugin import format_caustic
from objects import dv_dataset
import json
import os.path
import plugin_input
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

def parse_notelist(cvpj_notelist, causticpattern): 
    causticnotes = causticpattern['notes']
    for causticnote in causticnotes:
        if causticnote[1] != 4294967295:
            key = causticnote[6]
            if key != 0: 
                cvpj_notelist.add_r(causticnote[2]*4, causticnote[3]*4, key-60, causticnote[14], {})

def add_caustic_fx(convproj_obj, track_obj, CausticFXData, start_plugid):
    for slotnum in CausticFXData:
        if CausticFXData[slotnum] != {}: 
            slot_fxslotdata = CausticFXData[slotnum]['controls']
            fx_pluginid = start_plugid+'_slot'+str(slotnum)

            fxtype = caustic_fxtype[CausticFXData[slotnum]['type']]
            plugin_obj = convproj_obj.add_plugin(fx_pluginid, 'native-caustic', fxtype)
            plugin_obj.fxdata_add(bool(not int(slot_fxslotdata[5])), 1)
            plugin_obj.visual.name, plugin_obj.visual.color = dataset.object_get_name_color('plugin_fx', fxtype)

            paramlist = dataset.params_list('plugin_fx', fxtype)

            if paramlist != None:
                for paramid in paramlist: 
                    if paramid != '5':
                        paramid = int(paramid)
                        paramval = slot_fxslotdata[paramid] if paramid in slot_fxslotdata else None
                        plugin_obj.add_from_dset(str(paramid), paramval, dataset, 'plugin_fx', fxtype)

            track_obj.fxslots_audio.append(fx_pluginid)

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
    tm_ap = []
    auto_duration = int(len(auto_points))
    for auto_curpoint in range((int(pl_duration)*2)-1):
        point_value = auto_points[auto_curpoint]
        if auto_smooth == 0.0: tm_ap.append([auto_curpoint/2, point_value, 'instant'])
        else:
            tm_ap.append([auto_curpoint/2, point_value, 'normal'])
            if auto_smooth != 1.0: tm_ap.append([(auto_curpoint/2)+(auto_smooth/2), point_value, 'normal'])
    return tm_ap

def pat_auto_place(convproj_obj, pl_position, pl_duration, autodata, autoloc):
    auto_smooth = autodata['smooth']
    auto_points = autodata['data']
    auto_duration = int(len(auto_points))
    remainingloops = pl_duration
    looppos = 0
    while remainingloops > 0:
        loopsize = min(1, remainingloops/(auto_duration/2))
        remainingloops -= auto_duration/2
        autopl_obj = convproj_obj.add_automation_pl(autoloc, 'float')
        autopl_obj.position = pl_position+looppos
        autopl_obj.duration = (auto_duration/2)*loopsize
        for t_ap in pat_auto_place_part(pl_position+looppos, (auto_duration/2)*loopsize, auto_smooth, auto_points):
            autopoint_obj = autopl_obj.data.add_point()
            autopoint_obj.pos = t_ap[0]
            autopoint_obj.value = t_ap[1]
            autopoint_obj.type = t_ap[2]
        looppos += auto_duration/2

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
    def parse(self, convproj_obj, input_file, extra_param):
        global dataset

        convproj_obj.type = 'ri'
        convproj_obj.set_timings(4, True)

        CausticData = format_caustic.deconstruct_main(input_file)
        machines = CausticData['Machines']
        SEQN = CausticData['SEQN']
        SEQN_tempo = CausticData['SEQN_tempo']
        EFFX = CausticData['EFFX']
        MSTR = CausticData['MSTR']
        AUTO_data = CausticData['AUTO']

        dataset = dv_dataset.dataset('./data_dset/caustic.dset')

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
            pluginid = 'machine'+machid
            cvpj_trackid = 'MACH'+machid

            dset_name, cvpj_trackcolor = dataset.object_get_name_color('plugin_inst', machine['id'])

            track_obj = convproj_obj.add_track(cvpj_trackid, 'instrument', 1, True)
            track_obj.visual.name = machine['name'] if 'name' in machine else dset_name
            track_obj.visual.color = cvpj_trackcolor
            track_obj.inst_pluginid = pluginid

            # -------------------------------- PCMSynth --------------------------------
            if machine['id'] == 'PCMS':
                middlenote = 0
                track_obj.params.add('usemasterpitch', True, 'bool')
                if len(machine['regions']) == 1:
                    singlewav = machine['regions'][0]
                    if singlewav['key_lo'] == 24 and singlewav['key_hi'] == 108: isMultiSampler = False
                    else: isMultiSampler = True
                else: isMultiSampler = True

                if not isMultiSampler:
                    singlewav = machine['regions'][0]

                    sampleref = machid + '_PCMSynth_0'
                    wave_path = samplefolder+sampleref+'.wav'

                    loopdata = None
                    if singlewav['mode'] != 0 and singlewav['mode'] != 1: loopdata = {'loop':[singlewav['start'], singlewav['end']]}
                    if singlewav['samp_ch'] != 0: audio_wav.generate(wave_path, singlewav['samp_data'], singlewav['samp_ch'], singlewav['samp_hz'], 16, loopdata)
                    
                    plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'single')
                    sampleref_obj = convproj_obj.add_sampleref(sampleref, wave_path)

                    plugin_obj.samplerefs['sample'] = sampleref
                    middlenote += singlewav['key_root']-60
                    plugin_obj.datavals.add('point_value_type', "samples")
                    data_start, data_end, data_trigger, data_loopdata = loopmode_cvpj(singlewav)
                    plugin_obj.datavals.add('start', data_start)
                    plugin_obj.datavals.add('end', data_end)
                    plugin_obj.datavals.add('trigger', data_trigger)
                    plugin_obj.datavals.add('loop', data_loopdata)

                else:
                    plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'multi')
                    for samplecount, singlewav in enumerate(machine['regions']):
                        loopdata = None
                        if singlewav['mode'] != 0 and singlewav['mode'] != 1: loopdata = {'loop':[singlewav['start'], singlewav['end']]}
                        sampleref = machid + '_PCMSynth_'+str(samplecount)
                        wave_path = samplefolder+sampleref+'.wav'
                        audio_wav.generate(wave_path, singlewav['samp_data'], singlewav['samp_ch'], singlewav['samp_hz'], 16, loopdata)
                        convproj_obj.add_sampleref(sampleref, wave_path)
                        regionparams = {}
                        regionparams['middlenote'] = singlewav['key_root']-60
                        regionparams['volume'] = singlewav['volume']
                        regionparams['pan'] = (singlewav['pan']-0.5)*2
                        regionparams['sampleref'] = sampleref
                        regionparams['start'], regionparams['end'], regionparams['trigger'], regionparams['loop'] = loopmode_cvpj(singlewav)
                        plugin_obj.regions.add(singlewav['key_lo']-60, singlewav['key_hi']-60, regionparams)

                pcms_c = machine['controls']

                middlenote += int(pcms_c[1]*12)
                middlenote += int(pcms_c[2])

                track_obj.params.add('pitch', pcms_c[3], 'float')
                track_obj.datavals.add('middlenote', -middlenote)
                plugin_obj.env_asdr_add('volume', 0, pcms_c[5], 0, pcms_c[6], pcms_c[7], pcms_c[8], 1)

            # -------------------------------- BeatBox --------------------------------
            elif machine['id'] == 'BBOX':
                plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'multi')
                track_obj.params.add('usemasterpitch', False, 'bool')
                samplecount = 0
                for samplecount, bbox_sample in enumerate(machine['samples']):
                    sampleref = machid + '_BeatBox_'+str(samplecount)
                    wave_path = samplefolder+sampleref+'.wav'
                    if bbox_sample['chan'] != 0 and bbox_sample['hz'] != 0: audio_wav.generate(wave_path, bbox_sample['data'], bbox_sample['chan'], bbox_sample['hz'], 16, None)
                    convproj_obj.add_sampleref(sampleref, wave_path)
                    regionparams = {}
                    regionparams['middlenote'] = samplecount-12
                    regionparams['sampleref'] = sampleref
                    regionparams['start'] = 0
                    regionparams['end'] = bbox_sample['len']
                    regionparams['trigger'] = 'oneshot'
                    regionparams['loop'] = {'enabled': 0}
                    plugin_obj.regions.add(samplecount-12, samplecount-12, regionparams)
            elif machine['id'] == 'NULL':
                pass
            else:
                plugin_obj = convproj_obj.add_plugin(pluginid, 'native-caustic', machine['id'])
                if 'controls' in machine: 
                    paramlist = dataset.params_list('plugin_inst', machine['id'])

                    if paramlist != None: 
                        for paramid in paramlist:
                            paramdata = dataset.params_i_get('plugin_inst', machine['id'], paramid)
                            plugin_obj.add_from_dset(str(paramid), machine['controls'][int(paramid)], dataset, 'plugin_inst', machine['id'])

                if 'customwaveform1' in machine: 
                    customwaveform1 = list(struct.unpack("<"+("h"*660), machine['customwaveform1']))
                    wave_obj = plugin_obj.wave_add('customwaveform1')
                    wave_obj.set_all_range(customwaveform1, -157, 157)
                    
                if 'customwaveform2' in machine: 
                    customwaveform2 = list(struct.unpack("<"+("h"*660), machine['customwaveform2']))
                    wave_obj = plugin_obj.wave_add('customwaveform2')
                    wave_obj.set_all_range(customwaveform2, -157, 157)

            track_obj.params.add('vol', mach_mixer_vol[machnum-1], 'float')
            track_obj.params.add('pan', mach_mixer_pan[machnum-1], 'float')
            track_obj.params.add('enabled', int(not bool(mach_mixer_mute[machnum-1])), 'bool')
            track_obj.params.add('solo', mach_mixer_solo[machnum-1], 'bool')

            if machine['id'] != 'NULL':
                if 'patterns' in machine:
                    patterns = machine['patterns']
                    for pattern in patterns:
                        patid = pattern
                        causticpattern = patterns[pattern]
                        nle_obj = track_obj.add_notelistindex(patid)
                        nle_obj.visual.name = pattern
                        parse_notelist(nle_obj.notelist, causticpattern)

            if machnum in CausticData['EFFX']: 
                add_caustic_fx(convproj_obj, track_obj, CausticData['EFFX'][machnum], 'machine'+str(machnum))

            slot_mixereqfxslotdata = {}
            slot_mixereqfxslotdata['bass'] = mach_mixer_eq_low[machnum-1]
            slot_mixereqfxslotdata['mid'] = mach_mixer_eq_mid[machnum-1]
            slot_mixereqfxslotdata['high'] = mach_mixer_eq_high[machnum-1]

            track_obj.sends.add('master_delay', cvpj_trackid+'_send_delay', mach_mixer_send_delay[machnum-1])
            track_obj.sends.add('master_reverb', cvpj_trackid+'_send_reverb', mach_mixer_send_reverb[machnum-1])

            mixereq_plugid = 'machine'+str(machnum)+'_eq'
            plugin_obj = convproj_obj.add_plugin(mixereq_plugid, 'native-caustic', 'mixer_eq')
            plugin_obj.visual.name = 'Mixer EQ'
            plugin_obj.visual.color = [0.67, 0.67, 0.67]
            plugin_obj.params.add('bass', mach_mixer_eq_low[machnum-1], 'float')
            plugin_obj.params.add('mid', mach_mixer_eq_mid[machnum-1], 'float')
            plugin_obj.params.add('high', mach_mixer_eq_high[machnum-1], 'float')
            track_obj.fxslots_audio.append(mixereq_plugid)

            width_plugid = 'machine'+str(machnum)+'_width'
            plugin_obj = convproj_obj.add_plugin(width_plugid, 'native-caustic', 'width')
            plugin_obj.visual.name = 'Width'
            plugin_obj.visual.color = [0.66, 0.61, 0.76]
            plugin_obj.params.add('width', mach_mixer_width[machnum-1], 'float')
            track_obj.fxslots_audio.append(width_plugid)
            
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

            patmeasures = machines[SEQNe[0]]['patterns'][t_patid]['measures']*16 if 'patterns' in machines[SEQNe[0]] else 16

            if SEQNe_type == 2:
                cuttype = 'None'
                cutdata = {}
                if patmeasures != 0: 
                    cuttype = 'cut'
                    cutdata = {'type': 'loop', 'loopend': patmeasures}
                if str(SEQNe_mach) not in t_track_placements: t_track_placements[str(SEQNe_mach)] = []
                t_track_placements[str(SEQNe_mach)].append([SEQNe_pos, SEQNe_len, t_patid, cuttype, cutdata])

                if 'patterns' in machines[SEQNe[0]]:
                    autodata = machines[SEQNe[0]]['patterns'][t_patid]['auto']
                    for autoid in autodata:
                        pat_auto_place(convproj_obj, SEQNe_pos, SEQNe_len, autodata[autoid], ['plugin', 'machine'+str(SEQNe_mach), str(autoid)])

        for t_track_placement in t_track_placements:
            for t_pl in t_track_placements[t_track_placement]:
                track_found, track_obj = convproj_obj.find_track('MACH'+str(t_track_placement))
                if track_found: 
                    placement_obj = track_obj.placements.add_notes()
                    placement_obj.position = t_pl[0]
                    placement_obj.duration = t_pl[1]
                    placement_obj.cut_type = t_pl[3]
                    placement_obj.cut_data = t_pl[4]
                    placement_obj.fromindex = t_pl[2]

        for point in SEQN_tempo: convproj_obj.add_autopoint(['main', 'bpm'], 'float', point[0]*4, point[1], 'normal')

        #'machine'+machid

        for machnum in range(14):
            for autoname in AUTO_data['MACH_'+str(machnum+1)]:
                convproj_obj.add_autopoints_twopoints(['plugin', 'machine'+str(machnum+1), str(autoname)], 'float', AUTO_data['MACH_'+str(machnum+1)][autoname])

        for mixernum in range(2):
            mixerid = 'MIXER_'+str(mixernum+1)
            for machnum in range(7):
                auto_machid = machnum+1+(mixernum*7)
                if machnum in AUTO_data[mixerid]: 
                    convproj_obj.add_autopoints_twopoints(['track', 'MACH'+str(auto_machid), 'vol'], 'float', AUTO_data[mixerid][machnum])
                if (machnum*2)+8 in AUTO_data[mixerid]: 
                    convproj_obj.add_autopoints_twopoints(['send', 'MACH'+str(auto_machid)+'_send_delay', 'amount'], 'float', AUTO_data[mixerid][(machnum*2)+8])
                if (machnum*2)+9 in AUTO_data[mixerid]: 
                    convproj_obj.add_autopoints_twopoints(['send', 'MACH'+str(auto_machid)+'_send_reverb', 'amount'], 'float', AUTO_data[mixerid][(machnum*2)+9])
                if machnum+24 in AUTO_data[mixerid]: 
                    convproj_obj.add_autopoints_twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'bass'], 'float', AUTO_data[mixerid][machnum+24])
                if machnum+32 in AUTO_data[mixerid]: 
                    convproj_obj.add_autopoints_twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'mid'], 'float', AUTO_data[mixerid][machnum+32])
                if machnum+40 in AUTO_data[mixerid]: 
                    convproj_obj.add_autopoints_twopoints(['plugin', 'machine'+str(auto_machid)+'_eq', 'high'], 'float', AUTO_data[mixerid][machnum+40])
                if machnum+64 in AUTO_data[mixerid]: 
                    t_auto = AUTO_data[mixerid][machnum+64]
                    for x in t_auto: x[0] = (x[0]*2)-0.5
                    convproj_obj.add_autopoints_twopoints(['track', 'MACH'+str(auto_machid), 'pan'], 'float', t_auto)
                if machnum+72 in AUTO_data[mixerid]: 
                    convproj_obj.add_autopoints_twopoints(['plugin', 'machine'+str(auto_machid)+'_width', 'width'], 'float', AUTO_data[mixerid][machnum+72])

        for mixernum in range(2):
            mixerid = 'FX_'+str(mixernum+1)
            for autonum in AUTO_data[mixerid]:
                autofx_num = (autonum//16)
                autofx_slot = (autonum//8)-(autofx_num*2)
                autofx_ctrl = autonum-(autofx_slot*8)-(autofx_num*16)
                cvpj_fx_autoid = 'machine'+str(autofx_num+1+(mixernum*7))+'_slot'+str(autofx_slot+1)

                if autofx_ctrl == 5: 
                    t_auto = AUTO_data[mixerid][autonum]
                    for x in t_auto: x[0] = (x[0]*-1)-1
                    convproj_obj.add_autopoints_twopoints(['slot', cvpj_fx_autoid, 'enabled'], 'bool', t_auto)
                else: 
                    convproj_obj.add_autopoints_twopoints(['plugin', cvpj_fx_autoid, str(autofx_ctrl)], 'float', AUTO_data[mixerid][autonum])

        master_fxchaindata = []

        if 'EFFX' in MSTR: add_caustic_fx(convproj_obj, convproj_obj.track_master, MSTR['EFFX'], 'master_slot')

        for fxid in ['master_delay','master_reverb','master_eq','master_limiter']:

            plugin_obj = convproj_obj.add_plugin(fxid, 'native-caustic', fxid)
            plugin_obj.visual.name, plugin_obj.visual.color = dataset.object_get_name_color('plugin_master_fx', fxid)

            if fxid in ['master_delay','master_reverb']:
                return_obj = convproj_obj.track_master.add_return(fxid)
                return_obj.visual.name = plugin_obj.visual.name
                return_obj.visual.color = plugin_obj.visual.color
                return_obj.fxslots_audio.append(fxid)
            else:
                convproj_obj.track_master.fxslots_audio.append(fxid)

            if fxid == 'master_delay': plugin_obj.fxdata_add(not bool(MSTR['CCOL'][40]), 1)
            if fxid == 'master_reverb': plugin_obj.fxdata_add(not bool(MSTR['CCOL'][41]), 1)
            if fxid == 'master_eq': plugin_obj.fxdata_add(not bool(MSTR['CCOL'][42]), 1)
            if fxid == 'master_limiter': plugin_obj.fxdata_add(not bool(MSTR['CCOL'][43]), 1)

            paramlist = dataset.params_list('plugin_master_fx', fxid)
            if paramlist != None:
                for paramid in paramlist: 
                    paramid = int(paramid)
                    paramval = MSTR['CCOL'][paramid] if paramid in MSTR['CCOL'] else None
                    plugin_obj.add_from_dset(str(paramid), paramval, dataset, 'plugin_master_fx', fxid)

        for autonum in AUTO_data['MASTER']:
            if autonum in MSTR['CCOL']:
                t_fxtypeparam = MSTR['CCOL'][autonum]
                defparams = params_i_get('plugin_master_fx', fxid, str(autonum))
                if 1 <= autonum <= 9: convproj_obj.add_autopoints_twopoints(['plugin', 'master_limiter', str(autonum)], defparams[1], AUTO_data['MASTER'][autonum])
                if 16 <= autonum <= 25: convproj_obj.add_autopoints_twopoints(['plugin', 'master_reverb', str(autonum)], defparams[1], AUTO_data['MASTER'][autonum])
                if 30 <= autonum <= 34: convproj_obj.add_autopoints_twopoints(['plugin', 'master_eq', str(autonum)], defparams[1], AUTO_data['MASTER'][autonum])
                if 35 <= autonum <= 38: convproj_obj.add_autopoints_twopoints(['plugin', 'master_limiter', str(autonum)], defparams[1], AUTO_data['MASTER'][autonum])
                elif autonum == 39: convproj_obj.add_autopoints_twopoints(['master', 'vol'], 'float', AUTO_data['MASTER'][autonum])
                #elif autonum == 40: convproj_obj.add_autopoints_twopoints(['slot', 'master_delay'], 'bool', AUTO_data['MASTER'][autonum])
                #elif autonum == 41: convproj_obj.add_autopoints_twopoints(['slot', 'master_reverb'], 'bool', AUTO_data['MASTER'][autonum])
                #elif autonum == 42: convproj_obj.add_autopoints_twopoints(['slot', 'master_eq'], 'bool', AUTO_data['MASTER'][autonum])
                #elif autonum == 43: convproj_obj.add_autopoints_twopoints(['slot', 'master_limiter'], 'bool', AUTO_data['MASTER'][autonum])

            elif autonum >= 64:
                autonum_calc = autonum - 64
                autofx_slot = (autonum_calc//8)
                autofx_ctrl = autonum-(autofx_slot*8)
                cvpj_fx_autoid = 'master_slot'+str(autofx_slot+1)

                if autofx_ctrl-64 == 5:
                    t_auto = AUTO_data['MASTER'][autonum]
                    for x in t_auto: x[0] = (x[0]*-1)-1
                    convproj_obj.add_autopoints_twopoints(['slot', cvpj_fx_autoid, 'enabled'], 'bool', t_auto)
                else: 
                    convproj_obj.add_autopoints_twopoints(['plugin', cvpj_fx_autoid, str(autofx_ctrl-64)], 'float', AUTO_data['MASTER'][autonum])

        convproj_obj.track_master.params.add('vol', MSTR['CCOL'][39], 'float')
        convproj_obj.track_master.visual.name = 'Master'
        convproj_obj.track_master.visual.color = [0.52, 0.52, 0.52]
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.params.add('bpm', CausticData['Tempo'], 'float')
        convproj_obj.timesig = [CausticData['Numerator'], 4]

