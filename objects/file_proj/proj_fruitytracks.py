# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from functions_plugin import format_flp_tlv
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

verbose = False
def verboseprint(event_id, event_data):
	cmdname = '__UNKNOWN'

	if event_id == 2: cmdname = 'PRE_TRACK_VOL'
	if event_id == 3: cmdname = 'PRE_TRACK_PAN'
	if event_id == 7: cmdname = 'NEW_TRACK'
	if event_id == 5: cmdname = 'NEW_CLIP'
	if event_id == 6: cmdname = 'CLIP_SHOWWAVE'
	if event_id == 12: cmdname = 'MASTER_VOL'
	if event_id == 15: cmdname = 'CLIP_DONTSTART'
	if event_id == 66: cmdname = 'BPM'
	if event_id == 4: cmdname = 'CLIP_VOL_START'
	if event_id == 13: cmdname = 'CLIP_VOL_END'
	if event_id == 8: cmdname = 'CLIP_PAN_START'
	if event_id == 14: cmdname = 'CLIP_PAN_END'
	if event_id == 138: cmdname = 'CLIP_RESO'
	if event_id == 139: cmdname = 'CLIP_CUTOFF'
	if event_id == 196: cmdname = 'CLIP_FILE'
	if event_id == 193: cmdname = 'CLIP_NAME'
	if event_id == 129: cmdname = 'CLIP_POS'
	if event_id == 130: cmdname = 'CLIP_DUR'
	if event_id == 131: cmdname = 'CLIP_REPEATLEN'
	if event_id == 137: cmdname = 'CLIP_STRETCH'
	if event_id == 194: cmdname = 'TITLE'
	if event_id == 197: cmdname = 'URL'
	if event_id == 198: cmdname = 'COMMENT'
	if event_id == 199: cmdname = 'VIDEO'
	if event_id == 132: cmdname = 'LOOPSTART'
	if event_id == 133: cmdname = 'LOOPEND'
	if event_id == 134: cmdname = 'ZOOM_H'
	if event_id == 135: cmdname = 'ZOOM_V'
	if event_id == 201: cmdname = 'CLIP_VOL_ENV'
	if event_id == 192: cmdname = 'TRACK_NAME'
	if event_id == 200: cmdname = 'PLUGIN'

	print(cmdname.ljust(15)+'|'+str(event_id).ljust(4)+'|'+str(event_data))

class ftr_clip:
	def __init__(self):
		self.file = ''
		self.name = ''
		self.pos = 0
		self.dur = 0
		self.repeatlen = 0
		self.stretch = 0
		self.vol_start = 0
		self.vol_end = 0
		self.pan_start = 0
		self.pan_end = 0
		self.reso_start = 0
		self.cutoff_start = 0
		self.reso_end = 0
		self.muted = 0
		self.cutoff_end = 0
		self.vol_env = []

class ftr_track:
	def __init__(self):
		self.clips = []
		self.vol = 100
		self.pan = 64
		self.name = ''
		self.plugins = {}

class ftr_plugin:
	def __init__(self):
		self.slotnum = 0
		self.version = 1
		self.name = ''
		self.params = []

	def read(self, pluginbytes):
		plugindata = bytereader.bytereader()
		plugindata.load_raw(pluginbytes)
		self.slotnum = plugindata.uint8()
		self.version = plugindata.uint16()
		self.name = plugindata.c_string__int32(False)
		paramsize = plugindata.uint32()
		numparams = plugindata.uint32()
		self.params = plugindata.l_float(numparams)

class ftr_song:
	def __init__(self):
		self.bpm = 120
		self.tracks = []
		self.title = ''
		self.url = ''
		self.comment = ''
		self.video = ''
		self.showinfo = 0
		self.vol = 100
		self.loopstart = 0
		self.loopend = 0
		self.zoom_h = 0
		self.zoom_v = 0
		self.dontstart = 0
		self.plugins = {}

	def load_from_file(self, input_file):
		song_data = bytereader.bytereader()
		song_data.load_file(input_file)

		cur_track = None
		cur_clip = None
		vol = 100
		pan = 64

		clip_vol_start = 100
		clip_vol_end = 100
		clip_pan_start = 64
		clip_pan_end = 64
		clip_reso = 0
		clip_cutoff = 0

		tlvdatafound = False
		main_iff_obj = song_data.chunk_objmake()
		for chunk_obj in main_iff_obj.iter(0, song_data.end):
			if chunk_obj.id == b'FTdt':
				tlvdatafound = True
				for event_id, event_data in format_flp_tlv.decode(song_data, chunk_obj.end):
					if event_id == 2: vol = event_data
					elif event_id == 3: pan = event_data
					elif event_id == 7: 
						cur_track = ftr_track()
						cur_track.vol = vol
						cur_track.pan = pan
						self.tracks.append(cur_track)

					elif event_id == 200: 
						plugin_obj = ftr_plugin()
						plugin_obj.read(event_data)
						if not cur_track: self.plugins[plugin_obj.slotnum] = plugin_obj
						else: cur_track.plugins[plugin_obj.slotnum] = plugin_obj

					elif event_id == 192: 
						cur_track.name = event_data.decode().rstrip('\x00')

					elif event_id == 5:
						cur_clip = ftr_clip()
						cur_clip.vol_start = clip_vol_start
						cur_clip.vol_end = clip_vol_end
						cur_clip.pan_start = clip_pan_start
						cur_clip.pan_end = clip_pan_end
						cur_clip.reso_start = clip_reso&(0xFFFF)
						cur_clip.reso_end = clip_reso&(0xFFFF0000)>>16
						cur_clip.cutoff_start = clip_cutoff&(0xFFFF)
						cur_clip.cutoff_end = clip_cutoff&(0xFFFF0000)>>16
						cur_clip.muted = event_data
						cur_track.clips.append(cur_clip)

					elif event_id == 10: self.showinfo = event_data
					elif event_id == 12: self.vol = event_data

					elif event_id == 66: self.bpm = event_data
					elif event_id == 132: self.loopstart = event_data
					elif event_id == 133: self.loopend = event_data
					elif event_id == 134: self.zoom_h = event_data
					elif event_id == 135: self.zoom_v = event_data

					elif event_id == 4: clip_vol_start = event_data
					elif event_id == 13: clip_vol_end = event_data
					elif event_id == 8: clip_pan_start = event_data
					elif event_id == 14: clip_pan_end = event_data
					elif event_id == 138: clip_reso = event_data
					elif event_id == 139: clip_cutoff = event_data
					elif event_id == 196: cur_clip.file = event_data.decode().rstrip('\x00')
					elif event_id == 193: cur_clip.name = event_data.decode().rstrip('\x00')
					elif event_id == 129: cur_clip.pos = event_data
					elif event_id == 130: cur_clip.dur = event_data
					elif event_id == 131: cur_clip.repeatlen = event_data
					elif event_id == 137: cur_clip.stretch = event_data
					elif event_id == 15: cur_clip.dontstart = event_data
					elif event_id == 6: cur_clip.showwave = event_data
					elif event_id == 201: cur_clip.vol_env.append(event_data)

					elif event_id == 194: self.title = event_data.decode().rstrip('\x00')
					elif event_id == 197: self.url = event_data.decode().rstrip('\x00')
					elif event_id == 198: self.comment = event_data.decode().rstrip('\x00')
					elif event_id == 199: self.video = event_data.decode().rstrip('\x00')

					if verbose: verboseprint(event_id, event_data)

		if not tlvdatafound: raise ProjectFileParserException('fruitytracks: TLV data not found')
		return tlvdatafound