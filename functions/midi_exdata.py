
import struct
from functions import data_bytes

sysex_brand = {}
sysex_brand[int("01",16)] = "Sequential Circuits"
sysex_brand[int("02",16)] = "IDP"
sysex_brand[int("03",16)] = "Voyetra Turtle Beach, Inc."
sysex_brand[int("04",16)] = "Moog Music"
sysex_brand[int("05",16)] = "Passport Designs"
sysex_brand[int("06",16)] = "Lexicon Inc."
sysex_brand[int("07",16)] = "Kurzweil / Young Chang"
sysex_brand[int("08",16)] = "Fender"
sysex_brand[int("09",16)] = "MIDI9"
sysex_brand[int("0A",16)] = "AKG Acoustics"
sysex_brand[int("0B",16)] = "Voyce Music"
sysex_brand[int("0C",16)] = "WaveFrame (Timeline)"
sysex_brand[int("0D",16)] = "ADA Signal Processors, Inc."
sysex_brand[int("0E",16)] = "Garfield Electronics"
sysex_brand[int("0F",16)] = "Ensoniq"
sysex_brand[int("10",16)] = "Oberheim / Gibson Labs"
sysex_brand[int("11",16)] = "Apple"
sysex_brand[int("12",16)] = "Grey Matter Response"
sysex_brand[int("13",16)] = "Digidesign Inc."
sysex_brand[int("14",16)] = "Palmtree Instruments"
sysex_brand[int("15",16)] = "JLCooper Electronics"
sysex_brand[int("16",16)] = "Lowrey Organ Company"
sysex_brand[int("17",16)] = "Adams-Smith"
sysex_brand[int("18",16)] = "E-mu"
sysex_brand[int("19",16)] = "Harmony Systems"
sysex_brand[int("1A",16)] = "ART"
sysex_brand[int("1B",16)] = "Baldwin"
sysex_brand[int("1C",16)] = "Eventide"
sysex_brand[int("1D",16)] = "Inventronics"
sysex_brand[int("1E",16)] = "Key Concepts"
sysex_brand[int("1F",16)] = "Clarity"
sysex_brand[int("20",16)] = "Passac"
sysex_brand[int("21",16)] = "Proel Labs (SIEL)"
sysex_brand[int("22",16)] = "Synthaxe (UK)"
sysex_brand[int("23",16)] = "Stepp"
sysex_brand[int("24",16)] = "Hohner"
sysex_brand[int("25",16)] = "Twister"
sysex_brand[int("26",16)] = "Ketron s.r.l."
sysex_brand[int("27",16)] = "Jellinghaus MS"
sysex_brand[int("28",16)] = "Southworth Music Systems"
sysex_brand[int("29",16)] = "PPG (Germany)"
sysex_brand[int("2A",16)] = "JEN"
sysex_brand[int("2B",16)] = "Solid State Logic Organ Systems"
sysex_brand[int("2C",16)] = "Audio Veritrieb-P. Struven"
sysex_brand[int("2D",16)] = "Neve"
sysex_brand[int("2E",16)] = "Soundtracs Ltd."
sysex_brand[int("2F",16)] = "Elka"
sysex_brand[int("30",16)] = "Dynacord"
sysex_brand[int("31",16)] = "Viscount International Spa (Intercontinental Electronics)"
sysex_brand[int("32",16)] = "Drawmer"
sysex_brand[int("33",16)] = "Clavia Digital Instruments"
sysex_brand[int("34",16)] = "Audio Architecture"
sysex_brand[int("35",16)] = "Generalmusic Corp SpA"
sysex_brand[int("36",16)] = "Cheetah Marketing"
sysex_brand[int("37",16)] = "C.T.M."
sysex_brand[int("38",16)] = "Simmons UK"
sysex_brand[int("39",16)] = "Soundcraft Electronics"
sysex_brand[int("3A",16)] = "Steinberg Media Technologies GmbH"
sysex_brand[int("3B",16)] = "Wersi Gmbh"
sysex_brand[int("3C",16)] = "AVAB Niethammer AB"
sysex_brand[int("3D",16)] = "Digigram"
sysex_brand[int("3E",16)] = "Waldorf Electronics GmbH"
sysex_brand[int("3F",16)] = "Quasimidi"
sysex_brand[int("40",16)] = "Kawai Musical Instruments MFG. CO. Ltd"
sysex_brand[int("41",16)] = "Roland Corporation"
sysex_brand[int("42",16)] = "Korg Inc."
sysex_brand[int("43",16)] = "Yamaha Corporation"
sysex_brand[int("44",16)] = "Casio Computer Co. Ltd"
sysex_brand[int("46",16)] = "Kamiya Studio Co. Ltd"
sysex_brand[int("47",16)] = "Akai Electric Co. Ltd."
sysex_brand[int("48",16)] = "Victor Company of Japan, Ltd."
sysex_brand[int("4B",16)] = "Fujitsu Limited"
sysex_brand[int("4C",16)] = "Sony Corporation"
sysex_brand[int("4E",16)] = "Teac Corporation"
sysex_brand[int("50",16)] = "Matsushita Electric Industrial Co. , Ltd"
sysex_brand[int("51",16)] = "Fostex Corporation"
sysex_brand[int("52",16)] = "Zoom Corporation"
sysex_brand[int("54",16)] = "Matsushita Communication Industrial Co., Ltd."
sysex_brand[int("55",16)] = "Suzuki Musical Instruments MFG. Co., Ltd."
sysex_brand[int("56",16)] = "Fuji Sound Corporation Ltd."
sysex_brand[int("57",16)] = "Acoustic Technical Laboratory, Inc."
sysex_brand[int("59",16)] = "Faith, Inc."
sysex_brand[int("5A",16)] = "Internet Corporation"
sysex_brand[int("5C",16)] = "Seekers Co. Ltd."
sysex_brand[int("5F",16)] = "SD Card Association"

