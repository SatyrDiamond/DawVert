# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import plugin_input
import json
import zlib
import struct

keytable = [0,2,4,5,7,9,11,12]

notess_instruments =  {}
notess_instruments[12]  = [None,   25, [0.81, 0.59, 0.35], 'Acoustic Guitar']
notess_instruments[82]  = [None,   29, [0.87, 0.66, 0.07], 'Damant Spectrum Muted']
notess_instruments[79]  = [None,   26, [0.51, 0.80, 0.76], 'Fender Strat Guitar']
notess_instruments[78]  = [None,   26, [0.33, 0.42, 0.68], 'Strat Guitar']
notess_instruments[47]  = [None,   30, [0.05, 0.05, 0.05], 'Metal Guitar']
notess_instruments[64]  = [None,   27, [0.71, 0.38, 0.13], 'Guitar Electric']
notess_instruments[77]  = [None,   28, [0.23, 0.21, 0.21], 'Clean Electric Guitar']
notess_instruments[81]  = [None, None, [0.72, 0.09, 0.15], 'Damant Spectrum Harm']
notess_instruments[49]  = [None, None, [0.64, 0.24, 0.04], 'Bass Guitar']
notess_instruments[1]   = [None,   33, [0.64, 0.24, 0.04], 'Bass']
notess_instruments[39]  = [None,   34, [0.70, 0.29, 0.24], 'Bass #2']
notess_instruments[52]  = [None,   35, [0.70, 0.36, 0.12], 'Bass #3']
notess_instruments[59]  = [None,   36, [0.49, 0.11, 0.13], 'Bass #4']
notess_instruments[0]   = [None,   39, [0.18, 0.20, 0.21], 'Synth Bass']
notess_instruments[21]  = [None,   40, [0.18, 0.20, 0.21], 'Synth Bass #2']
notess_instruments[135] = [None,  105, [0.43, 0.13, 0.04], 'Sitar']
notess_instruments[136] = [None,   46, [0.91, 0.38, 0.16], 'Pizzicato']
notess_instruments[9]   = [None,   49, [0.89, 0.36, 0.16], 'Strings']
notess_instruments[36]  = [None,   50, [0.91, 0.38, 0.16], 'Strings #2']
notess_instruments[37]  = [None,   49, [0.71, 0.24, 0.09], 'Strings #3']
notess_instruments[31]  = [None,   51, [0.40, 0.53, 0.42], 'Synth Strings']
notess_instruments[80]  = [None, None, [0.33, 0.33, 0.33], 'Fret Noise']

notess_instruments[28]  = [None,    1, [0.00, 0.00, 0.00], 'Grand Piano']
notess_instruments[114] = [None,    5, [0.18, 0.18, 0.16], 'Rhodes']
notess_instruments[121] = [None,   56, [0.37, 0.18, 0.14], 'Orchestra Hit']
notess_instruments[13]  = [None, None, [0.00, 0.00, 0.00], 'Low Piano']
notess_instruments[115] = [None,    6, [0.68, 0.68, 0.68], 'Rhodes #2']
notess_instruments[11]  = [None, None, [0.56, 0.67, 0.25], 'Synth']
notess_instruments[116] = [None,    3, [0.79, 0.04, 0.09], 'Electric Piano']
notess_instruments[117] = [None,   19, [0.67, 0.49, 0.39], 'Rock Organ']
notess_instruments[17]  = [None,   84, [0.11, 0.11, 0.11], 'Synth #2']
notess_instruments[111] = [None,    8, [0.76, 0.76, 0.76], 'Clavinet']
notess_instruments[118] = [None,   20, [0.37, 0.18, 0.14], 'Church Organ']
notess_instruments[23]  = [None,   81, [0.33, 0.34, 0.39], 'Synthesizer']
notess_instruments[112] = [None, None, [0.56, 0.37, 0.31], 'Electric Clavinet']
notess_instruments[119] = [None,   18, [0.34, 0.31, 0.35], 'Percussive Organ']
notess_instruments[34]  = [None,   82, [0.33, 0.34, 0.39], 'Synthesizer #2']
notess_instruments[113] = [None,    7, [0.48, 0.31, 0.31], 'Harpsichord']
notess_instruments[120] = [None,   17, [0.11, 0.11, 0.11], 'Organ']
notess_instruments[50]  = [None,   83, [0.33, 0.34, 0.39], 'Synthesizer #3']
notess_instruments[110] = [None,   22, [0.45, 0.17, 0.20], 'Accordian']
notess_instruments[22]  = [None, None, [0.33, 0.34, 0.39], 'Triangle Wave']

