# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# ---------------------------------------------- Instruments ----------------------------------------------

def get_params_inst(pluginname): return autoval_inst[pluginname] 

autoval_inst = {}

autoval_inst['bitinvader'] = [ ['interpolation','normalize','sampleLength'], ['sampleShape','version'] ]

autoval_inst['papu'] = [ ['Bass','ch1so1','ch1so2','ch1ssl','ch1vol','ch1vsd','ch1wpd','ch2so1','ch2so2','ch2ssl','ch2vol','ch2vsd','ch2wpd','ch3so1','ch3so2','ch3vol','ch4so1','ch4so2','ch4ssl','ch4vol','ch4vsd','sd','so1vol','so2vol','srs','srw','st','Treble'],['sampleShape'] ]

autoval_inst['gigplayer'] = [ ['patch','bank','gain'] , ['src'] ]

autoval_inst['kicker'] = [ ['click','decay','dist','distend','endfreq','endnote','env','gain','noise','slope','startfreq','startnote','version'], [] ]

autoval_inst['lb302'] = [ ['db24','dead','dist','slide','slide_dec','vcf_cut','vcf_dec','vcf_mod','vcf_res','shape'], [] ]

autoval_inst['malletsstk'] = [ ['adsr','crossfade','hardness','lfo_depth','lfo_speed','modulator','oldversion','position','pressure','spread','stick_mix','strike','velocity','version','vib_freq','vib_gain'], ['preset'] ]

autoval_inst['monstro'] = [ ['e1att','e1att_denominator','e1att_numerator','e1att_syncmode','e1dec','e1dec_denominator','e1dec_numerator','e1dec_syncmode','e1hol','e1hol_denominator','e1hol_numerator','e1hol_syncmode','e1pre','e1pre_denominator','e1pre_numerator','e1pre_syncmode','e1rel','e1rel_denominator','e1rel_numerator','e1rel_syncmode','e1slo','e1sus','e2att','e2att_denominator','e2att_numerator','e2att_syncmode','e2dec','e2dec_denominator','e2dec_numerator','e2dec_syncmode','e2hol','e2hol_denominator','e2hol_numerator','e2hol_syncmode','e2pre','e2pre_denominator','e2pre_numerator','e2pre_syncmode','e2rel','e2rel_denominator','e2rel_numerator','e2rel_syncmode','e2slo','e2sus','f1e1','f1e2','f1l1','f1l2','f2e1','f2e2','f2l1','f2l2','f3e1','f3e2','f3l1','f3l2','l1att','l1att_denominator','l1att_numerator','l1att_syncmode','l1phs','l1rat','l1rat_denominator','l1rat_numerator','l1rat_syncmode','l1wav','l2att','l2att_denominator','l2att_numerator','l2att_syncmode','l2phs','l2rat','l2rat_denominator','l2rat_numerator','l2rat_syncmode','l2wav','o1crs','o1ftl','o1ftr','o1pan','o1pw','o1spo','o1ssf','o1ssr','o1vol','o23mo','o2crs','o2ftl','o2ftr','o2pan','o2spo','o2syn','o2synr','o2vol','o2wav','o3crs','o3pan','o3spo','o3sub','o3syn','o3synr','o3vol','o3wav1','o3wav2','p1e1','p1e2','p1l1','p1l2','p2e1','p2e2','p2l1','p2l2','p3e1','p3e2','p3l1','p3l2','s3e1','s3e2','s3l1','s3l2','v1e1','v1e2','v1l1','v1l2','v2e1','v2e2','v2l1','v2l2','v3e1','v3e2','v3l1','v3l2','w1e1','w1e2','w1l1','w1l2'], [] ]

autoval_inst['nes'] = [ ['crs1','crs2','crs3','dc1','dc2','envlen1','envlen2','envlen4','envloop1','envloop2','envloop4','envon1','envon2','envon4','nfreq4','nfrqmode4','nmode4','nq4','nswp4','on1','on2','on3','on4','swamt1','swamt2','sweep1','sweep2','swrate1','swrate2','vibr','vol','vol1','vol2','vol3','vol4'], [] ]

autoval_inst['organic'] = [ ['foldback','newdetune0','newdetune1','newdetune2','newdetune3','newdetune4','newdetune5','newdetune6','newdetune7','newharmonic0','newharmonic1','newharmonic2','newharmonic3','newharmonic4','newharmonic5','newharmonic6','newharmonic7','num_osc','pan0','pan1','pan2','pan3','pan4','pan5','pan6','pan7','vol','vol0','vol1','vol2','vol3','vol4','vol5','vol6','vol7','wavetype0','wavetype1','wavetype2','wavetype3','wavetype4','wavetype5','wavetype6','wavetype7'], [] ]

autoval_inst['sfxr'] = [ ['att','changeAmt','changeSpeed','dec','dSlide','hold','hpFilCut','hpFilCutSweep','lpFilCut','lpFilCutSweep','lpFilReso','minFreq','phaserOffset','phaserSweep','repeatSpeed','slide','sqrDuty','sqrSweep','startFreq','sus','version','vibDepth','vibSpeed','waveForm'], [] ]

autoval_inst['sid'] = [ ['attack0','attack1','attack2','chipModel','coarse0','coarse1','coarse2','decay0','decay1','decay2','filtered0','filtered1','filtered2','filterFC','filterMode','filterResonance','pulsewidth0','pulsewidth1','pulsewidth2','release0','release1','release2','ringmod0','ringmod1','ringmod2','sustain0','sustain1','sustain2','sync0','sync1','sync2','test0','test1','test2','voice3Off','volume','waveform0','waveform1','waveform2'], [] ]

