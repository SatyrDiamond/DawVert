# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from functions import notelist_data
from functions import data_bytes
from functions import auto
from functions import audio
import plugin_output
import json
import lxml.etree as ET
from xml.dom import minidom

colorlist = ['FF94A6','FFA529','CC9927','F7F47C','BFFB00','1AFF2F','25FFA8','5CFFE8','8BC5FF','5480E4','92A7FF','D86CE4','E553A0','FFFFFF','FF3636','F66C03','99724B','FFF034','87FF67','3DC300','00BFAF','19E9FF','10A4EE','007DC0','886CE4','B677C6','FF39D4','D0D0D0','E2675A','FFA374','D3AD71','EDFFAE','D2E498','BAD074','9BC48D','D4FDE1','CDF1F8','B9C1E3','CDBBE4','AE98E5','E5DCE1','A9A9A9','C6928B','B78256','99836A','BFBA69','A6BE00','7DB04D','88C2BA','9BB3C4','85A5C2','8393CC','A595B5','BF9FBE','BC7196','7B7B7B','AF3333','A95131','724F41','DBC300','85961F','539F31','0A9C8E','236384','1A2F96','2F52A2','624BAD','A34BAD','CC2E6E','3C3C3C']
colorlist_one = [colors.hex_to_rgb_float(color) for color in colorlist]
 

# ---------------------------------------------- Functions Main ----------------------------------------------
# ---------  Main  ---------

unusednum = 500000
def get_unused_id():
    global unusednum
    unusednum += 1
    return unusednum

autopointeenum = 400000
def get_pointee():
    global autopointeenum
    autopointeenum += 1
    return autopointeenum

autocontnum = 300000
def get_contid():
    global autocontnum
    autocontnum += 1
    return autocontnum

clipid = 0
def get_clipid():
    global clipid
    clipid += 1
    return clipid

keytrackid = -1
def get_keytrackid():
    global keytrackid
    keytrackid += 1
    return keytrackid

noteid = 0
def get_noteid():
    global noteid
    noteid += 1
    return noteid

def get_noteid_next():
    global noteid
    return noteid

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

