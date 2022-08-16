from io import BytesIO

import json
import _func_riff
import struct
import os.path

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("flm")
parser.add_argument("cvpj")
args = parser.parse_args()

samplepath = os.path.dirname(args.flm)

def parse_evn2_notelist(evn2bytes):
	notelistdata = BytesIO()
	notelistdata.write(evn2bytes)
	fileobject.seek(0,2)
	notelistdata_filesize = notelistdata.tell()
	notelistdata.seek(0)
	something = int.from_bytes(notelistdata.read(2), "little")
	notelist = []
	while notelistdata.tell() < notelistdata_filesize:
		notejson = {}
		notejson['position'] = int.from_bytes(notelistdata.read(4), "little")/128
		notejson['duration'] = struct.unpack('d', notelistdata.read(8))[0]
		notejson['key'] = int.from_bytes(notelistdata.read(1), "little") - 72
		notelistdata.read(1)
		notejson['vol'] = int.from_bytes(notelistdata.read(1), "little")/255
		notejson['pan'] = 0.0
		notelistdata.read(4)
		notelist.append(notejson)
	#for note in notelist:
	#	print(str(note))
	return notelist

def parse_evnt_notelist(evn2bytes):
	notelistdata = BytesIO()
	notelistdata.write(evn2bytes)
	fileobject.seek(0,2)
	notelistdata_filesize = notelistdata.tell()
	notelistdata.seek(0)
	notelist = []
	while notelistdata.tell() < notelistdata_filesize:
		notejson = {}
		notejson['position'] = int.from_bytes(notelistdata.read(4), "little")/128
		notejson['duration'] = struct.unpack('d', notelistdata.read(8))[0]
		notejson['key'] = int.from_bytes(notelistdata.read(1), "little") - 72
		notelistdata.read(1)
		notejson['vol'] = int.from_bytes(notelistdata.read(1), "little")/255
		notejson['pan'] = 0.0
		notelistdata.read(3)
		notelist.append(notejson)
	#for note in notelist:
	#	print(str(note))
	return notelist

fileobject = open(args.flm, 'rb')
fileobject.seek(0,2)
filesize = fileobject.tell()
fileobject.seek(0)
headername = fileobject.read(4)

riffobjects = _func_riff.readriffdata(fileobject, 4)

tracklist = []

for riffobject in riffobjects:
	if riffobject[0] == b'HEAD':
		headerdata = BytesIO()
		headerdata.write(riffobject[1])
		headerdata.seek(8)
		songname = headerdata.read(256).split(b'\x00')[0].decode("utf-8")
		bpm = struct.unpack('d', headerdata.read(8))[0]

	if riffobject[0] == b'CHNL':
		chnldata = _func_riff.readriffdata(riffobject[1],8)
		placements = []
		trackdata_json = {}
		for chnlobj in chnldata:
			if chnlobj[0] == b'CHHD':
				riffobjects_chhd = chnlobj[1]
				TrackName = riffobjects_chhd.split(b'\x00' * 1)[0].decode("utf-8")
				print('Track Name: ' + TrackName)
				trackdata_json['type'] = "instrument"
				trackdata_json['name'] = TrackName
				trackdata_json['vol'] = 1.0
				trackdata_json['pan'] = 0.0
				trackdata_json['muted'] = 0
				instrumentdata_json = {}
				instrumentdata_json['plugin'] = "none"
				trackdata_json['instrumentdata'] = instrumentdata_json
				plugindata_json = {}
				trackdata_json['plugindata'] = plugindata_json
			if chnlobj[0] == b'TRKH':
				trkhdata = _func_riff.readriffdata(chnlobj[1],0)
				for trkhobj in trkhdata:
					#print(str(trkhobj[0])+ " " + str(len(trkhobj[1])))
					if trkhobj[0] == b'DESc':
						TrackType = trkhobj[1][0]
					if trkhobj[0] == b'CLIP':
						clipobject = _func_riff.bytearray2BytesIO(trkhobj[1])
						clipobject.seek(0)
						notelist_position = int.from_bytes(clipobject.read(4), "little")/128
						riff_clip_inside = _func_riff.readriffdata(clipobject,8)
						placement_json = {}
						for riff_clip_inside_part in riff_clip_inside:
							if TrackType == 0:
								if riff_clip_inside_part[0] == b'CLHd':
									if riff_clip_inside_part[1][0:8] == riff_clip_inside_part[1][8:16] != 0:
										placement_json['noteloop'] = {}
										placement_json['noteloop']['duration'] = struct.unpack('d', riff_clip_inside_part[1][0:8])[0]
										placement_json['noteloop']['endpoint'] = struct.unpack('d', riff_clip_inside_part[1][8:16])[0]
										placement_json['noteloop']['startpoint'] = struct.unpack('d', riff_clip_inside_part[1][16:24])[0]
								if riff_clip_inside_part[0] == b'EVN2':
									placement_json['position'] = notelist_position
									placement_json['notelist'] = parse_evn2_notelist(riff_clip_inside_part[1])
								if riff_clip_inside_part[0] == b'EVNT':
									placement_json['position'] = notelist_position
									placement_json['notelist'] = parse_evnt_notelist(riff_clip_inside_part[1])
						if placement_json != {}:
							placements.append(placement_json)
		if TrackType == 0:
			trackdata_json['type'] = "instrument"
		if TrackType == 2:
			trackdata_json['type'] = "audio"
		trackdata_json['placements'] = placements
		tracklist.append(trackdata_json)


json_root = {}
json_root['mastervol'] = 1.0
json_root['timesig_numerator'] = 4
json_root['timesig_denominator'] = 4
json_root['bpm'] = bpm
json_root['title'] = songname
json_root['tracks'] = tracklist

with open(args.cvpj + '.cvpj', 'w') as outfile:
    outfile.write(json.dumps(json_root, indent=2))
