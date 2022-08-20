# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import math
import json
import _func_tracker
import _func_noteconv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("s3m")
parser.add_argument("cvpjm")
parser.add_argument("samplefolder")
args = parser.parse_args()

modfile = open(args.s3m, 'rb')
name = modfile.read(28).decode().rstrip('\x00')
sig1 = modfile.read(1)
type = modfile.read(1)
reserved = int.from_bytes(modfile.read(2), "little")
orderCount = int.from_bytes(modfile.read(2), "little")
instrumentCount = int.from_bytes(modfile.read(2), "little")
patternPtrCount = int.from_bytes(modfile.read(2), "little")
flags = modfile.read(2)
trackerVersion = modfile.read(2)
sampleType = int.from_bytes(modfile.read(2), "little")
sig2 = modfile.read(4)
globalVolume = int.from_bytes(modfile.read(1), "little")
initialSpeed = int.from_bytes(modfile.read(1), "little")
initialTempo = int.from_bytes(modfile.read(1), "little")
masterVolume = modfile.read(1)
ultraClickRemoval = int.from_bytes(modfile.read(1), "little")
defaultPan = modfile.read(1)
reserved2 = modfile.read(8)
ptrSpecial = int.from_bytes(modfile.read(2), "little")
channelSettings = modfile.read(32)

orderListBytes = modfile.read(orderCount)
orderList = []
for orderListByte in orderListBytes:
	orderList.append(orderListByte)

while 255 in orderList:
	orderList.remove(255)

print(orderList)

ptrInstruments = []
for _ in range(instrumentCount):
	ptrInstruments.append(int.from_bytes(modfile.read(2), "little")*16)

ptrPatterns = []
for _ in range(patternPtrCount):
	ptrPatterns.append(int.from_bytes(modfile.read(2), "little")*16)

instrumentjson_table = []
outputfx = []
outputtracks = []

instrumentcount = 0
for ptrInstrument in ptrInstruments:
	fxchannel = {}
	modfile.seek(ptrInstrument)
	instrumentjson = {}
	instrumenttype = int.from_bytes(modfile.read(1), "little")
	instrumentfilenamebytes = modfile.read(12)
	if instrumenttype == 0 or instrumenttype == 1:
		instrument_ptrDataH = int.from_bytes(modfile.read(1), "little")
		instrument_ptrDataL = int.from_bytes(modfile.read(2), "little")
		instrument_length = int.from_bytes(modfile.read(4), "little")
		instrument_loopStart = int.from_bytes(modfile.read(4), "little")
		instrument_loopEnd = int.from_bytes(modfile.read(4), "little")
		instrumentjson['volume'] = int.from_bytes(modfile.read(1), "little")/64
		instrument_reserved = int.from_bytes(modfile.read(1), "little")
		instrument_pack = int.from_bytes(modfile.read(1), "little")
		instrument_flags = int.from_bytes(modfile.read(1), "little")
		instrument_c2spd = int.from_bytes(modfile.read(4), "little")
		instrument_internal = modfile.read(12)
		instrument_namebytes = modfile.read(28)
		instrument_sig = modfile.read(4)
	try:
		instrument_name = instrumentfilenamebytes.split(b'\x00' * 1)[0].decode("utf-8")
	except:
		instrument_name = str(instrumentcount)
	try:
		fxchannel['name'] = instrument_namebytes.split(b'\x00' * 1)[0].decode("utf-8")
	except:
		fxchannel['name'] = ''
	instrumentjson['id'] = instrumentcount+1
	instrumentjson['name'] = instrument_name
	instrumentjson['fxrack_channel'] = instrumentcount+1
	instrumentjson['volume'] = 0.3
	instrumentjson_inst = {}
	instrumentjson_inst['plugin'] = "sampler"
	instrumentjson_inst['basenote'] = 60
	instrumentjson_inst['pitch'] = 0
	instrumentjson_inst['usemasterpitch'] = 1
	instrumentjson_inst_plugindata = {}
	instrumentjson_inst_plugindata['file'] = args.samplefolder + '/' + str(instrumentcount+1).zfill(2) + '.wav'
	instrumentjson_inst['plugindata'] = instrumentjson_inst_plugindata
	instrumentjson['instrumentdata'] = instrumentjson_inst
	instrumentjson_table.append(instrumentjson)
	fxchannel['num'] = instrumentcount+1
	outputfx.append(fxchannel)
	instrumentcount += 1

