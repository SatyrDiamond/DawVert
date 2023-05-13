# SPDX-FileCopyrightText: 2023 B0ney
# SPDX-License-Identifier: MIT or APACHE-2.0

from typing import IO, Callable, Optional
from dataclasses import dataclass

FORMATS = ["it", "xm", "s3m", "mod"]
MAGIC_UPKG = bytes([0xc1, 0x83, 0x2a, 0x9e])
MINIMUM_VERSION = 61
NULL = bytes([0])


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

# Some tests
# if __name__ == "__main__":
#     print(strip_umx("test/umx/Mayhem.umx", "test/mayhem"))
#     print(strip_umx("test/umx/DeathValley.umx", "test/deathvalley"))
#     print(strip_umx("test/umx/deus ex/MJ12_Music.umx", "test/mj12"))
#     print(strip_umx("test/umx/deus ex/Lebedev_Music.umx", "test/lebedev"))