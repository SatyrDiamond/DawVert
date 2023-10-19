# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import song
from functions import plugins
from functions import placement_data
import xml.etree.ElementTree as ET
import plugin_input
import json
import zipfile
from functions_tracks import tracks_r
from functions_tracks import tracks_master
from functions_tracks import trackfx
from functions_tracks import fxslot

as_pattern_color = {
    0: [0.07, 0.64, 0.86],
    1: [0.07, 0.84, 0.90],
    2: [0.05, 0.71, 0.56],
    3: [0.05, 0.69, 0.30],
    4: [0.64, 0.94, 0.22],
    5: [0.95, 0.79, 0.38],
    6: [0.95, 0.49, 0.32],
    7: [0.94, 0.25, 0.38],
    8: [0.93, 0.20, 0.70],
    9: [0.69, 0.06, 0.79],
}

def getvalue(xmltag, xmlname, fallbackval): 
    if xmltag.findall(xmlname) != []: return xmltag.findall(xmlname)[0].text.strip()
    else: return fallbackval

def getbool(input_val):
    if input_val == 'true': return 1
    if input_val == 'false': return 0

def setasdr(i_attack, i_decay, i_release, i_sustain):
    out_attack = i_attack
    out_decay = i_decay
    out_release = i_release
    out_sustain = i_sustain
    if out_decay == 0: i_sustain = 1
    return out_attack, out_decay, out_release, out_sustain

audiosanua_device_params = {}
audiosanua_device_params[1] = ['aOp1', 'aOp2', 'attack', 'decay', 'dOp1', 'dOp2', 'fine1', 'fine2', 'fm', 'oct1', 'oct2', 'osc1Vol', 'osc2Vol', 'portamento', 'release', 'semi1', 'semi2', 'sOp1', 'sOp2', 'sustain', 'wave1', 'wave2', 'waveform']
audiosanua_device_params[0] = ['aOp1', 'aOp2', 'aOp3', 'aOp4', 'attack', 'decay', 'dOp1', 'dOp2', 'dOp3', 'dOp4','fine1', 'fine2', 'fine3', 'fine4', 'fmAlgorithm', 'fmFeedBack', 'frq1', 'frq2', 'frq3', 'frq4', 'opAmp1', 'opAmp2', 'opAmp3', 'opAmp4', 'portamento', 'release', 'sOp1', 'sOp2', 'sOp3', 'sOp4', 'sustain', 'waveform']
audiosanua_device_id = ['analog', 'fm']

def make_fxslot(x_device_sound, fx_type, as_device):
    pluginid = plugins.get_id()

    fx_wet = 1
    if fx_type == 'chorus':
        plugins.add_plug(cvpj_l, pluginid, 'native-audiosauna', 'chorus')
        plugins.add_plug_param(cvpj_l, pluginid, "speed", float(getvalue(x_device_sound, 'chorusSpeed', 0))/100, 'float', "Speed")

        if as_device in [0,1]: 
            fx_wet = float(getvalue(x_device_sound, 'chorusMix', 0))/100
            plugins.add_plug_param(cvpj_l, pluginid, "size", float(getvalue(x_device_sound, 'chorusLevel', 0))/100, 'float', "Size")
        else: 
            fx_wet = float(getvalue(x_device_sound, 'chorusDryWet', 0))/100
            plugins.add_plug_param(cvpj_l, pluginid, "size", float(getvalue(x_device_sound, 'chorusSize', 0))/100, 'float', "Size")

        plugins.add_plug_fxdata(cvpj_l, pluginid, True, fx_wet)
        plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Chorus', None)

    if fx_type == 'distortion':
        plugins.add_plug(cvpj_l, pluginid, 'native-audiosauna', 'distortion')
        plugins.add_plug_param(cvpj_l, pluginid, "overdrive", float(getvalue(x_device_sound, 'overdrive', 0))/100, 'float', "Overdrive")
        if as_device in [0,1]: plugins.add_plug_param(cvpj_l, pluginid, "modulate", float(getvalue(x_device_sound, 'driveModul', 0))/100, 'float', "Modulate")
        else: plugins.add_plug_param(cvpj_l, pluginid, "modulate", float(getvalue(x_device_sound, 'modulate', 0))/100, 'float', "Modulate")
        plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Distortion', None)

    if fx_type == 'bitcrush':
        bitrateval = float(getvalue(x_device_sound, 'bitrate', 0))
        if bitrateval != 0.0: 
            plugins.add_plug(cvpj_l, pluginid, 'native-audiosauna', 'bitcrush')
            plugins.add_plug_param(cvpj_l, pluginid, "frames", bitrateval, 'float', "Frames")
        plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Bitcrush', None)

    if fx_type == 'tape_delay':
        plugins.add_plug(cvpj_l, pluginid, 'native-audiosauna', 'tape_delay')
        plugins.add_plug_param(cvpj_l, pluginid, "time", float(getvalue(x_device_sound, 'dlyTime', 0)), 'float', "Time")
        plugins.add_plug_param(cvpj_l, pluginid, "damage", float(getvalue(x_device_sound, 'dlyDamage', 0))/100, 'float', "Damage")
        plugins.add_plug_param(cvpj_l, pluginid, "feedback", float(getvalue(x_device_sound, 'dlyFeed', 0))/100, 'float', "Feedback")
        plugins.add_plug_param(cvpj_l, pluginid, "sync", getbool(getvalue(x_device_sound, 'dlySync', 0)), 'float', "Sync")
        plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Tape Delay', None)

    if fx_type == 'reverb':
        plugins.add_plug(cvpj_l, pluginid, 'native-audiosauna', 'reverb')
        plugins.add_plug_param(cvpj_l, pluginid, "time", float(getvalue(x_device_sound, 'rvbTime', 0)), 'float', "Time")
        plugins.add_plug_param(cvpj_l, pluginid, "feedback", float(getvalue(x_device_sound, 'rvbFeed', 0))/100, 'float', "Feedback")
        plugins.add_plug_param(cvpj_l, pluginid, "width", float(getvalue(x_device_sound, 'rvbWidth', 0))/100, 'float', "Width")
        plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Reverb', None)

    if fx_type == 'amp':
        ampval = float(getvalue(x_device_sound, 'masterAmp', 0))/100
        if ampval != 1.0: 
            plugins.add_plug(cvpj_l, pluginid, 'native-audiosauna', 'amp')
            plugins.add_plug_param(cvpj_l, pluginid, "level", ampval, 'float', "Level")
        plugins.add_plug_fxvisual(cvpj_l, pluginid, 'Amp', None)

    return pluginid

