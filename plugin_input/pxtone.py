# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_mod
from functions import audio_wav
from functions import folder_samples
import plugin_input
import json
import varint
import struct
import os

ptcop_events = {}
ptcop_events[0] = '--None--'
ptcop_events[1] = 'Note    '
ptcop_events[2] = 'Pitch   '
ptcop_events[3] = 'Pan     '
ptcop_events[4] = 'Velocity'
ptcop_events[5] = 'Volume  '
ptcop_events[6] = 'Porta   '
ptcop_events[12] = 'Voice # '
ptcop_events[13] = 'Group # '
ptcop_events[14] = 'Key Corr'
ptcop_events[15] = 'Pan Time'

colors_inst = [
[0.94, 0.50, 0.00],
[0.41, 0.47, 1.00],
[0.79, 0.72, 0.72],
[0.68, 0.25, 1.00],
[0.57, 0.78, 0.00],
[0.99, 0.20, 0.80],
[0.00, 0.75, 0.38],
[1.00, 0.47, 0.36],
[0.00, 0.74, 1.00]]

global colornum
colornum = 0

def getcolor():
    global colornum
    out_color = colors_inst[colornum]
    colornum += 1
    if colornum == 9: colornum = 0
    return out_color

def parse_event(bio_stream):
    position = varint.decode_stream(bio_stream)
    unitnum = int.from_bytes(bio_stream.read(1), "little")
    eventnum = int.from_bytes(bio_stream.read(1), "little")
    value = varint.decode_stream(bio_stream)

    if eventnum == 2: 
        pitch = (value-25344)/256
        note = int((value-25344)/256)
        value = [note, note-pitch]
    if eventnum == 4: value = value/128

    return [position, unitnum, eventnum, value]

def parse_matePTV(bio_stream):
    size, voice_number, tuning, sz = struct.unpack("hhfi", bio_stream.read(12))
    ptvoice_data = bio_stream.read(sz)

def parse_assiWOIC(bio_stream, chunksize):
    voice_number = int.from_bytes(bio_stream.read(4), "little")
    print('[input-ptcop]   Voice #: '+str(voice_number))
    voice_name_bytes = bio_stream.read(chunksize-4)
    voice_name = voice_name_bytes.split(b'\x00')[0].decode("shift-jis")
    print('[input-ptcop]   Voice Name: '+str(voice_name))
    return voice_number, voice_name

def parse_assiUNIT(bio_stream, chunksize):
    unit_number = int.from_bytes(bio_stream.read(4), "little")
    print('[input-ptcop]   Unit #: '+str(unit_number))
    unit_name_bytes = bio_stream.read(chunksize-4)
    unit_name = unit_name_bytes.split(b'\x00')[0].decode("shift-jis")
    print('[input-ptcop]   Unit Name: '+str(unit_name))
    return unit_number, unit_name

