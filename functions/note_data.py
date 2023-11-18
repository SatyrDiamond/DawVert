# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import math

def rx_makenote(t_pos, t_dur, t_key, t_vol, t_pan):
    note_data = {}
    note_data['position'] = t_pos
    if t_dur != None: note_data['duration'] = t_dur
    else: note_data['duration'] = 1
    note_data['key'] = t_key
    if t_pan != None: note_data['pan'] = t_pan
    if t_vol != None: note_data['vol'] = t_vol
    return note_data

def mx_makenote(t_inst, t_pos, t_dur, t_key, t_vol, t_pan):
    note_data = rx_makenote(t_pos, t_dur, t_key, t_vol, t_pan)
    note_data['instrument'] = t_inst
    return note_data

keytable_vals = [0,2,4,5,7,9,11] 
keytable = ['C','D','E','F','G','A','B']

def text_to_note(i_keytxt):
    keyletter = i_keytxt[0]
    keysharp = True if i_keytxt[1] == '#' else False
    keyoct = int(i_keytxt[-1])-5
    return keyletter_to_note(keyletter, keyoct) + int(keysharp)

def keynum_to_note(i_keynum, i_oct):
    return keytable_vals[i_keynum] + (i_oct)*12

def keyletter_to_note(i_keyletter, i_oct):
    return keytable_vals[keytable.index(i_keyletter)] + (i_oct)*12

def freq_to_note_noround(freq):
    return 12*math.log2(freq/(440*pow(2, -4.75)))-60

def freq_to_note(freq):
    out_note = 12*math.log2(freq/(440*pow(2, -4.75)))-60
    return round(out_note), round((out_note-round(out_note))*100)

def note_to_freq(note):
    return (440/32)*(2**((note+63)/12))










class pitchmod2point:
    def __init__(self):
        self.pitchpoints = []
        self.pitch_cur = 0
        self.pitch_prev = 0
        self.slide_zeropospointexist = False

    def pitchmod2point(cvpj_note, position, ptype, maindur, slideparam, input_pitch):
        mainslideparam_mul = slideparam*maindur
        pitch_exact = False

        if ptype == 0:
            if slideparam <= maindur:
                self.pitch_cur += input_pitch
                self.pitchpoints.append({'position': position, 'value': self.pitch_prev})
                self.pitchpoints.append({'position': position+slideparam, 'value': self.pitch_cur})
            elif slideparam > maindur:
                self.pitch_cur = xtramath.between_from_one(self.pitch_prev, self.pitch_prev+input_pitch, maindur/slideparam)
                self.pitchpoints.append({'position': position, 'value': self.pitch_prev})
                self.pitchpoints.append({'position': position+maindur, 'value': self.pitch_cur})

        elif ptype == 1:
            input_pitch -= cvpj_note['key']

            outdur = maindur
            if self.pitch_cur < input_pitch:
                self.pitch_cur += (mainslideparam_mul)
                pitch_exact = input_pitch < self.pitch_cur
                if pitch_exact == True: outdur = (mainslideparam_mul-(self.pitch_cur-input_pitch))/slideparam

            elif self.pitch_cur > input_pitch:
                self.pitch_cur -= (mainslideparam_mul)
                pitch_exact = input_pitch > self.pitch_cur
                if pitch_exact == True: outdur = (mainslideparam_mul+(self.pitch_cur-input_pitch))/slideparam

            if pitch_exact == True: self.pitch_cur = input_pitch

            totalslidedur = outdur/maindur

            if totalslidedur > 0.1:
                self.pitchpoints.append({'position': position, 'value': self.pitch_prev})
                self.pitchpoints.append({'position': position+(totalslidedur), 'value': self.pitch_cur})
            else:
                self.pitchpoints.append({'position': position, 'value': self.pitch_cur, 'type': 'instant'})

        elif ptype == 2:
            #print( 
            #   str(position).ljust(4),  
            #   str(maindur).ljust(4),  
            #   str(slideparam).ljust(4),  
            #   str(input_pitch).ljust(4),  
            #   str(position).rjust(4)+'-'+str(position+slideparam).ljust(4),
            #   str(slideparam/maindur).ljust(4),  
            #   )
    
            if self.slide_zeropospointexist == False:
                self.pitchpoints.append({'position': 0, 'value': 0})
                self.slide_zeropospointexist = True
            if slideparam != 0:
                self.pitchpoints.append({'position': position, 'value': self.pitch_cur})
                if slideparam > maindur:
                    self.pitchpoints.append({'position': position+maindur, 'value': input_pitch*(maindur/slideparam)})
                    self.pitch_cur = input_pitch*(maindur/slideparam)
                else:
                    self.pitchpoints.append({'position': position+slideparam, 'value': input_pitch})
                    self.pitch_cur = input_pitch
            else:
                self.pitchpoints.append({'position': position, 'value': input_pitch, 'type': 'instant'})
                self.pitch_cur = input_pitch

        self.pitch_prev = self.pitch_cur









