# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import colors
from functions import audio
from functions import data_values
from functions import placement_data
from functions import plugins
from functions import song
from functions_plugin import ableton_values

import base64
import xml.etree.ElementTree as ET
import plugin_input
import json
import gzip
import math

colorlist = ['FF94A6','FFA529','CC9927','F7F47C','BFFB00','1AFF2F','25FFA8','5CFFE8','8BC5FF','5480E4','92A7FF','D86CE4','E553A0','FFFFFF','FF3636','F66C03','99724B','FFF034','87FF67','3DC300','00BFAF','19E9FF','10A4EE','007DC0','886CE4','B677C6','FF39D4','D0D0D0','E2675A','FFA374','D3AD71','EDFFAE','D2E498','BAD074','9BC48D','D4FDE1','CDF1F8','B9C1E3','CDBBE4','AE98E5','E5DCE1','A9A9A9','C6928B','B78256','99836A','BFBA69','A6BE00','7DB04D','88C2BA','9BB3C4','85A5C2','8393CC','A595B5','BF9FBE','BC7196','7B7B7B','AF3333','A95131','724F41','DBC300','85961F','539F31','0A9C8E','236384','1A2F96','2F52A2','624BAD','A34BAD','CC2E6E','3C3C3C']
colorlist_one = [colors.hex_to_rgb_float(color) for color in colorlist]

def get_value(xmldata, varname, fallback): 
	if len(xmldata.findall(varname)) != 0:
		xml_e = xmldata.findall(varname)[0]
		return xml_e.get('Value')
	else:
		return fallback

def get_id(xmldata, varname, fallback): 
	if len(xmldata.findall(varname)) != 0:
		xml_e = xmldata.findall(varname)[0]
		return xml_e.get('Id')


def use_valuetype(i_valtype, i_value): 
	if i_valtype == 'string': return str(i_value)
	if i_valtype == 'float': return float(i_value)
	if i_valtype == 'int': return int(i_value)
	if i_valtype == 'bool': return ['false','true'].index(i_value)

def get_param(xmldata, varname, vartype, fallback, i_loc, i_addmul): 
	if len(xmldata.findall(varname)) != 0:
		param_data = xmldata.findall(varname)[0]
		out_value = get_value(param_data, 'Manual', fallback)
		autonumid = int(get_id(param_data, 'AutomationTarget', None))
		outdata = use_valuetype(vartype, out_value)
		if autonumid != None:
			tracks.autoid_in_define(autonumid, i_loc, vartype, i_addmul)
		return outdata
	else:
		return fallback

def get_sampleref(xmldata):
	x_sampleref = xmldata.findall('SampleRef')[0]
	x_fileref = x_sampleref.findall('FileRef')[0]
	out_data = {}
	out_data['file'] = get_value(x_fileref, 'Path', '')
	out_data['samples'] = float(get_value(x_sampleref, 'DefaultDuration', 1))
	out_data['rate'] = float(get_value(x_sampleref, 'DefaultSampleRate', 1))
	out_data['seconds'] = out_data['samples'] / out_data['rate']
	return out_data

def get_auto(x_track_data): 
	track_AutomationEnvelopes = x_track_data.findall('AutomationEnvelopes')[0]
	track_Envelopes = track_AutomationEnvelopes.findall('Envelopes')[0]
	for AutomationEnvelope in track_Envelopes.findall('AutomationEnvelope'):
		env_EnvelopeTarget = AutomationEnvelope.findall('EnvelopeTarget')[0]
		env_Automation = AutomationEnvelope.findall('Automation')[0]
		env_AutoEvents = env_Automation.findall('Events')[0]
		autotarget = int(get_value(env_EnvelopeTarget, 'PointeeId', None))

		cvpj_autopoints = []
		for env_AutoEvent in env_AutoEvents:
			if env_AutoEvent.tag == 'FloatEvent':
				cvpj_autopoints.append({
					"position": max(0,float(env_AutoEvent.get('Time'))*4), 
					"value": float(env_AutoEvent.get('Value'))
					})

		tracks.autoid_in_add_pl(autotarget, tracks.a_auto_nopl_to_pl(cvpj_autopoints))

def get_Range_cross(x_xml, rangename):
	x_range = x_xml.findall(rangename)[0]
	output = []
	output.append(int(get_value(x_range, 'Min', 0)))
	output.append(int(get_value(x_range, 'Max', 127)))
	output.append(int(get_value(x_range, 'CrossfadeMin', 0)))
	output.append(int(get_value(x_range, 'CrossfadeMax', 127)))
	return output

def get_Range(x_xml, rangename):
	rangevalfind = x_xml.findall(rangename)

	if len(rangevalfind) != 0:
		x_range = rangevalfind[0]
		output = []
		output.append(float(get_value(x_range, 'Min', None)))
		output.append(float(get_value(x_range, 'Max', None)))
		return output

