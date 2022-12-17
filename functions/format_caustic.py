
from functions import data_bytes
import struct

global caustic_instnames
caustic_instnames = {}
caustic_instnames['NULL'] = 'None'
caustic_instnames['SSYN'] = 'SubSynth'
caustic_instnames['PCMS'] = 'PCMSynth'
caustic_instnames['BLNE'] = 'BassLine'
caustic_instnames['BBOX'] = 'BeatBox'
caustic_instnames['PADS'] = 'PadSynth'
caustic_instnames['8SYN'] = '8BitSynth'
caustic_instnames['MDLR'] = 'Modular'
caustic_instnames['ORGN'] = 'Organ'
caustic_instnames['VCDR'] = 'Vocoder'
caustic_instnames['FMSN'] = 'FMSynth'
caustic_instnames['KSSN'] = 'KSSynth'
caustic_instnames['SAWS'] = 'SawSynth'

patletters = ['A','B','C','D']

global EFFX_num

global MSTR_num
    
EFFX_num = 0
MSTR_num = 0

# --------------------------------------------- Patterns ---------------------------------------------

def parse_note(SPAT_str, numnotes):
    notelist = []
    for _ in range(numnotes): 
        notedata = struct.unpack("IIffffIIIfffff", SPAT_str.read(56))
        #print(notedata)
        notelist.append(notedata)
    return notelist

def deconstruct_SPAT(bio_in):
    global patletters

    print('[format-caustic] SPAT')
    if bio_in.read(4) != b'SPAT':
        print('data is not SPAT')
        exit()

    l_patterns = {}

    for patletter in range(4): 
        for patnum in range(16): 
            l_patterns[patletters[patletter]+str(patnum+1)] = {}

    SPAT_size = int.from_bytes(bio_in.read(4), "little")
    SPAT_data = bio_in.read(SPAT_size)
    SPAT_str = data_bytes.bytearray2BytesIO(SPAT_data)

    # --------------- measures ---------------
    for patletter in range(4): 
        for patnum in range(16): 
            l_patterns[patletters[patletter]+str(patnum+1)]['measures'] = int.from_bytes(SPAT_str.read(4), "little")

    # --------------- numnote ---------------
    for patletter in range(4): 
        for patnum in range(16): 
            l_patterns[patletters[patletter]+str(patnum+1)]['numnote'] = int.from_bytes(SPAT_str.read(4), "little")

    # --------------- notes data ---------------
    for patletter in range(4): 
        for patnum in range(16): 
            numnote = l_patterns[patletters[patletter]+str(patnum+1)]['numnote']
            l_patterns[patletters[patletter]+str(patnum+1)]['notes'] = parse_note(SPAT_str, numnote)

    return l_patterns


def deconstruct_SEQN(bi_rack, Caustic_Main):
    SEQN_size = int.from_bytes(bi_rack.read(4), "little")
    SEQN_data = bi_rack.read(SEQN_size)
    SEQN_str = data_bytes.bytearray2BytesIO(SEQN_data)
    SEQN_header = struct.unpack("II", SEQN_str.read(8))
    placementcount = SEQN_header[1]
    pln = []
    for _ in range(placementcount):
        plndata = struct.unpack("IIffIfIfffffff", SEQN_str.read(56))
        pln.append(plndata)
    Caustic_Main['SEQN'] = pln

# --------------------------------------------- Controls ---------------------------------------------

def deconstruct_CCOL(bio_in):
    print('[format-caustic] CCOL |', end=' ')
    if bio_in.read(4) != b'CCOL':
        print('data is not CCOL')
        exit()
    CCOL_size = int.from_bytes(bio_in.read(4), "little")
    CCOL_data = bio_in.read(CCOL_size)
    CCOL_chunks = data_bytes.riff_read(CCOL_data, 0)
    CCOL_l_out = {}
    for part in CCOL_chunks:
        con_id = int.from_bytes(part[1][:4], "little")
        con_value = struct.unpack('<f', part[1][4:])[0]
        CCOL_l_out[con_id] = con_value
    print(str(len(CCOL_l_out))+' Controls')
    return CCOL_l_out

# --------------------------------------------- FX ---------------------------------------------

