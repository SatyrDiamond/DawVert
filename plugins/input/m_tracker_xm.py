# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import plugins
import os.path
from functions import data_values

try: import xmodits
except: xmodits_exists = False
else: xmodits_exists = True

TEXTSTART = 'XM_Inst_'
MAINCOLOR = [0.16, 0.33, 0.53]

def env_to_cvpj(xm_env, plugin_obj, ispan, fadeout):
	envtype = 'pan' if ispan else 'vol'
	autopoints_obj = plugin_obj.env_points_add(envtype, 48, False, 'float')
	autopoints_obj.enabled = xm_env.enabled
	autopoints_obj.sustain_on	= xm_env.sustain_on
	autopoints_obj.sustain_point = xm_env.sustain+1
	autopoints_obj.sustain_end = xm_env.sustain+1
	autopoints_obj.loop_on = xm_env.loop_on
	autopoints_obj.loop_start = xm_env.loop_start
	autopoints_obj.loop_end = xm_env.loop_end
	for n in range(min(xm_env.numpoints, len(xm_env.points))):
		xm_point = xm_env.points[n]
		autopoint_obj = autopoints_obj.add_point()
		autopoint_obj.pos = xm_point[0]
		autopoint_obj.value = (xm_point[1]-32)/32 if ispan else xm_point[1]/64

	if not ispan: 
		if fadeout: autopoints_obj.data['fadeout'] = (256/fadeout)

