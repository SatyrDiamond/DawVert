# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import tracks
from functions import note_data
from functions import placement_data
from functions import idvals
from functions import auto
from functions import data_bytes
from functions import plugins
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
    used_instruments = []
    for _ in range(track_num_events): 
        timbre_pos = int.from_bytes(file_stream.read(2), 'little')
        timbre_name = file_stream.read(9).split(b'\x00')[0].decode('ascii')
        if timbre_name not in used_instruments: used_instruments.append(timbre_name)
        rol_timbre_events[timbre_pos] = timbre_name
        file_stream.read(3)
    return track_name, rol_timbre_events, used_instruments

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

def closest(myList, in_value):
    outval = 0
    for num in myList:
        if num <= in_value: outval = num
    return outval

def parsetrack(file_stream, tracknum, notelen):
    rol_tr_voice = parsetrack_voice(file_stream)
    rol_tr_timbre = parsetrack_timbre(file_stream)
    rol_tr_volume = parsetrack_float(file_stream, 1, 0)
    rol_tr_pitch = parsetrack_float(file_stream, 1, -1)

    trackinstpart = 'track_'+str(tracknum+1)+'_'

    timbrepoints = []
    for timbrepos in rol_tr_timbre[1]:
        timbrepoints.append(timbrepos)

    for used_instrument in rol_tr_timbre[2]:
        instid = trackinstpart+used_instrument

        used_instrument_upper = used_instrument.upper()

        adlibrol_instname = idvals.get_idval(idvals_inst_adlib_rol, used_instrument_upper, 'name')
        if adlibrol_instname == 'noname': adlibrol_instname = used_instrument

        cvpj_instdata = {}

        if adlib_bnk == None:
            cvpj_instdata = {}
            adlibrol_gminst = idvals.get_idval(idvals_inst_adlib_rol, used_instrument_upper, 'gm_inst')
            if adlibrol_gminst != None: 
                pluginid = plugins.get_id()
                plugins.add_plug_gm_midi(cvpj_l, pluginid, 0, adlibrol_gminst-1)
                cvpj_instdata['pluginid'] = pluginid
        else:
            if used_instrument_upper in adlib_bnk[0]:
                opl2data = adlib_bnk[1][adlib_bnk[0][used_instrument_upper][0]]
                pluginid = plugins.get_id()
                cvpj_instdata = {}
                cvpj_instdata['middlenote'] = 24
                cvpj_instdata['pluginid'] = pluginid
                plugins.add_plug(cvpj_l, pluginid, 'fm', 'opl2')
                
                if opl2data[0][0] == 1: 
                    plugins.add_plug_param(cvpj_l, pluginid, 'perctype', opl2data[0][1]-6, 'int', 'perctype')
                else: 
                    plugins.add_plug_param(cvpj_l, pluginid, 'perctype', 0, 'int', 'perctype')

                plugins.add_plug_param(cvpj_l, pluginid, 'tremolo_depth', 0, 'int', 'tremolo_depth')
                plugins.add_plug_param(cvpj_l, pluginid, 'vibrato_depth', 0, 'int', 'vibrato_depth')
                plugins.add_plug_param(cvpj_l, pluginid, 'fm', 1, 'int', 'fm')
                
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_scale', opl2data[1][0], 'int', 'op1_scale')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_freqmul', opl2data[1][1], 'int', 'op1_freqmul')
                plugins.add_plug_param(cvpj_l, pluginid, 'feedback', opl2data[1][2], 'int', 'feedback')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_env_attack', (opl2data[1][3]*-1)+15, 'int', 'op1_env_attack')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_env_sustain', (opl2data[1][4]*-1)+15, 'int', 'op1_env_sustain')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_perc_env', int(not bool(opl2data[1][5])), 'int', 'op1_perc_env')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_env_decay', (opl2data[1][6]*-1)+15, 'int', 'op1_env_decay')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_env_release', (opl2data[1][7]*-1)+15, 'int', 'op1_env_release')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_level', (opl2data[1][8]*-1)+63, 'int', 'op1_level')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_tremolo', opl2data[1][9], 'int', 'op1_tremolo')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_vibrato', opl2data[1][10], 'int', 'op1_vibrato')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_ksr', opl2data[1][11], 'int', 'op1_ksr')
                plugins.add_plug_param(cvpj_l, pluginid, 'fm', opl2data[1][12], 'int', 'fm')
                plugins.add_plug_param(cvpj_l, pluginid, 'op1_waveform', opl2data[3][0], 'int', 'op1_waveform')

                plugins.add_plug_param(cvpj_l, pluginid, 'op2_scale', opl2data[2][0], 'int', 'op2_scale')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_freqmul', opl2data[2][1], 'int', 'op2_freqmul')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_env_attack', (opl2data[2][3]*-1)+15, 'int', 'op2_env_attack')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_env_sustain', (opl2data[2][4]*-1)+15, 'int', 'op2_env_sustain')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_perc_env', int(not bool(opl2data[2][5])), 'int', 'op2_perc_env')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_env_decay', (opl2data[2][6]*-1)+15, 'int', 'op2_env_decay')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_env_release', (opl2data[2][7]*-1)+15, 'int', 'op2_env_release')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_level', (opl2data[2][8]*-1)+63, 'int', 'op2_level')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_tremolo', opl2data[2][9], 'int', 'op2_tremolo')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_vibrato', opl2data[2][10], 'int', 'op2_vibrato')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_ksr', opl2data[2][11], 'int', 'op2_ksr')
                plugins.add_plug_param(cvpj_l, pluginid, 'op2_waveform', opl2data[3][1], 'int', 'op2_waveform')


        tracks.m_create_inst(cvpj_l, instid, cvpj_instdata)
        tracks.m_basicdata_inst(cvpj_l, instid, adlibrol_instname+' (Trk'+str(tracknum+1)+')', None, None, None)
        tracks.m_param_inst(cvpj_l, instid, 'fxrack_channel', tracknum+1)

        if len(rol_tr_pitch[1]) > 1: tracks.a_auto_nopl_twopoints(['track', instid, 'pitch'], 'float', rol_tr_pitch[1], notelen, 'instant')

    cvpj_notelist = []
    curtrackpos = 0
    for rol_notedata in rol_tr_voice[1]:
        if rol_notedata[0] >= 12:
            cvpj_noteinst = trackinstpart+rol_tr_timbre[1][closest(timbrepoints, curtrackpos)]
            cvpj_notelist.append(note_data.mx_makenote(cvpj_noteinst, curtrackpos*notelen, rol_notedata[1]*notelen, rol_notedata[0]-48, None, None))
        curtrackpos += rol_notedata[1]

    print('[input-adlib_rol] Track: "'+rol_tr_voice[0]+'", Instruments: '+str(rol_tr_timbre[2]))
    cvpj_l['fxrack'][tracknum+1] = {"name": rol_tr_voice[0]}

    if len(rol_tr_volume) > 1: tracks.a_auto_nopl_twopoints(['fxmixer', tracknum+1, 'vol'], 'float', rol_tr_volume[1], notelen, 'instant')
    
    placementdata = placement_data.nl2pl(cvpj_notelist)
    tracks.m_playlist_pl(cvpj_l, tracknum+1, rol_tr_voice[0], None, placementdata)

