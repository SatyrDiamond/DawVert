# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from functions import placement_data
from functions import note_data
from functions import data_values
from functions import idvals
from functions import midi_exdata
from functions import params
from functions import plugins
from functions import tracks
from functions import song
from functions import colors
from functions import auto

import chardet	

idvals_midi_ctrl = idvals.parse_idvalscsv('data_idvals/midi_ctrl.csv')
idvals_midi_inst = idvals.parse_idvalscsv('data_idvals/midi_inst.csv')
idvals_midi_inst_drums = idvals.parse_idvalscsv('data_idvals/midi_inst_drums.csv')
idvals_midi_inst_group = idvals.parse_idvalscsv('data_idvals/midi_inst_group.csv')

tracknumber = 0

song_channels = 16

def getbeforenoteall(table):
	out = None
	for tp in table:
		if tp != None: 
			if out == None: out = tp
			elif out > tp: out = tp
	return out

def add_chautopoint(time, channel, param, value):
	global automation_channel
	if param not in automation_channel[channel]: automation_channel[channel][param] = {}
	automation_channel[channel][param][time] = value

def add_autopoint(time, i_list, param, value):
	if param not in i_list: i_list[param] = {}
	i_list[param][time] = value

def add_point(i_list, time, value):
	if time not in i_list: i_list[time] = []
	i_list[time].append(value)

def song_start(numchannels, ppq, numtracks, tempo, timesig):
	global tracknumber
	global ppq_step
	global ppq_g
	global used_chan_inst
	global automation_channel
	global cvpj_l
	global song_channels

	global auto_bpm
	global auto_timesig
	global auto_sysex
	global auto_master
	global auto_key_signature
	global auto_markers
	global auto_chanmode
	global global_miditracks
	global global_data
	global loop_data

	global_miditracks = []

	auto_bpm = {}
	auto_timesig = {}
	auto_sysex = {}
	auto_master = {}
	auto_key_signature = {}
	auto_markers = {}
	auto_chanmode = [{0: False} for _ in range(numchannels)]
	auto_chanmode[9] = {0: True}
	global_data = {}
	loop_data = [None, None]


	ppq_g = ppq
	ppq_step = ppq/4
	used_chan_inst = [[] for _ in range(numchannels)]
	automation_channel = [{} for _ in range(numchannels)]
	song_channels = numchannels

