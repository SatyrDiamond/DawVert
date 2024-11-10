# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np

from functions import data_values
from functions import value_midi

from objects import datastore
from objects.data_bytes import structalloc
from objects.convproj import autoticks
from objects.convproj import project as convproj
from objects.songinput._midi_multi import mainauto
from objects.songinput._midi_multi import chanauto
from objects.songinput._midi_multi import instauto
from objects.songinput._midi_multi import instruments
from objects.songinput._midi_multi import track

class midi_song:
	def __init__(self, numchannels, ppq, tempo, timesig):
		self.miditracks = []

		self.song_channels = numchannels
		self.ppq = ppq
		self.pitch_gm = False

		self.fx_offset = 0

		self.auto_chan = chanauto.midi_cc_auto_multi(numchannels)
		self.auto_timesig = mainauto.timesig_premake.create()
		self.auto_master_vol = mainauto.otherauto_premake.create()
		self.auto_bpm = mainauto.bpm_premake.create()
		self.auto_pitch = chanauto.midi_pitch_auto_multi(numchannels)

		self.auto_insts = instauto.midi_instauto_multi(numchannels)
		self.copyright = None
		self.lyrics = {}
		self.device = 'gm'

		self.texts = datastore.auto_multidata()
		self.marker = datastore.auto_multidata()
		self.auto_sysex = datastore.auto_multidata()

		self.loop_start = None
		self.loop_end = None
		self.start_pos = None
		self.start_pos_est = True

		self.start_pitch = [0 for _ in range(self.song_channels)]

		self.instruments = instruments.midi_instruments()

		self.nocolor = False

	def add_port(self, numchannels):
		self.song_channels += numchannels
		self.start_pitch += [0 for _ in range(numchannels)]

	def create_track(self, numevents):
		track_obj = track.midi_track(numevents, self)
		self.miditracks.append(track_obj)
		return track_obj

	def postprocess(self):
		self.auto_chan.postprocess()

		self.auto_timesig.sort(['pos'])
		self.auto_bpm.sort(['pos'])

		self.auto_sysex.sort()

		self.g_used_fx = []
		self.used_fx = [[] for x in range(self.song_channels)]

		for x in self.miditracks:
			x.notes.clean()

		for x in self.auto_sysex:
			p_pos, p_sysexs = x
			for p_sysex in p_sysexs:
				if p_sysex.model_name == 'sc88':
					if p_sysex.category == 'patch_a' and p_sysex.group == 'block' and p_sysex.param == 'use_rhythm': 
						self.auto_insts.addp_drum(p_pos, p_sysex.num if p_sysex.num!=0 else 9, int(p_sysex.value!=0))

				if p_sysex.vendor.id == 127:
					if p_sysex.category == 'device' and p_sysex.param == 'master_volume': 
						mastervol_auto = self.auto_master_vol
						mastervol_auto.add()
						mastervol_auto['pos'] = p_pos
						mastervol_auto['value'] = p_sysex.value

		self.auto_master_vol.sort(['pos'])
		self.auto_insts.postprocess()

		s_prepos = np.rot90(np.array([[t.startpos_chan(c) for c in range(self.song_channels)] for t in self.miditracks]))
		self.startpos_chan = [np.min(x) for x in s_prepos][::-1]
		self.auto_chan.calc_startpos(self.startpos_chan)

		e_prepos = np.rot90(np.array([[t.endpos_chan(c) for c in range(self.song_channels)] for t in self.miditracks]))
		self.endpos_chan = [np.max(x) for x in e_prepos][::-1]

		for num, track in enumerate(self.miditracks):
			track.notes.postprocess()
			for channel in range(self.song_channels): self.auto_insts.applyinst_chan(track.notes.data, channel)
			track.used_insts = track.notes.get_used_insts()
			for ui in track.used_insts: self.instruments.add_instrument(num, ui['chan'], ui['i_bank'], ui['i_bank_hi'], ui['i_inst'], ui['i_drum'])

		self.auto_pitch.postprocess()
		self.auto_pitch.from_sysex(self.auto_sysex)
		chan_pitch = self.auto_pitch.get_chan_pitch()
		for chan in range(self.song_channels):
			if chan_pitch != None:
				s_pitch = chan_pitch[chan][['pos', 'value']]
				app = np.where(s_pitch['pos']<=self.startpos_chan[chan])
				if len(app[0])!=0: self.start_pitch[chan] = s_pitch['value'][app][-1]

	def get_insts_custom(self):
		for inst in self.instruments.midi_instruments.data:
			if inst['is_custom'] and inst['used']:
				instid = '_'.join([
					str(inst['track']), 
					str(inst['chan']), 
					str(inst['inst']), 
					str(inst['bank']), 
					str(inst['bank_hi']), 
					str(inst['drum'])])
				yield inst, instid

	def to_cvpj(self, convproj_obj):
		convproj_obj.set_timings(self.ppq, True)
		self.auto_timesig.clean()
		self.auto_bpm.clean()

		self.instruments.to_cvpj(convproj_obj, self.device, self.fx_offset)

		if len(self.miditracks)>1:

			single_trackinst = []
			for tracknum in range(len(self.miditracks)): single_trackinst.append(self.instruments.get_single_trackinst(tracknum))

			for tracknum, track in enumerate(self.miditracks):
				cvpj_trackid = 'track_'+str(tracknum)

				track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 0, False)
				track_obj.visual.name = track.track_name
				if not self.nocolor: track_obj.visual.color.set_int(track.track_color)

				s_tin = single_trackinst[tracknum]
				if s_tin != None:
					if not s_tin[3]:
						track_obj.visual.from_dset('midi', self.device+'_inst', '_'.join([s_tin[0],s_tin[1],s_tin[2]]), False)

				track.notes.to_cvpj(track_obj.placements.notelist, tracknum, -1)

			if self.nocolor: track_obj.visual.color.remove()

		if len(self.miditracks)==1:
			track = self.miditracks[0]
			convproj_obj.metadata.name = track.track_name
			usedchans = track.notes.get_used_chans()

			for usedchan in usedchans:
				cvpj_trackid = 'chan_'+str(usedchan)
				chantxt = 'Chan #'+str(usedchan+1)

				track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 0, False)

				track.notes.to_cvpj(track_obj.placements.notelist, 0, usedchan)

				instlist = self.instruments.find_idx_chan(usedchan)

				if len(instlist)==1:
					i = self.instruments.get_idx(instlist[0])

					if not i['drum']: 
						track_obj.visual.from_dset_midi(i['bank_hi'], i['bank'], i['inst'], i['drum'], self.device, False)
						if track_obj.visual.name: track_obj.visual.name += ' ('+str(chantxt)+')'
						else: track_obj.visual.name = chantxt
					else: 
						track_obj.visual.name = 'Drums'
						if not self.nocolor: track_obj.visual.color.set_float([0.81, 0.80, 0.82])

				else:
					track_obj.visual.name = chantxt

				if self.nocolor: track_obj.visual.color.remove()

		for ts in self.auto_timesig:
			convproj_obj.timesig_auto.add_point(ts['pos'], [ts['numerator'], ts['denominator']**2])

		for point in self.auto_master_vol:
			convproj_obj.automation.add_autotick(['main', 'vol'], 'float', point['pos'], point['value']/127)

		for bpm in self.auto_bpm:
			convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', bpm['pos'], bpm['tempo'])

		fxchannel_obj = convproj_obj.fx__chan__add(0)
		fxchannel_obj.visual.name = "Master"
		fxchannel_obj.visual.color.set_float([0.3, 0.3, 0.3])

		if self.nocolor: fxchannel_obj.visual.color.remove()

		if self.auto_chan.fx_used['reverb']:
			reverb_fxchannel_obj = convproj_obj.fx__chan__add(self.song_channels+1+self.fx_offset)
			reverb_fxchannel_obj.visual.name = 'Reverb'
			reverb_fxchannel_obj.visual_ui.other['docked'] = 1
			plugin_obj, reverb_pluginid = convproj_obj.plugin__add__genid('simple', 'reverb', None)
			plugin_obj.visual.name = 'Reverb'
			plugin_obj.fxdata_add(1, 0.5)
			reverb_fxchannel_obj.fxslots_audio.append(reverb_pluginid)

		for fx_num in range(self.fx_offset): fxchannel_obj = convproj_obj.fx__chan__add(fx_num+1)

		for ch_num in range(self.song_channels):
			fx_num = ch_num+1+self.fx_offset
			fxchannel_obj = convproj_obj.fx__chan__add(ch_num+1+self.fx_offset)
			fxchannel_obj.sends.add(0, None, 1)

			used_fx = self.auto_chan.fx_used_chans[ch_num]
			start_ctrls = self.auto_chan.start_vals[ch_num]
			start_pitch = self.start_pitch[ch_num]

			fxchannel_obj.params.add('pitch', start_pitch/8192, 'float')
			if start_ctrls[7] != -1: fxchannel_obj.params.add('vol', start_ctrls[7]/127, 'float')
			if start_ctrls[10] != -1: fxchannel_obj.params.add('pan', (start_ctrls[10]/127)-0.5, 'float')

			if used_fx['reverb']:
				reverbsend = start_ctrls[91]/127 if start_ctrls[91] != -1 else 0
				reverb_pluginid = str(fx_num+1)+'_reverb'
				fxchannel_obj.sends.add(self.song_channels+1, reverb_pluginid, reverbsend)

			if used_fx['chorus']:
				chorus_size = start_ctrls[93]/127 if 93 in start_ctrls else 0
				chorus_pluginid = str(fx_num+1)+'_chorus'
				chorus_plugin_obj = convproj_obj.plugin__add(chorus_pluginid, 'simple', 'chorus', None)
				chorus_plugin_obj.visual.name = 'Chorus'
				chorus_plugin_obj.params.add('amount', chorus_size, 'float')
				fxchannel_obj.fxslots_audio.append(chorus_pluginid)

			inst_chan = self.instruments.find_idx_chan(ch_num)
			if len(inst_chan):
				befsame_chan = self.instruments.get_idx(inst_chan)

				same_track = befsame_chan['track'][0] if np.all(befsame_chan['track']) else None
				if same_track != None:
					track = self.miditracks[same_track]
					fxchannel_obj.visual.add_opt(track.track_name if track.track_name else None, track.track_color)

				same_drum = befsame_chan['drum'][0] if np.all(befsame_chan['drum']) else None
				same_inst = befsame_chan['inst'][0] if np.all(befsame_chan['inst']) else None

				if same_drum == 1: fxchannel_obj.visual.add_opt('Drums', [0.81, 0.80, 0.82])
				elif same_inst != None: 
					b_instchan = befsame_chan[np.where(befsame_chan['inst']==same_inst)][0]
					fxchannel_obj.visual.from_dset('midi', self.device+'_inst', '0_0_'+str(same_inst), False)

			fxchannel_obj.visual.add_opt('Chan #'+str(ch_num+1), [0.1, 0.1, 0.1])

		for ch_num in range(self.song_channels):
			pitch_data = self.auto_pitch.filter_chan(ch_num)

			prevval = 0
			for pitchpoint in pitch_data:
				value = float(pitchpoint['value'])/(1365 if pitchpoint['mode'] else 8192)
				if prevval != value: convproj_obj.automation.add_autotick(['fxmixer', str(ch_num+1), 'pitch'], 'float', pitchpoint['pos'], value)
				prevval = value

		for channum, ctrlnum, autodata in self.auto_chan.iter():
			midiautoinfo = value_midi.get_cc_info(ctrlnum)
			autoloc = midiautoinfo.get_autoloc(channum, self.fx_offset)
			if midiautoinfo.name and len( np.where(autodata['pos']>=self.startpos_chan[channum])[0] ):
				prevval = 0
				for posval in autodata:
					value = ((posval['value']/127)+midiautoinfo.math_add)*midiautoinfo.math_mul
					if value != prevval: convproj_obj.automation.add_autotick(autoloc, 'float', posval['pos'], value)
					prevval = value

		if self.loop_start != None and self.loop_end != None: 
			convproj_obj.loop_active = True
			convproj_obj.loop_start = self.loop_start
			convproj_obj.loop_end = self.loop_end
		elif self.loop_start != None and self.loop_end == None: 
			convproj_obj.loop_active = True
			convproj_obj.loop_start = self.loop_start
			convproj_obj.loop_end = np.max(self.endpos_chan)

		if self.start_pos_est:
			self.start_pos = min(self.startpos_chan)

		if len(self.auto_timesig.data):
			ts_d = self.auto_timesig.data
			timesigm = ts_d[np.where(ts_d['pos']<=self.start_pos)]

			firstts = timesigm[-1]
			convproj_obj.timesig = [int(firstts['numerator']), int(firstts['denominator'])**2]

		if len(self.auto_bpm.data)>0:
			tb_d = self.auto_bpm.data
			tempom = tb_d[np.where(tb_d['pos']<=self.start_pos)]
			if len(tempom): convproj_obj.params.add('bpm', tempom[-1]['tempo'], 'float')
			else: convproj_obj.params.add('bpm', tb_d[0]['tempo'], 'float')
		
		convproj_obj.start_pos = self.start_pos
