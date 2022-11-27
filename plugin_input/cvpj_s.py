# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import json

class input_cvpj(plugin_input.base):
    def __init__(self):
        pass

    def getname(self):
        return 'ConvProj'

    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(8)
        if bytesdata == b'CONVPROJ':
            return True
        else:
            return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        with open(input_file) as f:
            inputT = "\n".join(f.readlines()[1:])
            inputJ = json.loads(inputT)
        return json.dumps(inputJ)

