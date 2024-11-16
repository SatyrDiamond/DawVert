# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import data_values
from functions import xtramath
from objects import colors
from objects import globalstore
from objects.exceptions import ProjectFileParserException
import plugins
import json
import os
import math

FILTERFREQ = [2378.41, 3363.59, 4756.83, 5656.85, 8000, 9513.66, 11313.71, 13454.34, 16000, 19027.31, None]

class rawchipwaves_part():
	__slots__ = ['expression', 'samples']
	def __init__(self): 
		self.expression = 1
		self.samples = []

class rawchipwaves():
	def __init__(self): 
		self.loaded = False
		self.waves = {}

	def load_from_file(self, filename): 
		wavefileobj = open(filename)
		for x in wavefileobj.readlines():
			splitv = x.strip().split('|')
			if len(splitv) == 3:
				chippart_obj = rawchipwaves_part()
				name, chippart_obj.expression, chippart_obj.samples = splitv
				chippart_obj.samples = chippart_obj.samples.split(',')
				for n, x in enumerate(chippart_obj.samples):
					if '/' in x:
						num, dem = x.split('/')
						chippart_obj.samples[n] = float(num)/float(dem)
					else: chippart_obj.samples[n] = float(x)
				self.waves[name] = chippart_obj

	def apply_wave(self, plugin_obj, name, wave_id):
		if name in self.waves:
			wave_obj = plugin_obj.wave_add(wave_id)
			wave_obj.set_all(self.waves[name].samples)

class jummbox_autotype():
	def __init__(self): 
		self.tracknum = -100
		self.instrument = 0
		self.param = 0

	def __str__(self):
		':'.join([str(self.tracknum), str(self.instrument), str(self.param)])

	def __eq__(self, o):
		return self.tracknum==o.tracknum and self.instrument==o.instrument and self.param==o.param

	def get_data(self):
		autoloc, m_add, m_mul = None, 0, 1

		if self.tracknum == -1:
			if self.param == 2:    return ['master', 'vol'], 0, 0.01
			elif self.param == 1:  return ['main', 'bpm'], 30, 1
			elif self.param == 3:  return ['slot', 'main_reverb', 'wet'], 0, 1/32
			elif self.param == 17: return ['main', 'pitch'], 250, 0.01
		else:
			auto_cvpj_instid = 'bb_ch'+str(self.tracknum+1)+'_inst'+str(self.instrument+1)
			if self.param == 6:    return ['track', auto_cvpj_instid, 'pan'], -50, 0.02
			elif self.param == 7:  return ['slot', auto_cvpj_instid+'_reverb', 'wet'], 0, 1/32
			elif self.param == 8:  return ['slot', auto_cvpj_instid+'_distortion', 'amount'], 0, 1/7
			elif self.param == 15: return ['slot', auto_cvpj_instid, 'pitch'], -200, 1
			elif self.param == 25: return ['plugin', auto_cvpj_instid+'_bitcrush', 'bits'], 0, 1
			elif self.param == 26: return ['plugin', auto_cvpj_instid+'_bitcrush', 'freq'], 0, 1
			elif self.param == 29: return ['plugin', auto_cvpj_instid+'_chorus', 'amount'], 0, 1/8
			elif self.param == 36: return ['track', auto_cvpj_instid, 'vol'], 0, 0.04

		return autoloc, m_add, m_mul

noteoffset = {}
noteoffset['B'] = 11
noteoffset['A♯'] = 10
noteoffset['A'] = 9
noteoffset['G♯'] = 8
noteoffset['G'] = 7
noteoffset['F♯'] = 6
noteoffset['F'] = 5
noteoffset['E'] = 4
noteoffset['D♯'] = 3
noteoffset['D'] = 2
noteoffset['C♯'] = 1
noteoffset['C'] = 0

def text_patternid(channum, patnum):
	return 'bb_ch'+str(channum)+'_pat'+str(patnum)

def text_instid(channum, instnum):
	return 'bb_ch'+str(channum)+'_inst'+str(instnum)

def addfx(convproj_obj, inst_obj, fxgroupname, cvpj_instid, fxname, fxsubname):
	fx_pluginid = cvpj_instid+'_'+fxname
	plugin_obj = convproj_obj.plugin__add(fx_pluginid, fxgroupname, fxname, fxsubname)
	plugin_obj.role = 'fx'
	inst_obj.plugslots.slots_audio.append(fx_pluginid)
	return plugin_obj

