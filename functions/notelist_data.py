# SPDX-FileCopyrightText: 2023 SatyrDiamond
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

def sort(notelist):
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
