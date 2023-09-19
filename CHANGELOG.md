# Changelog

## [1.1.0] - Unreleased

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
