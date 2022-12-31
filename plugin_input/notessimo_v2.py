# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import plugin_input
import json
import zlib
import struct

keytable = [0,2,4,5,7,9,11,12]

notess_instruments =  {}
notess_instruments[12]  = [[0.81, 0.59, 0.35], 'Acoustic Guitar']
notess_instruments[82]  = [[0.87, 0.66, 0.07], 'Damant Spectrum Muted']
notess_instruments[79]  = [[0.51, 0.80, 0.76], 'Fender Strat Guitar']
notess_instruments[78]  = [[0.33, 0.42, 0.68], 'Strat Guitar']
notess_instruments[47]  = [[0.05, 0.05, 0.05], 'Metal Guitar']
notess_instruments[64]  = [[0.71, 0.38, 0.13], 'Guitar Electric']
notess_instruments[77]  = [[0.23, 0.21, 0.21], 'Clean Electric Guitar']
notess_instruments[81]  = [[0.72, 0.09, 0.15], 'Damant Spectrum Harm']
notess_instruments[49]  = [[0.64, 0.24, 0.04], 'Bass Guitar']
notess_instruments[1]   = [[0.64, 0.24, 0.04], 'Bass']
notess_instruments[39]  = [[0.70, 0.29, 0.24], 'Bass #2']
notess_instruments[52]  = [[0.70, 0.36, 0.12], 'Bass #3']
notess_instruments[59]  = [[0.49, 0.11, 0.13], 'Bass #4']
notess_instruments[0]   = [[0.18, 0.20, 0.21], 'Synth Bass']
notess_instruments[21]  = [[0.18, 0.20, 0.21], 'Synth Bass #2']
notess_instruments[135] = [[0.43, 0.13, 0.04], 'Sitar']
notess_instruments[136] = [[0.91, 0.38, 0.16], 'Pizzicato']
notess_instruments[9]   = [[0.89, 0.36, 0.16], 'Strings']
notess_instruments[36]  = [[0.91, 0.38, 0.16], 'Strings #2']
notess_instruments[37]  = [[0.71, 0.24, 0.09], 'Strings #3']
notess_instruments[31]  = [[0.40, 0.53, 0.42], 'Synth Strings']
notess_instruments[80]  = [[0.33, 0.33, 0.33], 'Fret Noise']

notess_instruments[28]  = [[0.00, 0.00, 0.00], 'Grand Piano']
notess_instruments[114] = [[0.18, 0.18, 0.16], 'Rhodes']
notess_instruments[121] = [[0.37, 0.18, 0.14], 'Orchestra Hit']
notess_instruments[13]  = [[0.00, 0.00, 0.00], 'Low Piano']
notess_instruments[115] = [[0.68, 0.68, 0.68], 'Rhodes #2']
notess_instruments[11]  = [[0.56, 0.67, 0.25], 'Synth']
notess_instruments[116] = [[0.79, 0.04, 0.09], 'Electric Piano']
notess_instruments[117] = [[0.67, 0.49, 0.39], 'Rock Organ']
notess_instruments[17]  = [[0.11, 0.11, 0.11], 'Synth #2']
notess_instruments[111] = [[0.76, 0.76, 0.76], 'Clavinet']
notess_instruments[118] = [[0.37, 0.18, 0.14], 'Church Organ']
notess_instruments[23]  = [[0.33, 0.34, 0.39], 'Synthesizer']
notess_instruments[112] = [[0.56, 0.37, 0.31], 'Electric Clavinet']
notess_instruments[119] = [[0.34, 0.31, 0.35], 'Percussive Organ']
notess_instruments[34]  = [[0.33, 0.34, 0.39], 'Synthesizer #2']
notess_instruments[113] = [[0.48, 0.31, 0.31], 'Harpsichord']
notess_instruments[120] = [[0.11, 0.11, 0.11], 'Organ']
notess_instruments[50]  = [[0.33, 0.34, 0.39], 'Synthesizer #3']
notess_instruments[110] = [[0.45, 0.17, 0.20], 'Accordian']
notess_instruments[22]  = [[0.33, 0.34, 0.39], 'Triangle Wave']

notess_instruments[133] = [[0.07, 0.18, 0.26], 'Techno Bass']

