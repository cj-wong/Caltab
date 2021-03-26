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
from collections import defaultdict
from typing import Dict, Union

import pendulum
from google.oauth2 import service_account
from googleapiclient.discovery import build

import config

# Replaced imports:
#   datetime -> pendulum


def get_tab(entry: str) -> Union[str, None]:
    """Get a tab given its name, if it exists in `config.TAB_NAMES`.

    Args:
        entry (str): the name of an entry
        entry_names (dict): {tab: [aliases]}

    Returns:
        str: if `entry` matched a tab in `config.TAB_NAMES`

    Raises:
        TabNotFound: if `entry` did not match

    """
    for name, aliases in config.TAB_NAMES.items():
        if entry == name or entry in aliases:
            return name

    raise TabNotFound


class TabNotFound(ValueError):
    """The tab name wasn't found in the configuration. Ignore it."""

    pass


class Calendar:
    """Class for managing Google Calendar.

    Attributes:
        interface (Resource): an interface created from credentials;
            used to retrieve calendars and entries per calendar

    """

    def __init__(self, credentials: service_account.Credentials) -> None:
        """Initialize the Google Calendar interface.

        Args:
            credentials (service_account.Credentials): creds for Google APIs

        """
        self.interface = build(
            'calendar',
            'v3',
            credentials=credentials
            )

    def get_calendar_ids(self) -> Dict[str, str]:
        """Get IDs for calendars configured in config.yaml.

        The IDs will be used for retrieving entries/events per calendar.

        Returns:
            Dict[str, str]: {calendar name: calendar id}

        """
        cals = {}

        all_cals = self.interface.calendarList().list().execute()['items']

        for cal in all_cals:
            calendar = cal['summary']
            if calendar in config.CALS:
                cals[calendar] = cal['id']

        return cals

    def get_entries(self, cal_name: str, cal_id: str) -> Dict[str, int]:
        """Get entries in a calendar given `cal_id` from yesterday until today.

        We are interested in events that have elapsed from then and now.

        Args:
            cal_name (str): the name (summary) of the calendar
            cal_id (str): the ID of the calendar

        Returns:
            dict: {tab: hours}

        """
        tab_hours = defaultdict(int)

        all_entries = self.interface.events().list(
            calendarId=cal_id,
            timeMin=config.YESTERDAY,
            timeMax=config.TODAY,
            singleEvents=True,
            orderBy='startTime',
            ).execute()['items']

        for entry in all_entries:
            try:
                tab = get_tab(entry['summary'])
            except TabNotFound:
                continue
            start = pendulum.parse(entry['start']['dateTime'])
            end = pendulum.parse(entry['end']['dateTime'])
            tab_hours[tab] += (end - start).seconds/3600
            if tab_hours[tab] >= 24:
                config.LOGGER.warning(f'Hours exceeded 24 for tab {tab}')

        return tab_hours
