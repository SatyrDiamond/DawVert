# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import xtramath
from objects import globalstore
import plugins
import os
import numpy as np

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

		outdata.append([curpos, realdur, layerspot.id, sheet_tempo, sheetdata.valueSignature, sheetdata.nSignature])
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
					sampleref_obj.visual.name = notet_sample.name
					if notet_sample.comments: sampleref_obj.visual.comment = notet_sample.comments
					incolor(notet_sample.color, sampleref_obj.visual)
			samplekey = do_key(notet_sample.pitch, notet_sample.octave, notet_sample.accidental)
			return sample_id, notet_sample, samplekey, sampleref_obj
		return None, None, 0, None

DEBUGINSTNAMES = False

from functions import note_data

def do_key(pitch, octave, accidental):
	accidentald = ''
	if accidental == '(#) Sharp': accidentald = '#'
	outtxt = pitch+accidentald+str(octave)
	return note_data.text_to_note(outtxt)+24

class inst_manager():
	fxnum = 2

	def proc_inst(convproj_obj, plugin_obj, instid, inst_set, data_obj, notet_inst):
		sampleid, notet_sample, samplekey, sampleref_obj = sample_manager.add_sample(data_obj, convproj_obj, inst_set.sample_1)

		start_pitch = do_key(inst_set.pitch_start_1, inst_set.octave_start_1, inst_set.accidental_start_1)
		end_pitch = do_key(inst_set.pitch_end_1, inst_set.octave_end_1, inst_set.accidental_end_1)

		if notet_sample and sampleref_obj:
			dur_samples = sampleref_obj.get_dur_samples()
			if sampleid and dur_samples:
				sp_obj = plugin_obj.sampleregion_add(start_pitch, end_pitch, samplekey, None)
				sp_obj.sampleref = sampleid
				sp_obj.point_value_type = "samples"
				sp_obj.loop_active = notet_sample.loop_type == 'Loop'
				sp_obj.loop_start = notet_sample.start
				sp_obj.loop_end = notet_sample.end
				sp_obj.start = notet_sample.sample_start
				sp_obj.end = dur_samples
				sp_obj.pan = notet_sample.pan
				sp_obj.vol = xtramath.from_db(notet_sample.volume/3)
				sp_obj.scale = notet_inst.scale_inst
				sp_obj.pitch = notet_sample.cent/100
				sp_obj.visual = sampleref_obj.visual.copy()

	def add_inst(convproj_obj, instid, project_obj, maindata_obj):
		inst_obj = convproj_obj.instrument__add(instid)
		inst_obj.visual.from_datapack('notessimo_v3', 'inst', instid, True)
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
			if notet_inst.comments: inst_obj.visual.comment = notet_inst.comments
			if DEBUGINSTNAMES:
				if inst_obj.visual.name: inst_obj.visual.name = '['+dfrom+'] '+inst_obj.visual.name
				else: inst_obj.visual.name = '['+dfrom+'] !!! NO NAME'

			sampleids = [d.sample_1 for _, d in notet_inst.sets.items() if d.sample_1]

			if sampleids:
				plugin_obj = convproj_obj.plugin__add(instid, 'universal', 'sampler', 'multi')
				plugin_obj.role = 'synth'

				for setnum, set_data in notet_inst.sets.items():
					inst_manager.proc_inst(convproj_obj, plugin_obj, instid, set_data, notet_data, notet_inst)

			elif notet_inst.sample:
				plugin_obj = convproj_obj.plugin__add(instid, 'universal', 'sampler', 'single')
				plugin_obj.role = 'synth'

				sampleid, notet_sample, samplekey, sampleref_obj = sample_manager.add_sample(notet_data, convproj_obj, notet_inst.sample)

				if notet_sample and sampleref_obj:
					dur_samples = sampleref_obj.get_dur_samples()

					if dur_samples:
						sp_obj = plugin_obj.samplepart_add('sample')
						sp_obj.sampleref = sampleid
						sp_obj.point_value_type = "samples"
						sp_obj.loop_active = notet_sample.loop_type == 'Loop'
						sp_obj.loop_start = notet_sample.start
						sp_obj.loop_end = notet_sample.end
						sp_obj.start = notet_sample.sample_start
						sp_obj.end = dur_samples
						sp_obj.scale = notet_inst.scale_inst
	
						inst_obj.datavals.add('middlenote', samplekey)
					
						outvol = xtramath.from_db(notet_sample.volume/3)
						inst_obj.params.add('vol', outvol, 'float')
						inst_obj.params.add('pan', notet_sample.pan, 'float')

			else:
				plugin_obj = convproj_obj.plugin__add(instid, 'universal', 'midi', None)
				plugin_obj.midi.from_datapack('notessimo_v3', 'inst', instid)
				plugin_obj.midi.to_visual(inst_obj.visual, False)

			if notet_inst.midi>-1: plugin_obj.midi_fallback__add_inst(notet_inst.midi)
			else: plugin_obj.midi_fallback__add_from_datapack('notessimo_v3', 'inst', instid)

			inst_obj.plugslots.set_synth(instid)

			plugin_obj.env_asdr_add('vol', 0, notet_inst.fadeIn, 0, 0, 1, notet_inst.fadeOut, 1)

			if notet_inst.biquad_active != '0':
				fx_id = instid+'_filter'
				plugin_obj = convproj_obj.plugin__add(fx_id, 'universal', 'filter', 'single')
				plugin_obj.role = 'fx'
				plugin_obj.filter.on = True
				if notet_inst.biquad=='Low Pass': plugin_obj.filter.type.set('low_pass', None)
				if notet_inst.biquad=='High Pass': plugin_obj.filter.type.set('high_pass', None)
				if notet_inst.biquad=='Band Pass': plugin_obj.filter.type.set('band_pass', None)
				plugin_obj.filter.freq = int(notet_inst.biquad_frequency)
				plugin_obj.filter.q = notet_inst.biquad_q
				inst_obj.plugslots.plugin_autoplace(plugin_obj, fx_id)

