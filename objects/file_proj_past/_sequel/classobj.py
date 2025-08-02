# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

classes = {}
from objects.file_proj_past._sequel import func
from dataclasses import dataclass
from dataclasses import dataclass, field

sequel_object = func.sequel_object

def get_object(seqobj):
	if seqobj.obj_class in classes: 
		objc = classes[seqobj.obj_class]()
		objc.from_seqobj(seqobj)
		return objc
	#else:
	#	print('-------------------------')
	#	print('class class_'+seqobj.obj_class+':')
	#	for x in seqobj.obj_data.items():
	#		print( '	'+( x[0].replace(' ','_').lower() )+': '+type(x[1]).__name__+' = '+str(x[1] if type(x[1])!=list else 'list') )
	#	print('	def from_seqobj(self, seqobj):')
	#	print('		obj_data = seqobj.obj_data')
	#	for x in seqobj.obj_data.items():
	#		print("		if '"+x[0]+"' in obj_data: self."+( x[0].replace(' ','_').lower() )+" = obj_data['"+x[0]+"']")
	#	print("classes['"+seqobj.obj_class+"'] = class_"+seqobj.obj_class)

class seq_value:
	value: float = 0
	v_min: float = 0
	v_max: float = 1
	def from_memberobj(self, memberobj):
		if 'Value' in memberobj: self.value = memberobj['Value']
		if 'Min' in memberobj: self.v_min = memberobj['Min']
		if 'Max' in memberobj: self.v_max = memberobj['Max']

@dataclass
class class_ApplicationVersion:
	application: str = '*Sequel*'
	version: str = 'Version 3.0.0'
	builddate: str = 'Jul 26 2011'
	internalnumber: int = 300
	platform: str = 'WIN32'
	encoding: str = 'UTF-8'
	language: str = 'us'
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Application' in obj_data: self.application = obj_data['Application']
		if 'Version' in obj_data: self.version = obj_data['Version']
		if 'BuildDate' in obj_data: self.builddate = obj_data['BuildDate']
		if 'InternalNumber' in obj_data: self.internalnumber = obj_data['InternalNumber']
		if 'Platform' in obj_data: self.platform = obj_data['Platform']
		if 'Encoding' in obj_data: self.encoding = obj_data['Encoding']
		if 'Language' in obj_data: self.language = obj_data['Language']
classes['Application Version'] = class_ApplicationVersion

@dataclass
class class_UColorSet:
	setname: str = 'Event Colors'
	c_set: list = field(default_factory=list)
	c_defset: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'SetName' in obj_data: self.setname = obj_data['SetName']
		if 'Set' in obj_data: self.c_set = obj_data['Set']
		if 'DefSet' in obj_data: self.c_defset = obj_data['DefSet']
classes['UColorSet'] = class_UColorSet

@dataclass
class class_TrackParaEffect:
	name: str = ''
	index: float = 0
	isinsert: float = 1
	playinstop: float = 0
	inputs: list = field(default_factory=list)
	outputs: list = field(default_factory=list)
	transpose: seq_value = field(default_factory=seq_value)
	velocity_shift: seq_value = field(default_factory=seq_value)
	delay: seq_value = field(default_factory=seq_value)
	length_compression: seq_value = field(default_factory=seq_value)
	velocity_compression: seq_value = field(default_factory=seq_value)
	channelizer: seq_value = field(default_factory=seq_value)
	random1: float = 0
	random2: float = 0
	range1: float = 0
	range2: float = 0
	random1min: float = 0
	random1max: float = 0
	random2min: float = 0
	random2max: float = 0
	range1min: float = 1
	range1max: float = 1
	range2min: float = 1
	range2max: float = 1
	scale: seq_value = field(default_factory=seq_value)
	scale_note: seq_value = field(default_factory=seq_value)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Index' in obj_data: self.index = obj_data['Index']
		if 'IsInsert' in obj_data: self.isinsert = obj_data['IsInsert']
		if 'PlayInStop' in obj_data: self.playinstop = obj_data['PlayInStop']
		if 'Inputs' in obj_data: self.inputs = obj_data['Inputs']
		if 'Outputs' in obj_data: self.outputs = obj_data['Outputs']
		if 'Transpose' in obj_data: self.transpose.from_memberobj(obj_data['Transpose'])
		if 'Velocity Shift' in obj_data: self.velocity_shift.from_memberobj(obj_data['Velocity Shift'])
		if 'Delay' in obj_data: self.delay.from_memberobj(obj_data['Delay'])
		if 'Length Compression' in obj_data: self.length_compression.from_memberobj(obj_data['Length Compression'])
		if 'Velocity Compression' in obj_data: self.velocity_compression.from_memberobj(obj_data['Velocity Compression'])
		if 'Channelizer' in obj_data: self.channelizer.from_memberobj(obj_data['Channelizer'])
		if 'Random1' in obj_data: self.random1 = obj_data['Random1']
		if 'Random2' in obj_data: self.random2 = obj_data['Random2']
		if 'Range1' in obj_data: self.range1 = obj_data['Range1']
		if 'Range2' in obj_data: self.range2 = obj_data['Range2']
		if 'Random1Min' in obj_data: self.random1min = obj_data['Random1Min']
		if 'Random1Max' in obj_data: self.random1max = obj_data['Random1Max']
		if 'Random2Min' in obj_data: self.random2min = obj_data['Random2Min']
		if 'Random2Max' in obj_data: self.random2max = obj_data['Random2Max']
		if 'Range1Min' in obj_data: self.range1min = obj_data['Range1Min']
		if 'Range1Max' in obj_data: self.range1max = obj_data['Range1Max']
		if 'Range2Min' in obj_data: self.range2min = obj_data['Range2Min']
		if 'Range2Max' in obj_data: self.range2max = obj_data['Range2Max']
		if 'Scale' in obj_data: self.scale.from_memberobj(obj_data['Scale'])
		if 'Scale Note' in obj_data: self.scale_note.from_memberobj(obj_data['Scale Note'])
classes['TrackParaEffect'] = class_TrackParaEffect

