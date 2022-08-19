# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import _func_notemod

def removewarping(song):
	for trackdata in song['tracks']:
		#print(trackdata['name'])
		if trackdata['type'] == 'instrument':
			newplacements = []
			for placementdata in trackdata['placements']:
				firstsplit = 1
				trackposition = placementdata['position']
				tracknotelist = placementdata['notelist']
				#print(json.dumps(placementdata, indent=2))
				if 'noteloop' in placementdata:
					currentpos = 0
					duration = placementdata['noteloop']['duration']
					startpoint = placementdata['noteloop']['startpoint']
					endpoint = placementdata['noteloop']['endpoint']
					remainingduration = duration + startpoint
					print('----- ' + str(duration))
					if duration != endpoint:
						while currentpos-duration <= duration:
							newplacementdata = {}
							part_position = currentpos
							part_duration = endpoint
							trim_duration = min(part_duration,remainingduration)
							print(str(part_position) + ' ' + str(trim_duration))
							newnotelist = _func_notemod.trim(tracknotelist, trim_duration)
							if trim_duration > 0:
								if firstsplit == 1:
									newplacementdata['position'] = (trackposition + part_position + startpoint) - startpoint
									newplacementdata['notelist'] = _func_notemod.move(newnotelist, -startpoint)
								else:
									newplacementdata['position'] = (trackposition + part_position) - startpoint
									newplacementdata['notelist'] = newnotelist
								newplacements.append(newplacementdata)
							remainingduration -= endpoint 
							currentpos += endpoint
							firstsplit = 0
					else:
						newplacements.append(placementdata)
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