autoval_inst['tripleoscillator'] = [ ['coarse0','coarse1','coarse2','finel0','finel1','finel2','finer0','finer1','finer2','modalgo1','modalgo2','modalgo3','pan0','pan1','pan2','phoffset0','phoffset1','phoffset2','stphdetun0','stphdetun1','stphdetun2','vol0','vol1','vol2','wavetype0','wavetype1','wavetype2'] , ['userwavefile0','userwavefile1','userwavefile2'] ]

autoval_inst['vibedstrings'] = [ ['active0','active1','active2','active3','active4','active5','active6','active7','active8','detune0','detune1','detune2','detune3','detune4','detune5','detune6','detune7','detune8','impulse0','impulse1','impulse2','impulse3','impulse4','impulse5','impulse6','impulse7','impulse8','length0','length1','length2','length3','length4','length5','length6','length7','length8','octave0','octave1','octave2','octave3','octave4','octave5','octave6','octave7','octave8','pan0','pan1','pan2','pan3','pan4','pan5','pan6','pan7','pan8','pick0','pick1','pick2','pick3','pick4','pick5','pick6','pick7','pick8','pickup0','pickup1','pickup2','pickup3','pickup4','pickup5','pickup6','pickup7','pickup8','slap0','slap1','slap2','slap3','slap4','slap5','slap6','slap7','slap8','stiffness0','stiffness1','stiffness2','stiffness3','stiffness4','stiffness5','stiffness6','stiffness7','stiffness8','volume0','volume1','volume2','volume3','volume4','volume5','volume6','volume7','volume8'], ['graph0','graph1','graph2','graph3','graph4','graph5','graph6','graph7','graph8','version'] ]

autoval_inst['watsyn'] = [ ['a1_ltune','a1_mult','a1_pan','a1_rtune','a1_vol','a2_ltune','a2_mult','a2_pan','a2_rtune','a2_vol','abmix','amod','b1_ltune','b1_mult','b1_pan','b1_rtune','b1_vol','b2_ltune','b2_mult','b2_pan','b2_rtune','b2_vol','bmod','envAmt','envAtt','envAtt_denominator','envAtt_numerator','envAtt_syncmode','envDec','envDec_denominator','envDec_numerator','envDec_syncmode','envHold','envHold_denominator','envHold_numerator','envHold_syncmode','xtalk'], ['a1_wave','a2_wave','b1_wave','b2_wave'] ]

# ---------------------------------------------- FX ----------------------------------------------

def get_params_fx(pluginname): return autoval_fx[pluginname] 

autoval_fx = {}

autoval_fx['amplifier'] = [ ['pan','right','volume','left'], [] ]

autoval_fx['bassbooster'] = [ ['freq','gain','ratio'], [] ]

autoval_fx['bitcrush'] = [ ['depthon', 'outclip', 'innoise','stereodiff','outgain','ingain','levels','rateon'], ['rate'] ]

autoval_fx['crossovereq'] = [ ['gain1','gain2','gain3','gain4','mute1','mute2','mute3','mute4','xover12','xover23','xover34'], [] ]

autoval_fx['delay'] = [ ['DelayTimeSamples_numerator','LfoAmount','LfoFrequency_syncmode','DelayTimeSamples_denominator','LfoFrequency_denominator','LfoAmount_denominator','LfoFrequency_numerator','LfoAmount_numerator','LfoFrequency','DelayTimeSamples','OutGain','DelayTimeSamples_syncmode','FeebackAmount','LfoAmount_syncmode'], [] ]

autoval_fx['dualfilter'] = [ ['res2','enabled','filter','cut2','mix','res1','enabled1','filter1','cut1','gain1','gain2'], [] ]

autoval_fx['dynamicsprocessor'] = [ ['release', 'stereoMode', 'outputGain', 'attack', 'inputGain'], ['waveShape'] ]

autoval_fx['eq'] = [ ['AnalyseIn','AnalyseOut','Highshelfactive','HighShelfgain','HighShelfres','HP','HP12','HP24','HP48','HPactive','HPres','Lowshelfactive','Lowshelfgain','LowShelfres','LP','LP12','LP24','LP48','LPactive','LPres','Outputgain','Peak1active','Peak1bw','Peak2active','Peak2bw','Peak2gain','Peak3active','Peak3bw','Peak3gain','Peak4active','Peak4bw','Peak4gain','Inputgain','Peak1gain','HPfreq','LowShelffreq','Peak1freq','Peak2freq','Peak3freq','Peak4freq','Highshelffreq','LPfreq'], [] ]

autoval_fx['flanger'] = [ ['LfoAmount','LfoFrequency_syncmode','LfoFrequency_denominator','WhiteNoise','LfoFrequency_numerator','Feedback','Invert','LfoFrequency','DelayTimeSamples'], [] ]

autoval_fx['multitapecho'] = [ ['steplength','steplength_denominator','steps','drygain','steplength_numerator','steplength_syncmode','swapinputs','stages'], ['ampsteps','lpsteps'] ]

autoval_fx['peakcontrollereffect'] = [ ['amountmult','mute','decay','effectId','base','attack','amount','treshold','abs'], [] ]

autoval_fx['reverbsc'] = [ ['input_gain', 'size', 'output_gain', 'color'], [] ]

autoval_fx['spectrumanalyzer'] = [ [], [] ]

autoval_fx['stereomatrix'] = [ ['l-r', 'r-l', 'r-r', 'l-l'], [] ]

autoval_fx['stereoenhancer'] = [ ['width'], [] ]

autoval_fx['waveshaper'] = [ ['outputGain', 'clipInput', 'inputGain'], ['waveShape'] ]

















