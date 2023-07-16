# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import song_tracker
from functions import tracks
from functions import plugins
from functions import song
import plugin_input
import zlib
import struct
import json

chiptypecolors = {}
chiptypecolors['opn2'] = [0.20, 0.80, 1.00]
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
chipname['opn2'] = 'FM 4op'
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

def fxget(fxtype, fxparam, output_param, output_extra): 
    if fxtype == 0 and fxparam != 0:
        arpeggio_first = fxparam >> 4
        arpeggio_second = fxparam & 0x0F
        output_param['arpeggio'] = [arpeggio_first, arpeggio_second]

    if fxtype == 1: output_param['slide_up'] = fxparam

    if fxtype == 2: output_param['slide_down'] = fxparam

    if fxtype == 3: output_param['slide_to_note'] = fxparam

    if fxtype == 4: 
        vibrato_params = {}
        vibrato_params['speed'], vibrato_params['depth'] = data_bytes.splitbyte(fxparam)
        output_param['vibrato'] = vibrato_params

    if fxtype == 5:
        pos, neg = data_bytes.splitbyte(fxparam)
        output_param['vol_slide'] = (neg*-1) + pos
        output_param['slide_to_note'] = (neg*-1) + pos

    if fxtype == 6:
        pos, neg = data_bytes.splitbyte(fxparam)
        output_param['vibrato'] = {'speed': 0, 'depth': 0}
        output_param['vol_slide'] = (neg*-1) + pos

    if fxtype == 7:
        tremolo_params = {}
        tremolo_params['speed'], tremolo_params['depth'] = data_bytes.splitbyte(fxparam)
        output_param['tremolo'] = tremolo_params

    if fxtype == 8: output_param['pan'] = (fxparam-128)/128

    if fxtype == 9: output_param['sample_offset'] = fxparam*256

    if fxtype == 10:
        pos, neg = data_bytes.splitbyte(fxparam)
        output_param['vol_slide'] = (neg*-1) + pos

    if fxtype == 11: output_extra['pattern_jump'] = fxparam

    if fxtype == 12: output_param['vol'] = fxparam/64

    if fxtype == 13: output_extra['break_to_row'] = fxparam

    if fxtype == 15:
        if fxparam < 32: output_extra['speed'] = fxparam
        else: output_extra['tempo'] = fxparam

