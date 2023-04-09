# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import mido
from functions import notelist_data
from functions import xtramath

def add_cmd(i_list, i_pos, i_cmd):
	if i_pos not in i_list: i_list[i_pos] = []
	i_list[i_pos].append(i_cmd)

def notelist2midi(notelist, midi_file_path):
	midiobj = mido.MidiFile()
	miditrack = mido.MidiTrack()
	i_list = {}

	notelist = notelist_data.sort(notelist)

	for cvpj_tr_pl_n in notelist:
		cvmi_n_pos = int(cvpj_tr_pl_n['position']*4)*30
		cvmi_n_dur = int(cvpj_tr_pl_n['duration']*4)*30
		cvmi_n_key = int(cvpj_tr_pl_n['key'])+60
		cvmi_n_vol = 127
		if 'vol' in cvpj_tr_pl_n: cvmi_n_vol = xtramath.clamp(int(cvpj_tr_pl_n['vol']*127), 0, 127)
		add_cmd(i_list, cvmi_n_pos, ['note_on', cvmi_n_key, cvmi_n_vol])
		add_cmd(i_list, cvmi_n_pos+cvmi_n_dur, ['note_off', cvmi_n_key])

	i_list = dict(sorted(i_list.items(), key=lambda item: item[0]))

	prevpos = 0
	for i_list_e in i_list:
		for midi_notedata in i_list[i_list_e]:
			if midi_notedata[0] == 'note_on': miditrack.append(mido.Message('note_on', channel=0, note=midi_notedata[1], velocity=midi_notedata[2], time=i_list_e-prevpos))
			if midi_notedata[0] == 'note_off': miditrack.append(mido.Message('note_off', channel=0, note=midi_notedata[1], time=i_list_e-prevpos))
			prevpos = i_list_e

	midiobj.tracks.append(miditrack)
	midiobj.save(midi_file_path)