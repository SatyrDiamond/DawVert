# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects_convproj import params

class cvpj_send:
    def __init__(self):
        self.sendautoid = {}
        self.params = params.cvpj_paramset()

class cvpj_sends:
    def __init__(self):
        self.data = {}

    def add(self, target, sendautoid, amount):
        send_obj = cvpj_send()
        send_obj.params.add('amount', amount, 'float')
        send_obj.sendautoid = sendautoid
        self.data[target] = send_obj
        return send_obj

    def iter(self):
        for target, send_obj in self.data.items():
            yield target, send_obj

    def check(self):
        return len(self.data) != 0

