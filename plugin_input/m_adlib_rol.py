# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import note_data
from functions import placements
from functions import idvals
import plugin_input
import json
import struct

def parsetrack_tempo(file_stream, tickBeat):
    track_name = file_stream.read(15).split(b'\x00')[0].decode('ascii')
    track_tempo = struct.unpack("f", file_stream.read(4))[0]
    track_num_events = int.from_bytes(file_stream.read(2), 'little')
    tempo_data = []
    for _ in range(track_num_events): 
        tempo_data_part = []
        tempo_data_part.append(int.from_bytes(file_stream.read(2), 'little'))
        tempo_data_part.append(struct.unpack("<f", file_stream.read(4))[0])
        tempo_data.append(tempo_data_part)

    return (track_name, track_tempo, tempo_data)

def parsetrack_voice(file_stream):
    track_name = file_stream.read(15).split(b'\x00')[0].decode('ascii')
    track_nTicks = int.from_bytes(file_stream.read(2), 'little')
    rol_notelist = []
    curtickpos = 0
    while curtickpos < track_nTicks: 
        rol_note_data = struct.unpack("HH", file_stream.read(4))
        curtickpos += rol_note_data[1]
        rol_notelist.append(rol_note_data)
    #print('VOICE', track_name, len(rol_notelist))
    return (track_name, rol_notelist)

def parsetrack_timbre(file_stream):
    track_name = file_stream.read(15).split(b'\x00')[0].decode('ascii')
    track_num_events = int.from_bytes(file_stream.read(2), 'little')
    rol_timbre_events = {}
    used_instruments = []
    for _ in range(track_num_events): 
        timbre_pos = int.from_bytes(file_stream.read(2), 'little')
        timbre_name = file_stream.read(9).split(b'\x00')[0].decode('ascii')
        if timbre_name not in used_instruments: used_instruments.append(timbre_name)
        rol_timbre_events[timbre_pos] = timbre_name
        file_stream.read(3)
    #print('TIMBRE', track_name, rol_timbre_events)
    return (track_name, rol_timbre_events, used_instruments)

def parsetrack_volume(file_stream):
    track_name = file_stream.read(15).split(b'\x00')[0].decode('ascii')
    track_num_events = int.from_bytes(file_stream.read(2), 'little')
    rol_vol_events = []
    for _ in range(track_num_events): 
        rol_vol_events.append(struct.unpack("<hf", file_stream.read(6)))
    #print('VOLUME', track_name, rol_vol_events)
    return (track_name, rol_vol_events)

def parsetrack_pitch(file_stream):
    track_name = file_stream.read(15).split(b'\x00')[0].decode('ascii')
    track_num_events = int.from_bytes(file_stream.read(2), 'little')
    rol_pitch_events = []
    for _ in range(track_num_events): 
        rol_pitch_events.append(struct.unpack("<hf", file_stream.read(6)))
    #print('PITCH', track_name, rol_pitch_events)
    return (track_name, rol_pitch_events)
  
def closest(myList, in_value):
    outval = 0
    for num in myList:
        if num <= in_value: outval = num
    return outval

def parsetrack(file_stream, tracknum, notelen):
    rol_tr_voice = parsetrack_voice(file_stream)
    rol_tr_timbre = parsetrack_timbre(file_stream)
    rol_tr_volume = parsetrack_volume(file_stream)
    rol_tr_pitch = parsetrack_pitch(file_stream)

    trackinstpart = 'track_'+str(tracknum+1)+'_'

    timbrepoints = []
    for timbrepos in rol_tr_timbre[1]:
        timbrepoints.append(timbrepos)

    for used_instrument in rol_tr_timbre[2]:
        instid = trackinstpart+used_instrument
        adlibrol_instname = idvals.get_idval(idvals_inst_adlib_rol, used_instrument.upper(), 'name')
        if adlibrol_instname == 'noname': adlibrol_instname = used_instrument

        adlibrol_gminst = idvals.get_idval(idvals_inst_adlib_rol, used_instrument.upper(), 'gm_inst')
        cvpj_instdata = {}
        if adlibrol_gminst != None: cvpj_instdata = {'plugin': 'general-midi', 'plugindata': {'bank': 0, 'inst': adlibrol_gminst}}

        tracks.m_addinst(cvpj_l, instid,cvpj_instdata)
        tracks.m_addinst_data(cvpj_l, instid, adlibrol_instname+' (Trk'+str(tracknum+1)+')', None, None, None)
        tracks.m_addinst_param(cvpj_l, instid, 'fxrack_channel', tracknum+1)

    cvpj_notelist = []
    curtrackpos = 0
    for rol_notedata in rol_tr_voice[1]:
        if rol_notedata[0] >= 12:
            cvpj_noteinst = trackinstpart+rol_tr_timbre[1][closest(timbrepoints, curtrackpos)]
            cvpj_notelist.append(note_data.mx_makenote(cvpj_noteinst, curtrackpos*notelen, rol_notedata[1]*notelen, rol_notedata[0]-48, None, None))
        curtrackpos += rol_notedata[1]

    print('[input-adlib_rol] Track: "'+rol_tr_voice[0]+'" Instruments: '+str(rol_tr_timbre[2]))

    cvpj_l['fxrack'][tracknum+1] = {}
    cvpj_l['fxrack'][tracknum+1]["name"] = rol_tr_voice[0]

    placementdata = placements.nl2pl(cvpj_notelist)
    tracks.m_playlist_pl(cvpj_l, tracknum+1, rol_tr_voice[0], None, placementdata)

class input_adlib_rol(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'adlib_rol'
    def getname(self): return 'AdLib Visual Composer'
    def gettype(self): return 'm'
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

        song_file = open(input_file, 'rb')

        idvals_inst_adlib_rol = idvals.parse_idvalscsv('idvals/adlib_rol_inst.csv')

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
        
        t_tempo_data = parsetrack_tempo(song_file, rol_header_tickBeat/rol_header_beatMeasure)
        
        cvpj_l['fxrack'] = {}

        for tracknum in range(10):
            parsetrack(song_file, tracknum, (2/rol_header_tickBeat)*2)

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = True
        
        cvpj_l['timesig_numerator'] = 4
        cvpj_l['timesig_denominator'] = 4
        
        cvpj_l['bpm'] = t_tempo_data[1]
        return json.dumps(cvpj_l)

