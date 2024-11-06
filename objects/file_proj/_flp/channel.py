# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from functions import xtramath
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
from objects.file_proj._flp import plugin
import struct

class flp_env_lfo:
	def __init__(self):
		self.envlfo_flags = 0
		self.el_env_enabled = 0
		self.el_env_predelay = 100
		self.el_env_attack = 20000
		self.el_env_hold = 20000
		self.el_env_decay = 30000
		self.el_env_sustain = 50
		self.el_env_release = 20000
		self.el_env_aomunt = 0
		self.envlfo_lfo_predelay = 100
		self.envlfo_lfo_attack = 20000
		self.envlfo_lfo_amount = 0
		self.envlfo_lfo_speed = 32950
		self.envlfo_lfo_shape = 0
		self.el_env_attack_tension = 0.0
		self.el_env_decay_tension = 0.0
		self.el_env_release_tension = 0.0

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		self.envlfo_flags = event_bio.uint32()
		self.el_env_enabled = event_bio.uint32()
		self.el_env_predelay = event_bio.uint32()
		self.el_env_attack = event_bio.uint32()
		self.el_env_hold =event_bio.uint32()
		self.el_env_decay = event_bio.uint32()
		self.el_env_sustain = event_bio.uint32()
		self.el_env_release = event_bio.uint32()
		self.el_env_aomunt = event_bio.int32()
		self.envlfo_lfo_predelay = event_bio.uint32()
		self.envlfo_lfo_attack = event_bio.uint32()
		self.envlfo_lfo_amount = event_bio.uint32()
		self.envlfo_lfo_speed = event_bio.uint32()
		self.envlfo_lfo_shape = event_bio.uint32()
		self.el_env_attack_tension = event_bio.int32()/128
		self.el_env_decay_tension = event_bio.int32()/128
		self.el_env_release_tension = event_bio.int32()/128

	def write(self):
		el_env_attack_tension = int(self.el_env_attack_tension*128)
		el_env_decay_tension = int(self.el_env_decay_tension*128)
		el_env_release_tension = int(self.el_env_release_tension*128)

		env_lfo = bytewriter.bytewriter()
		env_lfo.uint32(self.envlfo_flags)
		env_lfo.uint32(self.el_env_enabled)
		env_lfo.uint32(self.el_env_predelay)
		env_lfo.uint32(self.el_env_attack)
		env_lfo.uint32(self.el_env_hold)
		env_lfo.uint32(self.el_env_decay)
		env_lfo.uint32(self.el_env_sustain)
		env_lfo.uint32(self.el_env_release)
		env_lfo.int32(self.el_env_aomunt)
		env_lfo.uint32(self.envlfo_lfo_predelay)
		env_lfo.uint32(self.envlfo_lfo_attack)
		env_lfo.uint32(self.envlfo_lfo_amount)
		env_lfo.uint32(self.envlfo_lfo_speed)
		env_lfo.uint32(self.envlfo_lfo_shape)
		env_lfo.int32(el_env_attack_tension)
		env_lfo.int32(el_env_decay_tension)
		env_lfo.int32(el_env_release_tension)
		return env_lfo.getvalue()

