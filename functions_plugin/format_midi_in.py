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

import chardet	

idvals_midi_ctrl = idvals.parse_idvalscsv('data_idvals/midi_ctrl.csv')
idvals_midi_inst = idvals.parse_idvalscsv('data_idvals/midi_inst.csv')
idvals_midi_inst_drums = idvals.parse_idvalscsv('data_idvals/midi_inst_drums.csv')

tracknumber = 0

song_channels = 16

def getbeforenoteall(table):
	out = None
	for tp in table:
		if tp != None: 
			if out == None: out = tp
			elif out > tp: out = tp
	return out

def point2beforeafter(points, notestart):

	prevval = None
	norepeats = {}
	for ctrlpos in points:
		ctrlval = points[ctrlpos]
		if prevval == None: norepeats[ctrlpos] = ctrlval
		elif prevval != ctrlval: norepeats[ctrlpos] = ctrlval
		prevval = ctrlval
	points = norepeats

	beforeafter = [{},{},{}]
	if notestart != None:
		for ctrlpos in points:
			ctrlval = points[ctrlpos]
			if notestart > ctrlpos: beforeafter[0][ctrlpos] = ctrlval
			elif notestart == ctrlpos: beforeafter[1][ctrlpos] = ctrlval
			else: beforeafter[2][ctrlpos] = ctrlval
	else: beforeafter[0] = points
	return beforeafter

def midiauto2cvpjauto(points, divi, add):
	return [[x[0]/ppq_step, (x[1]/divi)+add] for x in points]

def points2paramauto(cvpj_l, bapoints, divi, add):
	out_param = None
	out_twopoints = []

	twopoints_BE = [[x, bapoints[0][x]] for x in bapoints[0]]
	twopoints_EX = [[x, bapoints[1][x]] for x in bapoints[1]]
	twopoints_AF = [[x, bapoints[2][x]] for x in bapoints[2]]

	bapoints_len = [len(twopoints_BE), len(twopoints_EX), len(twopoints_AF)]

	if bapoints_len[0] == 1 and bapoints_len[2] == 0 and bapoints_len[1] == 0:
		out_param = (twopoints_BE[0][1]/divi)+add
	elif bapoints_len[0] == 0 and bapoints_len[1] == 1 and bapoints_len[2] == 0:
		out_param = (twopoints_EX[0][1]/divi)+add
	else:
		out_twopoints = midiauto2cvpjauto(twopoints_BE+twopoints_EX+twopoints_AF, divi, add)

	return out_param, out_twopoints

def addfxparamdata(cvpj_l, fx_num, name, fallbackval, bapoints, divi, add):
	out_param, out_twopoints = points2paramauto(cvpj_l, bapoints, divi, add)
	if out_param != None: tracks.fxrack_param(cvpj_l, fx_num, name, out_param, 'float')
	else: tracks.fxrack_param(cvpj_l, fx_num, name, fallbackval, 'float')
	if out_twopoints != []: tracks.a_auto_nopl_twopoints(['fxmixer', str(fx_num), name], 'float', out_twopoints, 1, 'instant')

def addfxsenddata(cvpj_l, fx_num, name, bapoints, divi, add):
	out_param, out_twopoints = points2paramauto(cvpj_l, bapoints, divi, add)
	if out_param != None: tracks.fxrack_param(cvpj_l, fx_num, name, out_param, 'float')
	if out_twopoints != []: tracks.a_auto_nopl_twopoints(['fxmixer', str(fx_num), name], 'float', out_twopoints, 1, 'instant')

