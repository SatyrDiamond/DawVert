# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
import io
import os.path
import plugins

TEXTSTART = 'it_inst_'
MAINCOLOR = [0.71, 0.58, 0.47]

def env_to_cvpj(it_env, plugin_obj, t_type, i_div): 
	autopoints_obj = plugin_obj.env_points_add(t_type, 48, False, 'float')
	autopoints_obj.sustain_on = bool(2 in it_env.flags)
	autopoints_obj.sustain_point = it_env.susloop_start
	autopoints_obj.sustain_end = it_env.susloop_end
	autopoints_obj.loop_on = bool(1 in it_env.flags)
	autopoints_obj.loop_start = it_env.loop_start
	autopoints_obj.loop_end = it_env.loop_end

	for pv, pp in it_env.env_points:
		autopoint_obj = autopoints_obj.add_point()
		autopoint_obj.pos = pp
		autopoint_obj.value = pv/i_div

	maxval = max([i[1]/i_div for i in it_env.env_points]) if it_env.env_points else 1
	return autopoints_obj, maxval

def sample_vibrato(it_samp, plugin_obj): 
	vibrato_on, vibrato_sweep, vibrato_wave, vibrato_speed, vibrato_depth = it_samp.vibrato_lfo()
	if vibrato_on:
		vibrato_speed = vibrato_speed
		lfo_obj = plugin_obj.lfo_add('pitch')
		lfo_obj.attack = vibrato_sweep
		lfo_obj.prop.shape = vibrato_wave
		lfo_obj.time.set_hz(vibrato_speed/2)
		lfo_obj.amount = vibrato_depth

def get_name(inst_name, dosfilename):
	if inst_name != '': return inst_name
	elif dosfilename != '': return dosfilename
	else: return " "

def calc_samp_vol(it_samp):
	defualtvolume = it_samp.defualtvolume/64
	samp_global_vol = it_samp.globalvol/64
	return defualtvolume*samp_global_vol

def calc_filter_freq(i_cutoff):
	return 131.0 * pow(2.0, (i_cutoff*512) * (5.29 / (127.0 * 512.0)))

def add_filter(plugin_obj, i_cutoff, i_reso):
	if i_cutoff != None:
		if i_cutoff != 127:
			plugin_obj.filter.on = True
			plugin_obj.filter.freq = calc_filter_freq(i_cutoff)
			plugin_obj.filter.q = ((i_reso/127)*6 + 1) if i_reso != None else 1
			plugin_obj.filter.type.set('low_pass', None)

def idsamp_spobj(it_samp, sp_obj):
	sp_obj.point_value_type = "samples"
	sp_obj.end = it_samp.length
	sp_obj.loop_active = 4 in it_samp.flags
	sp_obj.loop_mode =  'normal' if not (6 in it_samp.flags) else 'pingpong'
	sp_obj.loop_start = it_samp.loop_start
	sp_obj.loop_end = it_samp.loop_end

def add_single_sampler(convproj_obj, it_samp, sampleidnum):
	filename = samplefolder+str(sampleidnum)+'.wav'
	plugin_obj, pluginid, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler__genid(filename, None)
	idsamp_spobj(it_samp, sp_obj)
	sample_vibrato(it_samp, plugin_obj)
	return plugin_obj, pluginid, sampleref_obj