patterntable_all = []
for ptrPattern in ptrPatterns:
	patterntable_single = []
	if ptrPattern != 0:
		modfile.seek(ptrPattern)
		pattern_packed_len = int.from_bytes(modfile.read(2), "little")
		firstrow = 1
		for _ in range(64):
			pattern_done = 0
			pattern_row_local = []
			for _ in range(32):
				pattern_row_local.append([None, None, {}, {}])
			pattern_row = [pattern_row_local, {}]
			while pattern_done == 0:
				packed_what = bin(int.from_bytes(modfile.read(1), "little"))[2:].zfill(8)
				if int(packed_what, 2) == 0:
					pattern_done = 1
				else:
					packed_what_command_info = int(packed_what[0], 2)
					packed_what_volume = int(packed_what[1], 2)
					packed_what_note_instrument = int(packed_what[2], 2)
					packed_what_channel = int(packed_what[3:8], 2)

					packed_note = None
					packed_instrument = None
					packed_volume = None
					packed_command = None
					packed_info = None

					if packed_what_note_instrument == 1:
						packed_note = int.from_bytes(modfile.read(1), "little")

					if packed_what_note_instrument == 1:
						packed_instrument = int.from_bytes(modfile.read(1), "little")
						if packed_instrument == 0:
							packed_instrument = None
					if packed_what_volume == 1:
						packed_volume = int.from_bytes(modfile.read(1), "little")

					if packed_what_command_info == 1:
						packed_command = int.from_bytes(modfile.read(1), "little")
					if packed_what_command_info == 1:
						packed_info = int.from_bytes(modfile.read(1), "little")
					if packed_note != None:
						packed_note = bin(packed_note)[2:].zfill(8)
						packed_note_oct = int(packed_note[0:4], 2)-4
						packed_note_tone = int(packed_note[4:8], 2)
						final_note = packed_note_oct*12 + packed_note_tone
						pattern_row[0][packed_what_channel][0] = final_note
					if packed_instrument != None:
						pattern_row[0][packed_what_channel][1] = packed_instrument
					if packed_volume != None:
						pattern_row[0][packed_what_channel][2]['volume'] = packed_volume/64
					else:
						pattern_row[0][packed_what_channel][2]['volume'] = 1.0
					if firstrow == 1:
						pattern_row[0][packed_what_channel][3]['firstrow'] = 1
						pattern_row[1]['firstrow'] = 1

					if packed_what_command_info == 1 and packed_command == 1:
						pattern_row[0][packed_what_channel][3]['tracker_speed'] = packed_info
						pattern_row[1]['tracker_speed'] = packed_info

					#print(packed_what_command_info, packed_what_volume, packed_what_note_instrument, packed_what_channel)
			firstrow = 0
			patterntable_single.append(pattern_row)
	patterntable_all.append(patterntable_single)

for current_channelnum in range(31):
	_func_noteconv.timednotes2notelistplacement_track_start()
	channelsong = _func_tracker.entire_song_channel(patterntable_all,current_channelnum,orderList)
	timednotes = _func_tracker.convertchannel2timednotes(channelsong,initialSpeed)
	singletrack = {}
	singletrack['name'] = "Channel " + str(current_channelnum+1)
	singletrack['muted'] = 0
	singletrack['placements'] = _func_noteconv.timednotes2notelistplacement_parse_timednotes(timednotes)
	outputtracks.append(singletrack)


mainjson = {}
mainjson['mastervol'] = 1.0
mainjson['masterpitch'] = 0.0
mainjson['timesig_numerator'] = 4
mainjson['timesig_denominator'] = 4
mainjson['bpm'] = initialTempo
mainjson['multiple_instruments_in_single_track'] = 1
mainjson['tracks'] = outputtracks
mainjson['fxrack'] = outputfx
mainjson['instruments'] = instrumentjson_table

with open(args.cvpjm + '.cvpjm', 'w') as f:
    json.dump(mainjson, f, indent=2)
