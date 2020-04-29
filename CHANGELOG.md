# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.0] - 2020-04-29
### Changed
- The project has been renamed to *Caltab* for brevity: a tab (spreadsheet) with calendar entries' durations.
- Renamed `process.py` to [main.py](main.py).
- Moved all module-level code in [main.py](main.py) into separate function `main()`.
- Moved all *Google API* related modules into new directory [google](google).
- Changed return value of `api_handler.authorize()` to the credentials.
- Improved README; rewrote to clarify vocabulary and detailed steps for setup.
- [Configuration](config.yaml.example) has been simplified; to maintain separation, neither calendars nor sheets/tabs are nested in the other. Now, it's possible for two calendars to have the same event/sheet to track.
- In the [API handler](google/api_handler.py), `ExpiredCredentialsError` is now `ExpiredCredentials` and subclasses `RuntimeError` instead of an extraneous custom `Error`.
- In [google.calendar](google/calendar.py):
    - `Calendar.get_entries()` had its arguments reversed to match the dictionary's structure (`{calendar name: calendar id}`).
    - `get_tab()` no longer needs the second argument as `config.TABS` now contains the names and aliases. Furthermore, instead of returning `None`, the function either returns a string (matched tab name) or raises `TabNotFound` - handled with a try-except in `Calendar.get_entries()`.
- In [google.sheets](google/sheets.py):
    - `col_to_day()` and `day_to_col()` combined to form `get_yesterday_cell()`.
    - `Sheets.get_ids()` was removed, as it wasn't used.
    - Moved some functionality of `Sheets.input_hours()` into `Sheets.get_tab_cells()` to refactor. `Sheets.input_hours()` calls the new function to make up for lost functionality.

## [1.1.3] - 2019-12-25
### Changed
- Use `RotatingFileHandler` for logs

## [1.1.2] - 2019-11-20
### Changed
- Changed `len(update)` to more sensible `update['updatedCells']` in `gsheets.py`

### Fixed
- Fixed issue with missing `YESTERDAY` reference in `gsheets.py`

## [1.1.1] - 2019-11-05
### Changed
- Change stream logger error level to `INFO`

### Fixed
- Use `name` instead of `entry` when checking aliases in `gcalendar.py`

## [1.1.0] - 2019-10-12
### Added
- [`config.py`](config.py) handles configuration shared between all the modules.
- `api_handler.py` handles the *Google API* credentials and directly calls `gcalendar.py` & `gsheets.py`
- `gcalendar.py` & `gsheets.py` handle their respective *Google API* modules.

### Changed
- `process.py` was broken into the three new modules, for modularity.
- Furthermore, the Apache License *Google LLC*-licensed code was moved to [`config.py`](config.py)
- Instead of calling `sys.exit`, a new exception `api_handler.ExpiredCredentialsError` is raised.
- Several functions were simplified in name, because `gsheets.Sheets.get_sheet_ids` is redundant compared to `gsheets.Sheets.get_ids`.

## [1.0.0] - 2019-09-26
### Added
- Initial version
