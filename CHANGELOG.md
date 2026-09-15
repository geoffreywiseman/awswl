# Changelog

## [Unreleased]

### Internals

- Updated Ruff from 0.15.22 to 0.16.6
  - 0.16.0 expanded the default rule set from 59 rules to 413, which surfaced 18 lint violations
    in a project that relies on those defaults
  - Resolved all of them; the local date used by `--auto-desc` is deliberate and kept, with a
    documented suppression

## [1.3.1] - 2026-07-25

Patch release to fix publishing. The release workflow now takes the version from the git tag, so the
package metadata and the tag can no longer drift out of sync and fail the publish.

## [1.3.0] - 2026-07-25

### Added

- IPv6 Support
  - CIDR blocks are now recognized as IPv6 and allowlisted as such
- Privacy
  - `--disable-current` disables lookups of your current external IP address, preventing any network
    request to `checkip.amazonaws.com`
  - Cannot be combined with `add-current`, `remove-current` or `update-current`

### Changed

- Minimum Python is now 3.10, up from 3.9, which has reached end of life
  - The CI matrix drops 3.9 and adds 3.14
  - This is a breaking change for anyone still running 3.9
- `add` and `remove` now pre-check for duplicate or covering rules, and report more clearly when a
  CIDR block is already allowlisted or already covered by a broader existing rule

### Fixed

- Resolved the outstanding CodeQL alerts, and updated the CodeQL workflow for Python scanning

### Internals

- Upgraded moto from v4 to v5 (`mock_ec2` becomes `mock_aws`)
- Upgraded pytest from 7.4.4 to 9.1.1, modernised test idioms and filled coverage gaps
  - Consolidated the options fixtures into a single conftest factory
  - Re-enabled the CLI parser option tests
- Replaced the Safety scan with an explicit Dependabot configuration
- Stopped tracking `.coverage`
- Dependency updates, including boto3, requests, urllib3, cryptography, idna, mock and Ruff
- GitHub Actions updates, including checkout, setup-python, codeql-action and poetry-publish

## [1.2.2] - 2025-02-11

Updated dependencies to address security vulnerabilities. Added scan with safety cli.

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
