# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from functions_plugin_ext import plugin_vst2
import json

class serato_sampler_data:
	def __init__(self):
		self.slicePalette = {}
		self.slicePalette["Momentary"] = True
		self.slicePalette["PolyphonicMode"] = False
		self.slicePalette["AutoSetModeState"] = "2"
		self.slicePalette["SlicerSliceLength"] = "4"
		self.slicePalette["CurrentSlicerSlicePositions"] = []
		self.slicePalette["KeyboardModeIndex"] = -1
		self.slicePalette["SelectedParameterTab"] = 0
		self.slicePalette["slicePad"] = [ {"Favourite": False} for _ in range(32)]

		self.sourceSong = {}
		self.sourceSong['Name'] = ""
		self.sourceSong['Artist'] = ""
		self.sourceSong['File'] = ""
		self.sourceSong['OriginalBPM'] = 95
		self.sourceSong['BPM'] = 95
		self.sourceSong['Length'] = 0
		self.sourceSong['PlayheadPosition'] = 0
		self.sourceSong['PlaybackSpeed'] = 1
		self.sourceSong['KeySemitoneOffset'] = 0
		self.sourceSong['KeyCentOffset'] = 0
		self.sourceSong['SyncToHost'] = True
		self.sourceSong['BpmMultiplier'] = 1
		self.sourceSong['Key'] = "12"
		self.sourceSong['Analysis'] = 1
		self.sourceSong['GlideDuration'] = 0
		self.sourceSong['GlideMode'] = "0"
		self.sourceSong['TempoMap'] = "AQAAAAEAAAAAAAAAAAAAAAAAAAAAQFftAAAAAAA/0AAAAAAAAAEAAAABAAAAAAAAAAAAAAAA\nAAAAAAQE\n"
		self.sourceSong['DownbeatIndex'] = 0
		self.sourceSong['SampleRegions'] = ""
		self.sourceSong['PitchShiftingMethod'] = "0"
		self.sourceSong['SelectedStems'] = ["vocals","bass","drums","melody"]
		self.sourceSong['StemsFormatVersion'] = 0
		self.sourceSong['StemsAlgorithmVersion'] = 0
		self.sourceSong['ViewPosition'] = 0
		self.sourceSong['ViewDetail'] = 57
		self.sourceSong['slicePalette'] = self.slicePalette
		self.sourceSong['metronome'] = {"Enabled": False}

		self.params = {}
		self.params['Version'] = 35
		self.params['VaporwaveWaveformsActive'] = False
		self.params['VelocitySensitive'] = False
		self.params['Quantize'] = False
		self.params['sourceSong'] = self.sourceSong

	def to_cvpj_vst2(self, convproj_obj, plugin_obj):
		chunkdata = json.dumps({"project": self.params}, indent=4).encode('utf-8')

		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id','any', 1399681132, 'chunk', chunkdata, None)