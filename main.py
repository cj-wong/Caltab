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

import google.api_handler
import google.calendar
import google.sheets
from config import LOGGER


def main() -> None:
    """Run everything: authorization, calendar reads, spreadsheet writes.

    The spreadsheet is only written if events in the calendar are found.

    """
    creds = google.api_handler.authorize()
    calendar_api = google.calendar.Calendar(creds)
    sheets_api = google.sheets.Sheets(creds)
    calendars = calendar_api.get_calendar_ids()
    if not calendars:
        LOGGER.error(
            'No calendars were found matching any in your configuration')
        return
    for cal_name, cal_id in calendars.items():
        tab_hours = calendar_api.get_entries(cal_name, cal_id)
        if tab_hours:
            sheets_api.input_hours(tab_hours)
        else:
            LOGGER.info('No tab-hours were found for yesterday')


if __name__ == '__main__':
    main()
