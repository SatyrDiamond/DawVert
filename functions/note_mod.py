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
			t_slidenotepoints = []
			for l_sp in notemod['slide']:
				t_slidenotepoints.append([l_sp['position'], l_sp['duration'], l_sp['key']])

			cvpj_snps = []
			for num in range(len(t_slidenotepoints)):
				snpdata = t_slidenotepoints[num]
				cvpj_snps.append([snpdata[0], snpdata[1], snpdata[1], snpdata[2]])
				if num-1 >= 0:
					cvpj_snps[num-1][1] = cvpj_snps[num][0]-cvpj_snps[num-1][0]
			
			pitchmod2point_init()
			for cvpj_snp in cvpj_snps:
				pitchmod2point(noteJ, cvpj_snp[0], 2, cvpj_snp[1], cvpj_snp[2], cvpj_snp[3])


		if noteautopitch_exists == True and noteslide_exists == False:
			cvpj_auto_pitch = notemod['auto']['pitch'] 
			t_posval = []
			prevvalue = 0

			for part in cvpj_auto_pitch:
				isinstant = False
				if 'type' in part:
					if part['type'] == 'instant':
						isinstant = True

				if isinstant == True: t_posval.append([part['position'], prevvalue])
				t_posval.append([part['position'], part['value']])
				prevvalue = part['value']

			notemod['slide'] = []
			for pinu in range(len(t_posval)-1):
				slide_dur = t_posval[pinu+1][0] - t_posval[pinu][0]
				
				if t_posval[pinu+1][1] != t_posval[pinu][1]:
					notemod['slide'].append({
						'position': t_posval[pinu][0], 
						'duration': slide_dur, 
						'key': t_posval[pinu+1][1],
						'finepitch': (t_posval[pinu+1][1]-round(t_posval[pinu+1][1]))*100
						})



def pitchmod2point_init():
	global pitchpoints
	global pitch_cur
	global pitch_prev
	global slide_zeropospointexist

	pitchpoints = []
	pitch_cur = 0
	pitch_prev = 0
	slide_zeropospointexist = False

# normal			cvpj_note, position, 0, maindur, slideparam, input_pitch
# tone porta		cvpj_note, position, 1, maindur, slideparam, input_pitch
#

def pitchmod2point(cvpj_note, position, ptype, maindur, slideparam, input_pitch):
	global pitchpoints
	global pitch_cur
	global pitch_prev
	global slide_zeropospointexist

	#print( str(slideparam).ljust(4),  str(maindur).ljust(4),  str(maindur/slideparam).ljust(19), end='  ')

	mainslideparam_mul = slideparam*maindur
	pitch_exact = False

	if 'notemod' not in cvpj_note: cvpj_note['notemod'] = {}
	if 'auto' not in cvpj_note['notemod']: cvpj_note['notemod']['auto'] = {}
	if 'pitch' not in cvpj_note['notemod']['auto']: cvpj_note['notemod']['auto']['pitch'] = []
	
	pitchpoints = cvpj_note['notemod']['auto']['pitch']

	if ptype == 0:
		if slideparam <= maindur:
			pitch_cur += input_pitch
			pitchpoints.append({'position': position, 'value': pitch_prev})
			pitchpoints.append({'position': position+slideparam, 'value': pitch_cur})
		elif slideparam > maindur:
			pitch_cur = betweenvalues(pitch_prev, pitch_prev+input_pitch, maindur/slideparam)
			pitchpoints.append({'position': position, 'value': pitch_prev})
			pitchpoints.append({'position': position+maindur, 'value': pitch_cur})

	elif ptype == 1:
		input_pitch -= cvpj_note['key']

		outdur = maindur
		if pitch_cur < input_pitch:
			pitch_cur += (mainslideparam_mul)
			pitch_exact = input_pitch < pitch_cur
			if pitch_exact == True:
				outdur = (mainslideparam_mul-(pitch_cur-input_pitch))/slideparam

		elif pitch_cur > input_pitch:
			pitch_cur -= (mainslideparam_mul)
			pitch_exact = input_pitch > pitch_cur
			if pitch_exact == True:
				outdur = (mainslideparam_mul+(pitch_cur-input_pitch))/slideparam

		if pitch_exact == True:
			pitch_cur = input_pitch

		totalslidedur = outdur/maindur

		if totalslidedur > 0.1:
			pitchpoints.append({'position': position, 'value': pitch_prev})
			pitchpoints.append({'position': position+(totalslidedur), 'value': pitch_cur})
		else:
			pitchpoints.append({'position': position, 'value': pitch_cur, 'type': 'instant'})

	elif ptype == 2:
		if slide_zeropospointexist == False:
			pitchpoints.append({'position': 0, 'value': 0})
			slide_zeropospointexist = True
		if slideparam != 0:
			pitchpoints.append({'position': position, 'value': pitch_prev})
			pitchpoints.append({'position': position+min(maindur, slideparam), 'value': input_pitch})
			pitch_cur = input_pitch*min(1, maindur/slideparam)
		else:
			pitchpoints.append({'position': position, 'value': input_pitch, 'type': 'instant'})
			pitch_cur = input_pitch

	pitch_prev = pitch_cur