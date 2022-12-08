from functions import data_bytes
import plugin_input
import json

class input_cvpj_r(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'cvpj_r'
    def getname(self): return 'cvpj_r'
    def gettype(self): return 'r'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(12)
        if bytesdata == b'CONVPROJ___R': return True
        else: return False
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        file_data = bytestream.read()
        data = ''.join(file_data.split('\n')[1:])
        return data

