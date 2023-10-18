# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import varint
from io import BytesIO

# ---------------------- decode

def parse_flevent(datastream):
    event_id = int.from_bytes(datastream.read(1), "little")
    if event_id <= 63 and event_id >= 0: # int8
        event_data = int.from_bytes(datastream.read(1), "little")
    if event_id <= 127 and event_id >= 64 : # int16
        event_data = int.from_bytes(datastream.read(2), "little")
    if event_id <= 191 and event_id >= 128 : # int32
        event_data = int.from_bytes(datastream.read(4), "little")
    if event_id <= 224 and event_id >= 192 : # text
        eventpartdatasize = varint.decode_stream(datastream)
        event_data = datastream.read(eventpartdatasize)
    if event_id <= 255 and event_id >= 225 : # data
        eventpartdatasize = varint.decode_stream(datastream)
        event_data = datastream.read(eventpartdatasize)
    return [event_id, event_data]

def decode(mainevents):
    eventdatasize = len(mainevents)
    eventdatastream = BytesIO()
    eventdatastream.write(mainevents)
    eventdatastream.seek(0)
    eventtable = []
    while eventdatastream.tell() < int(eventdatasize):
        event_data = parse_flevent(eventdatastream)
        eventtable.append(event_data)
    return eventtable

# ---------------------- encode

def make_flevent(FLdt_bytes, value, data):
    if value <= 63 and value >= 0: # int8
        FLdt_bytes.write(value.to_bytes(1, "little"))
        FLdt_bytes.write(data.to_bytes(1, "little"))
    if value <= 127 and value >= 64 : # int16
        FLdt_bytes.write(value.to_bytes(1, "little"))
        FLdt_bytes.write(data.to_bytes(2, "little"))
    if value <= 191 and value >= 128 : # int32
        FLdt_bytes.write(value.to_bytes(1, "little"))
        FLdt_bytes.write(data.to_bytes(4, "little"))
    if value <= 224 and value >= 192 : # text
        FLdt_bytes.write(value.to_bytes(1, "little"))
        FLdt_bytes.write(varint.encode(len(data)))
        FLdt_bytes.write(data)
    if value <= 255 and value >= 225 : # data
        FLdt_bytes.write(value.to_bytes(1, "little"))
        FLdt_bytes.write(varint.encode(len(data)))
        FLdt_bytes.write(data)

def encode(eventtable):
    eventdatastream = BytesIO()
    for event_data in eventtable:
        make_flevent(eventdatastream, event_data[0], event_data[1])
    eventdatastream.seek(0)
    return eventdatastream.read()
