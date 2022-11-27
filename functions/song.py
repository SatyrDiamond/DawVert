# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from functions import notemod


def removenotecut(song):
	for trackdata in song['tracks']:
		if trackdata['type'] == 'instrument':
			newplacements = []
			for placementdata in trackdata['placements']:
				if 'notecut' in placementdata: 
					notecutJ = placementdata['notecut']
					newplacement_base = {}
					newplacement_base = newplacement_base | placementdata
					notecut_end = None
					notecut_start = None
					notecut_end = notecutJ['end']
					notecut_start = notecutJ['start']
					trk_notelist = newplacement_base['notelist']
					del newplacement_base['notelist']

					newplacementdata = {}
					newplacementdata['notelist'] = notemod.trimmove(trk_notelist, notecut_start, notecut_end)
					#newplacementdata['duration'] = notecut_end - notecut_start
					newplacementdata = newplacementdata | newplacement_base
					newplacements.append(newplacementdata)
				else:
					newplacements.append(placementdata)
			trackdata['placements'] = newplacements

def sort_by_cvpjm_inst(song):
	usedinstruments = []
	newtracks = []
	for track in song['tracks']:
		if track['frominstrumentid'] not in usedinstruments:
			usedinstruments.append(track['frominstrumentid'])
	usedinstruments = sorted(usedinstruments)
	for usedinstrument in usedinstruments:
		for track in song['tracks']:
			if track['frominstrumentid'] == usedinstrument:
				newtracks.append(track)
	song['tracks'] = newtracks
