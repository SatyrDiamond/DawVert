
# DawVert

Supported Inputs (DAWs): FL Studio, LMMS

Supported Inputs (Tracker): MOD, S3M, IT

Supported Inputs (Others): FamiStudio, Bosca Ceoil, PiyoPiyo, Lovely Composer

Supported Outputs: LMMS, FL Studio

## How to Use
```
python3 DawVert.py <input> <output type> <output>

input type: -it 
input file: -i 
output type: -ot 
output file: -o

e.g: 
    python3 DawVert.py -i song.txt -ot flp -o out.flp

    python3 DawVert.py -it fs_txt -i song.txt -ot flp -o out.flp

```

## VST Plugins

[Grace](https://github.com/s-oram/Grace)

[juicysfplugin](https://github.com/Birch-san/juicysfplugin)

[Zyn-Fusion](https://zynaddsubfx.sourceforge.io/zyn-fusion.html)

[Magical 8bit Plug 2](https://github.com/yokemura/Magical8bitPlug2)

## Supported DAWs

| PluginType | DataType | Short Name | Name | 
| --- | --- | --- | :--- |
| Input | M-I | ```flp``` | FL Studio | 
| Input | R | ```lmms``` | LMMS | 
| Input | M | ```mod``` | ProTracker  | 
| Input | M | ```s3m``` | Scream Tracker 3 | 
| Input | M | ```it``` | Impulse Tracker | 
| Input | M-I | ```fs_txt``` | FamiStudio Text | 
| Input | M-I | ```ceol``` | Bosca Ceoil | 
| Input | R | ```piyopiyo``` | PiyoPiyo | 
| Input | M | ```lovelycomposer``` | Lovely Composer | 
| output | M-I | ```flp``` | FL Studio | 
| output | R | ```lmms``` | LMMS |