@dataclass
class class_TControllerLaneDef:
	height: int = 80
	view_mode: int = 0
	controller: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Height' in obj_data: self.height = obj_data['Height']
		if 'View Mode' in obj_data: self.view_mode = obj_data['View Mode']
		if 'Controller' in obj_data: self.controller = obj_data['Controller']
classes['TControllerLaneDef'] = class_TControllerLaneDef

@dataclass
class class_Segmentation:
	intervalstartposition: int = 0
	intervalendposition: int = 0
	minimumsegmentlength: int = 0
	numsplitpositions: int = 0
	splitpos: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'intervalStartPosition' in obj_data: self.intervalstartposition = obj_data['intervalStartPosition']
		if 'intervalEndPosition' in obj_data: self.intervalendposition = obj_data['intervalEndPosition']
		if 'minimumSegmentLength' in obj_data: self.minimumsegmentlength = obj_data['minimumSegmentLength']
		if 'numSplitPositions' in obj_data: self.numsplitpositions = obj_data['numSplitPositions']
		for x in range(self.numsplitpositions):
			vstr = 'numSplitPositions'+str(x)
			if vstr in obj_data: self.splitpos[x] = obj_data[vstr]
classes['Segmentation'] = class_Segmentation

@dataclass
class class_StepEnvelopeGroup:
	segmentation: class_Segmentation = field(default_factory=class_Segmentation)
	strategy: str = 'HitPoints'
	envelope: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'segmentation' in obj_data: self.segmentation.from_seqobj(obj_data['segmentation'])
		if 'strategy' in obj_data: self.strategy = obj_data['strategy']
		if 'envelope' in obj_data: self.envelope = [get_object(x) for x in obj_data['envelope']]
		#print(self.envelope)
classes['StepEnvelopeGroup'] = class_StepEnvelopeGroup

@dataclass
class class_StepEnvelope:
	valuetype: str = 'continousRange'
	minvalue: float = 0
	maxvalue: float = 0
	numvalues: int = 0
	values: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'valueType' in obj_data: self.valuetype = obj_data['valueType']
		if 'minValue' in obj_data: self.minvalue = obj_data['minValue']
		if 'maxValue' in obj_data: self.maxvalue = obj_data['maxValue']
		if 'numValues' in obj_data: self.numvalues = obj_data['numValues']
		for x in range(self.numvalues):
			vstr = 'value'+str(x)
			if vstr in obj_data: self.values[x] = obj_data[vstr]
classes['StepEnvelope'] = class_StepEnvelope

@dataclass
class class_SmtgAlgoDescription:
	precision: int = 3
	grainSize: int = 300
	overlap: float = 0.2
	variance: float = 0.8
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'precision' in obj_data: self.precision = obj_data['precision']
		if 'grainSize' in obj_data: self.grainSize = obj_data['grainSize']
		if 'overlap' in obj_data: self.overlap = obj_data['overlap']
		if 'variance' in obj_data: self.variance = obj_data['variance']
classes['SmtgAlgoDescription'] = class_SmtgAlgoDescription

@dataclass
class class_ElastiquePreset:
	processingmode: str = ''
	stereomode: str = ''
	formantpreservation: int = 0
	tapestylemode: int = 0
	pitchaccuratemode: int = 1
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'processingMode' in obj_data: self.processingmode = obj_data['processingMode']
		if 'stereoMode' in obj_data: self.stereomode = obj_data['stereoMode']
		if 'formantPreservation' in obj_data: self.formantpreservation = obj_data['formantPreservation']
		if 'tapeStyleMode' in obj_data: self.tapestylemode = obj_data['tapeStyleMode']
		if 'pitchAccurateMode' in obj_data: self.pitchaccuratemode = obj_data['pitchAccurateMode']
classes['ElastiquePreset'] = class_ElastiquePreset

@dataclass
class class_QCDestinationValue:
	parametertag: int = -1
	nodepath: str = ''
	originalname: str = ''
	isrelativepath: int = 0
	string: str = ''
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'ParameterTag' in obj_data: self.precision = obj_data['ParameterTag']
		if 'NodePath' in obj_data: self.grainSize = obj_data['NodePath']
		if 'OriginalName' in obj_data: self.overlap = obj_data['OriginalName']
		if 'IsRelativePath' in obj_data: self.variance = obj_data['IsRelativePath']
		if 'String' in obj_data: self.variance = obj_data['String']
classes['QCDestinationValue'] = class_QCDestinationValue

@dataclass
class class_MMidiNote:
	start: float = 0
	data1: int = 0
	data2: int = 0
	flags: int = 0
	length: float = 0
	initial_startoffset: float = 0
	data3: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Data2' in obj_data: self.data2 = obj_data['Data2']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Initial Startoffset' in obj_data: self.initial_startoffset = obj_data['Initial Startoffset']
		if 'Data3' in obj_data: self.data3 = obj_data['Data3']
classes['MMidiNote'] = class_MMidiNote

@dataclass
class class_NoteEvent:
	ppqposition: float = 0
	muted: int = 0
	pitch: int = 0
	velocity: int = 0
	offvelocity: int = 0
	controllervalue1: int = 0
	controllervalue2: int = 0
	controllervalue3: int = 0
	lengthininternalppq: int = 0
	ppqoffset: int = 0
	offsettoprevious: int = 0
	index: int = 0
	ischord: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'ppqPosition' in obj_data: self.ppqposition = obj_data['ppqPosition']
		if 'muted' in obj_data: self.muted = obj_data['muted']
		if 'pitch' in obj_data: self.pitch = obj_data['pitch']
		if 'velocity' in obj_data: self.velocity = obj_data['velocity']
		if 'offVelocity' in obj_data: self.offvelocity = obj_data['offVelocity']
		if 'controllerValue1' in obj_data: self.controllervalue1 = obj_data['controllerValue1']
		if 'controllerValue2' in obj_data: self.controllervalue2 = obj_data['controllerValue2']
		if 'controllerValue3' in obj_data: self.controllervalue3 = obj_data['controllerValue3']
		if 'lengthInInternalPpq' in obj_data: self.lengthininternalppq = obj_data['lengthInInternalPpq']
		if 'ppqOffset' in obj_data: self.ppqoffset = obj_data['ppqOffset']
		if 'offsetToPrevious' in obj_data: self.offsettoprevious = obj_data['offsetToPrevious']
		if 'index' in obj_data: self.index = obj_data['index']
		if 'isChord' in obj_data: self.ischord = obj_data['isChord']
