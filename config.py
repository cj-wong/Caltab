# Copyright 2019-2021 cj-wong
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import logging.handlers
from typing import Dict, List

import pendulum
import yaml


class InvalidConfiguration(ValueError):
    """An invalid configuration was detected.

    The configuration error most likely stems from no calendars with
    corresponding tabs in TAB_NAMES.

    """

    def __init__(self) -> None:
        """Initialize the configuration error with a message."""
        super().__init__(
            'Your configuration was invalid. Most likely you did not put '
            'tabs into your calendars.\nTabs must be present in both the '
            'calendar ("tabs") and spreadsheet settings ("tabs").'
            )


_LOGGER_NAME = 'caltab'

LOGGER = logging.getLogger(_LOGGER_NAME)
LOGGER.setLevel(logging.DEBUG)

_FH = logging.handlers.RotatingFileHandler(
    f'{_LOGGER_NAME}.log',
    maxBytes=40960,
    backupCount=5,
    )
_FH.setLevel(logging.DEBUG)

_CH = logging.StreamHandler()
_CH.setLevel(logging.WARNING)

_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
_FH.setFormatter(_FORMATTER)
_CH.setFormatter(_FORMATTER)

YESTERDAY = pendulum.yesterday()
TODAY = pendulum.today()

with open('config.yaml', 'r') as f:
    CONF = yaml.safe_load(f)


SPREADSHEET_ID = CONF['spreadsheet']['id']
TABS = CONF['spreadsheet']['tabs']
# TAB_NAMES consists of tabs and their aliases (list of aliases)
TAB_NAMES: Dict[str, List[str]] = {}
# CALS consists of calendars that have tabs belonging in TAB_NAMES
CALS: List[str] = []

for calendar, cal_vals in CONF['calendars'].items():
    for tab in cal_vals['tabs']:
        if tab in TABS:
            if tab not in TAB_NAMES:
                TAB_NAMES[tab] = TABS[tab]['aliases']
            if calendar not in CALS:
                CALS.append(calendar)

# Both CALS and TAB_NAMES must not be empty.
if not CALS and not TAB_NAMES:
    raise InvalidConfiguration
