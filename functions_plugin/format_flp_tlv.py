# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import varint
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter

# ---------------------- decode

def read_tlv(tlv_data):
	event_id = tlv_data.uint8()
	if event_id <= 63 and event_id >= 0: return event_id, tlv_data.uint8()
	if event_id <= 127 and event_id >= 64: return event_id, tlv_data.uint16()
	if event_id <= 191 and event_id >= 128: return event_id, tlv_data.uint32()
	if event_id <= 224 and event_id >= 192: return event_id, tlv_data.raw(tlv_data.varint())
	if event_id <= 255 and event_id >= 225: return event_id, tlv_data.raw(tlv_data.varint())

def decode(song_data, endpos):
	eventtable = []
	while song_data.tell() < endpos:
		event_id, event_data = read_tlv(song_data)
		eventtable.append([event_id, event_data])
	return eventtable

# ---------------------- encode

def write_tlv(tlv_data, value, data):
	tlv_data.uint8(value)
	if value <= 63 and value >= 0: tlv_data.uint8(data)
	if value <= 127 and value >= 64: tlv_data.uint16(data)
	if value <= 191 and value >= 128: tlv_data.uint32(data)
	if value <= 224 and value >= 192:
		tlv_data.varint(len(data))
		tlv_data.raw(data)
	if value <= 255 and value >= 225:
		tlv_data.varint(len(data))
		tlv_data.raw(data)

def encode(eventtable):
	tlv_data = bytewriter.bytewriter()
	for event_data in eventtable: write_tlv(tlv_data, event_data[0], event_data[1])
	return tlv_data.getvalue()