# --------------------------------------- Plugin ----------------------------------------

class input_adlib_rol(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'adlib_rol'
    def getname(self): return 'AdLib Visual Composer'
    def gettype(self): return 'm'
    def getdawcapabilities(self): 
        return {
        'auto_nopl': False,
        'fxrack': True,
        'placement_cut': False,
        'placement_loop': False,
        'track_lanes': True,
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
        global idvals_inst_adlib_rol
        global adlib_bnk

        song_file = open(input_file, 'rb')

        adlib_bnk = None
        if 'extrafile' in extra_param:
            adlib_bnk = load_bank(extra_param['extrafile'])

        idvals_inst_adlib_rol = idvals.parse_idvalscsv('data_idvals/adlib_rol_inst.csv')

        cvpj_l = {}

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
        
        tracks.a_auto_nopl_twopoints(['main', 'bpm'], 'float', t_tempo_data[2], notelen, 'instant')

        cvpj_l['fxrack'] = {}

        for tracknum in range(10):
            parsetrack(song_file, tracknum, (2/rol_header_tickBeat)*2)

        tracks.a_auto_nopl_to_cvpj(cvpj_l)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['timesig_numerator'] = rol_header_beatMeasure
        cvpj_l['timesig_denominator'] = 4
        
        cvpj_l['bpm'] = t_tempo_data[1]
        return json.dumps(cvpj_l)

