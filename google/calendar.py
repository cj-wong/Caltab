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
from collections import defaultdict
from typing import Dict, Union

import pendulum
from googleapiclient.discovery import build

from config import CONF, LOGGER, TODAY, YESTERDAY

# Replaced imports:
#   datetime -> pendulum


def get_tab(entry: str, entry_names: Dict[str, list]) -> Union[str, None]:
    """Gets a tab given an `entry` and `entry_names`
    to filter, if the entry matches.

    Args:
        entry (str): the name of an entry
        entry_names (dict): {tab: [aliases]}

    Returns:
        str: if a tab was matched
        None: if no tabs were matched

    """
    if entry in entry_names:
        return entry
    else:
        for name, aliases in entry_names.items():
            if entry in aliases:
                return name

    return None


class Calendar:
    """Class for managing calendar."""
    def __init__(self, credentials) -> None:
        """Initialize the Calendar interface.

        Args:
            credentials: the Google API credentials

        """
        self.interface = build(
            'calendar',
            'v3',
            credentials=credentials
            )

    def get_calendars(self) -> Dict[str, str]:
        """Gets calendars filtered by valid calendar names in config.yaml.

        Returns:
            dict: {summary: id}

        """
        cals = {}
        cal_names = [
            value['calendar']['name']
            for value
            in CONF['tabs'].values()
            ]

        all_cals = self.interface.calendarList().list().execute()['items']

        for cal in all_cals:
            if cal['summary'] in cal_names:
                cals[cal['summary']] = cal['id']

        return cals

    def get_entries(self, cal_id: str, cal_name: str) -> Dict[str, int]:
        """Gets entries in a calendar given `cal_id`
        from yesterday until today.

        Args:
            cal_id (str): the ID of the calendar
            cal_name (str): the name (summary) of the calendar

        Returns:
            dict: {tab: hours}

        """
        tab_hours = defaultdict(int)
        entry_names = {
            tab: value['calendar']['entry_aliases']
            for tab, value
            in CONF['tabs'].items()
            if value['calendar']['name'] == cal_name
            }

        all_entries = self.interface.events().list(
            calendarId=cal_id,
            timeMin=YESTERDAY,
            timeMax=TODAY,
            singleEvents=True,
            orderBy='startTime',
            ).execute()['items']

        for entry in all_entries:
            tab = get_tab(entry['summary'], entry_names)
            if tab is None:
                continue
            start = pendulum.parse(entry['start']['dateTime'])
            end = pendulum.parse(entry['end']['dateTime'])
            tab_hours[tab] += (end - start).seconds/3600
            if tab_hours[tab] >= 24:
                LOGGER.warning(f'Hours exceeded for tab {tab}')

        return tab_hours
