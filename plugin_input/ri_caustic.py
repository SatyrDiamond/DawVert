# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects_file import audio_wav
from functions import data_bytes
from functions import xtramath
from objects_file import proj_caustic
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
patids = []
for x in patletters:
    for v in range(16):
        patids.append(x+str(v+1))

def add_caustic_fx(convproj_obj, track_obj, caustic_fx, start_plugid):
    for slotnum, caustic_fx_data in enumerate(caustic_fx):
        controls_data = caustic_fx_data.controls.data

        fx_pluginid = start_plugid+'_slot'+str(slotnum+1)

        if caustic_fx_data.fx_type not in [4294967295, -1]:
            fxtype = caustic_fxtype[caustic_fx_data.fx_type]
            plugin_obj = convproj_obj.add_plugin(fx_pluginid, 'native-caustic', fxtype)
            plugin_obj.role = 'effect'
            plugin_obj.fxdata_add(bool(not int(controls_data[5])), 1)
            plugin_obj.visual.name, plugin_obj.visual.color = dataset.object_get_name_color('plugin_fx', fxtype)

            paramlist = dataset.params_list('plugin_fx', fxtype)

            if paramlist != None:
                for paramid in paramlist: 
                    if paramid != '5':
                        paramid = int(paramid)
                        paramval = controls_data[paramid] if paramid in controls_data else 0
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

