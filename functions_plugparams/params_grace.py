# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET

def addvalue(xmltag, name, value):
    temp_xml = ET.SubElement(xmltag, name)
    if value != None: temp_xml.text = value

def create_main():
    gx_root = ET.Element("root")

    gx_GlobalParameters = ET.SubElement(gx_root, "GlobalParameters")
    addvalue(gx_GlobalParameters, 'VoiceMode', 'Poly')
    addvalue(gx_GlobalParameters, 'VoiceGlide', '0')

    gx_SampleGroup = ET.SubElement(gx_root, "SampleGroup")
    addvalue(gx_SampleGroup, 'Name', 'Group 1')
    gx_VoiceParameters = ET.SubElement(gx_SampleGroup, "VoiceParameters")
    addvalue(gx_VoiceParameters, 'AmpAttack', '0')
    addvalue(gx_VoiceParameters, 'AmpDecay', '0')
    addvalue(gx_VoiceParameters, 'AmpEnvSnap', 'SnapOff')
    addvalue(gx_VoiceParameters, 'AmpHold', '0')
    addvalue(gx_VoiceParameters, 'AmpRelease', '0')
    addvalue(gx_VoiceParameters, 'AmpSustain', '1')
    addvalue(gx_VoiceParameters, 'AmpVelocityDepth', 'Vel80')
    addvalue(gx_VoiceParameters, 'Filter1KeyFollow', '0.5')
    addvalue(gx_VoiceParameters, 'Filter1Par1', '0.5')
    addvalue(gx_VoiceParameters, 'Filter1Par2', '0.5')
    addvalue(gx_VoiceParameters, 'Filter1Par3', '0.5')
    addvalue(gx_VoiceParameters, 'Filter1Par4', '1')
    addvalue(gx_VoiceParameters, 'Filter1Type', 'ftNone')
    addvalue(gx_VoiceParameters, 'Filter2KeyFollow', '0.5')
    addvalue(gx_VoiceParameters, 'Filter2Par1', '0.5')
    addvalue(gx_VoiceParameters, 'Filter2Par2', '0.5')
    addvalue(gx_VoiceParameters, 'Filter2Par3', '0.5')
    addvalue(gx_VoiceParameters, 'Filter2Par4', '1')
    addvalue(gx_VoiceParameters, 'Filter2Type', 'ftNone')
    addvalue(gx_VoiceParameters, 'FilterOutputBlend', '1')
    addvalue(gx_VoiceParameters, 'FilterRouting', 'Serial')
    addvalue(gx_VoiceParameters, 'Lfo1Par1', '0.5')
    addvalue(gx_VoiceParameters, 'Lfo1Par2', '0.5')
    addvalue(gx_VoiceParameters, 'Lfo1Par3', '0.5')
    addvalue(gx_VoiceParameters, 'Lfo2Par1', '0.5')
    addvalue(gx_VoiceParameters, 'Lfo2Par2', '0.5')
    addvalue(gx_VoiceParameters, 'Lfo2Par3', '0.5')
    addvalue(gx_VoiceParameters, 'LfoFreqMode1', 'Fixed100Millisecond')
    addvalue(gx_VoiceParameters, 'LfoFreqMode2', 'Fixed100Millisecond')
    addvalue(gx_VoiceParameters, 'LfoShape1', 'Triangle')
    addvalue(gx_VoiceParameters, 'LfoShape2', 'Triangle')
    addvalue(gx_VoiceParameters, 'LoopEnd', '1')
    addvalue(gx_VoiceParameters, 'LoopStart', '0')
    addvalue(gx_VoiceParameters, 'ModAttack', '0')
    addvalue(gx_VoiceParameters, 'ModDecay', '0.300000011920929')
    addvalue(gx_VoiceParameters, 'ModEnvSnap', 'SnapOff')
    addvalue(gx_VoiceParameters, 'ModHold', '0')
    addvalue(gx_VoiceParameters, 'ModRelease', '0.300000011920929')
    addvalue(gx_VoiceParameters, 'ModSustain', '0.300000011920929')
    addvalue(gx_VoiceParameters, 'ModVelocityDepth', 'Vel80')
    addvalue(gx_VoiceParameters, 'OutputGain', '0.5')
    addvalue(gx_VoiceParameters, 'OutputPan', '0.504999995231628')
    addvalue(gx_VoiceParameters, 'PitchTracking', 'Note')
    addvalue(gx_VoiceParameters, 'SampleEnd', '1')
    addvalue(gx_VoiceParameters, 'SampleReset', 'None')
    addvalue(gx_VoiceParameters, 'SamplerLoopBounds', 'LoopPoints')
    addvalue(gx_VoiceParameters, 'SamplerTriggerMode', 'LoopOff')
    addvalue(gx_VoiceParameters, 'SampleStart', '0')
    addvalue(gx_VoiceParameters, 'Seq1Clock', 'Div_4')
    addvalue(gx_VoiceParameters, 'Seq1Direction', 'Forwards')
    addvalue(gx_VoiceParameters, 'Seq2Clock', 'Div_4')
    addvalue(gx_VoiceParameters, 'Seq2Direction', 'Forwards')
    addvalue(gx_VoiceParameters, 'StepSeq1Length', 'Eight')
    addvalue(gx_VoiceParameters, 'StepSeq2Length', 'Eight')
    addvalue(gx_VoiceParameters, 'VoicePitchOne', '0.5')
    addvalue(gx_VoiceParameters, 'VoicePitchTwo', '0.5')

    addvalue(gx_root, 'PatchFileFormatVersion', '4')
    addvalue(gx_root, 'PatchFileType', 'LucidityPatchFile')

    gx_PresetInfo = ET.SubElement(gx_root, "PresetInfo")
    addvalue(gx_PresetInfo, 'PresetName', 'Defualt')
    addvalue(gx_PresetInfo, 'PresetFileName', None)

    gx_MidiMap = ET.SubElement(gx_root, "MidiMap")
    return gx_root

