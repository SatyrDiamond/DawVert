import base64
import struct
from functions import data_bytes
from functions import list_vst
from functions import params_vst

simsynth_shapes = {0.4: 'noise', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}

def convert(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	fl_plugdata = base64.b64decode(plugindata['data'])
	fl_plugstr = data_bytes.bytearray2BytesIO(base64.b64decode(plugindata['data']))

	# ---------------------------------------- 3xOsc ----------------------------------------
	if plugindata['name'].lower() == '3x osc':
		fl_plugstr.read(4)
		#osc1_pan, osc1_shape, osc1_chorse, osc1_fine, osc1_ofs, osc1_detune, osc1_mixlevel
		osc1_pan, osc1_shape, osc1_chorse, osc1_fine, osc1_ofs, osc1_detune, osc1_mixlevel = struct.unpack('iiiiiii', fl_plugstr.read(28))
		osc2_pan, osc2_shape, osc2_chorse, osc2_fine, osc2_ofs, osc2_detune, osc2_mixlevel = struct.unpack('iiiiiii', fl_plugstr.read(28))
		osc3_pan, osc3_shape, osc3_chorse, osc3_fine, osc3_ofs, osc3_detune, phaseband = struct.unpack('iiiiiii', fl_plugstr.read(28))
		osc1_invert, osc2_invert, osc3_invert, osc3_am = struct.unpack('bbbb', fl_plugstr.read(4))

	# ---------------------------------------- Fruity Slicer ----------------------------------------
	if plugindata['name'].lower() == 'fruity slicer':
		fl_plugstr.read(4)
		slicer_beats = struct.unpack('f', fl_plugstr.read(4))[0]
		slicer_bpm = struct.unpack('f', fl_plugstr.read(4))[0]
		slicer_pitch, slicer_fitlen, slicer_unk1, slicer_att, slicer_dec = struct.unpack('iiiii', fl_plugstr.read(20))

		instdata['plugin'] = "slicer"
		instdata['plugindata'] = {}

		slicer_filelen = int.from_bytes(fl_plugstr.read(1), "little")
		slicer_filename = fl_plugstr.read(slicer_filelen).decode('utf-8')
		if slicer_filename != "": instdata['plugindata']['file'] = slicer_filename

		slicer_numslices = int.from_bytes(fl_plugstr.read(4), "little")

		cvpj_slices = []
		for _ in range(slicer_numslices):
			sd = {}
			slicer_slicenamelen = int.from_bytes(fl_plugstr.read(1), "little")
			slicer_slicename = fl_plugstr.read(slicer_slicenamelen).decode('utf-8')
			slicer_s_slice = struct.unpack('iihBBB', fl_plugstr.read(13))
			if slicer_slicename != "": sd['file'] = slicer_slicename
			sd['pos'] = slicer_s_slice[0]
			if slicer_s_slice[1] != -1: sd['note'] = slicer_s_slice[1]
			sd['reverse'] = slicer_s_slice[5]
			cvpj_slices.append(sd)

		for slicenum in range(len(cvpj_slices)):
			if slicenum-1 >= 0 and slicenum != len(cvpj_slices): cvpj_slices[slicenum-1]['end'] = cvpj_slices[slicenum]['pos']-1
			if slicenum == len(cvpj_slices)-1: cvpj_slices[slicenum]['end'] = cvpj_slices[slicenum]['pos']+100000000

		instdata['plugindata']['bpm'] = slicer_bpm
		instdata['plugindata']['beats'] = slicer_beats
		instdata['plugindata']['slices'] = cvpj_slices

	# ---------------------------------------- Wasp ----------------------------------------
	if plugindata['name'].lower() == 'wasp':
		wasp_unk = int.from_bytes(fl_plugstr.read(4), "little")
		wasp_1_shape, wasp_1_crs, wasp_1_fine, wasp_2_shape, wasp_2_crs, wasp_2_fine = struct.unpack('iiiiii', fl_plugstr.read(24))
		wasp_3_shape, wasp_3_amt, wasp_12_fade, wasp_pw, wasp_fm, wasp_ringmod = struct.unpack('iiiiii', fl_plugstr.read(24))
		wasp_amp_A, wasp_amp_S, wasp_amp_D, wasp_amp_R, wasp_fil_A, wasp_fil_S, wasp_fil_D, wasp_fil_R = struct.unpack('iiiiiiii', fl_plugstr.read(32))
		wasp_fil_kbtrack, wasp_fil_qtype, wasp_fil_cut, wasp_fil_res, wasp_fil_env = struct.unpack('iiiii', fl_plugstr.read(20))
		wasp_l1_shape, wasp_l1_target, wasp_l1_amt, wasp_l1_spd, wasp_l1_sync, wasp_l1_reset = struct.unpack('i'*6, fl_plugstr.read(24))
		wasp_l2_shape, wasp_l2_target, wasp_l2_amt, wasp_l2_spd, wasp_l2_sync, wasp_l2_reset = struct.unpack('i'*6, fl_plugstr.read(24))
		wasp_dist_on, wasp_dist_drv, wasp_dist_tone, wasp_dualvoice = struct.unpack('iiii', fl_plugstr.read(16))

	# ---------------------------------------- Wasp XT ----------------------------------------
	if plugindata['name'].lower() == 'wasp xt':
		wasp_unk = int.from_bytes(fl_plugstr.read(4), "little")
		wasp_1_shape, wasp_1_crs, wasp_1_fine, wasp_2_shape, wasp_2_crs, wasp_2_fine = struct.unpack('iiiiii', fl_plugstr.read(24))
		wasp_3_shape, wasp_3_amt, wasp_12_fade, wasp_pw, wasp_fm, wasp_ringmod = struct.unpack('iiiiii', fl_plugstr.read(24))
		wasp_amp_A, wasp_amp_S, wasp_amp_D, wasp_amp_R, wasp_fil_A, wasp_fil_S, wasp_fil_D, wasp_fil_R = struct.unpack('iiiiiiii', fl_plugstr.read(32))
		wasp_fil_kbtrack, wasp_fil_qtype, wasp_fil_cut, wasp_fil_res, wasp_fil_env = struct.unpack('iiiii', fl_plugstr.read(20))
		wasp_l1_shape, wasp_l1_target, wasp_l1_amt, wasp_l1_spd, wasp_l1_sync, wasp_l1_reset = struct.unpack('i'*6, fl_plugstr.read(24))
		wasp_l2_shape, wasp_l2_target, wasp_l2_amt, wasp_l2_spd, wasp_l2_sync, wasp_l2_reset = struct.unpack('i'*6, fl_plugstr.read(24))
		wasp_dist_on, wasp_dist_drv, wasp_dist_tone, wasp_dualvoice = struct.unpack('iiii', fl_plugstr.read(16))

		waspxt_amp, waspxt_analog, waspxt_me_atk, waspxt_me_dec = struct.unpack('i'*4, fl_plugstr.read(16))
		waspxt_me_amt, waspxt_me_1lvl, waspxt_me_2pitch, waspxt_me_1ami = struct.unpack('i'*4, fl_plugstr.read(16))
		waspxt_me_pw, waspxt_vol, waspxt_lfo1_delay, waspxt_lfo2_delay = struct.unpack('i'*4, fl_plugstr.read(16))
		waspxt_me_filter, waspxt_wnoise = struct.unpack('i'*2, fl_plugstr.read(8))

	# ---------------------------------------- Soundfont Player ----------------------------------------
	if plugindata['name'].lower() == 'fruity soundfont player':
		# flsf_asdf_A max 5940 - flsf_asdf_D max 5940 - flsf_asdf_S max 127 - flsf_asdf_R max 5940
		# flsf_lfo_predelay max 5900 - flsf_lfo_amount max 127 - flsf_lfo_speed max 127 - flsf_cutoff max 127
		flsf_unk, flsf_patch, flsf_bank, flsf_reverb_sendlvl, flsf_chorus_sendlvl, flsf_mod = struct.unpack('IIIIII', fl_plugstr.read(24))
		flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = struct.unpack('IIII', fl_plugstr.read(16))
		flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, flsf_cutoff = struct.unpack('IIII', fl_plugstr.read(16))

		flsf_filelen = int.from_bytes(fl_plugstr.read(1), "little")
		flsf_filename = fl_plugstr.read(flsf_filelen).decode('utf-8')

		flsf_reverb_sendto, flsf_reverb_builtin = struct.unpack('ib', fl_plugstr.read(5))
		flsf_chorus_sendto, flsf_chorus_builtin = struct.unpack('ib', fl_plugstr.read(5))

		flsf_hqrender = int.from_bytes(fl_plugstr.read(1), "little")

		flsf_patch -= 1

		instdata['plugin'] = "soundfont2"
		instdata['plugindata'] = {}
		instdata['plugindata']['file'] = flsf_filename
		if flsf_patch > 127:
			instdata['plugindata']['bank'] = 128
			instdata['plugindata']['patch'] = flsf_patch-128
		else:
			instdata['plugindata']['bank'] = flsf_bank
			instdata['plugindata']['patch'] = flsf_patch

	# ---------------------------------------- DX10 ----------------------------------------
	elif plugindata['name'].lower() == 'fruity dx10':
		int.from_bytes(fl_plugstr.read(4), "little")
		fldx_amp_att, fldx_amp_dec, fldx_amp_rel, fldx_mod_course = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod_fine, fldx_mod_init, fldx_mod_time, fldx_mod_sus = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod_rel, fldx_mod_velsen, fldx_vibrato, fldx_waveform = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod_thru, fldx_lforate, fldx_mod2_course, fldx_mod2_fine = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod2_init, fldx_mod2_time, fldx_mod2_sus, fldx_mod2_rel = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod2_velsen = int.from_bytes(fl_plugstr.read(4), "little")/65536
		fldx_octave = (int.from_bytes(fl_plugstr.read(4), "little", signed="True")/6)+0.5

		vstdxparams = {}
		params_vst.add_param(vstdxparams, 0, "Attack  ", fldx_amp_att/65536)
		params_vst.add_param(vstdxparams, 1, "Decay   ", fldx_amp_dec/65536)
		params_vst.add_param(vstdxparams, 2, "Release ", fldx_amp_rel/65536)
		params_vst.add_param(vstdxparams, 3, "Coarse  ", fldx_mod_course/65536)
		params_vst.add_param(vstdxparams, 4, "Fine    ", fldx_mod_fine/65536)
		params_vst.add_param(vstdxparams, 5, "Mod Init", fldx_mod_init/65536)
		params_vst.add_param(vstdxparams, 6, "Mod Dec ", fldx_mod_time/65536)
		params_vst.add_param(vstdxparams, 7, "Mod Sus ", fldx_mod_sus/65536)
		params_vst.add_param(vstdxparams, 8, "Mod Rel ", fldx_mod_rel/65536)
		params_vst.add_param(vstdxparams, 9, "Mod Vel ", fldx_mod_velsen/65536)
		params_vst.add_param(vstdxparams, 10, "Vibrato ", fldx_vibrato/65536)
		params_vst.add_param(vstdxparams, 11, "Octave  ", fldx_octave)
		params_vst.add_param(vstdxparams, 12, "FineTune", 0.5)
		params_vst.add_param(vstdxparams, 13, "Waveform", fldx_waveform/65536)
		params_vst.add_param(vstdxparams, 14, "Mod Thru", fldx_mod_thru/65536)
		params_vst.add_param(vstdxparams, 15, "LFO Rate", fldx_lforate/65536)
		list_vst.replace_params(instdata, 'DX10', 16, vstdxparams)

	# ---------------------------------------- SimSynth ----------------------------------------
	elif plugindata['name'].lower() == 'simsynth':
		#osc1_pw, osc1_crs, osc1_fine, osc1_lvl, osc1_lfo, osc1_env, osc1_shape
		osc1_pw, osc1_crs, osc1_fine, osc1_lvl, osc1_lfo, osc1_env, osc1_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
		osc2_pw, osc2_crs, osc2_fine, osc2_lvl, osc2_lfo, osc2_env, osc2_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
		osc3_pw, osc3_crs, osc3_fine, osc3_lvl, osc3_lfo, osc3_env, osc3_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
		lfo_del, lfo_rate, unused, lfo_shape = struct.unpack('dddd', fl_plugstr.read(32))
		UNK, svf_cut, svf_emph, svf_env = struct.unpack('dddd', fl_plugstr.read(32))
		svf_lfo, svf_kb, UNK, svf_high = struct.unpack('dddd', fl_plugstr.read(32))
		svf_band, UNK, amp_att, amp_dec = struct.unpack('dddd', fl_plugstr.read(32))
		amp_sus, amp_rel, amp_lvl, UNK = struct.unpack('dddd', fl_plugstr.read(32))
		svf_att, svf_dec, svf_sus, svf_rel = struct.unpack('dddd', fl_plugstr.read(32))
		fl_plugstr.read(64)
		fl_plugstr.read(12)
		osc1_on, osc1_o1, osc1_o2, osc1_warm = struct.unpack('IIII', fl_plugstr.read(16))
		osc2_on, osc2_o1, osc2_o2, osc2_warm = struct.unpack('IIII', fl_plugstr.read(16))
		osc3_on, osc3_o1, osc3_o2, osc3_warm = struct.unpack('IIII', fl_plugstr.read(16))
		lfo_on, lfo_retrugger, svf_on, UNK = struct.unpack('IIII', fl_plugstr.read(16))
		lfo_trackamp, UNK, chorus_on, UNK = struct.unpack('IIII', fl_plugstr.read(16))

		#params_vital.create()

		#vital_osc1_shape = []
		#for num in range(2048): vital_osc1_shape.append(tripleoct(num/2048, simsynth_shapes[osc1_shape], osc1_pw, osc1_o1, osc1_o2))
		#params_vital.replacewave(0, vital_osc1_shape)
		#params_vital.setvalue('osc_1_on', osc1_on)
		#params_vital.setvalue('osc_1_transpose', (osc1_crs-0.5)*48)
		#params_vital.setvalue('osc_1_tune', (osc1_fine-0.5)*2)
		#params_vital.setvalue('osc_1_level', osc1_lvl/2)
		#if osc1_warm == 1:
			#params_vital.setvalue('osc_1_unison_detune', 2.2)
			#params_vital.setvalue('osc_1_unison_voices', 6)

		#vital_osc2_shape = []
		#for num in range(2048): vital_osc2_shape.append(tripleoct(num/2048, simsynth_shapes[osc2_shape], osc2_pw, osc2_o1, osc2_o2))
		#params_vital.replacewave(1, vital_osc2_shape)
		#params_vital.setvalue('osc_2_on', osc2_on)
		#params_vital.setvalue('osc_2_transpose', (osc2_crs-0.5)*48)
		#params_vital.setvalue('osc_2_tune', (osc2_fine-0.5)*2)
		#params_vital.setvalue('osc_2_level', osc2_lvl/2)
		#if osc2_warm == 1:
			#params_vital.setvalue('osc_2_unison_detune', 2.2)
			#params_vital.setvalue('osc_2_unison_voices', 6)

		#vital_osc3_shape = []
		#for num in range(2048): vital_osc3_shape.append(tripleoct(num/2048, simsynth_shapes[osc3_shape], osc3_pw, osc3_o1, osc3_o2))
		#params_vital.replacewave(2, vital_osc3_shape)
		#params_vital.setvalue('osc_3_on', osc3_on)
		#params_vital.setvalue('osc_3_transpose', (osc3_crs-0.5)*48)
		#params_vital.setvalue('osc_3_tune', (osc3_fine-0.5)*2)
		#params_vital.setvalue('osc_3_level', osc3_lvl/2)
		#if osc3_warm == 1:
			#params_vital.setvalue('osc_3_unison_detune', 2.2)
			#params_vital.setvalue('osc_3_unison_voices', 6)

		#params_vital.setvalue('env_1_attack', ss_asdr(amp_att)*4)
		#params_vital.setvalue('env_1_decay', ss_asdr(amp_dec)*4)
		#params_vital.setvalue('env_1_sustain', amp_sus)
		#params_vital.setvalue('env_1_release', ss_asdr(amp_rel)*4)

		#vitaldata = params_vital.getdata()
		#list_vst.replace_data(instdata, 'Vital', vitaldata.encode('utf-8'))
