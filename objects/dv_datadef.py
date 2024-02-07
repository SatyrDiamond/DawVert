# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from io import BytesIO
import struct
import varint
import json

def string_fix(inputtxt):
    return inputtxt.split(b'\x00')[0].decode().translate(dict.fromkeys(range(32)))

class datadef:
    def __init__(self, filepath):
        self.structs = {}
        self.cases = {}
        self.metadata = {}
        self.using_structs = []
        self.errored = False
        self.errormeg = ''
        self.debugoutput = []
        self.leftoverbytes = b''
        self.bytestream = BytesIO()
        if filepath: self.load_file(filepath)

# ####################################################################################################
# ####################################################################################################
# --- decode
# ####################################################################################################
# ####################################################################################################

    def parse(self, dataname, databytes):
        self.debugoutput = []
        self.using_structs = []
        self.output = {}
        self.vars = {}
        self.errored = False
        self.emsg_partnum = ''
        self.emsg_structname = ''
        self.bytestream = BytesIO(databytes)
        try:
            if dataname in self.structs:
                self.output = self.decode_struct(dataname)
                self.leftoverbytes = self.bytestream.read(64)
        except Exception as e:
            self.errored = True
            self.errormeg = str(e)+' at line '+self.emsg_partnum+' on '+self.emsg_structname+':'

        return self.output

    def getnum(self, partdata, partnum, structname):
        if len(partdata) > 1:
            numpart, outpartdata = self.decode_part(partdata[1:], partnum, 'N '+structname)
            if isinstance(numpart, int): return numpart, outpartdata
            else: raise Exception('out is not int')
        else: raise Exception('not enough valtypes')

    def decode_part(self, partdata, partnum, structname):

        self.emsg_partnum = str(partnum+1)
        self.emsg_structname = structname

        if partdata:
            if self.bytestream.tell() < len(self.bytestream.getvalue()):
                outval = [1, None]
                outpartdata = partdata.copy()

                if partdata[0][0] in ['raw', 'string', 'dstring', 'list', 'skip_n']: 
                    outval[0] = 2
                    if outval[0] == 2 and not partdata[0][1].isnumeric(): raise Exception('subvaltype is not numeric')
                    else: subvalnum = int(partdata[0][1])

                if self.errored == False:

                    if partdata[0][0] == 'skip':             self.bytestream.read(1)
                    elif partdata[0][0] == 'skip_n':         self.bytestream.read(subvalnum)
                    elif partdata[0][0] == 'struct':         outval[1] = self.decode_struct(partdata[0][1])
                    elif partdata[0][0] == 'getvar':
                        if partdata[0][1] in self.vars:      outval[1] = self.vars[partdata[0][1]]
                        else: raise Exception('var "'+partdata[0][1]+'" not found')

                    elif partdata[0][0] == 'byte':           outval[1] = struct.unpack('B', self.bytestream.read(1))[0]
                    elif partdata[0][0] == 's_byte':         outval[1] = struct.unpack('b', self.bytestream.read(1))[0]

                    elif partdata[0][0] == 'short':          outval[1] = struct.unpack('H', self.bytestream.read(2))[0]
                    elif partdata[0][0] == 'short_b':        outval[1] = struct.unpack('>H', self.bytestream.read(2))[0]
                    elif partdata[0][0] == 's_short':        outval[1] = struct.unpack('h', self.bytestream.read(2))[0]
                    elif partdata[0][0] == 's_short_b':      outval[1] = struct.unpack('>h', self.bytestream.read(2))[0]

                    elif partdata[0][0] == 'int':            outval[1] = struct.unpack('I', self.bytestream.read(4))[0]
                    elif partdata[0][0] == 'int_b':          outval[1] = struct.unpack('>I', self.bytestream.read(4))[0]
                    elif partdata[0][0] == 's_int':          outval[1] = struct.unpack('i', self.bytestream.read(4))[0]
                    elif partdata[0][0] == 's_int_b':        outval[1] = struct.unpack('>i', self.bytestream.read(4))[0]

                    elif partdata[0][0] == 'float':          outval[1] = struct.unpack('f', self.bytestream.read(4))[0]
                    elif partdata[0][0] == 'float_b':        outval[1] = struct.unpack('>f', self.bytestream.read(4))[0]
                    elif partdata[0][0] == 'double':         outval[1] = struct.unpack('d', self.bytestream.read(8))[0]
                    elif partdata[0][0] == 'double_b':       outval[1] = struct.unpack('>d', self.bytestream.read(8))[0]

                    elif partdata[0][0] == 'varint':         outval[1] = varint.decode_stream(self.bytestream)
                    #elif partdata[0][0] == 'varint_4':       outval[1] = varint.decode_bytes(self.bytestream.read(4))

                    elif partdata[0][0] == 'raw':            outval[1] = self.bytestream.read(subvalnum)
                    elif partdata[0][0] == 'raw_part':
                        intval, outpartdata = self.getnum(outpartdata, partnum, structname)
                        outval[1] = self.bytestream.read(intval)

                    elif partdata[0][0] == 'string':         outval[1] = self.bytestream.read(subvalnum).split(b'\x00')[0].decode()
                    elif partdata[0][0] == 'string_part':
                        intval, outpartdata = self.getnum(outpartdata, partnum, structname)
                        outval[1] = self.bytestream.read(intval).split(b'\x00')[0].decode()

                    elif partdata[0][0] == 'dstring':        outval[1] = self.bytestream.read(subvalnum*2).decode()
                    elif partdata[0][0] == 'dstring_part':
                        intval, outpartdata = self.getnum(outpartdata, partnum, structname)
                        outval[1] = self.bytestream.read(intval*2).decode()

                    elif partdata[0][0] == 'string_t':       outval[1] = data_bytes.readstring(self.bytestream)

                    elif partdata[0][0] == 'list':
                        listdata = []
                        for _ in range(subvalnum):
                            pvalue, _ = self.decode_part(outpartdata[1:], partnum, 'L '+structname)
                            listdata.append(pvalue)
                        outpartdata = outpartdata[1:]
                        outval[1] = listdata

                    elif partdata[0][0] == 'list_part':
                        intval, outpartdata = self.getnum(outpartdata, partnum, structname)
                        listdata = []
                        for _ in range(intval):
                            pvalue, _ = self.decode_part(outpartdata[1:], partnum, 'L '+structname)
                            listdata.append(pvalue)
                        outpartdata = outpartdata[1:]
                        outval[1] = listdata

                    else: outval = [0, None]

                    bytepos = self.bytestream.tell()

                    if outval == [0, None]: 
                        raise Exception('unknown valtype')
                    else:
                        self.debugoutput.append([str(bytepos), self.emsg_structname, self.emsg_partname, partdata[0][0], str(outval[1])])
                        return outval[1], outpartdata
            else: raise Exception('end of stream')
        else: raise Exception('no valtypes found')


    def decode_struct(self, structname):
        dictval = {}
        self.emsg_partname = ''
        if structname not in self.using_structs: 
            if structname in self.structs:
                self.using_structs.append(structname)

                structdata = self.structs[structname]
                for strnum in range(len(structdata)):
                    strpart = structdata[strnum]

                    pa_type, pa_dv, pa_name = strpart

                    self.emsg_partname = pa_name

                    if pa_type in ['part', 'setvar']: 
                        pvalue, outpartdata = self.decode_part(pa_dv, strnum, structname)
                        if pa_name != '' and pvalue != None:
                            if pa_type == 'part': dictval[pa_name] = pvalue
                            if pa_type == 'setvar': self.vars[pa_name] = pvalue
                    else: raise Exception('unknown type on '+str(strnum+1)+' at '+structname)
                self.using_structs.remove(structname)
            else: raise Exception('struct not found: '+structname)
        else: raise Exception('recursion detected: '+structname)

        return dictval

