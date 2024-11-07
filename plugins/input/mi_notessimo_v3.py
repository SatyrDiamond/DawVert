# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_data
from functions import xtramath
from objects import globalstore
import json
import plugins
import struct
import zlib
import os

import logging
logger_input = logging.getLogger('input')

notess_noteoffset = {}
notess_noteoffset["C / A"] = [[       [ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 1, 1, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]],[[-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]]]
notess_noteoffset["(#) G / E"] = [[   [ 0, 0, 0, 0, 1, 0, 0],[ 0, 0, 0, 1, 0, 0, 0]],[[ 1, 1, 0, 1, 0, 1, 0],[ 1, 1, 1, 0, 1, 1, 1]],[[-1,-1,-1,-1, 0,-1,-1],[-1,-1,-1, 0,-1,-1,-1]]]
notess_noteoffset["(#) D / B"] = [[   [ 1, 0, 1, 0, 1, 0, 0],[ 1, 0, 0, 1, 0, 0, 1]],[[ 0, 1, 1, 1, 0, 1, 0],[ 0, 1, 1, 0, 1, 1, 0]],[[ 0,-1, 0,-1, 0,-1,-1],[ 0,-1,-1, 0,-1,-1, 0]]]
notess_noteoffset["(#) A / F#"] = [[  [ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 0, 1]],[[ 0, 1, 0, 0, 0, 1, 0],[ 0, 1, 0, 0, 1, 1, 0]],[[ 0,-1,-1, 0, 0,-1,-1],[ 0,-1, 0, 0,-1,-1, 0]]]
notess_noteoffset["(#) E / C#"] = [[  [ 1, 0, 1, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 1, 1]],[[ 0, 1, 1, 0, 0, 1, 0],[ 0, 1, 0, 0, 1, 0, 0]],[[ 0,-1, 0, 0, 0,-1, 0],[ 0,-1, 0, 0,-1, 0, 0]]]
notess_noteoffset["(#) B / G#"] = [[  [ 1, 0, 0, 1, 1, 0, 0],[ 1, 1, 1, 1, 0, 1, 1]],[[ 0, 1, 0, 0, 0, 1, 0],[ 0, 0, 0, 0, 1, 0, 0]],[[ 0,-1, 0, 0, 0,-1, 0],[ 0, 0, 0, 0,-1, 0, 0]]]
notess_noteoffset["(#) F# / D#"] = [[ [ 1, 0, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]],[[ 0, 1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 0,-1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]]]
notess_noteoffset["(#) C# / A#"] = [[ [ 1, 1, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 1]],[[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]]]
notess_noteoffset["(b) F / D"] = [[   [ 0,-1, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 1, 0, 0, 1, 1, 1, 0],[ 1, 1, 1, 1, 1, 1, 0]],[[-1, 0,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]]]
notess_noteoffset["(b) Bb / G"] = [[  [ 0,-1, 0, 0, 0,-1, 0],[ 0, 0, 0, 0,-1, 0, 0]],[[ 1, 0, 0, 1, 1, 0, 0],[ 1, 1, 1, 1, 0, 1, 1]],[[-1, 0,-1,-1,-1, 0,-1],[-1,-1,-1,-1, 0,-1,-1]]]
notess_noteoffset["(b) Eb / C"] = [[  [ 0,-1,-1, 0, 0,-1, 0],[ 0,-1, 0, 0,-1, 0, 0]],[[ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 1, 1]],[[-1, 0, 0,-1,-1, 0,-1],[-1, 0,-1, 0, 0,-1,-1]]]
notess_noteoffset["(b) Ab / F"] = [[  [ 0,-1,-1, 0, 0,-1,-1],[ 0,-1, 0, 0,-1,-1, 0]],[[ 1, 0, 0, 1, 1, 0, 0],[ 1, 0, 1, 1, 0, 0, 1]],[[-1, 0, 0,-1,-1, 0, 0],[-1, 0,-1, 0, 0, 0,-1]]]
notess_noteoffset["(b) Db / Bb"] = [[ [ 0,-1,-1,-1, 0,-1,-1],[ 0,-1,-1, 0,-1,-1, 0]],[[ 1, 0, 0, 0, 1, 0, 0],[ 1, 0, 0, 1, 0, 0, 1]],[[-1, 0, 0, 0,-1, 0, 0],[-1, 0, 0, 0, 0, 0,-1]]]
notess_noteoffset["(b) Gb / Eb"] = [[ [-1,-1,-1,-1, 0,-1,-1],[-1,-1,-1, 0,-1,-1,-1]],[[ 0, 0, 0, 0, 1, 0, 0],[ 0, 0, 0, 1, 0, 0, 0]],[[ 0, 0, 0, 0,-1, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]]]
notess_noteoffset["(b) Cb / Ab"] = [[ [-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1, 0,-1,-1,-1]],[[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]],[[ 0, 0, 0, 0, 0, 0, 0],[ 0, 0, 0, 0, 0, 0, 0]]]