def dmfenv(bio_dmf): 
    ENVELOPE_SIZE = bio_dmf.read(1)[0]
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
    def getdawcapabilities(self): 
        return {
        'track_lanes': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        output = False
        bytestream = open(input_file, 'rb')
        filedata = bytestream.read()
        try:
            zlibdata = zlib.decompress(filedata)
            dmfdata = data_bytes.to_bytesio(zlibdata)
            dmf_header = dmfdata.read(16)
            if dmf_header == b'.DelekDefleMask.': output = True
            else: output = False
        except: output = False
        return output
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'rb')
        bio_dmf = data_bytes.to_bytesio(zlib.decompress(bytestream.read()))

        dmf_header = bio_dmf.read(16)
        if dmf_header != b'.DelekDefleMask.':
            print('File is not DefleMask.')
            exit()

        cvpj_l = {}

        # FORMAT FLAGS
        dmf_version = bio_dmf.read(1)[0]

        if dmf_version != 24:
            print('[error] only version 24 is supported')
            exit()

        dmf_system = bio_dmf.read(1)[0]

        # SYSTEM SET
        if dmf_system == int("02",16): #GENESIS
            t_chantype = ['opn2','opn2','opn2','opn2','opn2','opn2','square','square','square','noise']
            t_channames = ['FM 1','FM 2','FM 3','FM 4','FM 5','FM 6','Square 1','Square 2','Square 3','Noise']
        if dmf_system == int("42",16): #SYSTEM_GENESIS (mode EXT. CH3) 
            t_chantype = ['opn2','opn2','opn2-op','opn2-op','opn2-op','opn2-op','opn2','opn2','opn2','square','square','square','noise']
            t_channames = ['FM 1','FM 2','FM 3 OP 1','FM 3 OP 2','FM 3 OP 3','FM 3 OP 4','FM 4','FM 5','FM 6','Square 1','Square 2','Square 3','Noise']
        if dmf_system == int("03",16): #SMS
            t_chantype = ['square','square','square','noise']
            t_channames = ['Square 1','Square 2','Square 3','Noise']
        if dmf_system == int("04",16): #GAMEBOY
            t_chantype = ['gameboy_pulse','gameboy_pulse','gameboy_wavetable','gameboy_noise']
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
            t_chantype = ['opn2','opn2','opn2','opn2','opn2','opn2','opn2','opn2','sample','sample','sample','sample','sample']
            t_channames = ['FM 1','FM 2','FM 3','FM 4','FM 5','FM 6','FM 7','FM 8','Channel 1','Channel 2','Channel 3','Channel 4','Channel 5']
        if dmf_system == int("09",16): #NEOGEO
            t_chantype = ['opn2','opn2','opn2','opn2','psg','psg','psg','adpcma','adpcma','adpcma','adpcma','adpcma','adpcma']
            t_channames = ['FM 1','FM 2','FM 3','FM 4','PSG 1','PSG 2','PSG 3','ADPCM-A 1','ADPCM-A 2','ADPCM-A 3','ADPCM-A 4','ADPCM-A 5','ADPCM-A 6']
        if dmf_system == int("49",16): #NEOGEO (mode EXT. CH2)
            t_chantype = ['opn2','opn2','opn2_op','opn2_op','opn2_op','opn2_op','opn2','psg','psg','psg','adpcma','adpcma','adpcma','adpcma','adpcma','adpcma']
            t_channames = ['FM 1','FM 2 OP 1','FM 2 OP 2','FM 2 OP 3','FM 2 OP 4','FM 3','FM 4','PSG 1','PSG 2','PSG 3','ADPCM-A 1','ADPCM-A 2','ADPCM-A 3','ADPCM-A 4','ADPCM-A 5','ADPCM-A 6']

        dmf_SYSTEM_TOTAL_CHANNELS = len(t_chantype)

        # VISUAL INFORMATION
        dmf_song_name = data_bytes.readstring_lenbyte(bio_dmf, 1, "little", None)
        dmf_song_author = data_bytes.readstring_lenbyte(bio_dmf, 1, "little", None)
        dmf_highlight_a_pat = bio_dmf.read(1)[0]
        dmf_highlight_b_pat = bio_dmf.read(1)[0]

        # MODULE INFORMATION
        dmf_TimeBase = bio_dmf.read(1)[0]
        dmf_TickTime1 = bio_dmf.read(1)[0]
        dmf_TickTime2 = bio_dmf.read(1)[0]
        dmf_FramesMode = bio_dmf.read(1)[0]
        dmf_UsingCustomHZ = bio_dmf.read(1)[0]
        dmf_CustomHZ1 = bio_dmf.read(1)[0]
        dmf_CustomHZ2 = bio_dmf.read(1)[0]
        dmf_CustomHZ3 = bio_dmf.read(1)[0]
        dmf_TOTAL_ROWS_PER_PATTERN = int.from_bytes(bio_dmf.read(4), "little")
        dmf_TOTAL_ROWS_IN_PATTERN_MATRIX = bio_dmf.read(1)[0]

        # PATTERN MATRIX VALUES
        t_ch_pat_orders = []
        for _ in range(dmf_SYSTEM_TOTAL_CHANNELS):
            t_ch_pat_orders.append(struct.unpack('b'*dmf_TOTAL_ROWS_IN_PATTERN_MATRIX, bio_dmf.read(dmf_TOTAL_ROWS_IN_PATTERN_MATRIX)))

        # INSTRUMENTS DATA
        dmf_TOTAL_INSTRUMENTS = bio_dmf.read(1)[0]

        dmf_insts = []
        dmf_instnames = []

        for instnum in range(dmf_TOTAL_INSTRUMENTS):
            dmf_inst = {}
            dmfi_name = data_bytes.readstring_lenbyte(bio_dmf, 1, "little", None)
            dmfi_mode = bio_dmf.read(1)[0]
            dmf_instnames.append(dmfi_name)
            if dmfi_mode == 1:
                dmf_inst['fm'] = True
                fmdata = {}
                fmdata['algorithm'] = bio_dmf.read(1)[0]
                fmdata['feedback'] = bio_dmf.read(1)[0]
                fmdata['fms'] = bio_dmf.read(1)[0] #(FMS on YM2612, PMS on YM2151)
                fmdata['ams'] = bio_dmf.read(1)[0] #(AMS on YM2612, AMS on YM2151)
                fmdata['lfo_enable'] = 0
                fmdata['lfo_frequency'] = 0
                for opnum in [0,2,1,3]:
                    optxt = 'op'+str(opnum+1)+'_'
                    fmdata[optxt+'am'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'env_attack'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'env_decay'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'freqmul'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'env_release'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'env_sustain'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'level'] = (bio_dmf.read(1)[0]*-1)+127
                    fmdata[optxt+'detune2'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'ratescale'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'detune'] = bio_dmf.read(1)[0]
                    fmdata[optxt+'env_decay2'] = bio_dmf.read(1)[0]
                    ssgmode = bio_dmf.read(1)[0]
                    fmdata[optxt+'ssg_enable'] = int(bool(ssgmode & 0b0001000))
                    fmdata[optxt+'ssg_mode'] = ssgmode & 0b00001111
                dmf_inst['fmdata'] = fmdata
            else:
                dmf_inst['fm'] = False
                if dmf_system != int("04",16): dmf_inst['env_volume'] = dmfenv(bio_dmf)
                dmf_inst['env_arpeggio'] = dmfenv(bio_dmf)
                dmf_inst['arpeggio_mode'] = bio_dmf.read(1)[0]
                dmf_inst['env_duty'] = dmfenv(bio_dmf)
                dmf_inst['env_wavetable'] = dmfenv(bio_dmf)
                if dmf_system == int("07",16) or dmf_system == int("47",16):
                    c64data = {}
                    c64data['wave_triangle'] = bio_dmf.read(1)[0]
                    c64data['wave_saw'] = bio_dmf.read(1)[0]
                    c64data['wave_pulse'] = bio_dmf.read(1)[0]
                    c64data['wave_noise'] = bio_dmf.read(1)[0]
                    c64data['attack'] = bio_dmf.read(1)[0]
                    c64data['decay'] = bio_dmf.read(1)[0]
                    c64data['sustain'] = bio_dmf.read(1)[0]
                    c64data['release'] = bio_dmf.read(1)[0]
                    c64data['pulse width'] = bio_dmf.read(1)[0]
                    c64data['ringmod'] = bio_dmf.read(1)[0]
                    c64data['syncmod'] = bio_dmf.read(1)[0]
                    c64data['to_filter'] = bio_dmf.read(1)[0]
                    c64data['volume_macro_to_filter_cutoff'] = bio_dmf.read(1)[0]
                    c64data['use_filter_values_from_instrument'] = bio_dmf.read(1)[0]
                    c64data['filter_resonance'] = bio_dmf.read(1)[0]
                    c64data['filter_cutoff'] = bio_dmf.read(1)[0]
                    c64data['filter_highpass'] = bio_dmf.read(1)[0]
                    c64data['filter_lowpass'] = bio_dmf.read(1)[0]
                    c64data['filter_CH2off'] = bio_dmf.read(1)[0]
                    dmf_inst['c64data'] = c64data
                if dmf_system == int("04",16):
                    gameboydata = {}
                    gameboydata['env_volume'] = bio_dmf.read(1)[0]
                    gameboydata['env_direction'] = bio_dmf.read(1)[0]
                    gameboydata['env_length'] = bio_dmf.read(1)[0]
                    gameboydata['sound_length'] = bio_dmf.read(1)[0]
                    dmf_inst['gameboydata'] = gameboydata
            dmf_insts.append(dmf_inst)

        #for dmf_inst in dmf_insts:
        #    print(dmf_inst)

        # WAVETABLES DATA
        dmf_wavetables = []

        dmf_TOTAL_WAVETABLES = bio_dmf.read(1)[0]
        for _ in range(dmf_TOTAL_WAVETABLES):
            dmf_WAVETABLE_SIZE = int.from_bytes(bio_dmf.read(4), "little")
            wavetable = struct.unpack('I'*dmf_WAVETABLE_SIZE , bio_dmf.read(dmf_WAVETABLE_SIZE*4))
            dmf_wavetables.append(wavetable)

        # PATTERNS DATA

        dmf_patterns = {}

        t_orders = {}

        for channum in range(dmf_SYSTEM_TOTAL_CHANNELS):
            dmf_patterns[channum] = {}
            s_chantype = t_chantype[channum]

            t_orders[channum] = t_ch_pat_orders[channum]
            dmf_pat_channel = []
            dmf_CHANNEL_EFFECTS_COLUMNS_COUNT = bio_dmf.read(1)[0]
            for patnum in t_ch_pat_orders[channum]:
                table_rows = []
                for rownum in range(dmf_TOTAL_ROWS_PER_PATTERN):
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
                        if s_chantype != 'opn2': output_param['vol'] = r_vol/16
                        else: output_param['vol'] = r_vol/127

                    for r_fxp in r_fx:
                        fxget(r_fxp[0], r_fxp[1], output_param, output_extra)

                    if r_note == 0 and r_oct == 0: output_note = None
                    elif r_note == 100: output_note = 'Off'
                    else: output_note = (r_note + r_oct*12)-60

                    if output_note != None and output_note != 'Off':
                        if s_chantype == 'square':  output_note += 36
                        if s_chantype == 'opn2': output_note += 12

                    if r_inst != -1 and output_note != None: output_inst = r_inst
                    if rownum == 0: table_rows.append([{'firstrow': 1},[output_note, output_inst, output_param, output_extra]])
                    else: table_rows.append([{},[output_note, output_inst, output_param, output_extra]])
                dmf_patterns[channum][patnum] = table_rows

        mt_pat = dmf_patterns
        mt_ord = t_orders
        mt_ch_insttype = t_chantype
        mt_ch_names = t_channames
        mt_type_colors = chiptypecolors

        len_table = song_tracker.multi_get_len_table(dmf_TOTAL_ROWS_PER_PATTERN, mt_pat, mt_ord, mt_ch_insttype)

        song_tracker.multi_convert(cvpj_l, dmf_TOTAL_ROWS_PER_PATTERN, mt_pat, mt_ord, mt_ch_insttype, len_table)

        total_used_instruments = song_tracker.get_multi_used_instruments()
        for total_used_instrument in total_used_instruments:
            pluginid = plugins.get_id()

            insttype = total_used_instrument[0]
            dmf_instid = total_used_instrument[1]
            dmf_instdata = dmf_insts[int(dmf_instid)]

            cvpj_instid = insttype+'_'+dmf_instid
            cvpj_inst = {}
            #print(dmf_instnames)
            cvpj_instname = dmf_instnames[int(dmf_instid)]+' ('+chipname[insttype]+')'
            cvpj_instcolor = None
            if insttype in chiptypecolors: cvpj_instcolor = chiptypecolors[insttype]
            cvpj_instdata = {}
            cvpj_instdata["plugindata"] = {}
            if insttype == 'square' or insttype == 'noise':
                plugins.add_plug(cvpj_l, pluginid, 'retro', insttype)
                if 'env_volume' in dmf_instdata:
                    loopval = None
                    if dmf_instdata['env_volume']['looppos'] != -1: loopval = dmf_instdata['env_volume']['looppos']
                    add_env_blocks(cvpj_l, pluginid, 'vol', dmf_instdata['env_volume']['values'], loopval, None)

            elif insttype == 'opn2':
                plugins.add_plug(cvpj_l, pluginid, 'fm', 'opn2')
                for fmdataval in dmf_instdata['fmdata']:
                    plugins.add_plug_param(cvpj_l, pluginid, fmdataval, 
                        dmf_instdata['fmdata'][fmdataval], 'int', fmdataval)
            else: 
                cvpj_instdata["plugin"] = 'none'
            
            tracks.m_create_inst(cvpj_l, cvpj_instid, {'pluginid': pluginid})
            tracks.m_basicdata_inst(cvpj_l, cvpj_instid, cvpj_instname, cvpj_instcolor, 1.0, 0.0)

        #dmf_insts

        song.add_info(cvpj_l, 'title', dmf_song_name)
        song.add_info(cvpj_l, 'author', dmf_song_author)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_lanefit'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        
        cvpj_l['bpm'] = 140
        return json.dumps(cvpj_l)

