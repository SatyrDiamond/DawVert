# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from io import BytesIO
from functions import xtramath
from objects_file._flp import plugin

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
		self.length = 4190208
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
		self.timefull_porta = 1
		self.timegate = 1447
		self.trim = 0
		self.midi_chan_thru = 0
		self.unkflag1 = 0

	def read(self, event_data):
		event_bio = BytesIO(event_data)
		event_bio.read(8) # ffffffff 00000000
		self.unkflag1 = int.from_bytes(event_bio.read(1), "little")
		self.remove_dc = int.from_bytes(event_bio.read(1), "little")
		self.delayflags = int.from_bytes(event_bio.read(1), "little")
		self.main_pitch = int.from_bytes(event_bio.read(1), "little")
		event_bio.read(28) # ffffffff3c0000000000803f0000803f0000803f0000803f0000803f
		self.arpdirection = int.from_bytes(event_bio.read(4), "little")
		self.arprange = int.from_bytes(event_bio.read(4), "little")
		self.arpchord = int.from_bytes(event_bio.read(4), "little")
		self.arptime = int.from_bytes(event_bio.read(4), "little")
		self.arpgate = int.from_bytes(event_bio.read(4), "little")
		self.arpslide = int.from_bytes(event_bio.read(1), "little")
		event_bio.read(1) # 00
		self.timefull_porta = int.from_bytes(event_bio.read(1), "little")
		self.addtokey = int.from_bytes(event_bio.read(1), "little")
		self.timegate = int.from_bytes(event_bio.read(2), "little")
		event_bio.read(2) # 05 00
		self.keyrange_min = int.from_bytes(event_bio.read(4), "little")
		self.keyrange_max = int.from_bytes(event_bio.read(4), "little")
		event_bio.read(4) # 00 00 00 00
		self.normalize = int.from_bytes(event_bio.read(1), "little")
		self.reversepolarity = int.from_bytes(event_bio.read(1), "little")
		event_bio.read(1) # 00
		self.declickmode = int.from_bytes(event_bio.read(1), "little")
		self.crossfade = int.from_bytes(event_bio.read(4), "little")
		self.trim = int.from_bytes(event_bio.read(4), "little")
		self.arprepeat = int.from_bytes(event_bio.read(4), "little")
		self.stretchingtime = int.from_bytes(event_bio.read(4), "little")
		self.stretchingpitch = int.from_bytes(event_bio.read(4), "little", signed=True)
		self.stretchingmultiplier = int.from_bytes(event_bio.read(4), "little", signed=True)
		self.stretchingmode = int.from_bytes(event_bio.read(4), "little", signed=True)

		event_bio.read(12)
		self.midi_chan_thru = int.from_bytes(event_bio.read(1), "little")
		event_bio.read(8)
		self.start = int.from_bytes(event_bio.read(4), "little")
		event_bio.read(4) # b'\x00\x00\x00\x00'
		self.length = int.from_bytes(event_bio.read(4), "little")
		event_bio.read(3) # b'\x00\x00\x00'
		self.start_offset = int.from_bytes(event_bio.read(4), "little")
		event_bio.read(5) # b'\xff\xff\xff\xff\x00'
		self.fix_trim = int.from_bytes(event_bio.read(1), "little")



	def write(self):
		bytes_params = b''
		bytes_params += b'\xff\xff\xff\xff\x00\x00\x00\x00'
		bytes_params += self.unkflag1.to_bytes(1, "little")
		bytes_params += self.remove_dc.to_bytes(1, "little")
		bytes_params += self.delayflags.to_bytes(1, "little")
		bytes_params += self.main_pitch.to_bytes(1, "little")
		bytes_params += b'\xff\xff\xff\xff'
		bytes_params += b'\x3c\x00\x00\x00'
		bytes_params += b'\x00\x00\x80\x3f'*5
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
		bytes_params += b'\x02\x00\x00\x00\xfe\xff\xff\xff\xff\xff\xff\xff'
		bytes_params += self.midi_chan_thru.to_bytes(1, "little")
		bytes_params += b'\x00\x00\x00\x00\x00\x00\x00\x00'
		bytes_params += self.start.to_bytes(4, "little")
		bytes_params += b'\x00\x00\x00\x00'
		bytes_params += self.length.to_bytes(4, "little")
		bytes_params += b'\x00\x00\x00'
		bytes_params += self.start_offset.to_bytes(4, "little")
		bytes_params += b'\xff\xff\xff\xff\x00'
		bytes_params += self.fix_trim.to_bytes(1, "little")
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

class flp_channel:
	def __init__(self):
		self.type = 0
		self.name = None
		self.icon = None
		self.color = None
		self.plugin = plugin.flp_plugin()
		self.enabled = None
		self.env_lfo = []
		self.attack = 0
		self.cutcutby = 0
		self.cutoff = 1024
		self.decay = 0
		self.delay = b'\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x90\x00\x00\x00'
		self.delayreso = 8388736
		self.fadestereo = 0
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