class flp_channel_params:
	def __init__(self):
		self.addtokey = 0
		self.arpchord = 4294967295
		self.arpdirection = 0
		self.arpgate = 48
		self.arprange = 1
		self.arprepeat = 1
		self.arpslide = 0
		self.arptime = 1024
		self.crossfade = 0
		self.declickmode = 0
		self.delayflags = 0
		self.fix_trim = 1
		self.keyrange_max = 256
		self.keyrange_min = 0
		self.length = 1
		self.main_pitch = 1
		self.normalize = 0
		self.pan = 0
		self.remove_dc = 0
		self.reversepolarity = 0
		self.start = 0
		self.start_offset = 0
		self.stretchingmode = 0
		self.stretchingmultiplier = 0
		self.stretchingpitch = 0
		self.stretchingtime = 0
		self.stretchingformant = 0
		self.timefull_porta = 1
		self.timegate = 1447
		self.trim = 0
		self.midi_chan_thru = 0
		self.unkflag1 = 0
		self.ds_tone = 1.0
		self.ds_over = 1.0
		self.ds_noise = 1.0
		self.ds_band = 1.0
		self.ds_time = 1.0

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		event_bio.skip(8) # ffffffff 00000000
		self.unkflag1 = event_bio.uint8()
		self.remove_dc = event_bio.uint8()
		self.delayflags = event_bio.uint8()
		self.main_pitch = event_bio.uint8()
		event_bio.skip(8) # ffffffff3c000000
		self.ds_tone = event_bio.float()
		self.ds_over = event_bio.float()
		self.ds_noise = event_bio.float()
		self.ds_band = event_bio.float()
		self.ds_time = event_bio.float()
		self.arpdirection = event_bio.uint32()
		self.arprange = event_bio.uint32()
		self.arpchord = event_bio.uint32()
		self.arptime = event_bio.uint32()
		self.arpgate = event_bio.uint32()
		self.arpslide = event_bio.uint8()
		event_bio.skip(1) # 00
		self.timefull_porta = event_bio.uint8()
		self.addtokey = event_bio.uint8()
		self.timegate = event_bio.uint16()
		event_bio.skip(2) # 05 00
		self.keyrange_min = event_bio.uint32()
		self.keyrange_max = event_bio.uint32()
		event_bio.skip(4) # 00 00 00 00
		self.normalize = event_bio.uint8()
		self.reversepolarity = event_bio.uint8()
		event_bio.skip(1) # 00
		self.declickmode = event_bio.uint8()
		self.crossfade = event_bio.uint32()
		self.trim = event_bio.uint32()
		self.arprepeat = event_bio.uint32()
		self.stretchingtime = event_bio.uint32()
		self.stretchingpitch = event_bio.int32()
		self.stretchingmultiplier = event_bio.int32()
		self.stretchingmode = event_bio.int32()

		self.midi_chan_thru = event_bio.uint32()

		if event_bio.remaining(): event_bio.skip(4)
		if event_bio.remaining(): event_bio.skip(4)
		if event_bio.remaining(): event_bio.skip(4)
		if event_bio.remaining(): self.start = event_bio.double()
		if event_bio.remaining(): self.length = event_bio.double()
		if event_bio.remaining(): self.start_offset = event_bio.double()
		if event_bio.remaining(): event_bio.skip(4)
		if event_bio.remaining(): event_bio.skip(4)
		if event_bio.remaining(): self.stretchingformant = (event_bio.double()-0.5)*24

	def write(self):
		bytes_params = bytewriter.bytewriter()
		bytes_params.int32(-1)
		bytes_params.int32(0)
		bytes_params.int8(self.unkflag1)
		bytes_params.int8(self.remove_dc)
		bytes_params.int8(self.delayflags)
		bytes_params.int8(self.main_pitch)
		bytes_params.int32(-1)
		bytes_params.int32(60)
		bytes_params.float(self.ds_tone)
		bytes_params.float(self.ds_over)
		bytes_params.float(self.ds_noise)
		bytes_params.float(self.ds_band)
		bytes_params.float(self.ds_time)

		bytes_params.uint32(self.arpdirection)
		bytes_params.uint32(self.arprange)
		bytes_params.uint32(self.arpchord)
		bytes_params.uint32(self.arptime)
		bytes_params.uint32(self.arpgate)
		bytes_params.int8(self.arpslide)
		bytes_params.raw(b'\x00')
		bytes_params.int8(self.timefull_porta)
		bytes_params.int8(self.addtokey)
		bytes_params.int16(self.timegate)
		bytes_params.raw(b'\x00\x00')
		bytes_params.uint32(self.keyrange_min)
		bytes_params.uint32(self.keyrange_max)
		bytes_params.raw(b'\x00\x00\x00\x00')
		bytes_params.int8(self.normalize)
		bytes_params.int8(self.reversepolarity)
		bytes_params.raw(b'\x00')
		bytes_params.int8(self.declickmode)
		bytes_params.uint32(self.crossfade)
		bytes_params.uint32(self.trim)
		bytes_params.uint32(self.arprepeat)
		bytes_params.uint32(self.stretchingtime)
		bytes_params.int32(self.stretchingpitch)
		bytes_params.int32(self.stretchingmultiplier)
		bytes_params.int32(self.stretchingmode)
		bytes_params.uint32(self.midi_chan_thru)
		bytes_params.int32(-2)
		bytes_params.int32(-1)
		bytes_params.int32(0)
		bytes_params.double(self.start)
		bytes_params.double(self.length)
		bytes_params.double(self.start_offset)
		bytes_params.raw(b'\xff\xff\xff\xff\x00\x01\x00\x00')
		bytes_params.double((self.stretchingformant/24)+0.5)
		return bytes_params.getvalue()

