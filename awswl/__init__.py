"""Expose the package version as ``awswl.version``."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 has no tomllib; tomli is the backport.
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None

_PACKAGE_NAME = "awswl"


def _version_from_source_tree() -> str | None:
    """Read the version from pyproject.toml, for a tree that was never installed."""
    if tomllib is None:
        return None
    for directory in Path(__file__).resolve().parents[:3]:
        pyproject = directory / "pyproject.toml"
        if not pyproject.is_file():
            continue
        with pyproject.open("rb") as handle:
            version = tomllib.load(handle).get("project", {}).get("version")
        # Trailing '+' marks a tree that may be modified or unreleased.
        return f"{version}+" if version else None
    return None


def __getattr__(name: str) -> str:
    if name in ("version", "_version"):
        try:
            return _distribution_version(_PACKAGE_NAME)
        except PackageNotFoundError:
            return _version_from_source_tree() or "unknown"
    raise AttributeError(f"No attribute {name} in module {__name__}.")
