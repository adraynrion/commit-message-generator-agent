"""Configuration models for the commit message generator."""

import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator


class CommitType(str, Enum):
    """Supported commit types."""

    FEATURE = "FEATURE"
    IMPROVE = "IMPROVE"
    BUGFIX = "BUGFIX"
    REFACTO = "REFACTO"
    CORE = "CORE"
    TEST = "TEST"
    DOC = "DOC"


class SeverityLevel(str, Enum):
    """Severity levels for commits."""

    MAJOR = "MAJOR"
    MEDIUM = "MEDIUM"
    MINOR = "MINOR"


class AIModelConfig(BaseModel):
    """Configuration for the AI model."""

    model_name: str = Field(
        ..., description="Name of the AI model to use (e.g., gpt-4o-mini)"
    )
    temperature: float = Field(
        0.2, ge=0.0, le=2.0, description="Temperature for text generation"
    )
    max_tokens: int = Field(
        500, ge=100, le=4000, description="Maximum number of tokens to generate"
    )
    top_p: float = Field(1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: str = Field("INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    file: Optional[str] = Field(
        None,
        description="Path to log file. If None or empty, logs to console only",
    )

    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that the logging level is valid."""
        v_upper = v.upper()
        if v_upper not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {v}. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        return v_upper


class CommitMessageConfig(BaseModel):
    """Configuration for commit message generation."""

    require_ticket: bool = Field(
        True, description="Whether a ticket number is required"
    )
    default_commit_type: CommitType = Field(
        CommitType.IMPROVE, description="Default commit type if not detected"
    )
    default_severity: SeverityLevel = Field(
        SeverityLevel.MEDIUM, description="Default severity if not detected"
    )
    max_line_length: int = Field(
        70, ge=50, le=100, description="Maximum line length for commit messages"
    )


class GeneratorConfig(BaseModel):
    """Top-level configuration for the commit message generator."""

    ai: AIModelConfig = Field(
        default_factory=AIModelConfig, description="AI model configuration"
    )
    commit: CommitMessageConfig = Field(
        default_factory=CommitMessageConfig,
        description="Commit message generation settings",
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration",
    )
    custom_prompts: Dict[str, str] = Field(
        default_factory=dict, description="Custom prompts for different commit types"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ai": {
                    "model_name": "gpt-4o-mini",
                    "temperature": 0.2,
                    "max_tokens": 500,
                    "top_p": 1.0,
                },
                "commit": {
                    "require_ticket": True,
                    "default_commit_type": "IMPROVE",
                    "default_severity": "MEDIUM",
                    "max_line_length": 70,
                },
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "file": "commit_gen.log"
                },
                "custom_prompts": {
                    "FEATURE": "You are adding a new feature...",
                    "BUGFIX": "You are fixing a bug...",
                },
            }
        }


def setup_logging(logging_config: LoggingConfig) -> None:
    """Configure logging based on the provided configuration.

    Args:
        logging_config: Logging configuration
    """
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging_config.level)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(logging_config.format)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if file path is specified
    if logging_config.file:
        try:
            # Create directory if it doesn't exist
            log_file = Path(logging_config.file).expanduser().resolve()
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.debug(f"Logging to file: {log_file}")
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {e}")

    logger.debug(f"Logging configured with level: {logging_config.level}")


def load_config_from_file(file_path: str) -> Optional[GeneratorConfig]:
    """Load configuration from a YAML or JSON file.

    Args:
        file_path: Path to the configuration file.

    Returns:
        Loaded configuration or None if the file doesn't exist.

    Raises:
        ValueError: If the file has an unsupported extension or is invalid.
    """
    import os
    from pathlib import Path

    if not os.path.isfile(file_path):
        return None

    file_ext = Path(file_path).suffix.lower()

    try:
        if file_ext in ('.yaml', '.yml'):
            import yaml
            with open(file_path, 'r') as f:
                config_data = yaml.safe_load(f)
        elif file_ext == '.json':
            import json
            with open(file_path, 'r') as f:
                config_data = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {file_ext}")

        # Initialize config
        config = GeneratorConfig(**config_data)

        # Set up logging based on config
        setup_logging(config.logging)

        return config
    except Exception as e:
        # Set up basic logging to capture the error
        logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to load config from {file_path}: {str(e)}")
        raise ValueError(f"Failed to load config from {file_path}: {str(e)}")
