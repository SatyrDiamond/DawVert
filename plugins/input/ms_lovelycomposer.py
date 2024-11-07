# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os.path
import struct
import numpy as np
from objects import colors
from functions import xtramath
from objects import globalstore

#                  Name,             Type,        FadeIn, FadeOut, PitchMod, Slide, Vib, Color

lc_instlist = {}
lc_instlist[ 2] = ['Square Wave'     ,'Square'    ,0  ,0  ,0  ,False ,False]
lc_instlist[ 1] = ['Triangle Wave'   ,'Triangle'  ,0  ,0  ,0  ,False ,False]
lc_instlist[ 0] = ['Pulse Wave'      ,'Pulse25'   ,0  ,0  ,0  ,False ,False]
lc_instlist[16] = ['SawTooth Wave'   ,'Saw'       ,0  ,0  ,0  ,False ,False]
lc_instlist[20] = ['Sine Wave'       ,'Sine'      ,0  ,0  ,0  ,False ,False]
lc_instlist[ 3] = ['Noise'           ,'Noise'     ,0  ,0  ,0  ,False ,False]
lc_instlist[ 4] = ['Piano Like'      ,'Pulse25'   ,0  ,1  ,0  ,False ,False]
lc_instlist[17] = ['Synth Piano'     ,'Saw'       ,0  ,1  ,0  ,False ,False]
lc_instlist[ 5] = ['Xylophone Like'  ,'Triangle'  ,0  ,1  ,0  ,False ,False]
lc_instlist[ 6] = ['Ice'             ,'Square'    ,0  ,1  ,0  ,False ,False]
lc_instlist[21] = ['Orgel Like'      ,'Sine'      ,0  ,1  ,0  ,False ,False]
lc_instlist[ 7] = ['Drum Like'       ,'Drum'      ,0  ,1  ,0  ,False ,False]
lc_instlist[ 8] = ['Strings Like'    ,'Pulse25'   ,0  ,0  ,0  ,False ,True ]
lc_instlist[ 9] = ['Vocal Like'      ,'Triangle'  ,0  ,0  ,0  ,False ,True ]
lc_instlist[10] = ['UFO'             ,'Square'    ,0  ,0  ,0  ,False ,True ]
lc_instlist[18] = ['Brass Like'      ,'Saw'       ,0  ,0  ,0  ,False ,True ]
lc_instlist[22] = ['Ghost'           ,'Sine'      ,0  ,0  ,0  ,False ,True ]

lc_instlist[14] = ['Glide Square'    ,'Square'    ,0  ,0  ,0  ,True  ,False]
lc_instlist[13] = ['Glide Triangle'  ,'Triangle'  ,0  ,0  ,0  ,True  ,False]
lc_instlist[12] = ['Glide Pulse'     ,'Pulse25'   ,0  ,0  ,0  ,True  ,False]
lc_instlist[19] = ['Glide SawTooth'  ,'Saw'       ,0  ,0  ,0  ,True  ,False]
lc_instlist[23] = ['Glide Sine'      ,'Sine'      ,0  ,0  ,0  ,True  ,False]
lc_instlist[15] = ['Glide Noise'     ,'Noise'     ,0  ,0  ,0  ,True  ,False]
lc_instlist[24] = ['Fish'            ,'Noise'     ,1  ,0  ,0  ,False ,False]
lc_instlist[25] = ['Flute Like'      ,'Triangle'  ,1  ,0  ,0  ,False ,False]
lc_instlist[26] = ['Slow String Like','Pulse25'   ,1  ,0  ,0  ,False ,False]
lc_instlist[27] = ['Saxophone Like'  ,'Saw'       ,1  ,0  ,0  ,False ,False]
lc_instlist[28] = ['Ocarina Like'    ,'Sine'      ,1  ,0  ,0  ,False ,False]
lc_instlist[29] = ['Seashore Like'   ,'Noise'     ,1  ,0  ,0  ,False ,False]
lc_instlist[30] = ['Stomp'           ,'Stomp'     ,0  ,1  ,-1 ,False ,False]
lc_instlist[31] = ['Twin Stomp'      ,'Stomp'     ,0  ,1  ,-1 ,False ,False]
lc_instlist[32] = ['Twin Drum'       ,'Drum'      ,0  ,2  ,0  ,False ,False]
lc_instlist[33] = ['Punch'           ,'Punch'     ,0  ,1  ,1  ,False ,False]
lc_instlist[34] = ['Orchestra Hit'   ,'OrchHit'   ,0  ,0  ,0  ,False ,False]

