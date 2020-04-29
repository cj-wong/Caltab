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
import re
from typing import Dict, Union

import pendulum
from googleapiclient.discovery import build

import config

# Replaced imports:
#   datetime -> pendulum

ALPHA = re.compile(r'[a-z]+', re.IGNORECASE)
ORD_Z = ord('Z')


def get_yesterday_cell(start: Dict[str, Union[str, int]]) -> str:
    """Retrieve the cell representing yesterday, given the starting
    cell and its characteristics. Note that if the cell isn't valid,
    `AttributeError` ,`TypeError`, or `ValueError` may be raised,
    from attempted string slicing (e.g. `cell[:col_end]`) and type-casts
    (e.g. `int(cell[col_end:])`).

    Args:
        start (Dict[str, Union[str, int]]): the characteristics of
            the starting (top-left) cell in the sheet; contains
            'cell' (spreadsheet format), 'year', and 'month'

    Returns:
        str: the cell in spreadsheet format, e.g. 'A1'

    """
    cell = start['cell']
    first = pendulum.datetime(start['year'], start['month'], 1, tz='local')
    col_end = ALPHA.search(cell).end()
    col = cell[:col_end].upper()
    # We want to perform math on cols to get the right column.
    # To do so, we must convert the letters using `ord()`.
    ncol = ord(col)
    # Columns are 1-indexed, so subtract to get the true offset.
    ncol += config.YESTERDAY.day - 1
    if ncol <= ORD_Z:
        col = chr(ncol)
    else: # After Z in columns are AA, AB, etc.
        col = f'A{chr(ncol - 26)}'
    # `monthy` represents the row given year and month, with offsets
    # from `start`.
    monthy = int(cell[col_end:])
    monthy += (config.YESTERDAY - first).months

    return f'{col}{monthy}'


class Sheets:
    """Class for manging sheets.

    Attributes:
        interface (Resource): an interface created from credentials;
            used to retrieve spreadsheets and their sheets

    """
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

    def get_tab_cells(self) -> Dict[str, str]:
        """For all valid tabs, get the cell representing yesterday so
        the hours can be recorded there.

        Returns:
            Dict[str, str]: {tab name: syntax for yesterday's cell}

        """
        tab_cells = {}
        for tab, conf in config.TABS.items():
            start = conf['start']
            cell = start['cell']

            try:
                yesterday = get_yesterday_cell(start)
            except (AttributeError, TypeError, ValueError) as e:
                config.LOGGER.error(f'Skipping {tab}: {e}')
                continue

            tab_cells[tab] = f'{tab}!{yesterday}'

        return tab_cells

    def input_hours(self, tab_hours: Dict[str, int]) -> None:
        """Inputs hours given `tab_hours` into their respective sheets.

        Args:
            tab_hours (Dict[str, int]): {tab name: hours}

        """

        values = self.interface.values()

        tab_cells = self.get_tab_cells()

        for tab, hour in tab_hours.items():
            update = values.update(
                spreadsheetId=config.SPREADSHEET_ID,
                range=tab_cells[tab],
                valueInputOption='USER_ENTERED',
                body={'values': [[hour]]},
                ).execute()
            config.LOGGER.info(
                f"Cells in sheet {tab} updated: {update['updatedCells']}"
                )