class input_audiosanua(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'audiosauna'
    def getname(self): return 'AudioSauna'
    def gettype(self): return 'r'
    def getdawcapabilities(self): return {'placement_cut': True}
    def supported_autodetect(self): return True
    def detect(self, input_file): 
        try:
            zip_data = zipfile.ZipFile(input_file, 'r')
            if 'songdata.xml' in zip_data.namelist(): return True
            else: return False
        except:
            return False
    def parse(self, input_file, extra_param):
        global cvpj_l
        zip_data = zipfile.ZipFile(input_file, 'r')

        cvpj_l = {}

        songdataxml_filename = None

        t_audiosanua_project = zip_data.read('songdata.xml')

        x_proj = ET.fromstring(t_audiosanua_project)

        x_proj_channels = x_proj.findall('channels')[0]
        x_proj_tracks = x_proj.findall('tracks')[0]
        x_proj_songPatterns = x_proj.findall('songPatterns')[0]
        x_proj_devices = x_proj.findall('devices')[0]

        xt_chan = x_proj_channels.findall('channel')
        xt_track = x_proj_tracks.findall('track')
        xt_pattern = x_proj_songPatterns.findall('pattern')
        xt_devices = x_proj_devices.findall('audioDevice')

        x_BPM = float(getvalue(x_proj, 'appTempo', 170))

        cvpj_plnotes = {}
        as_patt_notes = {}

        tracks_master.create(cvpj_l, int(getvalue(x_proj,'appMasterVolume',100))/100)
        tracks_master.visual(cvpj_l, name='Master')


        trackfx.return_add(cvpj_l, ['master'], 'audiosauna_send_tape_delay')
        trackfx.return_visual(cvpj_l, ['master'], 'audiosauna_send_tape_delay', name='Tape Delay')
        trackfx.return_param_add(cvpj_l, ['master'], 'audiosauna_send_tape_delay', 'vol', int(getvalue(x_proj,'dlyLevel',100))/100, 'float')
        fxslot.insert(cvpj_l, ['return', None, 'audiosauna_send_tape_delay'], 'audio', make_fxslot(x_proj, 'tape_delay', None))

        trackfx.return_add(cvpj_l, ['master'], 'audiosauna_send_reverb')
        trackfx.return_visual(cvpj_l, ['master'], 'audiosauna_send_reverb', name='Reverb')
        trackfx.return_param_add(cvpj_l, ['master'], 'audiosauna_send_reverb', 'vol', int(getvalue(x_proj,'rvbLevel',100))/100, 'float')
        fxslot.insert(cvpj_l, ['return', None, 'audiosauna_send_reverb'], 'audio', make_fxslot(x_proj, 'reverb', None))

        # ------------------------------------------ tracks ------------------------------------------
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

            cvpj_tr_color = as_pattern_color[as_channum]

            tracks_r.track_create(cvpj_l, cvpj_id, 'instrument')
            tracks_r.track_visual(cvpj_l, cvpj_id, name=cvpj_tr_name, color=cvpj_tr_color)

            tracks_r.track_param_add(cvpj_l, cvpj_id, 'vol', cvpj_tr_vol, 'float')
            tracks_r.track_param_add(cvpj_l, cvpj_id, 'pan', cvpj_tr_pan, 'float')
            tracks_r.track_param_add(cvpj_l, cvpj_id, 'enabled', int(not getbool(x_chan.get('mute'))), 'bool')
            tracks_r.track_param_add(cvpj_l, cvpj_id, 'solo', getbool(x_chan.get('solo')), 'bool')
            trackfx.send_add(cvpj_l, cvpj_id, 'audiosauna_send_tape_delay', int(x_chan.get('delay'))/100, None)
            trackfx.send_add(cvpj_l, cvpj_id, 'audiosauna_send_reverb', int(x_chan.get('reverb'))/100, None)

        # ------------------------------------------ patterns ------------------------------------------
        for x_pattern in xt_pattern:
            as_pattern_trackNro = int(x_pattern.get('trackNro'))
            as_pattern_patternId = int(x_pattern.get('patternId'))
            as_pattern_patternColor = int(x_pattern.get('patternColor'))
            as_pattern_startTick = int(x_pattern.get('startTick'))
            as_pattern_endTick = int(x_pattern.get('endTick'))
            as_pattern_patternLength = int(x_pattern.get('patternLength'))

            cvpj_pldata = placement_data.makepl_n(as_pattern_startTick/32, (as_pattern_endTick-as_pattern_startTick)/32, [])
            cvpj_pldata['cut'] = {'type': 'cut', 'start': 0, 'end': as_pattern_patternLength/32}
            cvpj_pldata['color'] = as_pattern_color[as_pattern_patternColor]

            if as_pattern_patternId in as_patt_notes:
                t_notelist = as_patt_notes[as_pattern_patternId]
                for t_note in t_notelist:
                    cvpj_note = note_data.rx_makenote((max(0,t_note[0]-as_pattern_startTick)/32), t_note[2]/32, t_note[3]-60, t_note[4]/100, None)
                    cvpj_note['cutoff'] = t_note[5]
                    cvpj_pldata['notelist'].append(cvpj_note)

            tracks_r.add_pl(cvpj_l, 'audiosanua'+str(as_pattern_trackNro), 'notes', cvpj_pldata)
        # ------------------------------------------ patterns ------------------------------------------
        devicenum = 0
        for x_device in xt_devices:
            v_device_deviceType = int(x_device.get('deviceType'))

            cvpj_trackid = 'audiosanua'+str(devicenum)

            #cvpj_instdata = {}

            pluginid = plugins.get_id()

            if v_device_deviceType == 1 or v_device_deviceType == 0:
                plugins.add_plug(cvpj_l, pluginid, 'native-audiosauna', audiosanua_device_id[v_device_deviceType])
                x_device_sound = x_device.findall('sound')[0]

                for v_device_param in audiosanua_device_params[v_device_deviceType]:
                    plugins.add_plug_param(cvpj_l, pluginid, v_device_param, float(getvalue(x_device_sound, v_device_param, 0)), 'float', v_device_param)

                v_attack, v_decay, v_release, v_sustain = setasdr(
                    float(getvalue(x_device_sound, 'attack', 0)), 
                    float(getvalue(x_device_sound, 'decay', 0)), 
                    float(getvalue(x_device_sound, 'release', 0)), 
                    float(getvalue(x_device_sound, 'sustain', 0))
                    )

                plugins.add_asdr_env(cvpj_l, pluginid, 'volume', 0, v_attack, 0, v_decay, v_sustain, v_release, 1)

                if v_device_deviceType == 1: oprange = 2
                if v_device_deviceType == 0: oprange = 4
                for opnum in range(oprange):
                    opnumtxt = str(opnum+1)

                    op_attack, op_decay, op_release, op_sustain = setasdr(
                        float(getvalue(x_device_sound, 'aOp'+opnumtxt, 0)), 
                        float(getvalue(x_device_sound, 'dOp'+opnumtxt, 0)), 
                        -1, 
                        float(getvalue(x_device_sound, 'sOp'+opnumtxt, 0))/100 )
                    plugins.add_asdr_env(cvpj_l, pluginid, 'op'+opnumtxt, 0, op_attack, 0, op_decay, op_sustain, op_release, 1)
                
            if v_device_deviceType == 2:
                plugins.add_plug_multisampler(cvpj_l, pluginid)
                plugins.add_plug_data(cvpj_l, pluginid, 'point_value_type', "percent")
                x_device_sound = x_device.findall('sampler')[0]

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
                    cvpj_region['name'] = getvalue(x_cell, 'name', '')
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
                    cvpj_region['r_key'] = [int(t_loKey)-60, int(t_hiKey)-60]
                    cvpj_region['start'] = float(t_smpStart)/100
                    cvpj_region['end'] = float(t_smpEnd)/100
                    cvpj_region['trigger'] = 'normal'
                    plugins.add_plug_multisampler_region(cvpj_l, pluginid, cvpj_region)

                v_attack, v_decay, v_release, v_sustain = setasdr(
                    float(getvalue(x_device_sound, 'masterAttack', 0)), 
                    float(getvalue(x_device_sound, 'masterDecay', 0)), 
                    float(getvalue(x_device_sound, 'masterRelease', 0)), 
                    float(getvalue(x_device_sound, 'masterSustain', 0))
                    )

                plugins.add_asdr_env(cvpj_l, pluginid, 'volume', 0, v_attack, 0, v_decay, v_sustain, v_release, 1)
                
            #cvpj_instdata['middlenote'] = int(getvalue(x_device_sound, 'masterTranspose', 0))*-1

            pre_t_cutoff = int(getvalue(x_device_sound, 'cutoff', 0))/100

            filter_cutoff = int(pre_t_cutoff)*7200
            filter_reso = int(getvalue(x_device_sound, 'resonance', 0))/100

            audiosauna_filtertype = getvalue(x_device_sound, 'filterType', '0')
            if audiosauna_filtertype == '0': filter_type = ['lowpass', None]
            if audiosauna_filtertype == '1': filter_type = ['highpass', None]
            if audiosauna_filtertype == '2': filter_type = ["lowpass", "double"]

            plugins.add_filter(cvpj_l, pluginid, True, filter_cutoff, filter_reso, filter_type[0], filter_type[1])

            f_attack, f_decay, f_release, f_sustain = setasdr(
                float(getvalue(x_device_sound, 'filterAttack', 0)), 
                float(getvalue(x_device_sound, 'filterDecay', 0)), 
                float(getvalue(x_device_sound, 'filterRelease', 0)), 
                float(getvalue(x_device_sound, 'filterSustain', 0)))

            audiosauna_lfoActive = getvalue(x_device_sound, 'lfoActive', 'false')
            audiosauna_lfoToggled = getvalue(x_device_sound, 'lfoToggled', 'false')
            audiosauna_lfoTime = float(getvalue(x_device_sound, 'lfoTime', 1))
            audiosauna_lfoFilter = float(getvalue(x_device_sound, 'lfoFilter', 0))
            audiosauna_lfoPitch = float(getvalue(x_device_sound, 'lfoPitch', 0))
            audiosauna_lfoDelay = float(getvalue(x_device_sound, 'lfoDelay', 0))
            audiosauna_lfoWaveForm = getvalue(x_device_sound, 'lfoWaveForm', '0')

            if audiosauna_lfoWaveForm == '0': audiosauna_lfoWaveForm = "tri"
            if audiosauna_lfoWaveForm == '1': audiosauna_lfoWaveForm = 'square'
            if audiosauna_lfoWaveForm == '2': audiosauna_lfoWaveForm = "random"
            if audiosauna_lfoToggled == 'true': audiosauna_lfoToggled = 1
            if audiosauna_lfoToggled == 'false': audiosauna_lfoToggled = 0
            p_lfo_amount = ((audiosauna_lfoPitch/100)*12)*audiosauna_lfoToggled
            c_lfo_amount = ((audiosauna_lfoFilter/100)*-7200)*audiosauna_lfoToggled
            g_lfo_attack = audiosauna_lfoDelay
            g_lfo_shape = audiosauna_lfoWaveForm
            g_lfo_speed = audiosauna_lfoTime

            plugins.add_lfo(cvpj_l, pluginid, 'pitch', 
                g_lfo_shape, 'seconds', g_lfo_speed, 0, g_lfo_attack, p_lfo_amount)
            plugins.add_lfo(cvpj_l, pluginid, 'cutoff', 
                g_lfo_shape, 'seconds', g_lfo_speed, 0, g_lfo_attack, c_lfo_amount)
            
            tracks_r.track_inst_pluginid(cvpj_l, cvpj_trackid, pluginid)

            for fx_name in ['distortion', 'bitcrush', 'chorus', 'amp']:
                fxslot.insert(cvpj_l, ['track', cvpj_trackid], 'audio', make_fxslot(x_proj, fx_name, v_device_deviceType))

            devicenum += 1

        as_loopstart = float(getvalue(x_proj, 'appLoopStart', 0))
        as_loopend = float(getvalue(x_proj, 'appLoopEnd', 0))
        if as_loopstart != 0 and as_loopend != 0: song.add_timemarker_looparea(cvpj_l, None, as_loopstart, as_loopend)

        song.add_param(cvpj_l, 'bpm', x_BPM)
        return json.dumps(cvpj_l)


