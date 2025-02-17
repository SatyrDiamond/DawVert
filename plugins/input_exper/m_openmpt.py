# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_openmpt(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'

	def get_shortname(self):
		return 'libopenmpt'

	def get_name(self):
		return 'libOpenMPT'

	def get_priority(self):
		return 0
		
	def usable(self): 
		from objects.extlib import openmpt
		openmpt_obj = openmpt.openmpt()
		usable = openmpt_obj.load_lib()!=-1
		usable_meg = "Library not found or can't be loaded" if not usable else ''
		del openmpt_obj
		return usable, usable_meg

	def get_prop(self, in_dict): 
		in_dict['track_lanes'] = True
		in_dict['projtype'] = 'ts'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.extlib import openmpt
		
		if dawvert_intent.input_mode == 'file':
			f = open(dawvert_intent.input_file, 'rb')
			moduledata = f.read()
		if dawvert_intent.input_mode == 'bytes':
			moduledata = dawvert_intent.input_data

		openmpt_obj = openmpt.openmpt()
		openmpt_obj.load_lib()
		openmpt_obj.openmpt_module_create_from_memory2(moduledata)

		metadata = openmpt_obj.get_metadata()
		if 'title' in metadata: convproj_obj.metadata.name = metadata['title']
		if 'artist' in metadata: convproj_obj.metadata.author = metadata['artist']
		if 'message' in metadata: convproj_obj.metadata.comment_text = metadata['message']

		num_channels = openmpt_obj.openmpt_module_get_num_channels()
		num_instruments = openmpt_obj.openmpt_module_get_num_instruments()
		num_samples = openmpt_obj.openmpt_module_get_num_samples()
		num_patterns = openmpt_obj.openmpt_module_get_num_patterns()
		uses_instruments = bool(num_instruments)

		tracker_obj = convproj_obj.main__create_tracker_single()
		tracker_obj.set_num_chans(num_channels)
		tracker_obj.maincolor = [0.6, 0.6, 0.6]
		tracker_obj.tempo = openmpt_obj.openmpt_module_get_current_tempo()
		tracker_obj.speed = openmpt_obj.openmpt_module_get_current_speed()
		tracker_obj.orders = openmpt_obj.get_orderlist()

		if num_instruments:
			for num in range(num_instruments):
				inst_obj = tracker_obj.add_inst(convproj_obj, num, None)
				inst_obj.visual.name = openmpt_obj.openmpt_module_get_instrument_name(num).decode()
		else:
			for num in range(num_samples):
				inst_obj = tracker_obj.add_inst(convproj_obj, num, None)
				inst_obj.visual.name = openmpt_obj.openmpt_module_get_sample_name(num).decode()
			
		for num_pat in range(num_patterns):
			num_rows = openmpt_obj.openmpt_module_get_pattern_num_rows(num_pat)
			pattern_obj = tracker_obj.pattern_add(num_pat, num_rows)
			pattern_obj.name = openmpt_obj.openmpt_module_get_pattern_name(num_pat)

			for num_ch in range(num_channels):
				for num_row in range(num_rows):
					note, inst, volfx, fx, vol, param = openmpt_obj.get_patnote(num_pat, num_row, num_ch)
					pattern_obj.cell_note(num_ch, num_row, note-1 if note else None, inst if inst else None)
					if volfx: pattern_obj.cell_param(num_ch, num_row, 'vol', vol/64)
					if fx == 16: pattern_obj.cell_g_param(num_ch, num_row, 'speed', param)
					if fx == 4: pattern_obj.cell_g_param(num_ch, num_row, 'std_slide_to_note', param)
					if fx == 3: pattern_obj.cell_param(num_ch, num_row, 'std_slide_down', param)
					if fx == 2: pattern_obj.cell_param(num_ch, num_row, 'std_slide_up', param)
					if fx == 17: pattern_obj.cell_g_param(num_ch, num_row, 'tempo', param)
					if fx == 14: pattern_obj.cell_g_param(num_ch, num_row, 'break_to_row', param)
