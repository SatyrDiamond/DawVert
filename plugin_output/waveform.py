# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
from functions import xtramath
from functions import colors
from objects import dv_dataset
import math

def get_plugins(convproj_obj, xml_tag, cvpj_fxids):
    for cvpj_fxid in cvpj_fxids:
        plugin_found, plugin_obj = convproj_obj.get_plugin(cvpj_fxid)
        if plugin_found: 
            fx_on, fx_wet = plugin_obj.fxdata_get()

            if plugin_obj.check_wildmatch('native-tracktion', None):
                wf_PLUGIN = ET.SubElement(xml_tag, "PLUGIN")
                wf_PLUGIN.set('type', plugin_obj.plugin_subtype)
                wf_PLUGIN.set('presetDirty', '1')
                wf_PLUGIN.set('enabled', str(fx_on))

                paramlist = dataset.params_list('plugin', plugin_obj.plugin_subtype)

                if paramlist:
                    for paramid in paramlist:
                        dset_paramdata = dataset.params_i_get('plugin', plugin_obj.plugin_subtype, paramid)
                        paramdata = track_obj.params.get(paramid, dset_paramdata[2]).value
                        wf_PLUGIN.set(paramid, str(paramdata))



class output_waveform_edit(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Waveform Edit'
    def getshortname(self): return 'waveform_edit'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'Waveform'
        dawinfo_obj.file_ext = 'tracktionedit'
        dawinfo_obj.placement_cut = True
        dawinfo_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
        dawinfo_obj.time_seconds = True
        dawinfo_obj.audio_stretch = ['rate']
        dawinfo_obj.plugin_included = ['native-tracktion']
    def parse(self, convproj_obj, output_file):
        global dataset

        convproj_obj.change_timings(4, True)

        wf_proj = ET.Element("EDIT")
        wf_proj.set('appVersion', "Waveform 11.5.18")
        wf_proj.set('modifiedBy', "DawVert")

        dataset = dv_dataset.dataset('./data_dset/waveform.dset')

        wf_numerator = 4
        wf_denominator = 4
        wf_bpmdata = convproj_obj.params.get('bpm', 140).value
        wf_numerator, wf_denominator = convproj_obj.timesig

        tempomul = 120/wf_bpmdata

        wf_globalid = 1000

        wf_TEMPOSEQUENCE = ET.SubElement(wf_proj, "TEMPOSEQUENCE")
        wf_TEMPO = ET.SubElement(wf_TEMPOSEQUENCE, "TEMPO")
        wf_TEMPO.set('startBeat', str(0.0))
        wf_TEMPO.set('bpm', str(wf_bpmdata))
        wf_TEMPO.set('curve', str(1.0))
        wf_TIMESIG = ET.SubElement(wf_TEMPOSEQUENCE, "TIMESIG")
        wf_TIMESIG.set('numerator', str(wf_numerator))
        wf_TIMESIG.set('denominator', str(wf_denominator))
        wf_TIMESIG.set('startBeat', str(0.0))

        wf_MASTERPLUGINS = ET.SubElement(wf_proj, "MASTERPLUGINS")
        get_plugins(convproj_obj, wf_MASTERPLUGINS, convproj_obj.track_master.fxslots_audio)
        wf_MASTERTRACK = ET.SubElement(wf_proj, "MASTERTRACK")
        wf_MASTERTRACK.set('id', str(wf_globalid))
        if convproj_obj.track_master.visual.name: wf_MASTERTRACK.set('name', convproj_obj.track_master.visual.name)
        wf_globalid =+ 1

        for trackid, track_obj in convproj_obj.iter_track():
            wf_TRACK = ET.SubElement(wf_proj, "TRACK")
            wf_TRACK.set('id', str(wf_globalid))
            if track_obj.visual.name: wf_TRACK.set('name', track_obj.visual.name)
            if track_obj.visual.color: wf_TRACK.set('colour', 'ff'+colors.rgb_float_to_hex(track_obj.visual.color))
            
            wf_INST = ET.SubElement(wf_TRACK, "PLUGIN")
            wf_INST.set('type', '4osc')
            wf_INST.set('enabled', '1')

            get_plugins(convproj_obj, wf_TRACK, track_obj.fxslots_audio)

            for notespl_obj in track_obj.placements.pl_notes:

                wf_MIDICLIP = ET.SubElement(wf_TRACK, "MIDICLIP")

                offset = notespl_obj.cut_data['start'] if 'start' in notespl_obj.cut_data else 0
                loopstart = notespl_obj.cut_data['loopstart'] if 'loopstart' in notespl_obj.cut_data else 0
                loopend = notespl_obj.cut_data['loopend'] if 'loopend' in notespl_obj.cut_data else notespl_obj.duration

                wf_MIDICLIP.set('start', str(notespl_obj.position_real))
                wf_MIDICLIP.set('length', str(notespl_obj.duration_real))

                if notespl_obj.cut_type == 'cut':
                    wf_MIDICLIP.set('offset', str((offset/8)*tempomul))
                elif notespl_obj.cut_type in ['loop', 'loop_off', 'loop_adv']:
                    wf_MIDICLIP.set('offset', str((offset/8)*tempomul))
                    wf_MIDICLIP.set('loopStartBeats', str((loopstart/4)))
                    wf_MIDICLIP.set('loopLengthBeats', str((loopend/4)))

                if notespl_obj.visual.name: wf_MIDICLIP.set('name', notespl_obj.visual.name)
                if notespl_obj.visual.color: wf_MIDICLIP.set('colour', 'ff'+colors.rgb_float_to_hex(notespl_obj.visual.color))
                wf_MIDICLIP.set('mute', str(int(notespl_obj.muted)))

                wf_SEQUENCE = ET.SubElement(wf_MIDICLIP, "SEQUENCE")
                wf_SEQUENCE.set('ver', '1')
                wf_SEQUENCE.set('channelNumber', '1')

                notespl_obj.notelist.sort()
                for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
                    for t_key in t_keys:
                        wf_NOTE = ET.SubElement(wf_SEQUENCE, "NOTE")
                        wf_NOTE.set('p', str(t_key+60))
                        wf_NOTE.set('b', str(t_pos/4))
                        wf_NOTE.set('l', str(t_dur/4))
                        wf_NOTE.set('v', str(int(xtramath.clamp(t_vol*127, 0, 127))))

            cvpj_track_vol = track_obj.params.get('vol', 1.0).value
            cvpj_track_pan = track_obj.params.get('pan', 0).value
            wf_PLUGINVOLPAN = ET.SubElement(wf_TRACK, "PLUGIN")
            wf_PLUGINVOLPAN.set('type', 'volume')
            wf_PLUGINVOLPAN.set('enabled', '1')
            wf_PLUGINVOLPAN.set('volume', str(cvpj_track_vol))
            wf_PLUGINVOLPAN.set('pan', str(cvpj_track_pan))

            wf_PLUGINMETER = ET.SubElement(wf_TRACK, "PLUGIN")
            wf_PLUGINMETER.set('type', 'level')
            wf_PLUGINMETER.set('enabled', '1')

            wf_globalid += 1

        outfile = ET.ElementTree(wf_proj)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
