# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from objects import dv_dataset
import json
import plugin_input
import xml.etree.ElementTree as ET
import zipfile

def getvalue(xmltag, xmlname, fallbackval): 
    if xmltag.findall(xmlname) != []: return xmltag.findall(xmlname)[0].text.strip()
    else: return fallbackval

def getbool(input_val):
    if input_val == 'true': return True
    if input_val == 'false': return False

def setasdr(i_attack, i_decay, i_release, i_sustain):
    out_attack = i_attack
    out_decay = i_decay
    out_release = i_release
    out_sustain = i_sustain
    if out_decay == 0: out_sustain = 1
    return out_attack, out_decay, out_release, out_sustain

audiosanua_device_id = ['fm', 'analog']

def make_fxslot(convproj_obj, x_device_sound, fx_type, as_device):
    fx_wet = 1
    if fx_type == 'chorus':
        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-audiosauna', 'chorus')
        plugin_obj.role = 'effect'
        plugin_obj.visual.name = 'Chorus'

        if as_device in [0,1]: 
            fx_wet = float(getvalue(x_device_sound, 'chorusMix', 0))/100
            chorus_size = float(getvalue(x_device_sound, 'chorusLevel', 0))/100
        else: 
            fx_wet = float(getvalue(x_device_sound, 'chorusDryWet', 0))/100
            chorus_size = float(getvalue(x_device_sound, 'chorusSize', 0))/100

        plugin_obj.params.add_named("speed", float(getvalue(x_device_sound, 'chorusSpeed', 0))/100, 'float', 'Speed')
        plugin_obj.params.add_named("size", chorus_size, 'float', 'Size')
        plugin_obj.fxdata_add(True, fx_wet)

        return pluginid

    if fx_type == 'distortion':
        modulate = float(getvalue(x_device_sound, 'driveModul' if as_device in [0,1] else 'modulate' , 0))/100
        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-audiosauna', 'distortion')
        plugin_obj.role = 'effect'
        plugin_obj.visual.name = 'Distortion'
        plugin_obj.params.add_named("overdrive", float(getvalue(x_device_sound, 'overdrive', 0))/100, 'float', 'Overdrive')
        plugin_obj.params.add_named("modulate", modulate, 'float', 'Modulate')
        return pluginid

    if fx_type == 'bitcrush':
        bitrateval = float(getvalue(x_device_sound, 'bitrate', 0))
        if bitrateval != 0.0: 
            plugin_obj, pluginid = convproj_obj.add_plugin_genid('universal', 'bitcrush')
            plugin_obj.role = 'effect'
            plugin_obj.visual.name = 'Bitcrush'
            plugin_obj.params.add("bits", 16, 'float')
            plugin_obj.params.add("freq", 22050/bitrateval, 'float')
            return pluginid

    if fx_type == 'tape_delay':
        dlyTime = float(getvalue(x_device_sound, 'dlyTime', 0))
        dlyDamage = float(getvalue(x_device_sound, 'dlyDamage', 0))/100
        dlyFeed = float(getvalue(x_device_sound, 'dlyFeed', 0))/100
        dlySync = getbool(getvalue(x_device_sound, 'dlySync', 0))

        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-audiosauna', 'tape_delay')
        plugin_obj.role = 'effect'
        plugin_obj.visual.name = 'Tape Delay'

        timing_obj = plugin_obj.timing_add('main')
        if dlySync: 
            if dlyTime == 0: timing_obj.set_frac(1, 64, '', convproj_obj)
            if dlyTime == 1: timing_obj.set_frac(1, 64, 't', convproj_obj)
            if dlyTime == 2: timing_obj.set_frac(1, 64, 'd', convproj_obj)
            if dlyTime == 3: timing_obj.set_frac(1, 32, '', convproj_obj)
            if dlyTime == 4: timing_obj.set_frac(1, 32, 't', convproj_obj)
            if dlyTime == 5: timing_obj.set_frac(1, 32, 'd', convproj_obj)
            if dlyTime == 6: timing_obj.set_frac(1, 16, '', convproj_obj)
            if dlyTime == 7: timing_obj.set_frac(1, 16, 't', convproj_obj)
            if dlyTime == 8: timing_obj.set_frac(1, 16, 'd', convproj_obj)
            if dlyTime == 9: timing_obj.set_frac(1, 8, '', convproj_obj)
            if dlyTime == 10: timing_obj.set_frac(1, 8, 't', convproj_obj)
            if dlyTime == 11: timing_obj.set_frac(1, 8, 'd', convproj_obj)
            if dlyTime == 12: timing_obj.set_frac(1, 4, '', convproj_obj)
            if dlyTime == 13: timing_obj.set_frac(1, 4, 't', convproj_obj)
            if dlyTime == 14: timing_obj.set_frac(1, 4, 'd', convproj_obj)
            if dlyTime == 15: timing_obj.set_frac(1, 2, '', convproj_obj)
            if dlyTime == 16: timing_obj.set_frac(1, 2, 't', convproj_obj)
            if dlyTime == 17: timing_obj.set_frac(1, 2, 'd', convproj_obj)
            if dlyTime == 18: timing_obj.set_frac(1, 1, '', convproj_obj)
        else: 
            timing_obj.set_seconds(dlyTime)

        plugin_obj.params.add_named("time", dlyTime, 'float', "Time")
        plugin_obj.params.add_named("damage", dlyDamage, 'float', "Damage")
        plugin_obj.params.add_named("feedback", dlyFeed, 'float', "Feedback")
        plugin_obj.params.add_named("sync", dlySync, 'bool', "Sync")
        return pluginid

    if fx_type == 'reverb':
        rvbTime = float(getvalue(x_device_sound, 'rvbTime', 0))
        rvbFeed = float(getvalue(x_device_sound, 'rvbFeed', 0))/100
        rvbWidth = float(getvalue(x_device_sound, 'rvbWidth', 0))/100

        plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-audiosauna', 'reverb')
        plugin_obj.role = 'effect'
        plugin_obj.visual.name = 'Reverb'

        plugin_obj.params.add_named("time", rvbTime, 'float', 'Time')
        plugin_obj.params.add_named("feedback", rvbFeed, 'float', 'Feedback')
        plugin_obj.params.add_named("width", rvbWidth, 'float', 'Width')
        return pluginid

    if fx_type == 'amp':
        ampval = float(getvalue(x_device_sound, 'masterAmp', 100))/100
        print(ampval)
        if ampval != 1.0: 
            plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-audiosauna', 'amp')
            plugin_obj.role = 'effect'
            plugin_obj.visual.name = 'Amp'
            plugin_obj.params.add_named("level", ampval, 'float', 'Level')
            plugin_obj.fxdata_add(True, fx_wet)
            return pluginid
        

