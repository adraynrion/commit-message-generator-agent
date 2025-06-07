# This is a runtime hook to handle pydantic_ai_slim package metadata
import os
import sys
from typing import cast

# Add the path to the pydantic_ai_slim package directory
# _MEIPASS is added by PyInstaller at runtime
pkg_dir = os.path.join(sys._MEIPASS, "pydantic_ai_slim")  # type: ignore[attr-defined]
sys.path.insert(0, pkg_dir)

# Mock the importlib.metadata functions to handle the package metadata
import importlib.metadata

_original_distribution = importlib.metadata.distribution
_original_from_name = importlib.metadata.Distribution.from_name


def patched_distribution(package_name):
    try:
        return _original_distribution(package_name)
    except importlib.metadata.PackageNotFoundError:
        if package_name == "pydantic_ai_slim":
            # Return a dummy distribution
            class DummyDistribution:
                def __init__(self) -> None:
                    self.metadata = {"Name": "pydantic-ai-slim", "Version": "0.1.0"}

                @property
                def version(self):
                    return self.metadata["Version"]

            return DummyDistribution()
        raise


# Patch the distribution function
importlib.metadata.distribution = patched_distribution


# Also patch the Distribution.from_name method
class PatchedDistribution(importlib.metadata.Distribution):
    @classmethod
    def from_name(cls, name: str) -> "PatchedDistribution":
        if name == "pydantic_ai_slim":
            return cast("PatchedDistribution", cls.at("/non/existent/path"))
        return cast("PatchedDistribution", _original_from_name(name))


# Use setattr to avoid mypy error about method assignment
setattr(importlib.metadata.Distribution, "from_name", PatchedDistribution.from_name)
