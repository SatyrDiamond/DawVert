# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json
import struct
import math
from functions import data_bytes
from objects import midi_in

def calc_gatetime(bio_mmf_Mtsq):
	out_duration = 0
	t_durgate = []
	t_durgate_value = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
	t_durgate.append(t_durgate_value)
	if bool(t_durgate_value & 0b10000000) == True: 
		t_durgate_value = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
		t_durgate.append(t_durgate_value)
		if bool(t_durgate_value & 0b10000000) == True: 
			t_durgate_value = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			t_durgate.append(t_durgate_value)

	shift = 0

	t_durgate.reverse()

	for note_durbyte in t_durgate:
		out_duration += (note_durbyte & 0b01111111) << shift
		shift += 7

	return out_duration

def noteresize(value):
	return value*8

def parse_ma3_Mtsq(Mtsqdata, tb_ms, convproj_obj):
	bio_mmf_Mtsq = data_bytes.to_bytesio(Mtsqdata)
	bio_mmf_Mtsq_size = len(Mtsqdata)
	notecount = 0
	#print('size', bio_mmf_Mtsq_size)
	#print('	  1ST 2ND | CH#  CMD')

	midiobj = midi_in.midi_in()
	midiobj.song_start(16, int(tb_ms*(math.pi*10000)), 120, [4,4])

	midicmds = []

	while bio_mmf_Mtsq.tell() < bio_mmf_Mtsq_size:
		resttime = calc_gatetime(bio_mmf_Mtsq)
		midicmds.append(['rest', resttime])

		#print(str(basepos).ljust(5), end=' ')

		firstbyte = data_bytes.splitbyte(int.from_bytes(bio_mmf_Mtsq.read(1), "big"))
		#print(str(firstbyte[0]).ljust(3), end=' ')

		if firstbyte[0] == 0:
			null_durgate = calc_gatetime(bio_mmf_Mtsq)
			#print('|	  NULL	', null_durgate)

		elif firstbyte[0] == 8:
			note_note = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			note_durgate = calc_gatetime(bio_mmf_Mtsq)
			#print('| '+str(firstbyte[1]).ljust(4), 'NOTE	', str(note_note).ljust(4), '	 dur ', note_durgate)
			midicmds.append(['note', firstbyte[1], note_note, 127, note_durgate])

		elif firstbyte[0] == 9:
			note_note = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			note_vol = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			note_durgate = calc_gatetime(bio_mmf_Mtsq)
			#print('| '+str(firstbyte[1]).ljust(4), 'NOTE+V  ', str(note_note).ljust(4), str(note_vol).ljust(4), 'dur ', note_durgate)
			midicmds.append(['note', firstbyte[1], note_note, note_vol, note_durgate])

		elif firstbyte[0] == 11:
			cntltype = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			cntldata = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			#print('| '+str(firstbyte[1]).ljust(4), 'CONTROL ', str(cntltype).ljust(4), str(cntldata).ljust(4))
			midicmds.append(['control_change', firstbyte[1], cntltype, cntldata])

		elif firstbyte[0] == 12:
			prognumber = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			#print('| '+str(firstbyte[1]).ljust(4), 'PROGRAM ', prognumber)
			midicmds.append(['program_change', firstbyte[1], prognumber])

		elif firstbyte[0] == 14:
			lsbpitch = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			msbpitch = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			#print('| '+str(firstbyte[1]).ljust(4), 'PITCH   ', str(lsbpitch).ljust(4), str(msbpitch).ljust(4))

		elif firstbyte[0] == 15 and firstbyte[1] == 0:
			sysexsize = int.from_bytes(bio_mmf_Mtsq.read(1), "big")
			sysexdata = bio_mmf_Mtsq.read(sysexsize)
			#print('| '+str(firstbyte[1]).ljust(4), 'SYSEX   ', sysexdata.hex())
			midicmds.append(['sysex', sysexdata])

		elif firstbyte[0] == 15 and firstbyte[1] == 15:
			pass
			#print('| '+str(firstbyte[1]).ljust(4), 'NOP	 ')

		else:
			print('Unknown Command', firstbyte[0], "0x%X" % firstbyte[0])
			exit()

	midiobj.add_track(0, midicmds)

	usedinsts = midiobj.song_end(convproj_obj)

	for usedinst in usedinsts:
		if usedinst:
			ui = usedinst[0]
			instid = '_'.join([str(ui[0]), str(ui[1]), str(ui[2]), str(ui[3])])

			if ui[2] == 124: 
				inst_obj = convproj_obj.add_instrument(instid)
				inst_obj.visual.name = 'MA-3 User #'+str(ui[1])
				inst_obj.visual.color = [0.3,0.3,0.3]
				inst_obj.fxrack_channel = ui[0]+1

			elif ui[2] == 125: 
				inst_obj = convproj_obj.add_instrument(instid)
				inst_obj.visual.name = 'MA-3 PCM #'+str(ui[1])
				inst_obj.visual.color = [0.3,0.3,0.3]
				inst_obj.fxrack_channel = ui[0]+1

	return True

