<div align="center">
<img alt="DawVert Logo" src="docs/dawvert.svg" width=23% height=23%>

# DawVert - The DAW ConVERTer
</div>


## How to Use

```
python3 DawVert.py -i <input> -ot <output type> -o <output>

input type: -it 
input file: -i 
output type: -ot 
output file: -o

e.g: 
    python3 DawVert.py -i song.txt -ot flp -o out.flp

    python3 DawVert.py -it jummbox -i song.txt -ot flp -o out.flp

```

## Command Line Options
```
GM Soundfont File Path (for GM MIDI instruments): 
--soundfont <sf2 file>

Sample Folder Path (path for sample extraction): 
--samplesfolder <sample folder>

e.g: 
    python3 DawVert.py --soundfont "MuseScore_General.sf2" -it notessimo_v2 -i song.note -ot flp -o out.flp

    python3 DawVert.py --samplefolder "a diffrent folder" -i "song.s3m" -ot lmms -o out.mmp
```

## VST Plugins

[Grace](https://github.com/s-oram/Grace) (Sampler)

[juicysfplugin](https://github.com/Birch-san/juicysfplugin) (Soundfont 2)

[Zyn-Fusion](https://zynaddsubfx.sourceforge.io/zyn-fusion.html) (ZynAddSubFX)

[Magical 8bit Plug 2](https://github.com/yokemura/Magical8bitPlug2)

[Vital](https://vital.audio/) (SimSynth, Beepbox)

[Ninjas2](https://github.com/clearly-broken-software/ninjas2) (Fruity Slicer)

[OPNplug](https://github.com/jpcima/ADLplug) (OPN2)

## Required Libraries
```
varint
numpy
mido
lxml
chardet
```

## Optional Libraries
```
xmodits_py - for extracting Impulse Tracker Samples
```

## Supported Outputs

| DataType | Short Name | Name |
| --- | --- | :--- |
| M-I | ```flp``` | FL Studio |
| R | ```lmms``` | LMMS |

## (Some) Supported Inputs
[Full List...](docs/input_plugins.md)

| DataType | Short Name | Name | Ext | Autodetect | 
| --- | --- | :--- | :--- | :--- |
| M | ```midi``` | MIDI | ```.mid``` | ✔️ | 
| M-I | ```flp``` | FL Studio | ```.flp``` | ✔️ |
| R | ```lmms``` | LMMS | ```.mmp``` | ✔️ |
| M | ```mod``` | ProTracker | ```.mod``` | ✔️ | 
| M | ```s3m``` | Scream Tracker 3 | ```.s3m``` | ✔️ | 
| M | ```it``` | Impulse Tracker | ```.it``` | ✔️ | 
| R | ```orgyana``` | Orgyana/OrgMaker | ```.org``` | ✔️ |
| M | ```ptcop``` | PxTone | ```.piximod``` | ✔️ |
| M-I | ```jummbox``` | Beepbox/Jummbox | ```.json``` | ❌ | 
| M-I | ```famistudio_txt``` | FamiStudio Text | ```.txt``` | ❌ | 
