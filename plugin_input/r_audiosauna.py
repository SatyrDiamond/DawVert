# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import tracks
from functions import note_data
from functions import song
from functions import placement_data
import xml.etree.ElementTree as ET
import plugin_input
import json
import zipfile

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

audiosanua_device_params = {}
audiosanua_device_params[1] = ['aOp1', 'aOp2', 'attack', 'decay', 'dOp1', 'dOp2', 'fine1', 'fine2', 'fm', 'oct1', 'oct2', 'osc1Vol', 'osc2Vol', 'portamento', 'release', 'semi1', 'semi2', 'sOp1', 'sOp2', 'sustain', 'wave1', 'wave2', 'waveform']
audiosanua_device_params[0] = ['aOp1', 'aOp2', 'aOp3', 'aOp4', 'attack', 'decay', 'dOp1', 'dOp2', 'dOp3', 'dOp4','fine1', 'fine2', 'fine3', 'fine4', 'fmAlgorithm', 'fmFeedBack', 'frq1', 'frq2', 'frq3', 'frq4', 'opAmp1', 'opAmp2', 'opAmp3', 'opAmp4', 'portamento', 'release', 'sOp1', 'sOp2', 'sOp3', 'sOp4', 'sustain', 'waveform']

def make_fxslot(x_device_sound, fx_type, as_device):
    fx_plugindata = {}
    fx_wet = 1
    if fx_type == 'chorus':
        fx_plugindata['speed'] = int(getvalue(x_device_sound, 'chorusSpeed', 0))/100
        if as_device in [0,1]: 
            fx_wet = int(getvalue(x_device_sound, 'chorusMix', 0))/100
            fx_plugindata['level'] = int(getvalue(x_device_sound, 'chorusLevel', 0))/100
        else: 
            fx_wet = int(getvalue(x_device_sound, 'chorusDryWet', 0))/100
            fx_plugindata['level'] = int(getvalue(x_device_sound, 'chorusSize', 0))/100

    if fx_type == 'distortion':
        fx_plugindata['overdrive'] = int(getvalue(x_device_sound, 'overdrive', 0))/100
        if as_device in [0,1]: fx_plugindata['modulate'] = float(getvalue(x_device_sound, 'driveModul', 0))/100
        else: fx_plugindata['modulate'] = float(getvalue(x_device_sound, 'modulate', 0))/100

    if fx_type == 'bitcrush': fx_plugindata['frames'] = int(getvalue(x_device_sound, 'bitrate', 0))
    if fx_type == 'amp': fx_plugindata['level'] = int(getvalue(x_device_sound, 'masterAmp', 0))/100

    if fx_type == 'tape_delay':
        fx_plugindata['damage'] = float(getvalue(x_device_sound, 'dlyDamage', 0))/100
        fx_plugindata['feedback'] = int(getvalue(x_device_sound, 'dlyFeed', 0))/100
        fx_plugindata['sync'] = getbool(getvalue(x_device_sound, 'dlySync', 0))

    if fx_type == 'reverb':
        fx_plugindata['time'] = float(getvalue(x_device_sound, 'rvbTime', 0))/100
        fx_plugindata['feedback'] = int(getvalue(x_device_sound, 'rvbFeed', 0))/100
        fx_plugindata['width'] = int(getvalue(x_device_sound, 'rvbWidth', 0))/100

    return fx_plugindata, fx_wet

