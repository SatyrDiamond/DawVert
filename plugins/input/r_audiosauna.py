# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import colors
from objects import globalstore
import plugins
import zipfile
import os

def setasdr(plugin_obj, asdr_name, i_dict, sustain_hundred, n_attack, n_decay, n_release, n_sustain):
	out_attack = float(getvalue(i_dict, n_attack)) if n_attack else -1
	out_decay = float(getvalue(i_dict, n_decay)) if n_decay else -1
	out_release = float(getvalue(i_dict, n_release)) if n_release else -1
	out_sustain = float(getvalue(i_dict, n_sustain)) if n_sustain else -1
	if out_decay == 0: out_sustain = 1
	if sustain_hundred: out_sustain = out_sustain/100
	plugin_obj.env_asdr_add(asdr_name, 0, out_attack, 0, out_decay, out_sustain, out_release, 1)
	return out_attack, out_decay, out_release, out_sustain

def getvalue(i_dict, i_id):
	return i_dict[i_id] if i_id in i_dict else 0

audiosanua_device_id = ['fm', 'analog']
delay_sync = [[1, 64, ''],[1, 64, 't'],[1, 64, 'd'],[1, 32, ''],[1, 32, 't'],[1, 32, 'd'],[1, 16, ''],[1, 16, 't'],[1, 16, 'd'],[1, 8, ''],[1, 8, 't'],[1, 8, 'd'],[1, 4, ''],[1, 4, 't'],[1, 4, 'd'],[1, 2, ''],[1, 2, 't'],[1, 2, 'd'],[1, 1, '']]
op_lfo_shapes = ['saw','square','triangle','random','sine']

