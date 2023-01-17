# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import song_tracker
from functions import note_convert
import plugin_input
import zlib
import struct
import json

chiptypecolors = {}
chiptypecolors['fm'] = [0.20, 0.80, 1.00]
chiptypecolors['square'] = [0.40, 1.00, 0.20]
chiptypecolors['pulse'] = [0.40, 1.00, 0.20]
chiptypecolors['noise'] = [0.80, 0.80, 0.80]
chiptypecolors['fmop'] = [0.20, 0.40, 1.00]
chiptypecolors['wavetable'] = [1.00, 0.50, 0.20]
chiptypecolors['pce'] = [1.00, 0.50, 0.20]
chiptypecolors['pcm'] = [1.00, 0.90, 0.20]
chiptypecolors['sample'] = [1.00, 0.90, 0.20]
chiptypecolors['adpcma'] = [1.00, 0.90, 0.20]
chiptypecolors['c64'] = [0.80, 0.80, 0.80]

chipname = {}
chipname['fm'] = 'FM 4op'
chipname['square'] = 'Square'
chipname['pulse'] = 'Pulse'
chipname['noise'] = 'Noise'
chipname['fmop'] = 'FM OP'
chipname['wavetable'] = 'Wavetable'
chipname['pce'] = 'PC Engine'
chipname['pcm'] = 'PCM'
chipname['adpcma'] = 'ADPCM-A'
chipname['sample'] = 'Sample'
chipname['c64'] = 'C64'

def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

def fxget(fxtype, fxparam, output_param, output_extra): 
    if fxtype == 0 and fxparam != 0:
        arpeggio_first = fxparam >> 4
        arpeggio_second = fxparam & 0x0F
        output_param['tracker_arpeggio'] = [arpeggio_first, arpeggio_second]
    if fxtype == 1: output_param['tracker_slide_up'] = fxparam
    if fxtype == 2: output_param['tracker_slide_down'] = fxparam
    if fxtype == 3: output_param['tracker_slide_to_note'] = fxparam
    if fxtype == 4: 
        vibrato_params = {}
        vibrato_params['speed'], vibrato_params['depth'] = splitbyte(fxparam)
        output_param['vibrato'] = vibrato_params
    if fxtype == 5:
        pos, neg = splitbyte(fxparam)
        output_param['tracker_vol_slide_plus_slide_to_note'] = (neg*-1) + pos
    if fxtype == 6:
        pos, neg = splitbyte(fxparam)
        output_param['tracker_vol_slide_plus_vibrato'] = (neg*-1) + pos
    if fxtype == 7:
        tremolo_params = {}
        tremolo_params['speed'], tremolo_params['depth'] = splitbyte(fxparam)
        output_param['tremolo'] = tremolo_params
    if fxtype == 8: output_param['pan'] = (fxparam-128)/128
    if fxtype == 9: output_param['audio_mod_inst_offset'] = fxparam*256
    if fxtype == 10:
        pos, neg = splitbyte(fxparam)
        output_param['tracker_vol_slide'] = (neg*-1) + pos
    if fxtype == 11: output_extra['tracker_jump_to_offset'] = fxparam
    if fxtype == 12: output_param['vol'] = fxparam/64
    if fxtype == 13: output_extra['tracker_break_to_row'] = fxparam
    if fxtype == 15:
        if fxparam < 32: output_extra['tracker_speed'] = fxparam
        else: output_extra['tempo'] = fxparam

def dmfstring(bio_dmf): 
    stringlen = int.from_bytes(bio_dmf.read(1), "little")
    return bio_dmf.read(stringlen).decode('utf-8').rstrip('\x00')

def dmfenv(bio_dmf): 
    ENVELOPE_SIZE = int.from_bytes(bio_dmf.read(1), "little")
    envdata = {}
    envdata['values'] = struct.unpack('I'*ENVELOPE_SIZE, bio_dmf.read(ENVELOPE_SIZE*4))
    if ENVELOPE_SIZE != 0: envdata['looppos'] = int.from_bytes(bio_dmf.read(1), "little", signed=True)
    return envdata

