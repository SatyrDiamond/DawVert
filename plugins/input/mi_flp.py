# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import zipfile
import json
import struct
import os.path
from objects import core
from pathlib import Path

from functions import data_bytes
from functions import xtramath
from objects import globalstore

from objects.convproj import fileref

filename_len = {}

ONESHOT_TRES = 0.3

chordids = [None,"major","sus2","sus4","majb5","minor","mb5","aug","augsus4","7ri","6","6sus4","6add9","m6","m6add9","7","7sus4","7#5","7b5","7#9","7b9","7#5#9","7#5b9","7b5b9","7add","7add13","7#11","maj7","maj7b5","maj7#5","maj7#11","maj7add13","m7","m7b5","m7b9","m7add11","m7add13","m-maj7","m-maj7add11","m-maj7add13","9","9sus4","add9","9#5","9b5","9#11","9b13","maj9","maj9sus4","maj9#5","maj9#11","m9","madd9","m9b5","m9-maj7","11","11b9","maj11","m11","m-maj11","13","13#9","13b9","13b5b9","maj13","m13","m-maj13","full_major","major_pentatonic","major_bebop","minor_harmonic","minor_melodic","minor_pentatonic","aeolian","minor_neapolitan","minor_hungarian","whole_tone","diminished","dominant_bebop","jap_in_sen","blues","arabic","enigmatic","neapolitan","dorian","phrygian","lydian","mixolydian","locrian"]

filtertype = [
['low_pass', None],
['low_pass', None],
['band_pass', None], 
['high_pass', None],
['notch', None],  
['low_pass','double'],
['low_pass','sv'],
['low_pass','sv'],
]

commoncolors = [11117467,3162224,4171773,4478854,4734799,4934768,5270418,5331300,6114897,6972764,7168597,7232607,7301463,7565918,7689020,8026220,8152667,8743259,9996162]

def calc_time(input_val):
	return ((((input_val/65535)*3.66)**4.5)/8)**0.6

def conv_color(b_color):
	color = b_color.to_bytes(4, "little")
	return [color[0],color[1],color[2]]


def flpauto_to_cvpjauto(i_value):
	out = [None, 0, 1]

	if i_value[0] == 'fx':
		if i_value[2] == 'plugin':
			pluginid = 'FLPlug_F_'+str(i_value[1])+'_'+str(i_value[3])
			out = [['id_plug', pluginid, i_value[4]], 0, 1]

	if i_value[0] == 'chan':
		cvpj_instid = 'FLInst' + str(i_value[1])
		if i_value[2] == 'param':
			if i_value[3] == 'vol': out = [['inst', cvpj_instid, 'vol'], 0, 16000]
			if i_value[3] == 'pan': out = [['inst', cvpj_instid, 'pan'], -6400, 6400]
		if i_value[2] == 'plugin':
			pluginid = 'FLPlug_G_'+str(i_value[1])
			out = [['id_plug', pluginid, i_value[3]], 0, 1]

	if i_value[0] == 'main':
		if i_value[1] == 'tempo': out = [['main', 'bpm'], 0, 1000]
		if i_value[1] == 'pitch': out = [['main', 'pitch'], 0, 100]
	if i_value[0] == 'fx':
		if i_value[2] == 'param':
			if i_value[3] == 'vol': out = [['fxmixer', i_value[1], 'vol'], 0, 16000]
			if i_value[3] == 'pan': out = [['fxmixer', i_value[1], 'pan'], 0, 6400]
		if i_value[2] == 'slot':
			if i_value[4] == 'wet': out = [['slot', 'FLPlug_F_'+i_value[1]+'_'+i_value[3], 'wet'], 0, 12800]
			if i_value[4] == 'on': out = [['slot', 'FLPlug_F_'+i_value[1]+'_'+i_value[3], 'enabled'], 0, 1]
		if i_value[2] == 'route':
			out = [[('send' if i_value[3] else 'send_master'), 'send_'+str(i_value[1])+'_'+str(i_value[3]), 'amount'], 0, 12800]

	return out

def flpauto_to_cvpjauto_points(i_value):
	out = [None, 0, 1]

	if i_value[0] == 'fx':
		if i_value[2] == 'plugin':
			pluginid = 'FLPlug_F_'+str(i_value[1])+'_'+str(i_value[3])
			out = [['id_plug_points', pluginid, i_value[4]], 0, 1]

	if i_value[0] == 'chan':
		cvpj_instid = 'FLInst' + str(i_value[1])
		if i_value[2] == 'param':
			if i_value[3] == 'vol': out = [['inst', cvpj_instid, 'vol'], 0, 1]
			if i_value[3] == 'pan': out = [['inst', cvpj_instid, 'pan'], -1, 1]
		if i_value[2] == 'plugin':
			pluginid = 'FLPlug_G_'+str(i_value[1])
			out = [['id_plug_points', pluginid, i_value[3]], 0, 1]

	if i_value[0] == 'main':
		if i_value[1] == 'tempo': out = [['main', 'bpm'], 10, 522]
		if i_value[1] == 'pitch': out = [['main', 'pitch'], -12, 12]
	if i_value[0] == 'fx':
		if i_value[2] == 'param':
			if i_value[3] == 'vol': out = [['fxmixer', i_value[1], 'vol'], 0, 1.25]
			if i_value[3] == 'pan': out = [['fxmixer', i_value[1], 'pan'], 1, -1]
		if i_value[2] == 'slot':
			if i_value[4] == 'wet': out = [['slot', 'FLPlug_F_'+i_value[1]+'_'+i_value[3], 'wet'], 0, 1]
			if i_value[4] == 'on': out = [['slot', 'FLPlug_F_'+i_value[1]+'_'+i_value[3], 'enabled'], 0, 1]
		if i_value[2] == 'route':
			out = [[('send' if i_value[3] else 'send_master'), 'send_'+str(i_value[1])+'_'+str(i_value[3]), 'amount'], 0, 1]

	return out


