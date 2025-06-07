# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import importlib.util
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

# Disable source code validation for Pydantic
os.environ['PYDANTIC_DISABLE_SOURCE_VALIDATION'] = '1'

# Add the current directory to the path
cwd = os.path.abspath('.')
sys.path.insert(0, cwd)

# Add the current directory to the hooks path
hookspath = ['hooks', cwd]

# Add runtime hooks
runtime_hooks = ['hooks/rthook-pydantic.py']

# Add hidden imports
hiddenimports = [
    'pydantic_core',
    'pydantic.json',
    'pydantic.typing',
    'pydantic.fields',
    'pydantic_ai_slim',
    'logfire.integrations.pydantic',
    'importlib_metadata',
]

block_cipher = None

# Collect metadata for required packages
datas = []
try:
    datas += copy_metadata('pydantic_ai')
    datas += copy_metadata('pydantic_ai_slim')
    datas += copy_metadata('importlib_metadata')
    # pkg_resources is part of setuptools, which is a dependency of PyInstaller
    # We don't need to copy its metadata as it's already included in the Python standard library
except Exception as e:
    print(f"Warning: Could not copy metadata: {e}")

# Add package data for commit_message_generator
try:
    pkg_data = collect_data_files('commit_message_generator')
    datas.extend(pkg_data)
    print(f"Added {len(pkg_data)} data files for commit_message_generator")
except Exception as e:
    print(f"Warning: Could not add commit_message_generator package data: {e}")

# Add package data for pydantic_ai_slim
try:
    pkg_data = collect_data_files('pydantic_ai_slim')
    datas.extend(pkg_data)
    print(f"Added {len(pkg_data)} data files for pydantic_ai_slim")
except Exception as e:
    print(f"Warning: Could not add pydantic_ai_slim package data: {e}")

# Add package data for importlib_metadata
try:
    pkg_data = collect_data_files('importlib_metadata')
    datas.extend(pkg_data)
    print(f"Added {len(pkg_data)} data files for importlib_metadata")
except Exception as e:
    print(f"Warning: Could not add importlib_metadata package data: {e}")

a = Analysis(
    ['commit_message_generator/__main__.py'],
    pathex=[cwd],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports + [
        'commit_message_generator',
        'commit_message_generator.commit_generator',
        'commit_message_generator.config',
        'commit_message_generator.git_utils',
        'commit_message_generator.models',
        'pydantic_ai',
        'pydantic_ai_slim',
        'importlib_metadata',
        'pkg_resources.py2_warn',
        'importlib_metadata._adapters',
        'importlib_metadata._collections',
        'importlib_metadata._compat',
        'importlib_metadata._functools',
        'importlib_metadata._itertools',
        'importlib_metadata._meta',
        'importlib_metadata._text',
    ],
    hookspath=hookspath,
    runtime_hooks=runtime_hooks + ['rthook-pydantic_ai.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Function to collect all files from a package
def collect_package_files(package_name, include_package_data=True):
    files = []
    try:
        # Get the package's distribution
        import importlib.metadata
        dist = importlib.metadata.distribution(package_name)

        # Get the package's location
        package_path = os.path.dirname(dist._path)  # type: ignore

        # Walk through the package directory
        for root, _, filenames in os.walk(package_path):
            for filename in filenames:
                if not filename.endswith('.pyc') and not filename.endswith('.pyo'):
                    src_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(src_path, os.path.dirname(package_path))
                    dst_dir = os.path.dirname(rel_path)
                    files.append((src_path, dst_dir))

        print(f"Added package data from: {package_name} at {package_path}")
    except Exception as e:
        print(f"Warning: Could not add package data for {package_name}: {e}")

    return files

# Add package data for pydantic_ai_slim
try:
    pkg_data = collect_package_files('pydantic_ai_slim')
    a.datas.extend(pkg_data)
    print(f"Added {len(pkg_data)} data files for pydantic_ai_slim")
except Exception as e:
    print(f"Warning: Could not add pydantic_ai_slim package data: {e}")

# Add package data for commit_message_generator
try:
    pkg_data = collect_data_files('commit_message_generator')
    for src, dst in pkg_data:
        a.datas.append((src, os.path.dirname(dst) if dst else ''))
    print(f"Added {len(pkg_data)} data files for commit_message_generator")
except Exception as e:
    print(f"Warning: Could not add commit_message_generator package data: {e}")

# Filter out any invalid TOC entries
def filter_toc(toc):
    return [item for item in toc if len(item) >= 3]

a.binaries = filter_toc(a.binaries)
a.datas = filter_toc(a.datas)

# Create the PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='commit-msg-gen',
    debug=False,
    bootloader_ignore_signals=True,
    strip=False,
    upx=True,
    console=True,
    onefile=True
)

print("\nBuild completed. To test the executable, run:")
print("  ./dist/commit-msg-gen --help")
