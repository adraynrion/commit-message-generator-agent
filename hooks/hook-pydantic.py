from PyInstaller.utils.hooks import collect_data_files

# Include all data files from pydantic
datas = collect_data_files("pydantic")

# Disable source code inspection for Pydantic
import os

os.environ["PYDANTIC_DISABLE_SOURCE_VALIDATION"] = "1"

# Add any additional hidden imports
hiddenimports = ["pydantic.json", "pydantic.typing", "pydantic.fields"]
