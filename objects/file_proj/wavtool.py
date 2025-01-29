# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

class wavtool_device:
	def __init__(self):
		self.type = ''
		self.sourceId = ''
		self.data = {}
		self.data_internal = {}
		self.name = 0
		self.x = 0
		self.y = 0

class wavtool_cable:
	def __init__(self):
		self.id = ''
		self.input_device = ''
		self.input_id = ''
		self.output_device = ''
		self.output_id = ''
		self.color = None

class wavtool_connections:
	def __init__(self):
		self.tracks = {}
		self.cables = []

	def add_track(self, i_track):
		self.tracks[i_track] = {}

	def add_device(self, i_track, i_id):
		device_obj = wavtool_device()
		self.tracks[i_track][i_id] = device_obj
		return device_obj

	def add_cable(self, input_device, input_id, output_device, output_id):
		cable_obj = wavtool_cable()
		cable_obj.input_device = input_device
		cable_obj.input_id = input_id
		cable_obj.output_device = output_device
		cable_obj.output_id = output_id
		self.cables.append(cable_obj)
		return cable_obj

class wavtool_clip:
	def __init__(self, pd):
		self.type = 'MIDI'
		self.color = '#333333'
		self.name = ''
		self.loopStart = 0
		self.loopEnd = 0
		self.loopEnabled = True
		self.fadeIn = 0
		self.fadeOut = 0
		self.readStart = 0
		self.lifted = False
		self.timelineStart = 0
		self.timelineEnd = 0
		self.transpose = 0
		self.warp = {}
		self.notes = []
		self.ccs = {}
		self.gain = 1
		self.audioBufferId = ''

		if pd != None:
			if 'type' in pd: self.type = pd['type']
			if 'color' in pd: self.color = pd['color']
			if 'name' in pd: self.name = pd['name']
			if 'loopStart' in pd: self.loopStart = pd['loopStart']
			if 'loopEnd' in pd: self.loopEnd = pd['loopEnd']
			if 'loopEnabled' in pd: self.loopEnabled = pd['loopEnabled']
			if 'fadeIn' in pd: self.fadeIn = pd['fadeIn']
			if 'fadeOut' in pd: self.fadeOut = pd['fadeOut']
			if 'readStart' in pd: self.readStart = pd['readStart']
			if 'lifted' in pd: self.lifted = pd['lifted']
			if 'timelineStart' in pd: self.timelineStart = pd['timelineStart']
			if 'timelineEnd' in pd: self.timelineEnd = pd['timelineEnd']
			if 'notes' in pd: self.notes = pd['notes']
			if 'ccs' in pd: self.ccs = pd['ccs']
			if 'gain' in pd: self.gain = pd['gain']
			if 'audioBufferId' in pd: self.audioBufferId = pd['audioBufferId']
			if 'transpose' in pd: self.transpose = pd['transpose']
			if 'warp' in pd: self.warp = pd['warp']

	def write(self):
		wt_clip = {}
		wt_id = str(uuid.uuid4())
		if self.type == 'MIDI':
			wt_clip['id'] = "midiClip-"+wt_id
			wt_clip['name'] = self.name
			wt_clip['color'] = self.color
			wt_clip['lifted'] = self.lifted
			wt_clip['notes'] = self.notes
			wt_clip['ccs'] = self.ccs
			wt_clip['timelineStart'] = self.timelineStart
			wt_clip['timelineEnd'] = self.timelineEnd
			wt_clip['readStart'] = self.readStart
			wt_clip['loopStart'] = self.loopStart
			wt_clip['loopEnd'] = self.loopEnd
			wt_clip['fadeIn'] = self.fadeIn
			wt_clip['fadeOut'] = self.fadeOut
			wt_clip['type'] = self.type
		if self.type == 'Audio':
			wt_clip['gain'] = self.gain
			wt_clip['name'] = self.name
			wt_clip['color'] = self.color
			wt_clip['lifted'] = self.lifted
			wt_clip['fadeIn'] = self.fadeIn
			wt_clip['fadeOut'] = self.fadeOut
			wt_clip['timelineStart'] = self.timelineStart
			wt_clip['timelineEnd'] = self.timelineEnd
			wt_clip['readStart'] = self.readStart
			wt_clip['loopStart'] = self.loopStart
			wt_clip['loopEnd'] = self.loopEnd
			wt_clip['type'] = self.type
			wt_clip['loopEnabled'] = self.loopEnabled
			wt_clip['transpose'] = self.transpose
			wt_clip['audioBufferId'] = self.audioBufferId
			wt_clip['id'] = "audioClip-"+wt_id
			if self.warp: wt_clip['warp'] = self.warp
		return wt_clip

