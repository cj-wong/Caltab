# Caltab

## Overview

Want to record event duration from your *[Google Calendar][GCAL]* calendar into a *[Google Sheets][GSHEETS]* spreadsheet? This project has you covered: it automates the process for you! Each tracked event can be recorded into a spreadsheet containing a sheet with the same name. Aliases can be added per event as necessary.

## Requirements

This code is designed around the following:

- Python 3
    - all *[Google API][GAPI]* related dependencies
    - `pendulum` in place of `datetime`
    - `pyyaml` for managing configuration
    - other [requirements](requirements.txt)

## Setup

1. Go to *[Google APIs][GAPI]* and create a new project. You may **edit** the project ID or set "Location" if necessary. After creating the project, select and open the project from the dropdown by the *"Google APIs"* logo.
2. Navigate to the **"APIs & Services"** section in the hamburger menu. Click on **"Enable APIs and Services"**.
3. Look for either *Google Calendar API* or *Google Sheets API* and select it. You'll repeat steps 2-4 for the other API.
4. Click **"Enable"**.
5. On the next screen, click either **"Credentials"** in the side menu or **"Create Credentials"**.
6. You'll have to enter in several values on the next page.

    - **"Which API are you using?":** pick the API you've selected.
    - **"Where will you be calling the API from?":** *"Other non-UI (e.g. cron job, daemon)"*
    - **"What data will you be accessing?":** *"Application Data"*
    - **"Are you planning to use this API with App Engine or Compute Engine?":** *"No, I'm not using them"*
    - Click **"What credentials do I need?"** next to proceed.

7. Enter a service account name. Under **"Role"**, click `Project > Editor`. Click "Continue", and a JSON should be downloaded. Rename this JSON as `credentials.json` and move it to the project root.
8. Repeat steps 2-4 for the other API.
9. In **"API & Services" > "Credentials"**, copy and/or make a note of the e-mail address of the service account just created. You will need this for setup with both *Google Calendar* and *Google Sheets*.
10. Copy [`config.yaml.example`](config.yaml.example) to `config.yaml`.
11. Follow the setup for *[Calendar](#calendar-setup)* and *[Sheets](#sheets-setup)*.

## [Calendar][GCAL] Setup

0. Create your calendars as desired.
1. In [settings](https://calendar.google.com/calendar/r/settings), click on the calendar you will link to this project.
2. In **"Share with specific people"**, click **"Add people"** and paste the aforementioned service account e-mail address. In the dropdown to the side, you can set the permission of the service account; I recommend **"See all event details"**, the minimum.
3. Repeat steps 1-2 as necessary with each calendar you wish to link.
4. For each calendar you linked to the service account, list them under `calendars:` along with corresponding sheets/tabs. **Note that these tabs must correspond to the `tabs:` under `spreadsheet:`.**

### Calendar Structure

Each event in the configuration must belong only to one calendar and must only be recorded in one sheet. Event names must match either the name (e.g. `Sheet Tab 1 Name` in the [example](config.yaml.example)) or its alias(es) (e.g. `alias 1`) in the configuration; unmatched events are skipped. In the examples below, *"event"* refers to the name (`Sheet Tab 1 Name`) and must correspond to a same-name spreadsheet sheet/tab.

*Examples:*

- You can have an event and its alias in the same calendar.
- You can have one event in one calendar and another event in another calendar.
- You can have two different events in the same calendar.
- You can have an event be in two calendars. Under both calendars in the configuration, list the event under `tabs:`.

## [Sheets][GSHEETS] Setup

0. Create your spreadsheet as desired, including sheets corresponding to each "tab" entry in the configuration.
1. Copy the speadsheet ID: it's the ellipsis in `https://docs.google.com/spreadsheets/d/.../edit#gid=0`. Record that into `id:` below `spreadsheet:` in the configuration. 
2. In the **"Share"** menu in the top right, paste the aforementioned service account e-mail address. In the dropdown to the side, you can set the permission of the service account; you must select **"Can edit"**, the minimum permission for the project.
3. For each sheet/tab you plan to use with calendar tracking, copy the template starting with the name up til `month:`. Follow the below instructions.

    - List each tab under `tabs:` with aliases and other attributes. **Note that each tabs must correspond to the `tabs:` under at least one calendar entry in `calendars:`.**
    - Record the starting cell (top-left cell) location into `cell:` under `start:`. In the example below, it's `cell: B2`.
    - Also under `start:`, record which year (`year:`) and month (`month:`) that row corresponds to the cell. In the example below, it's `year: 2019` and `month: 1`.

### Sheets Structure

For each sheet used by the project, use the structure below. *Italicized* values are the column and row markers, so don't input those. **Bold** values are user-inputted headers.

 .  | *A*         | *B*   | *C*   | *D*   | *E*   | ... | *AE*   | *AF*
----|-------------|-------|-------|-------|-------|-----|--------|--------
*1* | **yyyy, m** | **1** | **2** | **3** | **4** | ... | **30** | **31**
*2* | 2019, 1     |  `x`  |       |       |       |     |        |
*3* | 2019, 2     |       |       |       |       |     |        | 
... | ...         |       |       |       |       |     |        |
*12*| 2019, 11    |       |       |       |       |     |        |
*13*| 2019, 12    |       |       |       |       |     |        |

You can modify the rows and relabel column A (or even omit it), but the column structure should be consistent. Record where the sheet begins, i.e. the top-left corner of data. In this template, it's **B2**, where the `x` is.

## Project Files

- [config.py](config.py)
    - configuraton handler
- [config.yaml.example](config.yaml.example)
    - template configuration; copy to `config.yaml` and follow [setup](#setup)
- [main.py](main.py)
    - the script for this project
- [google/api_handler.py](google/api_handler.py)
    - handles credentials for the *[Google APIs][GAPI]*
- [google/calendar.py](google/calendar.py)
    - *[Google Calendar][GCAL] API* handler
- [google/sheets.py](google/sheets.py)
    - *[Google Sheets][GSHEETS] API* handler

## Disclaimer

This project is not affiliated with or endorsed by *Google*. See [LICENSE](LICENSE) and [NOTICE](NOTICE) for more detail.

[GAPI]: https://console.developers.google.com/
[GCAL]: https://calendar.google.com/
[GSHEETS]: https://sheets.google.com/
