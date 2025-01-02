# code from https://github.com/asb2m10/dexed/discussions/402
encodingTable = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"

def _setBitRange(size, data, bitRangeStart, numBits, bitsToSet):
    bite = bitRangeStart >> 3
    offsetInByte = int(bitRangeStart & 7)
    mask = ~(((0xffffffff) << (32 - numBits)) >> (32 - numBits))
    while numBits > 0 and bite < size:
        bitsThisTime = min(numBits, 8 - offsetInByte)
        tempMask = (mask << offsetInByte) | ~(((0xffffffff) >> offsetInByte) << offsetInByte)
        tempBits = bitsToSet << offsetInByte
        data[bite] = (data[bite] & tempMask) | tempBits
        bite += 1
        numBits -= bitsThisTime
        bitsToSet >>= bitsThisTime
        mask >>= bitsThisTime
        offsetInByte = 0

def fromJuceBase64Encoding(s):
    size = int(s[:s.index(".")])
    b64str = s[s.index(".") + 1:]
    pos = 0
    data = [0] * size
    for i in range(len(b64str)):
        c = b64str[i]
        for j in range(64):
            if encodingTable[j] == c:
                _setBitRange(size, data, pos, 6, j)
                pos += 6
                break
    return bytes(i & 0xff for i in data)

def _getBitRange(size, data, bitRangeStart, numBits):
    res = 0
    byte = bitRangeStart >> 3
    offsetInByte = bitRangeStart & 7
    bitsSoFar = 0
    while numBits > 0 and byte < size:
        bitsThisTime = min(numBits, 8 - offsetInByte)
        mask = (0xff >> (8 - bitsThisTime)) << offsetInByte
        res |= (((data[byte] & mask) >> offsetInByte) << bitsSoFar)
        bitsSoFar += bitsThisTime
        numBits -= bitsThisTime
        byte += 1
        offsetInByte = 0
    return res

def toJuceBase64Encoding(bytes):
    if not bytes: return None
    numChars = ((len(bytes) << 3) + 5) // 6
    s = str(len(bytes)) + '.'
    for i in range(numChars): s += encodingTable[_getBitRange(len(bytes), bytes, i * 6, 6)]
    return s
