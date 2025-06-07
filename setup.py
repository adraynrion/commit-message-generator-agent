from pathlib import Path

from setuptools import find_packages, setup

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="commit-message-generator",
    version="1.0.0",  # Updated version for the enhanced implementation
    author="Adraynrion",
    author_email="your.email@example.com",
    description="An AI-powered tool to generate conventional commit messages from git diffs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adraynrion/commit-message-generator-agent",
    packages=find_packages(
        include=["commit_message_generator", "commit_message_generator.*"]
    ),
    package_data={
        "commit_message_generator": ["py.typed"],
    },
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pytest>=7.3.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "types-PyYAML>=6.0.0",
            "types-requests>=2.28.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "commit-msg-gen=commit_message_generator.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Version Control :: Git",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    keywords="git commit message generator ai cli",
    project_urls={
        "Bug Reports": "https://github.com/adraynrion/commit-message-generator-agent/issues",
        "Source": "https://github.com/adraynrion/commit-message-generator-agent",
    },
)
