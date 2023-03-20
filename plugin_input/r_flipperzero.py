# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import os.path
from functions import placements
from functions import tracks

class input_fmf(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'flipper'
    def getname(self): return 'Flipper Music Format'
    def gettype(self): return 'r'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(30)
        if bytesdata == b'Filetype: Flipper Music Format': return True
        else: return False
        bytestream.seek(0)
    def parse(self, input_file, extra_param):

        l_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        fmf_BPM = 120
        fmf_Duration = 4
        fmf_Octave = 5
        Notes = []

        totalDuration = 0

        f_fmf = open(input_file, 'r')
        lines_fmf = f_fmf.readlines()
        for line in lines_fmf:
            if line != "\n":
                fmf_command, fmf_param = line.rstrip().split(': ')
                if fmf_command == 'BPM': fmf_BPM = int(fmf_param)
                if fmf_command == 'Duration': fmf_Duration = int(fmf_param)
                if fmf_command == 'Octave': fmf_Octave = int(fmf_param)
                if fmf_command == 'Notes':
                    fmf_notes = fmf_param.split(',')
                    for fmf_note in fmf_notes:
                        nospacenote = fmf_note.strip()
                        part_Note = ''
                        part_Duration = ''
                        part_Oct = ''
                        part_Period = 0
                        number_parsemode = 'D'
                        for notepart in nospacenote:
                            #print(notepart, end='')
                            if number_parsemode == 'D':
                                if notepart.isalpha() == False: part_Duration += notepart
                                if notepart == "#":
                                    part_Note += notepart
                                if notepart.isalpha() == True:
                                    part_Note += notepart
                                    number_parsemode = 'O'
                            if number_parsemode == 'O':
                                if notepart == "#": part_Note += notepart
                                if notepart.isnumeric() == True: part_Oct += notepart
                                if notepart == '.': part_Period += 1
                        

                        if part_Oct == '': output_Oct = (fmf_Octave-5)*12
                        else: output_Oct = (int(part_Oct)-5)*12
                        if part_Note in l_key: output_Note = l_key.index(part_Note)+output_Oct
                        else: output_Note = None
                        if part_Duration == '': output_Duration = (fmf_Duration/16)/8
                        else: output_Duration = (fmf_Duration*(1/int(part_Duration)))/8

                        Notes.append([output_Note, output_Duration])



        global tracklist
        global trackordering
        global trackplacements

        notelist = []

        position = 0
        for Note in Notes:
            n_d = Note[1]*fmf_Duration
            n_k = Note[0]
            totalDuration += n_d
            if n_k != None:
                notedata = {}
                notedata["duration"] = n_d
                notedata["key"] = n_k
                notedata["position"] = position
                notelist.append(notedata)
            position += n_d

        cvpj_l = {}

        tracks.r_addtrack_inst(cvpj_l, 'flipperzero', {})
        tracks.r_addtrack_data(cvpj_l, 'flipperzero', 'Flipper Zero', [0.94, 0.58, 0.23], None, None)
        tracks.r_addtrackpl(cvpj_l, 'flipperzero', placements.nl2pl(notelist))

        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        
        cvpj_l['bpm'] = fmf_BPM

        return json.dumps(cvpj_l)