lc_instlist[35] = ['Short Freq Noise','FreqNoise' ,0  ,0  ,0  ,False ,False]
lc_instlist[36] = ['Hammer'          ,'FreqNoise' ,0  ,1  ,0  ,False ,False]
lc_instlist[37] = ['Robot'           ,'FreqNoise' ,1  ,0  ,0  ,False ,False]
lc_instlist[38] =['Glide S-Freq Noise','FreqNoise',0  ,0  ,0  ,False ,True ]
lc_instlist[39] = ['12.5% Pulse'     ,'Pulse125'  ,0  ,0  ,0  ,False ,False]
lc_instlist[46] = ['Pulse Brass'     ,'Pulse125'  ,0  ,0  ,0  ,False ,True ]
lc_instlist[40] = ['Lo-Fi Piano'     ,'Pulse125'  ,0  ,1  ,0  ,False ,False]
lc_instlist[41] = ['Fiddle'          ,'Pulse125'  ,1  ,0  ,0  ,False ,False]
lc_instlist[42] = ['Glide 12.5% Pulse','Pulse125' ,0  ,0  ,0  ,True  ,False]
lc_instlist[43] = ['Dog'             ,'Dog'       ,0  ,0  ,-1 ,False ,False]
lc_instlist[45] = ['Robo Stomp'      ,'RoboStomp' ,0  ,0  ,-1 ,False ,False]
lc_instlist[47] =['Low-Reso Triangle','LowResoTri',0  ,0  ,0  ,False ,False]
lc_instlist[48] =['Low-Reso Xylophone','LowResoTri',0 ,1  ,0  ,False ,False]
lc_instlist[49] = ['Low-Reso Vocal'  ,'LowResoTri',0  ,0  ,0  ,False ,True ]
lc_instlist[50] = ['Glide L-Triangle','LowResoTri',0  ,0  ,0  ,True  ,False]
lc_instlist[51] = ['Low-Reso Flute'  ,'LowResoTri',1  ,0  ,0  ,True  ,False]
lc_instlist[52] = ['Tilted Sawtooth' ,'TiltedSaw' ,1  ,0  ,0  ,False ,False]

#                  Name,             Type,        FadeIn, FadeOut, PitchMod, Slide, Vib, Color

lc_instlist[53] = ['Organ Like Wave' ,'Organ'     ,0  ,0  ,0  ,False ,False]
lc_instlist[54] = ['Phaser Triangle' ,'PhaserTri' ,0  ,0  ,0  ,False ,False]
lc_instlist[55] = ['Plucked String'  ,'TiltedSaw' ,0  ,1  ,0  ,False ,False]
lc_instlist[56] = ['Bell'            ,'Organ'     ,0  ,1  ,0  ,False ,False]
lc_instlist[57] = ['Star'            ,'PhaserTri' ,0  ,1  ,0  ,False ,False]
lc_instlist[58] = ['Oboe'            ,'TiltedSaw' ,0  ,0  ,0  ,False ,True ]
lc_instlist[59] = ['Opera Choir'     ,'Organ'     ,0  ,0  ,0  ,False ,True ]
lc_instlist[60] = ['Country String'  ,'TiltedSaw' ,1  ,0  ,0  ,False ,False]
lc_instlist[61] = ['Accordian'       ,'Organ'     ,1  ,0  ,0  ,False ,False]
lc_instlist[62] = ['Planet'          ,'PhaserTri' ,1  ,0  ,0  ,False ,False]
lc_instlist[63] = ['Bubble'          ,'LowResoTri',0  ,0  ,1  ,False ,False]
lc_instlist[64] = ['Glide Organ'     ,'Organ'     ,0  ,0  ,0  ,True  ,False]
lc_instlist[65] = ['Glide Tilted Saw','TiltedSaw' ,0  ,0  ,0  ,True  ,False]
lc_instlist[66] = ['Alien'           ,'LowResoTri',0  ,0  ,-.5,False ,False]
lc_instlist[67] = ['Melodic Tom'     ,'Triangle'  ,0  ,0  ,-.5,False ,False]