class input_cvpj_r(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'deflemask'
    def getname(self): return 'DefleMask'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        output = False
        bytestream = open(input_file, 'rb')
        filedata = bytestream.read()
        try:
            zlibdata = zlib.decompress(filedata)
            dmfdata = data_bytes.bytearray2BytesIO(zlibdata)
            dmf_header = dmfdata.read(16)
            if dmf_header == b'.DelekDefleMask.': output = True
            else: output = False
        except: output = False
        return output
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'rb')
        bio_dmf = data_bytes.bytearray2BytesIO(zlib.decompress(bytestream.read()))

        dmf_header = bio_dmf.read(16)
        if dmf_header != b'.DelekDefleMask.':
            print('File is not DefleMask.')
            exit()

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}

        # FORMAT FLAGS
        dmf_version = int.from_bytes(bio_dmf.read(1), "little")
        dmf_system = int.from_bytes(bio_dmf.read(1), "little")

        # SYSTEM SET
        if dmf_system == int("02",16): #GENESIS
            t_chantype = ['fm','fm','fm','fm','fm','fm','square','square','square','noise']
            t_channames = ['FM 1','FM 2','FM 3','FM 4','FM 5','FM 6','Square 1','Square 2','Square 3','Noise']
        if dmf_system == int("42",16): #SYSTEM_GENESIS (mode EXT. CH3) 
            t_chantype = ['fm','fm','fmop','fmop','fmop','fmop','fm','fm','fm','square','square','square','noise']
            t_channames = ['FM 1','FM 2','FM 3 OP 1','FM 3 OP 2','FM 3 OP 3','FM 3 OP 4','FM 4','FM 5','FM 6','Square 1','Square 2','Square 3','Noise']
        if dmf_system == int("03",16): #SMS
            t_chantype = ['square','square','square','noise']
            t_channames = ['Square 1','Square 2','Square 3','Noise']
        if dmf_system == int("04",16): #GAMEBOY
            t_chantype = ['pulse','pulse','wavetable','noise']
            t_channames = ['Pulse 1','Pulse 2','Wavetable','Noise']
        if dmf_system == int("05",16): #PCENGINE
            t_chantype = ['pce','pce','pce','pce','pce','pce']
            t_channames = ['Channel 1','Channel 2','Channel 3','Channel 4','Channel 5','Channel 6']
        if dmf_system == int("06",16): #NES
            t_chantype = ['pulse','pulse','triangle','noise','pcm']
            t_channames = ['Pulse 1','Pulse 2','Triangle','Noise','PCM']
        if dmf_system == int("07",16): #C64 (SID 8580)
            t_chantype = ['c64','c64','c64']
            t_channames = ['Channel 1','Channel 2','Channel 3']
        if dmf_system == int("47",16): #C64 (mode SID 6581)
            t_chantype = ['c64','c64','c64']
            t_channames = ['Channel 1','Channel 2','Channel 3']
        if dmf_system == int("08",16): #ARCADE
            t_chantype = ['fm','fm','fm','fm','fm','fm','fm','fm','sample','sample','sample','sample','sample']
            t_channames = ['FM 1','FM 2','FM 3','FM 4','FM 5','FM 6','FM 7','FM 8','Channel 1','Channel 2','Channel 3','Channel 4','Channel 5']
        if dmf_system == int("09",16): #NEOGEO
            t_chantype = ['fm','fm','fm','fm','psg','psg','psg','adpcma','adpcma','adpcma','adpcma','adpcma','adpcma']
            t_channames = ['FM 1','FM 2','FM 3','FM 4','PSG 1','PSG 2','PSG 3','ADPCM-A 1','ADPCM-A 2','ADPCM-A 3','ADPCM-A 4','ADPCM-A 5','ADPCM-A 6']
        if dmf_system == int("49",16): #NEOGEO (mode EXT. CH2)
            t_chantype = ['fm','fm','fmop','fmop','fmop','fmop','fm','psg','psg','psg','adpcma','adpcma','adpcma','adpcma','adpcma','adpcma']
            t_channames = ['FM 1','FM 2 OP 1','FM 2 OP 2','FM 2 OP 3','FM 2 OP 4','FM 3','FM 4','PSG 1','PSG 2','PSG 3','ADPCM-A 1','ADPCM-A 2','ADPCM-A 3','ADPCM-A 4','ADPCM-A 5','ADPCM-A 6']

        dmf_SYSTEM_TOTAL_CHANNELS = len(t_chantype)

        # VISUAL INFORMATION
        dmf_song_name = dmfstring(bio_dmf)
        dmf_song_author = dmfstring(bio_dmf)
        dmf_highlight_a_pat = int.from_bytes(bio_dmf.read(1), "little")
        dmf_highlight_b_pat = int.from_bytes(bio_dmf.read(1), "little")

        # MODULE INFORMATION
        dmf_TimeBase = int.from_bytes(bio_dmf.read(1), "little")
        dmf_TickTime1 = int.from_bytes(bio_dmf.read(1), "little")
        dmf_TickTime2 = int.from_bytes(bio_dmf.read(1), "little")
        dmf_FramesMode = int.from_bytes(bio_dmf.read(1), "little")
        dmf_UsingCustomHZ = int.from_bytes(bio_dmf.read(1), "little")
        dmf_CustomHZ1 = int.from_bytes(bio_dmf.read(1), "little")
        dmf_CustomHZ2 = int.from_bytes(bio_dmf.read(1), "little")
        dmf_CustomHZ3 = int.from_bytes(bio_dmf.read(1), "little")
        dmf_TOTAL_ROWS_PER_PATTERN = int.from_bytes(bio_dmf.read(4), "little")
        dmf_TOTAL_ROWS_IN_PATTERN_MATRIX = int.from_bytes(bio_dmf.read(1), "little")

        # PATTERN MATRIX VALUES
        t_ch_pat_orders = []
        for _ in range(dmf_SYSTEM_TOTAL_CHANNELS):
            t_ch_pat_orders.append(struct.unpack('b'*dmf_TOTAL_ROWS_IN_PATTERN_MATRIX, bio_dmf.read(dmf_TOTAL_ROWS_IN_PATTERN_MATRIX)))

        # INSTRUMENTS DATA
        dmf_TOTAL_INSTRUMENTS = int.from_bytes(bio_dmf.read(1), "little")

        dmf_insts = []
        dmf_instnames = []

        for instnum in range(dmf_TOTAL_INSTRUMENTS):
            dmf_inst = {}
            dmfi_name = dmfstring(bio_dmf)
            dmfi_mode = int.from_bytes(bio_dmf.read(1), "little")
            dmf_instnames.append(dmfi_name)
            if dmfi_mode == 1:
                dmf_inst['fm'] = True
                fmdata = {}
                fmdata['algorithm'] = int.from_bytes(bio_dmf.read(1), "little")
                fmdata['feedback'] = int.from_bytes(bio_dmf.read(1), "little")
                fmdata['lfo'] = int.from_bytes(bio_dmf.read(1), "little") #(FMS on YM2612, PMS on YM2151)
                fmdata['lfo2'] = int.from_bytes(bio_dmf.read(1), "little") #(AMS on YM2612, AMS on YM2151)
                for opnum in range(4):
                    operator_param = {}
                    operator_param['am'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['env_attack'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['env_decay'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['freqmul'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['env_release'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['env_sustain'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['level'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['detune2'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['ratescale'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['detune'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['env_decay2'] = int.from_bytes(bio_dmf.read(1), "little")
                    operator_param['ssgmode'] = int.from_bytes(bio_dmf.read(1), "little")
                    fmdata['op'+str(opnum+1)] = operator_param
                dmf_inst['fmdata'] = fmdata
            else:
                dmf_inst['fm'] = False
                if dmf_system != int("04",16): dmf_inst['env_volume'] = dmfenv(bio_dmf)
                dmf_inst['env_arpeggio'] = dmfenv(bio_dmf)
                dmf_inst['arpeggio_mode'] = int.from_bytes(bio_dmf.read(1), "little")
                dmf_inst['env_duty'] = dmfenv(bio_dmf)
                dmf_inst['env_wavetable'] = dmfenv(bio_dmf)
                if dmf_system == int("07",16) or dmf_system == int("47",16):
                    c64data = {}
                    c64data['wave_triangle'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['wave_saw'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['wave_pulse'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['wave_noise'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['attack'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['decay'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['sustain'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['release'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['pulse width'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['ringmod'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['syncmod'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['to_filter'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['volume_macro_to_filter_cutoff'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['use_filter_values_from_instrument'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['filter_resonance'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['filter_cutoff'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['filter_highpass'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['filter_lowpass'] = int.from_bytes(bio_dmf.read(1), "little")
                    c64data['filter_CH2off'] = int.from_bytes(bio_dmf.read(1), "little")
                    dmf_inst['c64data'] = c64data
                if dmf_system == int("04",16):
                    gameboydata = {}
                    gameboydata['env_volume'] = int.from_bytes(bio_dmf.read(1), "little")
                    gameboydata['env_direction'] = int.from_bytes(bio_dmf.read(1), "little")
                    gameboydata['env_length'] = int.from_bytes(bio_dmf.read(1), "little")
                    gameboydata['sound_length'] = int.from_bytes(bio_dmf.read(1), "little")
                    dmf_inst['gameboydata'] = gameboydata
            dmf_insts.append(dmf_inst)

        #for dmf_inst in dmf_insts:
        #    print(dmf_inst)

        # WAVETABLES DATA
        dmf_wavetables = []

        dmf_TOTAL_WAVETABLES = int.from_bytes(bio_dmf.read(1), "little")
        for _ in range(dmf_TOTAL_WAVETABLES):
            dmf_WAVETABLE_SIZE = int.from_bytes(bio_dmf.read(4), "little")
            wavetable = struct.unpack('I'*dmf_WAVETABLE_SIZE , bio_dmf.read(dmf_WAVETABLE_SIZE*4))
            dmf_wavetables.append(wavetable)

        # PATTERNS DATA

        total_used_instruments = []
        dmf_patterns = []
        for channum in range(dmf_SYSTEM_TOTAL_CHANNELS):
            s_chantype = t_chantype[channum]

            dmf_pat_channel = []
            dmf_CHANNEL_EFFECTS_COLUMNS_COUNT = int.from_bytes(bio_dmf.read(1), "little")
            for patnum in t_ch_pat_orders[channum]:

                table_rows = []
                for _ in range(dmf_TOTAL_ROWS_PER_PATTERN):
                    r_note, r_oct, r_vol = struct.unpack('hhh', bio_dmf.read(6))
                    r_fx = []
                    for _ in range(dmf_CHANNEL_EFFECTS_COLUMNS_COUNT):
                        r_fx.append(struct.unpack('hh', bio_dmf.read(4)))
                    r_inst = int.from_bytes(bio_dmf.read(2), "little", signed=True)

                    output_note = None
                    output_inst = None
                    output_param = {}
                    output_extra = {}

                    if r_vol != -1:
                        if s_chantype != 'fm': output_param['vol'] = r_vol/16
                        else: output_param['vol'] = r_vol/127

                    for r_fxp in r_fx:
                        fxget(r_fxp[0], r_fxp[1], output_param, output_extra)

                    if r_note == 0 and r_oct == 0: output_note = None
                    elif r_note == 100: output_note = 'Off'
                    else: output_note = (r_note + r_oct*12)-60

                    if output_note != None and output_note != 'Off':
                        if s_chantype == 'square':  output_note += 36
                        if s_chantype == 'fm': output_note += 12

                    if r_inst != -1 and output_note != None: output_inst = r_inst

                    table_rows.append([[],[output_note, output_inst, output_param, output_extra]])

                TNT = song_tracker.convertchannel2timednotes(table_rows, '')
                note_convert.timednotes2notelistplacement_track_start()
                NLP = note_convert.timednotes2notelistplacement_parse_timednotes(TNT, s_chantype+'_')

                used_instruments = note_convert.timednotes2notelist_get_used_instruments()

                for used_instrument in used_instruments:
                    ui_split = used_instrument.split('_')
                    if ui_split not in total_used_instruments:
                        total_used_instruments.append(ui_split)

                if NLP != []:
                    nli_data = {}
                    nli_data['type'] = 'instruments'
                    nli_data['name'] = str(t_channames[channum])+' ('+str(patnum)+')'
                    nli_data['color'] = chiptypecolors[t_chantype[channum]]
                    nli_data['notelist'] = NLP[0]['notelist']
                    cvpj_l_notelistindex[str(channum)+'_'+str(patnum)] = nli_data

        plnum = 1
        chnum = 0
        curpos = 0
        for t_ch_pat_order in t_ch_pat_orders:
            curpos = 0
            cvpj_l_playlist[plnum] = {}
            cvpj_l_playlist[plnum]['name'] = t_channames[chnum]
            cvpj_l_playlist[plnum]['color'] = chiptypecolors[t_chantype[chnum]]
            cvpj_l_playlist[plnum]['placements'] = []
            for t_ch_patnum in t_ch_pat_order:
                cvpj_l_placement = {}
                cvpj_l_placement['type'] = "instruments"
                cvpj_l_placement['position'] = curpos
                cvpj_l_placement['duration'] = dmf_TOTAL_ROWS_PER_PATTERN
                cvpj_l_placement['fromindex'] = str(chnum)+'_'+str(t_ch_patnum)
                cvpj_l_playlist[plnum]['placements'].append(cvpj_l_placement)
                curpos += dmf_TOTAL_ROWS_PER_PATTERN
            plnum += 1
            chnum += 1

        for total_used_instrument in total_used_instruments:
            insttype = total_used_instrument[0]
            dmf_instid = total_used_instrument[1]
            dmf_instdata = dmf_insts[int(dmf_instid)]

            cvpj_instid = insttype+'_'+dmf_instid
            cvpj_inst = {}
            #print(dmf_instnames)
            cvpj_inst["name"] = dmf_instnames[int(dmf_instid)]+' ('+chipname[insttype]+')'
            cvpj_inst["pan"] = 0.0
            cvpj_inst["vol"] = 1.0
            if insttype in chiptypecolors:
                cvpj_inst["color"] = chiptypecolors[insttype]
            cvpj_inst["instdata"] = {}
            cvpj_inst["instdata"]["plugindata"] = {}
            if insttype == 'square' or insttype == 'noise':
                cvpj_inst["instdata"]["plugin"] = 'retro'
                cvpj_inst["instdata"]["plugindata"]['wave'] = insttype
                if 'env_volume' in dmf_instdata:
                    cvpj_inst["instdata"]["plugindata"]['env_vol'] = {}
                    valuet = []
                    for item in dmf_instdata['env_volume']['values']: valuet.append(item)
                    cvpj_inst["instdata"]["plugindata"]['env_vol']['values'] = valuet
                    if dmf_instdata['env_volume']['looppos'] != -1:
                        cvpj_inst["instdata"]["plugindata"]['env_vol']['loop'] = dmf_instdata['env_volume']['looppos']
            elif insttype == 'fm':
                cvpj_inst["instdata"]["plugin"] = 'opn2'
                cvpj_inst["instdata"]["plugindata"] = dmf_instdata['fmdata']
            else: 
                cvpj_inst["instdata"]["plugin"] = 'none'
            
            cvpj_l_instruments[cvpj_instid] = cvpj_inst
            cvpj_l_instrumentsorder.append(cvpj_instid)

        #dmf_insts

        cvpj_l['use_fxrack'] = False
        cvpj_l['title'] = dmf_song_name
        cvpj_l['author'] = dmf_song_author
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = 140
        return json.dumps(cvpj_l)

