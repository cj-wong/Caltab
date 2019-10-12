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
import re
from typing import Dict

import pendulum
from googleapiclient.discovery import build

from config import CONF, LOGGER


ALPHA = re.compile(r'[a-z]+', re.IGNORECASE)
NUM = re.compile(r'[0-9]+')


def col_to_day(col: str) -> int:
    """Converts a column `col` from a str to 1-indexed int (day).
    `col` will always be capitalized since `.upper` is called.

    Args:
        col (str): e.g. 'B' (1), 'C', (2) 'AA' (26)

    Returns:
        int: the day representation of the column

    """
    return ord(col) - 65


def day_to_col(day: int) -> str:
    """Converts a 1-based day back to str column format.

    Args:
        day (int): the day of the month to convert to column

    Returns:
        str: the column represented by the day

    """
    day += 65
    if day <= 90: # ord('Z')
        return chr(day)
    else:
        return f'A{chr(day-26)}'


class Sheets:
    """Class for manging sheets."""
    def __init__(self, credentials) -> None:
        """Initialize the Sheets interface.

        Args:
            credentials: the Google API credentials

        """
        self.interface = build(
            'sheets',
            'v4',
            credentials=credentials
            ).spreadsheets()

    def get_ids(self, tabs: list) -> Dict[str, str]:
        """Gets sheet IDs filtered by `entry_names`.

        Args:
            tabs (keys): tab names to filter for

        Returns:
            dict: {name: id}

        """
        sheet_ids = {}
        spreadsheet = self.interface.get(
            spreadsheetId = CONF['spreadsheet_id']
            ).execute()['sheets']
        for sheet in spreadsheet:
            properties = sheet['properties']
            if properties['title'] in tabs:
                sheet_ids[properties['title']] = properties['sheetId']

        return sheet_ids

    def input_hours(self, tab_hours: Dict[str, int]) -> None:
        """Inputs hours given `tab_hours` into their respective sheets.

        Args:
            tab_hours (dict): {tab: hours}

        """
        tab_starts = {}
        for tab, value in CONF['tabs'].items():
            cell = value['start']['cell']

            alpha = ALPHA.search(cell)
            col_int = col_to_day(cell[0:alpha.end()].upper())
            col_int += YESTERDAY.day - 1
            col = day_to_col(col_int)

            num = NUM.search(cell)
            try:
                row = int(cell[alpha.end():num.end()])
            except (TypeError, ValueError) as e:
                message = f'{e}, Skipping {tab}'
                print(message)
                LOGGER.error(message)
                continue
            start = pendulum.datetime(
                value['start']['year'],
                value['start']['month'],
                1,
                tz='local',
                )
            row += (YESTERDAY - start).months
            tab_starts[tab] = f'{tab}!{col}{row}'

        values = self.interface.values()

        for tab, hour in tab_hours.items():
            update = values.update(
                spreadsheetId=CONF['spreadsheet_id'],
                range=tab_starts[tab],
                valueInputOption='USER_ENTERED',
                body={'values': [[hour]]},
                ).execute()
            LOGGER.info(f'Cells in sheet {tab} updated: {len(update)}')