class wavtool_track:
	def __init__(self, pd):
		self.armed = False
		self.type = ''
		self.name = ''
		self.height = 160
		self.hasTimelineSelection = False
		self.gain = 1
		self.balance = 0
		self.color = '#333333'
		self.points = []
		self.clips = []
		self.role = ''
		self.mute = False
		self.solo = False
		self.channelStripId = ''
		self.monitorInput = None
		self.input = None
		self.setting = None

		if pd != None:
			if 'armed' in pd: self.armed = pd['armed']
			if 'type' in pd: self.type = pd['type']
			if 'name' in pd: self.name = pd['name']
			if 'height' in pd: self.height = pd['height']
			if 'hasTimelineSelection' in pd: self.hasTimelineSelection = pd['hasTimelineSelection']
			if 'gain' in pd: self.gain = pd['gain']
			if 'balance' in pd: self.balance = pd['balance']
			if 'color' in pd: self.color = pd['color']
			if 'mute' in pd: self.mute = pd['mute']
			if 'solo' in pd: self.solo = pd['solo']
			if 'channelStripId' in pd: self.channelStripId = pd['channelStripId']
			if 'monitorInput' in pd: self.monitorInput = pd['monitorInput']

			if 'points' in pd: self.points = pd['points']
			if 'clips' in pd: 
				for c in pd['clips']: self.clips.append(wavtool_clip(c))
			self.input = pd['input'] if 'input' in pd else None
			if 'setting' in pd: self.setting = pd['setting']


	def write(self, trackid):
		wt_track = {}
		wt_track['id'] = trackid
		wt_track['armed'] = self.armed
		wt_track['type'] = self.type
		wt_track['name'] = self.name
		wt_track['height'] = self.height
		wt_track['hasTimelineSelection'] = self.hasTimelineSelection
		wt_track['hasHeaderSelection'] = False
		wt_track['gain'] = self.gain
		wt_track['balance'] = self.balance
		if self.role: wt_track['role'] = self.role
		wt_track['color'] = self.color
		if self.type == 'Automation':
			wt_track['points'] = self.points
		wt_track['clips'] = [x.write() for x in self.clips]
		wt_track['mute'] = self.mute
		wt_track['solo'] = self.solo
		wt_track['channelStripId'] = self.channelStripId
		if self.monitorInput: wt_track['monitorInput'] = self.monitorInput
		wt_track['input'] = self.input
		if self.setting: wt_track['setting'] = self.setting
		return wt_track


