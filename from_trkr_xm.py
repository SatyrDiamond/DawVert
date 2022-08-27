# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import math
import json
import _func_tracker
import _func_noteconv
import argparse
from io import BytesIO


def parse_xm_cell(databytes):
	cell_note = None
	cell_instrument = None
	cell_vol = None
	cell_effect = None
	cell_param = None

	packed_first = int.from_bytes(databytes.read(1), "little")
	packed_flags = bin(packed_first)[2:].zfill(8)

	packed_note = int(packed_flags[7], 2) 
	packed_instrument = int(packed_flags[6], 2)
	packed_vol = int(packed_flags[5], 2)
	packed_effect = int(packed_flags[4], 2)
	packed_param = int(packed_flags[3], 2)
	packed_msb = int(packed_flags[0], 2)
	if packed_msb == 1:
		if packed_note == 1:
			cell_note = int.from_bytes(databytes.read(1), "little")
		if packed_instrument == 1:
			cell_instrument = int.from_bytes(databytes.read(1), "little")
		if packed_vol == 1:
			cell_vol = int.from_bytes(databytes.read(1), "little")
		if packed_effect == 1:
			cell_effect = int.from_bytes(databytes.read(1), "little")
		if packed_param == 1:
			cell_param = int.from_bytes(databytes.read(1), "little")
	else:
		cell_note = packed_first
		cell_instrument = int.from_bytes(databytes.read(1), "little")
		cell_vol = int.from_bytes(databytes.read(1), "little")
		cell_effect = int.from_bytes(databytes.read(1), "little")
		cell_param = int.from_bytes(databytes.read(1), "little")

	output_note = cell_note
	if cell_note != None:
		if cell_note == 97:
			output_note = 'Off'
		else:
			output_note = cell_note - 49
	output_inst = cell_instrument
	output_param = {}
	output_extra = {}

	#print(cell_note,cell_instrument,cell_vol,cell_effect,cell_param)

	if cell_param != None:
		if cell_effect == 15:
			if 31 >= cell_param:
				output_extra['tracker_speed'] = cell_param

		if cell_effect == 8:
			if cell_param:
				output_param['pan'] = ((cell_param/255)-0.5)*2

		if cell_effect == 12:
			if cell_param:
				output_param['volume'] = (cell_param)/64

	if cell_vol != None:
		if 80 >= cell_vol >= 16:
			output_param['volume'] = (cell_vol-16)/64

	return [output_note, output_inst, output_param, output_extra]

def parse_xm_row(xmdata, numchannels,firstrow):
	table_row = []
	globaljson = {}
	for channel in range(numchannels):
		if firstrow == 1:
			globaljson['firstrow'] = 1
		celldata = parse_xm_cell(xmdata)
		rowdata_global = celldata[3]
		globaljson = rowdata_global | globaljson
		table_row.append(celldata)
	return [table_row, globaljson]

def parse_xm_row_none(numchannels,firstrow):
	table_row = []
	globaljson = {}
	for channel in range(numchannels):
		if firstrow == 1:
			globaljson['firstrow'] = 1
		celldata = [None, None, {}, {}]
		table_row.append(celldata)
	return [table_row, globaljson]




parser = argparse.ArgumentParser()
parser.add_argument("xm")
parser.add_argument("cvpjm")
args = parser.parse_args()

xmfile = open(args.xm, 'rb')

header_magic = xmfile.read(17)
if header_magic != b'Extended Module: ':
	print('Not an XM File')
	exit()
header_songname = xmfile.read(20).split(b'\x00' * 1)[0].decode("utf-8")
print("Song Name: " + str(header_songname))
header_id = xmfile.read(1)
header_trackername = xmfile.read(20).split(b'\x00' * 1)[0].decode("utf-8")
print("Tracker Name: " + str(header_trackername))
header_trackerrevision_high = int.from_bytes(xmfile.read(1), "little")
header_trackerrevision_low = int.from_bytes(xmfile.read(1), "little")
print("Tracker Revision: " + str(header_trackerrevision_low) + "." + str(header_trackerrevision_high))
if header_trackerrevision_high != 4 and header_trackerrevision_low != 1: 
	print("Tracker Revision Not 1.4")
	exit()