class flp_channel_basicparams:
	def __init__(self):
		self.pan = 0
		self.volume = 1
		self.pitch = 0
		self.mod_x = 256
		self.mod_y = 0
		self.mod_type = 0

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		self.pan = ((event_bio.uint32()/12800)-0.5)*2
		self.volume = (event_bio.uint32()/12800)
		self.pitch = event_bio.int32()
		self.mod_x = event_bio.uint32()/256
		self.mod_y = event_bio.uint32()/256
		self.mod_type = event_bio.uint32()

	def write(self):
		basicp_pan = int(xtramath.clamp((self.pan/2)+0.5, 0, 1)*12800)
		basicp_volume = int(xtramath.clamp(self.volume, 0, 1)*12800)
		basicp_pitch = int(self.pitch)
		basicp_mod_x = int(xtramath.clamp(self.mod_x, 0, 1)*256)
		basicp_mod_y = int(xtramath.clamp(self.mod_y, 0, 1)*256)
		bytes_basicparams = bytewriter.bytewriter()
		bytes_basicparams.uint32(basicp_pan)
		bytes_basicparams.uint32(basicp_volume)
		bytes_basicparams.int32(basicp_pitch)
		bytes_basicparams.uint32(basicp_mod_x)
		bytes_basicparams.uint32(basicp_mod_y)
		bytes_basicparams.uint32(self.mod_type)
		return bytes_basicparams.getvalue()

class flp_channel_poly:
	def __init__(self):
		self.max = 0
		self.slide = 500
		self.flags = 0

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		self.max = event_bio.uint32()
		self.slide = event_bio.uint32()
		self.flags = event_bio.uint8()

	def write(self):
		bytes_poly = bytewriter.bytewriter()
		bytes_poly.uint32(self.max)
		bytes_poly.uint32(self.slide)
		bytes_poly.uint8(self.flags)
		return bytes_poly.getvalue()

class flp_channel_tracking:
	def __init__(self):
		self.mid = 0
		self.pan = 0
		self.mod_x = 0
		self.mod_y = 0

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		self.mid = event_bio.int32()
		self.pan = event_bio.int32()
		self.mod_x = event_bio.int32()
		self.mod_y = event_bio.int32()

	def write(self):
		bytes_trking = bytewriter.bytewriter()
		bytes_trking.int32(self.mid)
		bytes_trking.int32(self.pan)
		bytes_trking.int32(self.mod_x)
		bytes_trking.int32(self.mod_y)
		return bytes_trking.getvalue()

class flp_channel_delay:
	def __init__(self):
		self.feedback = 0
		self.pan = 0
		self.pitch = 0
		self.echoes = 4
		self.time = 3

	def read(self, event_data):
		event_bio = bytereader.bytereader(event_data)
		self.feedback = event_bio.uint32()/12800
		self.pan = event_bio.uint32()/19200
		self.pitch = event_bio.uint32()
		self.echoes = event_bio.uint32()
		self.time = event_bio.uint32()/48

	def write(self):
		bytes_delay = bytewriter.bytewriter()
		bytes_delay.uint32(int(self.feedback*12800))
		bytes_delay.uint32(int(self.pan*19200))
		bytes_delay.uint32(self.pitch)
		bytes_delay.uint32(self.echoes)
		bytes_delay.uint32(int(self.time*48))
		return bytes_delay.getvalue()

class flp_channel:
	def __init__(self):
		self.type = 0
		self.name = None
		self.icon = None
		self.color = None
		self.plugin = plugin.flp_plugin()
		self.enabled = 1
		self.env_lfo = []
		self.attack = 0
		self.cutcutby = 0
		self.cutoff = 1024
		self.decay = 0
		self.delay = flp_channel_delay()
		#self.delay = b'\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x90\x00\x00\x00'
		self.delayreso = 8388736
		self.fxflags = 0
		self.fx = 128
		self.fx3 = 256
		self.fxchannel = 0
		self.fxsine = 8388608
		self.layerflags = 0
		self.looptype = 0
		self.middlenote = 60
		self.ofslevels = b'\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		self.preamp = 0
		self.resonance = 0
		self.reverb = 65536
		self.sampleflags = 10
		self.shiftdelay = 0
		self.stdel = 2048
		self.basicparams = flp_channel_basicparams()
		self.poly = flp_channel_poly()
		self.params = flp_channel_params()
		self.cutcutby = 0
		self.layerflags = 0
		self.filtergroup = 0
		self.samplefilename = None
		self.tracking = []
		self.layer_chans = []
		self.autopoints = None