class input_xm(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'xm'
	def get_name(self): return 'FastTracker 2'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['xm']
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
		bytesdata = bytestream.read(17)
		if bytesdata == b'Extended Module: ': return True
		else: return False
		bytestream.seek(0)

	def parse_bytes(self, convproj_obj, input_bytes, dv_config, input_file):
		from objects.file_proj import proj_xm
		project_obj = proj_xm.xm_song()
		if not project_obj.load_from_raw(input_bytes): exit()
		self.parse_internal(convproj_obj, project_obj, dv_config, input_file)

	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_xm
		project_obj = proj_xm.xm_song()
		if not project_obj.load_from_file(input_file): exit()
		self.parse_internal(convproj_obj, project_obj, dv_config, input_file)

	def parse_internal(self, convproj_obj, project_obj, dv_config, input_file):
		from objects.tracker import pat_single
		global samplefolder
		samplefolder = dv_config.path_samples_extracted
		
		patterndata_obj = pat_single.single_patsong(project_obj.num_channels, TEXTSTART, MAINCOLOR)
		patterndata_obj.orders = project_obj.l_order

		for patnum, xmpat_obj in enumerate(project_obj.patterns):
			if xmpat_obj.used:
				pattern_obj = patterndata_obj.pattern_add(patnum, xmpat_obj.rows)
				for rownum, rowdatas in enumerate(xmpat_obj.data):
					for channel, cell_note, cell_inst, cell_vol, cell_effect, cell_param in rowdatas:
						output_note = cell_note
						if cell_note != None: output_note = 'off' if cell_note == 97 else cell_note-49
						pattern_obj.cell_note(channel, rownum, output_note, cell_inst)
						if cell_vol: pattern_obj.cell_param(channel, rownum, 'vol', cell_vol/64)
						if cell_effect == 13: pattern_obj.cell_g_param(channel, rownum, 'break_to_row', 0)
						if cell_effect != None and cell_param != None:
							pattern_obj.cell_fx_mod(channel, rownum, cell_effect, cell_param)
							if cell_effect == 12: pattern_obj.cell_param(channel, rownum, 'vol', cell_param/64)
							if cell_effect == 15: 
								if cell_param < 32: pattern_obj.cell_g_param(channel, rownum, 'speed', cell_param)
								else: pattern_obj.cell_g_param(channel, rownum, 'tempo', cell_param)
							if cell_effect == 16: pattern_obj.cell_param(channel, rownum, 'global_volume', cell_param/64)
							#if cell_effect == 17: pattern_obj.cell_param(channel, rownum, 'global_volume_slide', dv_trackerpattern.getfineval(cell_param))
							if cell_effect == 34:
								panbrello_params = {}
								panbrello_params['speed'], panbrello_params['depth'] = data_bytes.splitbyte(cell_param)
								pattern_obj.cell_param(channel, rownum, 'panbrello', panbrello_params)

		if project_obj.ompt_cnam:
			for n, t in enumerate(project_obj.ompt_cnam):
				if t: patterndata_obj.channels[n].name = t

		if len(project_obj.ompt_ccol):
			for n, t in enumerate(project_obj.ompt_ccol):
				r,g,b,u = t
				if not u: patterndata_obj.channels[n].color = [r/255,g/255,b/255]

		if project_obj.ompt_pnam:
			for n, t in enumerate(project_obj.ompt_pnam):
				if t: project_obj.patterns[n].name = t

		if project_obj.ompt_chfx:
			for n, t in enumerate(project_obj.ompt_chfx):
				if t: patterndata_obj.channels[n].fx_plugins.append('FX'+str(t))

		if project_obj.plugins:
			for fxnum, plugdata in project_obj.plugins.items():
				plugdata.to_cvpj(fxnum, convproj_obj)

		if xmodits_exists == True:
			if not os.path.exists(samplefolder): os.makedirs(samplefolder)
			try: xmodits.dump(input_file, samplefolder, index_only=True, index_raw=True, index_padding=0)
			except: pass

		xm_cursamplenum = 1

		for instnum, xm_inst in enumerate(project_obj.instruments):
			cvpj_instid = TEXTSTART + str(instnum+1)

			inst_obj = convproj_obj.instrument__add(cvpj_instid)
			inst_obj.visual.name = xm_inst.name
			inst_obj.visual.color.set_float(MAINCOLOR)
			inst_obj.params.add('vol', 0.3, 'float')

			sampleregions = data_values.list__to_reigons(xm_inst.notesampletable, 48)

			inst_used = False
			if xm_inst.num_samples == 0: pass
			elif xm_inst.num_samples == 1:
				inst_used = True
				trsamp = xm_inst.samp_head[0]
				inst_obj.params.add('vol', 0.3*(trsamp.vol), 'float')
				filename = samplefolder+str(xm_cursamplenum)+'.wav'

				plugin_obj, inst_obj.pluginid, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler__genid(filename, None)
				sp_obj.loop_active, sp_obj.loop_mode, sp_obj.loop_start, sp_obj.loop_end = trsamp.get_loop()
				if not sp_obj.loop_active: sp_obj.loop_end = trsamp.length
				sp_obj.end = trsamp.length
				sp_obj.point_value_type = "samples"
			else:
				inst_used = True
				inst_obj.params.add('vol', 0.3, 'float')
				plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
				for instnum, r_start, e_end in sampleregions:
					filename = samplefolder + str(xm_cursamplenum+instnum) + '.wav'
					sampleref_obj = convproj_obj.sampleref__add(filename, filename, None)
					trsamp = xm_inst.samp_head[instnum]
					sp_obj = plugin_obj.sampleregion_add(r_start, e_end, 0, None)
					sp_obj.loop_active, sp_obj.loop_mode, sp_obj.loop_start, sp_obj.loop_end = trsamp.get_loop()
					if not sp_obj.loop_active: sp_obj.loop_end = trsamp.length
					sp_obj.end = trsamp.length
					sp_obj.sampleref = filename
					sp_obj.point_value_type = "samples"

			if xm_inst.num_samples != 0:
				vibrato_rate, vibrato_depth, vibrato_type, vibrato_sweep = xm_inst.vibrato_lfo()
				if vibrato_rate != 0:
					lfo_obj = plugin_obj.lfo_add('pitch')
					lfo_obj.attack = vibrato_sweep
					lfo_obj.prop.shape = vibrato_type
					lfo_obj.time.set_hz(vibrato_rate/5)
					lfo_obj.amount = vibrato_depth

				env_to_cvpj(xm_inst.env_vol, plugin_obj, False, xm_inst.fadeout)
				env_to_cvpj(xm_inst.env_pan, plugin_obj, True, xm_inst.fadeout)

				plugin_obj.env_asdr_from_points('vol')

			xm_cursamplenum += xm_inst.num_samples

		patterndata_obj.to_cvpj(convproj_obj, TEXTSTART, project_obj.bpm, project_obj.speed, True, MAINCOLOR)

		convproj_obj.metadata.name = project_obj.title
		convproj_obj.metadata.comment_text = '\r'.join([i.name for i in project_obj.instruments])
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_lanefit')