# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class amped_contentGuid:
	def __init__(self, pd):
		self.is_custom = False
		self.id = None

		if pd != None:
			if 'userAudio' in pd:
				self.is_custom = True
				self.id = pd['userAudio']['exportedId']
			else:
				self.id = pd

	def write(self):
		return {"userAudio": {"exportedId": self.id}} if self.is_custom else self.id

class amped_automation:
	def __init__(self, pd):
		self.param = ''
		self.is_device = False
		self.deviceid = 0
		self.points = []
		self.spec = None

		if pd:
			if 'param' in pd:
				paramname = pd['param']
				if isinstance(paramname, dict):
					self.param = paramname['name']
					self.deviceid = paramname['deviceId']
					self.is_device = True
				else:
					self.param = paramname

			if 'points' in pd: self.points = pd['points']
			if 'spec' in pd: self.spec = pd['spec']

	def write(self):
		amped_auto = {}
		amped_auto['param'] = {'deviceId': self.deviceid, 'name': self.param} if self.is_device else self.param
		amped_auto['points'] = self.points
		if self.spec: amped_auto['spec'] = self.spec
		return amped_auto

class amped_clip:
	def __init__(self, pd):
		self.contentGuid = amped_contentGuid(None)
		self.position = 0
		self.gain = 1
		self.length = 7.999951625094482
		self.offset = 0
		self.stretch = 1
		self.pitchShift = 0
		self.reversed = False
		self.fadeIn = 0

		if pd != None:
			if 'position' in pd: self.position = pd['position']
			if 'gain' in pd: self.gain = pd['gain']
			if 'length' in pd: self.length = pd['length']
			if 'offset' in pd: self.offset = pd['offset']
			if 'stretch' in pd: self.stretch = pd['stretch']
			if 'pitchShift' in pd: self.pitchShift = pd['pitchShift']
			if 'reversed' in pd: self.reversed = pd['reversed']
			if 'fadeIn' in pd: self.fadeIn = pd['fadeIn']
			if 'contentGuid' in pd: self.contentGuid = amped_contentGuid(pd['contentGuid'])

	def write(self):
		amped_clip = {}
		amped_clip['contentGuid'] = self.contentGuid.write()
		amped_clip['position'] = self.position
		amped_clip['gain'] = self.gain
		amped_clip['length'] = self.length
		amped_clip['offset'] = self.offset
		amped_clip['stretch'] = self.stretch
		if self.pitchShift: amped_clip['pitchShift'] = self.pitchShift
		amped_clip['reversed'] = self.reversed
		amped_clip['fadeIn'] = self.fadeIn
		return amped_clip

class amped_region:
	def __init__(self, pd, color):
		self.id = 0
		self.position = 0
		self.length = 8
		self.offset = 0
		self.loop = 0
		self.name = ""
		self.color = None

		self.clips = []

		self.midi_notes = []
		self.midi_events = []
		self.midi_chords = []
		if pd != None:
			if 'id' in pd: self.id = pd['id']
			if 'position' in pd: self.position = pd['position']
			if 'length' in pd: self.length = pd['length']
			if 'offset' in pd: self.offset = pd['offset']
			if 'loop' in pd: self.loop = pd['loop']
			if 'name' in pd: self.name = pd['name']
			self.color = pd['color'] if 'color' in pd else color
			if 'midi' in pd: 
				mididata = pd['midi']
				if 'notes' in mididata: self.midi_notes = mididata['notes']
				if 'events' in mididata: self.midi_events = mididata['events']
				if 'chords' in mididata: self.midi_chords = mididata['chords']
			if 'clips' in pd: self.clips = [amped_clip(clip) for clip in pd['clips']]

	def write(self):
		amped_region = {}
		amped_region['id'] = self.id
		amped_region['position'] = self.position
		amped_region['length'] = self.length
		amped_region['offset'] = self.offset
		amped_region['loop'] = self.loop
		amped_region['clips'] = [x.write() for x in self.clips]
		amped_region['midi'] = {'notes': self.midi_notes, 'events': self.midi_events, 'chords': self.midi_chords}
		amped_region['name'] = self.name
		if self.color != None: amped_region['color'] = self.color
		return amped_region

