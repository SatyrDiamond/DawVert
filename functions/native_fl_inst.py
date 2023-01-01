import base64
import struct
from functions import data_bytes
from functions import list_vst
from functions import params_vst

def convert(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	fl_plugdata = base64.b64decode(plugindata['data'])
	fl_plugstr = data_bytes.bytearray2BytesIO(base64.b64decode(plugindata['data']))
	if plugindata['name'].lower() == 'fruity soundfont player':
		flsf_unk = int.from_bytes(fl_plugstr.read(4), "little")
		flsf_patch = int.from_bytes(fl_plugstr.read(4), "little")-1
		flsf_bank = int.from_bytes(fl_plugstr.read(4), "little")
		flsf_reverb_sendlvl = int.from_bytes(fl_plugstr.read(4), "little")
		flsf_chorus_sendlvl = int.from_bytes(fl_plugstr.read(4), "little")
		flsf_mod = int.from_bytes(fl_plugstr.read(4), "little")
		flsf_asdf_A = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
		flsf_asdf_D = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
		flsf_asdf_S = int.from_bytes(fl_plugstr.read(4), "little") # max 127
		flsf_asdf_R = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
		flsf_lfo_predelay = int.from_bytes(fl_plugstr.read(4), "little") # max 5900
		flsf_lfo_amount = int.from_bytes(fl_plugstr.read(4), "little") # max 127
		flsf_lfo_speed = int.from_bytes(fl_plugstr.read(4), "little") # max 127
		flsf_cutoff = int.from_bytes(fl_plugstr.read(4), "little") # max 127

		flsf_filelen = int.from_bytes(fl_plugstr.read(1), "little")
		flsf_filename = fl_plugstr.read(flsf_filelen).decode('utf-8')

		flsf_reverb_sendto = int.from_bytes(fl_plugstr.read(4), "little", signed="True")+1
		flsf_reverb_builtin = int.from_bytes(fl_plugstr.read(1), "little")
		flsf_chorus_sendto = int.from_bytes(fl_plugstr.read(4), "little", signed="True")+1
		flsf_reverb_builtin = int.from_bytes(fl_plugstr.read(1), "little")
		flsf_hqrender = int.from_bytes(fl_plugstr.read(1), "little")

		instdata['plugin'] = "soundfont2"
		instdata['plugindata'] = {}
		instdata['plugindata']['file'] = flsf_filename
		if flsf_patch > 127:
			instdata['plugindata']['bank'] = 128
			instdata['plugindata']['patch'] = flsf_patch-128
		else:
			instdata['plugindata']['bank'] = flsf_bank
			instdata['plugindata']['patch'] = flsf_patch
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
