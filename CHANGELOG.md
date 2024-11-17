# Changelog

## [1.2.1] - 2024-11-16

Discovered after publishing 1.2.0 that the version command which worked locally did not work in the installed version. Fixed and published again.

## [1.2.0] - 2024-11-16

Significant change to the CLI options and the addition of `update` commands.

### Added

- New commands to Update a Rule
  - `update` updates the CIDR block associated with a description to a new specified value
  - `update-current` updates the CIDR block associated with a description to your current external ip
  - Documentation for the new commands is available in [Usage](docs/usage.md) 

### Changed

- Refactored the CLI options
  - The *commands* have been changed from options (e.g. `awswl --list`) to positional arguments (e.g. `awswl list`)
  - This also means that each invocation can only have a single command.
  - Effectively this makes it easier to avoid weird interactions between multiple commands and their options.
  - Updated documentation in [Usage](docs/usage.md) to match

### Internals

- Dependency Updates
  - Several security vulnerabilities were reported in dependencies
  - Avoiding those vulnerabilities by updating to newer versions

## [1.1.0] - 2023-09-19

### Added
- Search for Security Group by Name
  - `--sg-name` option to let you modify a security group by unique name (including wildcards)
- Descriptions
  - Show descriptions in `--list`
  - `--auto-desc` to generate a description from username and date while adding
  - `--desc` to specify a description while adding

### Internals
- Converted to Poetry Project
- Dependency Upgrades
- GitHub Actions for CI / Publish
- Using Ruff for linting
- ReadTheDocs

## [1.0.1] - 2018-05-08

### Changed
- Made some improvements to the Python2 support after I discovered the python2 support in 1.0.0
  wasn't fully functional.

## [1.0.0]

### Added
- `--list` lists allowlist CIDR blocks
- `--add-current` adds your current external ip in CIDR form to the allowlist
- `--remove-current` to remove your current external ip in CIDR form from the allowlist
- `--add` to add manually-specified CIDR blocks to the allowlist
- `--remove` to remove manual CIDR blocks from the allowlist
