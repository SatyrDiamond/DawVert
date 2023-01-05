# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

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
	print(noteJ)
	if 'notemod' in noteJ:
		notemod = noteJ['notemod']

		noteautopitch_exists = False
		noteslide_exists = False
		if 'auto' in notemod:
			if 'pitch' in notemod['auto']:
				noteautopitch_exists = True
		if 'slide' in notemod: noteslide_exists = True

		if noteautopitch_exists == False and noteslide_exists == True:
			slidenumlist = {}
			slidenumlist[0] = {'value': 0, 'type':'normal'}
			curval = 0
			for slidepoint in notemod['slide']:
				print(slidepoint)
				slidenumlist[slidepoint['position']] = {'value': curval, 'type':'normal'}
				if slidepoint['duration'] == 0: slidenumlist[slidepoint['position']] = {'value': slidepoint['key'], 'type':'instant'}
				else: slidenumlist[slidepoint['position']+slidepoint['duration']] = {'value': slidepoint['key'], 'type':'normal'}
				curval = slidepoint['key']
			autolist = []
			for slidepart in slidenumlist: autolist.append({"position": slidepart, "value": slidenumlist[slidepart]['value'], "type": slidenumlist[slidepart]['type']})
			notemod['auto'] = {}
			notemod['auto']['pitch'] = autolist