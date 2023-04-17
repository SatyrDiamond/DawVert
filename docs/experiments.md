<div align="center">

# DawVert Experiments
</div>

DawVert Experiments

## How to Use

```
python3 DawVert.py --use-experiments -i <input> -ot <output type> -o <output>

input type: -it 
input file: -i 
output type: -ot 
output file: -o

e.g: 
    python3 DawVert.py -it basic_pitch -i piano.mp3 -ot flp -o out.flp

```

## Required Libraries
```
same as main

basic-pitch (for basic_pitch)
png (for color_art)
```

## Supported Inputs
| DataType | Short Name | Name | Info |
| --- | --- | :--- | :--- |
| R | ```basic_pitch``` | [Basic Pitch](https://github.com/spotify/basic-pitch) | Audio File | audio-to-MIDI converter with pitch bend detection
| R | ```color_art``` | Color Art | Image to Clip Colors