def add_track(startpos, midicmds):
	global global_miditracks

	global tracknumber
	global used_chan_inst
	global automation_channel
	global song_channels
	global ppq_step

	global auto_bpm
	global auto_timesig
	global auto_sysex
	global auto_master
	global auto_key_signature
	global auto_markers
	global auto_chanmode
	global global_data
	global loop_data

	track_name = None
	track_color = None
	track_copyright = None
	track_mode = 0 # 0=normal 1=single

	track_curpos = 0

	sequencer_specific = []

	t_chan_current_inst = [[0, 0] for x in range(song_channels)]
	t_chan_used_inst = [[] for x in range(song_channels)]
	track_active_notes = [[[] for x in range(128)] for x in range(song_channels)]

	loop_data = [None, None]

	for midicmd in midicmds:

		if midicmd[0] == 'rest': track_curpos += midicmd[1]

		elif midicmd[0] == 'track_name': track_name = midicmd[1]

		elif midicmd[0] == 'sequencer_specific': 
			exdata = midi_exdata.decode_exdata(midicmd[1], True)
			if exdata[0] == [83]:
				if exdata[1][0:5] == b'ign\x01\xff': #from Signal MIDI Editor
					track_color = colors.rgb_int_to_rgb_float(exdata[1][5:8][::-1])
			else:
				sequencer_specific.append(midicmd[1])

		elif midicmd[0] == 'copyright': track_copyright = midicmd[1]

		elif midicmd[0] == 'program_change': t_chan_current_inst[midicmd[1]][0] = midicmd[2]

		elif midicmd[0] == 'control_change': 
			if midicmd[2] == 0: t_chan_current_inst[midicmd[1]][1] = midicmd[3]
			elif midicmd[2] == 111: loop_data[0] = track_curpos/ppq_step
			else: add_chautopoint(track_curpos, midicmd[1], midicmd[2], midicmd[3])

		elif midicmd[0] == 'pitchwheel': add_chautopoint(track_curpos, midicmd[1], 'pitch', midicmd[2])

		elif midicmd[0] == 'tempo': auto_bpm[track_curpos] = midicmd[1]

		elif midicmd[0] == 'timesig': auto_timesig[track_curpos] = [midicmd[1], midicmd[2]]

		elif midicmd[0] == 'sysex': 
			#add_point(auto_sysex, track_curpos, midicmd[1])
			sysexdata = midi_exdata.decode(midicmd[1])
			if sysexdata != None:
				out_vendor, out_vendor_ext, out_brandname, out_device, out_model, out_command, out_data, devicename, groups, nameval = sysexdata

				if [out_vendor, out_vendor_ext] == [127, False]:
					if groups == ['device', None]:
						if nameval[0] == 'master_volume': add_autopoint(track_curpos, auto_master, 'volume', nameval[1][1]/127)

				if [out_vendor, out_vendor_ext] == [65, False]:
					if groups[0] == 'patch_a':
						if groups[1] == None:
							if nameval[0] == 'master_volume': add_autopoint(track_curpos, auto_master, 'volume', nameval[1][0]/127)
						if groups[1] == 'block':
							if nameval[0] == 'use_rhythm':
								auto_chanmode[groups[2]-1][track_curpos] = bool(nameval[1])

		elif midicmd[0] == 'marker': add_point(auto_markers, track_curpos, midicmd[1])

		elif midicmd[0] == 'key_signature': add_point(auto_key_signature, track_curpos, midicmd[1])

		elif midicmd[0] == 'note_on':
			curinst = t_chan_current_inst[midicmd[1]]
			track_active_notes[midicmd[1]][midicmd[2]].append([track_curpos,None,midicmd[3],curinst[0],curinst[1]])

		elif midicmd[0] == 'note':
			curinst = t_chan_current_inst[midicmd[1]]
			track_active_notes[midicmd[1]][midicmd[2]].append([track_curpos,track_curpos+midicmd[4],midicmd[3],curinst[0],curinst[1]])

		elif midicmd[0] == 'note_off': 
			for note in track_active_notes[midicmd[1]][midicmd[2]]:
				if note[1] == None:
					note[1] = track_curpos
					break

		#else: print(track_curpos, midicmd)



	global_miditracks.append([track_active_notes, track_name, track_copyright, sequencer_specific, track_color, track_mode])
	tracknumber += 1