class amped_param:
	def __init__(self, pd):
		self.id = 0
		self.name = ''
		self.value = 0
		if pd != None:
			if 'id' in pd: self.id = pd['id']
			if 'name' in pd: self.name = pd['name']
			if 'value' in pd: self.value = pd['value']

	def write(self):
		amped_param = {}
		amped_param['id'] = self.id
		amped_param['name'] = self.name
		amped_param['value'] = self.value
		return amped_param

class amped_device:
	def __init__(self, pd):
		self.id = 0
		self.className = ''
		self.label = ''
		self.params = []
		self.preset = None
		self.bypass = True
		self.data = {}

		if pd != None:
			for n, v in pd.items():
				if n == 'id': self.id = v
				elif n == 'className': self.className = v
				elif n == 'label': self.label = v
				elif n == 'params': self.params = [amped_param(p) for p in v]
				elif n == 'preset': self.preset = v
				elif n == 'bypass': self.bypass = v
				else: self.data[n] = v

	def add_param(self, id, name, value):
		d_amped_param = amped_param(None)
		d_amped_param.id = id
		d_amped_param.name = name
		d_amped_param.value = value
		self.params.append(d_amped_param)

	def write(self):
		amped_device = {}
		amped_device['id'] = self.id
		amped_device['className'] = self.className
		amped_device['label'] = self.label
		amped_device['params'] = [x.write() for x in self.params]
		if self.preset != None: amped_device['preset'] = self.preset
		amped_device['bypass'] = self.bypass
		amped_device = amped_device | self.data
		return amped_device


class amped_track:
	def __init__(self, pd):
		self.id = 0
		self.name = ""
		self.color = "mint"
		self.pan = 0
		self.volume = 1
		self.mute = False
		self.solo = False
		self.armed = {}
		self.regions = []
		self.devices = []
		self.automations = []

		if pd != None:
			if 'id' in pd: self.id = pd['id']
			if 'name' in pd: self.name = pd['name']
			if 'color' in pd: self.color = pd['color']
			if 'pan' in pd: self.pan = pd['pan']
			if 'volume' in pd: self.volume = pd['volume']
			if 'mute' in pd: self.mute = pd['mute']
			if 'solo' in pd: self.solo = pd['solo']
			if 'armed' in pd: self.armed = pd['armed']
			if 'regions' in pd: self.regions = [amped_region(region, self.color) for region in pd['regions']]
			if 'devices' in pd: self.devices = [amped_device(device) for device in pd['devices']]
			if 'automations' in pd: self.automations = [amped_automation(device) for device in pd['automations']]

	def add_region(self, position, duration, offset, idnum):
		amped_obj = amped_region(None, 'lime')
		amped_obj.id = idnum
		amped_obj.position = position/4
		amped_obj.length = duration/4
		amped_obj.offset = offset/4
		self.regions.append(amped_obj)
		return amped_obj

	def add_device(self, className, label, idnum): 
		amped_obj = amped_device(None)
		amped_obj.id = idnum
		amped_obj.className = className
		amped_obj.label = label
		self.devices.append(amped_obj)
		return amped_obj

	def add_auto(self, paramid, is_device, deviceid, pointsin, spec):
		amped_obj = amped_automation(None)
		amped_obj.param = paramid
		amped_obj.is_device = is_device
		amped_obj.deviceid = deviceid
		amped_obj.points = pointsin
		amped_obj.spec = spec
		self.automations.append(amped_obj)
		return amped_obj

	def write(self):
		amped_track = {}
		amped_track['id'] = self.id
		amped_track['name'] = self.name
		amped_track['color'] = self.color
		amped_track['pan'] = self.pan
		amped_track['volume'] = self.volume
		amped_track['mute'] = self.mute
		amped_track['solo'] = self.solo
		amped_track['armed'] = self.armed
		amped_track['regions'] = [x.write() for x in self.regions]
		amped_track['devices'] = [x.write() for x in self.devices]
		amped_track['automations'] = [x.write() for x in self.automations]
		return amped_track

class amped_masterTrack:
	def __init__(self, pd):
		self.volume = 1
		self.devices = []

		if pd != None:
			if 'volume' in pd: self.volume = pd['volume']
			if 'devices' in pd: self.devices = [amped_device(device) for device in pd['devices']]

	def write(self):
		amped_mastrack = {}
		amped_mastrack['volume'] = self.volume
		amped_mastrack['devices'] = [x.write() for x in self.devices]
		return amped_mastrack