class notelist:
    def __init__(self, ppq, in_notelist):
        self.nl = []
        self.ppq = ppq
        self.used_inst = []
        if in_notelist != None:
            for cn in in_notelist:
                cvpj_note = cn.copy()
                t_pos = cvpj_note['position']
                t_dur = cvpj_note['duration']
                t_key = cvpj_note['key']
                t_vol = cvpj_note['vol'] if 'vol' in cvpj_note else None
                t_inst = cvpj_note['instrument'] if 'instrument' in cvpj_note else None

                del cvpj_note['position']
                del cvpj_note['duration']
                del cvpj_note['key']
                if t_vol != None: del cvpj_note['vol']
                if t_inst != None: del cvpj_note['instrument']
                t_extra = cvpj_note
                self.add_m(t_inst, t_pos, t_dur, t_key, t_vol, t_extra)


    def add_r(self, t_pos, t_dur, t_key, t_vol, t_extra):
        self.nl.append([t_pos, t_dur, t_key, t_vol, None, t_extra, None, None])

    def add_m(self, t_inst, t_pos, t_dur, t_key, t_vol, t_extra):
        self.nl.append([t_pos, t_dur, t_key, t_vol, t_inst, t_extra, None, None])
        if t_inst != None: 
            if t_inst not in self.used_inst: self.used_inst.append(t_inst)

    def auto_add_last(self, a_type, p_pos, p_val, p_type, p_tension):
        if self.nl != []:
            if self.nl[-1][6] == None: self.nl[-1][6] = {}
            notedata = self.nl[-1]
            if a_type not in notedata[6]: notedata[6][a_type] = []
            notedata[6][a_type].append([p_pos, p_val, p_type, p_tension])



    def get_dur(self):
        duration_final = 0
        for note in self.nl:
            noteendpos = new_n[0]+new_n[1]
            if duration_final < noteendpos: duration_final = noteendpos
        return duration_final/self.ppq




    def edit_move(self, pos):
        new_nl = []
        for n in self.nl.copy():
            new_n[0] += pos
            if new_n[0] >= 0: new_nl.append()
        self.nl = new_nl

    def edit_move_minus(self, pos):
        for n in self.nl: n[0] += pos

    def edit_trim(self, pos):
        new_nl = []
        for n in self.nl.copy():
            if new_n[0] < pos: new_nl.append()
        self.nl = new_nl

    def edit_trimmove(self, startat, endat):
        if endat != None: self.trim(endat)
        if startat != None: self.move(-startat)

    def sort(self):
        t_nl_bsort = {}
        t_nl_sorted = {}
        new_nl = []
        for n in self.nl:
            if new_n[0] not in t_nl_bsort: t_nl_bsort[new_n[0]] = []
            t_nl_bsort[new_n[0]].append(n)
        t_nl_sorted = dict(sorted(t_nl_bsort.items(), key=lambda item: item[0]))
        for p in t_nl_sorted:
            for note in t_nl_sorted[p]: new_nl.append(note)
        self.nl = new_nl

    def to_cvpj(self):
        cvpj_out = []
        for note in self.nl:
            note_data = {}
            note_data['position'] = (note[0]/self.ppq)*4
            note_data['duration'] = (note[1]/self.ppq)*4
            note_data['key'] = note[2]
            if note[3] != None: note_data['vol'] = note[3]
            if note[4] != None: note_data['instrument'] = note[4]
            if note[5] != None: 
                for key, value in note[5].items(): note_data[key] = value
            if note[6] != None: 
                if 'notemod' not in note_data: note_data['notemod'] = {}
                if 'auto' not in note_data['notemod']: note_data['notemod']['auto'] = {}
                for key, value in note[6].items():
                    note_data['notemod']['auto'][key] = []
                    for autod in value:
                        pointJ = {}
                        pointJ['position'] = (autod[0]/self.ppq)*4
                        pointJ['value'] = autod[1]
                        pointJ['type'] = autod[2] if autod[2] != None else 'normal'
                        if autod[3] != None: pointJ['tension'] = autod[3]
                        note_data['notemod']['auto'][key].append(pointJ)

            cvpj_out.append(note_data)
        return cvpj_out