# ####################################################################################################
# ####################################################################################################
# --- encode
# ####################################################################################################
# ####################################################################################################

    def create(self, structname, dictdata):
        self.debugoutput = []
        self.using_structs = []
        self.output = dictdata
        self.vars = {}
        self.errored = False
        self.bytestream = BytesIO()
        try:
            if structname in self.structs: 
                self.output = self.encode_struct(structname, dictdata)
        except Exception as e:
            self.errored = True
            self.errormeg = str(e)

    def encode_numdata(self, valtype, outval):
        if valtype == 'byte': outbytes = struct.pack('B', outval)
        elif valtype == 's_byte': outbytes = struct.pack('b', outval)

        elif valtype == 'short': outbytes = struct.pack('H', outval)
        elif valtype == 'short_b': outbytes = struct.pack('>H', outval)
        elif valtype == 's_short': outbytes = struct.pack('h', outval)
        elif valtype == 's_short_b': outbytes = struct.pack('>h', outval)

        elif valtype == 'int': outbytes = struct.pack('I', outval)
        elif valtype == 'int_b': outbytes = struct.pack('>I', outval)
        elif valtype == 's_int': outbytes = struct.pack('i', outval)
        elif valtype == 's_int_b': outbytes = struct.pack('>i', outval)

        elif valtype == 'float': outbytes = struct.pack('f', outval)
        elif valtype == 'float_b': outbytes = struct.pack('>f', outval)
        elif valtype == 'double': outbytes = struct.pack('d', outval)
        elif valtype == 'double_b': outbytes = struct.pack('>d', outval)

        elif valtype == 'varint': outbytes = varint.encode(outval)

        else: raise Exception('unsupported number-related valtype')

        return outbytes

    def getfallback(self, valtype, subvalnum):
        if valtype == 'raw': return b'\x00'*subvalnum
        elif valtype == 'raw_part': return b''
        elif valtype == 'string': return ''
        elif valtype == 'string_part': return ''
        elif valtype == 'list': return []
        elif valtype == 'struct': return {}
        else: return 0

    def getval(self, v_tag, v_name, v_type, v_value, subvalnum):
        return v_value if v_value != None else self.getfallback(partdata[0][0], subvalnum)

    def encode_part(self, partdata, outval, structname):
        subvalnum = None
        if partdata:
            outpartdata = partdata.copy()
            if partdata[0][0] in ['raw', 'string', 'dstring', 'list', 'skip_n']: 
                if not partdata[0][1].isnumeric(): raise Exception('subvaltype is not numeric')
                else: subvalnum = int(partdata[0][1])
            
            if outval == None: outval = self.getfallback(partdata[0][0], subvalnum)

            if partdata[0][0] == 'skip': outbytes = b'\x00'
            elif partdata[0][0] == 'skip_n': outbytes = b'\x00'*subvalnum

            elif partdata[0][0] in ['int', 'int_b', 's_int', 's_int_b', 'byte', 's_byte', 'short', 'short_b', 's_short', 's_short_b', 'float', 'float_b', 'double', 'double_b', 'varint']: 
                outbytes = self.encode_numdata(partdata[0][0], outval)
            
            elif partdata[0][0] == 'raw': 
                if len(outval) != subvalnum: raise Exception('raw length not match')
                outbytes = outval

            elif partdata[0][0] == 'string': 
                outbytes = data_bytes.makestring_fixedlen(outval, subvalnum)

            elif partdata[0][0] == 'raw_part': 
                datalen = self.encode_numdata(partdata[1][0], len(outval))
                outbytes = outval
                outpartdata = outpartdata[1:]

            elif partdata[0][0] == 'string_part': 
                stringbytes = outval.encode()
                datalen = self.encode_numdata(partdata[1][0], len(stringbytes))
                outbytes = stringbytes
                outpartdata = outpartdata[1:]

            elif partdata[0][0] == 'list': 
                if len(outval) != subvalnum: raise Exception('list length not match')
                outbytes = b''
                outpartdata = outpartdata[1:]
                for listnum in range(subvalnum): self.encode_part(outpartdata, outval[listnum], structname)

            elif partdata[0][0] == 'list_part': 
                outbytes = b''
                outpartdata = outpartdata[1:]
                self.encode_part(outpartdata, len(outval), structname)
                outpartdata = outpartdata[1:]
                for liste in outval: self.encode_part(outpartdata, liste, structname)

            elif partdata[0][0] == 'struct': 
                outbytes = b''
                self.encode_struct(outpartdata[0][1], outval)
                self.emsg_structname = outpartdata[0][1]



            else: raise Exception('unsupported valtype: '+partdata[0][0])

            self.bytestream.write(outbytes)

            return outpartdata[1:]

    def encode_struct(self, structname, dictdata):
        self.emsg_structname = structname
        if structname not in self.using_structs: 
            if structname in self.structs:
                self.using_structs.append(structname)
                structdata = self.structs[structname]
                for strnum in range(len(structdata)):
                    strpart = structdata[strnum]
                    pa_type, pa_dv, pa_name = strpart

                    dictval = dictdata[pa_name] if pa_name in dictdata else None
                    if pa_type in ['part']: 
                        self.emsg_partnum = str(strnum+1)
                        self.encode_part(pa_dv, dictval, structname)
                    else: raise Exception('unsupported type on '+str(strnum+1)+' at '+structname)
                self.using_structs.remove(structname)
            else: raise Exception('struct not found: '+structname)
        else: raise Exception('recursion detected: '+structname)

