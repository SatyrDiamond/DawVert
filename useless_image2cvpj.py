from PIL import Image
import json

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("cvpj")
args = parser.parse_args()

image = Image.open(args.image)
pixels = image.load()
width, height = image.size

if height > 30:
	print("image must be 30 pix high")
	exit()

tracks = []
for currentheight in range(height):
	placements = []
	for currentwidth in range(width):
		placement = {}
		color = image.getpixel((currentwidth, currentheight))
		placement['color'] = [color[0]/255,color[1]/255,color[2]/255]
		placement['position'] = currentwidth*4
		placement['notelist'] = [{'key': 0,'position': 0.25,'pan': 0.0,'duration': 0.1,'vol': 1.0}]
		placements.append(placement)
	trackdata_json = {}
	trackdata_json['type'] = "instrument"
	trackdata_json['name'] = "lol"
	instrumentdata_json = {}
	instrumentdata_json['plugin'] = "none"
	trackdata_json['instrumentdata'] = instrumentdata_json
	trackdata_json['notelist'] = []
	trackdata_json['vol'] = 1
	trackdata_json['placements'] = placements
	tracks.append(trackdata_json)

json_root = {}
json_root['mastervol'] = 1.0
json_root['timesig_numerator'] = 4
json_root['timesig_denominator'] = 4
json_root['bpm'] = 140
json_root['tracks'] = tracks

with open(args.cvpj + '.cvpj', 'w') as outfile:
    outfile.write(json.dumps(json_root, indent=2))

