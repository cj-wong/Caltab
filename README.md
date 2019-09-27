# (Google) Calendar-to-Sheets

## Overview

This project aims to automate recording hours from elapsed *Google Calendar* events into a sheet in *Google Sheets*. Specifically, it reads from any arbitrary number of calendars into respective spreadsheet sheet: one sheet can be assigned to one event to check. Hours are recorded by analyzing past events from the day before it's run.

## Requirements

This code is designed around the following:

- Python 3
    - all *Google API* related dependencies
    - `pendulum` in place of `datetime`
    - `pyyaml` for managing configuration
    - other [requirements](requirements.txt)
- [setup on *Google APIs*](https://console.developers.google.com/)
    - create credentials for both the Calendar and Sheets APIs
    - create a service account
    - add the service account to
        - all source *Google Calendar* calendars from which you plan to read
            - minimum permissions: **See all event details**
        - your destination *Google Sheets* spreadsheet
            - minimum permissions: **Edit files directly**
- [setup on *Google Sheets*](#sheet-structure)

## Setup

Set up your environment for self-hosting. Read [Requirements](#Requirements) for dependencies.
Python `venv` is highly recommended for managing your files, including dependencies.
Like so:

```
$ git clone <url> && cd REPO_NAME
$ # venv may be installable in package management.
$ # For Debian-like distros, `apt install python3-venv`
$ python -m venv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ # See directly below for setting up your config.
```

To set up your configuration, copy [`config.yaml.example`](config.yaml.example) into `config.yaml` and change all the fields according to your build.

## Calendar Structure

You can use an arbitrary number of calendars (less than or equal to the number of events read), but only one currently can be assigned per event. Read events should always either match the `Sheet Tab Name` in [configuration](#configuration) or any of its aliases (`entry_aliases`), or they will be skipped and omitted.

### Examples

#### Valid 1

- Calendar 1
    - Event 1
    - Alias of Event 1

#### Valid 2

- Calendar 1
    - Event 1
- Calendar 2
    - Event 2

#### Valid 3

- Calendar 1
    - Event 1
    - Event 2

#### Invalid 1

- Calendar 1
    - Event 1
- Calendar 2
    - Event 1

## Sheet Structure

For each sheet used by the script, use the structure below. *Italicized* values are the column and row markers, so don't input those. **Bold** values are user-inputted headers.

 -- | *A*         | *B*   | *C*   | *D*   | *E*   | ... | *AE*   | *AF*
----|-------------|-------|-------|-------|-------|-----|--------|--------
*1* | **yyyy, m** | **1** | **2** | **3** | **4** | ... | **30** | **31**
*2* | 2019, 1     |  `x`  |       |       |       |     |        |
*3* | 2019, 2     |       |       |       |       |     |        | 
... | ...         |       |       |       |       |     |        |
*12*| 2019, 11    |       |       |       |       |     |        |
*13*| 2019, 12    |       |       |       |       |     |        |

You can modify the rows and relabel column A, but the column structure should be consistent. Record where the sheet begins, i.e. the top-left corner of data. In this template, it's **B2**, where the `x` is.

## [Configuration](config.yaml.example)

- `spreadsheet_id` - ID of the destination *Google Sheets* spreadsheet
- `tabs` - individual destination sheets of the spreadsheet
    - `Sheet Tab Name` - name of one sheet
        - `calendar` - the source *Google Calendar* calendar used to scan entries
            - `name` - name of the calendar
            - `entry_aliases` - a list of aliases to match to `Sheet Tab Name`
        - `start` - starting reference of the sheet
            - `cell` - the top-left cell, as defined in [Sheet Structure](#sheet-structure)
            - `year` - the calendar year corresponding to that cell
            - `month` - the calendar month corresponding to that cell

## Disclaimer

This project is not affiliated with or endorsed by Google. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE) for more detail.