def incolor(value, visual_obj): 
	if value not in ['0x000000', '', None]:
		if value.startswith('0x') and len(value)==8: 
			visual_obj.color.set_hex(value[2:])
			visual_obj.color.fx_allowed = ['saturate', 'brighter']
		elif value.isnumeric():
			colorval = int(value).to_bytes(3, 'big')
			visual_obj.color.set_int([colorval[0], colorval[1], colorval[2]])
			visual_obj.color.fx_allowed = ['saturate', 'brighter']

class input_notessimo_v3(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'notessimo_v3'
	
	def get_name(self):
		return 'Notessimo V3'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'mi'
		
	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_uncommon import notessimo_v3 as proj_notessimo_v3

		global sheetrealsize
		global samplefolder
		samplefolder = dawvert_intent.path_samples['extracted']

		# ---------- CVPJ Start ----------
		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'mi'

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['pl_points']

		convproj_obj.set_timings(4.0)

		globalstore.datapack.load('notessimo_v3', './data/datapack/app/notessimo_v3.xml')
		
		extpath_path = os.path.join(dawvert_intent.path_external_data, 'notessimo_v3', 'notessimo_v3_data.zip')

		# ---------- File ----------
		project_obj = proj_notessimo_v3.notev3_file()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		maindata_obj = proj_notessimo_v3.notev3_file()
		if os.path.exists(extpath_path): 
			if maindata_obj.load_from_file(extpath_path): 
				logger_input.info('loaded external data: "notessimo_v3.zip"')

		songlist = list(project_obj.songs)

		notet_cursong_id = songlist[dawvert_intent.songnum]
		notet_cursong_data = project_obj.songs[notet_cursong_id]

		used_insts = []

		sheetrealsize = {}

		for sheet_id, sheet_data in project_obj.sheets.items():
			nle_obj = convproj_obj.notelistindex__add(sheet_id)
			nle_obj.visual.name = sheet_data.name
			if sheet_data.comments: nle_obj.visual.comment = sheet_data.comments
			incolor(sheet_data.color, nle_obj.visual)

			sheetnoteofs = notess_noteoffset[sheet_data.signature]

			cvpj_notelist = nle_obj.notelist

			for nnn in sheet_data.get_allnotes():
				out_note, out_key, out_oct = nnn.get_key_nooffs()
				inum = 0
				if nnn.sharp: inum = 1
				if nnn.flat: inum = 2
				noteoffs = sheetnoteofs[inum][1][out_key]
				dur = nnn.dur*4 if not np.isnan(nnn.dur) else 1
				cvpj_notelist.add_m(nnn.inst, nnn.pos*2, dur, out_note+noteoffs, 1, None)
				if nnn.inst not in used_insts: used_insts.append(nnn.inst)
			cvpj_notelist.sort()

			sheetrealsize[sheet_id] = cvpj_notelist.get_dur()

		auto_bpm_obj = convproj_obj.automation.create(['main','bpm'], 'float', True)
		firstlayer = True

		fxchan_data = convproj_obj.fx__chan__add(0)
		incolor(notet_cursong_data.color, fxchan_data.visual)
		fxchan_data.params.add('vol', xtramath.from_db(notet_cursong_data.volume/3), 'float')
		fxchan_data.params.add('pan', notet_cursong_data.pan, 'float')
		
		for layer_id, layer_data in notet_cursong_data.layers.items():
			if layer_data.spots:
				playlist_obj = convproj_obj.playlist__add(layer_id, 1, True)
				durposdata = do_layers(project_obj, layer_data)

				for pos, dur, sid, tempo, denum, numer in durposdata:
					if firstlayer:
						auto_bpm_obj.add_all(pos*2, tempo, dur*2)
						convproj_obj.timesig_auto.add_point(pos*2, [numer, denum])

					cvpj_placement = playlist_obj.placements.add_notes_indexed()
					cvpj_placement.fromindex = sid
					time_obj = cvpj_placement.time
					time_obj.set_posdur(pos*2, dur*2)

				firstlayer = False

		fxchan_data = convproj_obj.fx__chan__add(1)
		fxchan_data.visual.name = 'Drums'

		for used_inst in used_insts:
			inst_manager.add_inst(convproj_obj, used_inst, project_obj, maindata_obj)

		if notet_cursong_data.name: convproj_obj.metadata.name = notet_cursong_data.name
		if notet_cursong_data.comments: convproj_obj.metadata.comment_text = notet_cursong_data.comments