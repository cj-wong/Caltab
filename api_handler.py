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
import pickle
from pathlib import Path

from google.oauth2 import service_account

import calendar
import sheets
from config import LOGGER

# Replaced imports:
#   os.path -> pathlib.Path
#   datetime -> pendulum
# Moved imports:
#   from google.oauth2 import service_account
# Removed imports:
#   from google.auth.transport.requests import Request


SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    ]


class Error(Exception):
    """Base exception for api_handler"""
    pass


class ExpiredCredentialsError(Error):
    """Credentials were expired."""
    def __init__(self):
        super().__init__('Credentials expired')


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
        with p.open(mode='rb') as token:
            try:
                creds = pickle.load(token)
            except EOFError:
                LOGGER.warning('token.pickle is likely empty')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Changed from:
            #   creds.refresh(Request())
            # Since this will be run as a cron job, i.e. no UI,
            # log this condition and raise an error instead.
            LOGGER.error('Credentials expired')
            raise ExpiredCredentialsError
        else:
            # Changed from:
            #   flow = InstalledAppFlow.from_client_secrets_file(
            #       'credentials.json', SCOPES)
            #   creds = flow.run_local_server(port=0)
            creds = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=SCOPES
                )
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Changed from:
    #   service = build('calendar', 'v3', credentials=creds)
    return (
        calendar.Calendar(creds),
        sheets.Sheets(creds),
        )