def get_sample(i_value):
	if i_value != None:
		if i_value[0:21] == "%FLStudioFactoryData%":
			restpath = i_value[21:]
			return restpath
		elif i_value[0:18] == "%FLStudioUserData%":
			restpath = i_value[18:]
			return restpath
		elif i_value[0:14] == "%FLStudioData%":
			restpath = i_value[14:]
			return restpath
		elif i_value[0:13] == "%USERPROFILE%":
			restpath = i_value[13:]
			return restpath
		else:
			return i_value
	else:
		return ''

#def parse_envlfo(envlfo, pluginid, envtype):
#	bio_envlfo = BytesIO(envlfo)

#	envlfo_flags = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_enabled = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_predelay = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_attack = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_hold = calc_time(int.from_bytes(bio_envlfo.read(4), "little"))
#	el_env_decay = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_sustain = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_release = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_aomunt = int.from_bytes(bio_envlfo.read(4), "little")
#	envlfo_lfo_predelay = int.from_bytes(bio_envlfo.read(4), "little")
#	envlfo_lfo_attack = int.from_bytes(bio_envlfo.read(4), "little")
#	envlfo_lfo_amount = int.from_bytes(bio_envlfo.read(4), "little")
#	envlfo_lfo_speed = int.from_bytes(bio_envlfo.read(4), "little")
#	envlfo_lfo_shape = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_attack_tension = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_decay_tension = int.from_bytes(bio_envlfo.read(4), "little")
#	el_env_release_tension = int.from_bytes(bio_envlfo.read(4), "little")

	#plugins.add_asdr_env(cvpj_l, pluginid, envtype, el_env_predelay, el_env_attack, el_env_hold, el_env_decay, el_env_sustain, el_env_release, el_env_aomunt)
	#plugins.add_asdr_env_tension(cvpj_l, pluginid, envtype, el_env_attack_tension, el_env_decay_tension, el_env_release_tension)

def to_samplepart(fl_channel_obj, sre_obj, convproj_obj, isaudioclip, flp_obj, dv_config):
	filename_sample = get_sample(fl_channel_obj.samplefilename)
	sampleref_obj = convproj_obj.sampleref__add(filename_sample, filename_sample, 'win')

	if flp_obj.zipped: sampleref_obj.find_relative('extracted')
	sampleref_obj.find_relative('projectfile')
	sampleref_obj.find_relative('factorysamples')

	#print(sampleref_obj.fileref.get_path('win', False))

	sre_obj.visual.name = fl_channel_obj.name
	sre_obj.visual.color.set_int(conv_color(fl_channel_obj.color))
	sre_obj.sampleref = filename_sample

	sre_obj.point_value_type = 'percent'
	sre_obj.start = fl_channel_obj.params.start
	sre_obj.end = fl_channel_obj.params.start+(fl_channel_obj.params.length*(1-fl_channel_obj.params.start))
	sre_obj.loop_end = sre_obj.end

	sre_obj.from_sampleref_obj(sampleref_obj)

	sre_obj.reverse = bool(fl_channel_obj.fxflags & 2)
	sre_obj.data['swap_stereo'] = bool(fl_channel_obj.fxflags & 256)
	sre_obj.data['remove_dc'] = fl_channel_obj.params.remove_dc
	sre_obj.data['normalize'] = fl_channel_obj.params.normalize
	sre_obj.data['reversepolarity'] = fl_channel_obj.params.reversepolarity
	sre_obj.interpolation = "sinc" if (fl_channel_obj.sampleflags & 1) else "none"

	if sampleref_obj.fileref.file.extension.lower() != 'ds':
		sre_obj.loop_active = bool(fl_channel_obj.sampleflags & 8)
		sre_obj.loop_mode = "normal" if fl_channel_obj.looptype == 0 else "pingpong"
				  
	t_stretchingmultiplier = 1

	t_stretchingpitch = 0
	t_stretchingpitch += fl_channel_obj.params.stretchingpitch/100
	if isaudioclip: 
		sre_obj.enabled = bool(fl_channel_obj.enabled)
		sre_obj.pan = fl_channel_obj.basicparams.pan
		sre_obj.vol = fl_channel_obj.basicparams.volume
		sre_obj.fxrack_channel = fl_channel_obj.fxchannel
		t_stretchingpitch += (fl_channel_obj.middlenote-60)*-1
		t_stretchingpitch += fl_channel_obj.basicparams.pitch/100

	sre_obj.pitch = t_stretchingpitch
	
	t_stretchingtime = fl_channel_obj.params.stretchingtime/384
	t_stretchingmode = fl_channel_obj.params.stretchingmode
	t_stretchingmultiplier = pow(2, fl_channel_obj.params.stretchingmultiplier/10000)

	sre_obj.stretch.preserve_pitch = t_stretchingmode != 0
	if t_stretchingmode == 1: 
		sre_obj.stretch.algorithm = 'elastique_v3'
		sre_obj.stretch.algorithm_mode = 'generic'
	if t_stretchingmode == 2: 
		sre_obj.stretch.algorithm = 'elastique_v3'
		sre_obj.stretch.algorithm_mode = 'mono'
	if t_stretchingmode == 3: sre_obj.stretch.algorithm = 'slice_stretch'
	if t_stretchingmode == 4: sre_obj.stretch.algorithm = 'auto'
	if t_stretchingmode == 5: sre_obj.stretch.algorithm = 'slice_map'
	if t_stretchingmode == 6: 
		sre_obj.stretch.algorithm = 'elastique_v2'
		sre_obj.stretch.algorithm_mode = 'generic'
	if t_stretchingmode == 7: 
		sre_obj.stretch.algorithm = 'elastique_v2'
		sre_obj.stretch.algorithm_mode = 'transient'
	if t_stretchingmode == 8: 
		sre_obj.stretch.algorithm = 'elastique_v2'
		sre_obj.stretch.algorithm_mode = 'mono'
	if t_stretchingmode == 9: 
		sre_obj.stretch.algorithm = 'elastique_v2'
		sre_obj.stretch.algorithm_mode = 'speech'
	if t_stretchingmode == -2: 
		sre_obj.stretch.algorithm = 'elastique_pro'
		sre_obj.stretch.params['formant'] = fl_channel_obj.params.stretchingformant

	if sampleref_obj.found:
		if t_stretchingtime != 0:
			sre_obj.stretch.set_rate_tempo(flp_obj.tempo, (sampleref_obj.dur_sec/t_stretchingtime)/t_stretchingmultiplier, False)

		elif t_stretchingtime == 0:
			sre_obj.stretch.set_rate_speed(flp_obj.tempo, 1/t_stretchingmultiplier, False)

	return sre_obj, sampleref_obj


