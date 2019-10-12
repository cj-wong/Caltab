# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1] - 2019-10-12
### Added
- [`config.py`](config.py) handles configuration shared between all the modules.
- [`api_handler.py`](api_handler.py) handles the *Google API* credentials and directly calls [`calendar.py`](calendar.py) & [`calendar.py`](calendar.py)
- [`calendar.py`](calendar.py) & [`calendar.py`](calendar.py) handle their respective *Google API* modules.

### Changed
- [`process.py`](process.py) was broken into the three new modules, for modularity.
- Furthermore, the Apache License *Google LLC*-licensed code was moved to [`config.py`](config.py)
- Instead of calling `sys.exit`, a new exception `api_handler.ExpiredCredentialsError` is raised.
- Several functions were simplified in name, because `sheets.Sheets.get_sheet_ids` is redundant compared to `sheets.Sheets.get_ids`.

## [1.0] - 2019-09-26
### Added
- Initial version