lc_instlist[68] = ['FastArp Square'  ,'FA-Square' ,0  ,0  ,0  ,False ,False]
lc_instlist[69] = ['FastArp Pulse25' ,'FA-Pul25'  ,0  ,0  ,0  ,False ,False]
lc_instlist[70] = ['FastArp Pulse125','FA-Pul125' ,0  ,0  ,0  ,False ,False]
lc_instlist[71] = ['FastArp Triangle','FA-Tri'    ,0  ,0  ,0  ,False ,False]
lc_instlist[72] = ['FastArp Sine'    ,'FA-Sine'   ,0  ,0  ,0  ,False ,False]
lc_instlist[73] =['FastArp TiltedSaw','FA-TiltSaw',0  ,0  ,0  ,False ,False]
lc_instlist[74] = ['FastArp Noise'   ,'FA-Noise'  ,0  ,0  ,0  ,False ,False]

lc_instlist[120] = ['Tone A'         ,'ToneA'     ,0  ,1  ,0  ,False ,False]
lc_instlist[121] = ['Tone B'         ,'ToneB'     ,0  ,1  ,0  ,False ,False]
lc_instlist[122] = ['Tone C'         ,'ToneC'     ,0  ,1  ,0  ,False ,False]
lc_instlist[123] = ['Tone D'         ,'ToneD'     ,0  ,1  ,0  ,False ,False]

lc_instlist[128]= ['_EXT'            ,'_EXT'      ,0  ,0  ,0  ,False ,False]
lc_instlist[129]= ['_EXT_E'          ,'_EXT'      ,0  ,1  ,0  ,False ,False]

def decode_tempo(inpit_val): return (3614.75409836/inpit_val)/2

def decode_pan(panbyte):
	if panbyte == 8: return 0
	elif panbyte == 15: return 1
	elif panbyte == 1: return -1
	else: return 0

def chord_parser(chordval):
	chordid = ((chordval)>>16)&0b111111
	extrachord = chordval>>22
	chordbytes_seven = extrachord&0b11
	chordbytes_nine = (extrachord>>2)&0b11
	output_val = None
	if chordid == 1: output_val = None
	else: 
		if chordid == 2: output_val = [0, 4, 7]
		if chordid == 3: output_val = [0, 3, 7]
		if chordid == 6: output_val = [0, 3, 6]
		if chordid == 5: output_val = [0, 4, 8]
		if chordid == 4: output_val = [0, 5, 7]
		if chordbytes_seven == 1: output_val.append(10)
		if chordbytes_seven == 2: output_val.append(11)
		if chordbytes_nine == 1: output_val.append(14)
		if chordbytes_nine == 2: output_val.append(13)
	return output_val

def customtone(project_obj, tonenum, osc_data, plugin_obj):
	osc_data.prop.type = 'wave'
	osc_data.prop.nameid = 'main'
	wave_type = project_obj.wave_memory_type_list[tonenum]
	wave_data = project_obj.wave_memory_table_list[tonenum]
	if wave_type == 0:
		wave_obj = plugin_obj.wave_add('main')
		wave_obj.set_all_range(wave_data, -32, 32)
	if wave_type == 1:
		wave_data = [x for n, x in enumerate(wave_data) if n%2 == 0]
		wave_obj = plugin_obj.wave_add('main')
		wave_obj.set_all_range(wave_data, -32, 32)