notess_instruments[133] = [None, None, [0.07, 0.18, 0.26], 'Techno Bass']

notess_instruments[2]   = [   1, None, [0.06, 0.07, 0.08], 'Bass Drum']
notess_instruments[18]  = [   1, None, [0.11, 0.39, 0.29], 'Bass Drum #2']
notess_instruments[24]  = [   1, None, [0.06, 0.07, 0.08], 'Bass Drum #3']
notess_instruments[43]  = [   1, None, [0.11, 0.39, 0.29], 'Bass Drum #4']
notess_instruments[60]  = [   1, None, [0.06, 0.07, 0.08], 'Bass Drum #5']
notess_instruments[15]  = [   1, None, [0.85, 0.66, 0.37], 'Snare Drum']
notess_instruments[42]  = [   1, None, [0.72, 0.73, 0.76], 'Snare Drum #2']
notess_instruments[44]  = [   1, None, [0.88, 0.78, 0.67], 'Snare Drum #3']
notess_instruments[56]  = [   1, None, [0.70, 0.60, 0.51], 'Snare Drum #4']
notess_instruments[67]  = [   1, None, [0.72, 0.73, 0.76], 'Snare Drum #5']
notess_instruments[14]  = [   1, None, [0.67, 0.61, 0.58], 'Tom Drums']
notess_instruments[27]  = [   1, None, [0.45, 0.45, 0.43], 'High Tom']
notess_instruments[53]  = [   1, None, [0.63, 0.45, 0.29], 'DX Tom']
notess_instruments[62]  = [   1, None, [0.35, 0.36, 0.53], 'Dry Tom']
notess_instruments[57]  = [   1, None, [0.39, 0.27, 0.16], 'Drum Reverb']
notess_instruments[3]   = [   1, None, [0.82, 0.56, 0.25], 'Closed Hi Hat']
notess_instruments[26]  = [   1, None, [0.82, 0.56, 0.25], 'Closed Hi Hat #2']
notess_instruments[61]  = [   1, None, [0.82, 0.56, 0.25], 'Closed Hi Hat #3']
notess_instruments[5]   = [   1, None, [0.80, 0.71, 0.41], 'Open Hi Hat']
notess_instruments[19]  = [   1, None, [0.89, 0.72, 0.34], 'Open Hi Hat #2']
notess_instruments[30]  = [   1, None, [0.80, 0.71, 0.41], 'Open Hi Hat #3']
notess_instruments[65]  = [   1, None, [0.89, 0.72, 0.34], 'Open Hi Hat #4']
notess_instruments[25]  = [   1, None, [0.86, 0.70, 0.44], 'Cymbal']
notess_instruments[45]  = [   1, None, [0.72, 0.71, 0.74], 'Cymbal #2']
notess_instruments[46]  = [   1, None, [0.10, 0.11, 0.14], 'Cymbal #3']
notess_instruments[66]  = [   1, None, [0.86, 0.70, 0.44], 'Reverse Cymbal']
notess_instruments[40]  = [   1, None, [0.88, 0.78, 0.67], 'Drum Loop']