def add_eq_data(inst_obj, cvpj_instid, eqfiltbands):
	plugin_obj = addfx(convproj_obj, inst_obj, 'universal', cvpj_instid, 'eq', 'bands')
	plugin_obj.role = 'fx'
	plugin_obj.visual.name = 'EQ'
	for eqfiltdata in eqfiltbands:
		eqgain_pass = eqfiltdata['linearGain']
		eqgain = (eqfiltdata['linearGain']-2)*6
		eqtype = eqfiltdata['type']
		filter_obj = plugin_obj.eq_add()
		filter_obj.freq = eqfiltdata['cutoffHz']
		if eqtype == 'low-pass':
			filter_obj.type.set('low_pass', None)
			filter_obj.q = eqgain_pass
		if eqtype == 'peak':
			filter_obj.type.set('peak', None)
		if eqtype == 'high-pass':
			filter_obj.type.set('high_pass', None)
			filter_obj.q = eqgain_pass

def get_harmonics(harmonics_obj, i_harmonics):
	n = 1
	for i in i_harmonics:
		harmonics_obj.add(n, i/100, {})
		n += 1
	harmonics_obj.add(n, i_harmonics[-1]/100, {})
	harmonics_obj.add(n+1, i_harmonics[-1]/100, {})
	harmonics_obj.add(n+2, i_harmonics[-1]/100, {})

def get_asdr(plugin_obj, bb_inst, jummbox_obj):
	a_attack = bb_inst.fadeInSeconds
	a_decay = 3
	a_sustain = 1
	a_release = abs(bb_inst.fadeOutTicks)/(jummbox_obj.ticksPerBeat*32)
	if bb_inst.type == 'Picked String' and 'stringSustain' in bb_inst.data: a_sustain = bb_inst.data['stringSustain']/100
	plugin_obj.env_asdr_add('vol', 0, a_attack, 0, a_decay, a_sustain, a_release, 1)

def parse_notes(cvpj_notelist, channum, bb_notes, bb_instruments):
	for note in bb_notes:
		points = note['points']
		pitches = note['pitches']

		pitches = [(x-48 + jummbox_key) for x in pitches]
		cvpj_note_dur = (points[-1]['tick'] - points[0]['tick'])

		arr_bendvals = []
		arr_volvals = []

		for point in points:
			arr_bendvals.append(point['pitchBend'])
			arr_volvals.append(point['volume'])

		maxvol = max(arr_volvals)
		t_vol = maxvol/100

		for bb_instrument in bb_instruments:
			t_instrument = text_instid(channum, bb_instrument)
			cvpj_notelist.add_m_multi(t_instrument, points[0]['tick'], cvpj_note_dur, pitches, t_vol, {})

			ifnotsame_gain = (all(element == arr_volvals[0] for element in arr_volvals) == False) and maxvol != 0
			ifnotsame_pitch = (all(element == arr_bendvals[0] for element in arr_bendvals) == False)

			for point in points:
				auto_pos = point['tick']-points[0]['tick']

				if ifnotsame_gain: 
					autopoint_obj = cvpj_notelist.last_add_auto('gain')
					autopoint_obj.pos = auto_pos
					autopoint_obj.value = (point['volume']*(1/maxvol))

				if ifnotsame_pitch: 
					autopoint_obj = cvpj_notelist.last_add_auto('pitch')
					autopoint_obj.pos = auto_pos
					autopoint_obj.value = point['pitchBend']

def add_inst_fx(convproj_obj, inst_obj, bb_fx, cvpj_instid):
	if 'echo' in bb_fx.used:
		from objects.inst_params import fx_delay
		fx_pluginid = cvpj_instid+'_echo'
		delay_obj = fx_delay.fx_delay()
		delay_obj.feedback_first = True
		delay_obj.feedback[0] = bb_fx.echoSustain/480
		timing_obj = delay_obj.timing_add(0)
		timing_obj.set_steps(bb_fx.echoDelayBeats*8, convproj_obj)
		fxplugin_obj, _ = delay_obj.to_cvpj(convproj_obj, fx_pluginid)
		fxplugin_obj.visual.name = 'Echo'
		fxplugin_obj.fxdata_add(1, 0.5)
		inst_obj.plugslots.slots_audio.append(fx_pluginid)
		
	if 'distortion' in bb_fx.used:
		fxplugin_obj = addfx(convproj_obj, inst_obj, 'simple', cvpj_instid, 'distortion', None)
		fxplugin_obj.visual.name = 'Distortion'
		param_obj = fxplugin_obj.params.add_named('amount', bb_fx.distortion/100, 'float', 'Amount')
	
	if 'bitcrusher' in bb_fx.used:
		fxplugin_obj = addfx(convproj_obj, inst_obj, 'universal', cvpj_instid, 'bitcrush', None)
		fxplugin_obj.visual.name = 'Bitcrusher'
		t_bits_val = round(xtramath.between_from_one(7, 0, bb_fx.bitcrusherQuantization/100))
		fxplugin_obj.params.add('bits', 2**t_bits_val, 'float')
		fxplugin_obj.params.add('freq', (bb_fx.bitcrusherOctave+1)*523.25, 'float')
		
	if 'chorus' in bb_fx.used:
		fxplugin_obj = addfx(convproj_obj, inst_obj, 'simple', cvpj_instid, 'chorus', None)
		fxplugin_obj.visual.name = 'Chorus'
		fxplugin_obj.params.add_named('amount', bb_fx.chorus/100, 'float', 'Amount')
		
	if 'reverb' in bb_fx.used:
		fxplugin_obj = addfx(convproj_obj, inst_obj, 'simple', cvpj_instid, 'reverb', None)
		fxplugin_obj.visual.name = 'Reverb'
		fxplugin_obj.fxdata_add(1, bb_fx.reverb/100)
						
