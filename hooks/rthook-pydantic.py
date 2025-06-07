# This hook prevents Pydantic from trying to access source code at runtime
import os

# Disable source code validation
os.environ["PYDANTIC_DISABLE_SOURCE_VALIDATION"] = "1"

# Monkey patch inspect.getsource to prevent source code access
import inspect


def _getsource_stub(*args, **kwargs) -> str:
    return "# Source code not available in frozen application"


original_getsource = inspect.getsource
inspect.getsource = _getsource_stub


# Also patch getsourcelines
def _getsourcelines_stub(*args, **kwargs):
    return ["# Source code not available in frozen application"], 0


original_getsourcelines = inspect.getsourcelines
inspect.getsourcelines = _getsourcelines_stub