def deconstruct_fx(EFFX_str, l_fxparams):
    fxtype = int.from_bytes(EFFX_str.read(4), "little")
    params = l_fxparams
    if fxtype == 0: 
        params['type'] = 'Delay'
        params['controls'] = deconstruct_CCOL(EFFX_str)
        EFFX_str.read(4)
    if fxtype == 1: 
        params['type'] = 'Reverb'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 2: 
        params['type'] = 'Distortion'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 3: 
        params['type'] = 'Compresser'
        params['controls'] = deconstruct_CCOL(EFFX_str)
        EFFX_str.read(4)
    if fxtype == 4: 
        params['type'] = 'Bitcrush'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 5: 
        params['type'] = 'Flanger'
        params['controls'] = deconstruct_CCOL(EFFX_str)
        EFFX_str.read(4)
    if fxtype == 6: 
        params['type'] = 'Phaser'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 7: 
        params['type'] = 'Chorus'
        params['controls'] = deconstruct_CCOL(EFFX_str)
        EFFX_str.read(4)
    if fxtype == 8: 
        params['type'] = 'AutoWah'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 9: 
        params['type'] = 'Param EQ'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 10: 
        params['type'] = 'Limiter'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 11: 
        params['type'] = 'VInylSim'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 12: 
        params['type'] = 'Comb'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 14: 
        params['type'] = 'Cab Sim'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 16: 
        params['type'] = 'StaticFlanger'
        params['controls'] = deconstruct_CCOL(EFFX_str)
        EFFX_str.read(4)
    if fxtype == 17: 
        params['type'] = 'Filter'
        params['controls'] = deconstruct_CCOL(EFFX_str)
        EFFX_str.read(4)
    if fxtype == 18: 
        params['type'] = 'Octaver'
        params['controls'] = deconstruct_CCOL(EFFX_str)
        EFFX_str.read(4)
    if fxtype == 19: 
        params['type'] = 'Vibrato'
        params['controls'] = deconstruct_CCOL(EFFX_str)
        EFFX_str.read(4)
    if fxtype == 20: 
        params['type'] = 'Tremolo'
        params['controls'] = deconstruct_CCOL(EFFX_str)
    if fxtype == 21: 
        params['type'] = 'AutoPan'
        params['controls'] = deconstruct_CCOL(EFFX_str)

def deconstruct_EFFX(bi_rack, Caustic_Main):
    global EFFX_num
    EFFX_size = int.from_bytes(bi_rack.read(4), "little")
    EFFX_data = bi_rack.read(EFFX_size)
    EFFX_str = data_bytes.bytearray2BytesIO(EFFX_data)

    for fxtrk in range(7): 
        Caustic_Main['EFFX'][(fxtrk+1)+(EFFX_num*7)] = {}
        for fxslot in range(2): 
            Caustic_Main['EFFX'][(fxtrk+1)+(EFFX_num*7)][fxslot+1] = {}

    for fxtrk in range(7): 
        for fxslot in range(2): 
            print('[format-caustic] EFFX | Track', (fxtrk+1)+(EFFX_num*7), 'Slot', fxslot+1)
            l_fxparams = Caustic_Main['EFFX'][(fxtrk+1)+(EFFX_num*7)][(fxslot+1)]
            deconstruct_fx(EFFX_str, l_fxparams)

    if EFFX_num == 0: bi_rack.read(4)
    Caustic_Main['EFFX'+str(EFFX_num)] = EFFX_data
    EFFX_num += 1

# --------------------------------------------- Mixer ---------------------------------------------

def deconstruct_MIXR(bi_rack, Caustic_Main):
    global MSTR_num
    MIXR_size = int.from_bytes(bi_rack.read(4), "little")
    MIXR_data = bi_rack.read(MIXR_size)
    MIXR_str = data_bytes.bytearray2BytesIO(MIXR_data)
    MIXR_str.read(4)
    Caustic_Main['MIXR'] = deconstruct_CCOL(MIXR_str)
    if MSTR_num == 0: bi_rack.read(4)
    MSTR_num += 1

def deconstruct_MSTR(bi_rack, Caustic_Main):
    MSTR_size = int.from_bytes(bi_rack.read(4), "little")
    MSTR_data = bi_rack.read(MSTR_size)
    #MSTR_str = data_bytes.bytearray2BytesIO(MSTR_data)
    #MSTR_str.read(8)
    #Caustic_Main['MSTR'] = deconstruct_CCOL(MSTR_str)

# --------------------------------------------- Inst ---------------------------------------------

