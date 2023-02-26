# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def betweenvalues(minval, maxval, value): 
    return (minval*(1-value))+(maxval*value)

def move(notelist, pos):
	newnotelist = []
	for note in notelist:
		newnote = note.copy()
		newnote['position'] = newnote['position'] + pos
		if newnote['position'] >= 0: newnotelist.append(newnote)
	return newnotelist

def trim(notelist, pos):
	newnotelist = []
	for note in notelist:
		if note['position'] < pos: newnotelist.append(note)
	return newnotelist

def getduration(notelist):
	duration_final = 0
	for note in notelist:
		noteendpos = note['position']+note['duration']
		if duration_final < noteendpos: duration_final = noteendpos
	return duration_final

def trimmove(notelist, startat, endat):
	newnotelist = notelist
	if endat != None: newnotelist = trim(newnotelist, endat)
	if startat != None: newnotelist = move(newnotelist, -startat)
	return newnotelist

def sortnotes(notelist):
	t_notelist_bsort = {}
	t_notelist_sorted = {}
	new_notelist = []
	for note in notelist:
		if note['position'] not in t_notelist_bsort:
			t_notelist_bsort[note['position']] = []
		t_notelist_bsort[note['position']].append(note)
	t_notelist_sorted = dict(sorted(t_notelist_bsort.items(), key=lambda item: item[0]))
	for t_notepos in t_notelist_sorted:
		for note in t_notelist_sorted[t_notepos]:
			new_notelist.append(note)
	return new_notelist

def notemod_conv(noteJ):
	if 'notemod' in noteJ:
		notemod = noteJ['notemod']

		noteautopitch_exists = False
		noteslide_exists = False
		if 'auto' in notemod:
			if 'pitch' in notemod['auto']:
				noteautopitch_exists = True
		if 'slide' in notemod: noteslide_exists = True

		if noteautopitch_exists == False and noteslide_exists == True:
			t_slidepoints = []
			for l_sp in notemod['slide']:
				t_slidepoints.append([l_sp['position'], l_sp['duration'], l_sp['duration'], l_sp['key']])

			if t_slidepoints != []:
				for pointnum in range(len(t_slidepoints)):
					if pointnum < len(t_slidepoints)-1:
						t_slidepoints[pointnum][1] = min(t_slidepoints[pointnum+1][0]-t_slidepoints[pointnum][0], t_slidepoints[pointnum][1])

			pitchmod2point_init()
			cvpj_noteauto_pitch = []
			for t_sp in t_slidepoints:
				pitchmod2point(noteJ, t_sp[0], 1, t_sp[1], 1/t_sp[2], t_sp[3])

def pitchmod2point_init():
    global pitchpoints
    global pitch_cur
    global pitch_prev

    pitchpoints = []
    pitch_cur = 0
    pitch_prev = 0


def pitchmod2point(cvpj_note, position, ptype, maindur, slidedur, input_pitch):
    global pitchpoints
    global pitch_cur
    global pitch_prev

    #print( str(slidedur).ljust(4),  str(maindur).ljust(4),  str(maindur/slidedur).ljust(19), end='  ')

    mainslidedur_mul = slidedur*maindur
    mainslidedur_div = maindur/slidedur
    pitch_exact = False

    if 'notemod' not in cvpj_note: cvpj_note['notemod'] = {}
    if 'auto' not in cvpj_note['notemod']: cvpj_note['notemod']['auto'] = {}
    if 'pitch' not in cvpj_note['notemod']['auto']: cvpj_note['notemod']['auto']['pitch'] = []
    pitchpoints = cvpj_note['notemod']['auto']['pitch']

    if ptype == 0:
        if slidedur <= maindur:
            pitch_cur += input_pitch
            pitchpoints.append({'position': position, 'value': pitch_prev})
            pitchpoints.append({'position': position+slidedur, 'value': pitch_cur})
        elif slidedur > maindur:
            pitch_cur = betweenvalues(pitch_prev, pitch_prev+input_pitch, mainslidedur_div)
            pitchpoints.append({'position': position, 'value': pitch_prev})
            pitchpoints.append({'position': position+maindur, 'value': pitch_cur})

    elif ptype == 1:
        outdur = maindur
        if pitch_cur < input_pitch:
            #print('PLUS ',  str(input_pitch).ljust(4),  str(mainslidedur_mul).ljust(4), str(pitch_cur).ljust(4), end='-' )
            pitch_cur += (mainslidedur_mul)
            #print( str(pitch_cur).ljust(4), input_pitch < pitch_cur, end='' )
            pitch_exact = input_pitch < pitch_cur
            if pitch_exact == True:
                outdur = (mainslidedur_mul-(pitch_cur-input_pitch))/slidedur

        elif pitch_cur > input_pitch:
            #print('MINUS',  str(input_pitch).ljust(4),  str(mainslidedur_mul).ljust(4), str(pitch_cur).ljust(4), end='-' )
            pitch_cur -= (mainslidedur_mul)
            #print( str(pitch_cur).ljust(4), input_pitch < pitch_cur, end='' )
            pitch_exact = input_pitch > pitch_cur
            if pitch_exact == True:
                outdur = (mainslidedur_mul+(pitch_cur-input_pitch))/slidedur

        if pitch_exact == True:
            pitch_cur = input_pitch

        pitchpoints.append({'position': position, 'value': pitch_prev})
        pitchpoints.append({'position': position+outdur, 'value': pitch_cur})

    pitch_prev = pitch_cur