class input_lc(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'lovelycomposer'
	def get_name(self): return 'Lovely Composer'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['jsonl']
		in_dict['track_lanes'] = True
		in_dict['plugin_included'] = ['universal:synth-osc']
		in_dict['auto_types'] = ['pl_points']
		in_dict['projtype'] = 'ms'
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_lovelycomposer

		convproj_obj.type = 'ms'
		convproj_obj.set_timings(4, False)

		project_obj = proj_lovelycomposer.LCMusic()
		if not project_obj.load_from_file(input_file): exit()

		if project_obj.title: convproj_obj.metadata.name = project_obj.title
		if project_obj.editor: convproj_obj.metadata.author = project_obj.editor

		globalstore.dataset.load('lovelycomposer', './data_main/dataset/lovelycomposer.dset')
		colordata = colors.colorset.from_dataset('lovelycomposer', 'track', 'main')

		for pat_num in range(len(project_obj.rhythms.ry)):
			sceneid = str(pat_num)
			convproj_obj.scene__add(sceneid)

		for tracknum in range(5):
			cvpj_instid = str(tracknum+1)
			color = colordata.getcolornum(tracknum)

			vol = xtramath.from_db(project_obj.ui_mixer_expression_list[tracknum]/2)
			pan = [0,-1,1][project_obj.mixer_output_channel_list[tracknum]]

			track_obj = convproj_obj.track__add(cvpj_instid, 'instruments', 1, False)
			track_obj.params.add('vol', vol, 'float')
			track_obj.params.add('pan', pan, 'float')
			track_obj.params.add('enabled', not project_obj.mixer_channel_switch_list[tracknum], 'bool')

			track_obj.visual.name = "Part "+cvpj_instid if tracknum != 4 else "Chord"
			track_obj.visual.color.set_float(color)
			voi_notes, voi_chord = project_obj.get_channel(tracknum)

			used_insts = []
			active_chord = [None, 0]
			active_chord_vol = 1

			for patnum, voi_note in enumerate(voi_notes):
				vl = voi_note.voicelist

				used_inst = np.unique(vl[np.where(vl['id']!=-1)]['id'])

				if project_obj.loop_end_bar != None:
					if project_obj.loop_end_bar<patnum: active_chord = [None, 0]

				if tracknum != 4:
					t_notelist = []
					prev_inst = None
					prev_key = None
					for num, vlp in enumerate(vl):
						instid = vlp['id']
						instkey = vlp['n']
						if instkey != -1:
							c_extend_inst = (not lc_instlist[instid][3]) or instid==128
							c_extend_note = instkey==prev_key
							c_extend = c_extend_inst and c_extend_note
							if not c_extend: t_notelist.append([num, 1, instkey, instid, [vlp['x']/15], [decode_pan(vlp['p'])]])
							else: 
								t_notelist[-1][1] += 1
								t_notelist[-1][4].append(vlp['x']/15)
								t_notelist[-1][5].append(decode_pan(vlp['p']))
						prev_key = instkey
						if instid<128: prev_inst = instid

					if t_notelist:
						trscene_obj = convproj_obj.track__add_scene(cvpj_instid, str(patnum), 'main')
						placement_obj = trscene_obj.add_notes()
						placement_obj.time.set_posdur(0, voi_note.play_notes)
						cvpj_notelist = placement_obj.notelist

						for nnn in t_notelist:
							maxvol = max(nnn[4])
							cvpj_ninstid = '_'.join([str(tracknum),lc_instlist[nnn[3]][1]])
							cvpj_notelist.add_m(cvpj_ninstid, nnn[0], nnn[1], nnn[2]-60, maxvol, {})
							if maxvol:
								for pos, val in enumerate(nnn[4]): 
									autopoint_obj = cvpj_notelist.last_add_auto('gain')
									autopoint_obj.pos = pos
									autopoint_obj.value = val/maxvol
							for pos, val in enumerate(nnn[5]): 
								autopoint_obj = cvpj_notelist.last_add_auto('pan')
								autopoint_obj.pos = pos
								autopoint_obj.value = val

					for i in used_inst:
						if i not in used_insts: used_insts.append(i)
				else:
					if active_chord:
						t_chordlist = [[0, 0, active_chord[0], active_chord[1], [active_chord_vol]]] if active_chord[0] else []
					else:
						t_chordlist = []
					for num, vlp in enumerate(vl):
						instid = vlp['id']
						instkey = vlp['n']
						if instkey != -1:
							if instid: 
								chordkeys = chord_parser(instid)
								t_chordlist.append([num, 0, chordkeys, instkey-60, []])
								active_chord = [chordkeys, instkey]
								active_chord_vol = vlp['x']/15

						if t_chordlist: 
							lastchord = t_chordlist[-1]
							lastchord[1] += 1
							lastchord[4].append(vlp['x']/15)



					if t_chordlist:
						trscene_obj = convproj_obj.track__add_scene(cvpj_instid, str(patnum), 'main')
						placement_obj = trscene_obj.add_notes()
						placement_obj.time.set_posdur(0, voi_note.play_notes)
						cvpj_notelist = placement_obj.notelist
						for nnn in t_chordlist:
							if nnn[2] and nnn[1]:
								maxvol = max(nnn[4])
								cvpj_notelist.add_m_multi('chord', nnn[0], nnn[1], [x+nnn[3] for x in nnn[2]], maxvol, {})

			if tracknum != 4:
				for used_instnum in used_insts:
					instdata = lc_instlist[used_instnum]

					cvpj_ninstid = '_'.join([str(tracknum),lc_instlist[used_instnum][1]])

					plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
					plugin_obj.role = 'synth'
					osc_data = plugin_obj.osc_add()
		
					inst_obj = convproj_obj.instrument__add(cvpj_ninstid)
					inst_obj.pluginid = pluginid
					inst_obj.visual.name = instdata[1]
					inst_obj.visual.color.set_float(color)
					inst_obj.is_drum = instdata[1] in ['Noise', 'FreqNoise']

					if instdata[1] == 'Sine': 
						osc_data.prop.shape = 'sine'
					elif instdata[1] == 'Square': 
						osc_data.prop.shape = 'square'
						osc_data.prop.pulse_width = 1/2
					elif instdata[1] == 'Triangle':
						osc_data.prop.shape = 'triangle'
					elif instdata[1] == 'Saw': 
						osc_data.prop.shape = 'saw'
					elif instdata[1] == 'Noise': 
						osc_data.prop.shape = 'noise'
						osc_data.prop.noise_type = '4bit'
					elif instdata[1] == 'FreqNoise': 
						osc_data.prop.shape = 'noise'
						osc_data.prop.noise_type = '1bit_short'
					elif instdata[1] == 'Pulse25': 
						osc_data.prop.shape = 'square'
						osc_data.prop.pulse_width = 1/4
					elif instdata[1] == 'Pulse125': 
						osc_data.prop.shape = 'square'
						osc_data.prop.noise_type = 1/8
					elif instdata[1] == 'ToneA': 
						osc_data.prop.type = 'wave'
						osc_data.prop.nameid = 'main'
						customtone(project_obj, 0, osc_data, plugin_obj)
					elif instdata[1] == 'ToneB': 
						osc_data.prop.type = 'wave'
						osc_data.prop.nameid = 'main'
						customtone(project_obj, 1, osc_data, plugin_obj)
					elif instdata[1] == 'ToneC': 
						osc_data.prop.type = 'wave'
						osc_data.prop.nameid = 'main'
						customtone(project_obj, 2, osc_data, plugin_obj)
					elif instdata[1] == 'ToneD': 
						osc_data.prop.type = 'wave'
						osc_data.prop.nameid = 'main'
						customtone(project_obj, 3, osc_data, plugin_obj)

					if instdata[1] in ['ToneA','ToneB','ToneC','ToneD'] and project_obj.wave_memory_effect_list: 
						tonenum = ['ToneA','ToneB','ToneC','ToneD'].index(instdata[1])

						plugin_obj.type_set('native', 'lovelycomposer', 'custom')
						plugin_obj.datavals.add('effect', project_obj.wave_memory_effect_list[tonenum])
					#else: 
					#	inst_plugindata = plugins.cvpj_plugin('deftype', 'lovelycomposer', instdata[1])
			else:
				inst_obj = convproj_obj.instrument__add('chord')
				inst_obj.visual.name = 'Chord'
				inst_obj.visual.color.set_float(color)
	
		patternlen = []
		voi_notes, voi_chord = project_obj.get_channel(tracknum)
		curpos = 0
		for pat_num, voi_note in enumerate(voi_notes):
			patlen = voi_note.play_notes
			patternlen.append(patlen)
			scenepl_obj = convproj_obj.scene__add_pl()
			scenepl_obj.position = curpos
			scenepl_obj.duration = patlen
			scenepl_obj.id = str(pat_num)

			autopl_obj = convproj_obj.automation.add_pl_points(['main', 'bpm'], 'float')
			autopl_obj.time.set_posdur(curpos, patlen)
			autopoint_obj = autopl_obj.data.add_point()
			autopoint_obj.value = decode_tempo(voi_note.play_speed)

			curpos += patlen

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.params.add('pitch', float(project_obj.mixer_transpose), 'float')
		convproj_obj.params.add('bpm', decode_tempo(project_obj.speed), 'float')