classes['NoteEvent'] = class_NoteEvent

@dataclass
class class_CmString:
	s: str = ''
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 's' in obj_data: self.s = obj_data['s']
classes['CmString'] = class_CmString

@dataclass
class class_GTreeEntry:
	#dataobject: sequel_object = field(default_factory=sequel_object)
	flags: int = 0
	name: str = ''
	v_id: int = 0
	subentries: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'DataObject' in obj_data: self.dataobject = obj_data['DataObject']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'ID' in obj_data: self.v_id = obj_data['ID']
		if 'DefSet' in obj_data: self.c_defset = obj_data['DefSet']
classes['GTreeEntry'] = class_GTreeEntry

@dataclass
class class_CmLinkedList:
	ownership: int = 1
	subentries: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'ownership' in obj_data: self.ownership = obj_data['ownership']
		if 'obj' in obj_data: self.obj = [get_object(x) for x in obj_data['obj']]
classes['CmLinkedList'] = class_CmLinkedList

@dataclass
class class_FNPath:
	name: str = ''
	path: str = ''
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Path' in obj_data: self.path = obj_data['Path']
classes['FNPath'] = class_FNPath

@dataclass
class class_CmVariant:
	type: int = 1
	lvalue: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.type = obj_data['type']
		if 'lValue' in obj_data: self.lvalue = obj_data['lValue']
classes['CmVariant'] = class_CmVariant

@dataclass
class class_PStepData:
	idx: int = 0
	vel: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Idx' in obj_data: self.idx = obj_data['Idx']
		if 'Vel' in obj_data: self.vel = obj_data['Vel']
classes['PStepData'] = class_PStepData

@dataclass
class class_PGridDefinition:
	tempo: float = 120
	signom: int = 4
	sigdenom: int = 4
	beats: int = 4
	offset: float = 0.0
	offsettempo: float = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Tempo' in obj_data: self.tempo = obj_data['Tempo']
		if 'SigNom' in obj_data: self.signom = obj_data['SigNom']
		if 'SigDenom' in obj_data: self.sigdenom = obj_data['SigDenom']
		if 'Beats' in obj_data: self.beats = obj_data['Beats']
		if 'Offset' in obj_data: self.offset = obj_data['Offset']
		if 'offsetTempo' in obj_data: self.offsettempo = obj_data['offsetTempo']
classes['PGridDefinition'] = class_PGridDefinition

@dataclass
class class_PAudioWarpScale:
	warptab: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'WarpTab' in obj_data: self.warptab = [get_object(x) for x in obj_data['WarpTab']]
classes['PAudioWarpScale'] = class_PAudioWarpScale

@dataclass
class class_PWarpTab:
	position: float = 0.0
	warped: float = 0.0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Position' in obj_data: self.position = obj_data['Position']
		if 'Warped' in obj_data: self.warped = obj_data['Warped']
classes['PWarpTab'] = class_PWarpTab

@dataclass
class class_AudioCluster:
	substreams: list = field(default_factory=list)
	segments: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Substreams' in obj_data: self.substreams = [get_object(x) for x in obj_data['Substreams']]
		if 'Segments' in obj_data: self.segments = obj_data['Segments']
classes['AudioCluster'] = class_AudioCluster

@dataclass
class class_AudioFile:
	fpath: class_FNPath = field(default_factory=class_FNPath)
	framecount: int = 0
	sample_size: int = 0
	frame_size: int = 0
	channels: int = 0
	rate: float = 0
	format: int = 0
	byteorder: int = 0
	dataoffset: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'FPath' in obj_data: self.fpath.from_seqobj(obj_data['FPath'])
		if 'FrameCount' in obj_data: self.framecount = obj_data['FrameCount']
		if 'Sample Size' in obj_data: self.sample_size = obj_data['Sample Size']
		if 'Frame Size' in obj_data: self.frame_size = obj_data['Frame Size']
		if 'Channels' in obj_data: self.channels = obj_data['Channels']
		if 'Rate' in obj_data: self.rate = obj_data['Rate']
		if 'Format' in obj_data: self.format = obj_data['Format']
		if 'ByteOrder' in obj_data: self.byteorder = obj_data['ByteOrder']
		if 'DataOffset' in obj_data: self.dataoffset = obj_data['DataOffset']
classes['AudioFile'] = class_AudioFile

@dataclass
class class_MRegionMarker:
	name: str = ''
	start: float = 0
	length: float = 0
	origin: float = 0
	snap: float = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Origin' in obj_data: self.origin = obj_data['Origin']
		if 'Snap' in obj_data: self.snap = obj_data['Snap']
classes['MRegionMarker'] = class_MRegionMarker

@dataclass
class class_MHitPointEvent:
	time: float = 0
	weight: float = 0
	flags: int = 0
	filterflags: int = 0
	peak: float = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Time' in obj_data: self.time = obj_data['Time']
		if 'Weight' in obj_data: self.weight = obj_data['Weight']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'FilterFlags' in obj_data: self.filterflags = obj_data['FilterFlags']
		if 'Peak' in obj_data: self.peak = obj_data['Peak']
classes['MHitPointEvent'] = class_MHitPointEvent

