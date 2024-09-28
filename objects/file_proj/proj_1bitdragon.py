# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from io import BytesIO
import json
import base64
import zlib
from functions import data_values
from objects.exceptions import ProjectFileParserException

class onebitd_instrument:
	def __init__(self, i_dict):
		self.on = i_dict['on']
		self.volume = i_dict['volume']
		self.audioClipId = i_dict['audioClipId']
		self.preset = i_dict['preset']
		self.accompanimentId = i_dict['accompanimentId']
		self.accompaniment = i_dict['accompaniment']
		self.presetAccompaniment = i_dict['presetAccompaniment']
		self.arpeggiatorId = i_dict['arpeggiatorId']
		self.arpeggiator = i_dict['arpeggiator']
		self.presetArpeggiator = i_dict['presetArpeggiator']
		self.offset = i_dict['offset']
		self.noteDuration = i_dict['noteDuration']

	def get_instid(self):
		return 'inst'+'_'.join([str(int(self.on)), str(self.audioClipId), str(self.volume)])

class onebitd_drum:
	def __init__(self, i_dict):
		self.on = i_dict['on']
		self.euclidean = i_dict['euclidean']
		self.audioClipId = i_dict['audioClipId']
		self.beats = i_dict['beats']
		self.loop = i_dict['loop']
		self.offset = i_dict['offset']
		self.volume = i_dict['volume']
		self.preset = i_dict['preset']

	def get_instid(self):
		return 'drum'+'_'.join([str(int(self.on)), str(self.audioClipId), str(self.volume)])

class onebitd_block:
	def __init__(self, i_dict):
		self.isEmpty = i_dict['isEmpty']
		self.repeat = i_dict['repeat']
		self.state = i_dict['state']
		self.columns = i_dict['columns']
		self.drums = [onebitd_drum(x) for x in i_dict['drums']]
		self.instruments = [onebitd_instrument(x) for x in i_dict['instruments']]

		notesdata = i_dict['notes']
		self.n_drums = [[] for x in range(5)]
		self.n_inst = [[[] for x in range(16)] for x in range(4)]

		datafirst = data_values.list__chunks(notesdata, 9*128)
		for firstnum in range(len(datafirst)):
			datasecond = datafirst[firstnum]
			datathird = data_values.list__chunks(datasecond, 9)
			for thirdnum in range(128):
				stepnum = ((thirdnum&0b0000111)<<4)+((thirdnum&0b1111000)>>3)
				forthdata = datathird[thirdnum]
				for notevirt in range(9):
					notevirt_t = -notevirt+8 + firstnum*9
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