DEBUGAUTOTICKS = False


class input_flp(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'flp'
	def get_name(self): return 'FL Studio 12-24'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['flp']
		in_dict['auto_types'] = ['pl_ticks', 'pl_points']
		in_dict['track_lanes'] = True
		in_dict['placement_cut'] = True
		in_dict['fxrack_params'] = ['enabled','vol','pan']
		in_dict['audio_stretch'] = ['rate']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3','wv','ds','wav_codec']
		in_dict['plugin_included'] = ['universal:sampler:single','universal:arpeggiator','native:flstudio','universal:soundfont2']
		in_dict['fxchain_mixer'] = True
		in_dict['plugin_ext'] = ['vst2']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'mi'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		try:
			zip_data = zipfile.ZipFile(input_file, 'r')
			for filename in zip_data.namelist():
				if filename.endswith('.flp'): return True
			return False
		except:
			bytestream = open(input_file, 'rb')
			bytestream.seek(0)
			bytesdata = bytestream.read(4)
			if bytesdata == b'FLhd': return True
			else: return False
	def parse(self, convproj_obj, input_file, dv_config):
		from functions_plugin import flp_dec_plugins
		from objects.file_proj import proj_flp
		from objects.inst_params import fx_delay

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'mi'

		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FL Studio 2024\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\Image-Line\\FL Studio 2024\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FL Studio 21\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\Image-Line\\FL Studio 21\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FL Studio 20\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\Image-Line\\FL Studio 20\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FL Studio 8\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\Image-Line\\FL Studio 8\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FL Studio 7\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\Image-Line\\FL Studio 7\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\Image-Line\\FLStudio5\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\Image-Line\\FLStudio5\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\FLStudio4\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\FLStudio4\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\FruityLoops3.5\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\FruityLoops3.5\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files\\FruityLoops3\\", 'win')
		fileref.filesearcher.add_searchpath_full_append('factorysamples', "C:\\Program Files (x86)\\FruityLoops3\\", 'win')

		flp_obj = proj_flp.flp_project()
		flp_obj.read(input_file)

		if flp_obj.zipped:
			for filename in flp_obj.zipfile.namelist():
				if not filename.endswith('.flp'):
					try:
						flp_obj.zipfile.extract(filename, path=dv_config.path_samples_extracted, pwd=None)
					except PermissionError:
						pass

		globalstore.datadef.load('fl_studio', './data_main/datadef/fl_studio.ddef')
		globalstore.dataset.load('fl_studio', './data_main/dataset/fl_studio.dset')

		wrapper_plugids = []

		convproj_obj.set_timings(flp_obj.ppq, False)
		convproj_obj.timesig[0] = flp_obj.numerator
		convproj_obj.timesig[1] = int(((flp_obj.denominator/4)**-1)*4)

		convproj_obj.params.add('pitch', flp_obj.mainpitch/100, 'float')
		convproj_obj.params.add('bpm', flp_obj.tempo, 'float')
		convproj_obj.params.add('shuffle', flp_obj.shuffle/128, 'float')

		convproj_obj.params.add('vol', flp_obj.initfxvals.initvals['main/vol']/12800 if 'main/vol' in flp_obj.initfxvals.initvals else 1, 'float')

		#for x in flp_obj.startvals.initvals.items():
		#	print(x)

		id_inst = {}
		id_auto = {}
		id_pat = {}
		sampleinfo = {}
		samplestretch = {}
		samplefolder = dv_config.path_samples_extracted

		instdata_chans = []

		layer_chans = {}
		chan_range = {}

		for instrument, channelnum in enumerate(flp_obj.channels):
			fl_channel_obj = flp_obj.channels[channelnum]
			instdata = {}

			spdata = None

			if fl_channel_obj.type in [0,1,2,3]:
				cvpj_instid = 'FLInst' + str(instrument)

				inst_obj = convproj_obj.instrument__add(cvpj_instid)

				inst_obj.visual.name = fl_channel_obj.name if fl_channel_obj.name else ''
				inst_obj.visual.color.set_int(conv_color(fl_channel_obj.color))

				inst_obj.visual.color.priority = -1 if (fl_channel_obj.color in commoncolors) else 0

				inst_obj.datavals.add('middlenote', fl_channel_obj.middlenote-60)
				inst_obj.params.add('enabled', fl_channel_obj.enabled, 'bool')
				inst_obj.params.add('pitch', fl_channel_obj.basicparams.pitch/100, 'float')
				inst_obj.params.add('usemasterpitch', fl_channel_obj.params.main_pitch, 'bool')
				inst_obj.params.add('pan', fl_channel_obj.basicparams.pan, 'float')
				inst_obj.params.add('vol', fl_channel_obj.basicparams.volume**1.5, 'float')
				inst_obj.fxrack_channel = fl_channel_obj.fxchannel

				chan_range[channelnum] = [fl_channel_obj.params.keyrange_min, fl_channel_obj.params.keyrange_max]

				plugin_obj = None
				if fl_channel_obj.type == 0:
					inst_obj.pluginid = 'FLPlug_G_'+str(channelnum)
					plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(inst_obj.pluginid, get_sample(fl_channel_obj.samplefilename), 'win')
					samplepart_obj, sampleref_obj = to_samplepart(fl_channel_obj, sp_obj, convproj_obj, False, flp_obj, dv_config)
					fl_asdr_obj_vol = fl_channel_obj.env_lfo[1]
					sampleloop = bool(fl_channel_obj.sampleflags & 8)
					samplepart_obj.trigger = 'normal' # if (bool(fl_asdr_obj_vol.el_env_enabled) or sampleloop) else 'oneshot'

					crossfade = fl_channel_obj.params.crossfade/1024

					if not sampleref_obj.loop_found and not crossfade: 
						sp_obj.loop_active = False
					
					spdata = sp_obj

				if fl_channel_obj.type == 2:
					if fl_channel_obj.plugin.name != None: 
						inst_obj.pluginid = 'FLPlug_G_'+str(channelnum)
						plugin_obj = flp_dec_plugins.getparams(convproj_obj, inst_obj.pluginid, fl_channel_obj.plugin, samplefolder, flp_obj.zipfile)
						if fl_channel_obj.plugin.name == 'fruity wrapper':
							wrapper_plugids.append(inst_obj.pluginid)

						if fl_channel_obj.samplefilename:
							sp_obj = plugin_obj.samplepart_add('audiofile')
							samplepart_obj, sampleref_obj = to_samplepart(fl_channel_obj, sp_obj, convproj_obj, False, flp_obj, dv_config)

				if fl_channel_obj.type == 3:
					layer_chans[channelnum] = fl_channel_obj.layer_chans

				if plugin_obj:
					fl_asdr_obj_vol = fl_channel_obj.env_lfo[1]
					fl_asdr_obj_cut = fl_channel_obj.env_lfo[2]
					fl_delay = fl_channel_obj.delay

					if fl_delay.feedback:
						chanfxpid = 'FLPlug_GD_'+str(channelnum)

						delay_obj = fx_delay.fx_delay()
						delay_obj.feedback_first = True
						delay_obj.feedback[0] = fl_delay.feedback*0.8
						delay_obj.num_echoes = fl_delay.echoes
						timing_obj = delay_obj.timing_add(0)
						timing_obj.set_steps(fl_delay.time, convproj_obj)
						chfxplugin_obj = delay_obj.to_cvpj(convproj_obj, chanfxpid)
						inst_obj.fxslots_audio.append(chanfxpid)

					vol_enabled = bool(fl_asdr_obj_vol.el_env_enabled)

					if vol_enabled:
						adsr_obj = plugin_obj.env_asdr_add('vol', 
							calc_time(fl_asdr_obj_vol.el_env_predelay), 
							calc_time(fl_asdr_obj_vol.el_env_attack), 
							calc_time(fl_asdr_obj_vol.el_env_hold), 
							calc_time(fl_asdr_obj_vol.el_env_decay), 
							fl_asdr_obj_vol.el_env_sustain/128, 
							calc_time(fl_asdr_obj_vol.el_env_release), 
							int(vol_enabled)
							)

						adsr_obj.attack_tension = fl_asdr_obj_vol.el_env_attack_tension
						adsr_obj.decay_tension = fl_asdr_obj_vol.el_env_decay_tension
						adsr_obj.release_tension = fl_asdr_obj_vol.el_env_release_tension

					elif fl_channel_obj.type == 0 and (not fl_channel_obj.sampleflags&8 or sampleref_obj.fileref.file.extension.lower() == 'ds'):
						plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 20, 1)

					fcalc = 0
					if fl_channel_obj.basicparams.mod_type == 0: fcalc = 1

					if fl_channel_obj.basicparams.mod_x != 1:
						plugin_obj.filter.on = True
						plugin_obj.filter.freq = xtramath.midi_filter(fl_channel_obj.basicparams.mod_x)
						if fcalc == 0: plugin_obj.filter.freq *= 2.7
						plugin_obj.filter.q = 1+(fl_channel_obj.basicparams.mod_y*6)
						plugin_obj.filter.type.set_list(filtertype[fl_channel_obj.basicparams.mod_type])

					envf_amount = xtramath.midi_filter(fl_asdr_obj_cut.el_env_aomunt/128)
					if fcalc == 0: envf_amount *= 2.7

					adsr_obj = plugin_obj.env_asdr_add('cutoff', 
						calc_time(fl_asdr_obj_cut.el_env_predelay), 
						calc_time(fl_asdr_obj_cut.el_env_attack), 
						calc_time(fl_asdr_obj_cut.el_env_hold), 
						calc_time(fl_asdr_obj_cut.el_env_decay), 
						fl_asdr_obj_cut.el_env_sustain/128, 
						calc_time(fl_asdr_obj_cut.el_env_release), 
						envf_amount
						)

					adsr_obj.attack_tension = fl_asdr_obj_cut.el_env_attack_tension
					adsr_obj.decay_tension = fl_asdr_obj_cut.el_env_decay_tension
					adsr_obj.release_tension = fl_asdr_obj_cut.el_env_release_tension

					polynum = 1 if bool(fl_channel_obj.poly.flags&1) else fl_channel_obj.poly.max

					poly_obj = plugin_obj.poly
					poly_obj.max = polynum
					poly_obj.limited = polynum != 0
					poly_obj.mono = bool(fl_channel_obj.poly.flags&1)
					poly_obj.slide_always = bool(fl_channel_obj.poly.flags&2)
					poly_obj.defined = True

					if poly_obj.slide_always: 
						poly_obj.porta_time.set_steps_nonsync((fl_channel_obj.poly.slide/1024)**(16/4), flp_obj.tempo)
						poly_obj.porta_time.type = 'steps'
					plugin_obj.role = 'synth'

				notefx_pluginid = 'FLPlug_GA_'+str(channelnum)
				plugin_obj = convproj_obj.plugin__add(notefx_pluginid, 'universal', 'arpeggiator', None)
				plugin_obj.fxdata_add(fl_channel_obj.params.arpdirection, None)
				plugin_obj.role = 'notefx'
				inst_obj.fxslots_notes.append(notefx_pluginid)

				if fl_channel_obj.params.arpdirection:
					plugin_obj.datavals.add('gate', fl_channel_obj.params.arpgate/48)
					plugin_obj.datavals.add('range', fl_channel_obj.params.arprange)
					plugin_obj.datavals.add('repeat', fl_channel_obj.params.arprepeat)
					plugin_obj.datavals.add('slide', bool(fl_channel_obj.params.arpslide))
					plugin_obj.datavals.add('direction', ['up','up','down','up_down','up_down','random'][fl_channel_obj.params.arpdirection])
					if fl_channel_obj.params.arpdirection == 4:
						plugin_obj.datavals.add('direction_mode', 'sticky')

					chord_obj = plugin_obj.chord_add('main')
					if fl_channel_obj.params.arpchord < 89:
						chord_obj.find_by_id(0, chordids[fl_channel_obj.params.arpchord])
					else:
						if fl_channel_obj.params.arpchord == 4294967294:
							plugin_obj.datavals.add('mode', 'sort')
						if fl_channel_obj.params.arpchord == 4294967295:
							plugin_obj.datavals.add('mode', 'sort')
							plugin_obj.datavals.add('mode_sub', 'sustain')

				timing_obj = plugin_obj.timing_add('main')
				timing_obj.set_steps((fl_channel_obj.params.arptime/1024)**4, convproj_obj)

				id_inst[str(instrument)] = 'FLInst' + str(instrument)

			if fl_channel_obj.type == 4:
				sre_obj = convproj_obj.sampleindex__add('FLSample' + str(instrument))
				samplepart_obj, sampleref_obj = to_samplepart(fl_channel_obj, sre_obj, convproj_obj, True, flp_obj, dv_config)

				if sampleref_obj.found:
					samplestretch[instrument] = sre_obj.stretch

			if fl_channel_obj.type == 5:
				id_auto[channelnum] = fl_channel_obj.autopoints 

			instdata_chans.append(spdata)

		autoticks_pat = {}
		autoticks_pl = {}

		oneshotnotenum_chans = [0 for x in range(len(flp_obj.channels))]
		numnotenum_chans = [0 for x in range(len(flp_obj.channels))]

		for pattern, fl_pattern in flp_obj.patterns.items():

			nle_obj = convproj_obj.notelistindex__add('FLPat' + str(pattern))

			autoticks_pat[pattern] = fl_pattern.automation

			if fl_pattern.notes:
				slidenotes = []
				for fl_note in fl_pattern.notes:
					note_inst = id_inst[str(fl_note.rack)] if str(fl_note.rack) in id_inst else ''
					note_pos = fl_note.pos
					note_dur = fl_note.dur
					note_key = fl_note.key-60
					note_vol = fl_note.velocity/100

					if not note_dur: oneshotnotenum_chans[fl_note.rack] += 1
					numnotenum_chans[fl_note.rack] += 1

					note_extra = {}
					if fl_note.finep != 120: note_extra['finepitch'] = (fl_note.finep-120)*10
					if fl_note.finep != 64: note_extra['release'] = fl_note.rel/128
					if fl_note.finep != 64: note_extra['pan'] = (fl_note.pan-64)/64
					if fl_note.finep != 128: note_extra['cutoff'] = fl_note.mod_x/255
					if fl_note.finep != 128: note_extra['reso'] = fl_note.mod_y/255
					notechan = data_bytes.splitbyte(fl_note.midich)[1]
					if notechan: note_extra['channel'] = notechan+1

					is_slide = bool(fl_note.flags & 0b000000000001000)

					if is_slide == True: 
						slidenotes.append([note_inst, note_pos, note_dur, note_key, note_vol, note_extra if note_extra else None])
					else: 
						nle_obj.notelist.add_m(note_inst, note_pos, note_dur, note_key, note_vol, note_extra if note_extra else None)

				for sn in slidenotes: 
					nle_obj.notelist.auto_add_slide(sn[0], sn[1], sn[2], sn[3], sn[4], sn[5])
				nle_obj.notelist.notemod_conv()
				nle_obj.notelist.extra_to_noteenv()

				for channum, lchans in layer_chans.items():
					note_inst = id_inst[str(channum)] if str(channum) in id_inst else ''
					if lchans and note_inst:
						basenotes = nle_obj.notelist.__copy__()
						basenotes.mod_filter_inst(note_inst)
						for lchan in lchans:
							channote = basenotes.__copy__()
							lchani = id_inst[str(lchan)] if str(lchan) in id_inst else ''
							channote.inst_all(lchani)
							imin, imax = chan_range[lchan]
							channote.mod_limit(imin-60, imax-60)
							nle_obj.notelist.merge(channote, 0)

				id_pat[str(pattern)] = 'FLPat' + str(pattern)

			if fl_pattern.color:
				color = fl_pattern.color.to_bytes(4, "little")
				if color != b'HQV\x00': nle_obj.visual.color.set_int([color[0],color[1],color[2]])
			if fl_pattern.name: nle_obj.visual.name = fl_pattern.name

			for fl_timemark in fl_pattern.timemarkers:
				if fl_timemark.type == 8:
					nle_obj.timesig_auto.add_point(fl_timemark.pos, [fl_timemark.numerator, fl_timemark.denominator])

		for num, sp_obj in enumerate(instdata_chans):
			if numnotenum_chans[num] and sp_obj:
				if oneshotnotenum_chans[num]/numnotenum_chans[num] > ONESHOT_TRES:
					sp_obj.trigger = 'oneshot'

		temp_pl_track = {}

		if len(flp_obj.arrangements) != 0:
			fl_arrangement = flp_obj.arrangements[0]

			used_tracks = []

			#for track_id, track_obj in fl_arrangement.tracks.items():
			#	if track_id in used_tracks:
			#		playlist_obj = convproj_obj.playlist__add(str(track_id), True, True)
			#		if track_obj.color: playlist_obj.visual.color = conv_color(track_obj.color)
			#		if track_obj.name: playlist_obj.visual.name = track_obj.name
			#		playlist_obj.visual_ui.height = track_obj.height
			#		playlist_obj.params.add('enabled', track_obj.enabled, 'bool')

			tr_n = 500
			if flp_obj.version_split[0] == 12: tr_n = 200

			for item in fl_arrangement.items:
				
				playlistline = (item.trackindex*-1)+tr_n
				if playlistline not in used_tracks: used_tracks.append(playlistline)

				if playlistline not in temp_pl_track:
					if playlistline in fl_arrangement.tracks: 
						playlist_obj = convproj_obj.playlist__add(playlistline-1, 1, True)
						color = fl_arrangement.tracks[playlistline].color.to_bytes(4, "little")
						if color != b'HQV\x00': playlist_obj.visual.color.set_int([color[0],color[1],color[2]])
						temp_pl_track[playlistline] = playlist_obj

				if item.itemindex > item.patternbase and playlistline in temp_pl_track:
					placement_obj = temp_pl_track[playlistline].placements.add_notes_indexed()
					placement_obj.time.set_posdur(item.position, item.length)
					placement_obj.muted = bool(item.flags & 0b0001000000000000)
					patnum = item.itemindex - item.patternbase
					placement_obj.fromindex = 'FLPat' + str(patnum)
					if item.startoffset not in [4294967295, 3212836864]: 
						placement_obj.time.set_offset(item.startoffset)

					if patnum in autoticks_pat:
						tickdata = autoticks_pat[patnum]
						autodata = [placement_obj.time.position, placement_obj.time.duration, item.startoffset]
						autod = autoticks_pat

						for autoid, autodata in tickdata.items():
							autoloc, aadd, adiv = flpauto_to_cvpjauto(autoid.split('/'))

							if autoloc == ['main','pitch']:
								for x in autodata: x[1] = struct.unpack('I', struct.pack('i', x[1]))[0]

							if autoloc: 
								if DEBUGAUTOTICKS: t = []

								autopl_obj = convproj_obj.automation.add_pl_ticks(autoloc, 'float')
								autopl_obj.time = placement_obj.time.copy()
								for pos, val in autodata: 
									autopl_obj.data.add_point(pos, (val+aadd)/adiv)
									if DEBUGAUTOTICKS: t.append(val)

								if DEBUGAUTOTICKS:
									print(autoloc, min(t), max(t))


				else:
					if item.itemindex in id_auto and item.itemindex in flp_obj.remote_assoc:
						fl_autopoints = id_auto[item.itemindex]

						for fl_remotectrl in flp_obj.remote_assoc[item.itemindex]:

							autoloc = fl_remotectrl.autoloc
							autotxt = autoloc.to_loctxt()
							autoloc, amin, amax = flpauto_to_cvpjauto_points(autotxt.split('/'))
	
							if autoloc: 
								autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
								autopl_obj.time.set_posdur(item.position, item.length)
								if item.startoffset not in [4294967295, 3212836864]: 
									if item.startoffset > 0:
										posdata = item.startoffset
										posdata = posdata/0.008
										autopl_obj.time.set_offset(posdata*flp_obj.ppq)

								curpos = 0
								for point in fl_autopoints.points:
									curpos += point.pos
	
									auto_pos = int(curpos*flp_obj.ppq)
									auto_val = xtramath.between_from_one(amin, amax, point.val)
	
									autopoint_obj = autopl_obj.data.add_point()
									autopoint_obj.pos = auto_pos
									autopoint_obj.value = auto_val
									autopoint_obj.type = 'normal' if point.type!=2 else 'instant'
	
									#print(auto_pos, auto_val)

					if playlistline in temp_pl_track:
						placement_obj = temp_pl_track[playlistline].placements.add_audio_indexed()
						placement_obj.time.set_posdur(item.position, item.length)

						placement_obj.fade_in.set_dur(item.f_in_dur/1000, 'seconds')
						placement_obj.fade_out.set_dur(item.f_out_dur/1000, 'seconds')

						placement_obj.muted = bool(item.flags & 0b0001000000000000)
						placement_obj.fromindex = 'FLSample' + str(item.itemindex)
						stretch_obj = samplestretch[item.itemindex] if item.itemindex in samplestretch else None
	
						out_rate = stretch_obj.calc_tempo_speed if stretch_obj else 1
	
						if item.startoffset not in [4294967295, 3212836864]:  
							posdata = item.startoffset/4
							placement_obj.time.set_offset((posdata/out_rate)*flp_obj.ppq)

			for fl_timemark in fl_arrangement.timemarkers:
				if fl_timemark.type == 8:
					convproj_obj.timesig_auto.add_point(fl_timemark.pos, [fl_timemark.numerator, fl_timemark.denominator])
				else:
					timemarker_obj = convproj_obj.timemarker__add()
					timemarker_obj.visual.name = fl_timemark.name
					timemarker_obj.position = fl_timemark.pos
					if fl_timemark.type == 5: timemarker_obj.type = 'start'
					if fl_timemark.type == 4: 
						timemarker_obj.type = 'loop'
						convproj_obj.loop_start = timemarker_obj.position
						convproj_obj.loop_active = True
					if fl_timemark.type == 1: timemarker_obj.type = 'markerloop'
					if fl_timemark.type == 2: timemarker_obj.type = 'markerskip'
					if fl_timemark.type == 3: timemarker_obj.type = 'pause'
					if fl_timemark.type == 9: timemarker_obj.type = 'punchin'
					if fl_timemark.type == 10: timemarker_obj.type = 'punchout'

		
		#print(flp_obj.initfxvals.initvals)
		#exit()

		for mixer_id, mixer_obj in flp_obj.mixer.items():

			fxchannel_obj = convproj_obj.fx__chan__add(mixer_id)
			if mixer_obj.name: fxchannel_obj.visual.name = mixer_obj.name
			if mixer_obj.color: 
				if mixer_obj.color not in [9801863, 8814968]:
					fxchannel_obj.visual.color.set_int(conv_color(mixer_obj.color))

			#print(mixer_obj.color)

			if mixer_obj.docked_center: dockedpos = 0
			else: dockedpos = -1 if not mixer_obj.docked_pos else 1
			fxchannel_obj.visual_ui.other['docked'] = dockedpos

			autoloctxt_vol = 'fx/'+str(mixer_id)+'/param/vol'
			autoloctxt_pan = 'fx/'+str(mixer_id)+'/param/pan'
			fx_vol = flp_obj.initfxvals.initvals[autoloctxt_vol]/12800 if autoloctxt_vol in flp_obj.initfxvals.initvals else 1
			fx_pan = flp_obj.initfxvals.initvals[autoloctxt_pan]/6400 if autoloctxt_pan in flp_obj.initfxvals.initvals else 0

			fxchannel_obj.params.add('vol', fx_vol**2, 'float')
			fxchannel_obj.params.add('pan', fx_pan, 'float')

			fxchannel_obj.sends.to_master_active = False

			for route in mixer_obj.routing:
				autoloctxt_route = 'fx/'+str(mixer_id)+'/route/'+str(route)
				fx_amount = flp_obj.initfxvals.initvals[autoloctxt_route]/12800 if autoloctxt_route in flp_obj.initfxvals.initvals else 1
				send_id = 'send_'+str(mixer_id)+'_'+str(route)
				if route == 0:
					fxchannel_obj.sends.to_master_active = True
					master_send = fxchannel_obj.sends.to_master
					master_send.params.add('amount', fx_amount, 'float')
					master_send.sendautoid = send_id
				else:
					fxchannel_obj.sends.add(route, send_id, fx_amount)

			for slot_id, slot_obj in enumerate(mixer_obj.slots):
				autoloctxt_on = 'fx/'+str(mixer_id)+'/slot/'+str(slot_id)+'/on'
				autoloctxt_wet = 'fx/'+str(mixer_id)+'/slot/'+str(slot_id)+'/wet'
				route_on = flp_obj.initfxvals.initvals[autoloctxt_on] if autoloctxt_on in flp_obj.initfxvals.initvals else 1
				route_wet = flp_obj.initfxvals.initvals[autoloctxt_wet]/12800 if autoloctxt_wet in flp_obj.initfxvals.initvals else 1

				if slot_obj:
					try:
						pluginid = 'FLPlug_F_'+str(mixer_id)+'_'+str(slot_id)
						plugin_obj = flp_dec_plugins.getparams(convproj_obj, pluginid, slot_obj.plugin, samplefolder, flp_obj.zipfile)
						plugin_obj.fxdata_add(bool(route_on), route_wet)
						plugin_obj.role = 'effect'
						if slot_obj.name: plugin_obj.visual.name = slot_obj.name
						if slot_obj.color: plugin_obj.visual.color.set_int(conv_color(slot_obj.color))
						if slot_obj.plugin.name == 'fruity wrapper':
							wrapper_plugids.append(pluginid)

						fxchannel_obj.fxslots_audio.append(pluginid)
					except:
						pass

			eq_fxid = 'FLPlug_ME_'+str(mixer_id)

			mixer_eq = []

			for eqnum in range(3):
				autoloctxt_level = 'fx/'+str(mixer_id)+'/param/eq'+str(eqnum+1)+'_level'
				autoloctxt_freq = 'fx/'+str(mixer_id)+'/param/eq'+str(eqnum+1)+'_freq'

				eq_level = flp_obj.initfxvals.initvals[autoloctxt_level] if autoloctxt_level in flp_obj.initfxvals.initvals else 0
				eq_freq = flp_obj.initfxvals.initvals[autoloctxt_freq] if autoloctxt_freq in flp_obj.initfxvals.initvals else 0

				mixer_eq.append([eq_freq, eq_level])

			eq_used = True
			if mixer_eq != [[5777, 0], [33145, 0], [55825, 0]]: eq_used = False
			if mixer_eq != [[0, 0], [0, 0], [0, 0]]: eq_used = False

			if eq_used:
				plugin_obj = convproj_obj.plugin__add(eq_fxid, 'universal', 'eq', 'bands')
				for n, e in enumerate(mixer_eq):
					eq_freq, eq_level = e
					eq_level /= 65536
					eq_freq /= 65536
					eq_freq **= 0.5
					eq_freq = 10 * 1600**eq_freq

					filter_obj, filterid = plugin_obj.eq_add()
					filter_obj.freq = eq_freq
					filter_obj.type.set(['low_shelf','peak','high_shelf'][n], None)
					filter_obj.gain = eq_level
				fxchannel_obj.fxslots_mixer.append(eq_fxid)

		#if len(flp_obj.arrangements) == 0 and len(FL_Patterns) == 1 and len(FL_Channels) == 0:
		#	fst_chan_notelist = [[] for x in range(16)]
		#	for cvpj_notedata in cvpj_l_notelistindex['FLPat0']['notelist']:
		#		cvpj_notedata['instrument'] = 'FST' + str(cvpj_notedata['channel'])
		#		fst_chan_notelist[cvpj_notedata['channel']-1].append(cvpj_notedata)

		#	for channum in range(16):
		#		cvpj_inst = {}
		#		cvpj_inst['name'] = 'Channel '+str(channum+1)
		#		cvpj_l_instrument_data['FST' + str(channum+1)] = cvpj_inst
		#		cvpj_l_instrument_order.append('FST' + str(channum+1))

		#		arrangementitemJ = {}
		#		arrangementitemJ['position'] = 0
		#		arrangementitemJ['duration'] = notelist_data.getduration(cvpj_l_notelistindex['FLPat0']['notelist'])
		#		arrangementitemJ['fromindex'] = 'FLPat0'

		#		cvpj_l_playlist["1"] = {}
		#		cvpj_l_playlist["1"]['placements_notes'] = []
		#		cvpj_l_playlist["1"]['placements_notes'].append(arrangementitemJ)

		convproj_obj.do_actions.append('do_lanefit')
		convproj_obj.do_actions.append('do_addloop')

		convproj_obj.loop_end = convproj_obj.get_dur()

		convproj_obj.automation.attempt_after()

		movequeue = []
		movequeue_points = []

		autodata = convproj_obj.automation.data
		for wrapper_plugid in wrapper_plugids:
			for n, x in autodata.items():
				if n.startswith(['id_plug',wrapper_plugid]):
					autol = n.get_list()
					movequeue.append([autol, ['plugin',autol[1],'ext_param_'+autol[2]]])

		for wrapper_plugid in wrapper_plugids:
			for n, x in autodata.items():
				if n.startswith(['id_plug_points',wrapper_plugid]):
					autol = n.get_list()
					movequeue_points.append([autol, ['plugin',autol[1],'ext_param_'+autol[2]]])

		for autopath, to_autopath in movequeue:
			convproj_obj.automation.calc(autopath, 'floatbyteint2float', 0, 0, 0, 0)
			convproj_obj.automation.move(autopath, to_autopath)

		for autopath, to_autopath in movequeue_points:
			convproj_obj.automation.move(autopath, to_autopath)

		if flp_obj.title: convproj_obj.metadata.name = flp_obj.title
		if flp_obj.author: convproj_obj.metadata.author = flp_obj.author
		if flp_obj.genre: convproj_obj.metadata.genre = flp_obj.genre
		if flp_obj.url: convproj_obj.metadata.url = flp_obj.url
		if flp_obj.comment: convproj_obj.metadata.comment_text = flp_obj.comment

		#for n, d in convproj_obj.automation.data.items():
		#	print(n, [x.value for x in d.pl_points.data[0].data])