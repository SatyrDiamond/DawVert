# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import placement_data
from functions import data_dataset
from functions import auto
from functions import data_bytes
from functions import data_values
from functions import plugins
from functions import song
from functions_tracks import tracks_rm
from functions_tracks import auto_nopl
from functions_plugdata import plugin_fm

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

def parsetrack_tempo(file_stream, tickBeat):
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

def parsetrack(file_stream, tracknum, notelen):
    rol_tr_voice = parsetrack_voice(file_stream)
    rol_tr_timbre = parsetrack_timbre(file_stream)
    rol_tr_volume = parsetrack_float(file_stream, 1, 0)
    rol_tr_pitch = parsetrack_float(file_stream, 1, -1)

    cvpj_trackid = 'track'+str(tracknum+1)

    timbrepoints = []
    for timbrepos in rol_tr_timbre[1]:
        timbrepoints.append(timbrepos)

    cvpj_notelist = []
    curtrackpos = 0
    for rol_notedata in rol_tr_voice[1]:
        if rol_notedata[0] >= 12:
            cvpj_noteinst = rol_tr_timbre[1][data_values.closest(timbrepoints, curtrackpos)]
            cvpj_notelist.append(note_data.mx_makenote(cvpj_noteinst.upper(), curtrackpos*notelen, rol_notedata[1]*notelen, rol_notedata[0]-48, None, None))
        curtrackpos += rol_notedata[1]

    print('[input-adlib_rol] Track: "'+rol_tr_voice[0]+'"')

    if len(rol_tr_volume) > 1: auto_nopl.twopoints(['track', tracknum+1, 'vol'], 'float', rol_tr_volume[1], notelen, 'instant')
    if len(rol_tr_pitch[1]) > 1: auto_nopl.twopoints(['track', tracknum+1, 'pitch'], 'float', rol_tr_pitch[1], notelen, 'instant')
    
    placementdata = placement_data.nl2pl(cvpj_notelist)
    tracks_rm.track_create(cvpj_l, cvpj_trackid, 'instruments')
    tracks_rm.track_visual(cvpj_l, cvpj_trackid, name=rol_tr_voice[0])
    tracks_rm.add_pl(cvpj_l, cvpj_trackid, 'notes', placementdata)

# --------------------------------------- Plugin ----------------------------------------

class input_adlib_rol(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'adlib_rol'
    def getname(self): return 'AdLib Visual Composer'
    def gettype(self): return 'rm'
    def getdawcapabilities(self): 
        return {
        'auto_nopl': True,
        'track_nopl': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(4)
        bytesdata = bytestream.read(40)
        if bytesdata == b'\\roll\\default\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00': return True
        else: return False
    def parse(self, input_file, extra_param):
        global cvpj_l
        song_file = open(input_file, 'rb')
        cvpj_l = {}
        dataset = data_dataset.dataset('./data_dset/adlib_rol.dset')
        dataset_midi = data_dataset.dataset('./data_dset/midi.dset')

        adlib_bnk = None
        if 'extrafile' in extra_param:
            adlib_bnk = load_bank(extra_param['extrafile'])
            numinst = len(adlib_bnk[0])
            for instname in adlib_bnk[0]:
                instname_upper = instname.upper()
                adlibrol_instname, _ = dataset.object_get_name_color('inst', instname_upper)
                tracks_rm.inst_create(cvpj_l, instname_upper)
                tracks_rm.inst_visual(cvpj_l, instname_upper, name=adlibrol_instname)
                tracks_rm.inst_pluginid(cvpj_l, instname_upper, instname_upper)
                instdatanum = adlib_bnk[0][instname][0]
                if instdatanum <= numinst:
                    opl2data = adlib_bnk[1][adlib_bnk[0][instname][0]]

                    fmdata = plugin_fm.fm_data('opl2')

                    tracks_rm.inst_dataval_add(cvpj_l, instname_upper, 'instdata', 'middlenote', 0)
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

                    fmdata.to_cvpj(cvpj_l, instname_upper)
                    
        else:
            miditolist = dataset.midito_list('inst')
            if miditolist:
                for instid in miditolist:
                    tracks_rm.import_dset(cvpj_l, instid, instid, dataset, dataset_midi, None, None)

        rol_header_majorVersion = int.from_bytes(song_file.read(2), 'little')
        print("[input-adlib_rol] majorVersion: " + str(rol_header_majorVersion))
        
        rol_header_minorVersion = int.from_bytes(song_file.read(2), 'little')
        print("[input-adlib_rol] minorVersion: " + str(rol_header_majorVersion))
        
        rol_header_signature = song_file.read(40)

        rol_header_tickBeat = int.from_bytes(song_file.read(2), 'little')
        print("[input-adlib_rol] tickBeat: " + str(rol_header_tickBeat))
        
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
        notelen = (2/rol_header_tickBeat)*2
        t_tempo_data = parsetrack_tempo(song_file, notelen)

        auto_nopl.twopoints(['main', 'bpm'], 'float', t_tempo_data[2], notelen, 'instant')
        for tracknum in range(10): parsetrack(song_file, tracknum, (2/rol_header_tickBeat)*2)
        auto_nopl.to_cvpj(cvpj_l)
        
        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True
        song.add_timesig(cvpj_l, rol_header_beatMeasure, 4)
        song.add_param(cvpj_l, 'bpm', t_tempo_data[1])
        return json.dumps(cvpj_l)

