
# DawVert

## How to Use
```
python3 DawVert.py -i <input> -ot <output type> -o <output>

input type: -it 
input file: -i 
output type: -ot 
output file: -o

e.g: 
    python3 DawVert.py -i song.txt -ot flp -o out.flp

    python3 DawVert.py -it fs_txt -i song.txt -ot flp -o out.flp

```

## VST Plugins

[Grace](https://github.com/s-oram/Grace) (Sampler)

[juicysfplugin](https://github.com/Birch-san/juicysfplugin) (Soundfont 2)

[Zyn-Fusion](https://zynaddsubfx.sourceforge.io/zyn-fusion.html) (ZynAddSubFX)

[Magical 8bit Plug 2](https://github.com/yokemura/Magical8bitPlug2)

## Supported Outputs

| DataType | Short Name | Name |
| --- | --- | :--- |
| M-I | ```flp``` | FL Studio |
| R | ```lmms``` | LMMS |

## (Some) Supported Inputs
[Full List...](docs/input_plugins.md)

| DataType | Short Name | Name | Autodetect | 
| --- | --- | :--- | :--- |
| M | ```midi``` | MIDI | ✔️ | 
| M-I | ```flp``` | FL Studio | ✔️ | 
| R | ```lmms``` | LMMS | ✔️ | 
| M | ```mod``` | ProTracker | ✔️ | 
| M | ```s3m``` | Scream Tracker 3 | ✔️ | 
| M | ```it``` | Impulse Tracker | ✔️ | 
| M-I | ```famistudio_txt``` | FamiStudio Text | ❌ | 
| M-I | ```ceol``` | Bosca Ceoil | ❌ | 
| M-I | ```deflemask``` | DefleMask | ❌ | 
| M-I | ```caustic``` | Caustic 3 | ❌ |
