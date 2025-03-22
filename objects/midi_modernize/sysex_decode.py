
from io import BytesIO
from objects import globalstore

from objects.data_bytes import bytereader

from objects.midi_modernize.vendors import universal
from objects.midi_modernize.vendors import roland
from objects.midi_modernize.vendors import yamaha
from objects.midi_modernize.vendors import sony

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

		self.vendor = vendor_obj()

		self.sequencer = None
		self.command = None
		self.param = None
		self.value = None

	def detect(self, sysexdata):

		if len(sysexdata)==9:
			if sysexdata[0:6] == b'Sign\x01\xff':
				self.sequencer = 'signal_midi'
				self.param = 'color'
				self.value = [x for x in sysexdata[6:9][::-1]]
				return True

			if sysexdata[0:6] == b'PreS\x01\xff':
				self.sequencer = 'studio_one'
				self.param = 'color'
				self.value = [x for x in sysexdata[6:9][::-1]]
				return True

		bstream = bytereader.bytereader()
		bstream.load_raw(sysexdata)
		
		self.vendor.read(bstream)
		if self.vendor == '#53':
			self.sequencer = 'anvil_studio'
			first = bstream.read(1)[0]
			if first == 15:
				second = bstream.read(1)[0]
				if second == 52: self.param, self.value = 'color', decode_anvil_color(bstream.read(4))
				elif second == 45: self.param, self.value = 'data', bstream.rest().decode().split(',')
				elif second == 6: self.param, self.value = 'synth_name', bstream.rest().decode()
				else: self.value = [15, second, bstream.rest()]
				return True
			else: 
				self.value = [first, bstream.rest()]
				return True

		else:
			self.value = bstream.rest()

	def __repr__(self):

		outstr = '< '
		outstr += 'Vendor:[%s - %s - %s]' % (str(self.vendor.id), str(self.vendor.name), str(self.sequencer))
		outstr += ', Param:"%s"' % str(self.param)
		if self.value: outstr += ', Value:"%s"' % str(self.value if self.param != None else self.value.hex())
		outstr += ' >'

		return outstr

# ------------------------------------------ Vendor ------------------------------------------

class vendor_obj:
	def __init__(self):
		globalstore.idvals.load('midi_sysex', './data_main/idvals/midi_sysex.csv')
		self.bytes = None
		self.ext = False
		self.hex = None

	def __repr__(self):
		name = self.get_name()
		outname = '%s (%s)' % (self.hex, name) if name else self.hex
		return '[Vendor %s]' % outname

	def __eq__(self, o):
		return self.hex==o

	def read(self, bstream):
		self.bytes = bstream.read(1)
		if self.bytes[0] == 0:
			self.ext = True
			self.bytes += bstream.read(2)
		self.hex = '#'+bytes.hex(self.bytes)

	def get_name(self):
		sysexidvals = globalstore.idvals.get('midi_sysex')
		if sysexidvals:
			name = sysexidvals.get_idval(self.hex, 'name')
			if name:
				return name

# ------------------------------------------ SysEx ------------------------------------------

class sysex_obj:
	def __init__(self):
		self.known = False

		self.starttxt = None

		self.vendor = vendor_obj()

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

		if datlen <= 3: return False

		bstream = BytesIO(sysexdata)

		self.vendor.read(bstream)

		self.device = bstream.read(1)[0]
		self.model_id = bstream.read(1)[0]
		self.command = bstream.read(1)[0]

		if self.vendor.ext == False:
			if self.vendor == '#41': 
				roland.decode(self, bstream)

			elif self.vendor in ['#7e', '#7f']: 
				universal.decode(self, bstream)

			elif self.vendor == '#4c': 
				sony.decode(self, bstream)

			elif self.vendor == '#43': 
				yamaha.decode(self, bstream)

		#self.print()

		return True

	def __repr__(self):

		outstr = '< SYSEX | '
		outstr += str(self.vendor)
		outstr += ', Model:"%s"' % (str(self.model_name))
		outstr += ', ParamType:"%s"' % '/'.join([str(x) for x in [self.category, self.group, self.subgroup, self.param, self.num] if x is not None])
		if self.value: outstr += ', Value:"%s"' % str(self.value if self.param != None else self.value.hex())
		outstr += ' >'

		return outstr

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