class amped_project:
	def __init__(self, pd):
		self.fileFormat = 'AMPED SONG v1.3'
		self.createdFrom = None
		self.createdWith = None
		self.settings = {}
		self.tracks = []
		self.masterTrack = amped_masterTrack(None)

		self.loop_active = False
		self.loop_start = 0
		self.loop_end = 0
		self.tempo = 120
		self.timesig_num = 4
		self.timesig_den = 4
		self.metronome = {"active": False, "level": 1}
		self.playheadPosition = 0

		if pd != None:
			if 'fileFormat' in pd: self.fileFormat = pd['fileFormat']
			if 'createdFrom' in pd: self.createdFrom = pd['createdFrom']
			if 'createdWith' in pd: self.createdWith = pd['createdWith']
			if 'settings' in pd: self.settings = pd['settings']
			if 'tracks' in pd:
				for track in pd['tracks']: self.tracks.append(amped_track(track))
			if 'masterTrack' in pd: self.masterTrack = amped_masterTrack(pd['masterTrack'])
			if 'looping' in pd: 
				looping = pd['looping']
				if 'active' in looping: self.loop_active = looping['active']
				if 'start' in looping: self.loop_start = looping['start']
				if 'end' in looping: self.loop_end = looping['end']
			if 'tempo' in pd: self.tempo = pd['tempo']
			if 'timeSignature' in pd: 
				timeSignature = pd['timeSignature']
				if 'num' in timeSignature: self.timesig_num = timeSignature['num']
				if 'den' in timeSignature: self.timesig_den = timeSignature['den']
			if 'metronome' in pd: self.metronome = pd['metronome']
			if 'playheadPosition' in pd: self.playheadPosition = pd['playheadPosition']

	def write(self):
		amped_proj = {}
		amped_proj['fileFormat'] = self.fileFormat
		if self.createdFrom != None: amped_proj['createdFrom'] = self.createdFrom
		if self.createdWith != None: amped_proj['createdWith'] = self.createdWith
		amped_proj['settings'] = self.settings
		amped_proj['tracks'] = [x.write() for x in self.tracks]
		amped_proj['masterTrack'] = self.masterTrack.write()
		amped_proj["workspace"] = {"library":False,"libraryWidth":300,"trackPanelWidth":160,"trackHeight":80,"beatWidth":24,"contentEditor":{"active":False,"trackId":5,"mode":"noteEditor","beatWidth":48,"noteEditorKeyHeight":10,"velocityPanelHeight":90,"velocityPanel":False,"audioEditorVerticalZoom":1,"height":400,"scroll":{"left":0,"top":0},"quantizationValue":0.25,"chordCreator":{"active":False,"scale":{"key":"C","mode":"Major"}}},"trackInspector":True,"trackInspectorTrackId":5,"arrangementScroll":{"left":0,"top":0},"activeTool":"arrow","timeDisplayInBeats":False,"openedDeviceIds":[],"virtualKeyboard":{"active":False,"height":187,"keyWidth":30,"octave":5,"scrollPositions":{"left":0,"top":0}},"xybeatz":{"active":False,"height":350,"zones":[{"genre":"Caribbean","beat":{"bpm":100,"name":"Zouk Electro 2"}},{"genre":"Soul Funk","beat":{"bpm":120,"name":"Defunkt"}},{"genre":"Greatest Breaks","beat":{"bpm":100,"name":"Walk This Way"}},{"genre":"Brazil","beat":{"bpm":95,"name":"Samba Partido Alto 1"}}],"parts":[{"x":0.75,"y":0.75,"gain":1},{"x":0.9,"y":0.2,"gain":1},{"x":0.8,"y":0.45,"gain":1},{"x":0.7,"y":0.7,"gain":1},{"x":0.7,"y":1,"gain":1},{"x":0.5,"y":0.5,"gain":1}],"partId":5,"fullKit":True,"soloPartId":-1,"complexity":50,"zoneId":0,"lastPartId":1},"displayedAutomations":{}}
		amped_proj['looping'] = {"active": self.loop_active, "start": self.loop_start, "end": self.loop_end}
		amped_proj['tempo'] = self.tempo
		amped_proj['timeSignature'] = {"num": self.timesig_num, "den": self.timesig_den}
		amped_proj['metronome'] = self.metronome
		amped_proj['playheadPosition'] = self.playheadPosition
		return amped_proj