class input_audiosanua(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'audiosauna'
    def getname(self): return 'AudioSauna'
    def gettype(self): return 'r'
    def getdawcapabilities(self): return {'placement_cut': True}
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
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

        cvpj_plnotes = {}
        as_patt_notes = {}

        tracks.a_addtrack_master(cvpj_l, 'Master', int(getvalue(x_proj,'appMasterVolume',100))/100, None)

        tracks.r_add_return(cvpj_l, ['master'], 'audiosauna_send_tape_delay')
        tracks.r_add_return_basicdata(cvpj_l, ['master'], 'audiosauna_send_tape_delay', 'Tape Delay', None, int(getvalue(x_proj,'dlyLevel',100))/100, None)
        send_reverb_data = make_fxslot(x_proj, 'tape_delay', None)
        tracks.add_fxslot_native(cvpj_l, 'audio', 'audiosauna', ['send', None, 'audiosauna_send_tape_delay'], None, None, None, 'tape_delay', send_reverb_data[0])

        tracks.r_add_return(cvpj_l, ['master'], 'audiosauna_send_reverb')
        tracks.r_add_return_basicdata(cvpj_l, ['master'], 'audiosauna_send_reverb', 'Reverb', None, int(getvalue(x_proj,'rvbLevel',100))/100, None)
        send_reverb_data = make_fxslot(x_proj, 'reverb', None)
        tracks.add_fxslot_native(cvpj_l, 'audio', 'audiosauna', ['send', None, 'audiosauna_send_reverb'], None, None, None, 'reverb', send_reverb_data[0])

        # ------------------------------------------ tracks ------------------------------------------
        for x_track in xt_track:
            x_track_trackIndex = int(x_track.get('trackIndex'))
            xt_track_seqNote = x_track.findall('seqNote')
            tracks.r_create_inst(cvpj_l, 'audiosanua'+str(x_track_trackIndex), {})
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

            tracks.r_basicdata(cvpj_l, cvpj_id, cvpj_tr_name, cvpj_tr_color, cvpj_tr_vol, cvpj_tr_pan)
            tracks.r_param(cvpj_l, cvpj_id,'mute', int(not getbool(x_chan.get('mute'))))
            tracks.r_param(cvpj_l, cvpj_id,'mute', getbool(x_chan.get('solo')))
            tracks.r_add_send(cvpj_l, cvpj_id, 'audiosauna_send_tape_delay', int(x_chan.get('delay'))/100, None)
            tracks.r_add_send(cvpj_l, cvpj_id, 'audiosauna_send_reverb', int(x_chan.get('reverb'))/100, None)

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

            tracks.r_pl_notes(cvpj_l, 'audiosanua'+str(as_pattern_trackNro), cvpj_pldata)
        # ------------------------------------------ patterns ------------------------------------------
        devicenum = 0
        for x_device in xt_devices:
            v_device_deviceType = int(x_device.get('deviceType'))

            cvpj_trackid = 'audiosanua'+str(devicenum)

            cvpj_instdata = {}
            cvpj_instdata['plugindata'] = {}
            cvpj_plugindata = cvpj_instdata['plugindata']
            cvpj_plugindata['asdrlfo'] = {}
            cvpj_plugindata['asdrlfo']['volume'] = {'envelope': {}, 'lfo': {}}
            cvpj_plugindata['asdrlfo']['cutoff'] = {'envelope': {}, 'lfo': {}}
            cvpj_plugindata['asdrlfo']['pitch'] = {'envelope': {}, 'lfo': {}}
            vol_asdr = cvpj_plugindata['asdrlfo']['volume']['envelope']
            cutoff_asdr = cvpj_plugindata['asdrlfo']['cutoff']['envelope']
            cutoff_lfo = cvpj_plugindata['asdrlfo']['cutoff']['lfo']
            pitch_lfo = cvpj_plugindata['asdrlfo']['pitch']['lfo']

            if v_device_deviceType == 1 or v_device_deviceType == 0:
                x_device_sound = x_device.findall('sound')[0]
                cvpj_instdata['plugin'] = 'native-audiosauna'
                cvpj_plugindata['type'] = v_device_deviceType
                cvpj_plugindata['data'] = {}
                for v_device_param in audiosanua_device_params[v_device_deviceType]:
                    cvpj_plugindata['data'][v_device_param] = getvalue(x_device_sound, v_device_param, 0)

            if v_device_deviceType == 2:
                x_device_sound = x_device.findall('sampler')[0]
                cvpj_instdata['plugin'] = 'sampler-multi'
                cvpj_plugindata['point_value_type'] = 'percent'
                cvpj_plugindata['regions'] = []
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

                    cvpj_plugindata['regions'].append(cvpj_region)

                vol_asdr['amount'] = 1
                vol_asdr['attack'] = float(getvalue(x_device_sound, 'masterAttack', 0))
                vol_asdr['decay'] = float(getvalue(x_device_sound, 'masterDecay', 0))
                vol_asdr['hold'] = 0
                vol_asdr['predelay'] = 0
                vol_asdr['release'] = float(getvalue(x_device_sound, 'masterRelease', 0))
                vol_asdr['sustain'] = float(getvalue(x_device_sound, 'masterSustain', 0))
                if vol_asdr['decay'] == 0: vol_asdr['sustain'] = 1

            cvpj_plugindata['middlenote'] = int(getvalue(x_device_sound, 'masterTranspose', 0))*-1
            cvpj_plugindata['amp'] = int(getvalue(x_device_sound, 'masterAmp', 0))/100
            cvpj_plugindata['filter'] = {}
            t_cutoff = int(getvalue(x_device_sound, 'cutoff', 0))/100
            cvpj_plugindata['filter']['cutoff'] = int(t_cutoff)*7200
            cvpj_plugindata['filter']['reso'] = int(getvalue(x_device_sound, 'resonance', 0))/100
            audiosauna_filtertype = getvalue(x_device_sound, 'filterType', 0)
            if audiosauna_filtertype == '0': 
                cvpj_plugindata['filter']['type'] = "lowpass"
            if audiosauna_filtertype == '1': 
                cvpj_plugindata['filter']['type'] = 'highpass'
            if audiosauna_filtertype == '2': 
                cvpj_plugindata['filter']['type'] = "lowpass"
                cvpj_plugindata['filter']['subtype'] = "double"
            cvpj_plugindata['filter']['wet'] = 1
            cutoff_asdr['amount'] = 1
            cutoff_asdr['attack'] = float(getvalue(x_device_sound, 'filterAttack', 0))
            cutoff_asdr['decay'] = float(getvalue(x_device_sound, 'filterDecay', 0))
            cutoff_asdr['hold'] = 0
            cutoff_asdr['predelay'] = 0
            cutoff_asdr['release'] = float(getvalue(x_device_sound, 'filterRelease', 0))
            cutoff_asdr['sustain'] = float(getvalue(x_device_sound, 'filterSustain', 0))
            if cutoff_asdr['decay'] == 0: cutoff_asdr['sustain'] = 1
            audiosauna_lfoActive = getvalue(x_device_sound, 'lfoActive', 'false')
            audiosauna_lfoToggled = getvalue(x_device_sound, 'lfoToggled', 'false')
            audiosauna_lfoTime = float(getvalue(x_device_sound, 'lfoTime', 1))
            audiosauna_lfoFilter = float(getvalue(x_device_sound, 'lfoFilter', 0))
            audiosauna_lfoPitch = float(getvalue(x_device_sound, 'lfoPitch', 0))
            audiosauna_lfoDelay = float(getvalue(x_device_sound, 'lfoDelay', 0))
            audiosauna_lfoWaveForm = getvalue(x_device_sound, 'lfoWaveForm', 0)
            if audiosauna_lfoWaveForm == '0': audiosauna_lfoWaveForm = "tri"
            if audiosauna_lfoWaveForm == '1': audiosauna_lfoWaveForm = 'square'
            if audiosauna_lfoWaveForm == '2': audiosauna_lfoWaveForm = "random"
            if audiosauna_lfoToggled == 'true': audiosauna_lfoToggled = 1
            if audiosauna_lfoToggled == 'false': audiosauna_lfoToggled = 0
            pitch_lfo['amount'] = ((audiosauna_lfoPitch/100)*12)*audiosauna_lfoToggled
            pitch_lfo['attack'] = audiosauna_lfoDelay
            pitch_lfo['predelay'] = 0
            pitch_lfo['shape'] = audiosauna_lfoWaveForm
            pitch_lfo['speed'] = {"time": audiosauna_lfoTime, "type": "seconds"}
            cutoff_lfo['amount'] = ((audiosauna_lfoFilter/100)*-7200)*audiosauna_lfoToggled
            cutoff_lfo['attack'] = audiosauna_lfoDelay
            cutoff_lfo['predelay'] = 0
            cutoff_lfo['shape'] = audiosauna_lfoWaveForm
            cutoff_lfo['speed'] = {"time": audiosauna_lfoTime, "type": "seconds"}

            tracks.r_param(cvpj_l, cvpj_trackid, 'instdata', cvpj_instdata)

            for fx_name in ['distortion', 'bitcrush', 'chorus', 'amp']:
                fx_plugindata, fx_wet = make_fxslot(x_device_sound, fx_name, v_device_deviceType)
                tracks.add_fxslot_native(cvpj_l, 'audio', 'audiosauna', ['track', cvpj_trackid], None, fx_wet, None, fx_name, fx_plugindata)

            devicenum += 1

        as_loopstart = float(getvalue(x_proj, 'appLoopStart', 0))
        as_loopend = float(getvalue(x_proj, 'appLoopEnd', 0))
        if as_loopstart != 0 and as_loopend != 0: song.add_timemarker_looparea(cvpj_l, None, as_loopstart, as_loopend)

        cvpj_l['bpm'] = float(getvalue(x_proj, 'appTempo', 170))
        return json.dumps(cvpj_l)