class input_pxtone(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'ptcop'
    def getname(self): return 'PxTone'
    def gettype(self): return 'm'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(16)
        if bytesdata == b'PTCOLLAGE-071119': return True
        else: return False
    def parse(self, input_file, extra_param):
        song_file = open(input_file, 'rb')
        song_file.seek(0,2)
        song_filesize = song_file.tell()
        song_file.seek(0)
        
        ptcop_header = song_file.read(16)
        ptcop_unk = int.from_bytes(song_file.read(4), "little")
        ptcop_unit_events = {}
        ptcop_name_voice = {}
        ptcop_name_unit = {}
        ptcop_song_name = None
        ptcop_song_comment = None
        ptcop_voice_num = 0

        t_voice_data = []

        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_timemarkers = []
        cvpj_l_playlist = {}

        while song_filesize > song_file.tell():
            chunkname = song_file.read(8)
            chunksize = int.from_bytes(song_file.read(4), "little")

            if chunkname == b'MasterV5':
                print('[input-ptcop] Chunk: Master', chunksize)
                ptcop_mas_unk1 = int.from_bytes(song_file.read(2), "little")
                ptcop_mas_beat = int.from_bytes(song_file.read(1), "little")
                print('[input-ptcop]   Beat: '+str(ptcop_mas_beat))
                ptcop_mas_unk2 = int.from_bytes(song_file.read(2), "little")
                ptcop_mas_beattempo = struct.unpack(">f", struct.pack("I", int.from_bytes(song_file.read(2), "big")))[0]
                print('[input-ptcop]   Tempo: '+str(ptcop_mas_beattempo))
                ptcop_mas_repeat = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Repeat: '+str(ptcop_mas_repeat))
                ptcop_mas_last = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Last: '+str(ptcop_mas_last))

            elif chunkname == b'Event V5':
                print('[input-ptcop] Chunk: Event', chunksize)
                num_of_events = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   # of events: '+str(num_of_events))
                
                cur_voice = 0
                cur_group = 0
                position_global = 0
                
                for _ in range(num_of_events):
                    eventdata = parse_event(song_file)
                    if eventdata[2] == 12: cur_voice = eventdata[3]
                    if eventdata[2] == 13: cur_group = eventdata[3]
                    if eventdata[1] not in ptcop_unit_events: ptcop_unit_events[eventdata[1]] = []
                    position_global += eventdata[0]
                    eventdata[0] = position_global
                    ptcop_unit_events[eventdata[1]].append(eventdata)
        
            elif chunkname == b'mateOGGV':
                print('[input-ptcop] Chunk: mateOGGV', chunksize)
                song_file.read(chunksize)
                t_voice_data.append(['none', {}])
                ptcop_voice_num += 1

            elif chunkname == b'matePTV ':
                print('[input-ptcop] Chunk: PTVoice', chunksize)
                parse_matePTV(song_file)
                t_voice_data.append(['none', {}])
                ptcop_voice_num += 1

            elif chunkname == b'matePTN ':
                print('[input-ptcop] Chunk: PTNoise', chunksize)
                song_file.read(chunksize)
                t_voice_data.append(['none', {}])
                ptcop_voice_num += 1

            elif chunkname == b'matePCM ':
                print('[input-ptcop] Chunk: PCM', chunksize)
                song_file.read(3)
                ptcop_pcm_basic_key_field = song_file.read(1)[0]
                print('[input-ptcop]   Basic Key field: '+str(ptcop_pcm_basic_key_field))
                ptcop_pcm_flags = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Voice flags: '+str(ptcop_pcm_flags))
                ptcop_pcm_loop = bool(ptcop_pcm_flags & 0b000000000000001)
                print('[input-ptcop]   Loop: '+str(ptcop_pcm_loop))
                ptcop_pcm_smooth = bool(ptcop_pcm_flags & 0b000000000000010)
                print('[input-ptcop]   Smooth: '+str(ptcop_pcm_smooth))
                ptcop_pcm_ch = int.from_bytes(song_file.read(2), "little")
                print('[input-ptcop]   Channels: '+str(ptcop_pcm_ch))
                ptcop_pcm_bits = int.from_bytes(song_file.read(2), "little")
                print('[input-ptcop]   Bits: '+str(ptcop_pcm_bits))
                ptcop_pcm_hz = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Hz: '+str(ptcop_pcm_hz))
                ptcop_pcm_key_correct = struct.unpack("f", song_file.read(4))[0]
                print('[input-ptcop]   Key Correct: '+str(ptcop_pcm_key_correct))
                ptcop_pcm_samples = int.from_bytes(song_file.read(4), "little")//(ptcop_pcm_bits//8)
                print('[input-ptcop]   Samples: '+str(ptcop_pcm_samples))
                ptcop_pcm_data = song_file.read((ptcop_pcm_bits//8) * ptcop_pcm_samples)

                os.makedirs(samplefolder, exist_ok=True)
                wave_path = samplefolder + str(ptcop_voice_num+1).zfill(2) + '.wav'

                plugindata = {'file': wave_path, 'start': 0, 'end': ptcop_pcm_samples, 'trigger': 'normal'}

                if ptcop_pcm_smooth == True: plugindata['interpolation'] = "linear"
                else: plugindata['interpolation'] = "none"

                if ptcop_pcm_loop == 1: 
                    loopdata = {'loop':[0, ptcop_pcm_samples]}
                    plugindata['loop'] = {'enabled':1, 'mode':"normal", 'points':[0, ptcop_pcm_samples]}
                else: 
                    loopdata = None
                    plugindata['loop'] = {'enabled':0, 'mode':"normal", 'points':[0, ptcop_pcm_samples]}

                audio_wav.generate(wave_path, ptcop_pcm_data, ptcop_pcm_ch, ptcop_pcm_hz, ptcop_pcm_bits, loopdata)

                t_voice_data.append(['sampler', plugindata])
                ptcop_voice_num += 1


            elif chunkname == b'assiWOIC':
                print('[input-ptcop] Chunk: assiWOIC', chunksize)
                assiWOIC_data = parse_assiWOIC(song_file, chunksize)
                ptcop_name_voice[assiWOIC_data[0]] = assiWOIC_data[1]

            elif chunkname == b'num UNIT':
                print('[input-ptcop] Chunk: num UNIT', chunksize)
                num_units = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   # of units: '+str(num_units))

            elif chunkname == b'assiUNIT':
                print('[input-ptcop] Chunk: assiUNIT', chunksize)
                assiUNIT_data = parse_assiUNIT(song_file, chunksize)
                ptcop_name_unit[assiUNIT_data[0]] = assiUNIT_data[1]

            elif chunkname == b'textNAME':
                print('[input-ptcop] Chunk: textNAME', chunksize)
                ptcop_song_name = song_file.read(chunksize).decode("shift-jis")

            elif chunkname == b'textCOMM':
                print('[input-ptcop] Chunk: textCOMM', chunksize)
                ptcop_song_comment = song_file.read(chunksize).decode("shift-jis")

            elif chunkname == b'effeDELA':
                print('[input-ptcop] Chunk: effeDELA', chunksize)
                song_file.read(chunksize)

            elif chunkname == b'effeOVER':
                print('[input-ptcop] Chunk: effeOVER', chunksize)
                song_file.read(chunksize)

            elif chunkname == b'pxtoneND':
                print('[input-ptcop] End.')
                break

            else:
                print('[input-ptcop] Unknown Chunk:', chunkname)
                exit()
            print('[input-ptcop]')

        t_notelist = {}

        for unit_eventnum in ptcop_unit_events:
            t_notelist[unit_eventnum] = []
            prevpos = 0
            position_global = 0
            cur_note = -3
            cur_voice = 0
            for unit_event in ptcop_unit_events[unit_eventnum]:
                if unit_event[2] == 2: cur_note = unit_event[3][0]+12
                if unit_event[2] == 12: cur_voice = unit_event[3]
                if unit_event[2] == 4: t_notelist[unit_eventnum][-1]['vol'] = unit_event[3]
                position_global = unit_event[0]

                if unit_event[2] == 1: 
                    cvpj_note = {}
                    cvpj_note['position'] = position_global/120
                    cvpj_note['key'] = cur_note
                    cvpj_note['duration'] = unit_event[3]/120
                    cvpj_note['instrument'] = 'ptcop_'+str(cur_voice)
                    t_notelist[unit_eventnum].append(cvpj_note)

                prevpos = unit_event[0]

        for unitnum in t_notelist:
            cvpj_notelist = t_notelist[unitnum]

            cvpj_placement = {}
            cvpj_placement['position'] = 0
            cvpj_placement['duration'] = note_mod.getduration(cvpj_notelist)
            cvpj_placement['type'] = 'instruments'
            cvpj_placement['notelist'] = cvpj_notelist

            playlistrowdata = {}
            if unitnum in ptcop_name_unit: playlistrowdata['name'] = ptcop_name_unit[unitnum]
            playlistrowdata['color'] = [0.14, 0.00, 0.29]
            playlistrowdata['placements'] = [cvpj_placement]

            cvpj_l_playlist[str(unitnum+1)] = playlistrowdata

        for voicenum in range(ptcop_voice_num):
            cvpj_inst = {}
            if voicenum in ptcop_name_voice: cvpj_inst['name'] = ptcop_name_voice[voicenum]
            else: cvpj_inst['name'] = ''
            cvpj_inst["pan"] = 0.0
            cvpj_inst["vol"] = 1.0
            cvpj_inst['color'] = getcolor()
            cvpj_inst["instdata"] = {}
            cvpj_inst['instdata']['plugin'] = t_voice_data[voicenum][0]
            cvpj_inst['instdata']['plugindata'] = t_voice_data[voicenum][1]
            instid = 'ptcop_'+str(voicenum)
            cvpj_l_instruments[instid] = cvpj_inst
            cvpj_l_instrumentsorder.append(instid)

        cvpj_l['info'] = {}
        if ptcop_song_name != None: cvpj_l['info']['title'] = ptcop_song_name
        if ptcop_song_comment != None: 
            cvpj_l['info']['message'] = {}
            cvpj_l['info']['message']['type'] = 'text'
            cvpj_l['info']['message']['text'] = ptcop_song_comment

        cvpj_l['use_addwrap'] = True
        cvpj_l['use_singlenotelistcut'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['timesig_numerator'] = ptcop_mas_beat
        cvpj_l['timesig_denominator'] = 4
        cvpj_l['instruments_data'] = cvpj_l_instruments
        cvpj_l['instruments_order'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = ptcop_mas_beattempo
        return json.dumps(cvpj_l)
