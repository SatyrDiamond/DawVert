# SPDX-FileCopyrightText: 2023 B0ney
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugin_input

from dataclasses import dataclass
from typing import IO, Callable, Optional, Dict

from plugin_input.mi_tracker_s3m import input_s3m as s3m
from plugin_input.mi_tracker_mod import input_mod as mod
from plugin_input.mi_tracker_it import input_it as it
from plugin_input.mi_tracker_xm import input_xm as xm

FORMATS = ["it", "xm", "s3m", "mod"]
MAGIC_UPKG = bytes([0xc1, 0x83, 0x2a, 0x9e])
MINIMUM_VERSION = 61
NULL = bytes([0])

TRACKER_FORMATS = {
    "s3m": s3m(),
    "it": it(),
    "xm": xm(),
}

class imput_umx(plugin_input.base):
    def is_dawvert_plugin(self) -> str: 
        return 'input'
    
    def getshortname(self) -> str: 
        return 'umx'
    
    def getname(self) -> str: 
        return 'Unreal Package Container'
    
    def gettype(self) -> str: 
        return 'm'
    
    def getdawcapabilities(self) -> Dict[str, bool]: 
        return { 'r_track_lanes': True }
    
    def supported_autodetect(self) -> bool: 
        return True
    
    def detect(self, input_file: str) -> bool:
        return is_umx(open(input_file, 'rb'))
    
    def parse(self, input_file: str, extra_param=None) -> Optional[str]:
        # Filename of stripped umx file
        stripped_umx = os.path.splitext(os.path.basename(input_file))[0]

        # Successfully validated and stripped umx files will return a UMXInfo class
        # which contains basic metadata about the contained tracker.
        try:
            stripped = strip_umx(input_file, stripped_umx)

            if stripped is None:
                return None
            
        except Exception as error:
            print(f"[error] { error }")
            return None    
        
        # Store the parsed cvpj json, because we need to 
        # remove the temporary file before returning it
        result = None

        try:
            # Using UMXInfo.hint() can be misleading, so iterate through a list of trackers
            # and only parse with that if it's a valid format. 
            for (extension, tracker) in TRACKER_FORMATS.items():
                if tracker.detect(stripped_umx):
                    stripped_umx = rename(stripped_umx, extension)

                    print(f"[info] Detected inner UMX format: { tracker.getname() }")
                    result = tracker.parse(stripped_umx, extra_param=extra_param)
            
            # An edge case where MOD files don't have the "detect" method.
            # In this circumstance, we can assume that valid UMX files will store a valid MOD file.
            if result is None:
                stripped_umx = rename(stripped_umx, "mod")

                result = mod().parse(stripped_umx, extra_param=extra_param)

        finally:
            # Remove the stripped umx file
            os.remove(stripped_umx)     
            
        return result

# Rename stripped umx to include file extension.
def rename(stripped_path: str, extension: str) -> str:
    os.rename(stripped_path, f"{stripped_path}.{extension}")

    return f"{stripped_path}.{extension}"


@dataclass
class UMXInfo():
    hint: str
    version: int
    size: int


def strip_umx(file: str, destination: str) -> Optional[UMXInfo]:
    with open(file, "rb") as umx_file:
        return parse_umx(umx_file, destination)


def parse_umx(file: IO, destination: str) -> Optional[UMXInfo]:
    if not is_umx(file):
        print("[error] File is not an Unreal Package")
        return None
    
    version = read_dword_le(file)
    
    if version < MINIMUM_VERSION:
        print(f"[error] UMX versions below {MINIMUM_VERSION} are not supported")
        return None
    
    skip_bytes(file, 4)
    name_count = read_dword_le(file)
    name_offset = read_dword_le(file)
    skip_bytes(file, 4)
    export_offset = read_dword_le(file)

    file.seek(name_offset) # Jump to the name table

    get_entry = read_name_table_func(version)
    contains_music = False
    hint = ""

    # Read the name table
    for _ in range(name_count):
        name = get_entry(file)

        if name == "Music":
            contains_music = True
            break

        if name.lower() in FORMATS:
            hint = name.lower()

        skip_bytes(file, 4)
    
    if not contains_music:
        print("[error] Unreal Package does not contain music")
        return None
    
    file.seek(export_offset)
    
    read_compact_index(file)    # skip class index
    read_compact_index(file)    # skip super index
    skip_bytes(file, 4)         # group
    read_compact_index(file)    # obj name
    skip_bytes(file, 4)         # obj flags

    serial_size = read_compact_index(file)

    if serial_size == 0:
        print("[error] UMX doesn't contain anything")
        return None
    
    serial_offset = read_compact_index(file)
    file.seek(serial_offset)  
    read_compact_index(file) # skip name index
    
    if version > MINIMUM_VERSION:
        skip_bytes(file, 4)
    
    read_compact_index(file) # obj size field
    inner_size = read_compact_index(file)
    
    # Copy the inner contents to a new file
    with open(destination, "wb") as inner_file:
        inner_file.write(file.read(inner_size))
    
    return UMXInfo(hint, version, inner_size)


def is_umx(file: IO) -> bool:
    magic = file.read(4)
    return magic == MAGIC_UPKG


def read_table_above_64(file: IO) -> str:
    length = read_byte(file)
    buffer = file.read(length)

    return str(buffer.strip(NULL), encoding="ascii", errors="ignore")


def read_table_below_64(file: IO) -> str:
    buffer = bytearray()

    while not buffer.endswith(NULL):
        buffer.append(read_byte(file))

    return str(buffer.strip(NULL), encoding="ascii", errors="ignore")


def read_name_table_func(version: int) -> Callable[[IO], str]:
    if version < 64:
        return read_table_below_64
    else:
        return read_table_above_64


# https://wiki.beyondunreal.com/Legacy:Package_File_Format/Data_Details
def read_compact_index(file: IO) -> int:
    output = 0
    signed = False

    for i in range(5):
        x = read_byte(file)

        if i == 0:
            if (x & 0x80) > 0:
                signed = True

            output |= x & 0x3F

            if x & 0x40 == 0:
                break

        elif i == 4:
            output |= (x & 0x1F) << (6 + (3 * 7))

        else:
            output |= (x & 0x7F) << (6 + ((i - 1) * 7))

            if x & 0x80 == 0:
                break

    if signed:
        output *= -1

    return output


def read_byte(file: IO) -> int:
    return file.read(1)[0]


def read_dword_le(file: IO) -> int:
    return int.from_bytes(file.read(4), byteorder="little")


def skip_bytes(file: IO, bytes: int):
    file.seek(bytes, 1)
