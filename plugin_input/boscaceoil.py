from functions import data_bytes
from functions import placements
import plugin_input
import json

ceol_instlist = {}
ceol_instlist[0] = ["MIDI", "Grand Piano", "midi.piano1"]
ceol_instlist[1] = ["MIDI", "Brite Piano", "midi.piano2"]
ceol_instlist[2] = ["MIDI", "E. Grand Piano", "midi.piano3"]
ceol_instlist[3] = ["MIDI", "HonkyTonk", "midi.piano4"]
ceol_instlist[4] = ["MIDI", "E.Piano1", "midi.piano5"]
ceol_instlist[5] = ["MIDI", "E.Piano2", "midi.piano6"]
ceol_instlist[6] = ["MIDI", "Harpsichord", "midi.piano7"]
ceol_instlist[7] = ["MIDI", "Clavi", "midi.piano8"]
ceol_instlist[8] = ["MIDI", "Celesta", "midi.chrom1"]
ceol_instlist[9] = ["MIDI", "Glocken", "midi.chrom2"]
ceol_instlist[10] = ["MIDI", "MusicBox", "midi.chrom3"]
ceol_instlist[11] = ["MIDI", "Vibes", "midi.chrom4"]
ceol_instlist[12] = ["MIDI", "Marimba", "midi.chrom5"]
ceol_instlist[13] = ["MIDI", "Xylophone", "midi.chrom6"]
ceol_instlist[14] = ["MIDI", "Tubular Bells", "midi.chrom7"]
ceol_instlist[15] = ["MIDI", "Dulcimer", "midi.chrom8"]
ceol_instlist[16] = ["MIDI", "DrawOrgn", "midi.organ1"]
ceol_instlist[17] = ["MIDI", "PercOrgn", "midi.organ2"]
ceol_instlist[18] = ["MIDI", "RockOrgn", "midi.organ3"]
ceol_instlist[19] = ["MIDI", "ChrchOrg", "midi.organ4"]
ceol_instlist[20] = ["MIDI", "ReedOrgn", "midi.organ5"]
ceol_instlist[21] = ["MIDI", "Acordion", "midi.organ6"]
ceol_instlist[22] = ["MIDI", "Harmnica", "midi.organ7"]
ceol_instlist[23] = ["MIDI", "TangoAcd", "midi.organ8"]
ceol_instlist[24] = ["MIDI", "NylonGtr", "midi.guitar1"]
ceol_instlist[25] = ["MIDI", "SteelGtr", "midi.guitar2"]
ceol_instlist[26] = ["MIDI", "Jazz Gtr", "midi.guitar3"]
ceol_instlist[27] = ["MIDI", "CleanGtr", "midi.guitar4"]
ceol_instlist[28] = ["MIDI", "Mute.Gtr", "midi.guitar5"]
ceol_instlist[29] = ["MIDI", "Ovrdrive", "midi.guitar6"]
ceol_instlist[30] = ["MIDI", "Dist.Gtr", "midi.guitar7"]
ceol_instlist[31] = ["MIDI", "GtrHarmo", "midi.guitar8"]
ceol_instlist[32] = ["MIDI", "Aco.Bass", "midi.bass1"]
ceol_instlist[33] = ["MIDI", "FngrBass", "midi.bass2"]
ceol_instlist[34] = ["MIDI", "PickBass", "midi.bass3"]
ceol_instlist[35] = ["MIDI", "Fretless", "midi.bass4"]
ceol_instlist[36] = ["MIDI", "SlapBas1", "midi.bass5"]
ceol_instlist[37] = ["MIDI", "SlapBas2", "midi.bass6"]
ceol_instlist[38] = ["MIDI", "SynBass1", "midi.bass7"]
ceol_instlist[39] = ["MIDI", "SynBass2", "midi.bass8"]
ceol_instlist[40] = ["MIDI", "Violin", "midi.strings1"]
ceol_instlist[41] = ["MIDI", "Viola", "midi.strings2"]
ceol_instlist[42] = ["MIDI", "Cello", "midi.strings3"]
ceol_instlist[43] = ["MIDI", "ContraBs", "midi.strings4"]
ceol_instlist[44] = ["MIDI", "Trem.Str", "midi.strings5"]
ceol_instlist[45] = ["MIDI", "Pizz.Str", "midi.strings6"]
ceol_instlist[46] = ["MIDI", "Harp", "midi.strings7"]
ceol_instlist[47] = ["MIDI", "Timpani", "midi.strings8"]
ceol_instlist[48] = ["MIDI", "Strings1", "midi.ensemble1"]
ceol_instlist[49] = ["MIDI", "Strings2", "midi.ensemble2"]
ceol_instlist[50] = ["MIDI", "Syn.Str1", "midi.ensemble3"]
ceol_instlist[51] = ["MIDI", "Syn.Str2", "midi.ensemble4"]
ceol_instlist[52] = ["MIDI", "ChoirAah", "midi.ensemble5"]
ceol_instlist[53] = ["MIDI", "VoiceOoh", "midi.ensemble6"]
ceol_instlist[54] = ["MIDI", "SynVoice", "midi.ensemble7"]
ceol_instlist[55] = ["MIDI", "Orch.Hit", "midi.ensemble8"]
ceol_instlist[56] = ["MIDI", "Trumpet", "midi.brass1"]
ceol_instlist[57] = ["MIDI", "Trombone", "midi.brass2"]
ceol_instlist[58] = ["MIDI", "Tuba", "midi.brass3"]
ceol_instlist[59] = ["MIDI", "Mute.Trp", "midi.brass4"]
ceol_instlist[60] = ["MIDI", "Fr.Horn", "midi.brass5"]
ceol_instlist[61] = ["MIDI", "BrasSect", "midi.brass6"]
ceol_instlist[62] = ["MIDI", "SynBras1", "midi.brass7"]
ceol_instlist[63] = ["MIDI", "SynBras2", "midi.brass8"]
ceol_instlist[64] = ["MIDI", "SprnoSax", "midi.reed1"]
ceol_instlist[65] = ["MIDI", "Alto Sax", "midi.reed2"]
ceol_instlist[66] = ["MIDI", "TenorSax", "midi.reed3"]
ceol_instlist[67] = ["MIDI", "Bari.Sax", "midi.reed4"]
ceol_instlist[68] = ["MIDI", "Oboe", "midi.reed5"]
ceol_instlist[69] = ["MIDI", "Eng.Horn", "midi.reed6"]
ceol_instlist[70] = ["MIDI", "Bassoon", "midi.reed7"]
ceol_instlist[71] = ["MIDI", "Clarinet", "midi.reed8"]
ceol_instlist[72] = ["MIDI", "Piccolo", "midi.pipe1"]
ceol_instlist[73] = ["MIDI", "Flute", "midi.pipe2"]
ceol_instlist[74] = ["MIDI", "Recorder", "midi.pipe3"]
ceol_instlist[75] = ["MIDI", "PanFlute", "midi.pipe4"]
ceol_instlist[76] = ["MIDI", "Bottle", "midi.pipe5"]
ceol_instlist[77] = ["MIDI", "Shakhchi", "midi.pipe6"]
ceol_instlist[78] = ["MIDI", "Whistle", "midi.pipe7"]
ceol_instlist[79] = ["MIDI", "Ocarina", "midi.pipe8"]
ceol_instlist[80] = ["MIDI", "SquareLd", "midi.lead1"]
ceol_instlist[81] = ["MIDI", "Saw.Lead", "midi.lead2"]
ceol_instlist[82] = ["MIDI", "CaliopLd", "midi.lead3"]
ceol_instlist[83] = ["MIDI", "ChiffLd", "midi.lead4"]
ceol_instlist[84] = ["MIDI", "CharanLd", "midi.lead5"]
ceol_instlist[85] = ["MIDI", "Voice Ld", "midi.lead6"]
ceol_instlist[86] = ["MIDI", "Fifth Ld", "midi.lead7"]
ceol_instlist[87] = ["MIDI", "Bass &Ld", "midi.lead8"]
ceol_instlist[88] = ["MIDI", "NewAgePd", "midi.pad1"]
ceol_instlist[89] = ["MIDI", "Warm Pad", "midi.pad2"]
ceol_instlist[90] = ["MIDI", "PolySyPd", "midi.pad3"]
ceol_instlist[91] = ["MIDI", "ChoirPad", "midi.pad4"]
ceol_instlist[92] = ["MIDI", "BowedPad", "midi.pad5"]
ceol_instlist[93] = ["MIDI", "MetalPad", "midi.pad6"]
ceol_instlist[94] = ["MIDI", "Halo Pad", "midi.pad7"]
ceol_instlist[95] = ["MIDI", "SweepPad", "midi.pad8"]
ceol_instlist[96] = ["MIDI", "Rain", "midi.fx1"]
ceol_instlist[97] = ["MIDI", "SoundTrk", "midi.fx2"]
ceol_instlist[98] = ["MIDI", "Crystal", "midi.fx3"]
ceol_instlist[99] = ["MIDI", "Atmosphr", "midi.fx4"]
ceol_instlist[100] = ["MIDI", "Bright", "midi.fx5"]
ceol_instlist[101] = ["MIDI", "Goblins", "midi.fx6"]
ceol_instlist[102] = ["MIDI", "Echoes", "midi.fx7"]
ceol_instlist[103] = ["MIDI", "Sci-Fi", "midi.fx8"]
ceol_instlist[104] = ["MIDI", "Sitar", "midi.world1"]
ceol_instlist[105] = ["MIDI", "Banjo", "midi.world2"]
ceol_instlist[106] = ["MIDI", "Shamisen", "midi.world3"]
ceol_instlist[107] = ["MIDI", "Koto", "midi.world4"]
ceol_instlist[108] = ["MIDI", "Kalimba", "midi.world5"]
ceol_instlist[109] = ["MIDI", "Bagpipe", "midi.world6"]
ceol_instlist[110] = ["MIDI", "Fiddle", "midi.world7"]
ceol_instlist[111] = ["MIDI", "Shanai", "midi.world8"]
ceol_instlist[112] = ["MIDI", "TnklBell", "midi.percus1"]
ceol_instlist[113] = ["MIDI", "Agogo", "midi.percus2"]
ceol_instlist[114] = ["MIDI", "SteelDrm", "midi.percus3"]
ceol_instlist[115] = ["MIDI", "WoodBlok", "midi.percus4"]
ceol_instlist[116] = ["MIDI", "TaikoDrm", "midi.percus5"]
ceol_instlist[117] = ["MIDI", "MelodTom", "midi.percus6"]
ceol_instlist[118] = ["MIDI", "Syn.Drum", "midi.percus7"]
ceol_instlist[119] = ["MIDI", "RevCymbl", "midi.percus8"]
ceol_instlist[120] = ["MIDI", "FretNoiz", "midi.se1"]
ceol_instlist[121] = ["MIDI", "BrthNoiz", "midi.se2"]
ceol_instlist[122] = ["MIDI", "Seashore", "midi.se3"]
ceol_instlist[123] = ["MIDI", "Tweet", "midi.se4"]
ceol_instlist[124] = ["MIDI", "Telphone", "midi.se5"]
ceol_instlist[125] = ["MIDI", "Helicptr", "midi.se6"]
ceol_instlist[126] = ["MIDI", "Applause", "midi.se7"]
ceol_instlist[127] = ["MIDI", "Gunshot", "midi.se8"]
ceol_instlist[128] = ["CHIPTUNE", "Square Wave", "square"]
ceol_instlist[129] = ["CHIPTUNE", "Saw Wave", "saw"]
ceol_instlist[130] = ["CHIPTUNE", "Triangle Wave", "triangle"]
ceol_instlist[131] = ["CHIPTUNE", "Sine Wave", "sine"]
ceol_instlist[132] = ["CHIPTUNE", "Noise", "noise"]
ceol_instlist[133] = ["CHIPTUNE", "Dual Square", "dualsquare"]
ceol_instlist[134] = ["CHIPTUNE", "Dual Saw", "dualsaw"]
ceol_instlist[135] = ["CHIPTUNE", "Triangle LO-FI", "triangle8"]
ceol_instlist[136] = ["CHIPTUNE", "Konami Wave", "konami"]
ceol_instlist[137] = ["CHIPTUNE", "Ramp Wave", "ramp"]
ceol_instlist[138] = ["CHIPTUNE", "Pulse Wave", "beep"]
ceol_instlist[139] = ["CHIPTUNE", "MA3 Wave", "ma1"]
ceol_instlist[140] = ["CHIPTUNE", "Noise (Bass)", "bassdrumm"]
ceol_instlist[141] = ["CHIPTUNE", "Noise (Snare)", "snare"]
ceol_instlist[142] = ["CHIPTUNE", "Noise (Hi-Hat)", "closedhh"]
ceol_instlist[143] = ["BASS", "Analog Bass", "valsound.bass1"]
ceol_instlist[144] = ["BASS", "Analog Bass #2", "valsound.bass2"]
ceol_instlist[145] = ["BASS", "Analog Bass #2 (q2)", "valsound.bass3"]
ceol_instlist[146] = ["BASS", "Chopper Bass 0", "valsound.bass4"]
ceol_instlist[147] = ["BASS", "Chopper Bass 1", "valsound.bass5"]
ceol_instlist[148] = ["BASS", "Chopper bass 2 (CUT)", "valsound.bass6"]
ceol_instlist[149] = ["BASS", "Chopper bass 3", "valsound.bass7"]
ceol_instlist[150] = ["BASS", "Elec.Chopper Bass", "valsound.bass8"]
ceol_instlist[151] = ["BASS", "Effect Bass 1", "valsound.bass9"]
ceol_instlist[152] = ["BASS", "Effect Bass 2 to UP", "valsound.bass10"]
ceol_instlist[153] = ["BASS", "Effect Bass 1", "valsound.bass11"]
ceol_instlist[154] = ["BASS", "Mohaaa", "valsound.bass12"]
ceol_instlist[155] = ["BASS", "Effect FB Bass #5", "valsound.bass13"]
ceol_instlist[156] = ["BASS", "Magical bass", "valsound.bass14"]
ceol_instlist[157] = ["BASS", "E.Bass #6", "valsound.bass15"]
ceol_instlist[158] = ["BASS", "E.Bass #7", "valsound.bass16"]
ceol_instlist[159] = ["BASS", "E.Bass 70", "valsound.bass17"]
ceol_instlist[160] = ["BASS", "VAL006 Euro", "valsound.bass18"]
ceol_instlist[161] = ["BASS", "E.Bass x2", "valsound.bass19"]
ceol_instlist[162] = ["BASS", "E.Bass x4", "valsound.bass20"]
ceol_instlist[163] = ["BASS", "Metal pick bass X5", "valsound.bass21"]
ceol_instlist[164] = ["BASS", "Groove Bass #1", "valsound.bass22"]
ceol_instlist[165] = ["BASS", "Analog Groove #2", "valsound.bass23"]
ceol_instlist[166] = ["BASS", "Harmonics #1", "valsound.bass24"]
ceol_instlist[167] = ["BASS", "Low Bass x1", "valsound.bass25"]
ceol_instlist[168] = ["BASS", "Low_bass x2", "valsound.bass26"]
ceol_instlist[169] = ["BASS", "Low Bass Rezzo", "valsound.bass27"]
ceol_instlist[170] = ["BASS", "Low Bass Picked", "valsound.bass28"]
ceol_instlist[171] = ["BASS", "Metal Bass", "valsound.bass29"]
ceol_instlist[172] = ["BASS", "e.n.bass 1", "valsound.bass30"]
ceol_instlist[173] = ["BASS", "psg bass 1", "valsound.bass31"]
ceol_instlist[174] = ["BASS", "psg bass 2", "valsound.bass32"]
ceol_instlist[175] = ["BASS", "rezonance bass", "valsound.bass33"]
ceol_instlist[176] = ["BASS", "slap bass", "valsound.bass34"]
ceol_instlist[177] = ["BASS", "slap bass 1", "valsound.bass35"]
ceol_instlist[178] = ["BASS", "slap bass 2 (1+)", "valsound.bass36"]
ceol_instlist[179] = ["BASS", "slap bass #3", "valsound.bass37"]
ceol_instlist[180] = ["BASS", "slap bass pull", "valsound.bass38"]
ceol_instlist[181] = ["BASS", "slap bass mute", "valsound.bass39"]
ceol_instlist[182] = ["BASS", "slap bass pick", "valsound.bass40"]
ceol_instlist[183] = ["BASS", "super bass #2", "valsound.bass41"]
ceol_instlist[184] = ["BASS", "sp_bass#3 soft", "valsound.bass42"]
ceol_instlist[185] = ["BASS", "sp_bass#4 soft*2", "valsound.bass43"]
ceol_instlist[186] = ["BASS", "sp_bass#5 attack", "valsound.bass44"]
ceol_instlist[187] = ["BASS", "sp.bass#6 rezz", "valsound.bass45"]
ceol_instlist[188] = ["BASS", "synth bass 1", "valsound.bass46"]
ceol_instlist[189] = ["BASS", "synth bass 2 myon", "valsound.bass47"]
ceol_instlist[190] = ["BASS", "synth bass #3 cho!", "valsound.bass48"]
ceol_instlist[191] = ["BASS", "synth-wind-bass #4", "valsound.bass49"]
ceol_instlist[192] = ["BASS", "synth bass #5 q2", "valsound.bass50"]
ceol_instlist[193] = ["BASS", "old wood bass", "valsound.bass51"]
ceol_instlist[194] = ["BASS", "w.bass bright", "valsound.bass52"]
ceol_instlist[195] = ["BASS", "w.bass x2 bow", "valsound.bass53"]
ceol_instlist[196] = ["BASS", "Wood Bass 3", "valsound.bass54"]
ceol_instlist[197] = ["BRASS", "Brass strings", "valsound.brass1"]
ceol_instlist[198] = ["BRASS", "E.mute Trampet", "valsound.brass2"]
ceol_instlist[199] = ["BRASS", "HORN 2", "valsound.brass3"]
ceol_instlist[200] = ["BRASS", "Alpine Horn #3", "valsound.brass4"]
ceol_instlist[201] = ["BRASS", "Lead brass", "valsound.brass5"]
ceol_instlist[202] = ["BRASS", "Normal HORN", "valsound.brass6"]
ceol_instlist[203] = ["BRASS", "Synth Oboe", "valsound.brass7"]
ceol_instlist[204] = ["BRASS", "Oboe 2", "valsound.brass8"]
ceol_instlist[205] = ["BRASS", "Attack Brass (q2)", "valsound.brass9"]
ceol_instlist[206] = ["BRASS", "SAX", "valsound.brass10"]
ceol_instlist[207] = ["BRASS", "Soft brass(lead)", "valsound.brass11"]
ceol_instlist[208] = ["BRASS", "Synth Brass 1 OLD", "valsound.brass12"]
ceol_instlist[209] = ["BRASS", "Synth Brass 2 OLD", "valsound.brass13"]
ceol_instlist[210] = ["BRASS", "Synth Brass 3", "valsound.brass14"]
ceol_instlist[211] = ["BRASS", "Synth Brass #4", "valsound.brass15"]
ceol_instlist[212] = ["BRASS", "Syn.Brass 5(long)", "valsound.brass16"]
ceol_instlist[213] = ["BRASS", "Synth Brass 6", "valsound.brass17"]
ceol_instlist[214] = ["BRASS", "Trumpet", "valsound.brass18"]
ceol_instlist[215] = ["BRASS", "Trumpet 2", "valsound.brass19"]
ceol_instlist[216] = ["BRASS", "Twin Horn (or OL=25)", "valsound.brass20"]
ceol_instlist[217] = ["BELL", "Calm Bell", "valsound.bell1"]
ceol_instlist[218] = ["BELL", "China Bell Double", "valsound.bell2"]
ceol_instlist[219] = ["BELL", "Church Bell", "valsound.bell3"]
ceol_instlist[220] = ["BELL", "Church Bell 2", "valsound.bell4"]
ceol_instlist[221] = ["BELL", "Glocken 1", "valsound.bell5"]
ceol_instlist[222] = ["BELL", "Harp #1", "valsound.bell6"]
ceol_instlist[223] = ["BELL", "Harp #2", "valsound.bell7"]
ceol_instlist[224] = ["BELL", "Kirakira", "valsound.bell8"]
ceol_instlist[225] = ["BELL", "Marimba", "valsound.bell9"]
ceol_instlist[226] = ["BELL", "Old Bell", "valsound.bell10"]
ceol_instlist[227] = ["BELL", "Percus. Bell", "valsound.bell11"]
ceol_instlist[228] = ["BELL", "Pretty Bell", "valsound.bell12"]
ceol_instlist[229] = ["BELL", "Synth Bell #0", "valsound.bell13"]
ceol_instlist[230] = ["BELL", "Synth Bell #1 o5", "valsound.bell14"]
ceol_instlist[231] = ["BELL", "Synth Bell 2", "valsound.bell15"]
ceol_instlist[232] = ["BELL", "Viberaphone", "valsound.bell16"]
ceol_instlist[233] = ["BELL", "Twin Marinba", "valsound.bell17"]
ceol_instlist[234] = ["BELL", "Bellend", "valsound.bell18"]
ceol_instlist[235] = ["GUITAR", "Guitar VeloLow", "valsound.guitar1"]
ceol_instlist[236] = ["GUITAR", "Guitar VeloHigh", "valsound.guitar2"]
ceol_instlist[237] = ["GUITAR", "A.Guitar #3", "valsound.guitar3"]
ceol_instlist[238] = ["GUITAR", "Cutting E.Guitar", "valsound.guitar4"]
ceol_instlist[239] = ["GUITAR", "Dis. Synth (old)", "valsound.guitar5"]
ceol_instlist[240] = ["GUITAR", "Dra-spi-Dis.G.", "valsound.guitar6"]
ceol_instlist[241] = ["GUITAR", "Dis.Guitar 3-", "valsound.guitar7"]
ceol_instlist[242] = ["GUITAR", "Dis.Guitar 3+", "valsound.guitar8"]
ceol_instlist[243] = ["GUITAR", "Feed-back Guitar 1", "valsound.guitar9"]
ceol_instlist[244] = ["GUITAR", "Hard Dis. Guitar 1", "valsound.guitar10"]
ceol_instlist[245] = ["GUITAR", "Hard Dis.Guitar 3", "valsound.guitar11"]
ceol_instlist[246] = ["GUITAR", "Dis.Guitar '94 Hard", "valsound.guitar12"]
ceol_instlist[247] = ["GUITAR", "New Dis.Guitar 1", "valsound.guitar13"]
ceol_instlist[248] = ["GUITAR", "New Dis.Guitar 2", "valsound.guitar14"]
ceol_instlist[249] = ["GUITAR", "New Dis.Guitar 3", "valsound.guitar15"]
ceol_instlist[250] = ["GUITAR", "Overdrive.G. (AL=013)", "valsound.guitar16"]
ceol_instlist[251] = ["GUITAR", "METAL", "valsound.guitar17"]
ceol_instlist[252] = ["GUITAR", "Soft Dis.Guitar", "valsound.guitar18"]
ceol_instlist[253] = ["LEAD", "Aco code", "valsound.lead1"]
ceol_instlist[254] = ["LEAD", "Analog synthe 1", "valsound.lead2"]
ceol_instlist[255] = ["LEAD", "Bosco-lead", "valsound.lead3"]
ceol_instlist[256] = ["LEAD", "Cosmo Lead", "valsound.lead4"]
ceol_instlist[257] = ["LEAD", "Cosmo Lead 2", "valsound.lead5"]
ceol_instlist[258] = ["LEAD", "Digital lead #1", "valsound.lead6"]
ceol_instlist[259] = ["LEAD", "Double sin wave", "valsound.lead7"]
ceol_instlist[260] = ["LEAD", "E.Organ 2 bright", "valsound.lead8"]
ceol_instlist[261] = ["LEAD", "E.Organ 2 (voice)", "valsound.lead9"]
ceol_instlist[262] = ["LEAD", "E.Organ 4 Click", "valsound.lead10"]
ceol_instlist[263] = ["LEAD", "E.Organ 5 Click", "valsound.lead11"]
ceol_instlist[264] = ["LEAD", "E.Organ 6", "valsound.lead12"]
ceol_instlist[265] = ["LEAD", "E.Organ 7 Church", "valsound.lead13"]
ceol_instlist[266] = ["LEAD", "Metal Lead", "valsound.lead14"]
ceol_instlist[267] = ["LEAD", "Metal Lead 3", "valsound.lead15"]
ceol_instlist[268] = ["LEAD", "MONO Lead", "valsound.lead16"]
ceol_instlist[269] = ["LEAD", "PSG like PC88 (long)", "valsound.lead17"]
ceol_instlist[270] = ["LEAD", "PSG Cut 1", "valsound.lead18"]
ceol_instlist[271] = ["LEAD", "Attack Synth", "valsound.lead19"]
ceol_instlist[272] = ["LEAD", "Sin wave", "valsound.lead20"]
ceol_instlist[273] = ["LEAD", "Synth, Bell 2", "valsound.lead21"]
ceol_instlist[274] = ["LEAD", "Chorus #2(Voice)+bell", "valsound.lead22"]
ceol_instlist[275] = ["LEAD", "Synth Cut 8-4", "valsound.lead23"]
ceol_instlist[276] = ["LEAD", "Synth long 8-4", "valsound.lead24"]
ceol_instlist[277] = ["LEAD", "ACO_Code #2", "valsound.lead25"]
ceol_instlist[278] = ["LEAD", "ACO_Code #3", "valsound.lead26"]
ceol_instlist[279] = ["LEAD", "Synth FB long 4", "valsound.lead27"]
ceol_instlist[280] = ["LEAD", "Synth FB long 5", "valsound.lead28"]
ceol_instlist[281] = ["LEAD", "Synth Lead 0", "valsound.lead29"]
ceol_instlist[282] = ["LEAD", "Synth Lead 1", "valsound.lead30"]
ceol_instlist[283] = ["LEAD", "Synth Lead 2", "valsound.lead31"]
ceol_instlist[284] = ["LEAD", "Synth Lead 3", "valsound.lead32"]
ceol_instlist[285] = ["LEAD", "Synth Lead 4", "valsound.lead33"]
ceol_instlist[286] = ["LEAD", "Synth Lead 5", "valsound.lead34"]
ceol_instlist[287] = ["LEAD", "Synth Lead 6", "valsound.lead35"]
ceol_instlist[288] = ["LEAD", "Synth Lead 7 (Soft FB)", "valsound.lead36"]
ceol_instlist[289] = ["LEAD", "Synth PSG", "valsound.lead37"]
ceol_instlist[290] = ["LEAD", "Synth PSG 2", "valsound.lead38"]
ceol_instlist[291] = ["LEAD", "Synth PSG 3", "valsound.lead39"]
ceol_instlist[292] = ["LEAD", "Synth PSG 4", "valsound.lead40"]
ceol_instlist[293] = ["LEAD", "Synth PSG 5", "valsound.lead41"]
ceol_instlist[294] = ["LEAD", "Sin water synth", "valsound.lead42"]
ceol_instlist[295] = ["PIANO", "Aco Piano2 (Attack)", "valsound.piano1"]
ceol_instlist[296] = ["PIANO", "Backing 1 (Clav.)", "valsound.piano2"]
ceol_instlist[297] = ["PIANO", "Clav. coad", "valsound.piano3"]
ceol_instlist[298] = ["PIANO", "Deep Piano 1", "valsound.piano4"]
ceol_instlist[299] = ["PIANO", "Deep Piano 3", "valsound.piano5"]
ceol_instlist[300] = ["PIANO", "E.piano #2", "valsound.piano6"]
ceol_instlist[301] = ["PIANO", "E.piano #3", "valsound.piano7"]
ceol_instlist[302] = ["PIANO", "E.piano #4(2+)", "valsound.piano8"]
ceol_instlist[303] = ["PIANO", "E.(Bell)Piano #5", "valsound.piano9"]
ceol_instlist[304] = ["PIANO", "E.Piano #6", "valsound.piano10"]
ceol_instlist[305] = ["PIANO", "E.Piano #7", "valsound.piano11"]
ceol_instlist[306] = ["PIANO", "Harpci chord 1", "valsound.piano12"]
ceol_instlist[307] = ["PIANO", "Harpci 2", "valsound.piano13"]
ceol_instlist[308] = ["PIANO", "Piano1", "valsound.piano14"]
ceol_instlist[309] = ["PIANO", "Piano3", "valsound.piano15"]
ceol_instlist[310] = ["PIANO", "Piano4", "valsound.piano16"]
ceol_instlist[311] = ["PIANO", "Digital Piano #5", "valsound.piano17"]
ceol_instlist[312] = ["PIANO", "Piano 6 High-tone", "valsound.piano18"]
ceol_instlist[313] = ["PIANO", "Panning Harpci", "valsound.piano19"]
ceol_instlist[314] = ["PIANO", "Yam Harpci chord", "valsound.piano20"]
ceol_instlist[315] = ["SPECIAL", "S.E.(Detune is needed o2c)", "valsound.se1"]
ceol_instlist[316] = ["SPECIAL", "S.E. 2 o0-1-2", "valsound.se2"]
ceol_instlist[317] = ["SPECIAL", "S.E. 3(Feedin /noise add.)", "valsound.se3"]
ceol_instlist[318] = ["SPECIAL", "Digital 1", "valsound.special1"]
ceol_instlist[319] = ["SPECIAL", "Digital 2", "valsound.special2"]
ceol_instlist[320] = ["SPECIAL", "Digital[BAS] 3 o2-o3", "valsound.special3"]
ceol_instlist[321] = ["SPECIAL", "Digital[GTR] 3 o2-o3", "valsound.special4"]
ceol_instlist[322] = ["SPECIAL", "Digital 4 o4a", "valsound.special5"]
ceol_instlist[323] = ["STRINGS", "Accordion1", "valsound.strpad1"]
ceol_instlist[324] = ["STRINGS", "Accordion2", "valsound.strpad2"]
ceol_instlist[325] = ["STRINGS", "Accordion3", "valsound.strpad3"]
ceol_instlist[326] = ["STRINGS", "Chorus #2(Voice)", "valsound.strpad4"]
ceol_instlist[327] = ["STRINGS", "Chorus #3", "valsound.strpad5"]
ceol_instlist[328] = ["STRINGS", "Chorus #4", "valsound.strpad6"]
ceol_instlist[329] = ["STRINGS", "F.Strings 1", "valsound.strpad7"]
ceol_instlist[330] = ["STRINGS", "F.Strings 2", "valsound.strpad8"]
ceol_instlist[331] = ["STRINGS", "F.Strings 3", "valsound.strpad9"]
ceol_instlist[332] = ["STRINGS", "F.Strings 4 (low)", "valsound.strpad10"]
ceol_instlist[333] = ["STRINGS", "Pizzicate#1(KOTO2)", "valsound.strpad11"]
ceol_instlist[334] = ["STRINGS", "sound truck modoki", "valsound.strpad12"]
ceol_instlist[335] = ["STRINGS", "Strings", "valsound.strpad13"]
ceol_instlist[336] = ["STRINGS", "Synth Accordion", "valsound.strpad14"]
ceol_instlist[337] = ["STRINGS", "Phaser synthe.", "valsound.strpad15"]
ceol_instlist[338] = ["STRINGS", "FB Synth.", "valsound.strpad16"]
ceol_instlist[339] = ["STRINGS", "Synth Strings MB", "valsound.strpad17"]
ceol_instlist[340] = ["STRINGS", "Synth Strings #2", "valsound.strpad18"]
ceol_instlist[341] = ["STRINGS", "Synth.Sweep Pad #1", "valsound.strpad19"]
ceol_instlist[342] = ["STRINGS", "Twin synth. #1 Calm", "valsound.strpad20"]
ceol_instlist[343] = ["STRINGS", "Twin synth. #2 FB", "valsound.strpad21"]
ceol_instlist[344] = ["STRINGS", "Twin synth. #3 FB", "valsound.strpad22"]
ceol_instlist[345] = ["STRINGS", "Vocoder voice1", "valsound.strpad23"]
ceol_instlist[346] = ["STRINGS", "Voice o3-o5", "valsound.strpad24"]
ceol_instlist[347] = ["STRINGS", "Voice' o3-o5", "valsound.strpad25"]
ceol_instlist[348] = ["WIND", "Clarinet #1", "valsound.wind1"]
ceol_instlist[349] = ["WIND", "Clarinet #2 Brighter", "valsound.wind2"]
ceol_instlist[350] = ["WIND", "E.Flute", "valsound.wind3"]
ceol_instlist[351] = ["WIND", "E.Flute 2", "valsound.wind4"]
ceol_instlist[352] = ["WIND", "Flute + Bell", "valsound.wind5"]
ceol_instlist[353] = ["WIND", "Old flute", "valsound.wind6"]
ceol_instlist[354] = ["WIND", "Whistle 1", "valsound.wind7"]
ceol_instlist[355] = ["WIND", "Whistle 2", "valsound.wind8"]
ceol_instlist[356] = ["WORLD", "Banjo (Harpci)", "valsound.world1"]
ceol_instlist[357] = ["WORLD", "KOTO", "valsound.world2"]
ceol_instlist[358] = ["WORLD", "Koto 2", "valsound.world3"]
ceol_instlist[359] = ["WORLD", "Sitar 1", "valsound.world4"]
ceol_instlist[360] = ["WORLD", "Shamisen 2", "valsound.world5"]
ceol_instlist[361] = ["WORLD", "Shamisen 1", "valsound.world6"]
ceol_instlist[362] = ["WORLD", "Synth Shamisen", "valsound.world7"]
ceol_instlist[363] = ["DRUMKIT", "Simple Drumkit", "drumkit.1"]
ceol_instlist[364] = ["DRUMKIT", "SiON Drumkit", "drumkit.2"]
ceol_instlist[365] = ["DRUMKIT", "Midi Drumkit", "drumkit.3"]