@dataclass
class class_PAudioClip:
	name: str = ''
	assetoid: str = ''
	history_number: int = 1
	origin_time: float = 0
	path: class_FNPath = field(default_factory=class_FNPath)
	uid: list = field(default_factory=list)
	additional_attributes: dict = field(default_factory=dict)
	cluster = class_AudioCluster = class_AudioCluster()
	events: list = field(default_factory=list)
	domain: dict = field(default_factory=dict)

	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Additional Attributes' in obj_data:
			self.additional_attributes = {}
			for k, v in obj_data['Additional Attributes'].obj_data.items():
				if k == 'Warpscale': self.additional_attributes['Warpscale'] = get_object(v)
				elif k == 'StretchPreset': 
					if v: self.additional_attributes['StretchPreset'] = get_object(v)
				elif k == 'OrigPath': self.additional_attributes['OrigPath'] = get_object(v)
				elif k == 'GridDef': self.additional_attributes['GridDef'] = get_object(v)
				elif k == 'SampleEditorModelData': self.additional_attributes['SampleEditorModelData'] = v.obj_data
				else: self.additional_attributes[k] = v
		if 'AssetOID' in obj_data: self.assetoid = obj_data['AssetOID']
		if 'Cluster' in obj_data: self.cluster.from_seqobj(obj_data['Cluster'])
		if 'Domain' in obj_data:
			self.domain = {}
			for k, v in obj_data['Domain'].obj_data.items():
				if k == 'Tempo Track': 
					if v: self.domain['Tempo Track'] = get_object(v)
				elif k == 'Signature Track': 
					if v: self.domain['Signature Track'] = get_object(v)
				else: 
					self.domain[k] = v
		if 'Events' in obj_data: self.events = [get_object(x) for x in obj_data['Events']]
		if 'History Number' in obj_data: self.history_number = obj_data['History Number']
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Origin Time' in obj_data: self.origin_time = obj_data['Origin Time']
		if 'Path' in obj_data: self.path.from_seqobj(obj_data['Path'])
		if 'UID' in obj_data: self.uid = obj_data['UID']
classes['PAudioClip'] = class_PAudioClip

@dataclass
class class_MParamEvent:
	start: float = 0
	value: float = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Value' in obj_data: self.value = obj_data['Value']
classes['MParamEvent'] = class_MParamEvent

@dataclass
class class_MLinearInterpolator:
	points: list = field(default_factory=list)
	xmin: float = 0.0
	xmax: float = 1.0
	ymin: float = 0.0
	ymax: float = 1.0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Points' in obj_data: self.points = obj_data['Points']
		if 'XMin' in obj_data: self.xmin = obj_data['XMin']
		if 'XMax' in obj_data: self.xmax = obj_data['XMax']
		if 'YMin' in obj_data: self.ymin = obj_data['YMin']
		if 'YMax' in obj_data: self.ymax = obj_data['YMax']
classes['MLinearInterpolator'] = class_MLinearInterpolator

@dataclass
class class_MFadeOut:
	curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Curve' in obj_data: self.curve.from_seqobj(obj_data['Curve'])
classes['MFadeOut'] = class_MFadeOut

@dataclass
class class_MAutomationTrackEvent:
	flags: int = 0
	start: float = 0
	length: float = 0
	node: sequel_object = sequel_object(None)
	#track_device: sequel_object = sequel_object(None)
	tag: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'Tag' in obj_data: self.tag = obj_data['Tag']
classes['MAutomationTrackEvent'] = class_MAutomationTrackEvent

@dataclass
class class_MAutomationNode:
	name: str = ''
	domain: dict = field(default_factory=dict)
	tracks: list = field(default_factory=list)
	#track_device: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	expanded: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data:
			self.domain = {}
			for k, v in obj_data['Domain'].obj_data.items():
				if k == 'Tempo Track': 
					if v: self.domain['Tempo Track'] = get_object(v)
				elif k == 'Signature Track': 
					if v: self.domain['Signature Track'] = get_object(v)
				else: 
					self.domain[k] = v
		if 'Tracks' in obj_data:
			self.tracks = [get_object(x) for x in obj_data['Tracks']]
		if 'Track Device' in obj_data: 
			self.track_device = obj_data['Track Device']
		if 'Expanded' in obj_data: self.expanded = obj_data['Expanded']
classes['MAutomationNode'] = class_MAutomationNode

@dataclass
class class_PTrackIconData:
	currentimagenamedata: str = ''
	magnifyvaluedata: int = 0
	tintingvaluedata: int = 0
	imagecenterxcoorddata: int = 0
	imagecenterycoorddata: int = 0
	rotatevaluedata: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'currentImageNameData' in obj_data: self.currentimagenamedata = obj_data['currentImageNameData']
		if 'magnifyValueData' in obj_data: self.magnifyvaluedata = obj_data['magnifyValueData']
		if 'tintingValueData' in obj_data: self.tintingvaluedata = obj_data['tintingValueData']
		if 'imageCenterXCoordData' in obj_data: self.imagecenterxcoorddata = obj_data['imageCenterXCoordData']
		if 'imageCenterYCoordData' in obj_data: self.imagecenterycoorddata = obj_data['imageCenterYCoordData']
		if 'rotateValueData' in obj_data: self.rotatevaluedata = obj_data['rotateValueData']
classes['PTrackIconData'] = class_PTrackIconData

@dataclass
class class_MPlayRangeListItem:
	#po_event: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	po_event_repeats: int = 1
	po_event_repeats_rational: float = 0.05
	po_event_itemflags: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'PO Event' in obj_data: self.po_event = obj_data['PO Event']
		if 'PO Event Repeats' in obj_data: self.po_event_repeats = obj_data['PO Event Repeats']
		if 'PO Event Repeats Rational' in obj_data: self.po_event_repeats_rational = obj_data['PO Event Repeats Rational']
		if 'PO Event ItemFlags' in obj_data: self.po_event_itemflags = obj_data['PO Event ItemFlags']
classes['MPlayRangeListItem'] = class_MPlayRangeListItem

@dataclass
class class_MAutoFadeSetting:
	flags: int = 0
	fade_length: float = 0.01
	fadein_curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	fadeout_curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	crossfade_in_curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	crossfade_out_curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Fade Length' in obj_data: self.fade_length = obj_data['Fade Length']
		if 'FadeIn Curve' in obj_data: self.fadein_curve.from_seqobj(obj_data['FadeIn Curve'])
		if 'FadeOut Curve' in obj_data: self.fadeout_curve.from_seqobj(obj_data['FadeOut Curve'])
		if 'Crossfade In Curve' in obj_data: self.crossfade_in_curve.from_seqobj(obj_data['Crossfade In Curve'])
		if 'Crossfade Out Curve' in obj_data: self.crossfade_out_curve.from_seqobj(obj_data['Crossfade Out Curve'])
