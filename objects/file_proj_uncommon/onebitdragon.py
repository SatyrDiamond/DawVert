# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from io import BytesIO
from objects.exceptions import ProjectFileParserException
import base64
import json
import zlib

# ============================================= instrument ============================================= 

class onebitd_instrument:
	def __init__(self, i_dict):
		self.on = True
		self.volume = 1
		self.audioClipId = 'none'
		self.preset = None
		self.accompanimentId = None
		self.accompaniment = None
		self.presetAccompaniment = None
		self.arpeggiatorId = None
		self.arpeggiator = None
		self.presetArpeggiator = None
		self.offset = None
		self.noteDuration = None
		if i_dict is not None: self.read(i_dict)

	def read(self, i_dict):
		if 'on' in i_dict: self.on = i_dict['on']
		if 'volume' in i_dict: self.volume = i_dict['volume']
		if 'audioClipId' in i_dict: self.audioClipId = i_dict['audioClipId']
		if 'preset' in i_dict: self.preset = i_dict['preset']
		if 'accompanimentId' in i_dict: self.accompanimentId = i_dict['accompanimentId']
		if 'accompaniment' in i_dict: self.accompaniment = i_dict['accompaniment']
		if 'presetAccompaniment' in i_dict: self.presetAccompaniment = i_dict['presetAccompaniment']
		if 'arpeggiatorId' in i_dict: self.arpeggiatorId = i_dict['arpeggiatorId']
		if 'arpeggiator' in i_dict: self.arpeggiator = i_dict['arpeggiator']
		if 'presetArpeggiator' in i_dict: self.presetArpeggiator = i_dict['presetArpeggiator']
		if 'offset' in i_dict: self.offset = i_dict['offset']
		if 'noteDuration' in i_dict: self.noteDuration = i_dict['noteDuration']

	def get_instid(self):
		return 'inst'+'_'.join([str(int(self.on)), str(self.audioClipId), str(self.volume)])

class onebitd_drum:
	def __init__(self, i_dict):
		self.on = True
		self.euclidean = None
		self.audioClipId = 'none'
		self.beats = None
		self.loop = None
		self.offset = None
		self.volume = 1
		self.preset = None
		if i_dict is not None: self.read(i_dict)

	def read(self, i_dict):
		if 'on' in i_dict: self.on = i_dict['on']
		if 'euclidean' in i_dict: self.euclidean = i_dict['euclidean']
		if 'audioClipId' in i_dict: self.audioClipId = i_dict['audioClipId']
		if 'beats' in i_dict: self.beats = i_dict['beats']
		if 'loop' in i_dict: self.loop = i_dict['loop']
		if 'offset' in i_dict: self.offset = i_dict['offset']
		if 'volume' in i_dict: self.volume = i_dict['volume']
		if 'preset' in i_dict: self.preset = i_dict['preset']

	def get_instid(self):
		return 'drum'+'_'.join([str(int(self.on)), str(self.audioClipId), str(self.volume)])

# ============================================= song ============================================= 

class onebitd_block:
	def __init__(self, i_dict):
		self.isEmpty = True
		self.repeat = False
		self.state = 99
		self.columns = []
		self.drums = []
		self.instruments = []
		self.n_drums = [[] for x in range(5)]
		self.n_inst = [[[] for x in range(16)] for x in range(4)]
		if i_dict is not None: self.read(i_dict)

	def read(self, i_dict):
		if 'isEmpty' in i_dict: self.isEmpty = i_dict['isEmpty']
		if 'repeat' in i_dict: self.repeat = i_dict['repeat']
		if 'state' in i_dict: self.state = i_dict['state']
		if 'columns' in i_dict: self.columns = i_dict['columns']
		if 'drums' in i_dict: self.drums = [onebitd_drum(x) for x in i_dict['drums']]
		if 'instruments' in i_dict: self.instruments = [onebitd_instrument(x) for x in i_dict['instruments']]

		if 'notes' in i_dict:
			notesdata = i_dict['notes']
			datafirst = data_values.list__chunks(notesdata, 9*128)
			for firstnum in range(len(datafirst)):
				datasecond = datafirst[firstnum]
				datathird = data_values.list__chunks(datasecond, 9)
				for thirdnum in range(128):
					stepnum = ((thirdnum&0b0000111)<<4)+((thirdnum&0b1111000)>>3)
					forthdata = datathird[thirdnum]
					for notevirt in range(9):
						notevirt_t = -notevirt+8 + firstnum*9
						if 'velocity' in forthdata[notevirt]:
							if forthdata[notevirt]['velocity'] != 0.0:
								tnotedata = [stepnum, forthdata[notevirt]]
								if notevirt_t < 5: self.n_drums[notevirt_t].append(tnotedata)
								else:
									instnumber = notevirt_t-5
									notenumber = instnumber//9
									instnumber -= (instnumber//9)*9
									self.n_inst[instnumber][notenumber].append(tnotedata)

class onebitd_song:
	def __init__(self):
		self.version = None
		self.reverb = False
		self.bpm = 120
		self.scaleId = 0
		self.volume = 1
		self.blocks = []

	def load_from_file(self, input_file):

		try:
			song_file = open(input_file, 'r')
			filetxt = song_file.read()
		except UnicodeDecodeError:
			raise ProjectFileParserException('1bitdragon: File is not text')

		basebase64stream = base64.b64decode(filetxt)
		bio_base64stream = BytesIO(basebase64stream)
		bio_base64stream.seek(4)
		
		try: 
			decompdata = json.loads(zlib.decompress(bio_base64stream.read(), 16+zlib.MAX_WBITS))
		except zlib.error as t:
			raise ProjectFileParserException('1bitdragon: '+str(t))

		self.version = decompdata['version'] if 'version' in decompdata else None
		self.reverb = decompdata['reverb']
		self.bpm = decompdata['bpm']
		self.scaleId = decompdata['scaleId']
		self.volume = decompdata['volume']
		self.blocks = [onebitd_block(x) for x in decompdata['blocks']]
		return True