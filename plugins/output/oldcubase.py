# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import uuid
import os
import shutil
from objects import globalstore
from functions import data_values
from functions import xtramath
from external.easybinrw import easybinrw
import math

logpreset_def = b'\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

DEBUG_DISABLE_INST_TRACK = False
DEBUG_DISABLE_AUDIO_TRACK = False

def make_blank_slots(num, synthslots):
	for x in range(num): synthslots.append({'State': 0})

def decode_color(intcolor):
	return int.from_bytes(bytes([intcolor[2], intcolor[1], intcolor[0]]), "little")

def do_color(visual_obj, total_colors, additional_attributes):
	if visual_obj.color: 
		colorint = visual_obj.color.get_int()
		if colorint not in total_colors: total_colors.append(colorint)
		additional_attributes['Farb'] = total_colors.index(colorint)

def calc_volume(o):
	if o: 
		vol = math.log2(o)/3
		vol = pow(2, vol)
		return xtramath.clamp(vol*25856, 0, 32765)
	else:
		return 0

def calc_pan(o):
	return ((o/2)+0.5)

class output_oldcubase(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_shortname(self):
		return 'oldcubase'
	
	def get_name(self):
		return 'Cubase 5+'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['audio_stretch'] = ['rate']
		in_dict['file_ext'] = 'steinberg-project'
		in_dict['audio_filetypes'] = ['wav']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['notes_midi'] = True
		in_dict['placement_cut'] = True
		in_dict['track_arranger'] = True
		in_dict['fxtype'] = 'groupreturn'
		in_dict['notepl_pitch'] = True

	def parse(self, convproj_obj, dawvert_intent):
		global to_wide_string
		global to_norm_string
		global add_list
		from objects import counter
		from objects.file_proj_past import sequel as proj_sequel
		to_wide_string = proj_sequel.to_wide_string
		to_norm_string = proj_sequel.to_norm_string
		add_list = proj_sequel.add_list
		add_list_genid = proj_sequel.add_list_genid
		sequel_list_int = proj_sequel.sequel_list_int
		sequel_list_float = proj_sequel.sequel_list_float
		sequel_list_string = proj_sequel.sequel_list_string
		sequel_list_dict = proj_sequel.sequel_list_dict
		sequel_list_obj = proj_sequel.sequel_list_obj

		timebase = 480

		convproj_obj.change_timings(timebase)
		
		project_dur = 1000000

		counter_id = counter.counter(5000000, '')
		returnnum_id = counter.counter(200, '')
		inbusnum_id = counter.counter(504, '')

		project_obj = proj_sequel.sequel_project()

		def_root_objects = project_obj.def_root_objects
		def_root_objects['Version'] = counter_id.get()
		def_root_objects['Project'] = counter_id.get()
		def_root_objects['Devices'] = counter_id.get()
		def_root_objects['GuiState'] = counter_id.get()

		seq_ApplicationVersion = proj_sequel.class_ApplicationVersion()
		seq_ApplicationVersion.idnum = def_root_objects['Version']
		project_obj.objects[seq_ApplicationVersion.idnum] = seq_ApplicationVersion

		seq_Project = proj_sequel.class_Project()
		seq_Project.idnum = def_root_objects['Project']
		project_obj.objects[seq_Project.idnum] = seq_Project

		seq_Devices = proj_sequel.class_Attributes()
		seq_Devices.idnum = def_root_objects['Devices']
		project_obj.objects[seq_Devices.idnum] = seq_Devices

		seq_GuiState = proj_sequel.class_Attributes()
		seq_GuiState.idnum = def_root_objects['GuiState']

		project_obj.objects[seq_GuiState.idnum] = seq_GuiState

		bpm = int(convproj_obj.params.get('bpm', 120).value)

		seq_MTempoTrackEvent = proj_sequel.class_MTempoTrackEvent()
		id_trk_bpm = seq_MTempoTrackEvent.idnum = counter_id.get()
		project_obj.objects[id_trk_bpm] = seq_MTempoTrackEvent

		tempopoints = {}
		tempopoints[0] = bpm
		if_found, autodata = convproj_obj.automation.get(['main', 'bpm'], 'float')
		if if_found:
			if autodata.u_nopl_ticks:
				for pos, val in autodata.nopl_ticks:
					tempopoints[pos] = val

		seq_MTempoTrackEvent.rehearsaltempo = bpm
		for pos, bpm in tempopoints.items():
			MTempoEvent = add_list_genid(seq_MTempoTrackEvent.tempoevent, 'MTempoEvent', counter_id)
			MTempoEvent.ppq = pos
			MTempoEvent.bpm = bpm

		seq_MSignatureTrackEvent = proj_sequel.class_MSignatureTrackEvent()
		id_trk_meas = seq_MSignatureTrackEvent.idnum = counter_id.get()
		project_obj.objects[id_trk_meas] = seq_MSignatureTrackEvent

		MTimeSignatureEvent = add_list_genid(seq_MSignatureTrackEvent.signatureevent, 'MTimeSignatureEvent', counter_id)
		MTimeSignatureEvent.numerator, MTimeSignatureEvent.denominator = convproj_obj.timesig

		mainatt = seq_Devices.data
		storeddevices = mainatt['StoredDevices'] = sequel_list_string([])
		storeddevices.append(to_norm_string(""))

		mainatt['Mixer'] = {}
		transport = mainatt['Transport'] = {}
		transport['Cycle Left'] = {'Time': float(convproj_obj.transport.loop_start), 'Domain': {'Type': 1, 'Period': 1.0}}
		transport['Cycle Right'] = {'Time': float(convproj_obj.transport.loop_end), 'Domain': {'Type': 1, 'Period': 1.0}}
		transport['RecordMode'] = 1
		transport['CycleRecordMode'] = 0
		vst_mixer = mainatt['VST Mixer'] = {}
		input_channels = vst_mixer['Input Channels'] = sequel_list_dict()

		guidata = seq_GuiState.data
		guidata['PlayOrderSettings'] = {}
		guidata['PlayOrderSettings']['PadLabel'] = sequel_list_string([to_norm_string('-') for x in range(16)])
		guidata['PlayOrderSettings']['PadAssignment'] = sequel_list_int([27 for x in range(16)])
		guidata['PlayOrderSettings']['PlayOrderActivate'] = sequel_list_float([0])
		guidata['Transpose Track Visible'] = 0
		guidata['Playorder Track Visible'] = 0

		# ================================================== InputChannels ==================================================
		deviceattributes = {}
		deviceattributes['Name'] = {'String': to_wide_string('Stereo In')}
		deviceattributes['Type'] = 7
		deviceattributes['InputGain'] = {'Value': 16383.5}
		deviceattributes['InputPhase'] = 0
		deviceattributes['Volume'] = {'Value': float(25856), 'AnchorValue': 0.0}
		deviceattributes['InsertFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
		make_blank_slots(3, deviceattributes['InsertFolder']['Slot'])
		deviceattributes['EQPosition'] = 0
		deviceattributes['hasEQ'] = 0
		deviceattributes['EQ'] = {}
		pandata = {}
		pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
		pandata['PannerType'] = {'Value': 2, 'Min': 0, 'Max': 11}
		pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
		pandata['Plugin Name'] = to_wide_string('Panner')
		pandata['Audio Input Count'] = 1
		pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
		pandata['Audio Output Count'] = 1
		pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
		pandata['Event Input Count'] = 0
		pandata['Event Output Count'] = 0
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.float(0.5)
		ebrw_writestr.float(0.5)
		ebrw_writestr.int_u32(4)
		ebrw_writestr.int_u32(2)
		ebrw_writestr.int_u32(0)
		pandata['audioComponent'] = ebrw_writestr.getvalue()
		pandata['editController'] = b''
		pandata['Active'] = 1
		pandata['IDString'] = to_wide_string('Panner')
		pandata['Bay Program'] = to_wide_string('')
		deviceattributes['Panner'] = pandata
		deviceattributes['VUSelect'] = 1
		deviceattributes['VURange'] = 0
		deviceattributes['Monitor'] = {'Value': 0, 'Min': 0, 'Max': 2}
		deviceattributes['OwnInputBus'] = {'Name': to_wide_string('Stereo In'), 'Bus UID': 1000001, 'Bus Type': 10, 'Input Arrangement': {'Type': sequel_list_int([1, 2])}, 'Output Arrangement': {'Type': sequel_list_int([1, 2])}}
		incon = deviceattributes['OwnInputBus']['Connections'] = sequel_list_string()
		incon.append(to_norm_string('I|DawVert Input|In 1'))
		incon.append(to_norm_string('I|DawVert Input|In 2'))
		deviceattributes['InputBusValue'] = {'Value': 0}
		deviceattributes['OutputBusValue'] = {'Value': 0}
		deviceattributes['OutputBus'] = {'Name': to_wide_string('Stereo In'), 'Bus UID': 2000002, 'Bus Type': 12, 'Input Arrangement': {'Type': sequel_list_int([1, 2])}, 'Output Arrangement': {'Type': sequel_list_int([1, 2])}}
		deviceattributes["FreezePosition"] = 2
		deviceattributes["Listen Mode"] = 0
		deviceattributes["LinkedPanner"] = 0
		deviceattributes["IDString"] = to_norm_string('InputChannel')
		input_channels.append(deviceattributes)

		childinbus = deviceattributes['OutputBus']['Child Bus'] = sequel_list_dict()
		childinbus.append( {'Name': to_wide_string('Left'), 'Bus UID': 3, 'Bus Type': 12, 'Input Arrangement': {'Type': sequel_list_int([1])}, 'Output Arrangement': {'Type': sequel_list_int([1])}} )
		childinbus.append( {'Name': to_wide_string('Right'), 'Bus UID': 4, 'Bus Type': 12, 'Input Arrangement': {'Type': sequel_list_int([2])}, 'Output Arrangement': {'Type': sequel_list_int([2])}} )

		deviceattributes = {}
		deviceattributes['Name'] = {'String': to_wide_string('In 1')}
		deviceattributes['Type'] = 7
		deviceattributes['InputGain'] = {'Value': 16383.5}
		deviceattributes['InputPhase'] = 0
		deviceattributes['Volume'] = {'Value': float(25856), 'AnchorValue': 0.0}
		deviceattributes['InsertFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
		make_blank_slots(3, deviceattributes['InsertFolder']['Slot'])
		deviceattributes['EQPosition'] = 0
		deviceattributes['hasEQ'] = 0
		deviceattributes['EQ'] = {}
		pandata = {}
		pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
		pandata['PannerType'] = {'Value': 6, 'Min': 0, 'Max': 11}
		pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
		pandata['Plugin Name'] = to_wide_string('Panner')
		pandata['Audio Input Count'] = 1
		pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([0])}])
		pandata['Audio Output Count'] = 1
		pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([0])}])
		pandata['Event Input Count'] = 0
		pandata['Event Output Count'] = 0
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.float(0.5)
		ebrw_writestr.float(0.5)
		ebrw_writestr.int_u32(4)
		ebrw_writestr.int_u32(2)
		ebrw_writestr.int_u32(0)
		pandata['audioComponent'] = ebrw_writestr.getvalue()
		pandata['editController'] = b''
		pandata['Active'] = 1
		pandata['IDString'] = to_wide_string('Panner')
		pandata['Bay Program'] = to_wide_string('')
		deviceattributes['Panner'] = pandata
		deviceattributes['VUSelect'] = 1
		deviceattributes['VURange'] = 0
		deviceattributes['Monitor'] = {'Value': 0, 'Min': 0, 'Max': 2}
		deviceattributes['OwnInputBus'] = {'Name': to_wide_string('In 1'), 'Bus UID': 1000010, 'Bus Type': 10, 'Input Arrangement': {'Type': sequel_list_int([0])}, 'Output Arrangement': {'Type': sequel_list_int([0])}}
		incon = deviceattributes['OwnInputBus']['Connections'] = sequel_list_string()
		incon.append(to_norm_string('I|DawVert Input|In 1'))
		deviceattributes['InputBusValue'] = {'Value': 0}
		deviceattributes['OutputBusValue'] = {'Value': 0}
		deviceattributes['OutputBus'] = {'Name': to_wide_string('In 1'), 'Bus UID': 2000011, 'Bus Type': 12, 'Input Arrangement': {'Type': sequel_list_int([0])}, 'Output Arrangement': {'Type': sequel_list_int([0])}}
		input_channels.append(deviceattributes)
		deviceattributes["FreezePosition"] = 2
		deviceattributes["Listen Mode"] = 0
		deviceattributes["LinkedPanner"] = 0
		deviceattributes["IDString"] = to_norm_string('InputChannel 2')

		deviceattributes = {}
		deviceattributes['Name'] = {'String': to_wide_string('In 2')}
		deviceattributes['Type'] = 7
		deviceattributes['InputGain'] = {'Value': 16383.5}
		deviceattributes['InputPhase'] = 0
		deviceattributes['Volume'] = {'Value': float(25856), 'AnchorValue': 0.0}
		deviceattributes['InsertFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
		make_blank_slots(3, deviceattributes['InsertFolder']['Slot'])
		deviceattributes['EQPosition'] = 0
		deviceattributes['hasEQ'] = 0
		deviceattributes['EQ'] = {}
		pandata = {}
		pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
		pandata['PannerType'] = {'Value': 6, 'Min': 0, 'Max': 11}
		pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
		pandata['Plugin Name'] = to_wide_string('Panner')
		pandata['Audio Input Count'] = 1
		pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([0])}])
		pandata['Audio Output Count'] = 1
		pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([0])}])
		pandata['Event Input Count'] = 0
		pandata['Event Output Count'] = 0
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.float(0.5)
		ebrw_writestr.float(0.5)
		ebrw_writestr.int_u32(4)
		ebrw_writestr.int_u32(2)
		ebrw_writestr.int_u32(0)
		pandata['audioComponent'] = ebrw_writestr.getvalue()
		pandata['editController'] = b''
		pandata['Active'] = 1
		pandata['IDString'] = to_wide_string('Panner')
		pandata['Bay Program'] = to_wide_string('')
		deviceattributes['Panner'] = pandata
		deviceattributes['VUSelect'] = 1
		deviceattributes['VURange'] = 0
		deviceattributes['Monitor'] = {'Value': 0, 'Min': 0, 'Max': 2}
		deviceattributes['OwnInputBus'] = {'Name': to_wide_string('In 2'), 'Bus UID': 1000012, 'Bus Type': 10, 'Input Arrangement': {'Type': sequel_list_int([0])}, 'Output Arrangement': {'Type': sequel_list_int([0])}}
		incon = deviceattributes['OwnInputBus']['Connections'] = sequel_list_string()
		incon.append(to_norm_string('I|DawVert Input|In 2'))
		deviceattributes['InputBusValue'] = {'Value': 0}
		deviceattributes['OutputBusValue'] = {'Value': 0}
		deviceattributes['OutputBus'] = {'Name': to_wide_string('In 2'), 'Bus UID': 2000013, 'Bus Type': 12, 'Input Arrangement': {'Type': sequel_list_int([0])}, 'Output Arrangement': {'Type': sequel_list_int([0])}}
		input_channels.append(deviceattributes)
		deviceattributes["FreezePosition"] = 2
		deviceattributes["Listen Mode"] = 0
		deviceattributes["LinkedPanner"] = 0
		deviceattributes["IDString"] = to_norm_string('InputChannel 3')

		vst_mixer['Default Input'] = 0

		# ================================================== OUTPUT ==================================================
		output_channels = vst_mixer['Output Channels'] = sequel_list_dict()
		deviceattributes = {}
		deviceattributes['Name'] = {'String': to_wide_string('Master')}
		deviceattributes['Type'] = 8
		deviceattributes['InputGain'] = {'Value': 16383.5}
		deviceattributes['InputPhase'] = 0
		deviceattributes['Volume'] = {'Value': float(25856), 'AnchorValue': 0.0}
		deviceattributes['hasAudioInserts'] = 1
		deviceattributes['InsertFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
		make_blank_slots(1, deviceattributes['InsertFolder']['Slot'])
		pandata = {}
		pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
		pandata['PannerType'] = {'Value': 2, 'Min': 0, 'Max': 11}
		pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
		pandata['Plugin Name'] = to_wide_string('Panner')
		pandata['Audio Input Count'] = 1
		pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
		pandata['Audio Output Count'] = 1
		pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
		pandata['Event Input Count'] = 0
		pandata['Event Output Count'] = 0
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.float(0.5)
		ebrw_writestr.float(0.5)
		ebrw_writestr.int_u32(4)
		ebrw_writestr.int_u32(2)
		ebrw_writestr.int_u32(0)
		pandata['audioComponent'] = ebrw_writestr.getvalue()
		pandata['editController'] = b''
		pandata['Active'] = 1
		pandata['IDString'] = to_wide_string('Panner')
		pandata['Bay Program'] = to_wide_string('')
		deviceattributes['Panner'] = pandata
		deviceattributes['VUSelect'] = 1
		deviceattributes['VURange'] = 0
		deviceattributes['Monitor'] = {'Value': 0, 'Min': 0, 'Max': 2}
		deviceattributes['OwnInputBus'] = {'Name': to_wide_string('Master'), 'Bus UID': 5, 'Bus Type': 18, 'Input Arrangement': {'Type': sequel_list_int([1, 2])}, 'Output Arrangement': {'Type': sequel_list_int([1, 2])}}
		deviceattributes['InputBusValue'] = {'Value': 0}
		deviceattributes['OutputBusValue'] = {'Value': 0}
		deviceattributes['OutputBus'] = {'Name': to_wide_string('Master'), 'Bus UID': 6, 'Bus Type': 11, 'Input Arrangement': {'Type': sequel_list_int([1, 2])}, 'Output Arrangement': {'Type': sequel_list_int([1, 2])}}
		incon = deviceattributes['OutputBus']['Connections'] = sequel_list_string()
		incon.append(to_norm_string('O|DawVert Output|Out 1'))
		incon.append(to_norm_string('O|DawVert Output|Out 2'))
		deviceattributes["FreezePosition"] = 4
		deviceattributes["Listen Mode"] = 0
		deviceattributes["LinkedPanner"] = 0
		deviceattributes["IDString"] = to_norm_string('OutputChannel')
		deviceattributes["clickEnable"] = 1
		deviceattributes["clickVolume"] = {'Value': float(25856), 'AnchorValue': 0.0}
		deviceattributes["clickPan"] = {'Value': 16383.5}
		output_channels.append(deviceattributes)

		childinbus = deviceattributes['OwnInputBus']['Child Bus'] = sequel_list_dict()
		childinbus.append( {'Name': to_wide_string('Left'), 'Bus UID': 7, 'Bus Type': 18, 'Input Arrangement': {'Type': sequel_list_int([1])}, 'Output Arrangement': {'Type': sequel_list_int([1])}} )
		childinbus.append( {'Name': to_wide_string('Right'), 'Bus UID': 8, 'Bus Type': 18, 'Input Arrangement': {'Type': sequel_list_int([2])}, 'Output Arrangement': {'Type': sequel_list_int([2])}} )

		vst_mixer["Default Output"] = 0
		vst_mixer['Synth Rack'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
		make_blank_slots(64, vst_mixer['Synth Rack']['Slot'])
		vst_mixer["MutePreSendInMute"] = 1
		portdescriptors = mainatt["PortDescriptors"] = sequel_list_dict([])
		portdescriptors.append({'ID': to_norm_string("I|DawVert Input|In 1"), 'Type': to_norm_string("audio"), 'Subtype': to_norm_string("system"), 'Role': to_norm_string("mono")})
		portdescriptors.append({'ID': to_norm_string("I|DawVert Input|In 2"), 'Type': to_norm_string("audio"), 'Subtype': to_norm_string("system"), 'Role': to_norm_string("mono")})
		portdescriptors.append({'ID': to_norm_string("O|DawVert Output|Out 1"), 'Type': to_norm_string("audio"), 'Subtype': to_norm_string("system"), 'Role': to_norm_string("left")})
		portdescriptors.append({'ID': to_norm_string("O|DawVert Output|Out 2"), 'Type': to_norm_string("audio"), 'Subtype': to_norm_string("system"), 'Role': to_norm_string("right")})

		
		# ================================================== ROOT ==================================================
		seq_engineroot = seq_Project.data_root
		seq_engineroot.length = project_dur
		seq_engineroot.spread_counter(counter_id)
		seq_engineroot.tempo_track.idnum = id_trk_bpm
		seq_engineroot.signature_track.idnum = id_trk_meas
		seq_engineroot.auto_fade_settings.spread_counter(counter_id)
		seq_engineroot.auto_fade_settings.init_values()

		working_directory = seq_engineroot.working_directory
		if dawvert_intent.output_mode == 'file':
			namet = dawvert_intent.output_visname
			working_directory.name = os.path.basename(dawvert_intent.output_file)
			working_directory.path = os.path.join(dawvert_intent.output_folder, namet)
			working_directory.type = 1
		else:
			working_directory.name = os.path.basename(dawvert_intent.output_file)
			working_directory.path = dawvert_intent.output_folder
			working_directory.type = 1

		root_pool = seq_engineroot.pool
		root_pool.media_tree.idnum = counter_id.get()
		root_pool.media_tree.root.idnum = counter_id.get()
		root_pool.media_tree.flags = 5
		media_root = root_pool.media_tree.root
		media_root.flags = 608
		media_root.name = to_wide_string("Media")

		subtree_audio = add_list_genid(media_root.subentries, 'GTreeEntry', counter_id)
		subtree_audio.flags = 578
		subtree_audio.name = to_wide_string("Audio")
		subtree_audio.v_id = 1

		subtree = add_list_genid(media_root.subentries, 'GTreeEntry', counter_id)
		subtree.flags = 578
		subtree.name = to_wide_string("Trash")
		subtree.v_id = 2

		proj_setup = seq_Project.setup
		proj_setup['Length'] = {'Time': float(30000000), 'Domain': {'Type': 1, 'Period': float(1)}}
		proj_setup['FrameType'] = 5
		proj_setup['TimeType'] = 0
		proj_setup['SampleRate'] = float(44100)
		proj_setup['SampleSize'] = 16
		proj_setup['PanLaw'] = 6

		seq_engineroot.additional_attributes['sCOL'] = 1
		root_miSe = seq_engineroot.additional_attributes['miSe'] = {}
		root_miSe['pitchFilter'] = 1
		root_miSe['onVeloFilter'] = 1
		root_miSe['offVeloFilter'] = 0
		root_miSe['moveInsertMode'] = 0
		root_miSe['lengthSnap'] = 0
		root_miSe['insertVelocity'] = 100
		insertVelocities = root_miSe['insertVelocities'] = proj_sequel.class_PInsVeloPreset()
		insertVelocities.idnum = counter_id.get()
		insertVelocities.velocities = sequel_list_int([100,90,70,50,120])
		root_miSe['editFeedback'] = 1
		root_miSe['eventColorMode'] = 0
		TControllerLaneDef = proj_sequel.class_TControllerLaneDef()
		TControllerLaneDef.idnum = counter_id.get()
		controllerLaneSetup = root_miSe['controllerLaneSetup'] = {}
		controllerLaneSetup['LaneInfo'] = sequel_list_obj([TControllerLaneDef])
		root_miSe['autoQuantize'] = 0

		total_colors = []

		sq_UColorSet = proj_sequel.class_UColorSet()
		sq_UColorSet.idnum = counter_id.get()
		for num, colornum in enumerate([15166282,15701074,16233818,16775019,11392619,8701547,4894059,4896173,4896231,5932221,6513573,6507148,9196172,11360916,15166356,15166323]):
			#sq_UColorSet.c_set.append({'Name': to_wide_string("Color %i"%int(num+1)), 'Color': colornum})
			sq_UColorSet.c_defset.append({'Name': to_wide_string("Color %i"%int(num+1)), 'Color': colornum})
		seq_engineroot.additional_attributes['EvCo'] = sq_UColorSet

		tracklist = seq_engineroot.node
		tracklist.domain.set_period(1)

		playrange_track = tracklist.add_track('MPlayRangeTrackEvent')
		playrange_track.spread_counter(counter_id)
		playrange_track.length = project_dur
		playrange_track_node = playrange_track.node
		playrange_track_node.name = to_wide_string("Arranger Track")
		playrange_track_node.domain.set_sync(id_trk_bpm, id_trk_meas)
		playrange_track.additional_attributes = {"TLID": 2, "FixH": 32, "THid": 1}
		playrange_track.track_device.connection_type = 2
		playrange_track_po_list = playrange_track.po_listbase
		add_list_genid(playrange_track_po_list, 'MPlayOrderList', counter_id).po_listname = to_wide_string("Arranger Chain 1")
		for x in range(15):
			add_list_genid(playrange_track_po_list, 'MPlayOrderList', counter_id).po_listname = to_wide_string("Play Order List %s" % (x+2))

		if len(convproj_obj.arranger):
			sortarr = dict([[x.position, x] for x in convproj_obj.arranger])
			sortarr = [sortarr[x] for x in sorted(list(sortarr))]

			for arr_obj in sortarr:
				arrevent = add_list_genid(playrange_track.node.events, 'MPlayRangeEvent', counter_id)
				arrevent.flags = 8960 
				arrevent.start = arr_obj.time.get_pos()
				arrevent.length = arr_obj.time.get_dur()
				if arr_obj.visual.name: arrevent.name = arr_obj.visual.name 
				do_color(arr_obj.visual, total_colors, arrevent.additional_attributes)

		if dawvert_intent.output_mode == 'file':
			namet = dawvert_intent.output_visname
			os.makedirs(os.path.join(dawvert_intent.output_folder, namet), exist_ok=True)
			os.makedirs(os.path.join(dawvert_intent.output_folder, namet, 'Audio'), exist_ok=True)

		returnids = {}
		used_paths = {}
		used_audio = []

		master_returns = convproj_obj.track_master.returns
		for num, rd in enumerate(master_returns.items()):
			returnid, return_obj = rd
			return_track = tracklist.add_track('MDeviceTrackEvent')
			return_track.flags = 32
			return_track.length = project_dur

			return_track.spread_counter(counter_id)
			return_track_node = return_track.node
			if return_obj.visual.name: return_track_node.name = to_wide_string(return_obj.visual.name)
			return_track_node.domain.set_sync(id_trk_bpm, id_trk_meas)

			return_track.additional_attributes['TLID'] = 1
			return_track.additional_attributes['THid'] = 1
			returntrack_device = return_track.track_device
			returntrack_device.connection_type = 1
			returntrack_device.device_name = "VST Multitrack"
			returntrack_device.channel_id = 5

			return_track.height = 74

			deviceattributes = returntrack_device.deviceattributes
			deviceattributes['Name'] = {'String': to_wide_string(return_obj.visual.name if return_obj.visual.name else 'untitled')}
			deviceattributes['Type'] = 6
			deviceattributes['InputGain'] = {'Value': 16383.5}
			deviceattributes['InputPhase'] = 0
			deviceattributes['Volume'] = {'Value': float(calc_volume(return_obj.params.get('vol', 1).value)), 'AnchorValue': 0.0}
			deviceattributes['hasAudioInserts'] = 1
			deviceattributes['InsertFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
			make_blank_slots(3, deviceattributes['InsertFolder']['Slot'])
			deviceattributes['EQPosition'] = 0
			deviceattributes['hasEQ'] = 0
			deviceattributes['EQ'] = {}

			pandata = {}
			pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
			pandata['PannerType'] = {'Value': 2, 'Min': 0, 'Max': 11}
			pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
			pandata['Plugin Name'] = to_wide_string('Panner')
			pandata['Audio Input Count'] = 1
			pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
			pandata['Audio Output Count'] = 1
			pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
			pandata['Event Input Count'] = 0
			pandata['Event Output Count'] = 0
			ebrw_writestr = easybinrw.binwrite()
			ebrw_writestr.float(calc_pan(return_obj.params.get('pan', 0).value))
			ebrw_writestr.float(0.5)
			ebrw_writestr.int_u32(4)
			ebrw_writestr.int_u32(2)
			ebrw_writestr.int_u32(0)
			pandata['audioComponent'] = ebrw_writestr.getvalue()
			pandata['editController'] = b''
			pandata['Active'] = 1
			pandata['IDString'] = to_wide_string('Panner')
			pandata['Bay Program'] = to_wide_string('')
			deviceattributes['Panner'] = pandata
			deviceattributes['VUSelect'] = 1
			deviceattributes['VURange'] = 0
			deviceattributes['Monitor'] = {'Value': 0, 'Min': 0, 'Max': 2}
			returnnum = returnnum_id.get()
			returnids[returnid] = returnnum
			deviceattributes['OwnInputBus'] = {'Name': to_wide_string('FxBus'), 'Bus UID': returnnum, 'Bus Type': 17, 'Input Arrangement': {'Type': sequel_list_int([1, 2])}, 'Output Arrangement': {'Type': sequel_list_int([1, 2])}}
			deviceattributes['InputBusValue'] = {'Value': 0}
			deviceattributes['OutputBusValue'] = {'Value': 5}
			deviceattributes['FreezePosition'] = 2
			deviceattributes['Listen Mode'] = 0
			deviceattributes['LinkedPanner'] = 0
			deviceattributes['IDString'] = to_norm_string('FxChannel'+(' '+str(num+1) if num else ' '))

			return_automation = return_track.automation
			return_automation.name = to_wide_string('Automation')
			return_automation.domain.set_sync(id_trk_bpm, id_trk_meas)
			instautodev = return_automation.track_device = proj_sequel.class_MAutomationTrack()
			instautodev.idnum = counter_id.get()
			instautodev.connection_type = 2
			instautodev.read = 0
			instautodev.write = 0

		#transpose_track = tracklist.add_track('MTransposeTrackEvent')
		#transpose_track.spread_counter(counter_id)
		#transpose_track.flags = 32
		#transpose_track.length = project_dur
		#transpose_track_node = transpose_track.node
		#transpose_track_node.name = to_wide_string("Transpose Track")
		#transpose_track_node.domain.set_sync(id_trk_bpm, id_trk_meas)
		#transpose_track.additional_attributes = {"TLID": 2, "FixH": 32}
		#transpose_track.track_device.connection_type = 2

		for trackid, track_obj in convproj_obj.track__iter():
			if track_obj.type == 'instrument' and not DEBUG_DISABLE_INST_TRACK:
				instrument_track = tracklist.add_track('MInstrumentTrackEvent')
				instrument_track.spread_counter(counter_id)
				instrument_track_node = instrument_track.node
				if track_obj.visual.name: instrument_track_node.name = to_wide_string(track_obj.visual.name)
				do_color(track_obj.visual, total_colors, instrument_track.additional_attributes)
				instrument_track_node.domain.set_sync(id_trk_bpm, id_trk_meas)
				instrument_track_device = instrument_track.track_device
				instrument_track_device.connection_type = 1
				instrument_track_device.channel_id = 8
				instrument_track_device.device_name = to_norm_string('VST Multitrack')

				instrument_track.height = 74

				track_obj.placements.pl_midi.sort()
				for midipl_obj in track_obj.placements.pl_midi:
					midipart = add_list_genid(instrument_track_node.events, 'MMidiPartEvent', counter_id)
					time_obj = midipl_obj.time
					midipart.start, midipart.length = time_obj.get_posdur()
					midipart.offset = time_obj.get_offset()
					midipart.transpose = int(midipl_obj.pitch)

					seq_MMidiPart = proj_sequel.class_MMidiPart()
					midipart.node_idnum = seq_MMidiPart.idnum = counter_id.get()
					project_obj.objects[seq_MMidiPart.idnum] = seq_MMidiPart
					seq_MMidiPart.domain.set_sync(id_trk_bpm, id_trk_meas)
					if midipl_obj.visual.name: seq_MMidiPart.name = to_wide_string(midipl_obj.visual.name)
					do_color(midipl_obj.visual, total_colors, midipart.additional_attributes)

					midievents_obj = midipl_obj.midievents
					midievents_obj.change_ppq(480)
					midievents_obj.sort()
					midievents_obj.add_note_durs()
					midievents_obj.sort()
					for x in midievents_obj.iter_events():
						etype = x[1]
						if etype == 'NOTE_DUR':
							midinote = add_list_genid(seq_MMidiPart.events, 'MMidiNote', counter_id)
							midinote.start = int(x['pos'])
							midinote.data1 = int(x['val1'])
							midinote.data2 = int(x['val2'])
							midinote.flags = 512
							midinote.length = int(x['val3'])
							midinote.data3 = int(x['off_vel'])
						elif etype == 'CONTROL':
							midictrl = add_list_genid(seq_MMidiPart.events, 'MMidiController', counter_id)
							midictrl.start = x['pos']
							midictrl.data1 = int(x['val1'])
							midictrl.data2 = int(x['val2'])
							midictrl.flags = 512
						elif etype == 'PITCH':
							outpitch = int(x[3])+8192
							midictrl = add_list_genid(seq_MMidiPart.events, 'MMidiPitchBend', counter_id)
							midictrl.start = int(x['pos'])
							midictrl.data2 = outpitch>>7
							midictrl.data1 = outpitch%128
							midictrl.flags = 512
						elif etype == 'PRESSURE':
							midictrl = add_list_genid(seq_MMidiPart.events, 'MMidiAfterTouch', counter_id)
							midictrl.start = x['pos']
							midictrl.data1 = int(x['val1'])
							midictrl.flags = 512

					seq_MGridQuantize = proj_sequel.class_MGridQuantize()
					midipart.quantize = seq_MGridQuantize.idnum = counter_id.get()
					project_obj.objects[seq_MGridQuantize.idnum] = seq_MGridQuantize

				deviceattributes = instrument_track_device.deviceattributes
				deviceattributes['Name'] = {'String': to_wide_string(track_obj.visual.name if track_obj.visual.name else 'untitled')}
				deviceattributes['Type'] = 4
				deviceattributes['InputGain'] = {'Value': 16383.5}
				deviceattributes['InputPhase'] = 0
				deviceattributes['Volume'] = {'Value': float(calc_volume(track_obj.params.get('vol', 1).value)), 'AnchorValue': 0.0}
				deviceattributes['hasAudioInserts'] = 1
				deviceattributes['InsertFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
				deviceattributes['EQPosition'] = 0
				deviceattributes['hasEQ'] = 0
				deviceattributes['EQ'] = {}
				deviceattributes['SendFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
				pandata = {}
				pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
				pandata['PannerType'] = {'Value': 2, 'Min': 0, 'Max': 11}
				pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
				pandata['Plugin Name'] = to_wide_string('Panner')
				pandata['Audio Input Count'] = 1
				pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
				pandata['Audio Output Count'] = 1
				pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
				pandata['Event Input Count'] = 0
				pandata['Event Output Count'] = 0
				ebrw_writestr = easybinrw.binwrite()
				ebrw_writestr.float(calc_pan(track_obj.params.get('pan', 0).value))
				ebrw_writestr.float(0.5)
				ebrw_writestr.int_u32(4)
				ebrw_writestr.int_u32(2)
				ebrw_writestr.int_u32(0)
				pandata['audioComponent'] = ebrw_writestr.getvalue()
				pandata['editController'] = b''
				pandata['Active'] = 1
				pandata['IDString'] = to_wide_string('Panner')
				pandata['Bay Program'] = to_wide_string('')
				deviceattributes['Panner'] = pandata
				deviceattributes['VUSelect'] = 1
				deviceattributes['VURange'] = 0
				deviceattributes['Monitor'] = {'Value': 0, 'Min': 0, 'Max': 2}
				deviceattributes['OwnInputBus'] = {'Name': to_wide_string('SynthChannel'), 'Bus UID': inbusnum_id.get(), 'Bus Type': 15, 'Input Arrangement': {'Type': sequel_list_int([1, 2])}, 'Output Arrangement': {'Type': sequel_list_int([1, 2])}}
				deviceattributes['InputBusValue'] = {'Value': 0}
				deviceattributes['OutputBusValue'] = {'Value': 5}
				deviceattributes['FreezePosition'] = 2
				deviceattributes['Listen Mode'] = 0
				deviceattributes['LinkedPanner'] = 0
				deviceattributes['IDString'] = to_norm_string('Instrument')

				# ---------------------------------- Midi Channel ----------------------------------
				deviceatt_midichan = deviceattributes['Midi Channel'] = {}
				deviceatt_midichan["DeviceNode Name"] = to_wide_string("MIDI Channel")
				deviceatt_midichan["ClassName"] = to_norm_string("MidiChannel")
				deviceatt_midichan["IDString"] = to_norm_string("MidiChannel")
				deviceatt_midichan["NodeFlags"] = 8
				deviceatt_midichan["NumberClassIDs"] = 2
				deviceatt_midichan["ClassIDs"] = sequel_list_string([to_norm_string('AB9705CD467B4D7A946C8860C504F492'), to_norm_string('CA1729D088FC4857937F78CC37D45B48')])

				# ---------------------------------- MIDI Inserts ----------------------------------
				deviceatt_midiinsert = deviceatt_midichan['MidiInsertFolder'] = {}
				deviceatt_midiinsert['hasMidiInserts'] = 1
				deviceatt_midiinsert['Bypass Inserts'] = 0
				deviceatt_l_midiinserts = deviceatt_midiinsert['Midi Inserts'] = sequel_list_obj()

				# ---------------------------------- TrackParaEffect ----------------------------------
				trackparam = proj_sequel.class_TrackParaEffect()
				trackparam.idnum = counter_id.get()
				trackparam.name = to_norm_string("Track FX")
				trackparam.index = 0
				peventreader = proj_sequel.class_PEventReader()
				peventreader.idnum = counter_id.get()
				trackparam.inputs.setvals([peventreader])
				pduplicator = proj_sequel.class_PDuplicator()
				pduplicator.idnum = counter_id.get()
				trackparam.outputs.setvals([pduplicator])
				trackparam.transpose.set_vals(0, -127, 127)
				trackparam.velocity_shift.set_vals(0, -126, 126)
				trackparam.delay.set_vals(0, -50, 50)
				trackparam.length_compression.set_vals(65537, 0, 100)
				trackparam.velocity_compression.set_vals(65537, 0, 100)
				trackparam.channelizer.set_vals(0, -1, 15)
				trackparam.scale.set_vals(27, 0, 27)
				trackparam.scale_note.set_vals(0, 0, 11)
				deviceatt_l_midiinserts.append(trackparam)

				for x in range(5):
					midieffectslot = proj_sequel.class_PMidiEffectBase()
					midieffectslot.idnum = counter_id.get()
					midieffectslot.name = to_norm_string("No Effect")
					midieffectslot.index = x+1
					peventreader = proj_sequel.class_PEventReader()
					peventreader.idnum = counter_id.get()
					midieffectslot.inputs.setvals([peventreader])
					pduplicator = proj_sequel.class_PDuplicator()
					pduplicator.idnum = counter_id.get()
					midieffectslot.outputs.setvals([pduplicator])
					deviceatt_l_midiinserts.append(midieffectslot)

				deviceatt_midiinsert['InsertOnOffMask'] = 1

				deviceatt_midichan['SendOnOffMask'] = 0
				deviceatt_midichan['SendPreMask'] = 0
				deviceatt_midichan['Bypass Sends'] = 0
				deviceatt_intrans = deviceatt_midichan['InputTransform'] = {}

				deviceatt_intrans["NumberOfTransformers"] = 4
				deviceatt_intrans["Active@"] = 0
				deviceatt_intrans["Selected@"] = 1
				deviceatt_intrans["LogPreset@"] = logpreset_def
				deviceatt_intrans["ActiveA"] = 0
				deviceatt_intrans["SelectedA"] = 0
				deviceatt_intrans["LogPresetA"] = logpreset_def
				deviceatt_intrans["ActiveB"] = 0
				deviceatt_intrans["SelectedB"] = 0
				deviceatt_intrans["LogPresetB"] = logpreset_def
				deviceatt_intrans["ActiveC"] = 0
				deviceatt_intrans["SelectedC"] = 0
				deviceatt_intrans["LogPresetC"] = logpreset_def
				deviceatt_intrans["ActivePreset"] = 0

				deviceatt_midichan['Volume'] = {'Value': -1.0, 'AnchorValue': 0.0}
				deviceatt_midichan['Pan'] = {'Value': -64, 'Min': -64, 'Max': 64}

				deviceatt_midichan['Splitter1'] = proj_sequel.obj_pointer()
				midieffectslot = proj_sequel.class_PMidiEffectBase()
				midieffectslot.idnum = counter_id.get()
				midieffectslot.isinsert = 0
				deviceatt_midichan['Splitter1'].idnum = midieffectslot.idnum
				midieffectslot.name = to_norm_string("Splitter1")
				peventreader = proj_sequel.class_PEventReader()
				peventreader.idnum = counter_id.get()
				midieffectslot.inputs.setvals([peventreader])
				pduplicator = proj_sequel.class_PDuplicator()
				pduplicator.idnum = counter_id.get()
				midieffectslot.outputs.setvals([pduplicator])
				project_obj.objects[midieffectslot.idnum] = midieffectslot

				deviceatt_midichan['Splitter2'] = proj_sequel.obj_pointer()
				midieffectslot = proj_sequel.class_PMidiEffectBase()
				midieffectslot.idnum = counter_id.get()
				midieffectslot.isinsert = 0
				deviceatt_midichan['Splitter2'].idnum = midieffectslot.idnum
				midieffectslot.name = to_norm_string("Splitter2")
				peventreader = proj_sequel.class_PEventReader()
				peventreader.idnum = counter_id.get()
				midieffectslot.inputs.setvals([peventreader])
				pduplicator = proj_sequel.class_PDuplicator()
				pduplicator.idnum = counter_id.get()
				midieffectslot.outputs.setvals([pduplicator])
				project_obj.objects[midieffectslot.idnum] = midieffectslot

				deviceatt_midisends = deviceatt_midichan['Midi Sends'] = sequel_list_obj()
				for x in range(4):
					midieffectslot = proj_sequel.class_PMidiEffectBase()
					midieffectslot.idnum = counter_id.get()
					midieffectslot.name = to_norm_string("No Effect")
					midieffectslot.index = x
					midieffectslot.isinsert = 0
					peventreader = proj_sequel.class_PEventReader()
					peventreader.idnum = counter_id.get()
					midieffectslot.inputs.setvals([peventreader])
					pextendedduplicator = proj_sequel.class_PExtendedDuplicator()
					pextendedduplicator.idnum = counter_id.get()
					midieffectslot.outputs.setvals([pextendedduplicator])
					deviceatt_midisends.append(midieffectslot)

				deviceatt_midichan["Midi Send Channel"] = sequel_list_int([0,0,0,0])
				deviceatt_midichan["Device"] = to_wide_string("")
				deviceatt_midichan["Port"] = to_wide_string("")
				deviceatt_midichan["inputTransformerSource"] = {'Value': 0, 'Min': 0, 'Max': 2}
				deviceatt_midichan["IdString"] = to_norm_string("MidiChannel")
				deviceatt_midichan["Monitor"] = 0

				deviceattributes["hasVSTi"] = 1
				deviceatt_synthslot = deviceattributes["Synth Slot"] = {}
				deviceatt_synthslot["State"] = 0

				instrument_track_device.input_type = 3
				instrument_track_device.input_device_id = to_norm_string('All MIDI Inputs')
				instrument_track_device.input_channel_id = 2
				instrument_track_device.input_port_name = to_norm_string('All MIDI Inputs')

				instrument_automation = instrument_track.automation
				instrument_automation.name = to_wide_string('Automation')
				instrument_automation.domain.set_sync(id_trk_bpm, id_trk_meas)
				instautodev = instrument_automation.track_device = proj_sequel.class_MAutomationTrack()
				instautodev.idnum = counter_id.get()
				instautodev.connection_type = 2
				instautodev.read = 1
				instautodev.write = 0

				for returnid, return_obj in master_returns.items():
					senddata = {}
					senddata['Volume'] = {'Value': float(18688), 'AnchorValue': 0.0}
					senddata['Output'] = {'Value': returnids[returnid]}
					pandata = {}
					pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
					pandata['PannerType'] = {'Value': 2, 'Min': 0, 'Max': 11}
					pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
					pandata['Plugin Name'] = to_wide_string('Panner')
					pandata['Audio Input Count'] = 1
					pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
					pandata['Audio Output Count'] = 1
					pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
					pandata['Event Input Count'] = 0
					pandata['Event Output Count'] = 0
					ebrw_writestr = easybinrw.binwrite()
					ebrw_writestr.float(0.5)
					ebrw_writestr.float(0.5)
					ebrw_writestr.int_u32(1)
					ebrw_writestr.int_u32(2)
					ebrw_writestr.int_u32(0)
					pandata['audioComponent'] = ebrw_writestr.getvalue()
					pandata['editController'] = b''
					pandata['Active'] = 1
					pandata['IDString'] = to_wide_string('Panner')
					pandata['Bay Program'] = to_wide_string('')
					senddata['Panner'] = pandata
					deviceattributes['SendFolder']['Slot'].append(senddata)

			if track_obj.type == 'audio' and not DEBUG_DISABLE_AUDIO_TRACK:
				audio_track = tracklist.add_track('MAudioTrackEvent')
				audio_track.spread_counter(counter_id)
				audio_track_node = audio_track.node
				if track_obj.visual.name: audio_track_node.name = to_wide_string(track_obj.visual.name)
				do_color(track_obj.visual, total_colors, audio_track.additional_attributes)
				audio_track_node.domain.set_sync(id_trk_bpm, id_trk_meas)

				audio_track.additional_attributes['TLID'] = 0
				audiotrack_device = audio_track.track_device
				audiotrack_device.connection_type = 1
				audiotrack_device.device_name = "VST Multitrack"
				audiotrack_device.channel_id = 1

				audio_track.height = 74

				deviceattributes = audiotrack_device.deviceattributes
				deviceattributes['Name'] = {'String': to_wide_string(track_obj.visual.name if track_obj.visual.name else 'untitled')}
				deviceattributes['Type'] = 1
				deviceattributes['InputGain'] = {'Value': 16383.5}
				deviceattributes['InputPhase'] = 0
				deviceattributes['Volume'] = {'Value': float(calc_volume(track_obj.params.get('vol', 1).value)), 'AnchorValue': 0.0}
				deviceattributes['hasAudioInserts'] = 1
				deviceattributes['InsertFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
				make_blank_slots(3, deviceattributes['InsertFolder']['Slot'])
				deviceattributes['EQPosition'] = 0
				deviceattributes['hasEQ'] = 0
				deviceattributes['EQ'] = {}
				deviceattributes['SendFolder'] = {'Bypass': 0, 'SeparationPosition': 0, 'Slot': sequel_list_dict([])}
				pandata = {}
				pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
				pandata['PannerType'] = {'Value': 4, 'Min': 0, 'Max': 11}
				pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
				pandata['Plugin Name'] = to_wide_string('Panner')
				pandata['Audio Input Count'] = 1
				pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
				pandata['Audio Output Count'] = 1
				pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
				pandata['Event Input Count'] = 0
				pandata['Event Output Count'] = 0
				ebrw_writestr = easybinrw.binwrite()
				ebrw_writestr.float(calc_pan(track_obj.params.get('pan', 0).value))
				ebrw_writestr.float(0.5)
				ebrw_writestr.int_u32(4)
				ebrw_writestr.int_u32(2)
				ebrw_writestr.int_u32(0)
				pandata['audioComponent'] = ebrw_writestr.getvalue()
				pandata['editController'] = b''
				pandata['Active'] = 1
				pandata['IDString'] = to_wide_string('Panner')
				pandata['Bay Program'] = to_wide_string('')
				deviceattributes['Panner'] = pandata
				deviceattributes['VUSelect'] = 1
				deviceattributes['VURange'] = 0
				deviceattributes['Monitor'] = {'Value': 0, 'Min': 0, 'Max': 2}
				deviceattributes['OwnInputBus'] = {'Name': to_norm_string('Audio'), 'Bus UID': inbusnum_id.get(), 'Bus Type': 13, 'Input Arrangement': {'Type': sequel_list_int([1, 2])}, 'Output Arrangement': {'Type': sequel_list_int([1, 2])}}
				deviceattributes['InputBusValue'] = {'Value': 0}
				deviceattributes['OutputBusValue'] = {'Value': 5}
				deviceattributes['FreezePosition'] = 2
				deviceattributes['Listen Mode'] = 0
				deviceattributes['LinkedPanner'] = 0
				deviceattributes['IDString'] = to_norm_string('Audio')

				autofade_settings = audio_track.autofade_settings
				autofade_settings.spread_counter(counter_id)
				autofade_settings.init_values()

				track_obj.placements.pl_audio.sort()
				for n, audiopl_obj in enumerate(track_obj.placements.pl_audio):
					sp_obj = audiopl_obj.sample
					reffound, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
					if reffound:

						fileref_obj = sampleref_obj.fileref
	
						if dawvert_intent.output_mode == 'file':
							namet = dawvert_intent.output_visname
							outfile = os.path.join(dawvert_intent.output_folder, namet, 'Audio', str(fileref_obj.file))
							sampleref_obj.copy_resample('win', outfile)

						samp_dur_samples = sampleref_obj.get_dur_samples()
						samp_dur_hz = sampleref_obj.get_hz()
						samp_dur_sec = sampleref_obj.get_dur_sec()
						samp_channels = sampleref_obj.get_channels()

						if samp_dur_samples and samp_dur_hz:
							stretch_obj = sp_obj.stretch
							timing_obj = stretch_obj.timing
	
							audiopart = add_list_genid(audio_track_node.events, 'MAudioEvent', counter_id)
							time_obj = audiopl_obj.time
							audiopart.priority = n+2
	
							if sp_obj.vol != 1: audiopart.volume = sp_obj.vol
							if audiopl_obj.muted: audiopart.flags = 2
		
							seq_PAudioClip = proj_sequel.class_PAudioClip()
							audiopart.clip_idnum = seq_PAudioClip.idnum = counter_id.get()
							project_obj.objects[seq_PAudioClip.idnum] = seq_PAudioClip
							if audiopl_obj.visual.name: seq_PAudioClip.name = to_wide_string(audiopl_obj.visual.name)
							do_color(audiopl_obj.visual, total_colors, audiopart.additional_attributes)
							if sp_obj.pitch: audiopart.additional_attributes['PitF'] = xtramath.pitch_to_speed(sp_obj.pitch)

							stretch_algo = stretch_obj.algorithm

							ElastiquePreset_obj = seq_PAudioClip.additional_attributes['StretchPreset'] = proj_sequel.class_ElastiquePreset()
							ElastiquePreset_obj.processingmode = 'pro default'
							ElastiquePreset_obj.stereomode = 'left-right'
							ElastiquePreset_obj.formantpreservation = int(bool(stretch_algo.preserve_formants))
							ElastiquePreset_obj.tapestylemode = int(not stretch_obj.preserve_pitch)
							ElastiquePreset_obj.pitchaccuratemode = 1
							ElastiquePreset_obj.idnum = counter_id.get()

							audiopath = seq_PAudioClip.path
							audiopath.idnum = counter_id.get()
							audiopath.name = str(fileref_obj.file)
							audiopath.path = '\\'.join(fileref_obj.folder.getpath('win'))+'\\'

							#print(fileref_obj.get_path(None, 0))
	
							audiopart.start, audiopart.length = time_obj.get_posdur()
							audiopart.offset = time_obj.get_offset()
							seq_PAudioClip.domain.set_sync(id_trk_bpm, id_trk_meas)

							subtree_part = add_list_genid(subtree_audio.subentries, 'GTreeEntry', counter_id)
							subtree_part.dataobject = seq_PAudioClip.idnum
							subtree_part.name = to_wide_string(str(fileref_obj.file.filename))
							subtree_part.flags = 611
							subtree_part.v_id = len(subtree_audio.subentries)
	
							#if fileref_obj not in used_paths:
	
							used_paths[fileref_obj] = audiopath.idnum
							fileext = fileref_obj.file.extension
							if fileext == 'wav': audiopath.filetype = {"MacType": 1463899717, "DosType": to_wide_string("wav"), "UnixType": to_wide_string("wav"), "Name": to_wide_string("Wave File")}
							if fileext == 'ogg': audiopath.filetype = {"MacType": 1332176726, "DosType": to_wide_string("ogg"), "Name": to_wide_string("OggVorbis File")}
							#else:
							#	seq_PAudioClip.path = proj_sequel.obj_pointer()
							#	seq_PAudioClip.path.idnum = used_paths[fileref_obj]
	
							clipattrib = seq_PAudioClip.additional_attributes
							clipattrib['Grain Size'] = 1740
							clipattrib['TransposeLock'] = int(bool(not sp_obj.usemasterpitch))

							GridDef = clipattrib['GridDef'] = proj_sequel.class_PGridDefinition()
							GridDef.idnum = counter_id.get()
							GridDef.tempo = bpm
							GridDef.offsettempo = bpm
	
							clipattrib['Stretch Preset'] = 4
							clipattrib['Warp Overlap'] = 0.14
							clipattrib['Warp Variance'] = 1.0
							AudioWarpScale = clipattrib['Warpscale'] = proj_sequel.class_PAudioWarpScale()
							AudioWarpScale.idnum = counter_id.get()
							add_list_genid(AudioWarpScale.warptab, 'PWarpTab', counter_id)
							warptab = add_list_genid(AudioWarpScale.warptab, 'PWarpTab', counter_id)
							warptab.position = samp_dur_samples
	
							speed = timing_obj.get__speed(sampleref_obj)
							warptab.warped = (samp_dur_sec*2*timebase)*speed

							if timing_obj.time_type=='speed': audiopart.offset *= speed

							clipattrib['unStretch'] = 0
	
							audiocluster = seq_PAudioClip.cluster
							audiocluster.idnum = counter_id.get()
	
							audiofile = add_list_genid(audiocluster.substreams, 'AudioFile', counter_id)
							audiofile.fpath = proj_sequel.obj_pointer()
							audiofile.fpath.idnum = audiopath.idnum
	
							audiofile.framecount = samp_dur_samples
							audiofile.sample_size = 16
							audiofile.frame_size = 4
							#audiofile.channels = sampleref_obj.get_channels()
							audiofile.rate = samp_dur_hz
							audiofile.format = 65536
							audiofile.byteorder = 0
							audiofile.dataoffset = 44
							if samp_channels is not None:
								if samp_channels>1:
									audiofile.speakerarr = {'Type': sequel_list_int([x+1 for x in range(samp_channels)])}
	
							segment = {}
							segment["Stream"] = proj_sequel.obj_pointer()
							segment["Stream"].idnum = audiofile.idnum
							segment["Offset"] = 0
							segment["Length"] = samp_dur_samples
							segment["Start"] = 0
							audiocluster.segments.setvals([segment])

				for returnid, return_obj in master_returns.items():
					senddata = {}
					senddata['Volume'] = {'Value': float(18688), 'AnchorValue': 0.0}
					senddata['Output'] = {'Value': returnids[returnid]}
					pandata = {}
					pandata['Default SurroundPan UID'] = {'GUID': to_wide_string('56535453506132737572726F756E6470')}
					pandata['PannerType'] = {'Value': 2, 'Min': 0, 'Max': 11}
					pandata['Plugin UID'] = {'GUID': to_wide_string('44E1149EDB3E4387BDD827FEA3A39EE7')}
					pandata['Plugin Name'] = to_wide_string('Panner')
					pandata['Audio Input Count'] = 1
					pandata['Audio Input Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
					pandata['Audio Output Count'] = 1
					pandata['Audio Output Arrangement'] = sequel_list_dict([{'Type': sequel_list_int([1, 2])}])
					pandata['Event Input Count'] = 0
					pandata['Event Output Count'] = 0
					ebrw_writestr = easybinrw.binwrite()
					ebrw_writestr.float(0.5)
					ebrw_writestr.float(0.5)
					ebrw_writestr.int_u32(1)
					ebrw_writestr.int_u32(2)
					ebrw_writestr.int_u32(0)
					pandata['audioComponent'] = ebrw_writestr.getvalue()
					pandata['editController'] = b''
					pandata['Active'] = 1
					pandata['IDString'] = to_wide_string('Panner')
					pandata['Bay Program'] = to_wide_string('')
					senddata['Panner'] = pandata
					deviceattributes['SendFolder']['Slot'].append(senddata)

				audio_automation = audio_track.automation
				audio_automation.name = to_wide_string('Automation')
				audio_automation.domain.set_sync(id_trk_bpm, id_trk_meas)
				autotrack = add_list_genid(audio_automation.tracks, 'MAutomationTrackEvent', counter_id)
				autotrack.flags = 2
				autotrack.length = project_dur
				autotrack.tag = 1025
				autotrack.node.idnum = counter_id.get()
				autotrack.track_device.idnum = counter_id.get()
				audio_automation.track_device.idnum = autotrack.track_device.idnum

				mautolistnode = proj_sequel.class_MAutoListNode()
				mautolistnode.idnum = autotrack.node.idnum
				mautolistnode.domain.set_sync(id_trk_bpm, id_trk_meas)
				project_obj.objects[mautolistnode.idnum] = mautolistnode

				mautotrack = proj_sequel.class_MAutomationTrack()
				mautotrack.idnum = audio_automation.track_device.idnum
				mautotrack.connection_type = 2
				mautotrack.read = 1
				mautotrack.write = 0
				project_obj.objects[mautotrack.idnum] = mautotrack


		for num, colordata in enumerate(total_colors):
			colordata = decode_color(colordata)
			sq_UColorSet.c_set.append({'Name': to_wide_string("Color %i"%int(num+1)), 'Color': colordata})

		if dawvert_intent.output_mode == 'file':
			namet = dawvert_intent.output_visname
			outfile = os.path.join(dawvert_intent.output_folder, namet, os.path.basename(dawvert_intent.output_file))
			project_obj.save_to_file(outfile)
