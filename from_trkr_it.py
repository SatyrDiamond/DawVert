# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import math
import json
import _func_tracker
import _func_noteconv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("it")
parser.add_argument("cvpjm")
args = parser.parse_args()

it_file = open(args.it, 'rb')

header_magic = it_file.read(4)
if header_magic != b'IMPM':
	print('Not an IT File')
	exit()

header_songname = it_file.read(26).split(b'\x00' * 1)[0].decode("utf-8")
print("Song Name: " + str(header_songname))
header_hilight_minor = it_file.read(1)
header_hilight_major = it_file.read(1)
header_ordnum = int.from_bytes(it_file.read(2), "little")
header_insnum = int.from_bytes(it_file.read(2), "little")
header_smpnum = int.from_bytes(it_file.read(2), "little")
header_patnum = int.from_bytes(it_file.read(2), "little")

header_cwtv = int.from_bytes(it_file.read(2), "little")
header_cmwt = int.from_bytes(it_file.read(2), "little")

header_flags = it_file.read(2)
header_special = it_file.read(2)
header_globalvol = int.from_bytes(it_file.read(1), "little")
header_mv = int.from_bytes(it_file.read(1), "little")
header_speed = int.from_bytes(it_file.read(1), "little")
header_tempo = int.from_bytes(it_file.read(1), "little")
header_sep = int.from_bytes(it_file.read(1), "little")
header_pwd = int.from_bytes(it_file.read(1), "little")
header_msglength = int.from_bytes(it_file.read(2), "little")
header_msgoffset = int.from_bytes(it_file.read(4), "little")
header_reserved = int.from_bytes(it_file.read(4), "little")
chnpan = []
for _ in range(64):
	chnpan.append(int.from_bytes(it_file.read(1), "little"))
chnvol = []
for _ in range(64):
	chnvol.append(int.from_bytes(it_file.read(1), "little"))
orders = []
for _ in range(header_ordnum):
	orders.append(int.from_bytes(it_file.read(1), "little"))

offset_instruments = []
for _ in range(header_insnum):
	offset_instruments.append(int.from_bytes(it_file.read(4), "little"))

offset_sampleheaders = []
for _ in range(header_smpnum):
	offset_sampleheaders.append(int.from_bytes(it_file.read(4), "little"))

offset_patterns = []
for _ in range(header_patnum):
	offset_patterns.append(int.from_bytes(it_file.read(4), "little"))


outputfx = []
instrumentjson_table = []
instrumentcount = 0

numofdummy_inst = len(offset_instruments)
if numofdummy_inst == 0:
	numofdummy_inst = len(offset_sampleheaders)

for instnumber in range(numofdummy_inst):
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


