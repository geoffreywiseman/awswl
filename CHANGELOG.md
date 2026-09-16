# Changelog

## [1.3.2] - 2026-09-15

### Internals

- Migrated project metadata from Poetry's `[tool.poetry]` schema to the PEP 621 `[project]`
  standard, keeping Poetry as the build and dependency tool
  - Caret constraints expanded to explicit PEP 508 ranges; dev dependencies moved to the PEP 735
    `[dependency-groups]` table
  - License declared as the SPDX expression `Unlicense` (matching `LICENSE.txt`) rather than the
    non-SPDX string "Public Domain", which PEP 639 deprecates
  - `poetry-core` now requires `>=2.0`, the first release to read `[project]`
- Replaced the `usingversion` dependency with `importlib.metadata` from the standard library
  - `usingversion` reads `tool.poetry.version` from `pyproject.toml` to resolve the version of an
    uninstalled source tree; that table no longer exists, so it raised `KeyError`. The package was
    last released in February 2024 and has no PEP 621 support
  - Behaviour is otherwise unchanged: an installed distribution reports its own version, and a
    source tree still reports a `+`-suffixed development version, now read from `[project]`
  - Drops two runtime dependencies (`usingversion`, `toml`)
- Removed the leftover `safety scan` step from the `lint` recipe in the justfile; it was already
  dropped from CI in favour of Dependabot
- Removed `awswl/VERSION`, an orphan from the 1.0.2 era that nothing read but that was still
  packaged, telling anyone who looked that this was version 1.0.2
- Corrected the README, which advertised a Python 3.9+ CI build; it covers 3.10 through 3.14
- Updated Ruff from 0.15.22 to 0.16.7
  - 0.16.0 expanded the default rule set from 59 rules to 413, which surfaced 18 lint violations
    in a project that relies on those defaults
  - Resolved all of them; the local date used by `--auto-desc` is deliberate and kept, with a
    documented suppression
- Dependency updates
  - boto3 from 1.43.53 to 1.43.95
  - moto from 5.2.2 to 5.2.3, cryptography from 48.0.1 to 50.0.1
  - Refreshed the full locked dependency set, including `certifi` from 2025.1.31 to 2026.7.22;
    `certifi` ships the CA bundle `requests` trusts, and it had drifted about eighteen months
    behind without being flagged by either Dependabot or the former Safety scan
- GitHub Actions updates
  - `actions/setup-python` from 6 to 7 in the release workflow

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
- Dependency updates
  - Runtime: boto3 from 1.36.17 to 1.43.53, requests from 2.32.3 to 2.34.2
  - The `urllib3` constraint was relaxed from `<2` to `<3`, moving it from 1.26.20 to 2.7.0
  - Development: Ruff from 0.7.4 to 0.15.22, mock from 5.1.0 to 5.2.0 (the pytest and moto
    upgrades are described above)
  - Transitive and documentation updates, including cryptography from 43.0.3 to 48.0.1, jinja2,
    idna, pygments, werkzeug and mkdocs
- GitHub Actions updates
  - `actions/checkout` from 2 to 7, `actions/setup-python` from 5 to 7,
    `github/codeql-action` from 1 to 4, `JRubics/poetry-publish` from 2.0 to 2.1

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
