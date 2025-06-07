from PyInstaller.utils.hooks import collect_data_files

# Include all data files from logfire
datas = collect_data_files("logfire")

# Add any additional hidden imports
hiddenimports = ["logfire.integrations.pydantic"]