patterncount = 1
patterntable_all = []
for offset_pattern in offset_patterns:
	print("Pattern: " + str(patterncount))
	patterntable_single = []
	if offset_pattern != 0:
		print('--- offset: ' + str(offset_pattern))
		it_file.seek(offset_pattern)
		pattern_length = int.from_bytes(it_file.read(2), "little")
		print('Length: ' + str(pattern_length))
		pattern_rows = int.from_bytes(it_file.read(2), "little")
		print('Rows: ' + str(pattern_rows))
		it_file.read(4)
		firstrow = 1
		rowcount = 0
		table_lastnote = []
		for _ in range(64):
			table_lastnote.append(None)
		table_lastinstrument = []
		for _ in range(64):
			table_lastinstrument.append(None)
		table_lastvolpan = []
		for _ in range(64):
			table_lastvolpan.append(None)
		table_lastcommand = []
		for _ in range(64):
			table_lastcommand.append([None, None])
		table_previousmaskvariable = []
		for _ in range(64):
			table_previousmaskvariable.append(None)
		for _ in range(pattern_rows):
			pattern_done = 0
			pattern_row_local = []
			for _ in range(64):
				pattern_row_local.append([None, None, {}, {}])
			pattern_row = [pattern_row_local, {}]
			while pattern_done == 0:
				channelvariable = bin(int.from_bytes(it_file.read(1), "little"))[2:].zfill(8)
				cell_previous_maskvariable = int(channelvariable[0:1], 2)
				cell_channel = int(channelvariable[1:8], 2)
				if int(channelvariable, 2) == 0:
					pattern_done = 1
				else:
					#print('ch:' + str(cell_channel) + '|', end=' ')
					if cell_previous_maskvariable == 1:
						maskvariable = bin(int.from_bytes(it_file.read(1), "little"))[2:].zfill(8)
						table_previousmaskvariable[cell_channel] = maskvariable
					else:
						maskvariable = table_previousmaskvariable[cell_channel]
					maskvariable_note = int(maskvariable[7], 2) 
					maskvariable_instrument = int(maskvariable[6], 2)
					maskvariable_volpan = int(maskvariable[5], 2)
					maskvariable_command = int(maskvariable[4], 2)
					maskvariable_last_note = int(maskvariable[3], 2)
					maskvariable_last_instrument = int(maskvariable[2], 2)
					maskvariable_last_volpan = int(maskvariable[1], 2)
					maskvariable_last_command = int(maskvariable[0], 2)

					cell_note = None
					cell_instrument = None
					cell_volpan = None
					cell_commandtype = None
					cell_commandnum = None

					if maskvariable_note == 1:
						cell_note = int.from_bytes(it_file.read(1), "little")
						table_lastnote[cell_channel] = cell_note
						#print('n=' + str(cell_note), end=' ')
					if maskvariable_instrument == 1:
						cell_instrument = int.from_bytes(it_file.read(1), "little")
						table_lastinstrument[cell_channel] = cell_instrument
						#print('i=' + str(cell_instrument), end=' ')
					if maskvariable_volpan == 1:
						cell_volpan = int.from_bytes(it_file.read(1), "little")
						table_lastvolpan[cell_channel] = cell_volpan
						#print('vp=' + str(cell_volpan), end=' ')
					if maskvariable_command == 1:
						cell_commandtype = int.from_bytes(it_file.read(1), "little")
						cell_commandnum = int.from_bytes(it_file.read(1), "little")
						table_lastcommand[cell_channel] = [cell_commandtype, cell_commandnum]
						#print('cmdt=' + str(cell_commandtype), end=' ')
						#print('cmdn=' + str(cell_commandnum), end=' ')

					if maskvariable_last_note == 1:
						cell_note = table_lastnote[cell_channel]
						#print('n=' + str(cell_note), end=' ')
					if maskvariable_last_instrument == 1:
						cell_instrument = table_lastinstrument[cell_channel]
						#print('i=' + str(cell_instrument), end=' ')
					if maskvariable_last_volpan == 1:
						cell_volpan = table_lastvolpan[cell_channel]
						#print('vp=' + str(cell_volpan), end=' ')
					if maskvariable_last_command == 1:
						cell_commandtype = table_lastcommand[cell_channel][0]
						cell_commandnum = table_lastcommand[cell_channel][1]
						#print('cmdt=' + str(cell_commandtype), end=' ')
						#print('cmdn=' + str(cell_commandnum), end=' ')

					if cell_note != None:
						pattern_row[0][cell_channel][0] = cell_note - 48
					if cell_note == 254:
						pattern_row[0][cell_channel][0] = 'Cut'
					if cell_note == 255:
						pattern_row[0][cell_channel][0] = 'Off'
					if cell_note == 246:
						pattern_row[0][cell_channel][0] = 'Cut'
					if cell_instrument != None:
						pattern_row[0][cell_channel][1] = cell_instrument
					if firstrow == 1:
						pattern_row[1]['firstrow'] = 1
					rowcount += 1
			firstrow = 0
			patterntable_single.append(pattern_row)
	patterntable_all.append(patterntable_single)
	patterncount += 1

while 254 in orders:
	orders.remove(254)

while 255 in orders:
	orders.remove(255)
print("Order List: " + str(orders))

outputtracks = []
for current_channelnum in range(64):
	print('Channel ' + str(current_channelnum+1) + ': ', end='')
	_func_noteconv.timednotes2notelistplacement_track_start()
	channelsong = _func_tracker.entire_song_channel(patterntable_all,current_channelnum,orders)
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
mainjson['bpm'] = header_tempo
mainjson['multiple_instruments_in_single_track'] = 1
mainjson['tracks'] = outputtracks
mainjson['fxrack'] = outputfx
mainjson['instruments'] = instrumentjson_table

with open(args.cvpjm + '.cvpjm', 'w') as f:
    json.dump(mainjson, f, indent=2)
