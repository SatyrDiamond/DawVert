# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from io import BytesIO
import struct

class flp_plugin:
	def __init__(self):
		self.name = None
		self.params = None
		self.fxnum = 0
		self.slotnum = 0
		self.window_p_x = 0
		self.window_p_y = 0
		self.window_s_x = 0
		self.window_s_y = 0
		self.visible = False
		self.detached = False
		self.generator = False
		self.smart_disable = False
		self.threaded_processing = True
		self.hide_settings = False
		self.minimized = False
		self.unk1 = 2
		self.unk2 = 0
		self.unk3 = 0
		self.unk4 = 0
		self.unk5 = 0
		self.unk6 = 0

	def read(self, event_data):
		event_bio = BytesIO(event_data)
		self.fxnum, self.slotnum, self.unk1, self.unk2, flags = struct.unpack('IIIII', event_bio.read(20))
		self.unk3, self.unk4, self.unk5, self.unk6 = struct.unpack('IIII', event_bio.read(16))
		self.window_p_x, self.window_p_y, self.window_s_x, self.window_s_y = struct.unpack('IIII', event_bio.read(16))

		self.visible = bool(flags&1)
		self.detached = bool(flags&4)
		self.generator = bool(flags&16)
		self.smart_disable = bool(flags&32)
		self.threaded_processing = bool(flags&64)
		#flags&128
		self.hide_settings = bool(flags&256)
		self.minimized = bool(flags&512)

		#print(self.unk1, self.unk2, flags, self.unk3, self.unk4, self.unk5, self.unk6)

	def write(self):
		outflags = 0
		outflags += int(self.visible)<<0
		outflags += int(self.detached)<<2
		outflags += int(self.generator)<<4
		outflags += int(self.smart_disable)<<5
		outflags += int(self.threaded_processing)<<6
		#outflags += 128
		outflags += int(self.hide_settings)<<8
		#outflags += int(self.minimized)<<9

		out_data = b''
		out_data += struct.pack('IIIII', self.fxnum, self.slotnum, self.unk1, self.unk2, outflags)
		out_data += struct.pack('IIII', self.unk3, self.unk4, self.unk5, self.unk6)
		out_data += struct.pack('IIII', self.window_p_x, self.window_p_y, self.window_s_x, self.window_s_y)


		#print(self.unk1, self.unk2, outflags, self.unk3, self.unk4, self.unk5, self.unk6)


		return out_data