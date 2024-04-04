# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct

def stream_decode(bio_org, org_numofnotes, maxchange, org_notelist, tnum):
	global cur_val
	for x in range(org_numofnotes):
		pre_val = bio_org.read(1)[0]
		if maxchange != None:
			if 0 <= pre_val <= maxchange: cur_val = pre_val
			org_notelist[x][tnum] = cur_val
		else:
			org_notelist[x][tnum] = pre_val

def stream_encode(invals):
	cur_val = -1
	for n, x in enumerate(invals):
		if cur_val == x: invals[n] = 255
		cur_val = x
	return invals

class orgyana_track:
	def __init__(self):
		self.pitch = 1000
		self.instrument = 0
		self.disable_sustaining_notes = 0
		self.number_of_notes = 0
		self.notes = []

class orgyana_project:
	def __init__(self):
		self.oldperc = False
		self.wait = 120
		self.stepsperbar = 4
		self.beatsperstep = 4
		self.loop_beginning = 0
		self.loop_end = 0
		self.tracks = [orgyana_track() for x in range(16)]

	def load_from_file(self, input_file):
		bio_org = open(input_file, 'rb')
		org_header = bio_org.read(4)
		self.oldperc = bio_org.read(2) == b'03'
		self.wait, self.stepsperbar, self.beatsperstep, self.loop_beginning, self.loop_end = struct.unpack('hbbii', bio_org.read(12))

		for n in range(16):
			org_track = self.tracks[n]
			org_track.pitch, org_track.instrument, org_track.disable_sustaining_notes, org_track.number_of_notes = struct.unpack('hbbh', bio_org.read(6))
			org_track.notes = [[0,0,0,0,0] for _ in range(org_track.number_of_notes)]

		for n in range(16):
			org_track = self.tracks[n]
			for x in range(org_track.number_of_notes): org_track.notes[x][0] = int.from_bytes(bio_org.read(4), "little") #position
			stream_decode(bio_org, org_track.number_of_notes, 95, org_track.notes, 1) #note
			stream_decode(bio_org, org_track.number_of_notes, 256, org_track.notes, 2) #duration
			stream_decode(bio_org, org_track.number_of_notes, 254, org_track.notes, 3) #vol
			stream_decode(bio_org, org_track.number_of_notes, 12, org_track.notes, 4) #pan

	def write(self):
		outbytes = b'Org-'+(b'03' if self.oldperc else b'02')
		outbytes += struct.pack('hbbii', self.wait, self.stepsperbar, self.beatsperstep, self.loop_beginning, self.loop_end)
		for n in range(16): 
			org_track = self.tracks[n]
			outbytes += struct.pack('hbbh', org_track.pitch, org_track.instrument, org_track.disable_sustaining_notes, len(org_track.notes))

		for n in range(16):
			org_track = self.tracks[n]
			n_notes = len(org_track.notes)
			m_pos = [x[0] for x in org_track.notes]
			m_note = [x[1] for x in org_track.notes]
			m_dur = [x[2] for x in org_track.notes]
			m_vol = [x[3] for x in org_track.notes]
			m_pan = [x[4] for x in org_track.notes]
			outbytes += struct.pack('i'*n_notes, *m_pos)
			outbytes += struct.pack('B'*n_notes, *m_note)
			outbytes += struct.pack('B'*n_notes, *m_dur)
			outbytes += struct.pack('B'*n_notes, *m_vol)
			outbytes += struct.pack('B'*n_notes, *m_pan)
		return outbytes

	def save_to_file(self, output_file):
		with open(output_file, "wb") as fileout:
			fileout.write(self.write())