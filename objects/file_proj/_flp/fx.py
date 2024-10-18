# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from io import BytesIO
import struct
from objects.file_proj._flp import plugin

class flp_fxchan:
	def __init__(self):
		self.color = None
		self.icon = None
		self.slots = [None,None,None,None,None,None,None,None,None,None]
		self.data = None
		self.name = None
		self.routing = []
		self.inchannum = 4294967295
		self.outchannum = 4294967295
		self.reversepolarity = False
		self.swap_lr = False
		self.fx_enabled = True
		self.docked_center = True
		self.docked_pos = False
		self.latency = 0
		self.enabled = True
		self.disable_threaded_proc = False
		self.seperator = False
		self.solo = False

	def read(self, event_data):
		event_bio = BytesIO(event_data)
		self.latency, flags = struct.unpack('fI', event_bio.read(8))

		#print( bool(flags&1), bool(flags&2), bool(flags&4), bool(flags&8), bool(flags&16), bool(flags&32), bool(flags&64), bool(flags&128) )
		self.reversepolarity = bool(flags&1)
		self.swap_lr = bool(flags&2)
		self.fx_enabled = bool(flags&4)
		self.enabled = bool(flags&8)
		self.disable_threaded_proc = bool(flags&16)
		self.docked_center = bool(flags&64)
		self.docked_pos = bool(flags&128)
		self.seperator = bool(flags&1024)
		self.solo = bool(flags&4096)

	def write(self):
		outflags = 0
		outflags += int(self.reversepolarity)*1
		outflags += int(self.swap_lr)*2
		outflags += int(self.fx_enabled)*4
		outflags += int(self.enabled)*8
		outflags += int(self.disable_threaded_proc)*16
		outflags += int(self.docked_center)*64
		outflags += int(self.docked_pos)*128
		outflags += int(self.seperator)*1024
		outflags += int(self.solo)*4096
		return struct.pack('fI', self.latency, outflags)+b'\x00\x00\x00\x00'

class flp_fxslot:
	def __init__(self, fxnum):
		self.plugin = plugin.flp_plugin()
		self.plugin.fxnum = fxnum
		self.icon = None
		self.color = None
		self.name = None
		self.used = False