notess_instruments[123] = [None,   10, [0.73, 0.65, 0.54], 'Glockenspiel']
notess_instruments[126] = [None,   14, [0.69, 0.58, 0.25], 'Xylophone']
notess_instruments[125] = [None,   12, [0.60, 0.61, 0.63], 'Vibraphone']
notess_instruments[124] = [None,   13, [0.89, 0.53, 0.02], 'Marimba']
notess_instruments[127] = [None,  109, [0.69, 0.36, 0.11], 'Kalimba']
notess_instruments[4]   = [None,  116, [0.76, 0.59, 0.43], 'Woodblock']
notess_instruments[129] = [None, None, [0.78, 0.75, 0.75], 'Clave']
notess_instruments[6]   = [None, None, [0.76, 0.76, 0.75], 'Tambourine']
notess_instruments[134] = [None,  115, [0.74, 0.22, 0.19], 'Steel Drum']
notess_instruments[130] = [None, None, [0.71, 0.46, 0.24], 'Conga']
notess_instruments[131] = [None, None, [0.98, 0.42, 0.15], 'Conga #2']
notess_instruments[132] = [None, None, [0.83, 0.65, 0.43], 'Conga #3']
notess_instruments[7]   = [None,  117, [0.82, 0.27, 0.11], 'Taiko Drum']
notess_instruments[10]  = [None,   48, [0.84, 0.70, 0.54], 'Timpani']
notess_instruments[128] = [None, None, [0.27, 0.29, 0.27], 'Cowbell']
notess_instruments[122] = [None,   15, [0.22, 0.20, 0.20], 'Tubular Bell']
notess_instruments[51]  = [None, None, [0.56, 0.59, 0.57], 'Blast']
notess_instruments[20]  = [None, None, [1.00, 0.82, 0.58], 'Hand Clap']

notess_instruments[8]   = [None,   57, [0.77, 0.63, 0.39], 'Trumpet']
notess_instruments[100] = [None,   57, [0.58, 0.51, 0.33], 'Trumpet #2']
notess_instruments[103] = [None,   73, [0.74, 0.67, 0.47], 'Piccolo Trumpet']
notess_instruments[99]  = [None, None, [0.75, 0.65, 0.47], 'Trumpet Muted']
notess_instruments[101] = [None, None, [0.60, 0.56, 0.45], 'Trumpet Hit']
notess_instruments[102] = [None, None, [0.69, 0.64, 0.53], 'Trumpet Section']
notess_instruments[97]  = [None,   58, [0.75, 0.65, 0.46], 'Trombone']
notess_instruments[95]  = [None,   59, [0.78, 0.65, 0.32], 'Tuba']
notess_instruments[98]  = [None,   61, [0.83, 0.68, 0.38], 'French Horn']
notess_instruments[58]  = [None,   63, [0.74, 0.62, 0.49], 'Synth Brass']

notess_instruments[83]  = [None,   65, [0.81, 0.73, 0.56], 'Soprano Sax']
notess_instruments[84]  = [None,   66, [0.95, 0.88, 0.63], 'Alto Sax']
notess_instruments[87]  = [None,   67, [0.67, 0.52, 0.31], 'Tenor Sax']
notess_instruments[88]  = [None,   68, [0.73, 0.59, 0.37], 'Baritone Sax']
notess_instruments[85]  = [None, None, [0.85, 0.72, 0.36], 'Sax Hit']
notess_instruments[86]  = [None, None, [0.79, 0.79, 0.57], 'Sax Sing']
notess_instruments[96]  = [None,   74, [0.79, 0.76, 0.73], 'Flute']
notess_instruments[89]  = [None, None, [0.62, 0.61, 0.63], 'Bass Clarinet']
notess_instruments[90]  = [None,   72, [0.47, 0.47, 0.45], 'Clarinet']
notess_instruments[91]  = [None,   70, [0.55, 0.54, 0.54], 'English Horn']
notess_instruments[92]  = [None,   69, [0.49, 0.43, 0.42], 'Oboe']
notess_instruments[93]  = [None,   80, [0.76, 0.36, 0.07], 'Ocarina']
notess_instruments[94]  = [None, None, [0.62, 0.50, 0.27], 'Wateki']

notess_instruments[104] = [None,   54, [0.98, 0.81, 0.86], 'Oohh']
notess_instruments[105] = [None,   53, [1.00, 0.67, 0.00], 'Aahh']
notess_instruments[106] = [None, None, [0.46, 0.46, 0.46], 'Choir']
notess_instruments[107] = [None, None, [0.80, 0.82, 0.85], 'Male Vox']
notess_instruments[108] = [None, None, [0.80, 0.82, 0.85], 'Female Vox']
notess_instruments[109] = [None,   55, [0.33, 0.67, 0.70], 'Synth Vox']
notess_instruments[16]  = [None, None, [0.35, 0.36, 0.40], 'Grinding']
notess_instruments[29]  = [None, None, [0.33, 0.67, 0.70], 'Cheers']
notess_instruments[33]  = [None, None, [0.44, 0.66, 0.85], 'Energy']
notess_instruments[35]  = [None, None, [0.22, 0.79, 0.98], 'Crystal']
notess_instruments[38]  = [None, None, [0.75, 0.67, 0.62], 'Fade In']
notess_instruments[41]  = [None, None, [0.99, 0.84, 0.32], 'Space']
notess_instruments[55]  = [None, None, [0.93, 0.93, 0.93], 'Nice']

