# Copyright 2019 cj-wong
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

import pendulum
import yaml


LOGGER = logging.getLogger('calendar-to-sheets')
LOGGER.setLevel(logging.DEBUG)

FH = logging.handlers.RotatingFileHandler(
    'calendar-to-sheets.log',
    maxBytes=4096,
    backupCount=5,
    )
FH.setLevel(logging.DEBUG)

CH = logging.StreamHandler()
CH.setLevel(logging.INFO)

FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
FH.setFormatter(FORMATTER)
CH.setFormatter(FORMATTER)

LOGGER.addHandler(FH)
LOGGER.addHandler(CH)

YESTERDAY = pendulum.yesterday()
TODAY = pendulum.today()

with open('config.yaml', 'r') as f:
    CONF = yaml.safe_load(f)


SPREADSHEET_ID = CONF['spreadsheet']['id']
TABS = CONF['spreadsheet']['tabs']
# TAB_NAMES consists of tabs (keys) and their aliases (values)
TAB_NAMES = {}
# CALS consists of calendars that have tabs belonging in TAB_NAMES
CALS = []

for calendar, cal_vals in CONF['calendars'].items():
    tabs = cal_vals['tabs']
    for tab in tabs:
        if tab in TABS:
            if tab not in TAB_NAMES:
                TAB_NAMES[tab] = TABS[tab]['aliases']
            if calendar not in CALS:
                CALS.append(calendar)

# Both CALS and TAB_NAMES must not be empty.
if not CALS and not TAB_NAMES:
    raise InvalidConfiguration


class InvalidConfiguration(ValueError):
    """An invalid configuration was detected, stemming from
    no calendars with corresponding tabs in TAB_NAMES.

    """
    def __init__(self) -> None:
        super().__init__(
            'Your configuration was invalid. Most likely you did not put '
            'tabs into your calendars.\nTabs must be present in both the '
            'calendar ("tabs") and spreadsheet settings ("tabs").'
            )
