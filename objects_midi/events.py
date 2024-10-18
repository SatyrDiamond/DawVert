import struct
from dataclasses import dataclass

@dataclass
class NoteOnEvent:
	__slots__ = ['deltaTime', 'channel', 'note', 'velocity']
	deltaTime: int
	channel: int
	note: int
	velocity: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, channel, memoryMap):
		note, velocity = struct.unpack("BB", memoryMap.read(2))
		return cls(deltaTime, channel, note, velocity)

@dataclass
class NoteOffEvent:
	__slots__ = ['deltaTime', 'channel', 'note', 'velocity']
	deltaTime: int
	channel: int
	note: int
	velocity: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, channel, memoryMap):
		note, velocity = struct.unpack("BB", memoryMap.read(2))
		return cls(deltaTime, channel, note, velocity)

@dataclass
class NotePressureEvent:
	__slots__ = ['deltaTime', 'channel', 'note', 'pressure']
	deltaTime: int
	channel: int
	note: int
	pressure: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, channel, memoryMap):
		note = struct.unpack("B", memoryMap.read(1))[0]
		pressure = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, channel, note, pressure)

@dataclass
class ControllerEvent:
	__slots__ = ['deltaTime', 'channel', 'controller', 'value']
	deltaTime: int
	channel: int
	controller: int
	value: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, channel, memoryMap):
		controller = struct.unpack("B", memoryMap.read(1))[0]
		value = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, channel, controller, value)

@dataclass
class ProgramEvent:
	__slots__ = ['deltaTime', 'channel', 'program']
	deltaTime: int
	channel: int
	program: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, channel, memoryMap):
		program = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, channel, program)

@dataclass
class ChannelPressureEvent:
	__slots__ = ['deltaTime', 'channel', 'pressure']
	deltaTime: int
	channel: int
	pressure: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, channel, memoryMap):
		pressure = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, channel, pressure)

@dataclass
class PitchBendEvent:
	__slots__ = ['deltaTime', 'channel', 'pitch']
	deltaTime: int
	channel: int
	pitch: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, channel, memoryMap):
		pitch = struct.unpack("<h", memoryMap.read(2))[0]-16384
		return cls(deltaTime, channel, pitch)

@dataclass
class SequenceNumberEvent:
	__slots__ = ['deltaTime', 'sequenceNumber']
	deltaTime: int
	sequenceNumber: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		sequenceNumber = struct.unpack(">H", memoryMap.read(2))[0]
		return cls(deltaTime, sequenceNumber)

@dataclass
class TextEvent:
	__slots__ = ['deltaTime', 'text']
	deltaTime: int
	text: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		text = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, text)

@dataclass
class CopyrightEvent:
	__slots__ = ['deltaTime', 'copyright']
	deltaTime: int
	copyright: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		copyright = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, copyright)

@dataclass
class TrackNameEvent:
	__slots__ = ['deltaTime', 'name']
	deltaTime: int
	name: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		name = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, name)

@dataclass
class InstrumentNameEvent:
	__slots__ = ['deltaTime', 'name']
	deltaTime: int
	name: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		name = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, name)

@dataclass
class LyricEvent:
	__slots__ = ['deltaTime', 'lyric']
	deltaTime: int
	lyric: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		lyric = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, lyric)

@dataclass
class MarkerEvent:
	__slots__ = ['deltaTime', 'marker']
	deltaTime: int
	marker: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		marker = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, marker)

@dataclass
class CuePointEvent:
	__slots__ = ['deltaTime', 'cuePoint']
	deltaTime: int
	cuePoint: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		cuePoint = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, cuePoint)

@dataclass
class ProgramNameEvent:
	__slots__ = ['deltaTime', 'name']
	deltaTime: int
	name: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		name = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, name)

@dataclass
class DeviceNameEvent:
	__slots__ = ['deltaTime', 'name']
	deltaTime: int
	name: str

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		name = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
		return cls(deltaTime, name)

@dataclass
class MidiChannelPrefixEvent:
	__slots__ = ['deltaTime', 'prefix']
	deltaTime: int
	prefix: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		prefix = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, prefix)

@dataclass
class MidiPortEvent:
	__slots__ = ['deltaTime', 'port']
	deltaTime: int
	port: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		port = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, port)

@dataclass
class EndOfTrackEvent:
	__slots__ = ['deltaTime']
	deltaTime: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		return cls(deltaTime)

@dataclass
class TempoEvent:
	__slots__ = ['deltaTime', 'tempo']
	deltaTime: int
	tempo: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		tempo = struct.unpack(">I", b"\x00" + memoryMap.read(3))[0]
		return cls(deltaTime, tempo)

@dataclass
class SmpteOffsetEvent:
	__slots__ = ['deltaTime', 'hours', 'minutes', 'seconds', 'fps', 'fractionalFrames']
	deltaTime: int
	hours: int
	minutes: int
	seconds: int
	fps: int
	fractionalFrames: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		hours = struct.unpack("B", memoryMap.read(1))[0]
		minutes = struct.unpack("B", memoryMap.read(1))[0]
		seconds = struct.unpack("B", memoryMap.read(1))[0]
		fps = struct.unpack("B", memoryMap.read(1))[0]
		fractionalFrames = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, hours, minutes, seconds, fps, fractionalFrames)

@dataclass
class TimeSignatureEvent:
	__slots__ = ['deltaTime', 'numerator', 'denominator', 'clocksPerClick', 'thirtySecondPer24Clocks']
	deltaTime: int
	numerator: int
	denominator: int
	clocksPerClick: int
	thirtySecondPer24Clocks: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		numerator = struct.unpack("B", memoryMap.read(1))[0]
		denominator = struct.unpack("B", memoryMap.read(1))[0]
		clocksPerClick = struct.unpack("B", memoryMap.read(1))[0]
		thirtySecondPer24Clocks = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, numerator, denominator, clocksPerClick, thirtySecondPer24Clocks)

@dataclass
class KeySignatureEvent:
	__slots__ = ['deltaTime', 'flatsSharps', 'majorMinor']
	deltaTime: int
	flatsSharps: int
	majorMinor: int

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		flatsSharps = struct.unpack("B", memoryMap.read(1))[0]
		majorMinor = struct.unpack("B", memoryMap.read(1))[0]
		return cls(deltaTime, flatsSharps, majorMinor)

@dataclass
class UnknownEvent:
	__slots__ = ['deltaTime', 'data']
	deltaTime: int
	data: bytes

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, data):
		print(length)
		data = data.read(length+1)
		return cls(deltaTime, data)

@dataclass
class SequencerEvent:
	__slots__ = ['deltaTime', 'data']
	deltaTime: int
	data: bytes

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		data = struct.unpack(f"{length}s", memoryMap.read(length))[0]
		return cls(deltaTime, data)

@dataclass
class SysExEvent:
	__slots__ = ['deltaTime', 'data']
	deltaTime: int
	data: bytes

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		data = struct.unpack(f"{length}s", memoryMap.read(length))[0]
		return cls(deltaTime, data)

@dataclass
class EscapeSequenceEvent:
	__slots__ = ['deltaTime', 'data']
	deltaTime: int
	data: bytes

	@classmethod
	def fromMemoryMap(cls, deltaTime, length, memoryMap):
		data = struct.unpack(f"{length}s", memoryMap.read(length))[0]
		return cls(deltaTime, data)