global sysexvals

sysexvals = {}


def decode_exdata(sysexdata, isseqspec):
    exdata = data_bytes.to_bytesio(struct.pack("B"*len(sysexdata),*sysexdata))

    manufac = [exdata.read(1)[0]]

    if manufac == [0]:
        for _ in range(2):
            manufac.append(exdata.read(1)[0])

    if len(manufac) == 1:
        if manufac[0] in sysex_brand: print('[midi-exdata] Brand: ', sysex_brand[manufac[0]])
        else: print('[midi-exdata] Brand: Unknown', manufac[0])

    if isseqspec == True:
        return manufac, exdata.read()


def parse_sysex(sysexdata):
    contents = data_bytes.to_bytesio(struct.pack("b"*len(sysexdata),*sysexdata))

    print('[debug] -------------- sysex', time)
    manufac = int.from_bytes(contents.read(1), "little")

    if manufac != 0:
        model = int.from_bytes(contents.read(1), "little")
        devid = int.from_bytes(contents.read(1), "little")
        cmd = int.from_bytes(contents.read(1), "little")
        code = contents.read()

        if manufac in sysex_brand: brandname = sysex_brand[manufac]+' ('+str(manufac)+')'
        else: brandname = 'unknonwn ('+str(hex(manufac))+')'

        print('[debug] Manu:',brandname, hex(manufac))
        print('[debug] Model:',model, hex(model))
        print('[debug] Dev:',devid, hex(devid))
        print('[debug] CMD:',cmd, hex(cmd))
        print('[debug] Data:',code.hex())

        if manufac == 65:
            # Device ----------------------------- SC-88/Pro -----------------------------
            if [model, devid] == [16, 66]:
                if 'sc88' not in sysexvals: sysexvals['sc88'] = {}
                if cmd == 18:
                    sc88data = {}
                    sc88data['address'] = code[0:3].hex()
                    sc88data['data'] = code[3]
                    print('test -------', code[0:3].hex(), code[3])
                    if time not in sysexvals['sc88']: sysexvals['sc88'][time] = []
                    sysexvals['sc88'][time].append(sc88data)

def get_sysexvals():
    return sysexvals