def do_layers(project_obj, layer_data):
	spl = {}
	for x in layer_data.spots: spl[x.pos] = x
	spl = [x for _, x in sorted(spl.items())]

	outdata = []

	curpos = 0
	prevend = 0
	for layerspot in spl:
		sheetdata = project_obj.sheets[layerspot.id]
		sheet_tempo = sheetdata.tempo
		sheet_width = sheetdata.width*8
		tempodiv = (sheet_tempo/120)

		pl_pos = layerspot.pos
		pl_dur = layerspot.len
		pl_end = pl_pos+pl_dur
		breakt = max(pl_pos-prevend, 0.0)

		calcdur = (sheet_width/tempodiv)
		calcscale = pl_dur/calcdur

		pauselen = breakt/(calcscale*(1/tempodiv))
		curpos += pauselen

		realdur = sheetrealsize[layerspot.id]/2
		realdur = (realdur/2).__ceil__()*2

		calcd = calcdur*(sheet_tempo/120)

		outdata.append([curpos, realdur, layerspot.id, sheet_tempo])
		prevend = pl_end
		curpos += realdur

	return outdata

class sample_manager():
	extracted_samples = []

	def add_sample(project_obj, convproj_obj, sample_id):
		samplekey = 0
		sampleref_obj = None
		if sample_id in project_obj.samples:
			notet_sample = project_obj.samples[sample_id]
			#print(notet_sample.name)
			if notet_sample.data:
				zipfilepath = 'resources/'+notet_sample.data
				if zipfilepath in project_obj.zip_data.namelist():
					#print(zipfilepath)
					try: project_obj.zip_data.extract(zipfilepath, path=samplefolder, pwd=None)
					except: pass
					realfilepath = os.path.join(samplefolder,zipfilepath)
					sampleref_obj = convproj_obj.sampleref__add(sample_id, realfilepath, None)
			samplekey = do_key(notet_sample.pitch, notet_sample.octave, notet_sample.accidental)
			return sample_id, notet_sample, samplekey, sampleref_obj
		return None, None, 0

DEBUGINSTNAMES = False

from functions import note_data

def do_key(pitch, octave, accidental):
	accidentald = ''
	if accidental == '(#) Sharp': accidentald = '#'
	outtxt = pitch+accidentald+str(octave)
	return note_data.text_to_note(outtxt)+24

class inst_manager():
	fxnum = 2

	def proc_inst(convproj_obj, plugin_obj, instid, inst_set, data_obj):
		sampleid, notet_sample, samplekey, sampleref_obj = sample_manager.add_sample(data_obj, convproj_obj, inst_set.sample_1)

		start_pitch = do_key(inst_set.pitch_start_1, inst_set.octave_start_1, inst_set.accidental_start_1)
		end_pitch = do_key(inst_set.pitch_end_1, inst_set.octave_end_1, inst_set.accidental_end_1)

		if sampleid:
			sp_obj = plugin_obj.sampleregion_add(start_pitch, end_pitch, samplekey, None)
			sp_obj.sampleref = sampleid
			sp_obj.point_value_type = "samples"
			sp_obj.loop_active = notet_sample.loop_type == 'Loop'
			sp_obj.loop_start = notet_sample.start
			sp_obj.loop_end = notet_sample.end
			sp_obj.start = notet_sample.sample_start
			sp_obj.end = sampleref_obj.dur_samples

	def add_inst(convproj_obj, instid, project_obj, maindata_obj):
		inst_obj = convproj_obj.instrument__add(instid)
		midifound = inst_obj.from_dataset('notessimo_v3', 'inst', instid, True)
		if midifound: inst_obj.to_midi(convproj_obj, instid, True)
		#inst_obj.fxrack_channel = 1 if inst_obj.midi.out_inst.drum else inst_manager.fxnum
		if inst_obj.visual.name and DEBUGINSTNAMES: inst_obj.visual.name = '[DSET] '+inst_obj.visual.name

		notet_inst = None
		notet_data = None
		dfrom = None

		if instid in maindata_obj.instruments:
			notet_inst = maindata_obj.instruments[instid]
			notet_data = maindata_obj
			dfrom = 'EXTD'
		elif instid in project_obj.instruments:
			notet_inst = project_obj.instruments[instid]
			notet_data = project_obj
			dfrom = 'PROJ'

		if notet_inst: 
			if notet_inst.name: inst_obj.visual.name = notet_inst.name
			incolor(notet_inst.color, inst_obj.visual)
			if DEBUGINSTNAMES:
				if inst_obj.visual.name: inst_obj.visual.name = '['+dfrom+'] '+inst_obj.visual.name
				else: inst_obj.visual.name = '['+dfrom+'] !!! NO NAME'

			sampleids = [d.sample_1 for _, d in notet_inst.sets.items() if d.sample_1]

			if sampleids:
				plugin_obj = convproj_obj.plugin__add(instid, 'universal', 'sampler', 'multi')
				plugin_obj.role = 'synth'
				inst_obj.pluginid = instid

				for setnum, set_data in notet_inst.sets.items():
					inst_manager.proc_inst(convproj_obj, plugin_obj, instid, set_data, notet_data)

			elif notet_inst.sample:
				plugin_obj = convproj_obj.plugin__add(instid, 'universal', 'sampler', 'single')
				plugin_obj.role = 'synth'
				inst_obj.pluginid = instid

				sampleid, notet_sample, samplekey, sampleref_obj = sample_manager.add_sample(notet_data, convproj_obj, notet_inst.sample)

				sp_obj = plugin_obj.samplepart_add('sample')
				sp_obj.sampleref = sampleid
				sp_obj.point_value_type = "samples"
				sp_obj.loop_active = notet_sample.loop_type == 'Loop'
				sp_obj.loop_start = notet_sample.start
				sp_obj.loop_end = notet_sample.end
				sp_obj.start = notet_sample.sample_start
				sp_obj.end = sampleref_obj.dur_samples

				inst_obj.datavals.add('middlenote', samplekey)
				
				outvol = xtramath.from_db(notet_sample.volume/3)
				inst_obj.params.add('vol', outvol, 'float')

				#print('S', dfrom, 0, notet_inst.sample)
				#inst_manager.proc_inst(convproj_obj, plugin_obj, instid, set_data, notet_data)

		#if inst_obj.fxrack_channel == 1:
		#	fxchan_data = convproj_obj.fx__chan__add(inst_manager.fxnum)
		#	fxchan_data.visual.name = inst_obj.visual.name
		#	fxchan_data.visual.color = inst_obj.visual.color.copy()
		#	inst_manager.fxnum += 1