class input_audiosanua(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'audiosauna'
    def gettype(self): return 'r'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'AudioSauna'
        dawinfo_obj.file_ext = 'song'
        dawinfo_obj.placement_cut = True
        dawinfo_obj.audio_filetypes = ['wav', 'mp3']
        dawinfo_obj.plugin_included = ['native-audiosauna', 'sampler:multi', 'universal:bitcrush']
    def supported_autodetect(self): return True
    def detect(self, input_file): 
        try:
            zip_data = zipfile.ZipFile(input_file, 'r')
            if 'songdata.xml' in zip_data.namelist(): return True
            else: return False
        except:
            return False
    def parse(self, convproj_obj, input_file, dv_config):
        global cvpj_l
        zip_data = zipfile.ZipFile(input_file, 'r')

        convproj_obj.type = 'r'
        convproj_obj.set_timings(128, False)

        dataset = dv_dataset.dataset('./data_dset/audiosauna.dset')
        colordata = colors.colorset(dataset.colorset_e_list('track', 'main'))
        t_audiosanua_project = zip_data.read('songdata.xml')

        x_proj = ET.fromstring(t_audiosanua_project)
        x_proj_channels = x_proj.findall('channels')[0]
        x_proj_tracks = x_proj.findall('tracks')[0]
        x_proj_songPatterns = x_proj.findall('songPatterns')[0]
        x_proj_devices = x_proj.findall('devices')[0]

        convproj_obj.params.add('bpm', float(getvalue(x_proj, 'appTempo', 170)), 'float')

        xt_chan = x_proj_channels.findall('channel')
        xt_track = x_proj_tracks.findall('track')
        xt_pattern = x_proj_songPatterns.findall('pattern')
        xt_devices = x_proj_devices.findall('audioDevice')

        convproj_obj.track_master.visual.name = 'Master'
        convproj_obj.track_master.params.add('vol', int(getvalue(x_proj,'appMasterVolume',100))/100, 'float')

        return_obj = convproj_obj.track_master.add_return('audiosauna_send_tape_delay')
        return_obj.visual.name = 'Tape Delay'
        return_obj.params.add('vol', int(getvalue(x_proj,'dlyLevel',100))/100, 'float')
        return_obj.fxslots_audio.append(make_fxslot(convproj_obj, x_proj, 'tape_delay', None))

        return_obj = convproj_obj.track_master.add_return('audiosauna_send_reverb')
        return_obj.visual.name = 'Reverb'
        return_obj.params.add('vol', int(getvalue(x_proj,'rvbLevel',100))/100, 'float')
        return_obj.fxslots_audio.append(make_fxslot(convproj_obj, x_proj, 'reverb', None))

        # ------------------------------------------ tracks ------------------------------------------
        as_patt_notes = {}

        for x_track in xt_track:
            x_track_trackIndex = int(x_track.get('trackIndex'))
            xt_track_seqNote = x_track.findall('seqNote')
            for x_track_seqNote in xt_track_seqNote:
                as_note_patternId = int(x_track_seqNote.get('patternId'))
                as_note_startTick = int(x_track_seqNote.get('startTick'))
                as_note_endTick = int(x_track_seqNote.get('endTick'))
                as_note_noteLength = int(x_track_seqNote.get('noteLength'))
                as_note_pitch = int(x_track_seqNote.get('pitch'))
                as_note_noteVolume = int(x_track_seqNote.get('noteVolume'))
                as_note_noteCutoff = int(x_track_seqNote.get('noteCutoff'))
                if as_note_patternId not in as_patt_notes: as_patt_notes[as_note_patternId] = []
                as_patt_notes[as_note_patternId].append([as_note_startTick, as_note_endTick, as_note_noteLength, as_note_pitch, as_note_noteVolume, as_note_noteCutoff])

        # ------------------------------------------ channels ------------------------------------------
        for x_chan in xt_chan:
            as_channum = int(x_chan.get('channelNro'))
            cvpj_id = 'audiosanua'+str(as_channum)

            cvpj_tr_vol = int(x_chan.get('volume'))/100
            cvpj_tr_pan = int(x_chan.get('pan'))/100
            cvpj_tr_name = x_chan.get('name')
            cvpj_tr_mute = getbool(x_chan.get('mute'))
            cvpj_tr_solo = getbool(x_chan.get('solo'))

            cvpj_tr_color = colordata.getcolornum(as_channum)

            track_obj = convproj_obj.add_track(cvpj_id, 'instrument', 1, False)
            track_obj.visual.name = x_chan.get('name')
            track_obj.visual.color = colordata.getcolornum(as_channum)

            track_obj.params.add('vol', cvpj_tr_vol, 'float')
            track_obj.params.add('pan', cvpj_tr_pan, 'float')
            track_obj.params.add('enabled', not getbool(x_chan.get('mute')), 'bool')
            track_obj.params.add('solo', getbool(x_chan.get('solo')), 'bool')

            track_obj.sends.add('audiosauna_send_tape_delay', None, int(x_chan.get('delay'))/100)
            track_obj.sends.add('audiosauna_send_reverb', None, int(x_chan.get('reverb'))/100)

        # ------------------------------------------ patterns ------------------------------------------
        for x_pattern in xt_pattern:
            as_pattern_trackNro = int(x_pattern.get('trackNro'))
            as_pattern_patternId = int(x_pattern.get('patternId'))
            as_pattern_patternColor = int(x_pattern.get('patternColor'))
            as_pattern_startTick = int(x_pattern.get('startTick'))
            as_pattern_endTick = int(x_pattern.get('endTick'))
            as_pattern_patternLength = int(x_pattern.get('patternLength'))

            track_found, track_obj = convproj_obj.find_track('audiosanua'+str(as_pattern_trackNro))
            if track_found:
                placement_obj = track_obj.placements.add_notes()
                placement_obj.position = as_pattern_startTick
                placement_obj.duration = as_pattern_endTick-as_pattern_startTick
                placement_obj.cut_loop_data(0, 0, as_pattern_patternLength)
                placement_obj.visual.color = colordata.getcolornum(as_pattern_patternColor)

                if as_pattern_patternId in as_patt_notes:
                    t_notelist = as_patt_notes[as_pattern_patternId]
                    for t_note in t_notelist: 
                        n_position = max(0,t_note[0]-as_pattern_startTick)
                        n_duration = t_note[2]
                        n_key = t_note[3]-60
                        n_volume = t_note[4]/100
                        n_extra = {'cutoff': t_note[5]}
                        placement_obj.notelist.add_r(n_position, n_duration, n_key, n_volume, n_extra)

        # ------------------------------------------ patterns ------------------------------------------
        devicenum = 0
        for x_device in xt_devices:
            v_device_deviceType = int(x_device.get('deviceType'))
            v_device_visible = x_device.get('visible')
            v_device_xpos = int(x_device.get('xpos'))
            v_device_ypos = int(x_device.get('ypos'))

            cvpj_trackid = 'audiosanua'+str(devicenum)
            track_found, track_obj = convproj_obj.find_track(cvpj_trackid)

            windata_obj = convproj_obj.window_data_add(['plugin',cvpj_trackid])
            windata_obj.pos_x = v_device_xpos
            windata_obj.pos_y = v_device_ypos
            windata_obj.open = int(getbool(v_device_visible))

            if v_device_deviceType == 1 or v_device_deviceType == 0:
                plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-audiosauna', audiosanua_device_id[v_device_deviceType])
                plugin_obj.role = 'synth'
                x_device_sound = x_device.findall('sound')[0]

                paramlist = dataset.params_list('plugin', str(v_device_deviceType))
                if paramlist:
                    for paramid in paramlist:
                        plugin_obj.add_from_dset(paramid, getvalue(x_device_sound, paramid, 0), dataset, 'plugin', str(v_device_deviceType))

                v_attack, v_decay, v_release, v_sustain = setasdr(
                    float(getvalue(x_device_sound, 'attack', 0)), 
                    float(getvalue(x_device_sound, 'decay', 0)), 
                    float(getvalue(x_device_sound, 'release', 0)), 
                    float(getvalue(x_device_sound, 'sustain', 0))
                    )

                plugin_obj.env_asdr_add('vol', 0, v_attack, 0, v_decay, v_sustain, v_release, 1)

                if v_device_deviceType == 1: oprange = 2
                if v_device_deviceType == 0: oprange = 4

                for opnum in range(oprange):
                    opnumtxt = str(opnum+1)

                    op_attack, op_decay, op_release, op_sustain = setasdr(
                        float(getvalue(x_device_sound, 'aOp'+opnumtxt, 0)), 
                        float(getvalue(x_device_sound, 'dOp'+opnumtxt, 0)), 
                        -1, 
                        float(getvalue(x_device_sound, 'sOp'+opnumtxt, 0))/100 )
                    plugin_obj.env_asdr_add('op'+opnumtxt, 0, op_attack, 0, op_decay, op_sustain, op_release, 1)

                    osc_data = plugin_obj.osc_add()
                    osc_data.env['vol'] = 'op'+opnumtxt

                    if v_device_deviceType == 0: 
                        as_oct = int(getvalue(x_device_sound, 'oct'+opnumtxt, 0))*12
                        as_fine = float(getvalue(x_device_sound, 'fine'+opnumtxt, 0))
                        as_semi = int(getvalue(x_device_sound, 'semi'+opnumtxt, 0))
                        as_shape = int(getvalue(x_device_sound, 'wave'+opnumtxt, 0))
                        as_vol = int(getvalue(x_device_sound, 'osc'+opnumtxt+'Vol', 1))

                        osc_data.params['course'] = as_oct+as_fine
                        osc_data.params['fine'] = as_semi/100
                        osc_data.params['vol'] = as_vol

                        if as_shape == 0: osc_data.shape = 'saw'
                        if as_shape == 1: osc_data.shape = 'square'
                        if as_shape == 2: osc_data.shape = 'triangle'
                        if as_shape == 3: osc_data.shape = 'noise'
                        if as_shape == 4: osc_data.shape = 'sine'

            if v_device_deviceType == 2:
                x_device_sound = x_device.findall('sampler')[0]

                plugin_obj, pluginid = convproj_obj.add_plugin_genid('sampler', 'multi')
                plugin_obj.role = 'synth'
                plugin_obj.datavals.add('point_value_type', "percent")

                x_device_samples = x_device_sound.findall('samples')[0]
                for x_cell in x_device_samples.findall('cell'):
                    t_loKey = float(getvalue(x_cell, 'loKey', 60))
                    t_hiKey = float(getvalue(x_cell, 'hiKey', 60))
                    t_rootKey = float(getvalue(x_cell, 'rootKey', 60))
                    t_loopMode = getvalue(x_cell, 'loopMode', 'off')
                    t_loopStart = float(getvalue(x_cell, 'loopStart', 0))
                    t_loopEnd = float(getvalue(x_cell, 'loopEnd', 100))
                    t_playMode = getvalue(x_cell, 'playMode', 'forward')
                    t_smpStart = float(getvalue(x_cell, 'smpStart', 0))
                    t_smpEnd = float(getvalue(x_cell, 'smpEnd', 100))

                    cvpj_region = {}
                    cvpj_region['point_value_type'] = 'percent'
                    filepath = getvalue(x_cell, 'name', '')
                    cvpj_region['sampleref'] = filepath
                    sampleref_obj = convproj_obj.add_sampleref(filepath, filepath)
                    cvpj_region['file'] = getvalue(x_cell, 'url', '')
                    if t_playMode == 'forward': cvpj_region['reverse'] = 0
                    else: cvpj_region['reverse'] = 1
                    cvpj_region['tone'] = float(getvalue(x_cell, 'semitone', 0))
                    cvpj_region['fine'] = float(getvalue(x_cell, 'finetone', 0))
                    cvpj_region['volume'] = float(getvalue(x_cell, 'volume', 100))/100
                    cvpj_region['pan'] = float(getvalue(x_cell, 'pan', 100))/100
                    cvpj_region['loop'] = {}
                    if t_loopMode == 'off':
                        cvpj_region['loop']['enabled'] = 0
                    if t_loopMode == 'normal':
                        cvpj_region['loop']['enabled'] = 1
                        cvpj_region['loop']['mode'] = 'normal'
                    if t_loopMode == 'ping-pong':
                        cvpj_region['loop']['enabled'] = 1
                        cvpj_region['loop']['mode'] = 'pingpong'
                    cvpj_region['loop']['points'] = [float(t_loopStart)/100, float(t_loopEnd)/100]
                    cvpj_region['middlenote'] = t_rootKey-60
                    cvpj_region['start'] = float(t_smpStart)/100
                    cvpj_region['end'] = float(t_smpEnd)/100
                    cvpj_region['trigger'] = 'normal'
                    plugin_obj.regions.add(int(t_loKey)-60, int(t_hiKey)-60, cvpj_region)

                v_attack, v_decay, v_release, v_sustain = setasdr(
                    float(getvalue(x_device_sound, 'masterAttack', 0)), 
                    float(getvalue(x_device_sound, 'masterDecay', 0)), 
                    float(getvalue(x_device_sound, 'masterRelease', 0)), 
                    float(getvalue(x_device_sound, 'masterSustain', 0))
                    )

                plugin_obj.env_asdr_add('vol', 0, v_attack, 0, v_decay, v_sustain, v_release, 1)

            for fx_name in ['distortion', 'bitcrush', 'chorus', 'amp']:
                track_obj.fxslots_audio.append(make_fxslot(convproj_obj, x_device_sound, fx_name, v_device_deviceType))

            #cvpj_instdata['middlenote'] = int(getvalue(x_device_sound, 'masterTranspose', 0))*-1

            audiosauna_filtertype = getvalue(x_device_sound, 'filterType', '0')
            if audiosauna_filtertype == '0': filter_type = ['low_pass', None]
            if audiosauna_filtertype == '1': filter_type = ['high_pass', None]
            if audiosauna_filtertype == '2': filter_type = ["low_pass", "double"]

            pre_t_cutoff = int(getvalue(x_device_sound, 'cutoff', 0))/100
            filter_cutoff = int(pre_t_cutoff)*7200
            plugin_obj.filter.on = True
            plugin_obj.filter.freq = int(pre_t_cutoff)*7200
            plugin_obj.filter.q = int(getvalue(x_device_sound, 'resonance', 0))/100
            plugin_obj.filter.type, plugin_obj.filter.subtype = filter_type

            f_attack, f_decay, f_release, f_sustain = setasdr(
                float(getvalue(x_device_sound, 'filterAttack', 0)), 
                float(getvalue(x_device_sound, 'filterDecay', 0)), 
                float(getvalue(x_device_sound, 'filterRelease', 0)), 
                float(getvalue(x_device_sound, 'filterSustain', 0)))

            plugin_obj.env_asdr_add('cutoff', 0, f_attack, 0, f_decay, f_release, f_sustain, 1)

            audiosauna_lfoActive = getvalue(x_device_sound, 'lfoActive', 'false')
            audiosauna_lfoToggled = getbool(getvalue(x_device_sound, 'lfoToggled', 'false'))
            audiosauna_lfoTime = float(getvalue(x_device_sound, 'lfoTime', 1))
            audiosauna_lfoFilter = float(getvalue(x_device_sound, 'lfoFilter', 0))
            audiosauna_lfoPitch = float(getvalue(x_device_sound, 'lfoPitch', 0))
            audiosauna_lfoDelay = float(getvalue(x_device_sound, 'lfoDelay', 0))
            audiosauna_lfoWaveForm = int(getvalue(x_device_sound, 'lfoWaveForm', '0'))

            p_lfo_amount = ((audiosauna_lfoPitch/100)*12)*audiosauna_lfoToggled
            c_lfo_amount = ((audiosauna_lfoFilter/100)*-7200)*audiosauna_lfoToggled
            g_lfo_attack = audiosauna_lfoDelay
            g_lfo_shape = ['triangle', 'square', 'random'][audiosauna_lfoWaveForm]
            g_lfo_speed = audiosauna_lfoTime

            lfo_obj = plugin_obj.lfo_add('pitch')
            lfo_obj.attack = g_lfo_attack
            lfo_obj.shape = g_lfo_shape
            lfo_obj.time.set_seconds(g_lfo_speed)
            lfo_obj.amount = p_lfo_amount

            lfo_obj = plugin_obj.lfo_add('cutoff')
            lfo_obj.attack = g_lfo_attack
            lfo_obj.shape = g_lfo_shape
            lfo_obj.time.set_seconds(g_lfo_speed)
            lfo_obj.amount = c_lfo_amount

            if track_found: 
                track_obj.inst_pluginid = pluginid

            devicenum += 1

        as_loopstart = float(getvalue(x_proj, 'appLoopStart', 0))
        as_loopend = float(getvalue(x_proj, 'appLoopEnd', 0))
        if as_loopstart != 0 and as_loopend != 0: 
            convproj_obj.loop_active = True
            convproj_obj.loop_start = as_loopstart
            convproj_obj.loop_end = as_loopend