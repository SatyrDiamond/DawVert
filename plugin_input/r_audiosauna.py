# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import tracks
from functions import note_data
from functions import song
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

audiosanua_device_effects_audio = {}
audiosanua_device_effects_audio['amp'] = ['masterAmp']
audiosanua_device_effects_audio['chorus'] = ['chorusLevel', 'chorusMix', 'chorusSpeed']
audiosanua_device_effects_audio['distortion'] = ['overdrive', 'driveModul', 'modulate']
audiosanua_device_effects_audio['bitrate'] = ['bitrate']

class input_audiosanua(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'audiosauna'
    def getname(self): return 'AudioSauna'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': True,
        'placement_warp': False,
        'no_placements': False
        }
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

        output_cvpj_inst = {} # [vol,pan,name,mute,solo,instdata,trackplacements,chain_fx_audio]

        # ------------------------------------------ tracks ------------------------------------------
        for x_track in xt_track:
            x_track_trackIndex = int(x_track.get('trackIndex'))
            xt_track_seqNote = x_track.findall('seqNote')
            if x_track_trackIndex not in output_cvpj_inst: output_cvpj_inst[x_track_trackIndex] = [None,None,None,1,0,{},[],[]]
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
            cvpj_tr_vol = int(x_chan.get('volume'))/100
            cvpj_tr_pan = int(x_chan.get('pan'))/100
            cvpj_tr_name = x_chan.get('name')
            cvpj_tr_mute = getbool(x_chan.get('mute'))
            cvpj_tr_solo = getbool(x_chan.get('solo'))
            as_channum = int(x_chan.get('channelNro'))
            if as_channum not in output_cvpj_inst: output_cvpj_inst[as_channum] = [None,None,None,1,0,{},[],[]]
            output_cvpj_inst[as_channum][0] = int(x_chan.get('volume'))/100
            output_cvpj_inst[as_channum][1] = int(x_chan.get('pan'))/100
            output_cvpj_inst[as_channum][2] = x_chan.get('name')
            output_cvpj_inst[as_channum][3] = int(not getbool(x_chan.get('mute')))
            output_cvpj_inst[as_channum][4] = getbool(x_chan.get('solo'))
            
        # ------------------------------------------ patterns ------------------------------------------
        for x_pattern in xt_pattern:
            as_pattern_trackNro = int(x_pattern.get('trackNro'))
            as_pattern_patternId = int(x_pattern.get('patternId'))
            as_pattern_patternColor = int(x_pattern.get('patternColor'))
            as_pattern_startTick = int(x_pattern.get('startTick'))
            as_pattern_endTick = int(x_pattern.get('endTick'))
            as_pattern_patternLength = int(x_pattern.get('patternLength'))

            cvpj_pldata = {}
            cvpj_pldata["position"] = as_pattern_startTick/32
            cvpj_pldata["duration"] = (as_pattern_endTick-as_pattern_startTick)/32
            cvpj_pldata['cut'] = {'type': 'cut', 'start': 0, 'end': as_pattern_patternLength/32}
            cvpj_pldata['color'] = as_pattern_color[as_pattern_patternColor]
            cvpj_pldata['notelist'] = []

            if as_pattern_patternId in as_patt_notes:
                t_notelist = as_patt_notes[as_pattern_patternId]
                for t_note in t_notelist:
                    # as_note_startTick, as_note_endTick, as_note_noteLength, as_note_pitch, as_note_noteVolume, as_note_noteCutoff]
                    cvpj_note = note_data.rx_makenote((max(0,t_note[0]-as_pattern_startTick)/32), t_note[2]/32, t_note[3]-60, t_note[4]/100, None)
                    cvpj_note['cutoff'] = t_note[5]
                    cvpj_pldata['notelist'].append(cvpj_note)

            output_cvpj_inst[as_pattern_trackNro][6].append(cvpj_pldata)
        # ------------------------------------------ patterns ------------------------------------------
        devicenum = 0
        for x_device in xt_devices:
            v_device_deviceType = int(x_device.get('deviceType'))
            output_cvpj_inst_instdata = output_cvpj_inst[devicenum][5]

            output_cvpj_inst_instdata['plugindata'] = {}
            cvpj_plugindata = output_cvpj_inst_instdata['plugindata']
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
                output_cvpj_inst_instdata['plugin'] = 'native-audiosauna'
                cvpj_plugindata['type'] = v_device_deviceType
                cvpj_plugindata['data'] = {}
                for v_device_param in audiosanua_device_params[v_device_deviceType]:
                    cvpj_plugindata['data'][v_device_param] = getvalue(x_device_sound, v_device_param, 0)

            if v_device_deviceType == 2:
                x_device_sound = x_device.findall('sampler')[0]
                output_cvpj_inst_instdata['plugin'] = 'sampler-multi'
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
            cvpj_plugindata['filter']['cutoff'] = (int(getvalue(x_device_sound, 'cutoff', 0))/100)*7200
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
            devicenum += 1

        as_loopstart = float(getvalue(x_proj, 'appLoopStart', 0))
        as_loopend = float(getvalue(x_proj, 'appLoopEnd', 0))
        if as_loopstart != 0 and as_loopend != 0: song.add_timemarker_looparea(cvpj_l, None, as_loopstart, as_loopend)

        for testval in output_cvpj_inst:
            cvpj_trd = output_cvpj_inst[testval]
            trackid = 'audiosanua'+str(testval)

            #[vol,pan,name,mute,solo,instdata,trackplacements,chain_fx_audio]
            tracks.r_addtrack_inst(cvpj_l, trackid, cvpj_trd[5])
            tracks.r_addtrack_data(cvpj_l, trackid, cvpj_trd[2], None, cvpj_trd[0], cvpj_trd[1])
            tracks.r_addtrack_param(cvpj_l, trackid, 'enabled', cvpj_trd[3])
            tracks.r_addtrack_param(cvpj_l, trackid, 'solo', cvpj_trd[4])
            tracks.r_addtrackpl(cvpj_l, trackid, cvpj_trd[6])

        cvpj_l['bpm'] = float(getvalue(x_proj, 'appTempo', 170))
        return json.dumps(cvpj_l)


