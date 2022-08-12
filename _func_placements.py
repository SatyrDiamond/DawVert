import json

def removewarping(song):
	for trackdata in song['tracks']:
		#print(trackdata['name'])
		newplacements = []
		for placementdata in trackdata['placements']:
			trackposition = placementdata['position']
			tracknotelist = placementdata['notelist']
			#print(json.dumps(placementdata, indent=2))
			if 'noteloop' in placementdata:
				currentpos = 0
				duration = placementdata['noteloop']['duration']
				startpoint = placementdata['noteloop']['startpoint']
				endpoint = placementdata['noteloop']['endpoint']
				remainingduration = duration
				print(str(duration))
				if duration != endpoint:
					while currentpos <= duration:
						newplacementdata = {}
						part_position = currentpos
						part_duration = endpoint
						print(str(part_position) + ' ' + str(min(part_duration,remainingduration)))
						newplacementdata['position'] = trackposition + part_position
						newplacementdata['notelist'] = tracknotelist
						newplacements.append(newplacementdata)
						remainingduration -= endpoint 
						currentpos += endpoint
				else:
					newplacements.append(placementdata)
			else:
				newplacements.append(placementdata)
		trackdata['placements'] = newplacements
