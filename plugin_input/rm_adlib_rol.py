# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_cvpj import params_fm
from objects import dv_dataset
from functions import data_bytes
from functions import data_values

import plugin_input
import json
import struct

# --------------------------------------- Bank File ----------------------------------------

def load_bank(filename):
    bio_bankfile = open(filename, 'rb')

    verMajor = bio_bankfile.read(1)
    verMinor = bio_bankfile.read(1)
    signature = bio_bankfile.read(6)
    numUsed = int.from_bytes(bio_bankfile.read(2), 'little')
    numInstruments = int.from_bytes(bio_bankfile.read(2), 'little')
    offsetName = int.from_bytes(bio_bankfile.read(4), 'little')
    offsetData = int.from_bytes(bio_bankfile.read(4), 'little')
    
    adlib_bnk_names = {}
    bio_bankfile.seek(offsetName)
    for _ in range(numInstruments):
        index = int.from_bytes(bio_bankfile.read(2), 'little')
        flags = bio_bankfile.read(1)[0]
        instname = data_bytes.readstring_fixedlen(bio_bankfile, 9, None)
        adlib_bnk_names[instname] = [index, flags]
    
    adlib_bnk_data = []
    bio_bankfile.seek(offsetData)
    for _ in range(numUsed):
        PercData = struct.unpack('BB', bio_bankfile.read(2))
        oplModulator = struct.unpack('BBBBBBBBBBBBB', bio_bankfile.read(13))
        oplCarrier = struct.unpack('BBBBBBBBBBBBB', bio_bankfile.read(13))
        WaveSel = struct.unpack('BB', bio_bankfile.read(2))
        adlib_bnk_data.append([PercData, oplModulator, oplCarrier, WaveSel])
    
    return adlib_bnk_names, adlib_bnk_data

# --------------------------------------- Track Data ----------------------------------------

def parsetrack_tempo(file_stream):
    track_name = data_bytes.readstring_fixedlen(file_stream, 15, 'ascii')
    track_tempo = struct.unpack("f", file_stream.read(4))[0]
    track_num_events = int.from_bytes(file_stream.read(2), 'little')
    tempo_data = []
    for _ in range(track_num_events): 
        tempo_data_part = []
        tempo_data_part.append(int.from_bytes(file_stream.read(2), 'little'))
        tempo_data_part.append((struct.unpack("<f", file_stream.read(4))[0])*track_tempo)
        tempo_data.append(tempo_data_part)
    return track_name, track_tempo, tempo_data

def parsetrack_voice(file_stream):
    track_name = data_bytes.readstring_fixedlen(file_stream, 15, 'ascii')
    track_nTicks = int.from_bytes(file_stream.read(2), 'little')
    rol_notelist = []
    curtickpos = 0
    while curtickpos < track_nTicks: 
        rol_note_data = struct.unpack("HH", file_stream.read(4))
        curtickpos += rol_note_data[1]
        rol_notelist.append(rol_note_data)
    return track_name, rol_notelist, track_name

def parsetrack_timbre(file_stream):
    track_name = data_bytes.readstring_fixedlen(file_stream, 15, 'ascii')
    track_num_events = int.from_bytes(file_stream.read(2), 'little')
    rol_timbre_events = {}
    for _ in range(track_num_events): 
        timbre_pos = int.from_bytes(file_stream.read(2), 'little')
        timbre_name = file_stream.read(9).split(b'\x00')[0].decode('ascii')
        rol_timbre_events[timbre_pos] = timbre_name
        file_stream.read(3)
    return track_name, rol_timbre_events

def parsetrack_float(file_stream, i_mul, i_add):
    track_name = data_bytes.readstring_fixedlen(file_stream, 15, 'ascii')
    track_num_events = int.from_bytes(file_stream.read(2), 'little')
    track_rol_events = []
    for _ in range(track_num_events): 
        track_rol_part = []
        track_rol_part.append(int.from_bytes(file_stream.read(2), 'little'))
        track_rol_part.append(((struct.unpack("<f", file_stream.read(4))[0])*i_mul)+i_add)
        track_rol_events.append(track_rol_part)
    return track_name, track_rol_events