def addvalue(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.set('Value', str(value))
    return x_temp

def addLomId(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.set('LomId', value)
    return x_temp
      
def addId(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.set('Id', value)
    return x_temp
      
def add_up_lower(xmltag, name, target, upper, lower):
    x_temp = ET.SubElement(xmltag, name)
    addvalue(x_temp, 'Target', target)
    addvalue(x_temp, 'UpperDisplayString', upper)
    addvalue(x_temp, 'LowerDisplayString', lower)
    return x_temp
      
def add_min_max(xmltag, name, imin, imax):
    x_temp = ET.SubElement(xmltag, name)
    addvalue(x_temp, 'Min', str(imin))
    addvalue(x_temp, 'Max', str(imax))
    return x_temp
      
def set_add_VideoWindowRect(xmltag):
    x_temp = ET.SubElement(xmltag, 'VideoWindowRect')
    x_temp.set('Top', '-2147483648')
    x_temp.set('Left', '-2147483648')
    x_temp.set('Bottom', '-2147483648')
    x_temp.set('Right', '-2147483648')

def add_xyval(xmltag, x_name, x_x, x_y):
    x_SessionScrollerPos = ET.SubElement(xmltag, x_name)
    x_SessionScrollerPos.set('X', str(x_x))
    x_SessionScrollerPos.set('Y', str(x_y))
#
def create_FollowAction(xmltag, FTime, Linked, LoopIter, FollowAct, FollowCha, JumpIndex, FollowEnabled):
    x_FollowAction = ET.SubElement(xmltag, 'FollowAction')
    addvalue(x_FollowAction, 'FollowTime', str(FTime))
    addvalue(x_FollowAction, 'IsLinked', Linked)
    addvalue(x_FollowAction, 'LoopIterations', str(LoopIter))
    addvalue(x_FollowAction, 'FollowActionA', str(FollowAct[0]))
    addvalue(x_FollowAction, 'FollowActionB', str(FollowAct[1]))
    addvalue(x_FollowAction, 'FollowChanceA', str(FollowCha[0]))
    addvalue(x_FollowAction, 'FollowChanceB', str(FollowCha[1]))
    addvalue(x_FollowAction, 'JumpIndexA', str(JumpIndex[0]))
    addvalue(x_FollowAction, 'JumpIndexB', str(JumpIndex[1]))
    addvalue(x_FollowAction, 'FollowActionEnabled', FollowEnabled)

def create_Locators(xmltag):
    x_temp = ET.SubElement(xmltag, 'Locators')
    x_Locators = ET.SubElement(x_temp, 'Locators')
    return x_Locators
    
def create_Scenes(xmltag):
    x_Scenes = ET.SubElement(xmltag, 'Scenes')
    for scenenum in range(8):
        x_Scene = addId(x_Scenes, 'Scene', str(scenenum))
        create_FollowAction(x_Scene, 4, 'true', 1, [4,0], [100,0], [0,0], 'false')
        addvalue(x_Scene, 'Name', "")
        addvalue(x_Scene, 'Annotation', "")
        addvalue(x_Scene, 'Color', "-1")
        addvalue(x_Scene, 'Tempo', "120")
        addvalue(x_Scene, 'IsTempoEnabled', "false")
        addvalue(x_Scene, 'TimeSignatureId', "201")
        addvalue(x_Scene, 'IsTimeSignatureEnabled', "false")
        addvalue(x_Scene, 'LomId', "0")
        addLomId(x_Scene, 'ClipSlotsListWrapper', "0")

ExpressionLaneNum = 0

def create_ExpressionLanes(xmltag):
    global ExpressionLaneNum
    x_ExpressionLanes = ET.SubElement(xmltag, 'ExpressionLanes')
    for lanenum in range(4):
        x_ExpressionLane = addId(x_ExpressionLanes, 'ExpressionLane', str(lanenum))
        addvalue(x_ExpressionLane, 'Type', str(ExpressionLaneNum))
        addvalue(x_ExpressionLane, 'Size', '41')
        addvalue(x_ExpressionLane, 'IsMinimized', 'true')
        ExpressionLaneNum += 1

def create_ContentLanes(xmltag):
    global ExpressionLaneNum
    x_ContentLanes = ET.SubElement(xmltag, 'ContentLanes')
    for lanenum in range(2):
        x_ExpressionLane = addId(x_ContentLanes, 'ExpressionLane', str(lanenum))
        addvalue(x_ExpressionLane, 'Type', str(ExpressionLaneNum))
        addvalue(x_ExpressionLane, 'Size', '41')
        addvalue(x_ExpressionLane, 'IsMinimized', 'true')
        ExpressionLaneNum += 1

def create_grid(xmltag, xmlname, FixedNumerator, FixedDenominator, GridIntervalPixel, Ntoles, SnapToGrid, Fixed):
    x_Grid = ET.SubElement(xmltag, xmlname)
    addvalue(x_Grid, 'FixedNumerator', str(FixedNumerator))
    addvalue(x_Grid, 'FixedDenominator', str(FixedDenominator))
    addvalue(x_Grid, 'GridIntervalPixel', str(GridIntervalPixel))
    addvalue(x_Grid, 'Ntoles', str(Ntoles))
    addvalue(x_Grid, 'SnapToGrid', str(SnapToGrid))
    addvalue(x_Grid, 'Fixed', str(Fixed))

def create_transport(xmltag, loopstart, looplen, Loopon):
    x_Transport = ET.SubElement(xmltag, 'Transport')
    addvalue(x_Transport, 'PhaseNudgeTempo', '10')
    addvalue(x_Transport, 'LoopOn', str(Loopon))
    addvalue(x_Transport, 'LoopStart', str(loopstart))
    addvalue(x_Transport, 'LoopLength', str(looplen))
    addvalue(x_Transport, 'LoopIsSongStart', 'false')
    addvalue(x_Transport, 'CurrentTime', '0')
    addvalue(x_Transport, 'PunchIn', 'false')
    addvalue(x_Transport, 'PunchOut', 'false')
    addvalue(x_Transport, 'MetronomeTickDuration', '0')
    addvalue(x_Transport, 'DrawMode', 'false')

def create_GroovePool(xmltag):
    x_temp = ET.SubElement(xmltag, 'GroovePool')
    addvalue(x_temp, 'LomId', '0')
    ET.SubElement(x_temp, 'Grooves')
    
def create_AutoColorPickerForPlayerAndGroupTracks(xmltag):
    x_temp = ET.SubElement(xmltag, 'AutoColorPickerForPlayerAndGroupTracks')
    addvalue(x_temp, 'NextColorIndex', '15')
    
def create_AutoColorPickerForReturnAndMasterTracks(xmltag):
    x_temp = ET.SubElement(xmltag, 'AutoColorPickerForReturnAndMasterTracks')
    addvalue(x_temp, 'NextColorIndex', '14')

def create_scaleinformation(xmltag):
    x_ScaleInformation = ET.SubElement(xmltag, 'ScaleInformation')
    addvalue(x_ScaleInformation, 'RootNote', '0')
    addvalue(x_ScaleInformation, 'Name', 'Major')

def create_songmastervalues(xmltag):
    x_SongMasterValues = ET.SubElement(xmltag, 'SongMasterValues')
    add_xyval(x_SongMasterValues, 'SessionScrollerPos', 0, 0)

def create_sequencernavigator(xmltag):
    x_SequencerNavigator = ET.SubElement(xmltag, 'SequencerNavigator')
    x_BeatTimeHelper = ET.SubElement(x_SequencerNavigator, 'BeatTimeHelper')
    addvalue(x_BeatTimeHelper, 'CurrentZoom', '0.08')
    add_xyval(x_SequencerNavigator, 'ScrollerPos', 0, 0)
    add_xyval(x_SequencerNavigator, 'ClientSize', 888, 587)

def create_viewstates(xmltag):
    x_Transport = ET.SubElement(xmltag, 'ViewStates')
    addvalue(x_Transport, 'SessionIO', '1')
    addvalue(x_Transport, 'SessionSends', '1')
    addvalue(x_Transport, 'SessionReturns', '1')
    addvalue(x_Transport, 'SessionMixer', '1')
    addvalue(x_Transport, 'SessionTrackDelay', '0')
    addvalue(x_Transport, 'SessionCrossFade', '0')
    addvalue(x_Transport, 'SessionShowOverView', '0')
    addvalue(x_Transport, 'ArrangerIO', '1')
    addvalue(x_Transport, 'ArrangerReturns', '1')
    addvalue(x_Transport, 'ArrangerMixer', '1')
    addvalue(x_Transport, 'ArrangerTrackDelay', '0')
    addvalue(x_Transport, 'ArrangerShowOverView', '1')

def create_timeselection(xmltag, AnchorTime, OtherTime):
    x_Transport = ET.SubElement(xmltag, 'TimeSelection')
    addvalue(x_Transport, 'AnchorTime', str(AnchorTime))
    addvalue(x_Transport, 'OtherTime', str(OtherTime))

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------- Track Base Data --------------------------------------------------------------

# ---------------- Device Chain / Mixer ----------------

def set_add_param(xmltag, param_name, param_value, auto_id, modu_id, midi_cc_thres, midi_cont_range):
    x_temp = ET.SubElement(xmltag, param_name)
    addvalue(x_temp, 'LomId', '0')
    addvalue(x_temp, 'Manual', param_value)
    x_AutomationTarget = addId(x_temp, 'AutomationTarget', str(auto_id))
    addvalue(x_AutomationTarget, 'LockEnvelope', '0')
    if modu_id != None: 
        x_ModulationTarget = addId(x_temp, 'ModulationTarget', str(modu_id))
        addvalue(x_ModulationTarget, 'LockEnvelope', '0')
    if midi_cc_thres != None: add_min_max(x_temp, 'MidiCCOnOffThresholds', midi_cc_thres[0], midi_cc_thres[1])
    if midi_cont_range != None: add_min_max(x_temp, 'MidiControllerRange', midi_cont_range[0], midi_cont_range[1])
      
def create_devicechain_mixer(xmltag, tracktype):
    global cvpj_bpm
    xmltag = ET.SubElement(xmltag, 'Mixer')
    addvalue(xmltag, 'LomId', '0')
    addvalue(xmltag, 'LomIdView', '0')
    addvalue(xmltag, 'IsExpanded', 'true')
    set_add_param(xmltag, 'On', 'true', str(get_unused_id()), None, [64,127], None)
    addvalue(xmltag, 'ModulationSourceCount', '0')
    addLomId(xmltag, 'ParametersListWrapper', '0')
    addId(xmltag, 'Pointee', str(get_pointee()))
    addvalue(xmltag, 'LastSelectedTimeableIndex', '0')
    addvalue(xmltag, 'LastSelectedClipEnvelopeIndex', '0')
    x_LastPresetRef = ET.SubElement(xmltag, 'LastPresetRef')
    x_LastPresetRef_Value = ET.SubElement(x_LastPresetRef, 'Value')
    x_LockedScripts = ET.SubElement(xmltag, 'LockedScripts')
    addvalue(xmltag, 'IsFolded', 'false')
    addvalue(xmltag, 'ShouldShowPresetName', 'false')
    addvalue(xmltag, 'UserName', '')
    addvalue(xmltag, 'Annotation', '')
    x_SourceContext = ET.SubElement(xmltag, 'SourceContext')
    x_SourceContext_Value = ET.SubElement(x_SourceContext, 'Value')
    x_Sends = ET.SubElement(xmltag, 'Sends')
    set_add_param(xmltag, 'Speaker', 'true', str(get_unused_id()), None, [64,127], None)
    addvalue(xmltag, 'SoloSink', 'false')
    addvalue(xmltag, 'PanMode', '0')
    set_add_param(xmltag, 'Pan', '0', str(get_unused_id()), str(get_unused_id()), None, [-1,1])
    set_add_param(xmltag, 'SplitStereoPanL', '-1', str(get_unused_id()), str(get_unused_id()), None, [-1,1])
    set_add_param(xmltag, 'SplitStereoPanR', '1', str(get_unused_id()), str(get_unused_id()), None, [-1,1])
    set_add_param(xmltag, 'Volume', '1', str(get_unused_id()), str(get_unused_id()), None, [0.0003162277571,1.99526238])
    addvalue(xmltag, 'ViewStateSesstionTrackWidth', '93')
    set_add_param(xmltag, 'CrossFadeState', '1', str(get_unused_id()), None, None, None)
    addLomId(xmltag, 'SendsListWrapper', '0')
    if tracktype == 'master':
        set_add_param(xmltag, 'Tempo', str(cvpj_bpm), str(get_unused_id()), str(get_unused_id()), None, [60,200])
        set_add_param(xmltag, 'TimeSignature', '201', str(get_unused_id()), None, None, None)
        set_add_param(xmltag, 'GlobalGrooveAmount', '100', str(get_unused_id()), str(get_unused_id()), None, [0,131.25])
        set_add_param(xmltag, 'CrossFade', '0', str(get_unused_id()), str(get_unused_id()), None, [-1,1])
        addvalue(xmltag, 'TempoAutomationViewBottom', '60')
        addvalue(xmltag, 'TempoAutomationViewTop', '200')

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------- Track Base / MainSequencer / MIDI Clips ----------------

def make_auto_point(xmltag, value, position, SubElementname):
    x_autopoint = ET.SubElement(xmltag, SubElementname)
    x_autopoint.set('TimeOffset', str(position/4))
    x_autopoint.set('Value', str(value))
    x_autopoint.set('CurveControl1X', '0.5')
    x_autopoint.set('CurveControl1Y', '0.5')
    x_autopoint.set('CurveControl2X', '0.5')
    x_autopoint.set('CurveControl2Y', '0.5')

def t_parse_automation(xmltag, cvpj_points):
    cvpj_points_no_instant = auto.remove_instant(cvpj_points, 0, True)
    for cvpj_point in cvpj_points_no_instant:
        make_auto_point(xmltag, cvpj_point['value']*170, cvpj_point['position'], "PerNoteEvent")

def create_notelist(xmltag, cvpj_notelist):
    t_keydata = {}
    x_KeyTracks = ET.SubElement(xmltag, 'KeyTracks')
    for note in cvpj_notelist:
        if note['key'] not in t_keydata: t_keydata[note['key']] = []
        note['id'] = get_noteid()
        t_keydata[note['key']].append(note)

    t_keydata = dict(sorted(t_keydata.items(), key=lambda item: item[0]))

    t_notemod = {}

    for keynum in t_keydata:
        x_KeyTrack = addId(x_KeyTracks, 'KeyTrack', str(get_keytrackid()))
        x_KeyTrack_notes = ET.SubElement(x_KeyTrack, 'Notes')
        for t_note in t_keydata[keynum]:
            x_MidiNoteEvent = ET.SubElement(x_KeyTrack_notes, 'MidiNoteEvent')
            x_MidiNoteEvent.set('Time', str(t_note['position']/4))
            x_MidiNoteEvent.set('Duration', str(t_note['duration']/4))
            if 'vol' in t_note: x_MidiNoteEvent.set('Velocity', str(t_note['duration']*100))
            else: x_MidiNoteEvent.set('Velocity', "100")
            x_MidiNoteEvent.set('VelocityDeviation', "0")
            if 'off_vol' in t_note: x_MidiNoteEvent.set('OffVelocity', str(t_note['off_vol']*100))
            else: x_MidiNoteEvent.set('OffVelocity', "64")
            if 'probability' in t_note: x_MidiNoteEvent.set('Probability', str(t_note['probability']))
            else: x_MidiNoteEvent.set('Probability', "1")
            if 'enabled' in t_note:
                if t_note['enabled'] == 1: x_MidiNoteEvent.set('IsEnabled', "true")
                if t_note['enabled'] == 0: x_MidiNoteEvent.set('IsEnabled', "false")
            else: x_MidiNoteEvent.set('IsEnabled', "true")
            if 'notemod' in t_note:
                if 'auto' in t_note['notemod']:
                    t_notemod[t_note['id']] = t_note['notemod']['auto']
            x_MidiNoteEvent.set('NoteId', str(t_note['id']))
        addvalue(x_KeyTrack, 'MidiKey', str(keynum+60))

    x_PerNoteEventStore = ET.SubElement(xmltag, 'PerNoteEventStore')
    x_EventLists = ET.SubElement(x_PerNoteEventStore, 'EventLists')

    PerNoteEventListID = 0
    for notemodnum in t_notemod:
        x_PerNoteEventList = ET.SubElement(x_EventLists, "PerNoteEventList")
        x_PerNoteEventList.set('Id', str(PerNoteEventListID))
        x_PerNoteEventList.set('NoteId', str(notemodnum))
        x_PerNoteEventList.set('CC', "-2")
        x_PerNoteEvents = ET.SubElement(x_PerNoteEventList, "Events")
        if 'pitch' in t_notemod[notemodnum]:
            t_parse_automation(x_PerNoteEvents, t_notemod[notemodnum]['pitch'])
        PerNoteEventListID += 1

    x_NoteIdGenerator = ET.SubElement(xmltag, 'NoteIdGenerator')
    addvalue(x_NoteIdGenerator, 'NextId', str(get_noteid_next()+1))

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------- Track Base / MainSequencer / Audio Clips ----------------


def create_sampleref(xmltag, aud_sampledata):
    x_SampleRef = ET.SubElement(xmltag, 'SampleRef')
    x_FileRef = ET.SubElement(x_SampleRef, 'FileRef')
    addvalue(x_FileRef, 'RelativePathType', '1')
    addvalue(x_FileRef, 'RelativePath', '')
    addvalue(x_FileRef, 'Path', aud_sampledata['path'])
    addvalue(x_FileRef, 'Type', '1')
    addvalue(x_FileRef, 'LivePackName', '')
    addvalue(x_FileRef, 'LivePackId', '')
    addvalue(x_FileRef, 'OriginalFileSize', aud_sampledata['file_size'])
    addvalue(x_FileRef, 'OriginalCrc', aud_sampledata['crc'])
    addvalue(x_SampleRef, 'LastModDate', aud_sampledata['mod_date'])
    x_SourceContext = ET.SubElement(x_SampleRef, 'SourceContext')
    addvalue(x_SampleRef, 'SampleUsageHint', '0')
    addvalue(x_SampleRef, 'DefaultDuration', aud_sampledata['dur'])
    addvalue(x_SampleRef, 'DefaultSampleRate', aud_sampledata['rate'])

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

def create_clip(xmltag, cliptype, cvpj_placement, trackcolor):
    cvpj_position = cvpj_placement['position']
    cvpj_duration = cvpj_placement['duration']

    able_position = cvpj_position/4
    able_duration = cvpj_duration/4

    t_name = ''
    t_color = trackcolor
    t_notelist = []
    t_disabled = 'false'
    if 'name' in cvpj_placement: t_name = cvpj_placement['name']
    if 'color' in cvpj_placement: t_color = colors.closest_color_index(colorlist_one, cvpj_placement['color'])
    if 'notelist' in cvpj_placement: t_notelist = notelist_data.sort(cvpj_placement['notelist'])
    if 'muted' in cvpj_placement: 
        if cvpj_placement['muted'] == 1: 
            t_disabled = 'true'

    # ------------------------------------------ audio ------------------------------------------
    t_file = ''
    t_vol = 1

    tempomul = (cvpj_bpm/120)

    if cliptype == 'audio':
        if 'file' in cvpj_placement: t_file = cvpj_placement['file']
        aud_sampledata = audio.get_audiofile_info(t_file)
        AudioDuration = aud_sampledata['dur_sec']
        normalspeed = (AudioDuration)*tempomul
        w_timemarkers = [{'pos': 0.0, 'pos_real': 0.0},{'pos': normalspeed, 'pos_real': AudioDuration}]
        if 'vol' in cvpj_placement: t_vol = cvpj_placement['vol']

    w_IsWarped = 'false'
    w_WarpMode = 4
    w_ComplexProEnvelope = 128
    w_ComplexProFormants = 100
    w_FluctuationTexture = 25
    w_GranularityTexture = 65
    w_GranularityTones = 30
    w_TransientEnvelope = 100 
    w_TransientLoopMode = 2
    w_TransientResolution = 6
    stretch_t_steps = able_duration
    stretch_t_pitch = 0
    FadeEnabled = 'false'
    FadeInCurveSkew = 0
    FadeInCurveSlope = 0
    FadeInLength = 0
    FadeOutCurveSkew = 0
    FadeOutCurveSlope = 0
    FadeOutLength = 0

    speedrate = 1

    # -------------------------------------------------------------------------------------------

    t_CurrentStart = able_position
    t_CurrentEnd = able_duration+able_position
    t_LoopStart = 0


    t_StartRelative = 0
    t_LoopOn = 'false'

    t_LoopEnd = (t_CurrentEnd/2)/tempomul

    cvpj_isstretched = False

    if cliptype == 'audio':

        if 'cut' in cvpj_placement:
            cvpj_placement_cut = cvpj_placement['cut']

            if 'type' in cvpj_placement_cut:
                if cvpj_isstretched == True:
                    if cvpj_placement_cut['type'] == 'cut':
                        if 'start' in cvpj_placement_cut: t_LoopStart = cvpj_placement_cut['start']/4
                        if 'end' in cvpj_placement_cut: t_LoopEnd = cvpj_placement_cut['end']/4
                    if cvpj_placement_cut['type'] == 'loop':
                        t_LoopOn = 'true'
                        if 'start' in cvpj_placement_cut: t_StartRelative = cvpj_placement_cut['start']/4
                        if 'loopstart' in cvpj_placement_cut: t_LoopStart = cvpj_placement_cut['loopstart']/4
                        if 'loopend' in cvpj_placement_cut: t_LoopEnd = cvpj_placement_cut['loopend']/4
                else:
                    if cvpj_placement_cut['type'] == 'cut':
                        if 'start' in cvpj_placement_cut: t_LoopStart = cvpj_placement_cut['start_real']
                        if 'end' in cvpj_placement_cut: t_LoopEnd = cvpj_placement_cut['end_real']
                    if cvpj_placement_cut['type'] == 'loop':
                        t_LoopOn = 'true'
                        w_IsWarped = 'true'
                        cvpj_placement['audiomod'] = {}
                        cvpj_placement['audiomod']['stretch'] = {}
                        cvpj_placement['audiomod']['stretch']['enabled'] = True
                        cvpj_placement['audiomod']['stretch']['time'] = {'type': 'rate_timed', 'data': {'rate': 1}}
                        
                        if 'start' in cvpj_placement_cut: t_StartRelative = cvpj_placement_cut['start']
                        if 'loopstart' in cvpj_placement_cut: t_LoopStart = cvpj_placement_cut['loopstart']
                        if 'loopend' in cvpj_placement_cut: t_LoopEnd = cvpj_placement_cut['loopend']



        if 'audiomod' in cvpj_placement:
            if 'stretch' in cvpj_placement['audiomod']:
                cvpj_stretch = cvpj_placement['audiomod']['stretch']

                if 'enabled' in cvpj_stretch: 
                    if cvpj_stretch['enabled'] == True: w_IsWarped = 'true'

                    if w_IsWarped == 'true':
                        cvpj_isstretched = True
                        if 'params' in cvpj_stretch: 
                            stretch_params = cvpj_stretch['params']
                            if 'ComplexProEnvelope' in stretch_params: w_ComplexProEnvelope = stretch_params['ComplexProEnvelope']
                            if 'ComplexProFormants' in stretch_params: w_ComplexProEnvelope = stretch_params['ComplexProFormants']
                            if 'FluctuationTexture' in stretch_params: w_ComplexProEnvelope = stretch_params['FluctuationTexture']
                            if 'GranularityTexture' in stretch_params: w_ComplexProEnvelope = stretch_params['GranularityTexture']
                            if 'GranularityTones' in stretch_params: w_ComplexProEnvelope = stretch_params['GranularityTones']
                            if 'TransientEnvelope' in stretch_params: w_ComplexProEnvelope = stretch_params['TransientEnvelope']
                            if 'TransientLoopMode' in stretch_params: w_ComplexProEnvelope = stretch_params['TransientLoopMode']
                            if 'TransientResolution' in stretch_params: w_ComplexProEnvelope = stretch_params['TransientResolution']

                        if 'mode' in cvpj_stretch: 
                            if cvpj_stretch == 'ableton_beats': w_WarpMode = 0
                            if cvpj_stretch == 'ableton_tones': w_WarpMode = 1
                            if cvpj_stretch == 'ableton_texture': w_WarpMode = 2
                            if cvpj_stretch == 'resample': w_WarpMode = 3
                            if cvpj_stretch == 'ableton_complex': w_WarpMode = 4
                        if cvpj_stretch == 'stretch_complexpro': w_WarpMode = 6

                        if 'pitch' in cvpj_stretch: stretch_t_pitch = cvpj_stretch['pitch']

                        if 'time' in cvpj_stretch:
                            if 'type' in cvpj_stretch['time'] and 'data' in cvpj_stretch['time']:
                                timedata = cvpj_stretch['time']['data']

                                if cvpj_stretch['time']['type'] == 'rate_timed': 
                                   speedrate = timedata['rate']
                                   rate_fixed = (1/speedrate)*AudioDuration
                                   w_timemarkers = [{'pos': 0.0, 'pos_real': 0.0}, {'pos': normalspeed*8, 'pos_real': rate_fixed}]


        #for value in [t_CurrentStart, t_CurrentEnd, t_StartRelative, t_LoopStart, t_LoopEnd]:
        #    print(str(value).ljust(20), end=' ')
        #print()

    else:
        t_LoopEnd = t_CurrentEnd
        if 'cut' in cvpj_placement:
            cvpj_placement_cut = cvpj_placement['cut']
            if 'type' in cvpj_placement_cut:
                if cvpj_placement_cut['type'] == 'cut':
                    t_StartRelative = 0
                    if 'start' in cvpj_placement_cut: t_StartRelative = (cvpj_placement_cut['start']/4)
                if cvpj_placement_cut['type'] == 'loop':
                    t_LoopOn = 'true'
                    t_StartRelative = cvpj_placement_cut['start']/4
                    t_LoopStart = cvpj_placement_cut['loopstart']/4
                    t_LoopEnd = cvpj_placement_cut['loopend']/4


    if cliptype == 'notes': x_ClipData = addId(xmltag, 'MidiClip', str(get_clipid()))
    if cliptype == 'audio': x_ClipData = addId(xmltag, 'AudioClip', str(get_clipid()))
    x_ClipData.set('Time', str(able_position))

    addvalue(x_ClipData, 'LomId', '0')
    addvalue(x_ClipData, 'LomIdView', '0')

    addvalue(x_ClipData, 'CurrentStart', str(t_CurrentStart))
    addvalue(x_ClipData, 'CurrentEnd', str(t_CurrentEnd))
    x_ClipData_loop = ET.SubElement(x_ClipData, 'Loop')
    addvalue(x_ClipData_loop, 'LoopStart', str(t_LoopStart))
    addvalue(x_ClipData_loop, 'LoopEnd', str(t_LoopEnd))
    addvalue(x_ClipData_loop, 'StartRelative', str(t_StartRelative))
    addvalue(x_ClipData_loop, 'LoopOn', t_LoopOn)
    addvalue(x_ClipData_loop, 'OutMarker', t_LoopEnd)
    addvalue(x_ClipData_loop, 'HiddenLoopStart', t_LoopStart)
    addvalue(x_ClipData_loop, 'HiddenLoopEnd', t_LoopEnd)

    addvalue(x_ClipData, 'Name', t_name)
    addvalue(x_ClipData, 'Annotation', '')
    addvalue(x_ClipData, 'Color', str(t_color))
    addvalue(x_ClipData, 'LaunchMode', "0")
    addvalue(x_ClipData, 'LaunchQuantisation', "0")
    x_ClipData_TimeSignature = ET.SubElement(x_ClipData, 'TimeSignature')
    x_ClipData_TimeSignature_s = ET.SubElement(x_ClipData_TimeSignature, 'TimeSignatures')
    x_ClipData_TimeSignature_s_remote = addId(x_ClipData_TimeSignature_s, 'RemoteableTimeSignature', '0')
    addvalue(x_ClipData_TimeSignature_s_remote, 'Numerator', '4')
    addvalue(x_ClipData_TimeSignature_s_remote, 'Denominator', '4')
    addvalue(x_ClipData_TimeSignature_s_remote, 'Time', '0')

    x_ClipData_Envelopes = ET.SubElement(x_ClipData, 'Envelopes')
    ET.SubElement(x_ClipData_Envelopes, 'Envelopes')
    x_ClipData_ScrollerTimePreserver = ET.SubElement(x_ClipData, 'ScrollerTimePreserver')
    addvalue(x_ClipData_ScrollerTimePreserver, 'LeftTime', t_CurrentStart)
    addvalue(x_ClipData_ScrollerTimePreserver, 'RightTime', t_CurrentEnd)

    # ------------------------------------------ audio ------------------------------------------
    if cliptype == 'audio':
        x_ClipData_TimeSelection = ET.SubElement(x_ClipData, 'TimeSelection')
        addvalue(x_ClipData_TimeSelection, 'AnchorTime', '0')
        addvalue(x_ClipData_TimeSelection, 'OtherTime', '0')
    # -------------------------------------------------------------------------------------------

    addvalue(x_ClipData, 'Legato', 'false')
    addvalue(x_ClipData, 'Ram', 'false')
    x_ClipData_GrooveSettings = ET.SubElement(x_ClipData, 'GrooveSettings')
    addvalue(x_ClipData_GrooveSettings, 'GrooveId', '-1')
    addvalue(x_ClipData, 'Disabled', t_disabled)
    addvalue(x_ClipData, 'VelocityAmount', '0')
    create_FollowAction(x_ClipData, 4, 'true', 1, [4,0], [100,0], [1,1], 'false')
    create_grid(x_ClipData, 'Grid', 1, 16, 20, 2, 'true', 'true')
    addvalue(x_ClipData, 'FreezeStart', '0')
    addvalue(x_ClipData, 'FreezeEnd', '0')

    if cliptype == 'notes':
        addvalue(x_ClipData, 'IsWarped', 'true')
        addvalue(x_ClipData, 'TakeId', '1')
        x_ClipDataNotes = ET.SubElement(x_ClipData, 'Notes')
        create_notelist(x_ClipDataNotes, t_notelist)
        addvalue(x_ClipData, 'BankSelectCoarse', '-1')
        addvalue(x_ClipData, 'BankSelectFine', '-1')
        addvalue(x_ClipData, 'ProgramChange', '-1')
        addvalue(x_ClipData, 'NoteEditorFoldInZoom', '-1')
        addvalue(x_ClipData, 'NoteEditorFoldInScroll', '0')
        addvalue(x_ClipData, 'NoteEditorFoldOutZoom', '3072')
        addvalue(x_ClipData, 'NoteEditorFoldOutScroll', '-647')
        addvalue(x_ClipData, 'NoteEditorFoldScaleZoom', '-1')
        addvalue(x_ClipData, 'NoteEditorFoldScaleScroll', '0')
        create_scaleinformation(x_ClipData)
        addvalue(x_ClipData, 'IsInKey', 'false')
        addvalue(x_ClipData, 'NoteSpellingPreference', '3')
        addvalue(x_ClipData, 'PreferFlatRootNote', 'false')
        create_grid(x_ClipData, 'ExpressionGrid', 1, 16, 20, 2, 'false', 'false')

    if cliptype == 'audio':
        t_pitch = stretch_t_pitch
        w_PitchCoarse = round(t_pitch)
        w_PitchFine = (t_pitch-round(t_pitch))*100

        addvalue(x_ClipData, 'IsWarped', w_IsWarped)
        addvalue(x_ClipData, 'TakeId', '1')
        create_sampleref(x_ClipData, aud_sampledata)
        x_ClipData_Onsets = ET.SubElement(x_ClipData, 'Onsets')
        x_ClipData_UserOnsets = ET.SubElement(x_ClipData_Onsets, 'UserOnsets')
        addvalue(x_ClipData_Onsets, 'HasUserOnsets', 'false')
        addvalue(x_ClipData, 'WarpMode', w_WarpMode)
        addvalue(x_ClipData, 'GranularityTones', w_GranularityTones)
        addvalue(x_ClipData, 'GranularityTexture', w_GranularityTexture)
        addvalue(x_ClipData, 'FluctuationTexture', w_FluctuationTexture)
        addvalue(x_ClipData, 'TransientResolution', w_TransientResolution)
        addvalue(x_ClipData, 'TransientLoopMode', w_TransientLoopMode)
        addvalue(x_ClipData, 'TransientEnvelope', w_TransientEnvelope)
        addvalue(x_ClipData, 'ComplexProFormants', w_ComplexProFormants)
        addvalue(x_ClipData, 'ComplexProEnvelope', w_ComplexProEnvelope)

        addvalue(x_ClipData, 'Sync', 'true')
        addvalue(x_ClipData, 'HiQ', 'true')

        if 'fade' in cvpj_placement:
            FadeEnabled = 'true'
            cvpj_fade = cvpj_placement['fade']
            if 'in' in cvpj_fade:
                if 'duration' in cvpj_fade['in']: FadeInLength = cvpj_fade['in']['duration']/8
                if 'skew' in cvpj_fade['in']: FadeInCurveSkew = cvpj_fade['in']['skew']
                if 'slope' in cvpj_fade['in']: FadeInCurveSlope = cvpj_fade['in']['slope']
            if 'out' in cvpj_fade:
                if 'duration' in cvpj_fade['out']: FadeOutLength = cvpj_fade['out']['duration']/8
                if 'skew' in cvpj_fade['out']: FadeOutCurveSkew = cvpj_fade['out']['skew']
                if 'slope' in cvpj_fade['out']: FadeOutCurveSlope = cvpj_fade['out']['slope']

        addvalue(x_ClipData, 'Fade', FadeEnabled)
        x_ClipData_Fades = ET.SubElement(x_ClipData, 'Fades')
        addvalue(x_ClipData_Fades, 'FadeInLength', FadeInLength)
        addvalue(x_ClipData_Fades, 'FadeOutLength', FadeOutLength)
        addvalue(x_ClipData_Fades, 'ClipFadesAreInitialized', 'true')
        addvalue(x_ClipData_Fades, 'CrossfadeInState', '0')
        addvalue(x_ClipData_Fades, 'FadeInCurveSkew', FadeInCurveSkew)
        addvalue(x_ClipData_Fades, 'FadeInCurveSlope', FadeInCurveSlope)
        addvalue(x_ClipData_Fades, 'FadeOutCurveSkew', FadeOutCurveSkew)
        addvalue(x_ClipData_Fades, 'FadeOutCurveSlope', FadeOutCurveSlope)
        addvalue(x_ClipData_Fades, 'IsDefaultFadeIn', 'true') 
        addvalue(x_ClipData_Fades, 'IsDefaultFadeOut', 'true')

        addvalue(x_ClipData, 'PitchCoarse', w_PitchCoarse)
        addvalue(x_ClipData, 'PitchFine', w_PitchFine)
        addvalue(x_ClipData, 'SampleVolume', t_vol)
        addvalue(x_ClipData, 'MarkerDensity', '2')
        addvalue(x_ClipData, 'AutoWarpTolerance', '4')

        x_ClipData_WarpMarkers = ET.SubElement(x_ClipData, 'WarpMarkers')

        #w_timemarker_last = w_timemarkers[-1].copy()
        #w_timemarker_last['pos'] *= 1.001
        #w_timemarker_last['pos_real'] *= 1.001
        #w_timemarkers.append(w_timemarker_last)

        warpid = 0
        for w_timemarker in w_timemarkers:
            x_ClipData_WarpMarker = ET.SubElement(x_ClipData_WarpMarkers, 'WarpMarker')
            x_ClipData_WarpMarker.set('Id', str(warpid))
            x_ClipData_WarpMarker.set('SecTime', str(w_timemarker['pos_real']))
            x_ClipData_WarpMarker.set('BeatTime', str(w_timemarker['pos']/4))
            warpid += 1

        x_ClipData_SavedWarpMarkersForStretched = ET.SubElement(x_ClipData, 'SavedWarpMarkersForStretched')
        addvalue(x_ClipData, 'MarkersGenerated', 'true')
        addvalue(x_ClipData, 'IsSongTempoMaster', 'false')

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------- Track Base / MainSequencer ----------------

def set_add_clipslots(x_MainSequencer):
    x_ClipSlotList = ET.SubElement(x_MainSequencer, 'ClipSlotList')
    for clipslotnum in range(8):
        x_ClipSlot = addId(x_ClipSlotList, 'ClipSlot', str(clipslotnum))
        addvalue(x_ClipSlot, 'LomId', '0')
        x_ClipSlot_i = ET.SubElement(x_ClipSlot, 'ClipSlot')
        ET.SubElement(x_ClipSlot_i, 'Value')
        addvalue(x_ClipSlot, 'HasStop', 'true')
        addvalue(x_ClipSlot, 'NeedRefreeze', 'true')
    return x_ClipSlotList

def set_add_sequencer_base(x_BaseSequencer):
    addvalue(x_BaseSequencer, 'LomId', '0')
    addvalue(x_BaseSequencer, 'LomIdView', '0')
    addvalue(x_BaseSequencer, 'IsExpanded', 'true')
    set_add_param(x_BaseSequencer, 'On', 'true', str(get_unused_id()), None, [64,127], None)
    addvalue(x_BaseSequencer, 'ModulationSourceCount', '0')
    addLomId(x_BaseSequencer, 'ParametersListWrapper', '0')
    addId(x_BaseSequencer, 'Pointee', str(get_pointee()))
    addvalue(x_BaseSequencer, 'LastSelectedTimeableIndex', '0')
    addvalue(x_BaseSequencer, 'LastSelectedClipEnvelopeIndex', '0')
    x_LastPresetRef = ET.SubElement(x_BaseSequencer, 'LastPresetRef')
    ET.SubElement(x_LastPresetRef, 'Value')
    x_LockedScripts = ET.SubElement(x_BaseSequencer, 'LockedScripts')
    addvalue(x_BaseSequencer, 'IsFolded', 'false')
    addvalue(x_BaseSequencer, 'ShouldShowPresetName', 'false')
    addvalue(x_BaseSequencer, 'UserName', '')
    addvalue(x_BaseSequencer, 'Annotation', '')
    x_SourceContext = ET.SubElement(x_BaseSequencer, 'SourceContext')
    ET.SubElement(x_SourceContext, 'Value')
    #addvalue(x_ClipSlotList, 'MonitoringEnum', '1')

def set_add_midi_track_mainsequencer(xmltag, track_placements, trackcolor):
    x_MainSequencer = ET.SubElement(xmltag, 'MainSequencer')
    set_add_sequencer_base(x_MainSequencer)
    x_ClipSlotList = set_add_clipslots(x_MainSequencer)
    x_ClipTimeable = ET.SubElement(x_MainSequencer, 'ClipTimeable')
    x_ArrangerAutomation = ET.SubElement(x_ClipTimeable, 'ArrangerAutomation')
    x_ArrangerAutomation_Events = ET.SubElement(x_ArrangerAutomation, 'Events')
    for cvpj_placement in track_placements:
        create_clip(x_ArrangerAutomation_Events, 'notes', cvpj_placement, trackcolor)
    create_timeselection(xmltag, 0, 4)
    x_ArrangerAutomation_AutomationTransformViewState = ET.SubElement(x_ArrangerAutomation, 'AutomationTransformViewState')
    addvalue(x_ArrangerAutomation_AutomationTransformViewState, 'IsTransformPending', 'false')
    ET.SubElement(x_ArrangerAutomation_AutomationTransformViewState, 'TimeAndValueTransforms')
    x_Recorder = ET.SubElement(x_MainSequencer, 'Recorder')
    addvalue(x_Recorder, 'IsArmed', 'false')
    addvalue(x_Recorder, 'TakeCounter', '0')
    x_MidiControllers = ET.SubElement(x_MainSequencer, 'MidiControllers')
    for clipslotnum in range(131):
        x_ControllerTargets = addId(x_MidiControllers, 'ControllerTargets.'+str(clipslotnum), str(get_contid()))
        addvalue(x_ControllerTargets, 'LockEnvelope', '0')
    #addvalue(x_MainSequencer, 'MonitoringEnum', '1')

def set_add_midi_track_freezesequencer(xmltag, track_placements):
    x_FreezeSequencer = ET.SubElement(xmltag, 'FreezeSequencer')
    set_add_sequencer_base(x_FreezeSequencer)
    x_ClipSlotList = set_add_clipslots(x_FreezeSequencer)
    set_add_sequencer_end(xmltag, track_placements)

def set_add_sequencer_end(x_FreezeSequencer, track_placements):
    x_VolumeModulationTarget = addId(x_FreezeSequencer, 'VolumeModulationTarget', str(get_unused_id()))
    addvalue(x_VolumeModulationTarget, 'LockEnvelope', '0')
    x_TranspositionModulationTarget = addId(x_FreezeSequencer, 'TranspositionModulationTarget', str(get_unused_id()))
    addvalue(x_TranspositionModulationTarget, 'LockEnvelope', '0')
    x_GrainSizeModulationTarget = addId(x_FreezeSequencer, 'GrainSizeModulationTarget', str(get_unused_id()))
    addvalue(x_GrainSizeModulationTarget, 'LockEnvelope', '0')
    x_FluxModulationTarget = addId(x_FreezeSequencer, 'FluxModulationTarget', str(get_unused_id()))
    addvalue(x_FluxModulationTarget, 'LockEnvelope', '0')
    x_SampleOffsetModulationTarget = addId(x_FreezeSequencer, 'SampleOffsetModulationTarget', str(get_unused_id()))
    addvalue(x_SampleOffsetModulationTarget, 'LockEnvelope', '0')
    addvalue(x_FreezeSequencer, 'PitchViewScrollPosition', '-1073741824')
    addvalue(x_FreezeSequencer, 'SampleOffsetModulationScrollPosition', '-1073741824')
    x_Recorder = ET.SubElement(x_FreezeSequencer, 'Recorder')
    addvalue(x_Recorder, 'IsArmed', 'false')
    addvalue(x_Recorder, 'TakeCounter', '0')

def set_add_audio_track_mainsequencer(xmltag, track_placements, trackcolor):
    x_MainSequencer = ET.SubElement(xmltag, 'MainSequencer')
    set_add_sequencer_base(x_MainSequencer)
    x_ClipSlotList = set_add_clipslots(x_MainSequencer)
    addvalue(x_MainSequencer, 'MonitoringEnum', '1')
    x_Sample = ET.SubElement(x_MainSequencer, 'Sample')
    x_ArrangerAutomation = ET.SubElement(x_Sample, 'ArrangerAutomation')
    x_ArrangerAutomation_Events = ET.SubElement(x_ArrangerAutomation, 'Events')

    for track_placement in track_placements:
        create_clip(x_ArrangerAutomation_Events, 'audio', track_placement, trackcolor)

    x_ArrangerAutomation_AutomationTransformViewState = ET.SubElement(x_ArrangerAutomation, 'AutomationTransformViewState')
    addvalue(x_ArrangerAutomation_AutomationTransformViewState, 'IsTransformPending', 'false')
    ET.SubElement(x_ArrangerAutomation_AutomationTransformViewState, 'TimeAndValueTransforms')
    
    set_add_sequencer_end(x_MainSequencer, track_placements)

def set_add_audio_track_freezesequencer(xmltag, track_placements):
    x_FreezeSequencer = ET.SubElement(xmltag, 'FreezeSequencer')
    set_add_sequencer_base(x_FreezeSequencer)
    x_ClipSlotList = set_add_clipslots(x_FreezeSequencer)
    set_add_sequencer_end(x_FreezeSequencer, track_placements)


def set_add_master_track_freezesequencer(xmltag, track_placements):
    x_FreezeSequencer = ET.SubElement(xmltag, 'FreezeSequencer')
    x_AudioSequencer = addId(x_FreezeSequencer, 'AudioSequencer', '0')
    set_add_sequencer_base(x_AudioSequencer)
    ET.SubElement(xmltag, 'ClipSlotList')

# ---------------- Track Base / Device Chain ----------------

def create_devicechain(xmltag, tracktype, track_placements, trackcolor):
    global LaneHeight
    # ------- AutomationLanes
    x_AutomationLanes = ET.SubElement(xmltag, 'AutomationLanes')
    x_AutomationLanes_i = ET.SubElement(x_AutomationLanes, 'AutomationLanes')
    x_AutomationTarget = addId(x_AutomationLanes_i, 'AutomationLane', '0')
    addvalue(x_AutomationTarget, 'SelectedDevice', '0')
    addvalue(x_AutomationTarget, 'SelectedEnvelope', '0')
    addvalue(x_AutomationTarget, 'IsContentSelectedInDocument', 'false')
    addvalue(x_AutomationTarget, 'LaneHeight', str(LaneHeight))
    addvalue(x_AutomationLanes, 'AreAdditionalAutomationLanesFolded', 'false')

    x_ClipEnvelopeChooserViewState = ET.SubElement(xmltag, 'ClipEnvelopeChooserViewState')
    addvalue(x_ClipEnvelopeChooserViewState, 'SelectedDevice', '0')
    addvalue(x_ClipEnvelopeChooserViewState, 'SelectedEnvelope', '0')
    addvalue(x_ClipEnvelopeChooserViewState, 'PreferModulationVisible', 'false')

    add_up_lower(xmltag, 'AudioInputRouting', 'AudioIn/External/S0', 'Ext. In', '1/2')
    add_up_lower(xmltag, 'MidiInputRouting', 'MidiIn/External.All/-1', 'Ext: All Ins', '')
    if tracktype == 'miditrack': add_up_lower(xmltag, 'AudioOutputRouting', 'AudioOut/Master', 'Master', '')
    elif tracktype == 'master': add_up_lower(xmltag, 'AudioOutputRouting', 'AudioOut/External/S0', 'Ext. Out', '1/2')
    elif tracktype == 'prehear': add_up_lower(xmltag, 'AudioOutputRouting', 'AudioOut/External/S0', 'Ext. Out', '')
    add_up_lower(xmltag, 'MidiOutputRouting', 'MidiOut/None', 'None', '')
    create_devicechain_mixer(xmltag, tracktype)
    if tracktype == 'miditrack':
        set_add_midi_track_mainsequencer(xmltag, track_placements, trackcolor)
        set_add_midi_track_freezesequencer(xmltag, track_placements)
    if tracktype == 'audiotrack':
        set_add_audio_track_mainsequencer(xmltag, track_placements, trackcolor)
        set_add_audio_track_freezesequencer(xmltag, track_placements)
    if tracktype == 'master':
        set_add_master_track_freezesequencer(xmltag, track_placements)
    x_DeviceChain_i = ET.SubElement(xmltag, 'DeviceChain')
    x_DeviceChain_i_Devices = ET.SubElement(x_DeviceChain_i, 'Devices')
    x_DeviceChain_i_SignalModulations = ET.SubElement(x_DeviceChain_i, 'SignalModulations')

# ---------------- Track Base ----------------

def set_add_trackbase(xmltag, trackid, tracktype, trackname, colorval, TrackUnfolded, track_placements):
    global t_mrkr_timesig
    addvalue(xmltag, 'LomId', '0')
    addvalue(xmltag, 'LomIdView', '0')
    addvalue(xmltag, 'IsContentSelectedInDocument', 'false')
    addvalue(xmltag, 'PreferredContentViewMode', '0')
    x_TrackDelay = ET.SubElement(xmltag, 'TrackDelay')
    addvalue(x_TrackDelay, 'Value',  '0')
    addvalue(x_TrackDelay, 'IsValueSampleBased', 'false')
    x_name = ET.SubElement(xmltag, 'Name')
    if tracktype == 'master': addvalue(x_name, 'EffectiveName', "Master")
    else: addvalue(x_name, 'EffectiveName', trackname)
    addvalue(x_name, 'UserName', trackname)
    addvalue(x_name, 'Annotation', '')
    addvalue(x_name, 'MemorizedFirstClipName', '')
    addvalue(xmltag, 'Color', str(colorval))
    x_AutomationEnvelopes = ET.SubElement(xmltag, 'AutomationEnvelopes')
    #if tracktype == 'master':

    x_Envelopes = ET.SubElement(x_AutomationEnvelopes, 'Envelopes')
    addvalue(xmltag, 'TrackGroupId', '-1')
    addvalue(xmltag, 'TrackUnfolded', TrackUnfolded)
    addLomId(xmltag, 'DevicesListWrapper', '0')
    addLomId(xmltag, 'ClipSlotsListWrapper', '0')
    addvalue(xmltag, 'ViewData', '{}')
    x_TakeLanes = ET.SubElement(xmltag, 'TakeLanes')
    x_TakeLanes_i = ET.SubElement(x_TakeLanes, 'TakeLanes')
    addvalue(x_TakeLanes, 'AreTakeLanesFolded', 'true')
    addvalue(xmltag, 'LinkedTrackGroupId', '-1')
    if tracktype in ['miditrack', 'audiotrack']: 
        addvalue(xmltag, 'SavedPlayingSlot', '-1')
        addvalue(xmltag, 'SavedPlayingOffset', '0')
        addvalue(xmltag, 'Freeze', 'false')
        addvalue(xmltag, 'VelocityDetail', '0')
        addvalue(xmltag, 'NeedArrangerRefreeze', 'true')
        addvalue(xmltag, 'PostProcessFreezeClips', '0')

    x_DeviceChain = ET.SubElement(xmltag, 'DeviceChain')
    create_devicechain(x_DeviceChain, tracktype, track_placements, colorval)
    addvalue(xmltag, 'ReWireSlaveMidiTargetId', '0')
    addvalue(xmltag, 'PitchbendRange', '96')

# ---------------------------------------------------------------- DawVert Plugin Func -------------------------------------------------------------

tracknum = 1

def ableton_make_midi_track(cvpj_trackid):
    global tracknum
    cvpj_trackname = 'noname'
    ableton_trackcolor = -1
    cvpj_trackplacements = []

    if cvpj_trackid in cvpj_l['track_data']:
        cvpj_track_data = cvpj_l['track_data'][cvpj_trackid]
        if 'name' in cvpj_track_data: cvpj_trackname = cvpj_track_data['name']
        if 'color' in cvpj_track_data: 
            ableton_trackcolor = colors.closest_color_index(colorlist_one, cvpj_track_data['color'])

    if cvpj_trackid in cvpj_l['track_placements']:
        if 'notes' in cvpj_l['track_placements'][cvpj_trackid]:
            cvpj_trackplacements = notelist_data.sort(cvpj_l['track_placements'][cvpj_trackid]['notes'])

    x_MidiTrack = addId(x_Tracks, 'MidiTrack', str(tracknum))
    set_add_trackbase(x_MidiTrack, None, 'miditrack', cvpj_trackname, ableton_trackcolor, 'true', cvpj_trackplacements)
    tracknum += 1

def ableton_make_audio_track(cvpj_trackid):
    global tracknum
    cvpj_trackname = 'noname'
    ableton_trackcolor = -1
    cvpj_trackplacements = []

    if cvpj_trackid in cvpj_l['track_data']:
        cvpj_track_data = cvpj_l['track_data'][cvpj_trackid]
        if 'name' in cvpj_track_data: cvpj_trackname = cvpj_track_data['name']
        if 'color' in cvpj_track_data: 
            ableton_trackcolor = colors.closest_color_index(colorlist_one, cvpj_track_data['color'])

    if cvpj_trackid in cvpj_l['track_placements']:
        if 'audio' in cvpj_l['track_placements'][cvpj_trackid]:
            cvpj_trackplacements = notelist_data.sort(cvpj_l['track_placements'][cvpj_trackid]['audio'])

    x_AudioTrack = addId(x_Tracks, 'AudioTrack', str(tracknum))
    set_add_trackbase(x_AudioTrack, None, 'audiotrack', cvpj_trackname, ableton_trackcolor, 'true', cvpj_trackplacements)
    tracknum += 1


# ---------------------------------------------------------------- DawVert Plugin -------------------------------------------------------------

class output_cvpj(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Ableton Live 11'
    def getshortname(self): return 'ableton'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': True,
        'placement_loop': True,
        'no_placements': False,
        'no_pl_auto': True,
        'audio_events': False
        }
    def parse(self, convproj_json, output_file):
        global cvpj_l
        global x_Tracks
        global LaneHeight
        global t_mrkr_timesig
        global output_file_global
        global cvpj_bpm

        output_file_global = output_file

        cvpj_l = json.loads(convproj_json)
        LaneHeight = 68

        if 'bpm' in cvpj_l: cvpj_bpm = cvpj_l['bpm']
        else: cvpj_bpm = 120

        t_mrkr_timesig = {}
        t_mrkr_locater = {}

        if 'timemarkers' in cvpj_l: 
            cvpj_timemarkers = cvpj_l['timemarkers']
            for cvpj_timemarker in cvpj_timemarkers:
                istimemarker = False
                if 'type' in cvpj_timemarker:
                    if cvpj_timemarker['type'] == 'timesig':
                        istimemarker = True
                if istimemarker == True:
                    if cvpj_timemarker['denominator'] in [1,2,4,8,16]:
                        cvpj_denominator = cvpj_timemarker['denominator']
                        if cvpj_denominator == 1: out_denominator = 0
                        if cvpj_denominator == 2: out_denominator = 1
                        if cvpj_denominator == 4: out_denominator = 2
                        if cvpj_denominator == 8: out_denominator = 3
                        if cvpj_denominator == 16: out_denominator = 4
                        t_mrkr_timesig[cvpj_timemarker['position']/4] = (out_denominator*99)+(cvpj_timemarker['numerator']-1)
                    else:
                        t_mrkr_timesig[cvpj_timemarker['position']/4] = 201
                    if 'name' in cvpj_timemarker: t_mrkr_locater[cvpj_timemarker['position']/4] = cvpj_timemarker['name']
                else:
                    t_mrkr_locater[cvpj_timemarker['position']/4] = cvpj_timemarker['name']

        # XML Ableton
        x_root = ET.Element("Ableton")
        x_root.set('MajorVersion', "5")
        x_root.set('MinorVersion', "11.0_433")
        x_root.set('Creator', "Ableton Live 11.0")
        x_root.set('Revision', "9dc150af94686f816d2cf27815fcf2907d4b86f8")
        
        # XML LiveSet
        x_LiveSet = ET.SubElement(x_root, "LiveSet")
        addvalue(x_LiveSet, 'NextPointeeId', '36943')
        addvalue(x_LiveSet, 'OverwriteProtectionNumber', '2816')
        addvalue(x_LiveSet, 'LomId', '0')
        addvalue(x_LiveSet, 'LomIdView', '0')

        x_Tracks = ET.SubElement(x_LiveSet, "Tracks")
        if 'track_order' in cvpj_l:

            cvpj_numtracks = len(cvpj_l['track_order'])

            if cvpj_numtracks > 35: LaneHeight = 17

            for cvpj_trackid in cvpj_l['track_order']:
                if cvpj_trackid in cvpj_l['track_data']:
                    cvpj_s_track_data = cvpj_l['track_data'][cvpj_trackid]
                    if 'type' in cvpj_s_track_data:
                        if cvpj_s_track_data['type'] == 'instrument':
                            ableton_make_midi_track(cvpj_trackid)
                        if cvpj_s_track_data['type'] == 'audio':
                            ableton_make_audio_track(cvpj_trackid)
                    #print(cvpj_trackid)

        x_MasterTrack = ET.SubElement(x_LiveSet, "MasterTrack")
        set_add_trackbase(x_MasterTrack, None, 'master', 'Master', -1, 'false', None)

        x_PreHearTrack = ET.SubElement(x_LiveSet, "PreHearTrack")
        set_add_trackbase(x_PreHearTrack, None, 'prehear', 'Master', -1, 'false', None)

        x_SendsPre = ET.SubElement(x_LiveSet, "SendsPre")

        create_Scenes(x_LiveSet)
        create_transport(x_LiveSet, 8, 16, 'false')
        create_songmastervalues(x_LiveSet)
        ET.SubElement(x_LiveSet, "SignalModulations")
        addvalue(x_LiveSet, 'GlobalQuantisation', '4')
        addvalue(x_LiveSet, 'AutoQuantisation', '0')
        create_grid(x_LiveSet, 'Grid', 1, 16, 20, 2, 'true', 'false')
        create_scaleinformation(x_LiveSet)
        addvalue(x_LiveSet, 'InKey', 'false')
        addvalue(x_LiveSet, 'SmpteFormat', '0')
        create_timeselection(x_LiveSet, 0, 0)
        create_sequencernavigator(x_LiveSet)
        addvalue(x_LiveSet, 'ViewStateExtendedClipProperties', 'false')
        addvalue(x_LiveSet, 'IsContentSplitterOpen', 'true')
        addvalue(x_LiveSet, 'IsExpressionSplitterOpen', 'true')
        create_ExpressionLanes(x_LiveSet)
        create_ContentLanes(x_LiveSet)
        addvalue(x_LiveSet, 'ViewStateFxSlotCount', '4')
        addvalue(x_LiveSet, 'ViewStateSessionMixerHeight', '120')

        LocaterID = 0
        x_Locaters = create_Locators(x_LiveSet)
        for s_mrkr_locater in t_mrkr_locater:
            x_Locator = addId(x_Locaters, 'Locator', str(LocaterID))
            addvalue(x_Locator, 'LomId', 0)
            addvalue(x_Locator, 'Time', s_mrkr_locater)
            addvalue(x_Locator, 'Name', t_mrkr_locater[s_mrkr_locater])
            addvalue(x_Locator, 'Annotation', '')
            addvalue(x_Locator, 'IsSongStart', 'false')
            LocaterID += 1

        x_DetailClipKeyMidis = ET.SubElement(x_LiveSet, "DetailClipKeyMidis")
        addLomId(x_LiveSet, 'TracksListWrapper', '0')
        addLomId(x_LiveSet, 'VisibleTracksListWrapper', '0')
        addLomId(x_LiveSet, 'ReturnTracksListWrapper', '0')
        addLomId(x_LiveSet, 'ScenesListWrapper', '0')
        addLomId(x_LiveSet, 'CuePointsListWrapper', '0')
        addvalue(x_LiveSet, 'ChooserBar', '0')
        addvalue(x_LiveSet, 'Annotation', '')
        addvalue(x_LiveSet, 'SoloOrPflSavedValue', 'true')
        addvalue(x_LiveSet, 'SoloInPlace', 'true')
        addvalue(x_LiveSet, 'CrossfadeCurve', '2')
        addvalue(x_LiveSet, 'LatencyCompensation', '2')
        addvalue(x_LiveSet, 'HighlightedTrackIndex', '2')
        create_GroovePool(x_LiveSet)
        addvalue(x_LiveSet, 'AutomationMode', 'false')
        addvalue(x_LiveSet, 'SnapAutomationToGrid', 'true')
        addvalue(x_LiveSet, 'ArrangementOverdub', 'false')
        addvalue(x_LiveSet, 'ColorSequenceIndex', '1')
        create_AutoColorPickerForPlayerAndGroupTracks(x_LiveSet)
        create_AutoColorPickerForReturnAndMasterTracks(x_LiveSet)
        addvalue(x_LiveSet, 'ViewData', '{}')
        addvalue(x_LiveSet, 'MidiFoldIn', 'false')
        addvalue(x_LiveSet, 'MidiFoldMode', '0')
        addvalue(x_LiveSet, 'MultiClipFocusMode', 'false')
        addvalue(x_LiveSet, 'MultiClipLoopBarHeight', '0')
        addvalue(x_LiveSet, 'MidiPrelisten', 'false')
        x_LinkedTrackGroups = ET.SubElement(x_LiveSet, "LinkedTrackGroups")
        addvalue(x_LiveSet, 'AccidentalSpellingPreference', '3')
        addvalue(x_LiveSet, 'PreferFlatRootNote', 'false')
        addvalue(x_LiveSet, 'UseWarperLegacyHiQMode', 'false')
        set_add_VideoWindowRect(x_LiveSet)
        addvalue(x_LiveSet, 'ShowVideoWindow', 'true')
        addvalue(x_LiveSet, 'TrackHeaderWidth', '93')
        addvalue(x_LiveSet, 'ViewStateArrangerHasDetail', 'false')
        addvalue(x_LiveSet, 'ViewStateSessionHasDetail', 'true')
        addvalue(x_LiveSet, 'ViewStateDetailIsSample', 'false')
        create_viewstates(x_LiveSet)

        # Main

        xmlstr = minidom.parseString(ET.tostring(x_root)).toprettyxml(indent="\t")
        with open(output_file, "w") as f:
            f.write(xmlstr)