notess_instruments[2]   = [[0.06, 0.07, 0.08], 'Bass Drum']
notess_instruments[18]  = [[0.11, 0.39, 0.29], 'Bass Drum #2']
notess_instruments[24]  = [[0.06, 0.07, 0.08], 'Bass Drum #3']
notess_instruments[43]  = [[0.11, 0.39, 0.29], 'Bass Drum #4']
notess_instruments[60]  = [[0.06, 0.07, 0.08], 'Bass Drum #5']
notess_instruments[15]  = [[0.85, 0.66, 0.37], 'Snare Drum']
notess_instruments[42]  = [[0.72, 0.73, 0.76], 'Snare Drum #2']
notess_instruments[44]  = [[0.88, 0.78, 0.67], 'Snare Drum #3']
notess_instruments[56]  = [[0.70, 0.60, 0.51], 'Snare Drum #4']
notess_instruments[67]  = [[0.72, 0.73, 0.76], 'Snare Drum #5']
notess_instruments[14]  = [[0.67, 0.61, 0.58], 'Tom Drums']
notess_instruments[27]  = [[0.45, 0.45, 0.43], 'High Tom']
notess_instruments[53]  = [[0.63, 0.45, 0.29], 'DX Tom']
notess_instruments[62]  = [[0.35, 0.36, 0.53], 'Dry Tom']
notess_instruments[57]  = [[0.39, 0.27, 0.16], 'Drum Reverb']
notess_instruments[3]   = [[0.82, 0.56, 0.25], 'Closed Hi Hat']
notess_instruments[26]  = [[0.82, 0.56, 0.25], 'Closed Hi Hat #2']
notess_instruments[61]  = [[0.82, 0.56, 0.25], 'Closed Hi Hat #3']
notess_instruments[5]   = [[0.80, 0.71, 0.41], 'Open Hi Hat']
notess_instruments[19]  = [[0.89, 0.72, 0.34], 'Open Hi Hat #2']
notess_instruments[30]  = [[0.80, 0.71, 0.41], 'Open Hi Hat #3']
notess_instruments[65]  = [[0.89, 0.72, 0.34], 'Open Hi Hat #4']
notess_instruments[25]  = [[0.86, 0.70, 0.44], 'Cymbal']
notess_instruments[45]  = [[0.72, 0.71, 0.74], 'Cymbal #2']
notess_instruments[46]  = [[0.10, 0.11, 0.14], 'Cymbal #3']
notess_instruments[66]  = [[0.86, 0.70, 0.44], 'Reverse Cymbal']
notess_instruments[40]  = [[0.88, 0.78, 0.67], 'Drum Loop']

notess_instruments[123] = [[0.73, 0.65, 0.54], 'Glockenspiel']
notess_instruments[126] = [[0.69, 0.58, 0.25], 'Xylophone']
notess_instruments[125] = [[0.60, 0.61, 0.63], 'Vibraphone']
notess_instruments[124] = [[0.89, 0.53, 0.02], 'Marimba']
notess_instruments[127] = [[0.69, 0.36, 0.11], 'Kalimba']
notess_instruments[4]   = [[0.76, 0.59, 0.43], 'Woodblock']
notess_instruments[129] = [[0.78, 0.75, 0.75], 'Clave']
notess_instruments[6]   = [[0.76, 0.76, 0.75], 'Tambourine']
notess_instruments[134] = [[0.74, 0.22, 0.19], 'Steel Drum']
notess_instruments[130] = [[0.71, 0.46, 0.24], 'Conga']
notess_instruments[131] = [[0.98, 0.42, 0.15], 'Conga #2']
notess_instruments[132] = [[0.83, 0.65, 0.43], 'Conga #3']
notess_instruments[7]   = [[0.82, 0.27, 0.11], 'Taiko Drum']
notess_instruments[10]  = [[0.84, 0.70, 0.54], 'Timpani']
notess_instruments[128] = [[0.27, 0.29, 0.27], 'Cowbell']
notess_instruments[122] = [[0.22, 0.20, 0.20], 'Tubular Bell']
notess_instruments[51]  = [[0.56, 0.59, 0.57], 'Blast']
notess_instruments[20]  = [[1.00, 0.82, 0.58], 'Hand Clap']

