from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules("pydantic_ai_slim")

# Collect all data files
datas = collect_data_files("pydantic_ai_slim")

# Print debug information
print(f"Collected {len(hiddenimports)} hidden imports for pydantic_ai_slim")
print(f"Collected {len(datas)} data files for pydantic_ai_slim")
