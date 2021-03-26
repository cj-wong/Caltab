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
import re
from typing import Dict

import pendulum
from googleapiclient.discovery import build

import config

# Replaced imports:
#   datetime -> pendulum

ALPHA = re.compile(r'[a-z]+', re.IGNORECASE)
ORD_Z = ord('Z')


def get_yesterday_cell(cell: str, start: Dict[str, int]) -> str:
    """Retrieve the cell location representing yesterday.

    The cell location can be determined given the starting cell location and
    year and month offsets. Note that if the cell isn't valid, AttributeError
    or TypeError may be raised, albeit indirectly.

    Args:
        cell (str): starting cell of spreadsheet in spreadsheet format
        start (Dict[str, int]): month and year of the starting cell

    Returns:
        str: the cell in spreadsheet format, e.g. 'A1'

    Raises:
        AttributeError: if any intermediary values are None
        TypeError: slicing or casting on None

    """
    first = pendulum.datetime(start['year'], start['month'], 1, tz='local')
    search = ALPHA.search(cell)
    if not search:
        raise ValueError(f'RegEx could not match {cell}')
    col_end = search.end()
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
    # `row_year_month` represents the row given year and month, with offsets
    # from `start`.
    row_year_month = int(cell[col_end:])
    row_year_month += (config.YESTERDAY - first).months

    return f'{col}{row_year_month}'


class Sheets:
    """Class for Google Sheets.

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
        """Get the cell representing yesterday to be written with hours.

        If the cell is invalid, nothing will be written.

        Returns:
            Dict[str, str]: {tab name: syntax for yesterday's cell}

        """
        tab_cells = {}
        for tab, conf in config.TABS.items():
            start = conf['start']
            cell = start['cell']

            try:
                yesterday = get_yesterday_cell(cell, start)
            except (AttributeError, TypeError, ValueError) as e:
                config.LOGGER.error(f'Skipping {tab}: {e}')
                continue

            tab_cells[tab] = f'{tab}!{yesterday}'

        return tab_cells

    def input_hours(self, tab_hours: Dict[str, int]) -> None:
        """Input hours into their respective sheets.

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