class input_jummbox(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'jummbox'
	def get_name(self): return 'Beepbox/Jummbox'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['json']
		in_dict['file_ext_detect'] = False
		in_dict['auto_types'] = ['pl_points']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['native:jummbox','universal:eq:bands','universal:delay','simple:distortion','universal:bitcrush','simple:chorus','simple:reverb']
		in_dict['projtype'] = 'mi'

	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_jummbox

		convproj_obj.type = 'mi'
		convproj_obj.set_timings(16, True)

		globalstore.dataset.load('beepbox', './data_main/dataset/beepbox.dset')

		colors_pitch = colors.colorset.from_dataset('beepbox', 'inst', 'beepbox_dark')
		colors_drums = colors.colorset.from_dataset('beepbox', 'drums', 'beepbox_dark')

		rawchipwaves_obj = rawchipwaves()
		rawchipwaves_obj.load_from_file(os.path.join('data_main','text','beepbox_shapes.txt')) 

		bytestream = open(input_file, 'r', encoding='utf8')

		try:
			jummbox_json = json.load(bytestream)
		except UnicodeDecodeError as t:
			raise ProjectFileParserException('jummbox: File is not text')
		except json.decoder.JSONDecodeError as t:
			raise ProjectFileParserException('jummbox: JSON parsing error: '+str(t))

		jummbox_obj = proj_jummbox.jummbox_project(jummbox_json)
		convproj_obj.params.add('bpm', jummbox_obj.beatsPerMinute, 'float')
		convproj_obj.track_master.params.add('vol', jummbox_obj.masterGain, 'float')
		if jummbox_obj.name: convproj_obj.metadata.name = jummbox_obj.name
		jummbox_key = noteoffset[jummbox_obj.key]
		
		jummbox_obj.get_durpos()
		durpos = jummbox_obj.get_durpos()

		convproj_obj.timesig = [4,8]
		convproj_obj.timemarker__from_patlenlist(durpos, -1)

		for channum, bb_chan in enumerate(jummbox_obj.channels):
			if bb_chan.type in ['pitch', 'drum']:
				if bb_chan.type == 'pitch': bb_color = colors_pitch.getcolor()
				if bb_chan.type == 'drum': bb_color = colors_drums.getcolor()

				chan_insts = []
				for instnum, bb_inst in enumerate(bb_chan.instruments):
					bb_fx = bb_inst.fx

					cvpj_instid = text_instid(channum, instnum+1)
					chan_insts.append(cvpj_instid)

					cvpj_volume = (bb_inst.volume/50)+0.5
					preset = str(bb_inst.preset) if bb_inst.preset else None

					main_dso = globalstore.dataset.get_obj('beepbox', 'preset', bb_inst.preset)
					ds_bb = main_dso.midi if main_dso else None

					midifound = False
					if ds_bb:
						if ds_bb.used != False:
							midifound = True
							inst_obj, plugin_obj = convproj_obj.instrument__add_from_dset(cvpj_instid, preset, 'beepbox', preset, None, bb_color)

					if not midifound:
						inst_obj = convproj_obj.instrument__add(cvpj_instid)
						inst_obj.plugslots.set_synth(cvpj_instid)
						plugin_obj = convproj_obj.plugin__add(cvpj_instid, 'native', 'jummbox', bb_inst.type)

						if 'unison' in bb_inst.data: plugin_obj.datavals.add('unison', bb_inst.data['unison'])

						if bb_chan.type == 'pitch': inst_obj.visual.from_dset('beepbox', 'inst', bb_inst.type, False)
						if bb_chan.type == 'drum': 
							inst_obj.visual.from_dset('beepbox', 'drums', bb_inst.type, False)
							inst_obj.is_drum = True

						if bb_inst.type == 'chip':
							bb_inst_wave = bb_inst.data['wave']
							inst_obj.visual.name = data_values.text__insidename_type(inst_obj.visual.name, bb_inst_wave, bb_inst.type)
							rawchipwaves_obj.apply_wave(plugin_obj, bb_inst_wave, 'chipwave')
				
						if bb_inst.type == 'PWM':
							pulseWidth = bb_inst.data['pulseWidth']
							inst_obj.visual.name = str(pulseWidth)+'% pulse ('+inst_obj.visual.name+')'
							param_obj = plugin_obj.params.add("pulse_width", pulseWidth/100, 'float')
							param_obj.visual.name = "Pulse Width"
				
						if bb_inst.type == 'harmonics':
							harmonics_obj = plugin_obj.harmonics_add('harmonics')
							get_harmonics(harmonics_obj, bb_inst.data['harmonics'])
				
						if bb_inst.type == 'Picked String':
							harmonics_obj = plugin_obj.harmonics_add('harmonics')
							get_harmonics(harmonics_obj, bb_inst.data['harmonics'])

						if bb_inst.type == 'spectrum':
							plugin_obj.datavals.add('spectrum', bb_inst.data['spectrum'])
				
						if bb_inst.type == 'FM':
							plugin_obj.datavals.add('algorithm', bb_inst.data['algorithm'])
							plugin_obj.datavals.add('feedback_type', bb_inst.data['feedbackType'])
							param_obj = plugin_obj.params.add("feedback_amplitude", bb_inst.data['feedbackAmplitude'], 'int')
							param_obj.visual.name = "Feedback Amplitude"
				
							for opnum in range(4):
								opdata = bb_inst.data['operators'][opnum]
								opnumtext = 'op'+str(opnum+1)+'/'
								plugin_obj.datavals.add(opnumtext+'frequency', opdata['frequency'])
								plugin_obj.datavals.add(opnumtext+'waveform', data_values.get_value(opdata, 'waveform', 'sine'))
								plugin_obj.datavals.add(opnumtext+'pulseWidth', data_values.get_value(opdata, 'pulseWidth', 0))
								plugin_obj.params.add(opnumtext+"amplitude", opdata['amplitude'], 'int')
				
						if bb_inst.type == 'custom chip':
							customChipWave = bb_inst.data['customChipWave']
							customChipWave = [customChipWave[str(i)] for i in range(64)]
							wave_obj = plugin_obj.wave_add('chipwave')
							wave_obj.set_all_range(customChipWave, -24, 24)
				
						if bb_inst.type == 'FM6op': #goldbox
							plugin_obj.datavals.add('algorithm', bb_inst.data['algorithm'])
							plugin_obj.datavals.add('feedback_type', bb_inst.data['feedbackType'])
							param_obj = plugin_obj.params.add_named("feedback_amplitude", bb_inst.data['feedbackAmplitude'], 'int', "Feedback Amplitude")
				
							for opnum in range(4):
								opdata = bb_inst.data['operators'][opnum]
								opnumtext = 'op'+str(opnum+1)+'_'
								plugin_obj.datavals.add(opnumtext+'frequency', opdata['frequency'])
								plugin_obj.datavals.add(opnumtext+'waveform', data_values.get_value(opdata, 'waveform', 'sine'))
								plugin_obj.datavals.add(opnumtext+'pulseWidth', data_values.get_value(opdata, 'pulseWidth', 0))
								plugin_obj.params.add(opnumtext+"amplitude", opdata['amplitude'], 'int')
				
							if bb_inst.data['algorithm'] == 'Custom': plugin_obj.datavals.add('customAlgorithm', bb_inst.data['customAlgorithm'])

					inst_obj.visual.color.set_float(bb_color)
				
					inst_obj.params.add('vol', cvpj_volume, 'float')

					add_inst_fx(convproj_obj, inst_obj, bb_fx, cvpj_instid)

					if 'vibrato' in bb_fx.used:
						if bb_fx.vibratoSpeed != 0 and bb_fx.vibratoDelay != 50:
							lfo_obj = plugin_obj.lfo_add('pitch')
							lfo_obj.predelay = (bb_fx.vibratoDelay/49)*2
							lfo_obj.time.set_seconds(0.7*(1/bb_fx.vibratoSpeed))
							lfo_obj.amount = bb_fx.vibratoDepth
			
					get_asdr(plugin_obj, bb_inst, jummbox_obj)
					plugin_obj.role = 'synth'

				for patnum, bb_pat in enumerate(bb_chan.patterns):
					nid_name = 'Ch#'+str(channum+1)+' Pat#'+str(patnum+1)
					cvpj_patid = text_patternid(channum, patnum)
					if bb_pat.notes:
						nle_obj = convproj_obj.notelistindex__add(cvpj_patid)
						nle_obj.visual.name = nid_name
						nle_obj.visual.color.set_float(bb_color)
						for note in bb_pat.notes:
							points = note.points
							pitches = [(x-48 + jummbox_key) for x in note.pitches]
							pos = points[0][0]
							dur = points[-1][0]-points[0][0]

							arr_bendvals = []
							arr_volvals = []
							for point in points:
								arr_bendvals.append(point[1])
								arr_volvals.append(point[2])

							maxvol = max(arr_volvals)
							t_vol = maxvol/100

							for instnum, chan_inst in enumerate(chan_insts):
								t_instrument = 'bb_ch'+str(channum)+'_inst'+str(instnum+1)
								nle_obj.notelist.add_m_multi(t_instrument, pos, dur, pitches, t_vol, {})
								ifnotsame_gain = (not all(x == arr_volvals[0] for x in arr_volvals)) and maxvol != 0
								ifnotsame_pitch = (not all(x == arr_bendvals[0] for x in arr_bendvals))

								for point in points:
									auto_pos = point[0]-pos
				
									if ifnotsame_gain: 
										autopoint_obj = nle_obj.notelist.last_add_auto('gain')
										autopoint_obj.pos = auto_pos
										autopoint_obj.value = (point[2]*(1/maxvol))
				
									if ifnotsame_pitch: 
										autopoint_obj = nle_obj.notelist.last_add_auto('pitch')
										autopoint_obj.pos = auto_pos
										autopoint_obj.value = point[1]

				placement_pos = 0
				for seqpos, patnum in enumerate(bb_chan.sequence):
					bb_partdur = durpos[seqpos]
					if patnum != 0:
						playlist_obj = convproj_obj.playlist__add(channum, True, True)
						playlist_obj.visual.color.set_float(bb_color)
						cvpj_placement = playlist_obj.placements.add_notes_indexed()
						cvpj_placement.fromindex = text_patternid(channum, patnum-1)
						cvpj_placement.time.set_posdur(placement_pos, bb_partdur)
					placement_pos += bb_partdur
			else:
				modChannels = bb_chan.instruments[0].modChannels
				modInstruments = bb_chan.instruments[0].modInstruments
				modSettings = bb_chan.instruments[0].modSettings

				bb_def = []
				for num in range(6):
					autot_obj = jummbox_autotype()
					autot_obj.tracknum = modChannels[num]
					autot_obj.instrument = modInstruments[num]
					autot_obj.param = modSettings[num]
					bb_def.append(autot_obj)

				placement_pos = 0
				for seqpos, patnum in enumerate(bb_chan.sequence):
					if patnum != 0:
						bb_pat = bb_chan.patterns[patnum-1]
						for note in bb_pat.notes:
							autot_obj = bb_def[note.pitches[0]]
							pos = note.points[0][0]
							ap = [[x[0]-pos, x[2]] for x in note.points]
							plpos = placement_pos+pos

							autoloc, m_add, m_mul = autot_obj.get_data()

							if autot_obj.tracknum > -1:
								if autot_obj.param == 25: 
									for s_ap in t_ap: s_ap[1] = 2**(7-s_ap[1])
								if autot_obj.param == 26: 
									for s_ap in t_ap: s_ap[1] = (s_ap[1]+1)*523.25

							if autoloc:
								autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
								autopl_obj.time.position = placement_pos+pos
								autopl_obj.time.duration = ap[-1][0]

								for s_ap in ap: 
									autopoint_obj = autopl_obj.data.add_point()
									autopoint_obj.pos = s_ap[0]
									autopoint_obj.value = (s_ap[1]*m_mul)+m_add

					placement_pos += bb_partdur

		#if 'introBars' in jummbox_json and 'loopBars' in jummbox_json:
		#	introbars = sum(patlentable[0:jummbox_json['introBars']])
		#	loopbars = (sum(patlentable[0:jummbox_json['loopBars']]) + introbars)
		#	convproj_obj.loop_active = True
		#	convproj_obj.loop_start = introbars
		#	convproj_obj.loop_end = loopbars if loopbars else patlentable[-1]

		#convproj_obj.automation.sort()

		convproj_obj.do_actions.append('do_addloop')
