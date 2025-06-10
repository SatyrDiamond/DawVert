# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

from objects.data_bytes import bytereader
from objects.data_bytes import riff_chunks
from functions import data_values
import logging
import numpy as np
import os

logger_input = logging.getLogger('input')

instpart = np.dtype([
	('key_min', np.uint8), 
	('key_max', np.uint8), 
	('key_root', np.uint8), 
	('cents', np.int8), 

	('offset', np.uint16), 
	('env_sustain_lvl', np.uint8), 
	('env_attack', np.uint8), 

	('env_release', np.uint8), 
	('env_sustain_rate', np.int8), 
	('__unk11', np.int8), 
	('vol', np.uint8), 

	('pan', np.uint8), 
	('__unk13', np.uint8), 
	('__unk14', np.uint8), 
	('reverb', np.uint8), 
	]) 

class apeescape_patch:
	def parse(self, byr_stream):
		self.unk1 = byr_stream.uint8()
		self.vol = byr_stream.uint8()
		self.header = byr_stream.l_uint8(4)
		self.startkey = byr_stream.uint8()
		self.unk2 = byr_stream.uint8()
		self.data = np.frombuffer(byr_stream.l_uint8(16*((self.unk1%128)+1)), dtype=instpart)

	def __getitem__(self, v):
		return self.data[v]

	def debugtxt(self):
		print('PART_HEADER', self.header)
		print('PART_DATA', self.vol, self.startkey, self.unk1%128, self.unk2)
		for x in self.data:
			print((x['offset']+2)*8, x)

class apeescape:
	def __init__(self):
		self.insts = []

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()

		byr_stream.load_file(input_file)

		hd_size = byr_stream.uint32()
		bd_size = byr_stream.uint32()

		byr_stream.skip(4)

		byr_stream.magic_check(b'SShd')
		ptr_inst = byr_stream.uint32()
		data_size = byr_stream.uint32()

		byr_stream.seek(ptr_inst)

		numpatches = byr_stream.uint16()
		num_unk2 = byr_stream.uint16()

		ptrlist = byr_stream.l_uint16(numpatches)

		iparts_obj = apeescape_patch()
		iparts_obj.parse(byr_stream)
		#iparts_obj.debugtxt()
		self.insts.append(iparts_obj)

		for x in range(numpatches):
			byr_stream.seek(ptrlist[x]+ptr_inst)
			iparts_obj = apeescape_patch()
			iparts_obj.parse(byr_stream)
			self.insts.append(iparts_obj)
			#iparts_obj.debugtxt()

class apeescape_bd:
	def load_from_file(self, input_file):
		self.byr_stream = bytereader.bytereader()
		self.byr_stream.load_file(input_file)
		self.samples = []

	def all_samples(self):
		self.byr_stream.seek(0)
		while self.byr_stream.remaining():
			rawdata = self.byr_stream.raw(16)
			if rawdata == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00': 
				self.samples.append(b'')
			else: self.samples[-1] += rawdata

	def rip_sample(self, loc):
		outdata = b''
		self.byr_stream.seek(loc)
		while self.byr_stream.remaining():
			rawdata = self.byr_stream.raw(16)
			if rawdata == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00': 
				break
			else: outdata += rawdata
		return outdata