# ####################################################################################################
# ####################################################################################################
# --- file
# ####################################################################################################
# ####################################################################################################

    def load_file(self, in_datadef):
        self.structs = {}
        self.metadata = {}
        self.cases = {}

        try:
            if in_datadef != None:
                f = open(in_datadef, "r")
                print('[datadef] Loaded '+in_datadef)
                ddlines = [x.strip().split('#')[0].split('|') for x in f.readlines()]
                ddlines = [[p.strip() for p in l] for l in ddlines]

                current_struct = None
                for ddline in ddlines:
                    if ddline != ['']:
                        if ddline[0] == 'meta':
                            self.metadata[ddline[1]] = ddline[2]
                        if ddline[0] == 'area_struct':
                            current_struct = ddline[1]
                            self.structs[ddline[1]] = []
                        if ddline[0] == 'part':
                            valtypes = ddline[1].split('/')
                            valtypes = [x.split('.') for x in valtypes]
                            valtypes = [x if len(x) > 1 else [x[0], ''] for x in valtypes]
                            self.structs[current_struct].append([ddline[0], valtypes, ddline[2]])
        except:
            pass

    def save_file(self, file_name):
        linesdata = []

        for key, value in self.metadata.items():
            linesdata.append('meta|'+key+'|'+value)

        for structname in self.structs:
            linesdata.append('')
            linesdata.append('area_struct|'+structname)
            for structpart in self.structs[structname]:
                subvals = structpart[1]
                subvals = [x[0] if x[1] == '' else x[0]+'.'+x[1] for x in subvals]
                subvals = '/'.join(subvals).replace(' ','')
                linesdata.append(structpart[0]+'|'+subvals+'|'+structpart[2])

        with open(file_name, "w") as fileout:
            for line in linesdata:
                fileout.write(line+'\n')