class wavtool_project:
	def __init__(self, pd):
		self.id = ''
		self.metronome = False
		self.midiOverdub = True
		self.loopStart = 16
		self.loopEnd = 32
		self.loopLifted = False
		self.loopEnabled = False
		self.bpm = 120
		self.beatNumerator = 4
		self.beatDenominator = 4
		self.name = ''
		self.arrangementFocusCategory = 'TrackContent'
		self.conductorMessageHistory = []
		self.conductorUserMessage = ''
		self.tracks = {}
		self.timelineSelectionStart = 48
		self.timelineSelectionEnd = 48
		self.countIn = False
		self.focusedSignal = None
		self.deviceRouting = {}
		self.devices = wavtool_connections()
		self.bpmAutomation = []

		self.devices.add_track('master')

		if pd != None:
			if 'id' in pd: self.id = pd['id']
			if 'metronome' in pd: self.metronome = pd['metronome']
			if 'midiOverdub' in pd: self.midiOverdub = pd['midiOverdub']
			if 'loopStart' in pd: self.loopStart = pd['loopStart']
			if 'loopEnd' in pd: self.loopEnd = pd['loopEnd']
			if 'loopLifted' in pd: self.loopLifted = pd['loopLifted']
			if 'loopEnabled' in pd: self.loopEnabled = pd['loopEnabled']
			if 'bpm' in pd: self.bpm = pd['bpm']
			if 'beatNumerator' in pd: self.beatNumerator = pd['beatNumerator']
			if 'beatDenominator' in pd: self.beatDenominator = pd['beatDenominator']
			if 'name' in pd: self.name = pd['name']
			if 'arrangementFocusCategory' in pd: self.arrangementFocusCategory = pd['arrangementFocusCategory']
			if 'conductorMessageHistory' in pd: self.conductorMessageHistory = pd['conductorMessageHistory']
			if 'conductorUserMessage' in pd: self.conductorUserMessage = pd['conductorUserMessage']
			if 'tracks' in pd: 
				for track in pd['tracks']:
					trackid = track['id']
					self.devices.add_track(trackid)
					self.tracks[trackid] = wavtool_track(track)

			if 'devices' in pd: 
				for dev_id, dev_data in pd['devices'].items():
					dev_trackId = dev_data['trackId']

					device_obj = self.devices.add_device(dev_trackId, dev_id)
					for n, d in dev_data.items():
						if n == 'name': device_obj.name = d
						elif n == 'x': device_obj.x = d
						elif n == 'y': device_obj.y = d
						elif n == 'type': device_obj.type = d
						elif n == 'sourceId': device_obj.sourceId = d
						else: device_obj.data[n] = d

					#print('DEVICE', dev_trackId, dev_id, device_obj.name)


			if 'deviceRouting' in pd: 
				for dev_to, dev_from in pd['deviceRouting'].items():
					from_t, from_i = dev_from.split('.')
					to_t, to_i = dev_to.split('.')
					self.devices.add_cable(from_t, from_i, to_t, to_i)

					#print('CON', from_t, from_i, to_t, to_i)

			if 'timelineSelectionStart' in pd: self.timelineSelectionStart = pd['timelineSelectionStart'] 
			if 'timelineSelectionEnd' in pd: self.timelineSelectionEnd = pd['timelineSelectionEnd'] 
			if 'countIn' in pd: self.countIn = pd['countIn'] 
			if 'focusedSignal' in pd: self.focusedSignal = pd['focusedSignal'] 
			if 'bpmAutomation' in pd: self.bpmAutomation = pd['bpmAutomation']


	def write(self):
		wt_out = {}
		wt_out['id'] = self.id
		wt_out['metronome'] = self.metronome
		wt_out['midiOverdub'] = self.midiOverdub
		wt_out['loopStart'] = self.loopStart
		wt_out['loopEnd'] = self.loopEnd if self.loopStart>self.loopEnd else self.loopEnd+16
		wt_out['loopLifted'] = self.loopLifted
		wt_out['loopEnabled'] = self.loopEnabled
		wt_out['bpm'] = int(self.bpm)
		wt_out['bpmAutomation'] = self.bpmAutomation
		wt_out['markers'] = []
		wt_out['beatNumerator'] = self.beatNumerator
		wt_out['beatDenominator'] = self.beatDenominator
		wt_out['name'] = self.name
		wt_out['arrangementFocusCategory'] = 'TrackContent'
		wt_out['tracks'] = []
		for trackid, track in self.tracks.items():
			wt_out['tracks'].append(track.write(trackid))

		wt_out['timelineSelectionStart'] = self.timelineSelectionStart
		wt_out['timelineSelectionEnd'] = self.timelineSelectionEnd
		wt_out['clipSelectionStart'] = 8.25
		wt_out['clipSelectionEnd'] = 8.25
		wt_out['headerAnchorTrackId'] = None
		wt_out['timelineAnchorTrackId'] = ''
		wt_out['editorTypeIntent'] = 'ClipEditor'
		wt_out['devices'] = {}
		wt_out['deviceRouting'] = {}
		wt_out['focusedSignal'] = self.focusedSignal
		wt_out['skills'] = []
		wt_out['panelTree'] = {"type": "Auto","size": 1,"units": "fr","state":{"follow": False, "xUnitsPerRem": 0.09147721,"xFocusBeats": 58.17143404147059,"yScrollRem": 0}}
		wt_out['focusedTrackId'] = ''
		wt_out['selectedDeviceId'] = None
		wt_out['countIn'] = self.countIn

		wt_devices = wt_out['devices']
		for cable_obj in self.devices.cables:
			to_t = cable_obj.input_device+'.'+cable_obj.input_id
			from_t = cable_obj.output_device+'.'+cable_obj.output_id
			wt_out['deviceRouting'][from_t] = to_t
		for trackid, trackdevices in self.devices.tracks.items():
			for dev_id, device_obj in trackdevices.items():
				device_data = {}
				device_data['id'] = dev_id
				device_data['name'] = device_obj.name

				ordering = device_obj.data_internal['order'] if 'order' in device_obj.data_internal else 0

				if device_obj.type in 'PortalIn':
					device_data['type'] = device_obj.type
					device_data['portalType'] = device_obj.data['portalType']
					device_data['trackId'] = trackid
					for n, d in device_obj.data.items(): device_data[n] = d
					device_data['x'] = device_obj.x
					device_data['y'] = device_obj.y

				if device_obj.type in 'PortalOut':
					device_data['type'] = device_obj.type
					device_data['portalType'] = device_obj.data['portalType']
					device_data['x'] = device_obj.x
					device_data['y'] = device_obj.y
					device_data['trackId'] = trackid
					for n, d in device_obj.data.items(): device_data[n] = d

				if device_obj.type == 'JS':
					if ordering == 1:
						device_data['sourceId'] = device_obj.sourceId
						device_data['trackId'] = trackid
						device_data['x'] = device_obj.x
						device_data['y'] = device_obj.y
						for n, d in device_obj.data.items(): device_data[n] = d
						device_data['type'] = device_obj.type
					elif ordering == 2:
						device_data['sourceId'] = device_obj.sourceId
						device_data['type'] = device_obj.type
						device_data['x'] = device_obj.x
						device_data['y'] = device_obj.y
						for n, d in device_obj.data.items(): device_data[n] = d
						device_data['trackId'] = trackid
					elif ordering == 3:
						device_data['sourceId'] = device_obj.sourceId
						device_data['trackId'] = trackid
						device_data['x'] = device_obj.x
						device_data['y'] = device_obj.y
						for n, d in device_obj.data.items(): device_data[n] = d
						device_data['type'] = device_obj.type
					else:
						device_data['type'] = device_obj.type
						device_data['x'] = device_obj.x
						device_data['y'] = device_obj.y
						for n, d in device_obj.data.items(): device_data[n] = d
						device_data['trackId'] = trackid
						device_data['sourceId'] = device_obj.sourceId

				wt_devices[dev_id] = device_data

		return wt_out