def get_MultiSampleMap(x_MultiSampleMap):
	outdata = []
	x_sampleparts = x_MultiSampleMap.findall('SampleParts')[0]
	xs_sampleparts = x_sampleparts.findall('MultiSamplePart')
	for xs_samplepart in xs_sampleparts:
		audiodata = get_sampleref(xs_samplepart)
		t_samppart = {}
		t_samppart['audiodata'] = audiodata
		t_samppart['Name'] = get_value(xs_samplepart, 'Name', '')
		t_samppart['KeyRange'] = get_Range_cross(xs_samplepart, 'KeyRange')
		t_samppart['VelocityRange'] = get_Range_cross(xs_samplepart, 'VelocityRange')
		t_samppart['SelectorRange'] = get_Range_cross(xs_samplepart, 'SelectorRange')
		t_samppart['CrossfadeMin'] = get_value(xs_samplepart, 'CrossfadeMin', 0)
		t_samppart['Detune'] = float(get_value(xs_samplepart, 'Detune', 0))/100
		t_samppart['TuneScale'] = float(get_value(xs_samplepart, 'TuneScale', 0))/100
		t_samppart['Volume'] = float(get_value(xs_samplepart, 'Volume', 1))
		t_samppart['SampleStart'] = float(get_value(xs_samplepart, 'SampleStart', 1))
		t_samppart['SampleEnd'] = float(get_value(xs_samplepart, 'SampleEnd', 1))
		for xmlname, tname in [['SustainLoop', 'loop_sustain'],['ReleaseLoop', 'loop_release']]:
			x_loop = xs_samplepart.findall(xmlname)[0]
			t_samppart[tname] = {}
			t_samppart[tname]['Start'] = int(get_value(x_loop, 'Start', 0))
			t_samppart[tname]['End'] = int(get_value(x_loop, 'End', 0))
			t_samppart[tname]['Mode'] = int(get_value(x_loop, 'Mode', 0))
			t_samppart[tname]['Crossfade'] = float(get_value(x_loop, 'Crossfade', 0))
			t_samppart[tname]['Detune'] = float(get_value(x_loop, 'Detune', 0))/100

		t_samppart_slice = {}
		t_samppart_slice['Threshold'] = int(get_value(xs_samplepart, 'SlicingThreshold', 0))
		t_samppart_slice['BeatGrid'] = int(get_value(xs_samplepart, 'SlicingBeatGrid', 0))
		t_samppart_slice['Regions'] = int(get_value(xs_samplepart, 'SlicingRegions', 0))
		t_samppart_slice['Style'] = int(get_value(xs_samplepart, 'SlicingStyle', 0))
		t_samppart_slice['UseDynamicBeatSlices'] = use_valuetype('bool', get_value(xs_samplepart, 'UseDynamicBeatSlices', 'true'))
		t_samppart_slice['UseDynamicRegionSlices'] = use_valuetype('bool', get_value(xs_samplepart, 'UseDynamicRegionSlices', 'true'))
		t_samppart_slice['Points'] = []

		x_SlicePoints = xs_samplepart.findall('SlicePoints')[0]
		for xs_SlicePoint in x_SlicePoints.findall('SlicePoint'):
			t_slice = {}
			t_slice['TimeInSeconds'] = float(xs_SlicePoint.get('TimeInSeconds'))
			t_slice['Rank'] = float(xs_SlicePoint.get('Rank'))
			t_slice['NormalizedEnergy'] = float(xs_SlicePoint.get('NormalizedEnergy'))
			t_samppart_slice['Points'].append(t_slice)

		outdata.append(t_samppart)
		
		return outdata

def isfloatboolstring(valuedata): 
	if valuedata.replace('.','',1).replace('-','',1).isdigit():
		return 'float'
	elif valuedata in ['true', 'false']:
		return 'bool'
	else:
		return 'string'

lfo_beatsteps = []
for lfo_beatstep in [1/64, 1/48, 1/32, 1/24, 1/16, 1/12, 1/8, 
	1/6, 3/16, 1/4, 5/16, 1/3, 3/8, 1/2, 3/4, 1, 1.5, 2, 3, 4, 6, 8]:
	lfo_beatsteps.append( math.log2(lfo_beatstep) )