def parsetrack(convproj_obj, file_stream, tracknum):
    rol_tr_voice = parsetrack_voice(file_stream)
    rol_tr_timbre = parsetrack_timbre(file_stream)
    rol_tr_volume = parsetrack_float(file_stream, 1, 0)
    rol_tr_pitch = parsetrack_float(file_stream, 1, -1)

    cvpj_trackid = 'track'+str(tracknum+1)

    timbrepoints = []
    for timbrepos in rol_tr_timbre[1]:
        timbrepoints.append(timbrepos)

    print('[input-adlib_rol] Track: "'+rol_tr_voice[0]+'"')
    track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 0, False)
    track_obj.visual.name = rol_tr_voice[0]

    curtrackpos = 0
    for rol_notedata in rol_tr_voice[1]:
        if rol_notedata[0] >= 12:
            cvpj_noteinst = rol_tr_timbre[1][data_values.closest(timbrepoints, curtrackpos)]
            track_obj.placements.notelist.add_m(cvpj_noteinst.upper(), curtrackpos, rol_notedata[1], rol_notedata[0]-48-12, 1, {})
        curtrackpos += rol_notedata[1]

    for a in rol_tr_volume[1]: convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'vol'], 'float', a[0], a[1])
    for a in rol_tr_pitch[1]: convproj_obj.automation.add_autotick(['track', cvpj_trackid, 'pitch'], 'float', a[0], a[1])
    
# --------------------------------------- Plugin ----------------------------------------

