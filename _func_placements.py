import json
import _func_notemod

def removewarping(song):
	for trackdata in song['tracks']:
		#print(trackdata['name'])
		if trackdata['type'] == 'instrument':
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
							trim_duration = min(part_duration,remainingduration)
							print(str(part_position) + ' ' + str(trim_duration))
							if trim_duration > 0:
								newplacementdata['position'] = trackposition + part_position
								newplacementdata['notelist'] = _func_notemod.trim(tracknotelist, trim_duration)
								newplacements.append(newplacementdata)
							remainingduration -= endpoint 
							currentpos += endpoint
					else:
						newplacements.append(placementdata)
				else:
					newplacements.append(placementdata)
			trackdata['placements'] = newplacements