class input_ableton(plugin_input.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'ableton'
	def getname(self): return 'Ableton Live 11'
	def gettype(self): return 'r'
	def supported_autodetect(self): return False
	def getdawcapabilities(self): 
		return {
		'placement_cut': True,
		'placement_loop': ['loop', 'loop_off', 'loop_adv'],
		'placement_audio_stretch': ['warp'],
		'auto_nopl': True,
		}
	def parse(self, input_file, extra_param):
		xmlstring = ""

		#_______paramfinder_param = {}
		#_______paramfinder_data = {}

		with open(input_file, 'rb') as alsbytes:
			if alsbytes.read(2) == b'\x1f\x8b': 
				alsbytes.seek(0)
				xmlstring = gzip.decompress(alsbytes.read())
			else:
				alsbytes.seek(0)
				xmlstring = alsbytes.read().decode()

		root = ET.fromstring(xmlstring)

		abletondatadef_params = ableton_values.devicesparam()
		abletondatadef_data = ableton_values.devicesdata()

		abletonversion = root.get('MinorVersion').split('.')[0]
		if abletonversion != '11':
			print('[error] Ableton version '+abletonversion+' is not supported.')
			exit()

		x_LiveSet = root.findall('LiveSet')[0]
		x_Tracks = x_LiveSet.findall('Tracks')[0]
		x_MasterTrack = x_LiveSet.findall('MasterTrack')[0]

		cvpj_l = {}

		x_mastertrack_Name = x_MasterTrack.findall('Name')[0]
		mastertrack_name = get_value(x_mastertrack_Name, 'EffectiveName', '')
		mastertrack_color = colorlist_one[int(get_value(x_MasterTrack, 'Color', 'test'))]
		x_mastertrack_DeviceChain = x_MasterTrack.findall('DeviceChain')[0]
		x_mastertrack_Mixer = x_mastertrack_DeviceChain.findall('Mixer')[0]
		mas_track_vol = get_param(x_mastertrack_Mixer, 'Volume', 'float', 0, ['master', 'vol'], None)
		mas_track_pan = get_param(x_mastertrack_Mixer, 'Pan', 'float', 0, ['master', 'pan'], None)
		tempo = get_param(x_mastertrack_Mixer, 'Tempo', 'float', 140, ['main', 'bpm'], None)
		tracks.a_addtrack_master(cvpj_l, mastertrack_name, mas_track_vol, mastertrack_color)
		song.add_param(cvpj_l, 'bpm', tempo)

		sendnum = 1
		returnid = 1

		for x_track_data in list(x_Tracks):
			tracktype = x_track_data.tag

			x_track_DeviceChain = x_track_data.findall('DeviceChain')[0]
			x_track_Mixer = x_track_DeviceChain.findall('Mixer')[0]

			x_track_Name = x_track_data.findall('Name')[0]

			fxloc = None

			track_id = x_track_data.get('Id')
			track_name = get_value(x_track_Name, 'EffectiveName', '')
			track_color = colorlist_one[int(get_value(x_track_data, 'Color', ''))]

			track_sends = x_track_Mixer.findall('Sends')[0]
			track_sendholders = track_sends.findall('TrackSendHolder')

			if tracktype == 'MidiTrack':
				fxloc = ['track', track_id]
				print('[input-ableton] MIDI: '+track_name+' ['+track_id+']')
				track_vol = get_param(x_track_Mixer, 'Volume', 'float', 0, ['track', track_id, 'vol'], None)
				track_pan = get_param(x_track_Mixer, 'Pan', 'float', 0, ['track', track_id, 'pan'], None)

				tracks.r_create_track(cvpj_l, 'instrument', track_id, name=track_name, color=track_color)
				tracks.r_add_param(cvpj_l, track_id, 'vol', track_vol, 'float')
				tracks.r_add_param(cvpj_l, track_id, 'pan', track_pan, 'float')
				tracks.r_pl_notes(cvpj_l, track_id, [])

				x_track_MainSequencer = x_track_DeviceChain.findall('MainSequencer')[0]
				x_track_ClipTimeable = x_track_MainSequencer.findall('ClipTimeable')[0]
				x_track_ArrangerAutomation = x_track_ClipTimeable.findall('ArrangerAutomation')[0]
				x_track_Events = x_track_ArrangerAutomation.findall('Events')[0]
				x_track_MidiClips = x_track_Events.findall('MidiClip')
				for x_track_MidiClip in x_track_MidiClips:
					note_placement_pos = float(get_value(x_track_MidiClip, 'CurrentStart', 0))*4
					note_placement_dur = float(get_value(x_track_MidiClip, 'CurrentEnd', 0))*4 - note_placement_pos
					note_placement_name = get_value(x_track_MidiClip, 'Name', '')
					note_placement_color = colorlist_one[int(get_value(x_track_MidiClip, 'Color', 0))]
					note_placement_muted = ['false','true'].index(get_value(x_track_MidiClip, 'Disabled', 'false'))

					cvpj_placement = {}
					cvpj_placement['position'] = note_placement_pos
					cvpj_placement['duration'] = note_placement_dur
					cvpj_placement['name'] = note_placement_name
					cvpj_placement['color'] = note_placement_color
					cvpj_placement['muted'] = note_placement_muted

					x_track_MidiClip_loop = x_track_MidiClip.findall('Loop')[0]
					note_placement_loop_l_start = float(get_value(x_track_MidiClip_loop, 'LoopStart', 0))*4
					note_placement_loop_l_end = float(get_value(x_track_MidiClip_loop, 'LoopEnd', 1))*4
					note_placement_loop_start = float(get_value(x_track_MidiClip_loop, 'StartRelative', 0))*4
					note_placement_loop_on = ['false','true'].index(get_value(x_track_MidiClip_loop, 'LoopOn', 'false'))

					if note_placement_loop_on == 1:
						cvpj_placement['cut'] = placement_data.cutloopdata(note_placement_loop_start, note_placement_loop_l_start, note_placement_loop_l_end)
					else:
						cvpj_placement['cut'] = {}
						cvpj_placement['cut']['type'] = 'cut'
						cvpj_placement['cut']['start'] = note_placement_loop_l_start
						cvpj_placement['cut']['end'] = note_placement_loop_l_end

					cvpj_placement['notelist'] = []

					x_track_MidiClip_Notes = x_track_MidiClip.findall('Notes')[0]
					x_track_MidiClip_KT = x_track_MidiClip_Notes.findall('KeyTracks')[0]

					t_notes = {}

					for x_track_MidiClip_KT_KT_s in x_track_MidiClip_KT.findall('KeyTrack'):
						t_ableton_note_key = int(get_value(x_track_MidiClip_KT_KT_s, 'MidiKey', 60))-60
						x_track_MidiClip_KT_KT_Notes = x_track_MidiClip_KT_KT_s.findall('Notes')[0]
						for x_track_MidiClip_MNE in x_track_MidiClip_KT_KT_Notes.findall('MidiNoteEvent'):
							t_note_data = {}
							t_note_data['key'] = t_ableton_note_key
							t_note_data['position'] = float(x_track_MidiClip_MNE.get('Time'))*4
							t_note_data['duration'] = float(x_track_MidiClip_MNE.get('Duration'))*4
							t_note_data['vol'] = float(x_track_MidiClip_MNE.get('Velocity'))/100
							t_note_data['off_vol'] = float(x_track_MidiClip_MNE.get('OffVelocity'))/100
							t_note_data['probability'] = float(x_track_MidiClip_MNE.get('Probability'))
							t_note_data['enabled'] = ['false','true'].index(x_track_MidiClip_MNE.get('IsEnabled'))
							note_id = int(x_track_MidiClip_MNE.get('NoteId'))
							t_notes[note_id] = t_note_data

					x_track_MidiClip_NES = x_track_MidiClip_Notes.findall('PerNoteEventStore')[0]
					x_track_MidiClip_NES_EL = x_track_MidiClip_NES.findall('EventLists')[0]

					for x_note_nevent in x_track_MidiClip_NES_EL.findall('PerNoteEventList'):
						auto_note_id = int(x_note_nevent.get('NoteId'))
						auto_note_cc = int(x_note_nevent.get('CC'))
						t_notes[auto_note_id]['notemod'] = {}
						t_notes[auto_note_id]['notemod']['auto'] = {}

						if auto_note_cc == -2:
							t_notes[auto_note_id]['notemod']['auto']['pitch'] = []
							cvpj_noteauto_pitch = t_notes[auto_note_id]['notemod']['auto']['pitch']
							x_note_nevent_ev = x_note_nevent.findall('Events')[0]

							for ableton_point in x_note_nevent_ev.findall('PerNoteEvent'):
								ap_pos = float(ableton_point.get('TimeOffset'))*4
								ap_val = float(ableton_point.get('Value'))/170
								cvpj_noteauto_pitch.append({'position': ap_pos, 'value': ap_val})

					for t_note in t_notes:
						cvpj_placement['notelist'].append(t_notes[t_note])

					tracks.r_pl_notes(cvpj_l, track_id, cvpj_placement)  

			if tracktype == 'AudioTrack':
				fxloc = ['track', track_id]
				print('[input-ableton] Audio: '+track_name+' ['+track_id+']')
				track_vol = get_param(x_track_Mixer, 'Volume', 'float', 0, ['track', track_id, 'vol'], None)
				track_pan = get_param(x_track_Mixer, 'Pan', 'float', 0, ['track', track_id, 'pan'], None)

				tracks.r_create_track(cvpj_l, 'audio', track_id, name=track_name, color=track_color)
				tracks.r_add_param(cvpj_l, track_id, 'vol', track_vol, 'float')
				tracks.r_add_param(cvpj_l, track_id, 'pan', track_pan, 'float')
				tracks.r_pl_audio(cvpj_l, track_id, [])

				x_track_MainSequencer = x_track_DeviceChain.findall('MainSequencer')[0]
				x_track_Sample = x_track_MainSequencer.findall('Sample')[0]
				x_track_ArrangerAutomation = x_track_Sample.findall('ArrangerAutomation')[0]
				x_track_Events = x_track_ArrangerAutomation.findall('Events')[0]
				x_track_AudioClips = x_track_Events.findall('AudioClip')
				audiorate = 1
				for x_track_AudioClip in x_track_AudioClips:

					t_CurrentStart = float(get_value(x_track_AudioClip, 'CurrentStart', 0))
					t_CurrentEnd = float(get_value(x_track_AudioClip, 'CurrentEnd', 0))

					audio_placement_pos = t_CurrentStart*4
					audio_placement_dur = (t_CurrentEnd-t_CurrentStart)*4
					audio_placement_name = get_value(x_track_AudioClip, 'Name', '')
					audio_placement_color = colorlist_one[int(get_value(x_track_AudioClip, 'Color', 0))]
					audio_placement_muted = ['false','true'].index(get_value(x_track_AudioClip, 'Disabled', 'false'))
					audio_placement_vol = float(get_value(x_track_AudioClip, 'SampleVolume', 0))

					audio_placement_warp_on = ['false','true'].index(get_value(x_track_AudioClip, 'IsWarped', 'false'))
					audio_placement_warp_mode = int(get_value(x_track_AudioClip, 'WarpMode', 0))

					audio_sampleref = get_sampleref(x_track_AudioClip)
					audio_sampleref_steps = audio_sampleref['seconds']*8

					cvpj_placement = {}
					cvpj_placement['position'] = audio_placement_pos
					cvpj_placement['duration'] = audio_placement_dur
					cvpj_placement['name'] = audio_placement_name
					cvpj_placement['color'] = audio_placement_color
					cvpj_placement['muted'] = audio_placement_muted
					cvpj_placement['vol'] = audio_placement_vol

					cvpj_placement['file'] = audio_sampleref['file']
					aud_sampledata = audio.get_audiofile_info(audio_sampleref['file'])

					x_track_AudioClip_loop = x_track_AudioClip.findall('Loop')[0]

					t_LoopStart = float(get_value(x_track_AudioClip_loop, 'LoopStart', 0))
					t_LoopEnd = float(get_value(x_track_AudioClip_loop, 'LoopEnd', 0))
					t_StartRelative = float(get_value(x_track_AudioClip_loop, 'StartRelative', 0))

					audio_placement_loop_l_start = t_LoopStart*4
					audio_placement_loop_l_end = t_LoopEnd*4
					audio_placement_loop_start = t_StartRelative*4
					audio_placement_loop_on = ['false','true'].index(get_value(x_track_AudioClip_loop, 'LoopOn', 'test'))

					audio_placement_Fade = ['false','true'].index(get_value(x_track_AudioClip, 'Fade', 'false'))
					x_track_AudioClip_fades = x_track_AudioClip.findall('Fades')[0]

					if audio_placement_Fade == 1:
						cvpj_placement['fade'] = {}
						cvpj_placement['fade']['in'] = {}
						cvpj_placement['fade']['in']['duration'] = float(get_value(x_track_AudioClip_fades, 'FadeInLength', 0))*8
						cvpj_placement['fade']['in']['skew'] = float(get_value(x_track_AudioClip_fades, 'FadeInCurveSkew', 0))
						cvpj_placement['fade']['in']['slope'] = float(get_value(x_track_AudioClip_fades, 'FadeInCurveSlope', 0))
						cvpj_placement['fade']['out'] = {}
						cvpj_placement['fade']['out']['duration'] = float(get_value(x_track_AudioClip_fades, 'FadeOutLength', 0))*8
						cvpj_placement['fade']['out']['skew'] = float(get_value(x_track_AudioClip_fades, 'FadeOutCurveSkew', 0))
						cvpj_placement['fade']['out']['slope'] = float(get_value(x_track_AudioClip_fades, 'FadeOutCurveSlope', 0))

					cvpj_placement['audiomod'] = {}
					cvpj_audiomod = cvpj_placement['audiomod']

					if audio_placement_warp_on == 1:
						cvpj_audiomod['stretch_method'] = 'warp'
						cvpj_audiomod['stretch_params'] = {}
						if audio_placement_warp_mode == 0:
							cvpj_audiomod['stretch_algorithm'] = 'beats'
							cvpj_audiomod['stretch_params']['TransientResolution'] = int(get_value(x_track_AudioClip, 'TransientResolution', 6))
							cvpj_audiomod['stretch_params']['TransientLoopMode'] = int(get_value(x_track_AudioClip, 'TransientLoopMode', 2))
							cvpj_audiomod['stretch_params']['TransientEnvelope'] = int(get_value(x_track_AudioClip, 'TransientEnvelope', 100))
						if audio_placement_warp_mode == 1:
							cvpj_audiomod['stretch_algorithm'] = 'ableton_tones'
							cvpj_audiomod['stretch_params']['GranularityTones'] = float(get_value(x_track_AudioClip, 'GranularityTones', 30))
						if audio_placement_warp_mode == 2:
							cvpj_audiomod['stretch_algorithm'] = 'ableton_texture'
							cvpj_audiomod['stretch_params']['GranularityTexture'] = float(get_value(x_track_AudioClip, 'GranularityTexture', 71.328125))
							cvpj_audiomod['stretch_params']['FluctuationTexture'] = float(get_value(x_track_AudioClip, 'FluctuationTexture', 27.34375))
						if audio_placement_warp_mode == 3:
							cvpj_audiomod['stretch_algorithm'] = 'resample'
						if audio_placement_warp_mode == 4:
							cvpj_audiomod['stretch_algorithm'] = 'ableton_complex'
						if audio_placement_warp_mode == 6:
							cvpj_audiomod['stretch_algorithm'] = 'stretch_complexpro'
							cvpj_audiomod['stretch_params']['ComplexProFormants'] = float(get_value(x_track_AudioClip, 'ComplexProFormants', 100))
							cvpj_audiomod['stretch_params']['ComplexProEnvelope'] = int(get_value(x_track_AudioClip, 'ComplexProEnvelope', 120))

						x_track_AudioClip_WarpMarkers_bef = x_track_AudioClip.findall('WarpMarkers')[0]
						x_track_AudioClip_WarpMarkers = x_track_AudioClip_WarpMarkers_bef.findall('WarpMarker')
						t_warpmarkers = []
						for x_track_AudioClip_WarpMarker in x_track_AudioClip_WarpMarkers:
							t_warpmarker = {}
							t_warpmarker['pos'] = float(x_track_AudioClip_WarpMarker.get('BeatTime'))*4
							t_warpmarker['pos_real'] = float(x_track_AudioClip_WarpMarker.get('SecTime'))
							onedur = t_warpmarker['pos_real']/audio_sampleref['seconds']
							t_warpmarkers.append(t_warpmarker)
						
						cvpj_audiomod['stretch_data'] = t_warpmarkers
						
					else:
						cvpj_audiomod['stretch_method'] = None

					audio_placement_PitchCoarse = float(get_value(x_track_AudioClip, 'PitchCoarse', 0))
					audio_placement_PitchFine = float(get_value(x_track_AudioClip, 'PitchFine', 0))
					cvpj_audiomod['pitch'] = audio_placement_PitchCoarse + audio_placement_PitchFine/100

					#for value in ["CurrentStart", "CurrentEnd", "StartRelative", "LoopStart", "LoopEnd"]:
					#	print(str(get_value(x_track_AudioClip, value, 0)).ljust(20), end=' ')
					#print()

					if audio_placement_warp_on == False:
						if audio_placement_loop_on == 0:
							cvpj_placement['cut'] = {}
							cvpj_placement['cut']['type'] = 'cut'
							data_values.time_from_seconds(cvpj_placement['cut'], 'start', False, audio_placement_loop_l_start/4, 1)
							data_values.time_from_seconds(cvpj_placement['cut'], 'end', False, audio_placement_loop_l_end/4, 1)
					else:
						if audio_placement_loop_on == 0:
							cvpj_placement['cut'] = {}
							cvpj_placement['cut']['type'] = 'cut'
							data_values.time_from_seconds(cvpj_placement['cut'], 'start', True, audio_placement_loop_l_start/8, 1)
							data_values.time_from_seconds(cvpj_placement['cut'], 'end', True, audio_placement_loop_l_end/8, 1)
						else:
							cvpj_placement['cut'] = {}
							cvpj_placement['cut']['type'] = 'loop'
							data_values.time_from_steps(cvpj_placement['cut'], 'start', False, audio_placement_loop_start, 1)
							data_values.time_from_steps(cvpj_placement['cut'], 'loopstart', False, audio_placement_loop_l_start, 1)
							data_values.time_from_steps(cvpj_placement['cut'], 'loopend', False, audio_placement_loop_l_end, 1)

					tracks.r_pl_audio(cvpj_l, track_id, cvpj_placement)  

			sendcount = 1
			if tracktype in ['MidiTrack', 'AudioTrack']:
				get_auto(x_track_data)
				for track_sendholder in track_sendholders:
					sendid = sendcount
					sendautoid = 'send_'+track_id+'_'+str(sendid)
					sendlevel = get_param(track_sendholder, 'Send', 'float', 0, ['send', sendautoid, 'amount'], None)
					print('[input-ableton] Send Holder: '+str(sendid))
					tracks.r_add_send(cvpj_l, track_id, 'return_'+str(sendid), sendlevel, sendautoid)
					sendcount += 1

			if tracktype == 'ReturnTrack':
				cvpj_returntrackid = 'return_'+str(returnid)
				fxloc = ['return', None, cvpj_returntrackid]
				track_vol = get_param(x_track_Mixer, 'Volume', 'float', 0, ['return', returnid, 'vol'], None)
				track_pan = get_param(x_track_Mixer, 'Pan', 'float', 0, ['return', returnid, 'pan'], None)
				print('[input-ableton] Return: '+track_name+' ['+str(returnid)+']')
				tracks.r_add_return(cvpj_l, ['master'], cvpj_returntrackid)
				tracks.r_add_return_basicdata(cvpj_l, ['master'], cvpj_returntrackid, track_name, track_color, track_vol, track_pan)
				returnid += 1

			x_track_DeviceChain_inside = x_track_DeviceChain.findall('DeviceChain')[0]
			x_trackdevices = x_track_DeviceChain_inside.findall('Devices')[0]

			for x_trackdevice in x_trackdevices:
				able_plug_id = x_trackdevice.get('Id')
				pluginid = track_id+'_'+able_plug_id
				devicename = str(x_trackdevice.tag)
				print(pluginid, devicename)

				devfx_enabled = get_param(x_trackdevice, 'On', 'bool', True, ['slot', 'able_plug_id', 'enabled'], None)
				devfx_wet = 1

				if devicename not in ['MultiSampler', 'OriginalSimpler']:
					plugins.add_plug(cvpj_l, pluginid, 'native-ableton', devicename)
					device_defparams = abletondatadef_params[devicename]
					for ableton_paramname in device_defparams:
						ableton_param_data = device_defparams[ableton_paramname]
						als_paramval = get_param(
							x_trackdevice, ableton_paramname, ableton_param_data[0], 
							ableton_param_data[1], ['plugin', pluginid, ableton_paramname], None)
						plugins.add_plug_param(cvpj_l, pluginid, ableton_paramname, als_paramval, ableton_param_data[0], ableton_paramname)

					device_defdata = abletondatadef_data[devicename]
					for ableton_dataname in device_defdata:
						ableton_data_data = device_defdata[ableton_dataname]
						plugins.add_plug_data(cvpj_l, pluginid, ableton_dataname, use_valuetype(ableton_data_data[0], get_value(x_trackdevice, ableton_dataname, ableton_data_data[1])))

				if devicename == 'Saturator':
					x_WaveShaper = x_trackdevice.findall('WaveShaper')[0]
					for waveshapevarname in ['Drive','Lin','Curve','Damp','Period','Depth']:
						ws_p_name = 'waveshaper_'+waveshapevarname
						als_paramval = get_param(x_WaveShaper, waveshapevarname, 'float', 0, ['plugin', pluginid, ws_p_name], None)
						plugins.add_plug_param(cvpj_l, pluginid, ws_p_name, als_paramval, 'float', ws_p_name)

				if devicename in ['AutoPan', 'AutoFilter', 'FrequencyShifter']:
					x_lfo = x_trackdevice.findall('Lfo')[0]
					lfo_data = {}

					lfo_data['Type'] = get_param(x_lfo, 'Type', 'int', 0, None, None)
					lfo_data['Frequency'] = get_param(x_lfo, 'Frequency', 'float', 0, None, None)
					lfo_data['RateType'] = get_param(x_lfo, 'RateType', 'float', 0, None, None)
					lfo_data['BeatRate'] = get_param(x_lfo, 'BeatRate', 'int', 0, None, None)
					lfo_data['StereoMode'] = get_param(x_lfo, 'StereoMode', 'int', 0, None, None)
					lfo_data['Spin'] = get_param(x_lfo, 'Spin', 'float', 0, None, None)
					lfo_data['Phase'] = get_param(x_lfo, 'Phase', 'float', 0, None, None)
					lfo_data['Offset'] = get_param(x_lfo, 'Offset', 'float', 0, None, None)
					lfo_data['IsOn'] = get_param(x_lfo, 'IsOn', 'bool', False, None, None)
					lfo_data['Quantize'] = get_param(x_lfo, 'Quantize', 'bool', False, None, None)
					lfo_data['BeatQuantize'] = get_param(x_lfo, 'BeatQuantize', 'float', 0, None, None)
					lfo_data['NoiseWidth'] = get_param(x_lfo, 'NoiseWidth', 'float', 0, None, None)
					lfo_data['LfoAmount'] = get_param(x_lfo, 'LfoAmount', 'float', None, None, None)
					lfo_data['LfoInvert'] = get_param(x_lfo, 'LfoInvert', 'bool', None, None, None)
					lfo_data['LfoShape'] = get_param(x_lfo, 'LfoShape', 'float', None, None, None)

					plugins.add_plug_data(cvpj_l, pluginid, 'lfo_data', lfo_data)

					#if lfo_IsOn == False: lfo_amount = 0

					#if lfo_Type == 0: a_shape = 'sine'
					#if lfo_Type == 1: a_shape = 'square'
					#if lfo_Type == 2: a_shape = 'triangle'
					#if lfo_Type == 3: a_shape = 'saw'
					#if lfo_Type == 4: a_shape = 'reverse_saw'
					#if lfo_Type == 4: a_shape = 'noise'

					#if lfo_RateType:
					#	a_speed = lfo_Frequency
					#	a_time_type = 'seconds'
					#	if lfo_StereoMode: lfo_stereo = {'type': 'spin', 'spin': lfo_Spin}
					#	else: lfo_stereo = {'type': 'phase', 'spin': lfo_Phase, 'offset': 0}
					#else:
					#	a_speed = lfo_beatsteps[lfo_BeatRate]
					#	a_time_type = 'bar'
					#	lfo_stereo = {'type': 'phase', 'spin': lfo_Phase, 'offset': lfo_Offset}

					#plugins.add_lfo(cvpj_l, pluginid, 'main', a_shape, a_time_type, a_speed, 0, 0, lfo_Amount)
					#plugins.add_lfo_extra(cvpj_l, pluginid, 'main', 'quantize', lfo_Quantize)
					#plugins.add_lfo_extra(cvpj_l, pluginid, 'main', 'beat_quantize', lfo_BeatQuantize)
					#plugins.add_lfo_extra(cvpj_l, pluginid, 'main', 'noise_width', lfo_NoiseWidth)

				if devicename in ['Looper']:
					hextext = x_trackdevice.findall('SavedBuffer')[0].text
					if hextext != None:
						base64text = base64.b64encode(bytes.fromhex(hextext)).decode()
						plugins.add_plug_data(cvpj_l, pluginid, 'SavedBuffer', base64text)

				if devicename == 'Hybrid':
					x_Hybrid = x_trackdevice.findall('ImpulseResponseHandler')[0]
					x_SampleSlot = x_Hybrid.findall('SampleSlot')[0]
					x_Value = x_SampleSlot.findall('Value')[0]
					plugins.add_plug_data(cvpj_l, pluginid, 'sample', get_sampleref(x_Value)['file'])

				if devicename == 'Vocoder':
					x_Vocoder_FilterBank = x_trackdevice.findall('FilterBank')[0]
					banddata = []
					for bandnum in range(40):
						banddata.append( float(get_value(x_Vocoder_FilterBank, 'BandLevel.'+str(bandnum), 1)) )
						float(get_value(x_Vocoder_FilterBank, 'BandLevel.'+str(bandnum), 1))
					plugins.add_plug_data(cvpj_l, pluginid, 'banddata', banddata)
					plugins.add_plug_data(cvpj_l, pluginid, 'bandcount', int(get_value(x_Vocoder_FilterBank, 'BandCount', 12)))

				#paramletter = ['A','B']
				#if devicename == 'Eq8':
				#	banddata = [[],[]]
				#	for num in range(8):
				#		x_eq8band = x_trackdevice.findall('Bands.'+str(num))[0]
				#		bandparams = {}
				#		for paramletnum in range(2):
				#			listletnum = paramletter[paramletnum]
				#			x_eq8let = x_eq8band.findall('Parameter'+listletnum)[0]
				#			bandparams['IsOn'] = get_param(x_eq8let, 'IsOn', 'bool', 'false', None, None)
				#			bandparams['Mode'] = get_param(x_eq8let, 'Mode', 'int', 0, None, None)
				#			bandparams['Freq'] = get_param(x_eq8let, 'Freq', 'float', 0, None, None)
				#			bandparams['Gain'] = get_param(x_eq8let, 'Gain', 'float', 0, None, None)
				#			bandparams['Q'] = get_param(x_eq8let, 'Q', 'float', 0, None, None)
				#			print(listletnum, bandparams)
				#			banddata[paramletnum].append(bandparams)
				#	plugins.add_plug_data(cvpj_l, pluginid, 'band_data', banddata)



				#if devicename in ['OriginalSimpler', 'MultiSampler']:
				#	plugins.add_plug(cvpj_l, pluginid, 'native-ableton', 'sampler')

				#	# Player
				#	x_samp_Player = x_trackdevice.findall('Player')[0]
				#	plugins.add_plug_data(cvpj_l, pluginid, 'samplemap', get_MultiSampleMap(x_samp_Player.findall('MultiSampleMap')[0]))
				#	plugins.add_plug_data(cvpj_l, pluginid, 'reverse', get_param(x_samp_Player, 'Reverse', 'bool', 'false', None, None))
				#	plugins.add_plug_data(cvpj_l, pluginid, 'subosc_on', get_param(x_samp_Player.findall('SubOsc')[0], 'IsOn', 'bool', 'false', None, None))
				#	plugins.add_plug_data(cvpj_l, pluginid, 'interpolation', int(get_value(x_samp_Player, 'InterpolationMode', 1)))

				#	# Pitch
				#	x_samp_Pitch = x_trackdevice.findall('Pitch')[0]
				#	plugins.add_plug_data(cvpj_l, pluginid, 'interpolation', int(get_value(x_samp_Player, 'InterpolationMode', 1)))
				#	TransposeKey = float(get_param(x_samp_Pitch, 'TransposeKey', 'float', 0, None, None))
				#	TransposeFine = float(get_param(x_samp_Pitch, 'TransposeFine', 'float', 0, None, None))
				#	plugins.add_plug_data(cvpj_l, pluginid, 'transpose', TransposeKey + TransposeFine/100)
				#	PitchLfoAmount = float(get_param(x_samp_Pitch, 'PitchLfoAmount', 'float', 0, None, None))
				#	plugins.add_plug_data(cvpj_l, pluginid, 'pitch_env_on', get_param(x_samp_Player.findall('Envelope')[0], 'IsOn', 'bool', 'false', None, None))
				#	ableton_pitch_data = {}
					# --------------------- SimplerSubOsc

				#	# Pitch
				#	x_samp_Filter = x_trackdevice.findall('Filter')[0]
				#	x_samp_Filter_on = get_param(x_samp_Filter, 'IsOn', 'bool', 'false', None, None)
				#	# --------------------- Filter
				#	ableton_filter_data = {}

				if fxloc != None: tracks.insert_fxslot(cvpj_l, fxloc, 'audio', pluginid)

				plugins.add_plug_fxdata(cvpj_l, pluginid, able_plug_id, devfx_wet)


				#_______paramfinder_data[devicename] = {}
				#_______paramfinder_param[devicename] = {}
				if False:
					for x_trackdevice_name in x_trackdevice:
						tagname = x_trackdevice_name.tag
						manualval = x_trackdevice_name.findall('Manual')
						if tagname not in ['On', 'LomId', 'LomIdView', 'IsExpanded', 'ModulationSourceCount',
						'ParametersListWrapper', 'Pointee', 'LastSelectedTimeableIndex', 'LastSelectedClipEnvelopeIndex',
						'LastPresetRef', 'LockedScripts', 'IsFolded', 'ShouldShowPresetName', 'UserName', 'Annotation', 
						'SourceContext', 'OverwriteProtectionNumber']:
							if manualval != []:
								findmanval = manualval[0].get('Value')
								valuetype = isfloatboolstring(findmanval)
								#print('--PARAM--', tagname, valuetype, findmanval)

								#_______paramfinder_param[devicename][tagname] = [valuetype, findmanval, 
								#get_Range(x_trackdevice_name, 'MidiControllerRange'), 
								#get_Range(x_trackdevice_name, 'MidiCCOnOffThresholds')]
							elif x_trackdevice_name.get('Value') != None :
								findmanval = x_trackdevice_name.get('Value')
								valuetype = isfloatboolstring(findmanval)
								print('--DATA---', tagname, valuetype, findmanval)
								_______paramfinder_data[devicename][tagname] = [valuetype, findmanval]
							else:
								print('---------', tagname)

		#for devicename in _______paramfinder_param:
		#	print('"'+devicename+'":', _______paramfinder_param[devicename],',')


		get_auto(x_MasterTrack)
		tracks.autoid_in_output(cvpj_l)

		return json.dumps(cvpj_l)