class input_adlib_rol(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'adlib_rol'
    def gettype(self): return 'rm'
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'AdLib Visual Composer'
        dawinfo_obj.file_ext = 'rol'
        dawinfo_obj.auto_types = ['nopl_ticks']
        dawinfo_obj.track_nopl = True
        dawinfo_obj.plugin_included = ['fm:opl2']
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(4)
        bytesdata = bytestream.read(40)
        if bytesdata == b'\\roll\\default\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00': return True
        else: return False
    def parse(self, convproj_obj, input_file, dv_config):
        convproj_obj.type = 'rm'

        song_file = open(input_file, 'rb')
        dataset = dv_dataset.dataset('./data_dset/adlib_rol.dset')
        dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

        adlib_bnk = None
        if dv_config.path_extrafile:
            adlib_bnk = load_bank(dv_config.path_extrafile)
            numinst = len(adlib_bnk[0])
            for instname in adlib_bnk[0]:
                instname_upper = instname.upper()
                adlibrol_instname, _ = dataset.object_get_name_color('inst', instname_upper)

                inst_obj = convproj_obj.add_instrument(instname_upper)
                inst_obj.pluginid = instname_upper
                inst_obj.visual.name = adlibrol_instname

                instdatanum = adlib_bnk[0][instname][0]
                if instdatanum <= numinst:
                    opl2data = adlib_bnk[1][adlib_bnk[0][instname][0]]

                    fmdata = params_fm.fm_data('opl2')

                    inst_obj.datavals.add('middlenote', 0)
                    if opl2data[0][0] == 1: fmdata.set_param('perctype', opl2data[0][1]-6)
                    else:
                        fmdata.set_op_param(0, 'sustained', 1)
                        fmdata.set_op_param(1, 'sustained', 1)

                    fmdata.set_op_param(0, 'ksl', opl2data[1][0])
                    fmdata.set_op_param(0, 'freqmul', opl2data[1][1])
                    fmdata.set_param('feedback', opl2data[1][2])
                    fmdata.set_op_param(0, 'env_attack', opl2data[1][3])
                    fmdata.set_op_param(0, 'env_sustain', opl2data[1][4])
                    fmdata.set_op_param(0, 'perc_env', int(not bool(opl2data[1][5])))
                    fmdata.set_op_param(0, 'env_decay', opl2data[1][6])
                    fmdata.set_op_param(0, 'env_release', opl2data[1][7])
                    fmdata.set_op_param(0, 'level', opl2data[1][8])
                    fmdata.set_op_param(0, 'tremolo', opl2data[1][9])
                    fmdata.set_op_param(0, 'vibrato', opl2data[1][10])
                    fmdata.set_op_param(0, 'ksr', opl2data[1][11])
                    fmdata.set_param('fm', opl2data[1][12])
                    fmdata.set_op_param(0, 'waveform', opl2data[3][0])

                    fmdata.set_op_param(1, 'ksl', opl2data[2][0])
                    fmdata.set_op_param(1, 'freqmul', opl2data[2][1])
                    fmdata.set_op_param(1, 'env_attack', opl2data[2][3])
                    fmdata.set_op_param(1, 'env_sustain', opl2data[2][4])
                    fmdata.set_op_param(1, 'perc_env', int(not bool(opl2data[2][5])))
                    fmdata.set_op_param(1, 'env_decay', opl2data[2][6])
                    fmdata.set_op_param(1, 'env_release', opl2data[2][7])
                    fmdata.set_op_param(1, 'level', opl2data[2][8])
                    fmdata.set_op_param(1, 'tremolo', opl2data[2][9])
                    fmdata.set_op_param(1, 'vibrato', opl2data[2][10])
                    fmdata.set_op_param(1, 'ksr', opl2data[2][11])
                    fmdata.set_op_param(1, 'waveform', opl2data[3][1])

                    fmdata.to_cvpj(convproj_obj, instname_upper)
                    
        else:
            miditolist = dataset.midito_list('inst')
            if miditolist:
                for instid in miditolist:
                    convproj_obj.add_instrument_from_dset(instid, instid, dataset, dataset_midi, instid, None, None)

        rol_header_majorVersion = int.from_bytes(song_file.read(2), 'little')
        print("[input-adlib_rol] majorVersion: " + str(rol_header_majorVersion))
        
        rol_header_minorVersion = int.from_bytes(song_file.read(2), 'little')
        print("[input-adlib_rol] minorVersion: " + str(rol_header_majorVersion))
        
        rol_header_signature = song_file.read(40)

        rol_header_tickBeat = int.from_bytes(song_file.read(2), 'little')
        print("[input-adlib_rol] tickBeat: " + str(rol_header_tickBeat))
        convproj_obj.set_timings(rol_header_tickBeat, False)

        rol_header_beatMeasure = int.from_bytes(song_file.read(2), 'little')
        print("[input-adlib_rol] beatMeasure: " + str(rol_header_beatMeasure))
        
        rol_header_scaleY = int.from_bytes(song_file.read(2), 'little')
        rol_header_scaleX = int.from_bytes(song_file.read(2), 'little')
        print("[input-adlib_rol] Editing Scale: " + str(rol_header_scaleX) + 'x' + str(rol_header_scaleY))
        
        song_file.read(1) #reserved
        rol_header_isMelodic = song_file.read(1)[0]
        print("[input-adlib_rol] OPL rhythm mode: " + str(rol_header_isMelodic))
        
        rol_header_cTicks = struct.unpack("HHHHHHHHHHH", song_file.read(22))
        rol_header_cTimbreEvents = struct.unpack("HHHHHHHHHHH", song_file.read(22))
        rol_header_cVolumeEvents = struct.unpack("HHHHHHHHHHH", song_file.read(22))
        rol_header_cPitchEvents = struct.unpack("HHHHHHHHHHH", song_file.read(22))
        rol_header_cTempoEvents = int.from_bytes(song_file.read(2), 'little')
        
        print("[input-adlib_rol] cTicks: " + str(rol_header_cTicks))
        print("[input-adlib_rol] cTimbreEvents: " + str(rol_header_cTimbreEvents))
        print("[input-adlib_rol] cVolumeEvents: " + str(rol_header_cVolumeEvents))
        print("[input-adlib_rol] cPitchEvents: " + str(rol_header_cPitchEvents))
        print("[input-adlib_rol] cTempoEvents: " + str(rol_header_cTempoEvents))
        song_file.read(38) #Padding
        t_tempo_data = parsetrack_tempo(song_file)

        for a in t_tempo_data[2]: convproj_obj.automation.add_autotick(['track', 'bpm'], 'float', a[0], a[1])
        for tracknum in range(10): parsetrack(convproj_obj, song_file, tracknum)
        
        convproj_obj.do_actions.append('do_addloop')
        convproj_obj.do_actions.append('do_singlenotelistcut')
        convproj_obj.timesig = [rol_header_beatMeasure, 4]
        convproj_obj.params.add('bpm', t_tempo_data[1], 'float')