def create_region(gx_root, regionparams):
    gx_SampleGroup = gx_root.findall('SampleGroup')[0]
    gx_Region = ET.SubElement(gx_SampleGroup, "Region")
    gx_RegionProp = ET.SubElement(gx_Region, "RegionProperties")
    gx_SampleProp = ET.SubElement(gx_Region, "SampleProperties")

    FileName = ''

    if 'file' in regionparams: FileName = regionparams['file']
    addvalue(gx_SampleProp, 'SampleFileName', str(FileName))

    LowNote = 0
    HighNote = 127
    LowVelocity = 0
    HighVelocity = 127
    RootNote = 60
    SampleStart = 0
    SampleEnd = 0
    LoopStart = -1
    LoopEnd = -1
    
    if 'r_key' in regionparams:
        LowNote = regionparams['r_key'][0] + 60
        HighNote = regionparams['r_key'][1] + 60

    if 'r_vol' in regionparams:
        LowVelocity = int(regionparams['vol'][0]*127)
        HighVelocity = int(regionparams['vol'][1]*127)

    if 'loop' in regionparams:
        if regionparams['loop']['enabled'] == 1:
            LoopStart = regionparams['loop']['points'][0]
            LoopEnd = regionparams['loop']['points'][1]

    if 'middlenote' in regionparams: RootNote = regionparams['middlenote'] + 60
    if 'start' in regionparams: SampleStart = regionparams['start']
    if 'end' in regionparams: SampleEnd = regionparams['end'] - 1

    addvalue(gx_RegionProp, 'LowNote', str(LowNote))
    addvalue(gx_RegionProp, 'HighNote', str(HighNote))
    addvalue(gx_RegionProp, 'LowVelocity', str(LowVelocity))
    addvalue(gx_RegionProp, 'HighVelocity', str(HighVelocity))
    addvalue(gx_RegionProp, 'RootNote', str(RootNote))
    addvalue(gx_RegionProp, 'SampleStart', str(SampleStart))
    addvalue(gx_RegionProp, 'SampleEnd', str(SampleEnd))
    addvalue(gx_SampleProp, 'SampleFrames', str(SampleEnd))
    addvalue(gx_RegionProp, 'LoopStart', str(LoopStart))
    addvalue(gx_RegionProp, 'LoopEnd', str(LoopEnd))

    SampleVolume = 0
    SamplePan = 0
    SampleTune = 0
    SampleFine = 0

    addvalue(gx_RegionProp, 'SampleVolume', str(SampleVolume))
    addvalue(gx_RegionProp, 'SamplePan', str(SamplePan))
    addvalue(gx_RegionProp, 'SampleTune', str(SampleTune))
    addvalue(gx_RegionProp, 'SampleFine', str(SampleFine))

    SampleBeats = 4

    addvalue(gx_RegionProp, 'SampleBeats', str(SampleBeats))

    return gx_root
