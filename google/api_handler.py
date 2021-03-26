# Copyright 2019-2021 cj-wong
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

from config import LOGGER

# Replaced imports:
#   os.path -> pathlib.Path
# Moved imports:
#   from google.oauth2 import service_account
# Removed imports:
#   from google.auth.transport.requests import Request


SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    ]


class ExpiredCredentials(RuntimeError):
    """Credentials were expired."""

    def __init__(self):
        """Initialize the error with a message."""
        super().__init__('Credentials expired')


def authorize() -> service_account.Credentials:
    """Authorize the connection to the Google API.

    Adapted from Google's example:
        https://developers.google.com/calendar/quickstart/python

    See NOTICE for attribution.

    Returns:
        service_account.Credentials: credentials from JSON/pickle

    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    # Changed from:
    #   if os.path.exists('token.pickle'):
    #       with open('token.pickle', 'rb') as token:
    p = Path('token.pickle')
    try:
        with p.open(mode='rb') as token:
            creds = pickle.load(token)
    except (EOFError, FileNotFoundError):
        creds = None
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Changed from:
            #   creds.refresh(Request())
            # Since this will be run as a cron job, i.e. no UI,
            # log this condition and raise an error instead.
            LOGGER.error('Credentials expired')
            raise ExpiredCredentials
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
    return creds