def parse_ma3_track(datain, tracknum, convproj_obj):
	bio_mmf_track = data_bytes.to_bytesio(datain)
	trk_type_format, trk_type_seq, trk_tb_d, trk_tb_g = struct.unpack("BBBB", bio_mmf_track.read(4))
	if trk_tb_d == 2: tb_ms = 0.004
	if trk_tb_d == 3: tb_ms = 0.005
	if trk_tb_d == 16: tb_ms = 0.010
	if trk_tb_d == 17: tb_ms = 0.020
	if trk_tb_d == 18: tb_ms = 0.040
	if trk_tb_d == 19: tb_ms = 0.050
	print('[input-smaf] TimeBase MS:', tb_ms*1000)
	trk_chanstat = struct.unpack("IIII", bio_mmf_track.read(16))
	#print(trk_type_format, trk_type_seq, trk_tb_d, trk_tb_g, trk_chanstat)
	trk_chunks = data_bytes.iff_read_big(bio_mmf_track.read(), 0)
	is_found = None
	for trk_chunk in trk_chunks:
		print('[input-smaf] MTR CHUNK:',trk_chunk[0])
		#if trk_chunk[0] == b'Mtsu':
		#	print(trk_chunk[1])
		#	exit()
		if trk_chunk[0] == b'Mtsq':
			is_found = parse_ma3_Mtsq(trk_chunk[1], tb_ms, convproj_obj)
	if is_found == None:
		print('[input-smaf] No Mtsq found.')
		exit()


class input_mmf(plugin_input.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'mmf'
	def gettype(self): return 'rm'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Mobile Music File'
		dawinfo_obj.file_ext = 'mmf'
		dawinfo_obj.fxtype = 'rack'
		dawinfo_obj.fxrack_params = ['vol']
		dawinfo_obj.auto_types = ['nopl_ticks']
		dawinfo_obj.track_nopl = True
		dawinfo_obj.plugin_included = ['midi']
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(4)
		if bytesdata == b'MMMD': return True
		else: return False
		bytestream.seek(0)
	def parse(self, convproj_obj, input_file, dv_config):
		mmf_f_stream = open(input_file, 'rb')
		mmf_chunks_main = data_bytes.iff_read(mmf_f_stream.read(), 0)
		if mmf_chunks_main[0][0] != b'MMMD':
			print('[input-smaf] Not a SMAF File.'); exit()

		convproj_obj.type = 'rm'

		mmf_chunks_ins = data_bytes.iff_read(mmf_chunks_main[0][1], 0)

		cvpj_l = {}

		trackparsed = False
		for mmf_chunk in mmf_chunks_ins:
			if mmf_chunk[0] == b'CNTI':
				bio_mmf_cnti = data_bytes.to_bytesio(mmf_chunk[1])
				mmf_cnti_class, mmf_cnti_type, mmf_cnti_codetype, mmf_cnti_status, mmf_cnti_counts = struct.unpack("BBBBB", bio_mmf_cnti.read(5))
				mmf_cnti_chunks = data_bytes.iff_read_big(bio_mmf_cnti, 5)
				for mmf_cnti_chunk in mmf_cnti_chunks:
					print('[input-smaf] CNTI CHUNK:', mmf_cnti_chunk[0])
					#if mmf_cnti_chunk[0] == b'OPDA':
					#	print(mmf_cnti_chunk[1])
					if mmf_cnti_chunk[0][:3] == b'MTR':
						mmf_tracknum = int.from_bytes(mmf_cnti_chunk[0][3:], "big")
						#print('track num', mmf_tracknum)
						if mmf_tracknum in range(1, 4):
							print('[input-smaf] Format: MA1/2 is not supported')
							exit()
						if mmf_tracknum in range(5, 8):
							print('[input-smaf] Format: MA3')
							trackparsed = True
							cvpj_l = parse_ma3_track(mmf_cnti_chunk[1], 3, convproj_obj)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', 120, 'float')