ceol_colors = {}
ceol_colors[0] = [0.23, 0.15, 0.93]
ceol_colors[1] = [0.61, 0.04, 0.94]
ceol_colors[2] = [0.82, 0.16, 0.23]
ceol_colors[3] = [0.82, 0.60, 0.16]
ceol_colors[4] = [0.21, 0.84, 0.14]
ceol_colors[5] = [0.07, 0.56, 0.91]

datapos = 0

def ceol_read():
    global datapos
    global ceol_data
    output = int(ceol_data[datapos])
    datapos += 1
    return output



class input_ceol(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'ceol'
    def getname(self): return 'Bosca Ceoil'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):

        cvpj_l = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_notelistindex = {}
        cvpj_l_playlist = {}

        global datapos
        global ceol_data
        fs_ceol = open(input_file, 'r')
        ceol_data = fs_ceol.readline().split(',')

        ceol_basic_versionnum = ceol_read()
        ceol_basic_swing = ceol_read()
        ceol_basic_effect = ceol_read()
        ceol_basic_effectvalue = ceol_read()
        ceol_basic_bpm = ceol_read()
        ceol_basic_patternlength = ceol_read()
        ceol_basic_barlength = ceol_read()

        ceol_numinstrument = ceol_read()

        for instnum in range(ceol_numinstrument):
            cvpj_instid = 'ceol_'+str(instnum).zfill(2)

            ceol_inst_number = ceol_read()
            ceol_inst_type = ceol_read()
            ceol_inst_palette = ceol_read()
            ceol_inst_cutoff = ceol_read()
            ceol_inst_resonance = ceol_read()
            ceol_inst_volume = ceol_read()

            ceol_instinfo = ceol_instlist[ceol_inst_number]

            cvpj_inst = {}
            cvpj_inst["instdata"] = {}
            cvpj_inst["name"] = ceol_instinfo[1]
            cvpj_inst["vol"] = ceol_inst_volume/256
            if ceol_inst_palette in ceol_colors: cvpj_inst["color"] = ceol_colors[ceol_inst_palette]
            else: cvpj_inst["color"] = [0.55, 0.55, 0.55]
            cvpj_instdata = cvpj_inst["instdata"]
            cvpj_instdata['plugindata'] = {}
            if ceol_instinfo[0] == 'MIDI':
                cvpj_instdata['plugin'] = 'general-midi'
                cvpj_instdata['plugindata'] = {'bank':0, 'inst':ceol_inst_number}
            elif ceol_inst_number == 128: cvpj_instdata['plugin'] = 'shape-square'
            elif ceol_inst_number == 129: cvpj_instdata['plugin'] = 'shape-saw'
            elif ceol_inst_number == 130: cvpj_instdata['plugin'] = 'shape-triangle'
            elif ceol_inst_number == 131: cvpj_instdata['plugin'] = 'shape-sine'
            elif ceol_inst_number == 132: cvpj_instdata['plugin'] = 'retro-noise'
            else: cvpj_instdata['plugin'] = 'none'
            cvpj_l_instruments[cvpj_instid] = cvpj_inst
            cvpj_l_instrumentsorder.append(cvpj_instid)

        ceol_numpattern = ceol_read()
        for patnum in range(ceol_numpattern):
            cvpj_notelist = []

            t_notepos_table = {}
            for t_notepos in range(ceol_basic_patternlength):
                t_notepos_table[t_notepos] = []

            cvpj_pat_id = 'ceol_'+str(patnum).zfill(3)

            ceol_pat_key = ceol_read()
            ceol_pat_scale = ceol_read()
            ceol_pat_instrument = ceol_read()
            ceol_pat_palette = ceol_read()
            ceol_numnotes = ceol_read()

            for _ in range(ceol_numnotes):
                ceol_nl_key = ceol_read()-60
                ceol_nl_len = ceol_read()
                ceol_nl_pos = ceol_read()
                ceol_read()
                t_notepos_table[ceol_nl_pos].append({'key': ceol_nl_key, 'instrument': 'ceol_'+str(ceol_pat_instrument).zfill(2), 'duration': ceol_nl_len})

            ceol_recordfilter = ceol_read()
            if ceol_recordfilter == 1:
                for _ in range(32):
                    ceol_read()
                    ceol_read()
                    ceol_read()

            for position in t_notepos_table:
            	for note in t_notepos_table[position]:
            		cvpj_notelist.append(note | {'position': position})

            cvpj_pat = {}
            if ceol_pat_palette in ceol_colors: cvpj_pat["color"] = ceol_colors[ceol_pat_palette]
            else: cvpj_pat["color"] = [0.55, 0.55, 0.55]
            cvpj_pat["notelist"] = cvpj_notelist
            cvpj_pat["name"] = str(patnum)
            cvpj_l_notelistindex[cvpj_pat_id] = cvpj_pat

        cvpj_l_playlist['1'] = {'color': [0.43, 0.52, 0.55], 'placements':[]}
        cvpj_l_playlist['2'] = {'color': [0.31, 0.40, 0.42], 'placements':[]}
        cvpj_l_playlist['3'] = {'color': [0.43, 0.52, 0.55], 'placements':[]}
        cvpj_l_playlist['4'] = {'color': [0.31, 0.40, 0.42], 'placements':[]}
        cvpj_l_playlist['5'] = {'color': [0.43, 0.52, 0.55], 'placements':[]}
        cvpj_l_playlist['6'] = {'color': [0.31, 0.40, 0.42], 'placements':[]}
        cvpj_l_playlist['7'] = {'color': [0.43, 0.52, 0.55], 'placements':[]}
        cvpj_l_playlist['8'] = {'color': [0.31, 0.40, 0.42], 'placements':[]}

        ceol_arr_length = ceol_read()
        ceol_arr_loopstart = ceol_read()
        ceol_arr_loopend = ceol_read()

        for plpos in range(ceol_arr_length):
            for plnum in range(8):
                plpatnum = ceol_read()
                if plpatnum != -1:
                    cvpj_l_placement = {}
                    cvpj_l_placement['type'] = "instruments"
                    cvpj_l_placement['position'] = plpos*ceol_basic_patternlength
                    cvpj_l_placement['fromindex'] = 'ceol_'+str(plpatnum).zfill(3)
                    cvpj_l_playlist[str(plnum+1)]['placements'].append(cvpj_l_placement)


        timesig = placements.get_timesig(ceol_basic_patternlength, ceol_basic_barlength)
        cvpj_l['timesig_numerator'] = timesig[0]
        cvpj_l['timesig_denominator'] = timesig[1]
        cvpj_l['notelistindex'] = cvpj_l_notelistindex
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = ceol_basic_bpm
        return json.dumps(cvpj_l)