def incolor(value, visual_obj): 
	if value not in ['0x000000', '', None]:
		if value.startswith('0x') and len(value)==8: 
			visual_obj.color.set_hex(value[2:])
		elif value.isnumeric():
			colorval = int(value).to_bytes(3, 'big')
			visual_obj.color.set_int([colorval[0], colorval[1], colorval[2]])

class input_notessimo_v3(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'notessimo_v3'
	def get_name(self): return 'Notessimo V3'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['note']
		in_dict['file_ext_detect'] = False
		in_dict['auto_types'] = ['pl_points']
		in_dict['track_lanes'] = True
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'mi'
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_notessimo_v3

		global sheetrealsize
		global samplefolder
		samplefolder = dv_config.path_samples_extracted

		# ---------- CVPJ Start ----------
		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'mi'
		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('notessimo_v3', './data_main/dataset/notessimo_v3.dset')
		
		extpath_path = os.path.join(dv_config.path_external_data, 'notessimo_v3', 'notessimo_v3_data.zip')

		# ---------- File ----------
		project_obj = proj_notessimo_v3.notev3_file()
		if not project_obj.load_from_file(input_file): exit()

		maindata_obj = proj_notessimo_v3.notev3_file()
		if os.path.exists(extpath_path): 
			if maindata_obj.load_from_file(extpath_path): 
				logger_input.info('loaded external data: "notessimo_v3.zip"')

		songlist = list(project_obj.songs)

		notet_cursong_id = songlist[dv_config.songnum-1]
		notet_cursong_data = project_obj.songs[notet_cursong_id]

		used_insts = []

		sheetrealsize = {}

		for sheet_id, sheet_data in project_obj.sheets.items():
			nle_obj = convproj_obj.notelistindex__add(sheet_id)
			nle_obj.visual.name = sheet_data.name
			incolor(sheet_data.color, nle_obj.visual)

			for nnn in sheet_data.get_allnotes():
				nle_obj.notelist.add_m(nnn.inst, nnn.pos*2, nnn.dur*4, nnn.get_note(), 1, None)
				if nnn.inst not in used_insts: used_insts.append(nnn.inst)
			nle_obj.notelist.sort()

			sheetrealsize[sheet_id] = nle_obj.notelist.get_dur()

		firstlayer = True
		for layer_id, layer_data in notet_cursong_data.layers.items():
			if layer_data.spots:
				playlist_obj = convproj_obj.playlist__add(layer_id, 1, True)
				durposdata = do_layers(project_obj, layer_data)

				for pos, dur, sid, tempo in durposdata:
					if firstlayer:
						autopl_obj = convproj_obj.automation.add_pl_points(['main','bpm'], 'float')
						autopl_obj.time.set_posdur(pos*2, dur*2)
						autopoint_obj = autopl_obj.data.add_point()
						autopoint_obj.value = tempo

					cvpj_placement = playlist_obj.placements.add_notes_indexed()
					cvpj_placement.fromindex = sid
					cvpj_placement.time.set_posdur(pos*2, dur*2)

				firstlayer = False

		fxchan_data = convproj_obj.fx__chan__add(1)
		fxchan_data.visual.name = 'Drums'

		for used_inst in used_insts:
			inst_manager.add_inst(convproj_obj, used_inst, project_obj, maindata_obj)
