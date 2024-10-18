# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from io import BytesIO
from functions import xtramath
from objects.data_bytes import bytereader
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
		event_bio = BytesIO(event_data)
		self.envlfo_flags = int.from_bytes(event_bio.read(4), "little")
		self.el_env_enabled = int.from_bytes(event_bio.read(4), "little")
		self.el_env_predelay = int.from_bytes(event_bio.read(4), "little")
		self.el_env_attack = int.from_bytes(event_bio.read(4), "little")
		self.el_env_hold =int.from_bytes(event_bio.read(4), "little")
		self.el_env_decay = int.from_bytes(event_bio.read(4), "little")
		self.el_env_sustain = int.from_bytes(event_bio.read(4), "little")
		self.el_env_release = int.from_bytes(event_bio.read(4), "little")
		self.el_env_aomunt = int.from_bytes(event_bio.read(4), "little", signed=True)
		self.envlfo_lfo_predelay = int.from_bytes(event_bio.read(4), "little")
		self.envlfo_lfo_attack = int.from_bytes(event_bio.read(4), "little")
		self.envlfo_lfo_amount = int.from_bytes(event_bio.read(4), "little")
		self.envlfo_lfo_speed = int.from_bytes(event_bio.read(4), "little")
		self.envlfo_lfo_shape = int.from_bytes(event_bio.read(4), "little")
		self.el_env_attack_tension = int.from_bytes(event_bio.read(4), "little", signed=True)/128
		self.el_env_decay_tension = int.from_bytes(event_bio.read(4), "little", signed=True)/128
		self.el_env_release_tension = int.from_bytes(event_bio.read(4), "little", signed=True)/128

	def write(self):
		env_lfo = b''
		env_lfo += self.envlfo_flags.to_bytes(4, "little")
		env_lfo += self.el_env_enabled.to_bytes(4, "little")
		env_lfo += self.el_env_predelay.to_bytes(4, "little")
		env_lfo += self.el_env_attack.to_bytes(4, "little")
		env_lfo += self.el_env_hold.to_bytes(4, "little")
		env_lfo += self.el_env_decay.to_bytes(4, "little")
		env_lfo += self.el_env_sustain.to_bytes(4, "little")
		env_lfo += self.el_env_release.to_bytes(4, "little")
		env_lfo += self.el_env_aomunt.to_bytes(4, "little", signed=True)
		env_lfo += self.envlfo_lfo_predelay.to_bytes(4, "little")
		env_lfo += self.envlfo_lfo_attack.to_bytes(4, "little")
		env_lfo += self.envlfo_lfo_amount.to_bytes(4, "little")
		env_lfo += self.envlfo_lfo_speed.to_bytes(4, "little")
		env_lfo += self.envlfo_lfo_shape.to_bytes(4, "little")
		env_lfo += int(self.el_env_attack_tension*128).to_bytes(4, "little", signed=True)
		env_lfo += int(self.el_env_decay_tension*128).to_bytes(4, "little", signed=True)
		env_lfo += int(self.el_env_release_tension*128).to_bytes(4, "little", signed=True)
		return env_lfo

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
		event_bio = bytereader.bytereader()
		event_bio.load_raw(event_data)
		event_bio.read(8) # ffffffff 00000000
		self.unkflag1 = event_bio.uint8()
		self.remove_dc = event_bio.uint8()
		self.delayflags = event_bio.uint8()
		self.main_pitch = event_bio.uint8()
		event_bio.read(8) # ffffffff3c000000
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
		event_bio.read(1) # 00
		self.timefull_porta = event_bio.uint8()
		self.addtokey = event_bio.uint8()
		self.timegate = event_bio.uint16()
		event_bio.read(2) # 05 00
		self.keyrange_min = event_bio.uint32()
		self.keyrange_max = event_bio.uint32()
		event_bio.read(4) # 00 00 00 00
		self.normalize = event_bio.uint8()
		self.reversepolarity = event_bio.uint8()
		event_bio.read(1) # 00
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
		bytes_params = b''
		bytes_params += b'\xff\xff\xff\xff\x00\x00\x00\x00'
		bytes_params += self.unkflag1.to_bytes(1, "little")
		bytes_params += self.remove_dc.to_bytes(1, "little")
		bytes_params += self.delayflags.to_bytes(1, "little")
		bytes_params += self.main_pitch.to_bytes(1, "little")
		bytes_params += b'\xff\xff\xff\xff'
		bytes_params += b'\x3c\x00\x00\x00'
		bytes_params += struct.pack('fffff', self.ds_tone, self.ds_over, self.ds_noise, self.ds_band, self.ds_time)
		bytes_params += self.arpdirection.to_bytes(4, "little")
		bytes_params += self.arprange.to_bytes(4, "little")
		bytes_params += self.arpchord.to_bytes(4, "little")
		bytes_params += self.arptime.to_bytes(4, "little")
		bytes_params += self.arpgate.to_bytes(4, "little")
		bytes_params += self.arpslide.to_bytes(1, "little")
		bytes_params += b'\x00'
		bytes_params += self.timefull_porta.to_bytes(1, "little")
		bytes_params += self.addtokey.to_bytes(1, "little")
		bytes_params += self.timegate.to_bytes(2, "little")
		bytes_params += b'\x00\x00'
		bytes_params += self.keyrange_min.to_bytes(4, "little")
		bytes_params += self.keyrange_max.to_bytes(4, "little")
		bytes_params += b'\x00\x00\x00\x00'
		bytes_params += self.normalize.to_bytes(1, "little")
		bytes_params += self.reversepolarity.to_bytes(1, "little")
		bytes_params += b'\x00'
		bytes_params += self.declickmode.to_bytes(1, "little")
		bytes_params += self.crossfade.to_bytes(4, "little")
		bytes_params += self.trim.to_bytes(4, "little")
		bytes_params += self.arprepeat.to_bytes(4, "little")
		bytes_params += self.stretchingtime.to_bytes(4, "little")
		bytes_params += self.stretchingpitch.to_bytes(4, "little", signed=True)
		bytes_params += self.stretchingmultiplier.to_bytes(4, "little", signed=True)
		bytes_params += self.stretchingmode.to_bytes(4, "little", signed=True)
		bytes_params += self.midi_chan_thru.to_bytes(4, "little")
		bytes_params += b'\xfe\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00'
		bytes_params += struct.pack('ddd', self.start, self.length, self.start_offset)
		bytes_params += b'\xff\xff\xff\xff\x00\x01\x00\x00'
		bytes_params += struct.pack('d', (self.stretchingformant/24)+0.5)
		return bytes_params

