# Copyright 2019-2020 cj-wong
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
from pathlib import Path
from typing import Dict, Tuple, Union

import google.api_handler
import google.calendar
import google.sheets
from config import CONF, LOGGER


def main() -> None:
    """This function runs everything: authorizes the connection,
    reads calendars, and writes to spreadsheet if records were found.

    """

    creds = google.api_handler.authorize()
    sheets = google.sheets.Sheets(creds)
    calendar = google.calendar.Calendar(creds)
    sheet_ids = sheets.get_ids(CONF['tabs'].keys())
    cals = calendar.get_calendars()
    if not cals:
        LOGGER.error(
            'No calendars were found matching any in your configuration'
            )
    for cal_name, cal_id in cals.items():
        tab_hours = calendar.get_entries(cal_id, cal_name)
        if tab_hours:
            sheets.input_hours(tab_hours)
        else:
            LOGGER.info('No tab-hours were found for yesterday')


if __name__ == '__main__':
    main()