class input_it(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'it'
	def get_name(self): return 'Impulse Tracker'
	def get_priority(self): return 0
	def get_prop(self, in_dict):
		in_dict['file_ext'] = ['it']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['universal:sampler:single', 'universal:sampler:multi']
	def supported_autodetect(self): return True

	def detect_bytes(self, in_bytes):
		bytestream = io.BytesIO(in_bytes)
		return self.detect_internal(bytestream)

	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		return self.detect_internal(bytestream)

	def detect_internal(self, bytestream):
		bytesdata = bytestream.read(4)
		if bytesdata == b'IMPM': return True
		else: return False
		bytestream.seek(0)

	def parse_bytes(self, convproj_obj, input_bytes, dv_config, input_file):
		from objects.file_proj import proj_it
		project_obj = proj_it.it_song()
		if not project_obj.load_from_raw(input_bytes): exit()
		self.parse_internal(convproj_obj, project_obj, dv_config, input_file)

	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_it
		project_obj = proj_it.it_song()
		if not project_obj.load_from_file(input_file): exit()
		self.parse_internal(convproj_obj, project_obj, dv_config, input_file)

	def parse_internal(self, convproj_obj, project_obj, dv_config, input_file):
		from objects.tracker import pat_single
		global samplefolder

		try: import xmodits
		except: xmodits_exists = False
		else: xmodits_exists = True

		samplefolder = dv_config.path_samples_extracted
		
		it_useinst = 2 in project_obj.flags

		table_orders = list(project_obj.l_order.copy())
		while -2 in table_orders: table_orders.remove(-2)
		while -1 in table_orders: table_orders.remove(-1)
		
		if xmodits_exists == True and input_file:
			if not os.path.exists(samplefolder): os.makedirs(samplefolder)
			try: xmodits.dump(input_file, samplefolder, index_only=True, index_raw=True, index_padding=0)
			except: pass

		patterndata_obj = pat_single.single_patsong(64, TEXTSTART, MAINCOLOR)
		patterndata_obj.orders = table_orders

		for patnum, itpat_obj in enumerate(project_obj.patterns):
			if itpat_obj.used:
				pattern_obj = patterndata_obj.pattern_add(patnum, itpat_obj.rows)
				for rownum, rowdatas in enumerate(itpat_obj.data):
					for cell_channel, cell_note, cell_instrument, cell_volpan, cell_commandtype, cell_commandval in rowdatas:
						out_note = None
						out_vol = 64
						out_pan = None

						out_inst = cell_instrument if cell_instrument != None else None
						
						if cell_volpan != None:
							if cell_volpan <= 64: out_vol = cell_volpan
							elif 192 >= cell_volpan >= 128: out_pan = ((cell_volpan-128)/64-0.5)*2
		
						if cell_note != None: out_note = cell_note - 60
						if cell_note == 254: out_note = 'cut'
						if cell_note == 255: out_note = 'off'
						if cell_note == 246: out_note = 'fade'

						pattern_obj.cell_note(cell_channel, rownum, out_note, out_inst)
						pattern_obj.cell_param(cell_channel, rownum, 'vol', out_vol/64)
						if out_pan != None: pattern_obj.cell_param(cell_channel, rownum, 'pan', out_pan)
						pattern_obj.cell_fx_s3m(cell_channel, rownum, cell_commandtype, cell_commandval)
						if cell_commandtype == 20: pattern_obj.cell_g_param(cell_channel, rownum, 'tempo', cell_commandval)
						if cell_commandtype == 26: pattern_obj.cell_param(cell_channel, rownum, 'pan', ((cell_commandval/255)-0.5)*2)

		if project_obj.ompt_cnam:
			for n, t in enumerate(project_obj.ompt_cnam):
				if t: patterndata_obj.channels[n].name = t

		if project_obj.ompt_pnam:
			for n, t in enumerate(project_obj.ompt_pnam):
				if t: project_obj.patterns[n].name = t

		if project_obj.plugins:
			for fxnum, plugdata in project_obj.plugins.items():
				plugdata.to_cvpj(fxnum, convproj_obj)

		if project_obj.ompt_chfx:
			for n, t in enumerate(project_obj.ompt_chfx):
				if t: patterndata_obj.channels[n].fx_plugins.append('FX'+str(t))

		patterndata_obj.to_cvpj(convproj_obj, TEXTSTART, project_obj.tempo, project_obj.speed, False, MAINCOLOR)

		for n in range(64):
			ch_pan = ((project_obj.l_chnpan[n]&127)/32)-1
			ch_mute = bool(project_obj.l_chnpan[n]&128)
			ch_vol = project_obj.l_chnvol[n]/64
			if n in convproj_obj.playlist:
				s_pl = convproj_obj.playlist[n]
				if ch_pan != 2.125: s_pl.params.add('pan', ch_pan, 'float')
				s_pl.params.add('vol', ch_vol, 'float')
				s_pl.params.add('on', not ch_mute, 'bool')

		track_volume = 0.3

		if it_useinst:
			for instrumentcount, it_inst in enumerate(project_obj.instruments):
				it_instname = TEXTSTART + str(instrumentcount+1)
				
				cvpj_instname = get_name(it_inst.name, it_inst.dosfilename)

				n_s_t = it_inst.notesampletable
				bn_s_t = []

				basenoteadd = 60
				for n_s_te in n_s_t:
					bn_s_t.append([n_s_te[0]+basenoteadd, n_s_te[1]])
					basenoteadd -= 1

				bn_s_t_ifsame = data_values.list__ifallsame(bn_s_t)
				if bn_s_t_ifsame: bn_s_t_f = bn_s_t[0]

				bn_s_t_ifsame = data_values.list__ifallsame(bn_s_t[12:108])
				if bn_s_t_ifsame: bn_s_t_f = bn_s_t[12]

				inst_obj = convproj_obj.instrument__add(it_instname)
				inst_obj.visual.name = cvpj_instname
				inst_obj.visual.color.set_float(MAINCOLOR)

				if bn_s_t_ifsame:
					if (not ''.join(list(map(lambda x: x.strip(), cvpj_instname.split())))):
						if bn_s_t_f[1] <= len(project_obj.samples):
							inst_obj.visual.name = project_obj.samples[bn_s_t_f[1]-1].name
							if not inst_obj.visual.name: 
								inst_obj.visual.name = project_obj.samples[bn_s_t_f[1]-1].dosfilename

				if it_inst.pitch_pan_separation:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'pitch_pan_separation', None)
					plugin_obj.params.add('range', 1/(it_inst.pitch_pan_separation/32), 'float')
					plugin_obj.datavals.add('center_note', it_inst.pitch_pan_center)
					inst_obj.fxslots_notes.append(pluginid)

				if it_inst.randomvariation_volume:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'random_variation', 'vol')
					plugin_obj.params.add('amount', it_inst.randomvariation_volume, 'float')
					inst_obj.fxslots_notes.append(pluginid)

				if it_inst.randomvariation_pan:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'random_variation', 'pan')
					plugin_obj.params.add('amount', it_inst.randomvariation_pan, 'float')
					inst_obj.fxslots_notes.append(pluginid)

				inst_used = False
				if bn_s_t_ifsame == True:

					if bn_s_t_f[1]-1 < len(project_obj.samples):
						it_samp = project_obj.samples[bn_s_t_f[1]-1]
						global_vol = it_inst.global_vol/128
						track_volume = 0.3*global_vol*calc_samp_vol(it_samp)
						plugin_obj, inst_obj.pluginid, sampleref_obj = add_single_sampler(convproj_obj, it_samp, bn_s_t_f[1])
						inst_used = True
				else:
					inst_used = True
					sampleregions = data_values.list__to_reigons(bn_s_t, 60)

					plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
					plugin_obj.datavals.add('point_value_type', "samples")

					global_vol = it_inst.global_vol/128
					track_volume = 0.3*global_vol

					for sampleregion in sampleregions:
						instrumentnum = sampleregion[0][1]

						filename = samplefolder + str(instrumentnum) + '.wav'
						sampleref_obj = convproj_obj.sampleref__add(filename, filename, None)
						sp_obj = plugin_obj.sampleregion_add(sampleregion[1], sampleregion[2], -(sampleregion[0][0]-60), None)
						sp_obj.sampleref = filename
						if instrumentnum-1 < len(project_obj.samples): 
							idsamp_spobj(project_obj.samples[instrumentnum-1], sp_obj)

				if inst_used:
					interpolation = data_values.list__optionalindex(it_inst.resampling, 'linear', ['none','linear','cubic_spline','sinc','sinc_lowpass'])
					plugin_obj.datavals.add('interpolation', interpolation)

				if it_inst.midi_chan != None: 
					inst_obj.midi.out_enabled = 1
					inst_obj.midi.out_chan = it_inst.midi_chan+1
				if it_inst.midi_inst != None: inst_obj.midi.out_patch = it_inst.midi_inst+1
				if it_inst.midi_bank != None: inst_obj.midi.out_bank = it_inst.midi_bank+1

				if inst_used:
					autopoints_obj, maxvol = env_to_cvpj(it_inst.env_vol, plugin_obj, 'vol', 48)
					if it_inst.fadeout != 0 and it_inst.new_note_action != 0: 
						autopoints_obj.data['fadeout'] = (256/it_inst.fadeout)/8
					autopoints_obj.data['use_fadeout'] = it_inst.new_note_action!=0
					autopoints_obj, _ = env_to_cvpj(it_inst.env_pan, plugin_obj, 'pan', 48)
					if 7 in it_inst.env_pitch.flags: 
						it_inst.env_pitch.env_points = [[calc_filter_freq(pv), pp] for pv, pp in it_inst.env_pitch.env_points]
						autopoints_obj, _ = env_to_cvpj(it_inst.env_pitch, plugin_obj, 'cutoff', 1)
					else:
						autopoints_obj, _ = env_to_cvpj(it_inst.env_pitch, plugin_obj, 'pitch', 48)

					if not (0 in it_inst.env_pitch.flags and 7 in it_inst.env_pitch.flags): 
						filtercutoff = it_inst.filtercutoff-128 if it_inst.filtercutoff >= 128 else None
						filterresonance = it_inst.filterresonance-128 if it_inst.filterresonance >= 128 else None
						add_filter(plugin_obj, filtercutoff, filterresonance)

					plugin_obj.env_asdr_from_points('vol')

				if it_inst.filtermode == 1: plugin_obj.filter.type = 'high_pass'

				if it_inst.pluginnum: inst_obj.fxslots_audio.append('FX'+str(it_inst.pluginnum))

				inst_obj.params.add('vol', track_volume, 'float')
				if it_inst.default_pan < 128: inst_obj.params.add('pan', (it_inst.default_pan/32)-1, 'float')

		if it_useinst == 0:
			for samplecount, it_samp in enumerate(project_obj.samples):
				it_instname = TEXTSTART + str(samplecount+1)
				cvpj_instname = get_name(it_samp.name, it_samp.dosfilename)
				track_volume = 0.3*calc_samp_vol(it_samp)

				inst_obj = convproj_obj.instrument__add(it_instname)
				inst_obj.visual.name = cvpj_instname
				inst_obj.visual.color.set_float(MAINCOLOR)
				plugin_obj, inst_obj.pluginid, sampleref_obj = add_single_sampler(convproj_obj, it_samp, samplecount+1)
				inst_obj.params.add('vol', track_volume, 'float')

		convproj_obj.track_master.params.add('vol', project_obj.globalvol/128, 'float')

		# ------------- Song Message -------------
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_lanefit')
		convproj_obj.params.add('bpm', project_obj.tempo/(project_obj.speed/6), 'float')

		convproj_obj.metadata.name = project_obj.title
		convproj_obj.metadata.comment_text = project_obj.songmessage