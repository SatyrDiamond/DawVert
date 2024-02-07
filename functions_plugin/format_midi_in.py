# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from functions import placement_data
from functions import note_data
from functions import data_values
from functions import midi_exdata
from objects import dv_dataset
from functions import params
from functions import plugins
from functions import song
from functions import colors
from functions import auto
from functions_tracks import tracks_rm
from functions_tracks import fxrack
from functions_tracks import fxslot
from functions_tracks import auto_nopl

import chardet	

dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

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

def add_fx(cvpj_l, fx_num, fxname, visname, wet_val):
	fx_plugindata = plugins.cvpj_plugin('deftype', 'simple', fxname)
	fx_plugindata.fxdata_add(1, 0.5)
	fx_plugindata.fxvisual_add(visname, None)
	fx_plugindata.to_cvpj(cvpj_l, 'plugin-'+fxname)
	fxrack.add(cvpj_l, fx_num, 1.0, None, name="[S] "+visname, color=[0.4, 0.4, 0.4])
	fxslot.insert(cvpj_l, ['fxrack', fx_num], 'audio', 'plugin-'+fxname)
	fxrack.addsend(cvpj_l, fx_num, 0, 1, None)







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

______debugtxt______ = False

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

		elif midicmd[0] == 'track_name': 
			track_name = midicmd[1]
			#print('TRACK NAME, '+track_name)

		elif midicmd[0] == 'sequencer_specific':
			exdata = midi_exdata.decode_exdata(midicmd[1], True)

			if ______debugtxt______: print('SEQ', exdata)

			if exdata[0] == [5]:
				if exdata[1][0] == 15: #from Anvil Studio
					if exdata[1][1] == 52:
						anvilcolordata = exdata[1][2:6]
						red_p1 = anvilcolordata[3] & 0x3f 
						red_p2 = anvilcolordata[2] & 0xe0
						out_red = (red_p1 << 2) + (red_p2 >> 5)

						green_p1 = anvilcolordata[2] & 0x1f
						green_p2 = anvilcolordata[1] & 0xf0
						out_green = (green_p1 << 3) + (green_p2 >> 4)

						blue_p1 = anvilcolordata[1] & 0x0f
						blue_p2 = anvilcolordata[0] & 0x0f
						out_blue = (blue_p1 << 4) + blue_p2

						track_color = colors.rgb_int_to_rgb_float([out_red, out_green, out_blue])
					#else:
					#	print(exdata[1][1], exdata[1][2:])

			elif exdata[0] == [83]:
				if exdata[1][0:5] == b'ign\x01\xff': #from Signal MIDI Editor
					track_color = colors.rgb_int_to_rgb_float(exdata[1][5:8][::-1])
			elif exdata[0] == [80]:
				if exdata[1][0:5] == b'reS\x01\xff': #from Studio One
					track_color = colors.rgb_int_to_rgb_float(exdata[1][5:8][::-1])
			else:
				sequencer_specific.append(midicmd[1])

		elif midicmd[0] == 'copyright': track_copyright = midicmd[1]

		elif midicmd[0] == 'program_change': t_chan_current_inst[midicmd[1]][0] = midicmd[2]

		elif midicmd[0] == 'control_change': 
			if midicmd[2] == 0: t_chan_current_inst[midicmd[1]][1] = midicmd[3]
			elif midicmd[2] == 111: loop_data[0] = track_curpos/ppq_step
			elif midicmd[2] == 116: loop_data[0] = track_curpos/ppq_step
			elif midicmd[2] == 117: loop_data[1] = track_curpos/ppq_step
			else: add_chautopoint(track_curpos, midicmd[1], midicmd[2], midicmd[3])

		elif midicmd[0] == 'pitchwheel': add_chautopoint(track_curpos, midicmd[1], 'pitch', midicmd[2])

		elif midicmd[0] == 'tempo': auto_bpm[track_curpos] = midicmd[1]

		elif midicmd[0] == 'timesig': auto_timesig[track_curpos] = [midicmd[1], midicmd[2]]

		elif midicmd[0] == 'sysex': 
			#add_point(auto_sysex, track_curpos, midicmd[1])
			sysexdata = midi_exdata.decode(midicmd[1])

			if ______debugtxt______: print('SYSEX', sysexdata)

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

		elif midicmd[0] == 'marker': 
			add_point(auto_markers, track_curpos, midicmd[1])
			if midicmd[1] == 'loopStart': loop_data[0] = track_curpos/ppq_step
			if midicmd[1] == 'loopEnd': loop_data[1] = track_curpos/ppq_step

		elif midicmd[0] == 'text': 
			if ______debugtxt______: print('TEXT', midicmd[1])

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
		tracks_rm.track_create(cvpj_l, cvpj_trackid, 'instruments')
		tracks_rm.track_visual(cvpj_l, cvpj_trackid, name=trackname, color=track_color)
		tracks_rm.add_pl(cvpj_l, cvpj_trackid, 'notes', placementdata)
		tracknum += 1

	for instnum in range(len(used_insts)):
		used_inst = used_insts[instnum]
		if used_inst[3] == 0: instname, instcolor = dataset_midi.object_get_name_color('inst', str(used_inst[1]))
		else: instname, instcolor = 'Drums', [0.81, 0.80, 0.82]
		used_insts[instnum] += [instname,instcolor]

	for used_inst in used_insts:
		instid = '_'.join([str(used_inst[0]), str(used_inst[1]), str(used_inst[2]), str(used_inst[3])])

		instname = used_inst[4]
		instcolor = used_inst[5]

		if used_inst[3] == 0: inst_plugindata = plugins.cvpj_plugin('midi', used_inst[2], used_inst[1])
		else: inst_plugindata = plugins.cvpj_plugin('midi', 128, used_inst[1])
		inst_plugindata.to_cvpj(cvpj_l, instid)

		tracks_rm.inst_create(cvpj_l, instid)
		tracks_rm.inst_visual(cvpj_l, instid, name=instname, color=instcolor)
		tracks_rm.inst_fxrackchan_add(cvpj_l, instid, int(used_inst[0]+1))
		tracks_rm.inst_pluginid(cvpj_l, instid, instid)

	for fxnum in range(song_channels):
		s_fx_usedinstid = fx_usedinstid[fxnum]

		for i_fx_usedinstid in s_fx_usedinstid:
			_, groupname = dataset_isobjfound, dataset_data = dataset_midi.object_var_get('group', 'inst', str(i_fx_usedinstid[1]))
			i_fx_usedinstid.append(groupname)

		fx_name = None
		fx_color = None

		name_usable = []
		color_usable = []

		usedinlen = len(s_fx_usedinstid)
		if usedinlen == 1:
			usedinstid = s_fx_usedinstid[0]

			iftrackname = (global_miditracks[usedinstid[0]][1] not in [None, '']) and tracknum != 1
			iftrackcolor = global_miditracks[usedinstid[0]][4]

			if iftrackname: name_usable.append(global_miditracks[usedinstid[0]][1])
			color_usable.append(global_miditracks[usedinstid[0]][4])

			if not usedinstid[3]: 
				name, color = dataset_midi.object_get_name_color('inst', str(usedinstid[1]))
				name_usable.append(name)
				color_usable.append(color)
			else:
				name_usable.append('Drums')
				color_usable.append([0.81, 0.80, 0.82])

			fx_name, fx_color = dataset_midi.object_get_name_color('inst', str(usedinstid[1]))
			name_usable.append(fx_name)
			color_usable.append(fx_color)

		elif usedinlen > 1:
			ifsametrackid = data_values.ifallsame([s_fx_usedinstid[x][0] for x in range(usedinlen)])
			ifsameinstid = data_values.ifallsame([s_fx_usedinstid[x][1] for x in range(usedinlen)])
			ifsamegroups = data_values.ifallsame([s_fx_usedinstid[x][4] for x in range(usedinlen)])
			ifsamealldrums = bool(data_values.ifallsame([s_fx_usedinstid[x][3] for x in range(usedinlen)]) and s_fx_usedinstid[0][3])

			if ifsametrackid:
				if global_miditracks[s_fx_usedinstid[0][0]][1] != '': name_usable.append(global_miditracks[s_fx_usedinstid[0][0]][1])
				color_usable.append(global_miditracks[s_fx_usedinstid[0][0]][4])

			if ifsameinstid and not ifsamealldrums:
				name, color = dataset_midi.object_get_name_color('inst', str(s_fx_usedinstid[0][1]))
				name_usable.append(name)
				color_usable.append(color)

			if ifsamegroups: 
				name, color = dataset_midi.groups_get_name_color('inst', s_fx_usedinstid[0][4])
				name_usable.append(name)
				color_usable.append(color)
			else:
				usedgroups = list(set([s_fx_usedinstid[x][4] for x in range(usedinlen)]))
				usedgroups = [dataset_midi.groups_get_name_color('inst', x)[0] for x in usedgroups]
				name_usable.append(' + '.join(usedgroups))

			if ifsamealldrums: 
				name_usable.append('Drums')
				color_usable.append([0.81, 0.80, 0.82])

			color_usable.append([0.4, 0.4, 0.4])

		if ______debugtxt______: print(usedinlen, name_usable, color_usable)

		out_name = data_values.list_usefirst(name_usable)
		out_color = data_values.list_usefirst(color_usable)

		if out_name != None: fxchannames[fxnum] = out_name
		if out_color != None: fxchancolors[fxnum] = out_color

	fxrack.add(cvpj_l, 0, 1.0, None, name="Master", color=[0.3, 0.3, 0.3])

	usedeffects = [False,False]

	for midi_channum in range(song_channels):
		s_chanauto = automation_channel[midi_channum]
		fxrack_chan = str(midi_channum+1)
		fxrack.add(cvpj_l, fxrack_chan, None, None, name=fxchannames[midi_channum], color=fxchancolors[midi_channum])

		for ccnum, name, defval, valdiv, valadd in [
			[  1 ,'modulation',    1,  127,   0],
			[  7 ,'vol',           1,  127,   0],
			[  10,'pan',           0,  64,   -1],
			[  11,'expression',    1,  127,   0],
			['pitch','pitch',      0,  1,     0],
		]:
			if ccnum in s_chanauto: 
				out_param = auto_nopl.paramauto(
					['fxmixer', fxrack_chan, name], 'float', s_chanauto[ccnum], ppq_step, firstchanusepos[midi_channum], defval, valdiv, valadd)
				fxrack.param_add(cvpj_l, midi_channum+1, name, out_param, 'float')

		for ccnum, fx2, fx1, fxname in [[91,0,0,'reverb'],[93,0,1,'chorus'],[92,1,0,'tremolo'],[95,1,1,'phaser']]:
			if ccnum in s_chanauto:
				sendname = str(midi_channum)+fxname
				usedeffects[fx2] = True
				sendtofx = song_channels+1+fx1+(fx2*2)
				out_param = auto_nopl.paramauto(['send', sendname, 'amount'], 'float', s_chanauto[ccnum], ppq_step, firstchanusepos[midi_channum], 0, 127, 0)
				fxrack.addsend(cvpj_l, midi_channum+1, 0, 1, None)
				fxrack.addsend(cvpj_l, midi_channum+1, sendtofx, out_param, sendname)

	if usedeffects[0] == True:
		add_fx(cvpj_l, song_channels+1, 'reverb', 'Reverb', 0.5)
		add_fx(cvpj_l, song_channels+2, 'chorus', 'Chorus', 1)

	if usedeffects[1] == True:
		add_fx(cvpj_l, song_channels+3, 'tremelo', 'Tremelo', 1)
		add_fx(cvpj_l, song_channels+4, 'phaser', 'Phaser', 1)

	veryfirstnotepos = getbeforenoteall(firstchanusepos)

	#tempo
	out_param = auto_nopl.paramauto(['main', 'bpm'], 'float', auto_bpm, ppq_step, veryfirstnotepos, 120, 1, 0)
	params.add(cvpj_l, [], 'bpm', out_param, 'float')

	#volume
	if 'volume' in auto_master:
		out_param = auto_nopl.paramauto(['fxmixer', '0', 'vol'], 'float', auto_master['volume'], ppq_step, veryfirstnotepos, 127, 1, 0)
		fxrack.param_add(cvpj_l, 0, 'vol', out_param, 'float')

	#timesig
	for timesigpoint in auto_timesig:
		timesig = auto_timesig[timesigpoint]
		timesigpos = (timesigpoint/ppq_step)
		if timesigpoint == 0: cvpj_l['timesig'] = timesig
		song.add_timemarker_timesig(cvpj_l, str(timesig[0])+'/'+str(timesig[1]), (timesigpoint/ppq_step), timesig[0], timesig[1])

	#timesig
	if loop_data[1] != None: song.add_timemarker_looparea(cvpj_l, 'Loop', loop_data[0], loop_data[1])
	elif loop_data[0] != None: song.add_timemarker_loop(cvpj_l, loop_data[0], 'Loop')
	
	auto_nopl.to_cvpj(cvpj_l)

	return used_insts