class input_audiosanua(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'audiosauna'
	def get_name(self): return 'AudioSauna'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['song']
		in_dict['placement_cut'] = True
		in_dict['audio_filetypes'] = ['wav', 'mp3']
		in_dict['plugin_included'] = ['native:audiosauna', 'universal:sampler:multi', 'universal:bitcrush']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'r'
	def supported_autodetect(self): return True
	def detect(self, input_file): 
		try:
			zip_data = zipfile.ZipFile(input_file, 'r')
			if 'songdata.xml' in zip_data.namelist(): return True
			else: return False
		except:
			return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_audiosauna

		global cvpj_l

		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'r'
		convproj_obj.set_timings(128, False)

		# ------------------------------------------ Start ------------------------------------------
		globalstore.dataset.load('audiosauna', './data_main/dataset/audiosauna.dset')
		colordata = colors.colorset.from_dataset('audiosauna', 'track', 'main')

		project_obj = proj_audiosauna.audiosauna_song()
		zip_data = project_obj.load_from_file(input_file)
		samplefolder = dv_config.path_samples_extracted

		# ------------------------------------------ Main ------------------------------------------
		convproj_obj.params.add('bpm', project_obj.appTempo, 'float')
		convproj_obj.track_master.visual.name = 'Master'
		convproj_obj.track_master.params.add('vol', project_obj.appMasterVolume/100, 'float')

		# ------------------------------------------ Tape Delay ------------------------------------------
		return_obj = convproj_obj.track_master.fx__return__add('audiosauna_send_tape_delay')
		return_obj.visual.name = 'Tape Delay'
		return_obj.params.add('vol', project_obj.dlyLevel/100, 'float')

		plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'audiosauna', 'tape_delay')
		plugin_obj.role = 'effect'
		plugin_obj.visual.name = 'Tape Delay'
		timing_obj = plugin_obj.timing_add('main')
		if project_obj.dlySync: 
			numer, denum, letter = delay_sync[int(project_obj.dlyTime)]
			timing_obj.set_frac(numer, denum, letter, convproj_obj)
		else: timing_obj.set_seconds(project_obj.dlyTime)
		plugin_obj.params.add_named("time", project_obj.dlyTime, 'float', "Time")
		plugin_obj.params.add_named("damage", project_obj.dlyDamage/100, 'float', "Damage")
		plugin_obj.params.add_named("feedback", project_obj.dlyFeed/100, 'float', "Feedback")
		plugin_obj.params.add_named("sync", project_obj.dlySync, 'bool', "Sync")
		return_obj.fxslots_audio.append(pluginid)

		# ------------------------------------------ Reverb ------------------------------------------
		return_obj = convproj_obj.track_master.fx__return__add('audiosauna_send_reverb')
		return_obj.visual.name = 'Reverb'
		return_obj.params.add('vol', project_obj.rvbLevel/100, 'float')

		plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'audiosauna', 'reverb')
		plugin_obj.role = 'effect'
		plugin_obj.visual.name = 'Reverb'
		plugin_obj.params.add_named("time", project_obj.rvbTime, 'float', 'Time')
		plugin_obj.params.add_named("feedback", project_obj.rvbFeed/100, 'float', 'Feedback')
		plugin_obj.params.add_named("width", project_obj.rvbWidth/100, 'float', 'Width')
		return_obj.fxslots_audio.append(pluginid)

		# ------------------------------------------ Tracks ------------------------------------------
		for as_channum, as_chan in project_obj.channels.items():
			cvpj_trackid = 'audiosanua'+str(as_channum)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
			track_obj.visual.name = as_chan.name
			track_obj.visual.color.set_float(colordata.getcolornum(as_channum))
			track_obj.params.add('vol', as_chan.volume/100, 'float')
			track_obj.params.add('pan', as_chan.pan/100, 'float')
			track_obj.params.add('enabled', not as_chan.mute, 'bool')
			track_obj.params.add('solo', as_chan.solo, 'bool')
			track_obj.sends.add('audiosauna_send_tape_delay', None, as_chan.delay/100)
			track_obj.sends.add('audiosauna_send_reverb', None, as_chan.reverb/100)

			for as_pattern in as_chan.patterns:
				pat_notes = as_chan.track.notes[as_pattern.patternId]

				placement_obj = track_obj.placements.add_notes()
				placement_obj.time.set_startend(as_pattern.startTick, as_pattern.endTick)
				placement_obj.time.set_loop_data(0, 0, as_pattern.patternLength)
				placement_obj.visual.color.set_float(colordata.getcolornum(as_pattern.patternColor))

				for t_note in pat_notes: 
					n_pos = max(0,t_note.startTick-as_pattern.startTick)
					n_dur = t_note.endTick-t_note.startTick
					n_key = t_note.pitch-60
					n_volume = t_note.noteVolume/100
					n_extra = {'cutoff': 1-(t_note.noteCutoff/100)}
					placement_obj.notelist.add_r(n_pos, n_dur, n_key, n_volume, n_extra)

			if as_chan.device != None:
				as_device = as_chan.device

				windata_obj = convproj_obj.viswindow__add(['plugin',cvpj_trackid])
				windata_obj.pos_x = as_device.xpos
				windata_obj.pos_y = as_device.ypos
				windata_obj.open = as_device.visible

				if as_device.deviceType == 1 or as_device.deviceType == 0:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'audiosauna', audiosanua_device_id[as_device.deviceType])
					plugin_obj.role = 'synth'
					track_obj.inst_pluginid = pluginid

					fldso = globalstore.dataset.get_obj('audiosauna', 'plugin', str(as_device.deviceType))
					if fldso:
						for param_id, dset_param in fldso.params.iter():
							outval = as_device.params[param_id] if param_id in as_device.params else None
							plugin_obj.dset_param__add(param_id, outval, dset_param)

					setasdr(plugin_obj, 'vol', as_device.params, False, 'attack', 'decay', 'release', 'sustain')

					if as_device.deviceType == 1: oprange = 2
					if as_device.deviceType == 0: oprange = 4

					for opnum in range(oprange):
						opnumtxt = str(opnum+1)
	
						setasdr(plugin_obj, 'op'+opnumtxt, as_device.params, True, 'aOp'+opnumtxt, 'dOp'+opnumtxt, None, 'sOp'+opnumtxt)

						osc_data = plugin_obj.osc_add()
						osc_data.env['vol'] = 'op'+opnumtxt
	
						if as_device.deviceType == 0: 
							as_oct = int(getvalue(as_device.params, 'oct'+opnumtxt))*12
							as_fine = float(getvalue(as_device.params, 'fine'+opnumtxt))
							as_semi = int(getvalue(as_device.params, 'semi'+opnumtxt))
							as_shape = int(getvalue(as_device.params, 'wave'+opnumtxt))
							as_vol = int(getvalue(as_device.params, 'osc'+opnumtxt+'Vol'))
							osc_data.prop.shape = op_lfo_shapes[as_shape]
							osc_data.params['course'] = as_oct+as_fine
							osc_data.params['fine'] = as_semi/100
							osc_data.params['vol'] = as_vol

				if as_device.deviceType == 2:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
					plugin_obj.role = 'synth'

					for num, as_cell in as_device.samples.items():
						sp_obj = plugin_obj.sampleregion_add(as_cell.loKey-60, as_cell.hiKey-60, as_cell.rootKey-60, None)
						sp_obj.visual.name = as_cell.name

						if as_cell.url != 'undefined':
							sampleref_obj = convproj_obj.sampleref__add(as_cell.url, as_cell.url, None)
							sp_obj.sampleref = as_cell.url
						else:
							samp_filename = 'sample_'+str(as_channum)+'_'+str(num)+'.wav'
							full_filename = os.path.join(samplefolder,samp_filename)
							zip_data.extract(samp_filename, path=samplefolder, pwd=None)
							sampleref_obj = convproj_obj.sampleref__add(full_filename, full_filename, None)
							sp_obj.sampleref = full_filename

						sp_obj.point_value_type = "percent"
						sp_obj.reverse = as_cell.playMode != 'forward'
						sp_obj.vol = as_cell.volume/100
						sp_obj.pan = as_cell.pan/100
						sp_obj.start = as_cell.smpStart/100
						sp_obj.end = as_cell.smpEnd/100

						sp_obj.loop_active = as_cell.loopMode != 'off'
						sp_obj.loop_start = as_cell.loopStart/100
						sp_obj.loop_end = as_cell.loopEnd/100
						if as_cell.loopMode == 'ping-pong': sp_obj.loop_mode = 'pingpong'

						sp_obj.data['tone'] = as_cell.semitone
						sp_obj.data['fine'] = as_cell.finetone

					setasdr(plugin_obj, 'vol', as_device.params, False, 'masterAttack', 'masterDecay', 'masterRelease', 'masterSustain')

				# distortion
				modulate = float(getvalue(as_device.params, 'driveModul' if as_device.deviceType in [0,1] else 'modulate'))/100
				overdrive = float(getvalue(as_device.params, 'overdrive'))/100
				if modulate == overdrive == 0:
					fx_plugin_obj, fx_pluginid = convproj_obj.plugin__add__genid('native', 'audiosauna', 'distortion')
					fx_plugin_obj.role = 'effect'
					fx_plugin_obj.visual.name = 'Distortion'
					fx_plugin_obj.params.add_named("overdrive", overdrive, 'float', 'Overdrive')
					fx_plugin_obj.params.add_named("modulate", modulate, 'float', 'Modulate')
					track_obj.fxslots_audio.append(fx_pluginid)

				# bitcrush
				bitrateval = float(getvalue(as_device.params, 'bitrate'))
				if bitrateval != 0.0: 
					fx_plugin_obj, fx_pluginid = convproj_obj.plugin__add__genid('universal', 'bitcrush', None)
					fx_plugin_obj.role = 'effect'
					fx_plugin_obj.visual.name = 'Bitcrush'
					fx_plugin_obj.params.add("bits", 16, 'float')
					fx_plugin_obj.params.add("freq", 22050/bitrateval, 'float')
					track_obj.fxslots_audio.append(fx_pluginid)

				# chorus
				chorus_wet = float(getvalue(as_device.params, 'chorusMix' if as_device in [0,1] else 'chorusDryWet'))/100
				if chorus_wet != 0:
					fx_plugin_obj, fx_pluginid = convproj_obj.plugin__add__genid('native', 'audiosauna', 'chorus')
					fx_plugin_obj.role = 'effect'
					fx_plugin_obj.visual.name = 'Chorus'
					chorus_size = float(getvalue(as_device.params, 'chorusLevel' if as_device in [0,1] else 'chorusSize'))/100
					chorus_speed = float(getvalue(as_device.params, 'chorusSpeed'))/100
					fx_plugin_obj.fxdata_add(True, chorus_wet)
					fx_plugin_obj.params.add_named("speed", chorus_speed, 'float', 'Speed')
					fx_plugin_obj.params.add_named("size", chorus_size, 'float', 'Size')
					track_obj.fxslots_audio.append(fx_pluginid)
		
				# amp
				ampval = float(getvalue(as_device.params, 'masterAmp'))/100
				if ampval != 1.0: 
					fx_plugin_obj, fx_pluginid = convproj_obj.plugin__add__genid('universal', 'volpan', None)
					fx_plugin_obj.role = 'effect'
					fx_plugin_obj.visual.name = 'Amp'
					fx_plugin_obj.params.add_named("vol", ampval, 'float', 'Level')
					fx_plugin_obj.fxdata_add(True, 1)
		
				plugin_obj.datavals.add('middlenote', int(getvalue(as_device.params, 'masterTranspose'))*-1)

				audiosauna_filtertype = int(getvalue(as_device.params, 'filterType'))
				if audiosauna_filtertype == 0: filter_type = ['low_pass', None]
				if audiosauna_filtertype == 1: filter_type = ['high_pass', None]
				if audiosauna_filtertype == 2: filter_type = ["low_pass", "double"]

				pre_t_cutoff = int(getvalue(as_device.params, 'cutoff'))/100
				filter_cutoff = int(pre_t_cutoff)*7200
				plugin_obj.filter.on = True
				plugin_obj.filter.freq = int(pre_t_cutoff)*7200
				plugin_obj.filter.q = int(getvalue(as_device.params, 'resonance'))/100
				plugin_obj.filter.type.set_list(filter_type)

				setasdr(plugin_obj, 'cutoff', as_device.params, False, 'filterAttack', 'filterDecay', 'filterRelease', 'filterSustain')

				audiosauna_lfoActive = getvalue(as_device.params, 'lfoActive')
				audiosauna_lfoToggled = getvalue(as_device.params, 'lfoToggled') == 'true'
				audiosauna_lfoTime = float(getvalue(as_device.params, 'lfoTime'))
				audiosauna_lfoFilter = float(getvalue(as_device.params, 'lfoFilter'))
				audiosauna_lfoPitch = float(getvalue(as_device.params, 'lfoPitch'))
				audiosauna_lfoDelay = float(getvalue(as_device.params, 'lfoDelay'))
				audiosauna_lfoWaveForm = int(getvalue(as_device.params, 'lfoWaveForm'))

				p_lfo_amount = ((audiosauna_lfoPitch/100)*12)*audiosauna_lfoToggled
				c_lfo_amount = ((audiosauna_lfoFilter/100)*-7200)*audiosauna_lfoToggled
				g_lfo_attack = audiosauna_lfoDelay
				g_lfo_shape = ['triangle', 'square', 'random'][audiosauna_lfoWaveForm]
				g_lfo_speed = audiosauna_lfoTime

				lfo_obj = plugin_obj.lfo_add('pitch')
				lfo_obj.attack = g_lfo_attack
				lfo_obj.prop.shape = g_lfo_shape
				lfo_obj.time.set_seconds(g_lfo_speed)
				lfo_obj.amount = p_lfo_amount

				lfo_obj = plugin_obj.lfo_add('cutoff')
				lfo_obj.attack = g_lfo_attack
				lfo_obj.prop.shape = g_lfo_shape
				lfo_obj.time.set_seconds(g_lfo_speed)
				lfo_obj.amount = c_lfo_amount

		convproj_obj.loop_active = project_obj.appUseLoop
		convproj_obj.loop_start = project_obj.appLoopStart
		convproj_obj.loop_end = project_obj.appLoopEnd