classes['MAutoFadeSetting'] = class_MAutoFadeSetting

@dataclass
class class_MPlayRangeEvent:
	flags: int = 0
	start: float = 0
	length: float = 0
	additional_attributes: dict = field(default_factory=dict)
	name: str = ''
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes'].obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
classes['MPlayRangeEvent'] = class_MPlayRangeEvent

@dataclass
class class_MMidiPartEvent:
	idnum: int = -1
	start: float = 0
	length: float = 0
	offset: int = 0
	#node: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	additional_attributes: dict = field(default_factory=dict)
	z_order: int = 1
	#quantize: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Offset' in obj_data: self.offset = obj_data['Offset']
		if 'Node' in obj_data: 
			self.node = obj_data['Node']
			self.idnum = self.node.obj_id
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes'].obj_data
		if 'Z-Order' in obj_data: self.z_order = obj_data['Z-Order']
		if 'Quantize' in obj_data: self.quantize = obj_data['Quantize']
classes['MMidiPartEvent'] = class_MMidiPartEvent

@dataclass
class class_MAudioEvent:
	idnum: int = -1
	start: float = 0
	length: float = 0
	priority: int = 1
	offset: int = 0
	additional_attributes: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		self.idnum = seqobj.obj_id
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Offset' in obj_data: self.offset = obj_data['Offset']
		if 'Priority' in obj_data: self.priority = obj_data['Priority']
		if 'AudioClip' in obj_data: 
			self.node = obj_data['AudioClip']
			self.idnum = self.node.obj_id
		if 'Additional Attributes' in obj_data:self.additional_attributes = obj_data['Additional Attributes'].obj_data
classes['MAudioEvent'] = class_MAudioEvent

@dataclass
class class_MListNode:
	name: str = ''
	domain: dict = field(default_factory=dict)
	events: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data: self.domain = obj_data['Domain']
		if 'Events' in obj_data: self.events = [get_object(x) for x in obj_data['Events']]
classes['MListNode'] = class_MListNode

@dataclass
class class_MAutoListNode:
	domain: dict = field(default_factory=dict)
	events: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Domain' in obj_data: self.domain = obj_data['Domain']
		if 'Events' in obj_data: self.events = [get_object(x) for x in obj_data['Events']]
classes['MAutoListNode'] = class_MAutoListNode

@dataclass
class class_MTrack:
	connection_type: int = 0
	device_name: str = ''
	channel_id: int = 0
	deviceattributes: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Device Name' in obj_data: self.device_name = obj_data['Device Name']
		if 'Channel ID' in obj_data: self.channel_id = obj_data['Channel ID']
		if 'DeviceAttributes' in obj_data:
			self.deviceattributes = obj_data['DeviceAttributes'].obj_data
			#print(self.deviceattributes)
classes['MTrack'] = class_MTrack

@dataclass
class class_MDeviceTrackEvent:
	start: float = 0.0
	length: float = 0
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MTrack = field(default_factory=class_MTrack)
	automation: class_MAutomationNode = field(default_factory=class_MAutomationNode)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node.from_seqobj(obj_data['Node'])
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes'].obj_data
		if 'Track Device' in obj_data: self.track_device.from_seqobj(obj_data['Track Device'])
		if 'Automation' in obj_data: self.automation.from_seqobj(obj_data['Automation'])
classes['MDeviceTrackEvent'] = class_MDeviceTrackEvent

@dataclass
class class_MMidiController:
	start: float = 0
	data1: int = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
classes['MMidiController'] = class_MMidiController

@dataclass
class class_MAutomationTrack:
	connection_type: int = 0
	read: int = 0
	write: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Read' in obj_data: self.read = obj_data['Read']
		if 'Write' in obj_data: self.write = obj_data['Write']
classes['MAutomationTrack'] = class_MAutomationTrack

@dataclass
class class_PLaneConfig:
	swingsetting: int = 1
	slide: float = 0.0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'SwingSetting' in obj_data: self.swingsetting = obj_data['SwingSetting']
		if 'Slide' in obj_data: self.slide = obj_data['Slide']
classes['PLaneConfig'] = class_PLaneConfig

@dataclass
class class_CmArray:
	ownership: int = 1
	obj: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'ownership' in obj_data: self.ownership = obj_data['ownership']
		if 'obj' in obj_data: self.obj = [get_object(x) for x in obj_data['obj']]
classes['CmArray'] = class_CmArray

@dataclass
class class_MMidiAfterTouch:
	start: float = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
classes['MMidiAfterTouch'] = class_MMidiAfterTouch

@dataclass
class class_MPlayOrderList:
	po_listname: str = ''
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'PO ListName' in obj_data: self.po_listname = obj_data['PO ListName']
classes['MPlayOrderList'] = class_MPlayOrderList

@dataclass
class class_PCollectPort:
	device: str = ''
	port: str = ''
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Device' in obj_data: self.device = obj_data['Device']
		if 'Port' in obj_data: self.port = obj_data['Port']
classes['PCollectPort'] = class_PCollectPort

@dataclass
class class_PExtendedDuplicator:
	device: str = 'No'
	port: str = ''
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Device' in obj_data: self.device = obj_data['Device']
		if 'Port' in obj_data: self.port = obj_data['Port']
classes['PExtendedDuplicator'] = class_PExtendedDuplicator

@dataclass
class class_PQuickControls:
	numberofquickcontrols: int = 8
	#qcdestinations: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	devicenode_name: str = 'Quick Controls'
	classname: str = 'Quick Controls'
	idstring: str = 'Quick Controls'
	nodeflags: int = 0
	numberclassids: int = 2
	classids: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'NumberOfQuickControls' in obj_data: self.numberofquickcontrols = obj_data['NumberOfQuickControls']
		if 'QCDestinations' in obj_data: self.qcdestinations = obj_data['QCDestinations']
		if 'DeviceNode Name' in obj_data: self.devicenode_name = obj_data['DeviceNode Name']
		if 'ClassName' in obj_data: self.classname = obj_data['ClassName']
		if 'IDString' in obj_data: self.idstring = obj_data['IDString']
		if 'NodeFlags' in obj_data: self.nodeflags = obj_data['NodeFlags']
		if 'NumberClassIDs' in obj_data: self.numberclassids = obj_data['NumberClassIDs']
		if 'ClassIDs' in obj_data: self.classids = obj_data['ClassIDs']
