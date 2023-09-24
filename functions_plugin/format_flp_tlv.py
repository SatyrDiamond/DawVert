# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import varint
from io import BytesIO

def parse_flevent(datastream):
    event_id = int.from_bytes(datastream.read(1), "little")
    if event_id <= 63 and event_id >= 0: # int8
        event_data = int.from_bytes(eventdatastream.read(1), "little")
    if event_id <= 127 and event_id >= 64 : # int16
        event_data = int.from_bytes(eventdatastream.read(2), "little")
    if event_id <= 191 and event_id >= 128 : # int32
        event_data = int.from_bytes(eventdatastream.read(4), "little")
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
        event_id = int.from_bytes(eventdatastream.read(1), "little")
        if event_id <= 63 and event_id >= 0: # int8
            event_data = int.from_bytes(eventdatastream.read(1), "little")
        if event_id <= 127 and event_id >= 64 : # int16
            event_data = int.from_bytes(eventdatastream.read(2), "little")
        if event_id <= 191 and event_id >= 128 : # int32
            event_data = int.from_bytes(eventdatastream.read(4), "little")
        if event_id <= 224 and event_id >= 192 : # text
            eventpartdatasize = varint.decode_stream(eventdatastream)
            event_data = eventdatastream.read(eventpartdatasize)
        if event_id <= 255 and event_id >= 225 : # data
            eventpartdatasize = varint.decode_stream(eventdatastream)
            event_data = eventdatastream.read(eventpartdatasize)
        eventtable.append([event_id, event_data])
    return eventtable