def add_autopoint(time, channel, param, value):
	global automation_channel
	if param not in automation_channel[channel]: automation_channel[channel][param] = {}
	automation_channel[channel][param][time] = value

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
	global global_miditracks

	global_miditracks = []

	auto_bpm = {}
	auto_timesig = {}
	auto_sysex = {}
	auto_master = {}
	auto_key_signature = {}
	auto_markers = {}

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

	global auto_bpm
	global auto_timesig
	global auto_sysex
	global auto_master
	global auto_key_signature
	global auto_markers

	track_name = None
	track_color = None
	track_copyright = None
	track_mode = 0 # 0=normal 1=single

	track_curpos = 0

	sequencer_specific = []

	t_chan_current_inst = [[0, 0, 0] for x in range(song_channels)]
	t_chan_used_inst = [[] for x in range(song_channels)]
	track_active_notes = [[[] for x in range(128)] for x in range(song_channels)]

	track_chantype = []
	for num in range(song_channels):
		if num == 9: 
			track_chantype.append(1)
			t_chan_current_inst[num] = [0, 0, 1]
		else: track_chantype.append(0)

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

		elif midicmd[0] == 'control_change': add_autopoint(track_curpos, midicmd[1], midicmd[2], midicmd[3])

		elif midicmd[0] == 'pitchwheel': add_autopoint(track_curpos, midicmd[1], 'pitchwheel', midicmd[2])

		elif midicmd[0] == 'tempo': auto_bpm[track_curpos] = midicmd[1]

		elif midicmd[0] == 'timesig': auto_timesig[track_curpos] = [midicmd[1], midicmd[2]]

		elif midicmd[0] == 'sysex': add_point(auto_sysex, track_curpos, midicmd[1])

		elif midicmd[0] == 'marker': add_point(auto_markers, track_curpos, midicmd[1])

		elif midicmd[0] == 'key_signature': add_point(auto_key_signature, track_curpos, midicmd[1])

		elif midicmd[0] == 'note_on':
			curinst = t_chan_current_inst[midicmd[1]]
			track_active_notes[midicmd[1]][midicmd[2]].append([track_curpos,None,midicmd[3],curinst[0],curinst[1],curinst[2]])

		elif midicmd[0] == 'note_off': 
			for note in track_active_notes[midicmd[1]][midicmd[2]]:
				if note[1] == None:
					note[1] = track_curpos
					break

		else: print(track_curpos, midicmd)

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
						note_drum = t_actnote[5]

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
		instname = idvals.get_idval(idvals_midi_inst, str(used_inst[1]), 'name')
		instcolor = idvals.get_idval(idvals_midi_inst, str(used_inst[1]), 'color')
		used_insts[instnum] += [instname,instcolor]

	for used_inst in used_insts:
		instid = '_'.join([str(used_inst[0]), str(used_inst[1]), str(used_inst[2]), str(used_inst[3])])

		if used_inst[3] == 0: 
			instname = used_inst[4]
			instcolor = used_inst[5]
			plugins.add_plug_gm_midi(cvpj_l, instid, used_inst[2], used_inst[1])
		else: 
			instname = 'Drums'
			instcolor = [0.81, 0.80, 0.82]
			plugins.add_plug_gm_midi(cvpj_l, instid, 128, 1)

		tracks.c_inst_create(cvpj_l, instid, name=instname, color=instcolor)
		tracks.c_inst_add_dataval(cvpj_l, instid, None, 'fxrack_channel', int(used_inst[0]+1))
		tracks.c_inst_pluginid(cvpj_l, instid, instid)

	for fxnum in range(song_channels):
		s_fx_usedinstid = fx_usedinstid[fxnum]

		for i_fx_usedinstid in s_fx_usedinstid:
			groupname = idvals.get_idval(idvals_midi_inst, str(i_fx_usedinstid[1]), 'group')
			i_fx_usedinstid.append(groupname)

		usedinlen = len(s_fx_usedinstid)
		if usedinlen == 1:
			usedinstid = s_fx_usedinstid[0]
			trackname = global_miditracks[usedinstid[0]][1]
			if usedinstid[3] == 0: instname = idvals.get_idval(idvals_midi_inst, str(usedinstid[1]), 'name')
			else: instname = 'Drums'
			if trackname not in [None, ''] and tracknumber != 1: fxchannames[fxnum] = trackname
			else: fxchannames[fxnum] = instname

			trackcolor = global_miditracks[usedinstid[0]][4]
			if usedinstid[3] == 0: instcolor = idvals.get_idval(idvals_midi_inst, str(usedinstid[1]), 'color')
			else: instcolor = [0.81, 0.80, 0.82]
			if trackcolor != None: fxchancolors[fxnum] = trackcolor
			elif instcolor != None: fxchancolors[fxnum] = instcolor

			fxchancolors
		elif usedinlen > 1:
			ifsametrackid = data_values.ifallsame([s_fx_usedinstid[x][0] for x in range(usedinlen)])
			ifsameinstid = data_values.ifallsame([s_fx_usedinstid[x][1] for x in range(usedinlen)])
			ifsamegroups = data_values.ifallsame([s_fx_usedinstid[x][4] for x in range(usedinlen)])
			ifsamealldrums = data_values.ifallsame([s_fx_usedinstid[x][3] for x in range(usedinlen)])

			if ifsamealldrums == True and s_fx_usedinstid[0][3] == 1:
				fxchannames[fxnum] = 'Drums'
				fxchancolors[fxnum] = [0.81, 0.80, 0.82]
				#print('alldrums')
			elif ifsametrackid == True and tracknumber != 1:
				trackname = global_miditracks[s_fx_usedinstid[0][0]][1]
				fxchancolors[fxnum] = [0.4, 0.4, 0.4]
				if trackname != None: fxchannames[fxnum] = trackname
				elif ifsamegroups == True: fxchannames[fxnum] = s_fx_usedinstid[0][4]

			elif ifsameinstid == True:
				fxchannames[fxnum] = idvals.get_idval(idvals_midi_inst, str(s_fx_usedinstid[0][1]), 'name')
				fxchancolors[fxnum] = idvals.get_idval(idvals_midi_inst, str(s_fx_usedinstid[0][1]), 'color')
				#print('instid')
			elif ifsamegroups == True:
				fxchannames[fxnum] = s_fx_usedinstid[0][4]
				fxchancolors[fxnum] = [0.4, 0.4, 0.4]
				#print('groups')


	for channum in range(song_channels):
		s_automation_chan = automation_channel[channum]

		for ctrlnum in s_automation_chan:
			s_automation_chan[ctrlnum] = point2beforeafter(s_automation_chan[ctrlnum], firstchanusepos[channum])
	
	tracks.fxrack_add(cvpj_l, 0, "Master", [0.3, 0.3, 0.3], 1.0, None)

	usedeffects = [False,False]

	for midi_channum in range(song_channels):
		s_chanauto = automation_channel[midi_channum]
		fxrack_chan = str(midi_channum+1)
		tracks.fxrack_add(cvpj_l, fxrack_chan, fxchannames[midi_channum], fxchancolors[midi_channum], None, None)
		if 7 in s_chanauto: addfxparamdata(cvpj_l, midi_channum+1, 'vol', 1, s_chanauto[7],127,0)
		if 10 in s_chanauto: addfxparamdata(cvpj_l, midi_channum+1, 'pan', 0, s_chanauto[10],64,-1)
		if 'pitchwheel' in s_chanauto: addfxparamdata(cvpj_l, midi_channum+1, 'pitch', 0, s_chanauto['pitchwheel'],1,0)

		for ccnum, fx2, fx1, fxname in [[91,0,0,'reverb'],[93,0,1,'chorus'],[92,1,0,'tremolo'],[95,1,1,'phaser']]:
			if ccnum in s_chanauto:
				sendname = str(midi_channum)+fxname
				usedeffects[fx2] = True
				sendtofx = song_channels+1+fx1+(fx2*2)
				out_param, out_twopoints = points2paramauto(cvpj_l, s_chanauto[ccnum], 127, 0)
				sendamt = out_param if out_param != None else 0
				tracks.fxrack_addsend(cvpj_l, midi_channum+1, 0, 1, None)
				tracks.fxrack_addsend(cvpj_l, midi_channum+1, sendtofx, sendamt, sendname)
				if out_twopoints != []: 
					print(out_twopoints)
					tracks.a_auto_nopl_twopoints(['send', sendname, 'amount'], 'float', out_twopoints, 1, 'instant')

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
	out_param, out_twopoints = points2paramauto(cvpj_l, point2beforeafter(auto_bpm, veryfirstnotepos), 1, 0)
	if out_param != None: params.add(cvpj_l, [], 'bpm', out_param, 'float')
	if out_twopoints != []: tracks.a_auto_nopl_twopoints(['main', 'bpm'], 'float', out_twopoints, 1, 'instant')

	for timesigpoint in auto_timesig:
		timesig = auto_timesig[timesigpoint]
		timesigpos = (timesigpoint/ppq_step)
		if timesigpoint == 0: cvpj_l['timesig'] = timesig
		song.add_timemarker_timesig(cvpj_l, str(timesig[0])+'/'+str(timesig[1]), (timesigpoint/ppq_step), timesig[0], timesig[1])

	tracks.a_auto_nopl_to_cvpj(cvpj_l)