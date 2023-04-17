# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import notelist_data

def nl2pl(cvpj_notelist):
    return [{'position': 0, 'duration': notelist_data.getduration(cvpj_notelist), 'notelist': cvpj_notelist}]
