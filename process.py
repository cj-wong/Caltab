# Copyright 2019 cj-wong
# Copyright 2018 Google LLC
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
import pickle
import re
import sys
from collections import defaultdict
from pathlib import Path

import pendulum
import yaml

from googleapiclient.discovery import build
from google.oauth2 import service_account

# Replaced imports:
#   os.path -> pathlib.Path
#   datetime -> pendulum
# Removed imports:
#   from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    ]

logger = logging.getLogger('calendar-to-sheets')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('calendar-to-sheets.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

with Path('config.yaml').open() as f:
    conf = yaml.safe_load(f)

YESTERDAY = pendulum.yesterday()
TODAY = pendulum.today()

ALPHA = re.compile(r'[a-z]+', re.IGNORECASE)
NUM = re.compile(r'[0-9]+')


def authorize():
    """Adapted from Google's example:
    https://developers.google.com/calendar/quickstart/python

    See NOTICE for attribution.

    Returns:
        tuple: of googleapiclient.discovery.Resource objects
            (Calendar, Sheets)

    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # Changed from:
    #   if os.path.exists('token.pickle'):
    #       with open('token.pickle', 'rb') as token:
    p = Path('token.pickle')
    if p.exists():
        with p.open(mode = 'rb') as token:
            try:
                creds = pickle.load(token)
            except EOFError:
                logger.warning('token.pickle is likely empty')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Changed from:
            #   creds.refresh(Request())
            # Since this will be run as a cron job i.e. no UI,
            # log this condition and exit instead.
            logger.error('Credentials expired')
            sys.exit(1)
        else:
            # Changed from:
            #   flow = InstalledAppFlow.from_client_secrets_file(
            #       'credentials.json', SCOPES)
            #   creds = flow.run_local_server(port=0)
            creds = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes = SCOPES
                )
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Changed from:
    #   service = build('calendar', 'v3', credentials=creds)
    return (
        build(
            'calendar',
            'v3',
            credentials=creds
            ),
        build(
            'sheets',
            'v4',
            credentials=creds
            ),
        )


def get_calendars(calendar):
    """Gets calendars filtered by valid calendar names in config.yaml.

    Args:
        calendar (googleapiclient.discovery.Resource): calendar res

    Returns:
        dict: {summary (str): id (str)}

    """
    cals = {}
    cal_names = [
        value['calendar']['name']
        for value
        in conf['tabs'].values()
        ]
    all_cals = calendar.calendarList().list().execute()['items']
    for cal in all_cals:
        if cal['summary'] in cal_names:
            cals[cal['summary']] = cal['id']

    return cals


def get_tab(entry: str, entry_names: dict):
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
                return entry

    return None


def get_calendar_entries(calendar, cal_id: str, cal_name: str):
    """Gets entries in a calendar given `cal_id`
    from yesterday until today.

    Args:
        calendar (googleapiclient.discovery.Resource): calendar res
        cal_id (str): the ID of the calendar
        cal_name (str): the name (summary) of the calendar

    Returns:
        dict: {tab (str): hours (int)}

    """
    tab_hours = defaultdict(int)
    entry_names = {
        tab: value['calendar']['entry_aliases']
        for tab, value
        in conf['tabs'].items()
        if value['calendar']['name'] == cal_name
        }
    all_entries = calendar.events().list(
        calendarId = cal_id,
        timeMin = YESTERDAY,
        timeMax = TODAY,
        singleEvents = True,
        orderBy = 'startTime',
        ).execute()['items']

    for entry in all_entries:
        tab = get_tab(entry['summary'], entry_names)
        if tab is None:
            continue
        start = pendulum.parse(entry['start']['dateTime'])
        end = pendulum.parse(entry['end']['dateTime'])
        tab_hours[tab] += (end - start).seconds/3600
        if tab_hours[tab] >= 24:
            logger.warning(f'Hours exceeded for tab {tab}')

    return tab_hours


def get_sheet_ids(sheets, tabs: list):
    """Gets sheet IDs filtered by `entry_names`.

    Args:
        sheets (googleapiclient.discovery.Resource): sheets res
        tabs (keys): tab names to filter for

    Returns:
        dict: {name: id}

    """
    sheet_ids = {}
    spreadsheet = sheets.spreadsheets().get(
        spreadsheetId = conf['spreadsheet_id']
        ).execute()['sheets']
    for sheet in spreadsheet:
        properties = sheet['properties']
        if properties['title'] in tabs:
            sheet_ids[properties['title']] = properties['sheetId']

    return sheet_ids


def col_to_day(col: str):
    """Converts a column `col` from a str to 1-indexed int (day).
    `col` will always be capitalized since `.upper` is called.

    Args:
        col (str): e.g. 'B' (1), 'C', (2) 'AA' (26)

    Returns:
        int: the day representation of the column

    """
    return ord(col) - 65


def day_to_col(day: int):
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


def input_hours_into_sheet(sheets, tab_hours: dict):
    """Inputs hours given `tab_hours` into their respective sheets.

    Args:
        sheets (googleapiclient.discovery.Resource): sheets res
        tab_hours (dict): {tab (str): hours (int)}

    Returns:
        None

    """
    tab_starts = {}
    for tab, value in conf['tabs'].items():
        cell = value['start']['cell']

        alpha = ALPHA.search(cell)
        col_int = col_to_day(cell[0:alpha.end()].upper())
        col_int += YESTERDAY.day - 1
        col = day_to_col(col_int)

        num = NUM.search(cell)
        try:
            row = int(cell[alpha.end():num.end()])
        except (TypeError, ValueError) as e:
            logger.error(e)
            continue
        start = pendulum.datetime(
            value['start']['year'],
            value['start']['month'],
            1,
            tz = 'local',
            )
        row += (YESTERDAY - start).months
        tab_starts[tab] = f'{tab}!{col}{row}'

    values = sheets.spreadsheets().values()

    for tab, hour in tab_hours.items():
        update = values.update(
            spreadsheetId = conf['spreadsheet_id'],
            range = tab_starts[tab],
            valueInputOption = 'USER_ENTERED',
            body = {'values': [[hour]]},
            ).execute()
        logger.info(f'Cells in sheet {tab} updated: {len(update)}')

    return


if __name__ == '__main__':
    calendar, sheets = authorize()
    sheet_ids = get_sheet_ids(sheets, conf['tabs'].keys())
    cals = get_calendars(calendar)
    if not cals:
        logger.error(
            'No calendars were found matching any in your configuration'
            )
    for cal_name, cal_id in cals.items():
        tab_hours = get_calendar_entries(calendar, cal_id, cal_name)
        if tab_hours:
            input_hours_into_sheet(sheets, tab_hours)
        else:
            logger.info('No tab-hours were found for yesterday')