class reader_midifile_class():
	def do_song(self, input_file, convproj_obj):
		from objects.midi_file.parser import MidiFile
		midifile = MidiFile.fromFile(input_file)
		ppq = midifile.ppqn
		convproj_obj.set_timings(ppq, False)
		for n, miditrack in enumerate(midifile.tracks):
			track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)
			logger_input.info('Track '+str(n+1)+' of '+str(len(midifile.tracks)))
			self.do_track(miditrack.events, track_obj)
		return ppq

	def do_track(self, eventlist, track_obj):
		from objects.midi_file import events as MidiEvents
		events_obj = track_obj.placements.midievents
		events_obj.data.alloc(len(eventlist))

		curpos = 0
		for msg in eventlist:
			curpos += msg.deltaTime
			if type(msg) == MidiEvents.NoteOnEvent: events_obj.add_note_on(curpos, msg.channel, msg.note, msg.velocity)
			elif type(msg) == MidiEvents.NoteOffEvent: events_obj.add_note_off(curpos, msg.channel, msg.note, 0)
			elif type(msg) == MidiEvents.TrackNameEvent: track_obj.visual.name = msg.name
			elif type(msg) == MidiEvents.CopyrightEvent: events_obj.add_copyright(msg.copyright)
			elif type(msg) == MidiEvents.PitchBendEvent: events_obj.add_pitch(curpos, msg.channel, msg.pitch)
			elif type(msg) == MidiEvents.ControllerEvent: events_obj.add_control(curpos, msg.channel, msg.controller, msg.value)
			elif type(msg) == MidiEvents.ProgramEvent: events_obj.add_program(curpos, msg.channel, msg.program)
			elif type(msg) == MidiEvents.TempoEvent: events_obj.add_tempo(curpos, 60000000/msg.tempo)
			elif type(msg) == MidiEvents.TimeSignatureEvent: events_obj.add_timesig(curpos, msg.numerator, msg.denominator**2)
			elif type(msg) == MidiEvents.TextEvent: events_obj.add_text(curpos, msg.text)
			elif type(msg) == MidiEvents.SysExEvent: events_obj.add_sysex(curpos, msg.data)
			elif type(msg) == MidiEvents.MarkerEvent: events_obj.add_marker(curpos, msg.marker)
			elif type(msg) == MidiEvents.LyricEvent: events_obj.add_lyric(curpos, msg.lyric)
			elif type(msg) == MidiEvents.SequencerEvent: events_obj.add_seq_spec(msg.data)
			elif type(msg) == MidiEvents.MidiPortEvent: events_obj.add_port(msg.port)
			elif type(msg) == MidiEvents.EndOfTrackEvent: break

class input_petaporon(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'ps2_hdbd_ax3'
	
	def get_name(self):
		return 'Ape Escape 3'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'cm'

	def parse(self, convproj_obj, dawvert_intent):
		from objects import audio_data

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cm'

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		midiread_obj = reader_midifile_class()

		apeinst_obj = apeescape()
		sample_obj = apeescape_bd()

		if dawvert_intent.input_mode == 'file':
			midiread_obj.do_song(dawvert_intent.input_file, convproj_obj)

			path_hd = os.path.splitext(dawvert_intent.input_file)[0]+'.hd'
			apeinst_obj.load_from_file(path_hd)
	
			path_bd = os.path.splitext(dawvert_intent.input_file)[0]+'.bd'
			sample_obj.load_from_file(path_bd)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')

		samplefolder = dawvert_intent.path_samples['extracted']

		custinst_obj = convproj_obj.main__add_midi_custom_inst()
		custinst_obj.bank = 0
		custinst_obj.bank_hi = 0
		custinst_obj.visual.name = 'PS2 VAG #$patch$'
		custinst_obj.visual.color.set_int([50,140,255])
		custinst_obj.pluginid = 'voice_$patch$'

		offset_points = {}

		for instnum, vaginst in enumerate(apeinst_obj.insts):
			plugin_obj = convproj_obj.plugin__add('voice_'+str(instnum), 'universal', 'sampler', 'multi')
			plugin_obj.role = 'synth'
			plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)

			for sampnum, vagsamp in enumerate(vaginst):
				sample_offset = str(vagsamp['offset'])
				sample_id = '_'.join([str(instnum), str(sampnum), sample_offset])
				wav_path = samplefolder + sample_offset + '.wav'

				audio_obj = None
				if vagsamp['offset'] not in offset_points:
					logger_input.info('Ripping Sample #'+str(sampnum+1)+' from Instrument #'+str(instnum+1))
					sample_data = sample_obj.rip_sample((vagsamp['offset']+2)*8)
					audio_obj = audio_data.audio_obj()
					audio_obj.decode_from_codec('sony_vag', sample_data)
					audio_obj.to_file_wav(wav_path)
					offset_points[vagsamp['offset']] = wav_path

					sampleref_obj = convproj_obj.sampleref__add(sample_id, wav_path, None)
					sampleref_obj.set_fileformat('wav')
					audio_obj.to_sampleref_obj(sampleref_obj)

				sp_obj = plugin_obj.sampleregion_add(vagsamp['key_min']-60, vagsamp['key_max']-60, vagsamp['key_root']-60, None, samplepartid=sample_id)
				sp_obj.sampleref = sample_id
				sp_obj.from_sampleref(convproj_obj, sp_obj.sampleref)

				sp_obj.pitch = (vagsamp['cents']/100) - 0.4
				sp_obj.vol = vagsamp['vol']/127
				sp_obj.pan = (int(vagsamp['pan'])-64)/64
#