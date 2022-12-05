# SPDX-FileCopyrightText: 2022 SatyrDiamond
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