def deconstruct_machine(datain, l_machine):
    #print(datain[:100])
    data_str = data_bytes.bytearray2BytesIO(datain)
    # -------------------------------- SubSynth --------------------------------
    if l_machine['id'] == 'SSYN':
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        l_machine['unknown4'] = int.from_bytes(data_str.read(4), "little")
        l_machine['customwaveform1'] = data_str.read(1320)
        l_machine['customwaveform2'] = data_str.read(1320)
        data_str.read(12)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    # -------------------------------- BassLine --------------------------------
    elif l_machine['id'] == 'BLNE':
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
        data_str.read(4)
        l_machine['customwaveform'] = data_str.read(1320)
    # -------------------------------- PadSynth --------------------------------
    elif l_machine['id'] == 'PADS':
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['unknown1'] = int.from_bytes(data_str.read(4), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(4), "little")
        l_machine['harm1'] = struct.unpack("ffffffffffffffffffffffff", data_str.read(96))
        l_machine['harm1vol'] = struct.unpack("f", data_str.read(4))[0]
        l_machine['harm2'] = struct.unpack("ffffffffffffffffffffffff", data_str.read(96))
        l_machine['harm2vol'] = struct.unpack("f", data_str.read(4))[0]
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    # -------------------------------- Organ --------------------------------
    elif l_machine['id'] == 'ORGN':
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['unknown1'] = int.from_bytes(data_str.read(4), "little")
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    # -------------------------------- FMSynth --------------------------------
    elif l_machine['id'] == 'FMSN':
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['unknown4'] = int.from_bytes(data_str.read(4), "little")
        l_machine['unknown5'] = int.from_bytes(data_str.read(4), "little")
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    # -------------------------------- KSSynth --------------------------------
    elif l_machine['id'] == 'KSSN':
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    # -------------------------------- 8BitSynth --------------------------------
    elif l_machine['id'] == '8SYN':
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['bitcode1'] = data_str.read(128).split(b'\x00')[0].decode('ascii')
        l_machine['bitcode2'] = data_str.read(128).split(b'\x00')[0].decode('ascii')
        l_machine['unknown4'] = int.from_bytes(data_str.read(4), "little")
        l_machine['unknown5'] = int.from_bytes(data_str.read(4), "little")
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    # -------------------------------- BeatBox --------------------------------
    elif l_machine['id'] == 'BBOX':
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
        l_machine['samples'] = []
        data_str.read(256)
        data_str.read(8)
        for _ in range(8):
            sampledata = {}
            sample_name = data_str.read(32).split(b'\x00')[0].decode('ascii')
            sample_len = int.from_bytes(data_str.read(4), "little")
            sample_hz = int.from_bytes(data_str.read(4), "little")
            sample_chan = int.from_bytes(data_str.read(4), "little")
            print('[format-caustic] BBOX | len:'+str(sample_len)+', hz:'+str(sample_hz)+', ch:'+str(sample_chan))
            sampledata['data'] = data_str.read((sample_len*2)*sample_chan)
            sampledata['name'] = sample_name
            sampledata['hz'] = sample_hz
            sampledata['len'] = sample_len
            sampledata['chan'] = sample_chan
            l_machine['samples'].append(sampledata)
    # -------------------------------- Vocoder --------------------------------
    elif l_machine['id'] == 'VCDR':
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['currentnumber'] = int.from_bytes(data_str.read(4), "little")
        l_machine['samples'] = []
        data_str.read(28)
        data_str.read(8)

        for _ in range(6):
            sampledata = {}
            sample_name = data_str.read(256).split(b'\x00')[0].decode('ascii')
            data_str.read(4)
            sample_len = int.from_bytes(data_str.read(4), "little")
            sample_hz = int.from_bytes(data_str.read(4), "little")
            sample_data = data_str.read(sample_len*2)
            print('[format-caustic] VCDR | len:'+str(sample_len)+', hz:'+str(sample_hz))
            sampledata['name'] = sample_name
            sampledata['len'] = sample_len
            sampledata['hz'] = sample_hz
            sampledata['data'] = sample_data
            l_machine['samples'].append(sampledata)

        l_machine['unknown4'] = int.from_bytes(data_str.read(4), "little")
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    # -------------------------------- Modular --------------------------------
    elif l_machine['id'] == 'MDLR': pass
    # -------------------------------- PCMSynth --------------------------------
    elif l_machine['id'] == 'PCMS': 
        l_machine['unknown1'] = int.from_bytes(data_str.read(2), "little")
        l_machine['unknown2'] = int.from_bytes(data_str.read(1), "little")
        l_machine['unknown3'] = int.from_bytes(data_str.read(1), "little")
        l_machine['controls'] = deconstruct_CCOL(data_str)
        l_machine['presetname'] = data_str.read(32).split(b'\x00')[0].decode('ascii')
        presetpath_size = int.from_bytes(data_str.read(4), "little")
        l_machine['presetpath'] = data_str.read(presetpath_size).split(b'\x00')[0].decode('ascii')
        data_str.read(4)
        numsamples = int.from_bytes(data_str.read(4), "little")
        #print(numsamples)
        regions = []
        for _ in range(numsamples):
            region = {}
            region['volume'] = struct.unpack("f", data_str.read(4))[0]
            data_str.read(4)
            region['pan'] = struct.unpack("f", data_str.read(4))[0]
            region['key_root'] = int.from_bytes(data_str.read(4), "little")
            region['key_lo'] = int.from_bytes(data_str.read(4), "little")
            region['key_hi'] = int.from_bytes(data_str.read(4), "little")
            region['mode'] = int.from_bytes(data_str.read(4), "little")
            region['start'] = int.from_bytes(data_str.read(4), "little")
            region['end'] = int.from_bytes(data_str.read(4), "little")
            region['path'] = data_str.read(256).split(b'\x00')[0].decode('ascii')
            data_str.read(4)
            sample_len = int.from_bytes(data_str.read(4), "little")
            region['samp_hz'] = int.from_bytes(data_str.read(4), "little")
            data_str.read(4)
            sample_chan = int.from_bytes(data_str.read(4), "little")
            region['samp_data'] = data_str.read((sample_len*2)*sample_chan)
            region['samp_len'] = sample_len
            region['samp_ch'] = sample_chan
            regions.append(region)
        l_machine['regions'] = regions
        data_str.read(9)
        l_machine['patterns'] = deconstruct_SPAT(data_str)
    del l_machine['data']