notess_instruments[8]   = [[0.77, 0.63, 0.39], 'Trumpet']
notess_instruments[100] = [[0.58, 0.51, 0.33], 'Trumpet #2']
notess_instruments[103] = [[0.74, 0.67, 0.47], 'Piccolo Trumpet']
notess_instruments[99]  = [[0.75, 0.65, 0.47], 'Trumpet Muted']
notess_instruments[101] = [[0.60, 0.56, 0.45], 'Trumpet Hit']
notess_instruments[102] = [[0.69, 0.64, 0.53], 'Trumpet Section']
notess_instruments[97]  = [[0.75, 0.65, 0.46], 'Trombone']
notess_instruments[95]  = [[0.78, 0.65, 0.32], 'Tuba']
notess_instruments[98]  = [[0.83, 0.68, 0.38], 'French Horn']
notess_instruments[58]  = [[0.74, 0.62, 0.49], 'Synth Brass']

notess_instruments[83]  = [[0.81, 0.73, 0.56], 'Soprano Sax']
notess_instruments[84]  = [[0.95, 0.88, 0.63], 'Alto Sax']
notess_instruments[87]  = [[0.67, 0.52, 0.31], 'Tenor Sax']
notess_instruments[88]  = [[0.73, 0.59, 0.37], 'Baritone Sax']
notess_instruments[85]  = [[0.85, 0.72, 0.36], 'Sax Hit']
notess_instruments[86]  = [[0.79, 0.79, 0.57], 'Sax Sing']
notess_instruments[96]  = [[0.79, 0.76, 0.73], 'Flute']
notess_instruments[89]  = [[0.62, 0.61, 0.63], 'Bass Clarinet']
notess_instruments[90]  = [[0.47, 0.47, 0.45], 'Clarinet']
notess_instruments[91]  = [[0.55, 0.54, 0.54], 'English Horn']
notess_instruments[92]  = [[0.49, 0.43, 0.42], 'Oboe']
notess_instruments[93]  = [[0.76, 0.36, 0.07], 'Ocarina']
notess_instruments[94]  = [[0.62, 0.50, 0.27], 'Wateki']

notess_instruments[104] = [[0.98, 0.81, 0.86], 'Oohh']
notess_instruments[105] = [[1.00, 0.67, 0.00], 'Aahh']
notess_instruments[106] = [[0.46, 0.46, 0.46], 'Choir']
notess_instruments[107] = [[0.80, 0.82, 0.85], 'Male Vox']
notess_instruments[108] = [[0.80, 0.82, 0.85], 'Female Vox']
notess_instruments[109] = [[0.33, 0.67, 0.70], 'Synth Vox']
notess_instruments[16]  = [[0.35, 0.36, 0.40], 'Grinding']
notess_instruments[29]  = [[0.33, 0.67, 0.70], 'Cheers']
notess_instruments[33]  = [[0.44, 0.66, 0.85], 'Energy']
notess_instruments[35]  = [[0.22, 0.79, 0.98], 'Crystal']
notess_instruments[38]  = [[0.75, 0.67, 0.62], 'Fade In']
notess_instruments[41]  = [[0.99, 0.84, 0.32], 'Space']
notess_instruments[55]  = [[0.93, 0.93, 0.93], 'Nice']


def parsenotes(bio_data, notelen): 
    patsize, numnotes = struct.unpack('>II', bio_data.read(8))

    notesout = {}
    for _ in range(numnotes):
        notedata = bio_data.read(20)
        #print(struct.unpack('>Ibbhbffh', notedata[:19]))
        n_pos,n_note,n_layer,n_inst,n_sharp,n_vol,n_pan,n_len = struct.unpack('>Ibbhbffh', notedata[:19])

        n_note = n_note-1

        n_key = (n_note-40)*-1
        out_oct = int(n_key/7)
        out_key = n_key - out_oct*7
        out_offset = 0

        if n_layer not in notesout: notesout[n_layer] = []
        if n_inst not in used_instruments: used_instruments.append(n_inst)

        if n_sharp == 2: out_offset = 1
        if n_sharp == 1: out_offset = -1


        note = {}
        note['position'] = (n_pos)*notelen
        note['duration'] = (n_len/4)*notelen
        note['key'] = keytable[out_key] + (out_oct-3)*12 + out_offset
        note['instrument'] = str(n_inst)
        notesout[n_layer].append(note)

    return patsize-32, notelen, notesout