classes['PQuickControls'] = class_PQuickControls

@dataclass
class class_MGridQuantize:
	grid: int = 4
	type: int = 0
	swing: float = 0.0
	unquantized: int = 0
	legato: int = 50
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Grid' in obj_data: self.grid = obj_data['Grid']
		if 'Type' in obj_data: self.type = obj_data['Type']
		if 'Swing' in obj_data: self.swing = obj_data['Swing']
		if 'Unquantized' in obj_data: self.unquantized = obj_data['Unquantized']
		if 'Legato' in obj_data: self.legato = obj_data['Legato']
classes['MGridQuantize'] = class_MGridQuantize

@dataclass
class class_MMidiPitchBend:
	start: float = 0
	data2: int = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data2' in obj_data: self.data2 = obj_data['Data2']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
classes['MMidiPitchBend'] = class_MMidiPitchBend

@dataclass
class class_MMidiPart:
	name: str = ''
	domain: dict = field(default_factory=dict)
	events: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data: self.domain = obj_data['Domain']
		if 'Events' in obj_data: self.events = [get_object(x) for x in obj_data['Events']]
classes['MMidiPart'] = class_MMidiPart

@dataclass
class class_MTransposeTrackNode:
	name: str = ''
	domain: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data: self.domain = obj_data['Domain']
classes['MTransposeTrackNode'] = class_MTransposeTrackNode