class input_cvpj_r(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'caustic'
    def gettype(self): return 'ri'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Caustic 3'
        dawinfo_obj.file_ext = 'caustic'
        dawinfo_obj.placement_cut = True
        dawinfo_obj.placement_loop = ['loop']
        dawinfo_obj.audio_stretch = ['warp']
        dawinfo_obj.auto_types = ['pl_points', 'nopl_points']
        dawinfo_obj.plugin_included = ['native-caustic','sampler:single','sampler:multi']
        dawinfo_obj.fxchain_mixer = True
    def supported_autodetect(self): return False
    def parse(self, convproj_obj, input_file, dv_config):
        global dataset

        convproj_obj.type = 'ri'
        convproj_obj.set_timings(1, True)

        dataset = dv_dataset.dataset('./data_dset/caustic.dset')

        f = open(input_file, 'rb')
        caustic_data = proj_caustic.caustic_project(f)

        samplefolder = dv_config.path_samples_extracted

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

        for mixnum, ctrldata in enumerate(caustic_data.mixr.controls):
            for paramnum in range(7): 
                paramnumid = paramnum+(mixnum*7)
                mach_mixer_vol[paramnumid] = ctrldata.data[paramnum]
                mach_mixer_pan[paramnumid] = (ctrldata.data[paramnum+64]-0.5)*2
                mach_mixer_width[paramnumid] = ctrldata.data[paramnum+72]
                mach_mixer_send_delay[paramnumid] = ctrldata.data[(paramnum*2)+8]
                mach_mixer_send_reverb[paramnumid] = ctrldata.data[(paramnum*2)+9]
                mach_mixer_eq_low[paramnumid] = ctrldata.data[paramnum+24]
                mach_mixer_eq_mid[paramnumid] = ctrldata.data[paramnum+32]
                mach_mixer_eq_high[paramnumid] = ctrldata.data[paramnum+40]

        for paramnum in range(14): 
            mach_mixer_mute[paramnum] = caustic_data.mixr.solo_mute[paramnum*2]
            mach_mixer_solo[paramnum] = caustic_data.mixr.solo_mute[(paramnum*2)+1]

        cvpj_tracks = []

        for machnum, machine in enumerate(caustic_data.machines):
            machid = str(machnum)
            pluginid = 'machine'+machid
            cvpj_trackid = 'MACH'+machid

            dset_name, cvpj_trackcolor = dataset.object_get_name_color('plugin_inst', machine.mach_id)

            track_obj = convproj_obj.add_track(cvpj_trackid, 'instrument', 1, True)
            track_obj.visual.name = machine.name if machine.name else dset_name
            track_obj.visual.color = cvpj_trackcolor
            track_obj.inst_pluginid = pluginid
            cvpj_tracks.append(track_obj)

            # -------------------------------- PCMSynth --------------------------------
            if machine.mach_id == 'PCMS':
                middlenote = 0
                track_obj.params.add('usemasterpitch', True, 'bool')
                if len(machine.samples) == 1:
                    singlewav = machine.samples[0]
                    if singlewav[0]['key_lo'] == 24 and singlewav[0]['key_hi'] == 108: isMultiSampler = False
                    else: isMultiSampler = True
                else: isMultiSampler = True

                if not isMultiSampler:
                    region_data, wave_data = machine.samples[0]

                    sampleref = machid + '_PCMSynth_0'
                    wave_path = samplefolder+sampleref+'.wav'

                    if region_data['samp_ch'] != 0: 
                        wavfile_obj = audio_wav.wav_main()
                        wavfile_obj.set_freq(region_data['samp_hz'])
                        wavfile_obj.data_add_data(16, region_data['samp_ch'], False, wave_data)
                        if region_data['mode'] not in [0, 1]: wavfile_obj.add_loop(region_data['start'], region_data['end'])
                        wavfile_obj.write(wave_path)

                    plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'single')
                    plugin_obj.role = 'synth'
                    sampleref_obj = convproj_obj.add_sampleref(sampleref, wave_path)

                    plugin_obj.samplerefs['sample'] = sampleref
                    middlenote += region_data['key_root']-60
                    plugin_obj.datavals.add('point_value_type', "samples")
                    data_start, data_end, data_trigger, data_loopdata = loopmode_cvpj(region_data)
                    plugin_obj.datavals.add('start', data_start)
                    plugin_obj.datavals.add('end', data_end)
                    plugin_obj.datavals.add('trigger', data_trigger)
                    plugin_obj.datavals.add('loop', data_loopdata)

                else:
                    plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'multi')
                    plugin_obj.role = 'synth'
                    for samplecount, data in enumerate(machine.samples):
                        region_data, wave_data = data
                        loopdata = None
                        sampleref = machid + '_PCMSynth_'+str(samplecount)
                        wave_path = samplefolder+sampleref+'.wav'
                        wavfile_obj = audio_wav.wav_main()
                        wavfile_obj.set_freq(region_data['samp_hz'])
                        wavfile_obj.data_add_data(16, region_data['samp_ch'], False, wave_data)
                        wavfile_obj.write(wave_path)
                        if region_data['mode'] not in [0, 1]: wavfile_obj.add_loop(region_data['start'], region_data['end'])
                        convproj_obj.add_sampleref(sampleref, wave_path)
                        regionparams = {}
                        regionparams['middlenote'] = region_data['key_root']-60
                        regionparams['volume'] = region_data['volume']
                        regionparams['pan'] = (region_data['pan']-0.5)*2
                        regionparams['sampleref'] = sampleref
                        regionparams['start'], regionparams['end'], regionparams['trigger'], regionparams['loop'] = loopmode_cvpj(region_data)
                        plugin_obj.regions.add(region_data['key_lo']-60, region_data['key_hi']-60, regionparams)

                if machine.samples:
                    pcms_c = machine.controls.data

                    middlenote += int(pcms_c[1]*12)
                    middlenote += int(pcms_c[2])

                    track_obj.params.add('pitch', pcms_c[3], 'float')
                    track_obj.datavals.add('middlenote', -middlenote)
                    plugin_obj.env_asdr_add('vol', 0, pcms_c[5], 0, pcms_c[6], pcms_c[7], pcms_c[8], 1)

            # -------------------------------- BeatBox --------------------------------
            elif machine.mach_id == 'BBOX':
                plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'multi')
                plugin_obj.role = 'synth'
                track_obj.params.add('usemasterpitch', False, 'bool')
                samplecount = 0
                for samplecount, bbox_sample in enumerate(machine.samples):
                    region_data, wave_data = bbox_sample
                    sampleref = machid + '_BeatBox_'+str(samplecount)
                    wave_path = samplefolder+sampleref+'.wav'
                    if region_data['chan'] != 0 and region_data['hz'] != 0: 
                        wavfile_obj = audio_wav.wav_main()
                        wavfile_obj.set_freq(region_data['hz'])
                        wavfile_obj.data_add_data(16, region_data['chan'], False, wave_data)
                        wavfile_obj.write(wave_path)
                    convproj_obj.add_sampleref(sampleref, wave_path)
                    regionparams = {}
                    regionparams['middlenote'] = samplecount-12
                    regionparams['sampleref'] = sampleref
                    regionparams['start'] = 0
                    regionparams['end'] = region_data['len']
                    regionparams['trigger'] = 'oneshot'
                    regionparams['loop'] = {'enabled': 0}
                    plugin_obj.regions.add(samplecount-12, samplecount-12, regionparams)
            elif machine.mach_id == 'NULL':
                pass
            else:
                plugin_obj = convproj_obj.add_plugin(pluginid, 'native-caustic', machine.mach_id)
                plugin_obj.role = 'synth'

                paramlist = dataset.params_list('plugin_inst', machine.mach_id)

                if paramlist != None: 
                    for paramid in paramlist:
                        paramdata = dataset.params_i_get('plugin_inst', machine.mach_id, paramid)
                        plugin_obj.add_from_dset(str(paramid), machine.controls.data[int(paramid)], dataset, 'plugin_inst', machine.mach_id)

                if machine.customwaveform1: 
                    customwaveform1 = list(struct.unpack("<"+("h"*660), machine.customwaveform1))
                    wave_obj = plugin_obj.wave_add('customwaveform1')
                    wave_obj.set_all_range(customwaveform1, -157, 157)
                    
                if machine.customwaveform2: 
                    customwaveform2 = list(struct.unpack("<"+("h"*660), machine.customwaveform2))
                    wave_obj = plugin_obj.wave_add('customwaveform2')
                    wave_obj.set_all_range(customwaveform2, -157, 157)

            track_obj.params.add('vol', mach_mixer_vol[machnum], 'float')
            track_obj.params.add('pan', mach_mixer_pan[machnum], 'float')
            track_obj.params.add('enabled', int(not bool(mach_mixer_mute[machnum])), 'bool')
            track_obj.params.add('solo', mach_mixer_solo[machnum], 'bool')

            if machine.mach_id != 'NULL':
                for num, pattern in enumerate(machine.patterns.data):
                    patid = patids[num]
                    nle_obj = track_obj.add_notelistindex(patid)
                    nle_obj.visual.name = patid
                    for n in pattern.notes: nle_obj.notelist.add_r(n.pos, n.dur, n.key-60, n.vol, {})

            c_fxdata = caustic_data.effx.fxslots[machnum*2:machnum*2+2]
            add_caustic_fx(convproj_obj, track_obj, c_fxdata, 'machine'+str(machnum))

            track_obj.sends.add('master_delay', cvpj_trackid+'_send_delay', mach_mixer_send_delay[machnum])
            track_obj.sends.add('master_reverb', cvpj_trackid+'_send_reverb', mach_mixer_send_reverb[machnum])

            mixereq_plugid = 'machine'+str(machnum)+'_eq'
            plugin_obj = convproj_obj.add_plugin(mixereq_plugid, 'native-caustic', 'mixer_eq')
            plugin_obj.visual.name = 'Mixer EQ'
            plugin_obj.visual.color = [0.67, 0.67, 0.67]
            plugin_obj.params.add('bass', mach_mixer_eq_low[machnum], 'float')
            plugin_obj.params.add('mid', mach_mixer_eq_mid[machnum], 'float')
            plugin_obj.params.add('high', mach_mixer_eq_high[machnum], 'float')
            track_obj.fxslots_audio.append(mixereq_plugid)

            width_plugid = 'machine'+str(machnum)+'_width'
            plugin_obj = convproj_obj.add_plugin(width_plugid, 'native-caustic', 'width')
            plugin_obj.visual.name = 'Width'
            plugin_obj.visual.color = [0.66, 0.61, 0.76]
            plugin_obj.params.add('width', mach_mixer_width[machnum], 'float')
            track_obj.fxslots_audio.append(width_plugid)
        
        for x in caustic_data.seqn.parts:
            x.pat = x.pat%100 + (x.pat//100)*16

            patmeasures = caustic_data.machines[x.mach].patterns.data[x.pat].measures*16
            autodata = caustic_data.machines[x.mach].patterns.auto[x.pat]
            if patmeasures == 0: patmeasures = 16
            patid = patids[x.pat]

            placement_obj = cvpj_tracks[x.mach].placements.add_notes_indexed()
            placement_obj.position = x.pos
            placement_obj.duration = x.dur
            placement_obj.cut_type = 'loop'
            placement_obj.cut_data = {'loopend': patmeasures/4}
            placement_obj.fromindex = patid

            if autodata:
                cutpoints = xtramath.cutloop(x.pos, x.dur, 0, 0, patmeasures/4)

                for position, duration, loopstart, loopend in cutpoints:
                    for autoid, sauto in autodata.items():
                        autopl_obj = convproj_obj.automation.add_pl_points(['plugin', 'machine'+str(x.mach+1), str(autoid)], 'float')
                        autopl_obj.position = position
                        autopl_obj.duration = duration
                        autopl_obj.data.from_steps(sauto.data, sauto.smooth, 1)

        for pos, val in caustic_data.seqn.tempoauto: 
            convproj_obj.automation.add_autopoint(['main', 'bpm'], 'float', pos, val, 'normal')

        for machnum, machauto in enumerate(caustic_data.seqn.auto_mach):
            for ctrlid, s_machauto in machauto.data.items():
                convproj_obj.automation.add_autopoints_twopoints(['plugin', 'machine'+str(machnum+1), str(ctrlid)], 'float', s_machauto)

        for fxsetnum, machauto in enumerate(caustic_data.seqn.auto_mixer):
            fxsetnum = fxsetnum*7
            for ctrlid, s_machauto in machauto.data.items():
                ctrl_s, ctrl_g = ctrlid%8, ctrlid//8
                autoloc = None
                if ctrl_g == 0: autoloc = ['track', 'MACH'+str(ctrl_s+1+fxsetnum), 'vol']
                elif ctrl_g in [1,2]: 
                    basev = ctrlid-8
                    autoloc = ['send', 'MACH'+str((basev//2)+1+fxsetnum)+('_send_reverb' if basev%2 else '_send_delay'), 'amount']
                elif ctrl_g == 3: autoloc = ['plugin', 'machine'+str(ctrl_s+1+fxsetnum)+'_eq', 'bass']
                elif ctrl_g == 4: autoloc = ['plugin', 'machine'+str(ctrl_s+1+fxsetnum)+'_eq', 'mid']
                elif ctrl_g == 5: autoloc = ['plugin', 'machine'+str(ctrl_s+1+fxsetnum)+'_eq', 'high']
                elif ctrl_g == 8: autoloc = ['track', 'MACH'+str(ctrl_s+1+fxsetnum), 'pan']
                elif ctrl_g == 9: autoloc = ['plugin', 'machine'+str(ctrl_s+1+fxsetnum)+'_width', 'width']

                if autoloc: 
                    if ctrl_g == 8: 
                        for x in s_machauto: x[1] = (x[1]-0.5)*2
                    convproj_obj.automation.add_autopoints_twopoints(autoloc, 'float', s_machauto)

        for fxsetnum, machauto in enumerate(caustic_data.seqn.auto_fx):
            fxsetnum = fxsetnum*7
            for ctrlid, s_machauto in machauto.data.items():
                autofx_num = (ctrlid//16)
                autofx_slot = (ctrlid//8)-(autofx_num*2)
                autofx_ctrl = ctrlid-(autofx_slot*8)-(autofx_num*16)
                cvpj_fx_autoid = 'machine'+str(autofx_num+1+(fxsetnum))+'_slot'+str(autofx_slot+1)

                if autofx_ctrl == 5: 
                    t_auto = AUTO_data[mixerid][autonum]
                    for x in t_auto: x[1] = (x[1]*-1)-1
                    convproj_obj.automation.add_autopoints_twopoints(['slot', cvpj_fx_autoid, 'enabled'], 'bool', s_machauto)
                else: 
                    convproj_obj.automation.add_autopoints_twopoints(['plugin', cvpj_fx_autoid, str(autofx_ctrl)], 'float', s_machauto)

        master_fxchaindata = []

        add_caustic_fx(convproj_obj, convproj_obj.track_master, caustic_data.mstr.fxslots, 'master_slot')

        master_controls_data = caustic_data.mstr.controls.data

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

            if fxid == 'master_delay': plugin_obj.fxdata_add(not bool(master_controls_data[40]), 1)
            if fxid == 'master_reverb': plugin_obj.fxdata_add(not bool(master_controls_data[41]), 1)
            if fxid == 'master_eq': plugin_obj.fxdata_add(not bool(master_controls_data[42]), 1)
            if fxid == 'master_limiter': plugin_obj.fxdata_add(not bool(master_controls_data[43]), 1)

            paramlist = dataset.params_list('plugin_master_fx', fxid)
            if paramlist != None:
                for paramid in paramlist: 
                    paramid = int(paramid)
                    paramval = master_controls_data[paramid] if paramid in master_controls_data else None
                    plugin_obj.add_from_dset(str(paramid), paramval, dataset, 'plugin_master_fx', fxid)

        for ctrlid, s_machauto in caustic_data.seqn.auto_master.data.items():
            autoloc = None
            if 1 <= ctrlid <= 9: autoloc = ['plugin', 'master_delay', str(ctrlid)]
            elif 16 <= ctrlid <= 25: autoloc = ['plugin', 'master_reverb', str(ctrlid)]
            elif 30 <= ctrlid <= 34: autoloc = ['plugin', 'master_eq', str(ctrlid)]
            elif 35 <= ctrlid <= 38: autoloc = ['plugin', 'master_limiter', str(ctrlid)]
            elif ctrlid == 39: autoloc = ['master', 'vol']
            elif ctrlid >= 64:
                autonum_calc = ctrlid - 64
                autofx_slot = (autonum_calc//8)
                autofx_ctrl = ctrlid-(autofx_slot*8)
                cvpj_fx_autoid = 'master_slot'+str(autofx_slot+1)

                if autofx_ctrl-64 == 5:
                    for x in s_machauto: x[1] = (x[1]*-1)-1
                    autoloc = ['slot', cvpj_fx_autoid, 'enabled']
                else:  autoloc = ['plugin', cvpj_fx_autoid, str(autofx_ctrl-64)]

            if autoloc: convproj_obj.automation.add_autopoints_twopoints(autoloc, 'float', s_machauto)

        convproj_obj.track_master.params.add('vol', master_controls_data[39], 'float')
        convproj_obj.track_master.visual.name = 'Master'
        convproj_obj.track_master.visual.color = [0.52, 0.52, 0.52]
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.params.add('bpm', caustic_data.tempo, 'float')
        convproj_obj.timesig = [caustic_data.numerator, 4]