class input_notessimo_v2(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'notessimo_v2'
    def getname(self): return 'Notessimo V2'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global used_instruments

        bytestream = open(input_file, 'rb')
        nv2_data = data_bytes.bytearray2BytesIO(zlib.decompress(bytestream.read()))
        len_songname = int.from_bytes(nv2_data.read(2), "big")
        text_songname = nv2_data.read(len_songname).decode('ascii')

        len_songauthor = int.from_bytes(nv2_data.read(2), "big")
        text_songauthor = nv2_data.read(len_songauthor).decode('ascii')

        len_date1 = int.from_bytes(nv2_data.read(2), "big")
        text_date1 = nv2_data.read(len_date1).decode('ascii')
        #print(text_songname, '-', text_songauthor)

        len_date2 = int.from_bytes(nv2_data.read(2), "big")
        text_date2 = nv2_data.read(len_date2).decode('ascii')
        #print(text_date1, '-', text_date2)

        len_order = int.from_bytes(nv2_data.read(2), "big")
        arr_order = struct.unpack('b'*len_order, nv2_data.read(len_order))
        #print(arr_order)

        tempo_table = struct.unpack('>'+'H'*100, nv2_data.read(200))

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}
        cvpj_auto_tempo = []
        used_instruments = []

        notess_sheets = {}
        for sheetnum in range(100):
            tempo = tempo_table[sheetnum]
            notelen = 1

            if tempo > 200:
                tempo = tempo/2
                notelen = notelen/2

            notess_sheets[sheetnum] = parsenotes(nv2_data, notelen)

        for sheetnum in range(100):
            sheetdata = notess_sheets[sheetnum][2]
            for layer in sheetdata:
                patid = str(sheetnum)+'_'+str(layer)
                cvpj_l_notelistindex[patid] = {}
                cvpj_l_notelistindex[patid]['notelist'] = sheetdata[layer]
                cvpj_l_notelistindex[patid]['name'] = '#'+str(sheetnum+1)+' Layer '+str(layer+1)

        #print(used_instruments)

        for used_instrument in used_instruments:
            notess_instdata = notess_instruments[used_instrument]

            cvpj_inst = {}
            cvpj_inst["pan"] = 0.0
            cvpj_inst['name'] = notess_instdata[1]
            cvpj_inst['color'] = notess_instdata[0]
            cvpj_inst["vol"] = 1.0
            cvpj_inst['instdata'] = {}
            cvpj_inst['instdata']['plugin'] = 'none'

            cvpj_l_instruments[str(used_instrument)] = cvpj_inst
            cvpj_l_instrumentsorder.append(str(used_instrument))

        curpos = 0
        for sheetnum in arr_order:
            cursheet_data = notess_sheets[sheetnum]
            for layer in cursheet_data[2]:
                patid = str(sheetnum)+'_'+str(layer)
                cvpj_l_placement = {}
                cvpj_l_placement['type'] = "instruments"
                cvpj_l_placement['position'] = curpos
                cvpj_l_placement['duration'] = cursheet_data[0]*cursheet_data[1]
                cvpj_l_placement['fromindex'] = patid
                if str(layer+1) not in cvpj_l_playlist: 
                    cvpj_l_playlist[str(layer+1)] = {}
                    cvpj_l_playlist[str(layer+1)]['placements'] = []
                cvpj_l_playlist[str(layer+1)]['placements'].append(cvpj_l_placement)

            autoplacement = {}
            autoplacement['position'] = curpos
            autoplacement['duration'] = cursheet_data[0]*cursheet_data[1]
            autoplacement['points'] = [{"position": 0, "value": tempo_table[sheetnum]*cursheet_data[1]}]
            cvpj_auto_tempo.append(autoplacement)

            curpos += cursheet_data[0]*cursheet_data[1]
        
        placements_auto = {}
        placements_auto['bpm'] = cvpj_auto_tempo

        cvpj_l['placements_auto_main'] = placements_auto
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = tempo_table[0]*notess_sheets[arr_order[0]][1]
        return json.dumps(cvpj_l)