def song_end(cvpj_l):
	global tracknumber
	global ppq_step
	global used_chan_inst
	global automation_channel
	global song_channels

	global auto_bpm
	global auto_timesig
	global auto_sysex
	global auto_key_signature
	global auto_markers
	global global_miditracks
	global global_data
	global loop_data

	used_insts = []
	firstchanusepos = [None for x in range(song_channels)]
	fxchannames = ['Chan #'+str(x+1) for x in range(song_channels)]
	fxchancolors = [[0, 0, 0] for _ in range(song_channels)]
	fx_usedinstid = [[] for x in range(song_channels)]

	numtracks = len(global_miditracks)

	tracknum = 0
	for global_miditrack in global_miditracks:
		cvpj_trackid = 'track_'+str(tracknum)
		track_color = global_miditrack[4]

		t_cvpj_notelist = []
		for channelnum in range(song_channels):
			#print(channelnum)
			notekey = -60
			for c_active_notes in global_miditrack[0][channelnum]:
				for t_actnote in c_active_notes:
					#print(notekey, '-------------', t_actnote)
					if t_actnote[1] != None:

						if firstchanusepos[channelnum] == None: firstchanusepos[channelnum] = t_actnote[0]
						elif t_actnote[0] < firstchanusepos[channelnum]: firstchanusepos[channelnum] = t_actnote[0]

						note_pos = t_actnote[0]/ppq_step
						note_dur = (t_actnote[1]-t_actnote[0])/ppq_step
						note_key = notekey
						note_chan = channelnum
						note_inst = t_actnote[3]
						note_bank = t_actnote[4]
						closest_drum = data_values.closest(auto_chanmode[note_chan], t_actnote[0])
						note_drum = int(auto_chanmode[note_chan][closest_drum])
						#print(note_chan, t_actnote[0], closest_drum, auto_chanmode[note_chan], note_drum)

						used_inst_part = [note_chan,note_inst,note_bank,note_drum]
						if used_inst_part not in used_insts: used_insts.append(used_inst_part)

						fxui_part = [tracknum,note_inst,note_bank,note_drum]
						if fxui_part not in fx_usedinstid[note_chan]: fx_usedinstid[note_chan].append(fxui_part)

						note_instid = '_'.join([str(note_chan), str(note_inst), str(note_bank), str(note_drum)])
						notedata = note_data.mx_makenote(note_instid, note_pos, note_dur, notekey, t_actnote[2]/127, None)
						notedata['channel'] = channelnum+1
						t_cvpj_notelist.append(notedata)
				notekey += 1

		placementdata = placement_data.nl2pl(t_cvpj_notelist)
		trackname = None
		if numtracks == 1: song.add_info(cvpj_l, 'title', global_miditrack[1])
		else: trackname = global_miditrack[1]
		tracks.c_create_track(cvpj_l, 'instruments', cvpj_trackid, name=trackname, color=track_color)
		tracks.c_pl_notes(cvpj_l, cvpj_trackid, placementdata)
		tracknum += 1

	for instnum in range(len(used_insts)):
		used_inst = used_insts[instnum]
		if used_inst[3] == 0: 
			instname = idvals.get_idval(idvals_midi_inst, str(used_inst[1]), 'name')
			instcolor = idvals.get_idval(idvals_midi_inst, str(used_inst[1]), 'color')
		else:
			instname = 'Drums'
			instcolor = [0.81, 0.80, 0.82]

		used_insts[instnum] += [instname,instcolor]

	for used_inst in used_insts:
		instid = '_'.join([str(used_inst[0]), str(used_inst[1]), str(used_inst[2]), str(used_inst[3])])

		instname = used_inst[4]
		instcolor = used_inst[5]

		if used_inst[3] == 0: plugins.add_plug_gm_midi(cvpj_l, instid, used_inst[2], used_inst[1])
		else: plugins.add_plug_gm_midi(cvpj_l, instid, 128, 1)

		tracks.c_inst_create(cvpj_l, instid, name=instname, color=instcolor)
		tracks.c_inst_add_dataval(cvpj_l, instid, None, 'fxrack_channel', int(used_inst[0]+1))
		tracks.c_inst_pluginid(cvpj_l, instid, instid)

	for fxnum in range(song_channels):
		s_fx_usedinstid = fx_usedinstid[fxnum]

		for i_fx_usedinstid in s_fx_usedinstid:
			groupname = idvals.get_idval(idvals_midi_inst, str(i_fx_usedinstid[1]), 'group')
			i_fx_usedinstid.append(groupname)

		fx_name = None
		fx_color = None

		usedinlen = len(s_fx_usedinstid)
		if usedinlen == 1:
			usedinstid = s_fx_usedinstid[0]

			iftrackname = (global_miditracks[usedinstid[0]][1] not in [None, '']) and tracknum != 1
			iftrackcolor = global_miditracks[usedinstid[0]][4]

			if fx_name == None and iftrackname: 
				fx_n_namefrom, fx_name = '1_track', global_miditracks[usedinstid[0]][1]
			if fx_name == None: 
				if usedinstid[3] == 0: 
					fx_n_namefrom, fx_name = '1_inst', idvals.get_idval(idvals_midi_inst, str(usedinstid[1]), 'name')
				else: 
					fx_n_namefrom, fx_name = '1_drums', 'Drums'
	
			if fx_color == None and iftrackcolor != None:
				fx_c_namefrom, fx_color = '1_track', global_miditracks[usedinstid[0]][4]
			if fx_color == None:
				if usedinstid[3] == 0: 
					fx_c_namefrom, fx_color = '1_inst', idvals.get_idval(idvals_midi_inst, str(usedinstid[1]), 'color')
				else: 
					fx_c_namefrom, fx_color = '1_drums',[0.81, 0.80, 0.82]
	

		elif usedinlen > 1:
			ifsametrackid = data_values.ifallsame([s_fx_usedinstid[x][0] for x in range(usedinlen)])
			ifsameinstid = data_values.ifallsame([s_fx_usedinstid[x][1] for x in range(usedinlen)])
			ifsamegroups = data_values.ifallsame([s_fx_usedinstid[x][4] for x in range(usedinlen)])
			ifsamealldrums = data_values.ifallsame([s_fx_usedinstid[x][3] for x in range(usedinlen)]) and s_fx_usedinstid[0][3]

			fx_n_namefrom = None
			fx_c_namefrom = None

			if fx_name == None and ifsametrackid: fx_n_namefrom, fx_name = 'track', global_miditracks[s_fx_usedinstid[0][0]][1]
			if fx_name == None and ifsameinstid: 
				if ifsamealldrums: fx_n_namefrom, fx_name = 'inst-drums', 'Drums'
				else: fx_n_namefrom, fx_name = 'inst', idvals.get_idval(idvals_midi_inst, str(s_fx_usedinstid[0][1]), 'name')
			if fx_name == None and ifsamegroups: fx_n_namefrom, fx_name = 'groups', idvals.get_idval(idvals_midi_inst_group, str(s_fx_usedinstid[0][4]), 'name')
			if fx_name == None and ifsamealldrums: fx_n_namefrom, fx_name = 'drums', 'Drums'
			if fx_name == None:
				usedgroups = list(set([s_fx_usedinstid[x][4] for x in range(usedinlen)]))
				usedgroups = [idvals.get_idval(idvals_midi_inst_group, x, 'name') for x in usedgroups]
				fx_n_namefrom, fx_name = 'mulgroup', ' + '.join(usedgroups)


			if fx_color == None and ifsametrackid: fx_c_namefrom, fx_color = 'track', global_miditracks[s_fx_usedinstid[0][0]][4]
			if fx_color == None and ifsamealldrums: fx_c_namefrom, fx_color = 'drums', [0.81, 0.80, 0.82]
			if fx_color == None and ifsameinstid: fx_c_namefrom, fx_color = 'inst', idvals.get_idval(idvals_midi_inst, str(s_fx_usedinstid[0][1]), 'color')
			if fx_color == None and ifsamegroups: fx_c_namefrom, fx_color = 'groups', idvals.get_idval(idvals_midi_inst_group, str(s_fx_usedinstid[0][4]), 'color')
			if fx_color == None: fx_c_namefrom, fx_color = 'none', [0.4, 0.4, 0.4]

		#if usedinlen != 0: print(
		#	fxnum, usedinlen, '|', 
		#	fx_n_namefrom, fx_name, '|', 
		#	fx_c_namefrom, fx_color, '|', 
		#	s_fx_usedinstid)

		if fx_name != None: fxchannames[fxnum] = fx_name
		if fx_color != None: fxchancolors[fxnum] = fx_color

	tracks.fxrack_add(cvpj_l, 0, "Master", [0.3, 0.3, 0.3], 1.0, None)

	usedeffects = [False,False]

	for midi_channum in range(song_channels):
		s_chanauto = automation_channel[midi_channum]
		fxrack_chan = str(midi_channum+1)
		tracks.fxrack_add(cvpj_l, fxrack_chan, fxchannames[midi_channum], fxchancolors[midi_channum], None, None)

		for ccnum, name, defval, valdiv, valadd in [
			[  1 ,'modulation',    1,  127,   0],
			[  7 ,'vol',           1,  127,   0],
			[  10,'pan',           0,  64,   -1],
			[  11,'expression',    1,  127,   0],
			['pitch','pitch',      0,  1,     0],
		]:
			if ccnum in s_chanauto: 
				out_param = tracks.a_auto_nopl_paramauto(
					['fxmixer', fxrack_chan, name], 'float', s_chanauto[ccnum], ppq_step, firstchanusepos[midi_channum], defval, valdiv, valadd)
				tracks.fxrack_param(cvpj_l, midi_channum+1, name, out_param, 'float')

		for ccnum, fx2, fx1, fxname in [[91,0,0,'reverb'],[93,0,1,'chorus'],[92,1,0,'tremolo'],[95,1,1,'phaser']]:
			if ccnum in s_chanauto:
				sendname = str(midi_channum)+fxname
				usedeffects[fx2] = True
				sendtofx = song_channels+1+fx1+(fx2*2)
				out_param = tracks.a_auto_nopl_paramauto(['send', sendname, 'amount'], 'float', s_chanauto[ccnum], ppq_step, firstchanusepos[midi_channum], 0, 127, 0)
				tracks.fxrack_addsend(cvpj_l, midi_channum+1, 0, 1, None)
				tracks.fxrack_addsend(cvpj_l, midi_channum+1, sendtofx, out_param, sendname)

	if usedeffects[0] == True:
		plugins.add_plug(cvpj_l, 'plugin-reverb', 'simple', 'reverb-send')
		plugins.add_plug(cvpj_l, 'plugin-chorus', 'simple', 'chorus-send')
		plugins.add_plug_fxvisual(cvpj_l, 'plugin-reverb', 'Reverb', None)
		plugins.add_plug_fxvisual(cvpj_l, 'plugin-chorus', 'Chorus', None)
		tracks.fxrack_add(cvpj_l, song_channels+1, "[S] Reverb", [0.4, 0.4, 0.4], 1.0, None)
		tracks.fxrack_add(cvpj_l, song_channels+2, "[S] Chorus", [0.4, 0.4, 0.4], 1.0, None)
		tracks.insert_fxslot(cvpj_l, ['fxrack', song_channels+1], 'audio', 'plugin-reverb')
		tracks.insert_fxslot(cvpj_l, ['fxrack', song_channels+2], 'audio', 'plugin-chorus')
		tracks.fxrack_addsend(cvpj_l, song_channels+1, 0, 1, None)
		tracks.fxrack_addsend(cvpj_l, song_channels+2, 0, 1, None)

	if usedeffects[1] == True:
		plugins.add_plug(cvpj_l, 'plugin-tremelo', 'simple', 'tremelo-send')
		plugins.add_plug(cvpj_l, 'plugin-phaser', 'simple', 'phaser-send')
		plugins.add_plug_fxvisual(cvpj_l, 'plugin-tremelo', 'Tremelo', None)
		plugins.add_plug_fxvisual(cvpj_l, 'plugin-phaser', 'Phaser', None)
		tracks.fxrack_add(cvpj_l, song_channels+3, "[S] Tremelo", [0.4, 0.4, 0.4], 1.0, None)
		tracks.fxrack_add(cvpj_l, song_channels+4, "[S] Phaser", [0.4, 0.4, 0.4], 1.0, None)
		tracks.insert_fxslot(cvpj_l, ['fxrack', song_channels+3], 'audio', 'plugin-tremelo')
		tracks.insert_fxslot(cvpj_l, ['fxrack', song_channels+4], 'audio', 'plugin-phaser')
		tracks.fxrack_addsend(cvpj_l, song_channels+3, 0, 1, None)
		tracks.fxrack_addsend(cvpj_l, song_channels+4, 0, 1, None)

	veryfirstnotepos = getbeforenoteall(firstchanusepos)

	#tempo
	out_param = tracks.a_auto_nopl_paramauto(['main', 'bpm'], 'float', auto_bpm, ppq_step, veryfirstnotepos, 120, 1, 0)
	params.add(cvpj_l, [], 'bpm', out_param, 'float')

	#volume
	if 'volume' in auto_master:
		out_param = tracks.a_auto_nopl_paramauto(['fxmixer', '0', 'vol'], 'float', auto_master['volume'], ppq_step, veryfirstnotepos, 127, 1, 0)
		tracks.fxrack_param(cvpj_l, 0, 'vol', out_param, 'float')

	#timesig
	for timesigpoint in auto_timesig:
		timesig = auto_timesig[timesigpoint]
		timesigpos = (timesigpoint/ppq_step)
		if timesigpoint == 0: cvpj_l['timesig'] = timesig
		song.add_timemarker_timesig(cvpj_l, str(timesig[0])+'/'+str(timesig[1]), (timesigpoint/ppq_step), timesig[0], timesig[1])

	#timesig
	if loop_data[1] != None: song.add_timemarker_looparea(cvpj_l, 'Loop', loop_data[0], loop_data[1])
	elif loop_data[0] != None: song.add_timemarker_loop(cvpj_l, loop_data[0], 'Loop')
	
	tracks.a_auto_nopl_to_cvpj(cvpj_l)

	return used_insts