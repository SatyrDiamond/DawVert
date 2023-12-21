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