class flp_channel_basicparams:
	def __init__(self):
		self.pan = 0
		self.volume = 1
		self.pitch = 0
		self.mod_x = 256
		self.mod_y = 0
		self.mod_type = 0

	def read(self, event_data):
		event_bio = BytesIO(event_data)
		self.pan = ((int.from_bytes(event_bio.read(4), "little")/12800)-0.5)*2
		self.volume = (int.from_bytes(event_bio.read(4), "little")/12800)
		self.pitch = int.from_bytes(event_bio.read(4), "little", signed="True")
		self.mod_x = int.from_bytes(event_bio.read(4), "little")/256
		self.mod_y = int.from_bytes(event_bio.read(4), "little")/256
		self.mod_type = int.from_bytes(event_bio.read(4), "little")

	def write(self):
		basicp_pan = int(xtramath.clamp((self.pan/2)+0.5, 0, 1)*12800)
		basicp_volume = int(xtramath.clamp(self.volume, 0, 1)*12800)
		basicp_mod_x = int(xtramath.clamp(self.mod_x, 0, 1)*256)
		basicp_mod_y = int(xtramath.clamp(self.mod_y, 0, 1)*256)
		bytes_basicparams = b''
		bytes_basicparams += basicp_pan.to_bytes(4, "little")
		bytes_basicparams += basicp_volume.to_bytes(4, "little")
		bytes_basicparams += int(self.pitch).to_bytes(4, "little", signed=True)
		bytes_basicparams += self.mod_x.to_bytes(4, "little")
		bytes_basicparams += self.mod_y.to_bytes(4, "little")
		bytes_basicparams += self.mod_type.to_bytes(4, "little")
		return bytes_basicparams

class flp_channel_poly:
	def __init__(self):
		self.max = 0
		self.slide = 500
		self.flags = 0

	def read(self, event_data):
		event_bio = BytesIO(event_data)
		self.max = int.from_bytes(event_bio.read(4), "little")
		self.slide = int.from_bytes(event_bio.read(4), "little")
		self.flags = int.from_bytes(event_bio.read(1), "little")

	def write(self):
		bytes_poly = b''
		bytes_poly += self.max.to_bytes(4, "little")
		bytes_poly += self.slide.to_bytes(4, "little")
		bytes_poly += self.flags.to_bytes(1, "little")
		return bytes_poly

class flp_channel_tracking:
	def __init__(self):
		self.mid = 0
		self.pan = 0
		self.mod_x = 0
		self.mod_y = 0

	def read(self, event_data):
		event_bio = BytesIO(event_data)
		self.mid = int.from_bytes(event_bio.read(4), "little", signed=True)
		self.pan = int.from_bytes(event_bio.read(4), "little", signed=True)
		self.mod_x = int.from_bytes(event_bio.read(4), "little", signed=True)
		self.mod_y = int.from_bytes(event_bio.read(4), "little", signed=True)

	def write(self):
		bytes_trking = b''
		bytes_trking += self.mid.to_bytes(4, "little", signed=True)
		bytes_trking += self.pan.to_bytes(4, "little", signed=True)
		bytes_trking += self.mod_x.to_bytes(4, "little", signed=True)
		bytes_trking += self.mod_y.to_bytes(4, "little", signed=True)
		return bytes_trking

class flp_channel_delay:
	def __init__(self):
		self.feedback = 0
		self.pan = 0
		self.pitch = 0
		self.echoes = 4
		self.time = 3

	def read(self, event_data):
		event_bio = BytesIO(event_data)
		self.feedback = int.from_bytes(event_bio.read(4), "little")/12800
		self.pan = int.from_bytes(event_bio.read(4), "little")/19200
		self.pitch = int.from_bytes(event_bio.read(4), "little")
		self.echoes = int.from_bytes(event_bio.read(4), "little")
		self.time = int.from_bytes(event_bio.read(4), "little")/48

	def write(self):
		bytes_delay = b''
		bytes_delay += int(self.feedback*12800).to_bytes(4, "little")
		bytes_delay += int(self.pan*19200).to_bytes(4, "little")
		bytes_delay += self.pitch.to_bytes(4, "little")
		bytes_delay += self.echoes.to_bytes(4, "little")
		bytes_delay += int(self.time*48).to_bytes(4, "little")
		return bytes_delay

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
