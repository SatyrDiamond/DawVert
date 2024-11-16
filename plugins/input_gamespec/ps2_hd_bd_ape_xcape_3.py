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
	def do_song(self, input_file):
		from objects.songinput import midi_in
		from objects_midi.parser import MidiFile
		midifile = MidiFile.fromFile(input_file)
		ppq = midifile.ppqn
		song_obj = midi_in.midi_song(16, ppq, 120, [4,4])
		for n, miditrack in enumerate(midifile.tracks):
			logger_input.info('Track '+str(n+1)+' of '+str(len(midifile.tracks)))
			track_obj = song_obj.create_track(len(miditrack.events))
			self.do_track(miditrack.events, track_obj, song_obj)
		return 16, ppq, song_obj

	def do_track(self, eventlist, track_obj, song_obj):
		from objects_midi import events as MidiEvents
		curpos = 0
		for msg in eventlist:
			curpos += msg.deltaTime
			if type(msg) == MidiEvents.NoteOnEvent:
				if msg.velocity != 0: track_obj.note_on(curpos, msg.channel, msg.note, msg.velocity)
				else: track_obj.note_off(curpos, msg.channel, msg.note)
			elif type(msg) == MidiEvents.NoteOffEvent:       track_obj.note_off(curpos, msg.channel, msg.note)
			elif type(msg) == MidiEvents.TrackNameEvent:     track_obj.track_name = msg.name
			elif type(msg) == MidiEvents.PitchBendEvent:     track_obj.pitchwheel(curpos, msg.channel, msg.pitch)
			elif type(msg) == MidiEvents.ControllerEvent:    track_obj.control_change(curpos, msg.channel, msg.controller, msg.value)
			elif type(msg) == MidiEvents.ProgramEvent:       track_obj.program_change(curpos, msg.channel, msg.program)
			elif type(msg) == MidiEvents.TempoEvent:         track_obj.set_tempo(curpos, 60000000/msg.tempo)
			elif type(msg) == MidiEvents.TimeSignatureEvent: track_obj.time_signature(curpos, msg.numerator, msg.denominator)
			elif type(msg) == MidiEvents.TextEvent:          track_obj.text(curpos, msg.text)
			elif type(msg) == MidiEvents.MarkerEvent:        track_obj.marker(curpos, msg.marker)
			elif type(msg) == MidiEvents.SequencerEvent:     track_obj.sequencer_specific(msg.data)
			elif type(msg) == MidiEvents.SysExEvent:         track_obj.sysex(curpos, msg.data)
			elif type(msg) == MidiEvents.CopyrightEvent:     track_obj.copyright(msg.copyright)
			elif type(msg) == MidiEvents.LyricEvent:         track_obj.lyric(curpos, msg.lyric)
			elif type(msg) == MidiEvents.KeySignatureEvent:  pass
			elif type(msg) == MidiEvents.EndOfTrackEvent:    break

class input_petaporon(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'ps2_hd_bd_ape_xcape_3'
	def get_name(self): return 'Ape Escape 3'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = []
		in_dict['track_nopl'] = True
	def parse(self, convproj_obj, input_file, dv_config):
		from objects import audio_data

		convproj_obj.type = 'rm'

		samplefolder = dv_config.path_samples_extracted

		path_bd = os.path.splitext(input_file)[0]+'.bd'
		path_hd = os.path.splitext(input_file)[0]+'.hd'

		apeinst_obj = apeescape()
		apeinst_obj.load_from_file(path_hd)

		sample_obj = apeescape_bd()
		sample_obj.load_from_file(path_bd)

		midiread_obj = reader_midifile_class()

		numchans, ppq, song_obj = midiread_obj.do_song(input_file)
		song_obj.nocolor = True

		logger_input.info('PPQ: ' + str(ppq))
		convproj_obj.set_timings(ppq, False)

		song_obj.postprocess()

		offset_points = {}

		for i, instpart in enumerate(apeinst_obj.insts):
			for s, inst in enumerate(instpart):
				if inst['offset'] not in offset_points:
					sample_offset = (inst['offset']+2)*8
					logger_input.info('Ripping Sample #'+str(s+1)+' from Instrument #'+str(i+1))
					sample_data = sample_obj.rip_sample(sample_offset)
					wav_path = samplefolder + str(inst['offset']) + '.wav'
					audio_obj = audio_data.audio_obj()
					audio_obj.decode_from_codec('sony_vag', sample_data)
					audio_obj.to_file_wav(wav_path)
					offset_points[inst['offset']] = wav_path

		for x in song_obj.instruments.midi_instruments.data:
			if len(apeinst_obj.insts) >= x['inst']:
				x['is_custom'] = 1
				x['custom_name'] = 'PS2 VAG #'+str(x['inst'])
				x['custom_color_used'] = 1
				x['custom_color'] = [50,140,255]
		
		song_obj.to_cvpj(convproj_obj)

		for inst, instid in song_obj.get_insts_custom():
			if instid in convproj_obj.instruments:
				if inst['inst']<len(apeinst_obj.insts):
					vaginst = apeinst_obj.insts[inst['inst']]
	
					inst_obj = convproj_obj.instruments[instid]
					plugin_obj, synthid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
					plugin_obj.role = 'synth'
					plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)

					inst_obj.plugslots.set_synth(synthid)

					for n, v in enumerate(vaginst):
						sample_offset = str(v['offset'])
						sample_id = '_'.join([str(inst['inst']), str(n), sample_offset])
						wav_path = samplefolder + str(v['offset']) + '.wav'
						sampleref_obj = convproj_obj.sampleref__add(sample_id, wav_path, None)
						sp_obj = plugin_obj.sampleregion_add(v['key_min']-60, v['key_max']-60, v['key_root']-60, None, samplepartid=sample_id)
						sp_obj.sampleref = sample_id
						sp_obj.from_sampleref(convproj_obj, sp_obj.sampleref)

						sp_obj.pitch = (v['cents']/100) - 0.4
						sp_obj.vol = v['vol']/127
						sp_obj.pan = (int(v['pan'])-64)/64

			convproj_obj.do_actions.append('do_addloop')
			convproj_obj.do_actions.append('do_singlenotelistcut')
			#convproj_obj.do_actions.append('do_sorttracks')

