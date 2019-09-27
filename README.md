# (Google) Calendar-to-Sheets

## Overview

This project aims to automate recording hours from elapsed Google Calendar events into a sheet in Google Sheets. Specifically, it reads from any arbitrary number of calendars into respective spreadsheet sheet: one sheet can be assigned to one event to check. Hours are recorded by analyzing past events from the day before it's run.

## Sheet Structure

yy, m | 1 | 2 | 3 | 4 | ... | 30 | 31
------|---|---|---|---|-----|----|----
19, 1 |   |   |   |   |     |    |
19, 2 |   |   |   |   |     |    | 

You can modify the rows, but the columns should be consistent.

## Requirements

This code is designed around the following:

- Python 3
    - all Google API related dependencies
    - `pendulum` in place of `datetime`
    - `pyyaml` for managing configuration
    - other [requirements](requirements.txt)
- setup on Google APIs
    - create authorization for both the Calendar and Sheets APIs
    - create a service account
    - add the service account to:
        - all Calendar calendars you plan to read from
        - your Google Sheets spreadsheet
- setup on Google Sheets
    - create (or reuse) your own spreadsheet

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

## Disclaimer

This project is not affiliated with or endorsed by Google. See [`LICENSE`](LICENSE) for more detail.
