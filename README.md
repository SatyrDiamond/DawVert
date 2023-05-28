<div align="center">
<img alt="DawVert Logo" src="docs/dawvert.svg" width=23% height=23%>

# DawVert - The DAW ConVERTer
</div>

DawVert is a Project File Converter

<p align="center">
  <a title="Discord Server" href="https://discord.gg/SWkR6Z9pQC">
    <img alt="Discord Server" src="https://img.shields.io/discord/1094015153529430129?label=Discord&logo=Discord&logoColor=fff&style=for-the-badge">
  </a>
</p>

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

Song Number (used for Multi-Song inputs): 
--songnum <number>

MultipleIndexed2Multiple:  
--mi2m--output-unused-nle           (Output Unused Patterns)

e.g: 
    python3 DawVert.py --soundfont "MuseScore_General.sf2" -it notessimo_v2 -i song.note -ot flp -o out.flp

    python3 DawVert.py --samplefolder "a diffrent folder" -i "song.s3m" -ot lmms -o out.mmp

    python3 DawVert.py --songnum 3 -it famistudio_txt -i "song.txt" -ot lmms -o out.mmp
```

## Required Libraries
```
varint
numpy
mido
lxml
chardet
av
beautifulsoup4
blackboxprotobuf
git+https://github.com/Perlence/rpp
```

## Optional Libraries
```
xmodits_py - for extracting Impulse Tracker and FastTracker2 Samples
```

## Supported Outputs

| DataType | Short Name | Name |
| --- | --- | :--- |
| M-I | ```flp``` | FL Studio |
| R | ```lmms``` | LMMS |
| R | ```ableton``` | Ableton Live 11 |
| R | ```midi``` | MIDI |
| R | ```muse``` | MusE Sequencer |
| R | ```reaper``` | Reaper |

## (Some) Supported Inputs
[Full List...](docs/input_plugins.md)

| DataType | Short Name | Name | Ext | Autodetect | 
| --- | --- | :--- | :--- | :--- |
| M | ```midi``` | MIDI | ```.mid``` | ✔️ | 
| M-I | ```flp``` | FL Studio | ```.flp``` | ✔️ |
| R | ```ableton``` | Ableton Live 11 | ```.als``` | ✔️ |
| R | ```lmms``` | LMMS | ```.mmp``` | ✔️ |
| M | ```mod``` | ProTracker | ```.mod``` | ❌ | 
| M | ```xm``` | FastTracker 2 | ```.xm``` | ✔️ | 
| M | ```s3m``` | Scream Tracker 3 | ```.s3m``` | ✔️ | 
| M | ```it``` | Impulse Tracker | ```.it``` | ✔️ | 
| R | ```orgyana``` | Orgyana/OrgMaker | ```.org``` | ✔️ |
| M | ```ptcop``` | PxTone | ```.ptcop``` | ✔️ |
| M-I | ```jummbox``` | Beepbox/Jummbox | ```.json``` | ❌ | 
| M-I | ```famistudio_txt``` | FamiStudio Text | ```.txt``` | ❌ | 

## VST Plugins
[Full List...](docs/vsts.md)