@dataclass
class class_MTransposeTrackEvent:
	flags: int = 0
	start: float = 0.0
	length: float = 0
	node: class_MTransposeTrackNode = field(default_factory=class_MTransposeTrackNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MTrack = field(default_factory=class_MTrack)
	bound: int = 1
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node.from_seqobj(obj_data['Node'])
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes'].obj_data
		if 'Track Device' in obj_data: self.track_device.from_seqobj(obj_data['Track Device'])
		if 'bound' in obj_data: self.bound = obj_data['bound']
classes['MTransposeTrackEvent'] = class_MTransposeTrackEvent

@dataclass
class class_FilterDefaults:
	categories: list = field(default_factory=list)
	flags: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'categories' in obj_data: self.categories = [get_object(x) for x in obj_data['categories']]
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
classes['FilterDefaults'] = class_FilterDefaults

@dataclass
class class_GTree:
	root: class_GTreeEntry = field(default_factory=class_GTreeEntry)
	flags: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Root' in obj_data: self.root.from_seqobj(obj_data['Root'])
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
classes['GTree'] = class_GTree

@dataclass
class class_MInstrumentTrack:
	connection_type: int = 0
	device_name: str = ''
	channel_id: int = 0
	deviceattributes: dict = field(default_factory=dict)
	input_type: int = 0
	input_device_id: str = ''
	input_channel_id: int = 0
	input_port_name: str = ''
	solo_flags: int = 0
	drummapname: str = ''
	bank: int = -0
	patch: int = -0
	presetindex: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Device Name' in obj_data: self.device_name = obj_data['Device Name']
		if 'Channel ID' in obj_data: self.channel_id = obj_data['Channel ID']
		if 'DeviceAttributes' in obj_data: self.deviceattributes = obj_data['DeviceAttributes'].obj_data
		if 'Input Type' in obj_data: self.input_type = obj_data['Input Type']
		if 'Input Device ID' in obj_data: self.input_device_id = obj_data['Input Device ID']
		if 'Input Channel ID' in obj_data: self.input_channel_id = obj_data['Input Channel ID']
		if 'Input Port Name' in obj_data: self.input_port_name = obj_data['Input Port Name']
		if 'Solo Flags' in obj_data: self.solo_flags = obj_data['Solo Flags']
		if 'DrummapName' in obj_data: self.drummapname = obj_data['DrummapName']
		if 'Bank' in obj_data: self.bank = obj_data['Bank']
		if 'Patch' in obj_data: self.patch = obj_data['Patch']
		if 'PresetIndex' in obj_data: self.presetindex = obj_data['PresetIndex']
classes['MInstrumentTrack'] = class_MInstrumentTrack

@dataclass
class class_MInstrumentTrackEvent:
	start: float = 0.0
	length: float = 1007999.9899864197
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MInstrumentTrack = field(default_factory=class_MInstrumentTrack)
	height: int = 73
	automation: class_MAutomationNode = field(default_factory=class_MAutomationNode)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node.from_seqobj(obj_data['Node'])
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes'].obj_data
		if 'Track Device' in obj_data: self.track_device.from_seqobj(obj_data['Track Device'])
		if 'Height' in obj_data: self.height = obj_data['Height']
		if 'Automation' in obj_data: self.automation.from_seqobj(obj_data['Automation'])
classes['MInstrumentTrackEvent'] = class_MInstrumentTrackEvent

@dataclass
class class_MAudioTrack:
	connection_type: int = 0
	device_name: str = ''
	channel_id: int = 0
	deviceattributes: dict = field(default_factory=dict)
	flags: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Device Name' in obj_data: self.device_name = obj_data['Device Name']
		if 'Channel ID' in obj_data: self.channel_id = obj_data['Channel ID']
		if 'DeviceAttributes' in obj_data: self.deviceattributes = obj_data['DeviceAttributes'].obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
classes['MAudioTrack'] = class_MAudioTrack

@dataclass
class class_MAudioTrackEvent:
	start: float = 0.0
	length: float = 1007999.9899864197
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MAudioTrack = field(default_factory=class_MAudioTrack)
	height: int = 73
	automation: class_MAutomationNode = field(default_factory=class_MAutomationNode)
	autofade_settings: class_MAutoFadeSetting = field(default_factory=class_MAutoFadeSetting)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node.from_seqobj(obj_data['Node'])
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Track Device' in obj_data: self.track_device.from_seqobj(obj_data['Track Device'])
		if 'Height' in obj_data: self.height = obj_data['Height']
		if 'Automation' in obj_data: self.automation.from_seqobj(obj_data['Automation'])
		if 'Autofade Settings' in obj_data: self.autofade_settings.from_seqobj(obj_data['Autofade Settings'])
classes['MAudioTrackEvent'] = class_MAudioTrackEvent

@dataclass
class class_MPlayRangeTrackEvent:
	flags: int = 32
	start: float = 0.0
	length: float = 1007999.9899864197
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MTrack = field(default_factory=class_MTrack)
	po_listbase: list = field(default_factory=list)
	po_activelist_index: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node.from_seqobj(obj_data['Node'])
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Track Device' in obj_data: self.track_device.from_seqobj(obj_data['Track Device'])
		if 'PO ListBase' in obj_data: self.po_listbase = [get_object(x) for x in obj_data['PO ListBase']]
		if 'PO ActiveList Index' in obj_data: self.po_activelist_index = obj_data['PO ActiveList Index']
classes['MPlayRangeTrackEvent'] = class_MPlayRangeTrackEvent

@dataclass
class class_MTimeSignatureEvent:
	bar: int = 0
	numerator: int = 4
	denominator: int = 4
	position: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Bar' in obj_data: self.bar = obj_data['Bar']
		if 'Numerator' in obj_data: self.numerator = obj_data['Numerator']
		if 'Denominator' in obj_data: self.denominator = obj_data['Denominator']
		if 'Position' in obj_data: self.position = obj_data['Position']
classes['MTimeSignatureEvent'] = class_MTimeSignatureEvent

@dataclass
class class_MSignatureTrackEvent:
	signatureevent: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'SignatureEvent' in obj_data: self.signatureevent = [get_object(x) for x in obj_data['SignatureEvent']]
classes['MSignatureTrackEvent'] = class_MSignatureTrackEvent

@dataclass
class class_MTempoEvent:
	bpm: float = 120.0
	ppq: float = 0.0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'BPM' in obj_data: self.bpm = obj_data['BPM']
		if 'PPQ' in obj_data: self.ppq = obj_data['PPQ']
classes['MTempoEvent'] = class_MTempoEvent

@dataclass
class class_MTempoTrackEvent:
	tempoevent: list = field(default_factory=list)
	rehearsaltempo: float = 120
	rehearsalmode: int = 1
	additional_attributes: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'TempoEvent' in obj_data: self.tempoevent = [get_object(x) for x in obj_data['TempoEvent']]
		if 'RehearsalTempo' in obj_data: self.rehearsaltempo = obj_data['RehearsalTempo']
		if 'RehearsalMode' in obj_data: self.rehearsalmode = obj_data['RehearsalMode']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes'].obj_data
classes['MTempoTrackEvent'] = class_MTempoTrackEvent

@dataclass
class class_MTrackList:
	domain: dict = field(default_factory=dict)
	tracks: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Domain' in obj_data: self.domain = obj_data['Domain']
		if 'Tracks' in obj_data: self.tracks = [get_object(x) for x in obj_data['Tracks']]
classes['MTrackList'] = class_MTrackList

@dataclass
class class_PControllerLaneSetup:
	laneinfo: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'LaneInfo' in obj_data: self.laneinfo = [get_object(x) for x in obj_data['LaneInfo']]
classes['PControllerLaneSetup'] = class_PControllerLaneSetup

@dataclass
class class_PDrumMapPool:
	drum_map: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Drum Map' in obj_data: self.drum_map = [get_object(x) for x in obj_data['Drum Map']]
classes['PDrumMapPool'] = class_PDrumMapPool

@dataclass
class class_PDrumMap:
	name: str = ''
	quantize: list = field(default_factory=list)
	map: list = field(default_factory=list)
	order: list = field(default_factory=list)
	outputdevices: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Quantize' in obj_data: self.quantize = obj_data['Quantize']
		if 'Map' in obj_data: self.map = obj_data['Map']
		if 'Order' in obj_data: self.order = obj_data['Order']
		if 'OutputDevices' in obj_data: self.outputdevices = obj_data['OutputDevices']
classes['PDrumMap'] = class_PDrumMap

@dataclass
class class_PInsVeloPreset:
	velocities: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Velocities' in obj_data: self.velocities = obj_data['Velocities']
classes['PInsVeloPreset'] = class_PInsVeloPreset

@dataclass
class class_PPatternBank:
	name: str = ''
	activepattern: int = 2
	displayedpattern: int = 0
	lanestyle: int = 0
	lanetopitchmap: list = field(default_factory=list)
	mutestates: dict = field(default_factory=dict)
	solostates: dict = field(default_factory=dict)
	usedpatterns: list = field(default_factory=list)
	patterns: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'ActivePattern' in obj_data: self.activepattern = obj_data['ActivePattern']
		if 'DisplayedPattern' in obj_data: self.displayedpattern = obj_data['DisplayedPattern']
		if 'LaneStyle' in obj_data: self.lanestyle = obj_data['LaneStyle']
		if 'LaneToPitchMap' in obj_data: self.lanetopitchmap = obj_data['LaneToPitchMap']
		if 'MuteStates' in obj_data: self.mutestates = obj_data['MuteStates'].obj_data
		if 'SoloStates' in obj_data: self.solostates = obj_data['SoloStates'].obj_data
		if 'UsedPatterns' in obj_data: self.usedpatterns = obj_data['UsedPatterns']
		if 'Patterns' in obj_data: self.patterns = [get_object(x) for x in obj_data['Patterns']]
classes['PPatternBank'] = class_PPatternBank

@dataclass
class class_PPattern:
	nrsteps: int = 16
	stepresolution: int = 120
	swinga: float = 0
	swingb: float = 0
	flampos1: float = 0
	flamvel1: float = 0
	flampos2: float = 0
	flamvel2a: float = 0
	flamvel2b: float = 0
	flampos3: float = 0
	flamvel3a: float = 0
	flamvel3b: float = 0
	flamvel3c: float = 0
	nrlanes: int = 128
	laneconfig: list = field(default_factory=list)
	stepdata: list = field(default_factory=list)
	activesteps: int = 3
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'NrSteps' in obj_data: self.nrsteps = obj_data['NrSteps']
		if 'StepResolution' in obj_data: self.stepresolution = obj_data['StepResolution']
		if 'SwingA' in obj_data: self.swinga = obj_data['SwingA']
		if 'SwingB' in obj_data: self.swingb = obj_data['SwingB']
		if 'FlamPos1' in obj_data: self.flampos1 = obj_data['FlamPos1']
		if 'FlamVel1' in obj_data: self.flamvel1 = obj_data['FlamVel1']
		if 'FlamPos2' in obj_data: self.flampos2 = obj_data['FlamPos2']
		if 'FlamVel2a' in obj_data: self.flamvel2a = obj_data['FlamVel2a']
		if 'FlamVel2b' in obj_data: self.flamvel2b = obj_data['FlamVel2b']
		if 'FlamPos3' in obj_data: self.flampos3 = obj_data['FlamPos3']
		if 'FlamVel3a' in obj_data: self.flamvel3a = obj_data['FlamVel3a']
		if 'FlamVel3b' in obj_data: self.flamvel3b = obj_data['FlamVel3b']
		if 'FlamVel3c' in obj_data: self.flamvel3c = obj_data['FlamVel3c']
		if 'NrLanes' in obj_data: self.nrlanes = obj_data['NrLanes']
		if 'LaneConfig' in obj_data: self.laneconfig = [get_object(x) for x in obj_data['LaneConfig']]
		if 'StepData' in obj_data: self.stepdata = [get_object(x) for x in obj_data['StepData']]
		if 'ActiveSteps' in obj_data: self.activesteps = obj_data['ActiveSteps']
classes['PPattern'] = class_PPattern

@dataclass
class class_PStepDesigner2:
	name: str = ''
	index: int = 0
	isinsert: int = 0
	playinstop: int = 0
	inputs: list = list
	outputs: list = list
	#patternbank: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	triggermode: int = 1
	loopsendlessly: int = 0
	onlyplayduringpatternlength: int = 1
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Index' in obj_data: self.index = obj_data['Index']
		if 'IsInsert' in obj_data: self.isinsert = obj_data['IsInsert']
		if 'PlayInStop' in obj_data: self.playinstop = obj_data['PlayInStop']
		if 'Inputs' in obj_data: self.inputs = obj_data['Inputs']
		if 'Outputs' in obj_data: self.outputs = obj_data['Outputs']
		if 'PatternBank' in obj_data: self.patternbank = obj_data['PatternBank']
		if 'TriggerMode' in obj_data: self.triggermode = obj_data['TriggerMode']
		if 'LoopsEndlessly' in obj_data: self.loopsendlessly = obj_data['LoopsEndlessly']
		if 'OnlyPlayDuringPatternLength' in obj_data: self.onlyplayduringpatternlength = obj_data['OnlyPlayDuringPatternLength']
classes['PStepDesigner2'] = class_PStepDesigner2

@dataclass
class class_PPool:
	media_tree: class_GTree = field(default_factory=class_GTree)
	document_path: class_FNPath = field(default_factory=class_FNPath)
	pool_id: int = 0
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Media Tree' in obj_data: self.media_tree.from_seqobj(obj_data['Media Tree'])
		if 'Document Path' in obj_data: self.document_path.from_seqobj(obj_data['Document Path'])
		if 'Pool ID' in obj_data: self.pool_id = obj_data['Pool ID']
classes['PPool'] = class_PPool

@dataclass
class class_LastAppliedFileInfo:
	#path: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	filename: str = ''
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Path' in obj_data: self.path = obj_data['Path']
		if 'FileName' in obj_data: self.filename = obj_data['FileName']
classes['LastAppliedFileInfo'] = class_LastAppliedFileInfo

@dataclass
class class_PMidiEffectBase:
	name: str = ''
	index: int = 2
	isinsert: int = 0
	playinstop: int = 0
	inputs: list = list
	outputs: list = list
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Index' in obj_data: self.index = obj_data['Index']
		if 'IsInsert' in obj_data: self.isinsert = obj_data['IsInsert']
		if 'PlayInStop' in obj_data: self.playinstop = obj_data['PlayInStop']
		if 'Inputs' in obj_data: self.inputs = obj_data['Inputs']
		if 'Outputs' in obj_data: self.outputs = obj_data['Outputs']
classes['PMidiEffectBase'] = class_PMidiEffectBase

@dataclass
class class_Root_of_Engine:
	start: float = 0.0
	length: float = 0
	node: class_MTrackList = field(default_factory=class_MTrackList)
	additional_attributes: dict = field(default_factory=dict)
	working_directory: class_FNPath = field(default_factory=class_FNPath)
	pool: class_PPool = field(default_factory=class_PPool)
	#tempo_track: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	#signature_track: sequel_object = <Seq3 Obj - Class: "None" Data: []>
	auto_fade_settings: class_MAutoFadeSetting = field(default_factory=class_MAutoFadeSetting)
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node.from_seqobj(obj_data['Node'])
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Working Directory' in obj_data: self.working_directory.from_seqobj(obj_data['Working Directory'])
		if 'Pool' in obj_data: self.pool.from_seqobj(obj_data['Pool'])
		if 'Tempo Track' in obj_data: self.tempo_track = obj_data['Tempo Track']
		if 'Signature Track' in obj_data: self.signature_track = obj_data['Signature Track']
		if 'Auto Fade Settings' in obj_data: self.auto_fade_settings.from_seqobj(obj_data['Auto Fade Settings'])
classes['Root of Engine'] = class_Root_of_Engine

@dataclass
class class_Project:
	data_root: class_Root_of_Engine = field(default_factory=class_Root_of_Engine)
	#setup: sequel_member = <_sequel.func.sequel_member object at 0x00000286AF6C3D90>
	def from_seqobj(self, seqobj):
		obj_data = seqobj.obj_data
		if 'Data Root' in obj_data: self.data_root.from_seqobj(obj_data['Data Root'])
		if 'Setup' in obj_data: self.setup = obj_data['Setup']
classes['Project'] = class_Project