# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def get_datadef(pluginname):
	out = []

	if pluginname == '3x osc':
		out = [
			["i",False,"version","Version"],
			["i",True,"osc1_pan","Osc 1 Pan"],
			["i",True,"osc1_shape","Osc 1 Shape"],
			["i",True,"osc1_coarse","Osc 1 Coarse"],
			["i",True,"osc1_fine","Osc 1 Fine"],
			["i",True,"osc1_ofs","Osc 1 Offset"],
			["i",True,"osc1_detune","Osc 1 Detune"],
			["i",True,"osc1_mixlevel","Osc 1 Mix Level"],
			["i",True,"osc2_pan","Osc 2 Pan"],
			["i",True,"osc2_shape","Osc 2 Shape"],
			["i",True,"osc2_coarse","Osc 2 Coarse"],
			["i",True,"osc2_fine","Osc 2 Fine"],
			["i",True,"osc2_ofs","Osc 2 Offset"],
			["i",True,"osc2_detune","Osc 2 Detune"],
			["i",True,"osc2_mixlevel","Osc 2 Mix Level"],
			["i",True,"osc3_pan","Osc 3 Pan"],
			["i",True,"osc3_shape","Osc 3 Shape"],
			["i",True,"osc3_coarse","Osc 3 Coarse"],
			["i",True,"osc3_fine","Osc 3 Fine"],
			["i",True,"osc3_ofs","Osc 3 Offset"],
			["i",True,"osc3_detune","Osc 3 Detune"],
			["i",True,"phase_rand","Phase Rand"],
			["b",True,"osc1_invert","Osc 1 Invert"],
			["b",True,"osc2_invert","Osc 2 Invert"],
			["b",True,"osc3_invert","Osc 3 Invert"],
			["b",True,"osc3_am","Osc 3 AM"]
		]

	elif pluginname == 'fruit kick':
		out = [
			["i",False,"version","Version"],
			["i",True,"max_freq","Max Freq"],
			["i",True,"min_freq","Min Freq"],
			["i",True,"decay_freq","Decay Freq"],
			["i",True,"decay_vol","Decay Vol"],
			["i",True,"osc_click","Osc Click"],
			["i",True,"osc_dist","Osc Dist"]
		]

	elif pluginname == 'fruity dx10':
		out = [
			["i",False,"version","Version"],
			["i",True,"amp_att","Attack"],
			["i",True,"amp_dec","Decay"],
			["i",True,"amp_rel","Release"],
			["i",True,"mod_course","Coarse"],
			["i",True,"mod_fine","Fine"],
			["i",True,"mod_init","Mod Init"],
			["i",True,"mod_time","Mod Dec"],
			["i",True,"mod_sus","Mod Sus"],
			["i",True,"mod_rel","Mod Rel"],
			["i",True,"mod_velsen","Vel Sen"],
			["i",True,"vibrato","Vibrato"],
			["i",True,"waveform","Waveform"],
			["i",True,"mod_thru","Mod Thru"],
			["i",True,"lforate","LFO Rate"],
			["i",True,"mod2_course","Mod 2 Coarse"],
			["i",True,"mod2_fine","Mod 2 Fine"],
			["i",True,"mod2_init","Mod 2 Init"],
			["i",True,"mod2_time","Mod 2 Dec"],
			["i",True,"mod2_sus","Mod 2 Sus"],
			["i",True,"mod2_rel","Mod 2 Rel"],
			["i",True,"mod2_velsen","Mod 2 Vel Sen"],
			["I",True,"octave","Octave"]
		]

	elif pluginname == 'plucked!':
		out = [
			["i",True,"decay","Decay"],
			["i",True,"color","Color"],
			["i",True,"norm_decay","Normalize Decay"],
			["i",True,"release","Short Release"],
			["i",True,"wide","Widen"],
		]

	elif pluginname in ['wasp', 'wasp xt']:
		out = [
			["i",False,"version","Version"],

			["i",True,"1_shape",""],
			["i",True,"1_crs",""],
			["i",True,"1_fine",""],
			["i",True,"2_shape",""],
			["i",True,"2_crs",""],
			["i",True,"2_fine",""],

			["i",True,"3_shape",""],
			["i",True,"3_amt",""],
			["i",True,"12_fade",""],
			["i",True,"pw",""],
			["i",True,"fm",""],
			["i",True,"ringmod",""],

			["i",True,"amp_A",""],
			["i",True,"amp_S",""],
			["i",True,"amp_D",""],
			["i",True,"amp_R",""],
			["i",True,"fil_A",""],
			["i",True,"fil_S",""],
			["i",True,"fil_D",""],
			["i",True,"fil_R",""],

			["i",True,"fil_kbtrack",""],
			["i",True,"fil_qtype",""],
			["i",True,"fil_cut",""],
			["i",True,"fil_res",""],
			["i",True,"fil_env",""],

			["i",True,"lfo1_shape",""],
			["i",True,"lfo1_target",""],
			["i",True,"lfo1_amt",""],
			["i",True,"lfo1_spd",""],
			["i",True,"lfo1_sync",""],
			["i",True,"lfo1_reset",""],

			["i",True,"lfo2_shape",""],
			["i",True,"lfo2_target",""],
			["i",True,"lfo2_amt",""],
			["i",True,"lfo2_spd",""],
			["i",True,"lfo2_sync",""],
			["i",True,"lfo2_reset",""],

			["i",True,"dist_on",""],
			["i",True,"dist_drv",""],
			["i",True,"dist_tone",""],
			["i",True,"dualvoice",""],
		]

		if pluginname == 'wasp xt':
			out += [
			["i",True,"amp",""],
			["i",True,"analog",""],
			["i",True,"me_atk",""],
			["i",True,"me_dec",""],

			["i",True,"me_amt",""],
			["i",True,"me_1lvl",""],
			["i",True,"me_2pitch",""],
			["i",True,"me_1ami",""],

			["i",True,"me_pw",""],
			["i",True,"vol",""],
			["i",True,"lfo1_delay",""],
			["i",True,"lfo2_delay",""],

			["i",True,"me_filter",""],
			["i",True,"wnoise",""],

		]

	elif pluginname == 'simsynth':
		out = [
			["d",True,"osc1_pw",""],
			["d",True,"osc1_crs",""],
			["d",True,"osc1_fine",""],
			["d",True,"osc1_lvl",""],
			["d",True,"osc1_lfo",""],
			["d",True,"osc1_env",""],
			["d",True,"osc1_shape",""],

			["d",True,"osc2_pw",""],
			["d",True,"osc2_crs",""],
			["d",True,"osc2_fine",""],
			["d",True,"osc2_lvl",""],
			["d",True,"osc2_lfo",""],
			["d",True,"osc2_env",""],
			["d",True,"osc2_shape",""],

			["d",True,"osc3_pw",""],
			["d",True,"osc3_crs",""],
			["d",True,"osc3_fine",""],
			["d",True,"osc3_lvl",""],
			["d",True,"osc3_lfo",""],
			["d",True,"osc3_env",""],
			["d",True,"osc3_shape",""],

			["d",True,"lfo_del",""],
			["d",True,"lfo_rate",""],
			["d",True,"unk_1",""],
			["d",True,"lfo_shape",""],

			["d",True,"unk_2",""],
			["d",True,"svf_cut",""],
			["d",True,"svf_emph",""],
			["d",True,"svf_env",""],
			["d",True,"svf_lfo",""],
			["d",True,"svf_kb",""],

			["d",True,"unk_3",""],
			["d",True,"svf_high",""],
			["d",True,"svf_band",""],

			["d",True,"unk_4",""],
			["d",True,"amp_att",""],
			["d",True,"amp_dec",""],
			["d",True,"amp_sus",""],
			["d",True,"amp_rel",""],
			["d",True,"amp_lvl",""],

			["d",True,"unk_5",""],
			["d",True,"svf_att",""],
			["d",True,"svf_dec",""],
			["d",True,"svf_sus",""],
			["d",True,"svf_rel",""],

			["x",64],
			["x",12],

			["i",True,"osc1_on",""],
			["i",True,"osc1_o1",""],
			["i",True,"osc1_o2",""],
			["i",True,"osc1_warm",""],

			["i",True,"osc2_on",""],
			["i",True,"osc2_o1",""],
			["i",True,"osc2_o2",""],
			["i",True,"osc2_warm",""],

			["i",True,"osc3_on",""],
			["i",True,"osc3_o1",""],
			["i",True,"osc3_o2",""],
			["i",True,"osc3_warm",""],

			["i",True,"osc3_on",""],
			["i",True,"osc3_o1",""],
			["i",True,"osc3_o2",""],
			["i",True,"osc3_warm",""],

			["i",True,"lfo_on",""],
			["i",True,"lfo_retrigger",""],
			["i",True,"svf_on",""],
			["i",True,"unk_6",""],

			["i",True,"lfo_trackamp",""],
			["i",True,"unk_7",""],
			["i",True,"chorus_on",""],
			["i",True,"unk_8",""],
		]

	elif pluginname == 'effector':
		out = [
			["i",False,"version","Version"],

			["f",True,"effect","Effect"],
			["f",True,"bypass","Bypass"],
			["f",True,"wet","Wet"],
			["f",True,"x_param","X Param"],
			["f",True,"y_param","Y Param"],
			["f",True,"mod_rate","Mod Rate"],
			["f",True,"tempo","Tempo Reduce"],
			["f",True,"x_mod","X Mod"],
			["f",True,"y_mod","Y Mod"],
			["f",True,"mod_shape","Mod Shape"],
			["f",True,"input_level","Input Level"],
			["f",True,"output_gain","Output Gain"],
		]

	elif pluginname == 'frequency shifter':
		out = [
			["i",False,"version","Version"],

			["i",True,"mix","Mix"],
			["i",True,"type","Type"],
			["i",True,"frequency","Frequency"],
			["i",True,"lr_phase","L/R Phase"],
			["i",True,"shape_left","Shape Left"],
			["i",True,"shape_right","Shape Right"],
			["i",True,"feedback","Feedback"],
			["i",True,"stereo","Stereo"],
			["i",True,"freqtype","Freq Type"],
			["i",True,"start_phase","Start Phase"],
			["i",True,"mixer_track","Mixer Track"],
		]

	elif pluginname == 'fruity 7 band eq':
		out = [
			["i",True,"band_1",""],
			["i",True,"band_2",""],
			["i",True,"band_3",""],
			["i",True,"band_4",""],
			["i",True,"band_5",""],
			["i",True,"band_6",""],
			["i",True,"band_7",""],
		]

	elif pluginname == 'fruity balance':
		out = [
			["i",True,"pan",""],
			["i",True,"vol",""],
		]

	elif pluginname == 'fruity bass boost':
		out = [
			["i",False,"version","Version"],

			["i",True,"freq",""],
			["i",True,"amount",""],
		]

	elif pluginname == 'fruity big clock':
		out = [
			["b",False,"version","Version"],
			
			["b",True,"beats",""],
			["b",True,"color",""],
		]

	elif pluginname == 'fruity blood overdrive':
		out = [
			["I",False,"version","Version"],

			["I",True,"preband","PreBand"],
			["I",True,"color","Color"],
			["I",True,"preamp","PreAmp"],
			["I",True,"x100","x 100"],
			["I",True,"postfilter","PostFilter"],
			["I",True,"postgain","PostGain"],

			["I",False,"unknown_1",""],
			["I",False,"unknown_2",""],
		]

	elif pluginname == 'fruity center':
		out = [
			["I",False,"version","Version"],
			["I",True,"on",""],
		]

	elif pluginname == 'fruity chorus':
		out = [
			["I",False,"version","Version"],
			
			["I",True,"delay","Delay"],
			["I",True,"depth","Depth"],
			["I",True,"stereo","Stereo"],
			["I",True,"lfo1_freq","LFO 1 Freq"],
			["I",True,"lfo2_freq","LFO 2 Freq"],
			["I",True,"lfo3_freq","LFO 3 Freq"],
			["I",True,"lfo1_wave","LFO 1 wave"],
			["I",True,"lfo2_wave","LFO 2 wave"],
			["I",True,"lfo3_wave","LFO 3 wave"],
			["I",True,"crosstype","Cross Type"],
			["I",True,"crosscutoff","Cross Cutoff"],
			["I",True,"wetonly","Wet Only"],
		]

	elif pluginname == 'fruity delay':
		out = [
			["i",False,"version","Version"],
			
			["i",True,"input","Input"],
			["i",True,"fb","Feedback"],
			["i",True,"cutoff","Cutoff"],
			["i",True,"tempo","Tempo"],
			["i",True,"steps","Steps"],
			["i",True,"mode","Mode"],
		]

	elif pluginname == 'fruity delay 2':
		out = [
			["i",True,"input_pan","Input Pan"],
			["i",True,"input_vol","Input Vol"],
			["i",True,"dry","Dry"],
			["i",True,"fb_vol","Feedback Vol"],
			["i",True,"time","Time"],
			["i",True,"time_stereo_offset","Stereo Offset"],
			["i",True,"fb_mode","Feedback Mode"],
			["i",True,"fb_cut","Feedback Cut"],
		]

	elif pluginname == 'fruity delay 3':
		out = [
			["i",False,"version","Version"],
			["i",True,"wet",""],
			["i",True,"delay_type",""],
			["i",True,"tempo_sync",""],
			["i",True,"keep_pitch",""],
			["i",True,"delay_time",""],
			["i",True,"offset",""],
			["i",True,"smoothing",""],
			["i",True,"stereo",""],
			["i",True,"mod_rate",""],
			["i",True,"mod_time",""],
			["i",True,"mod_cutoff",""],
			["i",True,"diffusion_level",""],
			["i",True,"diffusion_spread",""],
			["i",True,"feedbackdist_type",""],
			["i",True,"feedback_level",""],
			["i",True,"unknown_1",""],
			["i",True,"feedback_cutoff",""],
			["i",True,"feedback_reso",""],
			["i",True,"feedbackdist_level",""],
			["i",True,"feedbackdist_knee",""],
			["i",True,"feedbackdist_symmetry",""],
			["i",True,"feedback_sample_rate",""],
			["i",True,"feedback_bits",""],
			["i",True,"wet",""],
			["i",True,"tone",""],
			["i",True,"dry",""],
		]

	elif pluginname == 'fruity fast dist':
		out = [
			["i",True,"pre","Pre Amp"],
			["i",True,"threshold","Threshold"],
			["i",True,"type","Type"],
			["i",True,"mix","Mix"],
			["i",True,"post","Post"],
		]

	elif pluginname == 'fruity fast lp':
		out = [
			["I",True,"cutoff","Cutoff"],
			["I",True,"reso","Reso"],
			["I",False,"unknown_1",""],
		]

	elif pluginname == 'fruity filter':
		out = [
			["I",True,"cutoff","Cutoff"],
			["I",True,"reso","Reso"],
			["I",True,"lowpass","Low Pass"],
			["I",True,"bandpass","Band Pass"],
			["I",True,"hipass","High Pass"],
			["I",True,"x2","x2"],
			["b",False,"center","Center"],
		]

	elif pluginname == 'fruity flanger':
		out = [
			["i",False,"version","Version"],
			["I",True,"delay",""],
			["I",True,"depth",""],
			["I",True,"rate",""],
			["I",True,"phase",""],
			["I",True,"damp",""],
			["I",True,"shape",""],
			["I",True,"feed",""],
			["I",True,"inv_feedback",""],
			["I",True,"inv_wet",""],
			["I",True,"dry",""],
			["I",True,"wet",""],
			["I",True,"cross",""],
		]

	elif pluginname == 'fruity flangus':
		out = [
			["i",True,"ord",""],
			["i",True,"depth",""],
			["i",True,"speed",""],
			["i",True,"delay",""],
			["i",True,"spread",""],
			["i",True,"cross",""],
			["i",True,"dry",""],
			["i",True,"wet",""],
		]

	elif pluginname == 'fruity free filter':
		out = [
			["I",True,"type","Type"],
			["I",True,"freq","Frequency"],
			["I",True,"q","Q"],
			["I",True,"gain","Gain"],
			["I",True,"center","Center"],
		]

	elif pluginname == 'fruity limiter':
		out = [
			["i",True,"gain","Gain"],
			["i",True,"sat","Soft Saturation Threshold"],

			["i",True,"limiter_ceil","Limiter Ceil"],
			["i",True,"limiter_att","Limiter Attack"],
			["i",True,"limiter_att_curve","Limiter Attack Curve"],
			["i",True,"limiter_rel","Limiter Release"],
			["i",True,"limiter_rel_curve","Limiter Release Curve"],
			["i",True,"limiter_sus","Limiter Sustain"],

			["i",True,"comp_thres","Comp Threshold"],
			["i",True,"comp_knee","Comp Knee"],
			["i",True,"comp_ratio","Comp Ratio"],
			["i",True,"comp_att","Comp Attack"],
			["i",True,"comp_rel","Comp Release"],
			["i",True,"comp_att_curve","Comp Attack Curve"],
			["i",True,"comp_sus","Comp Sustain"],

			["i",True,"noise_gain","Noise Gain"],
			["i",True,"noise_thres","Noise Threshold"],
			["i",True,"noise_rel","Noise Release"],

			["x",18*4],

			["i",True,"unknown_0",""],
			["b",True,"unknown_1",""],
			["b",True,"unknown_2",""],
			["b",True,"unknown_3",""],
			["b",True,"unknown_4",""],
			["b",True,"unknown_5",""],
			["b",True,"unknown_6",""],
			["b",True,"unknown_7",""],
			["b",True,"unknown_8",""],
			["b",True,"unknown_9",""],
			["b",True,"unknown_10",""],
			["b",True,"unknown_11",""],
			["b",True,"unknown_12",""],
			["b",True,"unknown_13",""],
			["b",True,"unknown_14",""],
			["b",True,"unknown_15",""],
			["b",True,"unknown_16",""],
			["b",True,"sidechain_number",""],
			["b",True,"unknown_18",""],
			["b",True,"unknown_19",""],
			["b",True,"unknown_20",""],
			["b",True,"unknown_21",""],
		]

	elif pluginname == 'fruity mute 2':
		out = [
			["I",True,"mute","Mute"],
			["I",True,"channel","Channel"],
			["I",False,"unknown_1",""],
		]

	elif pluginname == 'fruity panomatic':
		out = [
			["I",True,"pan","Pan"],
			["I",True,"vol","Vol"],
			["I",True,"lfo_shape","LFO Shape"],
			["I",True,"lfo_target","LFO Target"],
			["I",True,"lfo_amount","LFO Amount"],
			["I",True,"lfo_speed","LFO Speed"],
		]

	elif pluginname == 'fruity parametric eq 2':
		out = [ ["i",False,"version","Version"] ]

		for bandvar in [
			['_gain',"Gain"],
			['_freq'," Freq"],
			['_width'," Width"],
			['_type'," Type"],
			['_order'," Order"]
			]:
			for bandnum in range(7):
				out.append(["i",True,str(bandnum+1)+bandvar[0],"Band "+str(bandnum+1)+bandvar[1]])

		out.append(["I",True,'main_lvl',"Main Level"])

	elif pluginname == 'fruity parametric eq':
		for bandvar in [
			['_q'," Q"],
			['_freq'," Freq"],
			['_width'," Width"],
			['_type'," Type"]
			]:
			for bandnum in range(7):
				out.append(["i",True,str(bandnum+1)+bandvar[0],"Band "+str(bandnum+1)+bandvar[1]])

		out.append(["I",True,'main_lvl',"Main Level"])

	elif pluginname == 'fruity phase inverter':
		out = [
			["i",False,"version","Version"],
			["i",True,"state","State"]
		]

	elif pluginname == 'fruity phaser':
		out = [
			["i",False,"version","Version"],

			["i",True,"sweep_freq","Sweep Freq"],
			["i",True,"depth_min","Min Depth"],
			["i",True,"depth_max","Max Depth"],
			["i",True,"freq_range","Freq Range"],
			["i",True,"stereo","Stereo"],
			["i",True,"num_stages","NR. Stages"],
			["i",True,"feedback","Feedback"],
			["i",True,"drywet","Dry-Wet"],
			["i",True,"gain","gain"],
		]

	elif pluginname == 'fruity reeverb':
		out = [
			["i",False,"version","Version"],

			["i",True,"lowcut","Low Cut"],
			["i",True,"highcut","High Cut"],
			["i",True,"predelay","Predelay"],
			["i",True,"room_size","Room Size"],
			["i",True,"diffusion","Diffusion"],

			["i",True,"color","Color"],
			["i",True,"decay","Decay"],
			["i",True,"hidamping","High Damping"],
			["i",True,"dry","Dry"],
			["i",True,"reverb","Reverb"],
		]

	elif pluginname == 'fruity reeverb 2':
		out = [
			["i",False,"version","Version"],

			["i",True,"lowcut","Low Cut"],
			["i",True,"highcut","High Cut"],
			["i",True,"predelay","Predelay"],
			["i",True,"room_size","Room Size"],
			["i",True,"diffusion","Diffusion"],
			["i",True,"decay","Decay"],
			["i",True,"hidamping","High Damping"],
			["i",True,"bass","Bass Multi"],

			["i",True,"cross","Crossover"],
			["i",True,"stereo","Stereo Seperation"],
			["i",True,"dry","Dry"],
			["i",True,"er","Early Reflection"],
			["i",True,"wet","Wet"],
			["i",True,"mod_speed","Mod Speed"],
			["i",True,"mod","Mod Depth"],
			["b",True,"tempo_predelay","Tempo Based Predelay"],

			["b",True,"mid_side","Mid/Side Input"],
		]

	elif pluginname == 'fruity soft clipper':
		out = [
			["i",True,"threshold","Threshold"],
			["i",True,"postgain","PostGain"]
		]

	elif pluginname == 'fruity stereo enhancer':
		out = [
			["i",True,"pan","Pan"],
			["i",True,"vol","Volume"],
			["i",True,"stereo","Stereo Seperation"],
			["i",True,"phase_offs","Phase Offset"],
			["i",True,"prepost","Pre/Post"],
			["i",True,"phaseinvert","Phase Invert"],
		]

	elif pluginname == 'fruity stereo shaper':
		out = [
			["i",True,"r2l","Right to Left"],
			["i",True,"l2l","Left"],
			["i",True,"r2r","Right"],
			["i",True,"l2r","Left to Right"],
			["i",True,"delay","Delay"],
			["i",True,"dephase","Dephaseing"],
			["i",True,"iodiff","In/Out Diffrence"],
			["i",True,"prepost","Pre/Post"],
		]

	elif pluginname == 'fruity spectroman':
		out = [
			["b",False,"unknown_1",""],

			["f",True,"outputmode","Output Mode"],
			["f",True,"amp","Amp"],
			["f",True,"scale","Freq Scale"],
			["b",False,"windowing",""],
			["b",False,"show_peaks",""],
			["b",False,"stereo",""],
		]

	elif pluginname == 'tuner':
		out = [
			["i",False,"version","Version"],

			["I",True,"refrence","Refrence"],
			["I",True,"reactivity","Reactivity"],
			["I",True,"bass","Bass"],
			["I",False,"display_mode","Display Mode"],
		]

	elif pluginname == 'transient processor':
		out = [
			["i",False,"version","Version"],

			["I",True,"attack",""],
			["I",True,"drive",""],
			["I",True,"release",""],
			["I",True,"gain",""],
			["I",True,"attack_shape",""],
			["I",True,"release_shape",""],
			["I",True,"split_freq",""],
			["I",True,"split_balance",""],
			["I",True,"effect_on",""],
			["I",False,"display_flags",""],
			["I",False,"display_scroll",""],
		]

	elif pluginname == 'soundgoodizer':
		out = [
			["i",False,"version","Version"],

			["I",True,"mode",""],
			["I",True,"amount",""],
		]








	return out