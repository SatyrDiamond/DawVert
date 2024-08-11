
from io import BytesIO
#from objects import globalstore

from objects.data_bytes import bytereader

from objects_midi.vendors import universal
from objects_midi.vendors import roland
from objects_midi.vendors import yamaha
from objects_midi.vendors import sony

class vendor_obj:
	def __init__(self, bstream):
		self.id = None
		self.ext = False
		self.name = None
		self.hex = None
		if bstream:
			self.id = bstream.read(1)
			if self.id[0] == 0:
				self.ext = True
				self.id += bstream.read(2)

			self.hex = '#'+bytes.hex(self.id)
			#if idvals_sysex_brands.check_exists(self.hex): 
			#	self.name = idvals_sysex_brands.get_idval(str(self.hex), 'name')
			self.id = int.from_bytes(self.id, 'big')

def decode_anvil_color(anvilcolordata):
	red_p1 = anvilcolordata[3] & 0x3f 
	red_p2 = anvilcolordata[2] & 0xe0
	out_red = (red_p1 << 2) + (red_p2 >> 5)

	green_p1 = anvilcolordata[2] & 0x1f
	green_p2 = anvilcolordata[1] & 0xf0
	out_green = (green_p1 << 3) + (green_p2 >> 4)

	blue_p1 = anvilcolordata[1] & 0x0f
	blue_p2 = anvilcolordata[0] & 0x0f
	out_blue = (blue_p1 << 4) + blue_p2
	return [out_red, out_green, out_blue]

class seqspec_obj:
	def __init__(self):
		self.data = None
		self.known = False

		self.sequencer = None
		self.command = None
		self.param = None
		self.value = None

	def detect(self, sysexdata):
		bstream = bytereader.bytereader()
		bstream.load_raw(sysexdata)

		self.vendor = vendor_obj(bstream)
		if self.vendor.id == 5 and self.vendor.ext == False:
			self.sequencer = 'anvil_studio'
			first = bstream.read(1)[0]
			if first == 15:
				second = bstream.read(1)[0]
				if second == 52: self.param, self.value = 'color', decode_anvil_color(bstream.read(4))
				elif second == 45: self.param, self.value = 'data', bstream.rest().decode().split(',')
				elif second == 6: self.param, self.value = 'synth_name', bstream.rest().decode()
				else: self.value = [15, second, bstream.rest()]
			else: self.value = [first[0], bstream.rest()]

		elif self.vendor.id == 83 and self.vendor.ext == False:
			if bstream.read(5) == b'ign\x01\xff': 
				self.sequencer = 'signal_midi'
				self.param = 'color'
				self.value = [x for x in bstream.read(3)[::-1]]

		elif self.vendor.id == 80 and self.vendor.ext == False:
			if bstream.read(5) == b'reS\x01\xff':
				self.sequencer = 'studio_one'
				self.param = 'color'
				self.value = [x for x in bstream.read(3)[::-1]]

		else:
			self.value = bstream.rest()

	def print(self):
		print(self.vendor.id, self.vendor.name, self.data, self.sequencer, self.param, self.value if self.param != None else self.value.hex())


class sysex_obj:
	def __init__(self):
		#globalstore.idvals.load('midi_sysex', './data_main/idvals/midi_sysex.csv')

		self.known = False

		self.starttxt = None

		self.vendor = None

		self.model_id = None
		self.model_name = None

		self.device = None
		self.command = None

		self.category = None
		self.group = None
		self.subgroup = None
		self.num = None

		self.param = None
		self.value = None

		self.address = None


	def detect(self, sysexdata):
		datlen = len(sysexdata)
		self.starttxt = sysexdata[0:10]

		bstream = BytesIO(sysexdata)

		self.vendor = vendor_obj(bstream)

		if datlen <= 3: return False

		self.device = bstream.read(1)[0]
		self.model_id = bstream.read(1)[0]
		self.command = bstream.read(1)[0]

		if self.vendor.ext == False:
			if self.vendor.id == 65: 
				roland.decode(self, bstream)

			elif self.vendor.id in [126, 127]: 
				universal.decode(self, bstream)

			elif self.vendor.id == 76: 
				sony.decode(self, bstream)

			elif self.vendor.id == 67: 
				yamaha.decode(self, bstream)

		#self.print()

		return True

	def print(self):
		codehex = self.starttxt.hex()
		print(
			self.known, '|', 
			self.vendor.hex, self.vendor.name, self.vendor.id, '|',
			self.device, self.command, '|',
			self.model_id, self.model_name, '|',
			self.category, self.group, self.subgroup, self.num, '|',
			self.param, self.value, '|', ' '.join([codehex[i:i+2] for i in range(0,len(codehex), 2)])
			)