header_headersize = int.from_bytes(xmfile.read(4), "little")
print("Header Size: " + str(header_headersize))
header_songlength_in_patterns = int.from_bytes(xmfile.read(2), "little")
print("songlength_in_patterns: " + str(header_songlength_in_patterns))
header_restart_position = int.from_bytes(xmfile.read(2), "little")
print("restart_position: " + str(header_restart_position))
header_number_of_channels = int.from_bytes(xmfile.read(2), "little")
print("number_of_channels: " + str(header_number_of_channels))
header_number_of_patterns = int.from_bytes(xmfile.read(2), "little")
print("number_of_patterns: " + str(header_number_of_patterns))
header_number_of_instruments = int.from_bytes(xmfile.read(2), "little")
print("number_of_instruments: " + str(header_number_of_instruments))
header_flags = int.from_bytes(xmfile.read(2), "little")
print("flags: " + str(header_flags))
header_speed = int.from_bytes(xmfile.read(2), "little")
print("speed: " + str(header_speed))
header_bpm = int.from_bytes(xmfile.read(2), "little")
print("bpm: " + str(header_bpm))
order_list = []
for number in range(256):
	ordernum = int.from_bytes(xmfile.read(1), "little")
	if number < header_songlength_in_patterns:
		order_list.append(ordernum)
print(order_list)

xmdata_patterns = []

for header_number_of_pattern in range(header_number_of_patterns):
	pattern_headerlength = int.from_bytes(xmfile.read(4), "little")
	pattern_packingtype = int.from_bytes(xmfile.read(1), "little")
	if pattern_packingtype != 0:
		print("Stopped, not a standard .XM file (possably saved with OpenMPT)")
		exit()
	pattern_number_of_rows = int.from_bytes(xmfile.read(2), "little")
	if pattern_packingtype > 256:
		print("Stopped, not a standard .XM file (possably saved with OpenMPT)")
		exit()
	pattern_packed_data_size = int.from_bytes(xmfile.read(2), "little")
	currentdatapos = xmfile.tell()
	xmdata_packeddata = None
	if pattern_packed_data_size != 0:
		xmdata_packeddata = xmfile.read(pattern_packed_data_size)
	xmdata_patterns.append([pattern_headerlength, pattern_number_of_rows, xmdata_packeddata])

outputfx = []
instrumentjson_table = []
instrumentcount = 0

for instnumber in range(header_number_of_instruments):
	fxchannel = {}
	instrumentjson = {}
	instrumentjson['id'] = instrumentcount+1
	instrumentjson['name'] = str(instrumentcount+1)
	instrumentjson['volume'] = 0.3
	instrumentjson['fxrack_channel'] = instrumentcount+1
	instrumentjson['type'] = 'instrument'
	instrumentjson_inst = {}
	instrumentjson_inst['plugin'] = "none"
	instrumentjson_inst['basenote'] = 60
	instrumentjson_inst['pitch'] = 0
	instrumentjson_inst['usemasterpitch'] = 1
	instrumentjson['instrumentdata'] = instrumentjson_inst
	fxchannel['name'] = str(instrumentcount+1)
	fxchannel['num'] = instrumentcount+1
	outputfx.append(fxchannel)
	instrumentjson_table.append(instrumentjson)
	instrumentcount += 1


patterntable_all = []

for xmdata_pattern in xmdata_patterns:
	xmdata_patterndata = BytesIO()
	if xmdata_pattern[2] != None:
		xmdata_patterndata.write(xmdata_pattern[2])
		xmdata_patterndata.seek(0)
		patterntable_single = []
		pattern_firstrow = 1
		for row in range(xmdata_pattern[1]):
			patterntable_single.append(parse_xm_row(xmdata_patterndata, header_number_of_channels, pattern_firstrow))
			pattern_firstrow = 0
		patterntable_all.append(patterntable_single)
	else:
		patterntable_single = []
		pattern_firstrow = 1
		for row in range(xmdata_pattern[1]):
			patterntable_single.append(parse_xm_row_none(header_number_of_channels, pattern_firstrow))
			pattern_firstrow = 0
		patterntable_all.append(patterntable_single)

outputtracks = []
for current_channelnum in range(header_number_of_channels):
	print('Channel ' + str(current_channelnum+1) + ': ', end='')
	_func_noteconv.timednotes2notelistplacement_track_start()
	channelsong = _func_tracker.entire_song_channel(patterntable_all,current_channelnum,order_list)
	timednotes = _func_tracker.convertchannel2timednotes(channelsong,header_speed)
	placements = _func_noteconv.timednotes2notelistplacement_parse_timednotes(timednotes)
	singletrack = {}
	singletrack['name'] = "Channel " + str(current_channelnum+1)
	singletrack['muted'] = 0
	print(str(len(placements)) + ' Placements')
	singletrack['placements'] = placements
	outputtracks.append(singletrack)


mainjson = {}
mainjson['mastervol'] = 1.0
mainjson['masterpitch'] = 0.0
mainjson['timesig_numerator'] = 4
mainjson['timesig_denominator'] = 6
mainjson['title'] = header_songname
mainjson['bpm'] = header_bpm
mainjson['multiple_instruments_in_single_track'] = 1
mainjson['tracks'] = outputtracks
mainjson['fxrack'] = outputfx
mainjson['instruments'] = instrumentjson_table

with open(args.cvpjm + '.cvpjm', 'w') as f:
    json.dump(mainjson, f, indent=2)