def deconstruct_OUTP(bi_rack, Caustic_Main):
    global caustic_machdata
    OUTP_size = int.from_bytes(bi_rack.read(4), "little")
    OUTP_data = bi_rack.read(OUTP_size)

    caustic_machines = []

    for _ in range(14):
        machtype = bi_rack.read(4).decode("utf-8")
        bi_rack.read(1)
        caustic_machines.append({'id': machtype})

    te_num = 0
    for machpart in caustic_machines:
        print('[format-caustic] OUTP |', end=' ')
        print(caustic_instnames[machpart['id']], end='')
        if machpart['id'] != 'NULL':
            bi_rack.read(10)
            te_name = bi_rack.read(4)
            te_size = int.from_bytes(bi_rack.read(4), "little")
            print(', '+str(te_size))
            te_data = bi_rack.read(te_size)
            caustic_machines[te_num]['data'] = te_data
            deconstruct_machine(te_data, caustic_machines[te_num])
            #print(te_data[:100])
        else: print()
        te_num += 1
    Caustic_Main['Machines'] = caustic_machines

# --------------------------------------------- Main ---------------------------------------------

def deconstruct_main(filepath):
    fileobject = open(filepath, 'rb')
    headername = fileobject.read(4)
    ro_rack = data_bytes.riff_read(fileobject, 0)

    for rod_rack in ro_rack:
        if rod_rack[0] == b'RACK':
            rackdata = rod_rack[1]
            bi_rack = data_bytes.bytearray2BytesIO(rackdata)

    bi_rack.seek(0,2)
    racksize = bi_rack.tell()
    bi_rack.seek(0)

    header = bi_rack.read(264)

    Caustic_Main = {}
    Caustic_Main['EFFX'] = {}

    while racksize > bi_rack.tell():
        chunk_datatype = bi_rack.read(4)
        print('[format-caustic] main | chunk:', chunk_datatype)
        if chunk_datatype == b'OUTP': deconstruct_OUTP(bi_rack, Caustic_Main)
        elif chunk_datatype == b'EFFX': deconstruct_EFFX(bi_rack, Caustic_Main)
        elif chunk_datatype == b'MIXR': deconstruct_MIXR(bi_rack, Caustic_Main)
        elif chunk_datatype == b'MSTR': deconstruct_MSTR(bi_rack, Caustic_Main)
        elif chunk_datatype == b'SEQN': deconstruct_SEQN(bi_rack, Caustic_Main)
        else: break

    return Caustic_Main