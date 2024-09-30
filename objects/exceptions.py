# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
logger_projparse = logging.getLogger('projparse')

class ProjectFileParserException(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger_projparse.error(message)

class OutputPluginException(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger_projparse.error(message)