def getstring(bytesdata):
    stringlen = int.from_bytes(bytesdata.read(2), "big")
    if stringlen != 0: return bytesdata.read(stringlen).decode("utf-8")
    else: return ''

def parsenotes(bio_data, notelen): 
    patsize, numnotes = struct.unpack('>II', bio_data.read(8))

    notesout = {}
    for _ in range(numnotes):
        notedata = bio_data.read(20)
        n_pos,n_note,n_layer,n_inst,n_sharp,n_vol,n_pan,n_len = struct.unpack('>Ibbhbffh', notedata[:19])

        n_key = (n_note-41)*-1
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
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'notessimo_v2'
    def getname(self): return 'Notessimo V2'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global used_instruments

        bytestream = open(input_file, 'rb')
        nv2_data = data_bytes.bytearray2BytesIO(zlib.decompress(bytestream.read()))
        text_songname = getstring(nv2_data)
        text_songauthor = getstring(nv2_data)
        text_date1 = getstring(nv2_data)
        text_date2 = getstring(nv2_data)
        print("[input-notessimo_v2] Song Name: " + str(text_songname))
        print("[input-notessimo_v2] Song Author: " + str(text_songauthor))

        len_order = int.from_bytes(nv2_data.read(2), "big")
        arr_order = struct.unpack('b'*len_order, nv2_data.read(len_order))
        print("[input-notessimo_v2] Order List: " + str(arr_order))

        tempo_table = struct.unpack('>'+'H'*100, nv2_data.read(200))

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}
        cvpj_l_fxrack = {}
        cvpj_auto_tempo = []
        used_instruments = []

        cvpj_l_fxrack["1"] = {}
        cvpj_l_fxrack["1"]["name"] = "Drums"

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
            if len(sheetdata) != 0: 
                print("[input-notessimo_v2] Sheet "+str(sheetnum)+", Layers:",end=' ')
                for layer in sheetdata:
                    print(layer,end=' ')
                    patid = str(sheetnum)+'_'+str(layer)
                    cvpj_l_notelistindex[patid] = {}
                    cvpj_l_notelistindex[patid]['notelist'] = sheetdata[layer]
                    cvpj_l_notelistindex[patid]['name'] = '#'+str(sheetnum+1)+' Layer '+str(layer+1)
                print()

        fxnum = 2
        for used_instrument in used_instruments:
            notess_instdata = notess_instruments[used_instrument]
            print("[input-notessimo_v2] Instrument: " + str(notess_instdata[3]))
            midiinst = notess_instdata[1]

            cvpj_inst = {}
            cvpj_inst["pan"] = 0.0
            cvpj_inst['name'] = notess_instdata[3]
            cvpj_inst['color'] = notess_instdata[2]

            if notess_instdata[0] == 1:
                cvpj_inst['fxrack_channel'] = 1
            else:
                cvpj_inst['fxrack_channel'] = fxnum
                cvpj_l_fxrack[str(fxnum)] = {}
                cvpj_l_fxrack[str(fxnum)]["name"] = notess_instdata[3]
                cvpj_l_fxrack[str(fxnum)]["color"] = notess_instdata[2]
                fxnum += 1
                
            cvpj_inst["vol"] = 1.0
            cvpj_inst['instdata'] = {}
            if midiinst == None:
                cvpj_inst['instdata']['plugin'] = 'none'
            else:
                cvpj_inst['instdata']['plugin'] = 'general-midi'
                cvpj_inst['instdata']['plugindata'] = {'bank':0, 'inst':midiinst}

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

        cvpj_l['use_fxrack'] = True
        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['placements_auto_main'] = placements_auto
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = tempo_table[0]*notess_sheets[arr_order[0]][1]
        return json.dumps(cvpj_l)
