import json

with open('proj.conv_otsn', 'r') as otsnfile:
	json_proj = json.loads(otsnfile.read())

for json_track in json_proj['tracks']: #position
	notelist = json_track['notelist']
	placements = {}
	placements['startat'] = 0
	placements['notelist'] = notelist
	json_track['placements'] = [placements]
	json_proj['datatype'] = 'otmn'
	del json_track['notelist']

with open('proj.conv_otmn', 'w') as outfile:
        outfile.write(json.dumps(json_proj, indent=2))
