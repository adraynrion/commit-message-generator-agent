"""Configuration models for the commit message generator."""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional

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
        default="gpt-4o-mini",
        description="Name of the AI model to use (e.g., gpt-4o-mini)",
    )
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description="Temperature for text generation",
    )
    max_tokens: int = Field(
        default=500,
        ge=100,
        le=4000,
        description="Maximum number of tokens to generate",
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter",
    )
    max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of attempts to generate a valid commit message",
    )

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    file: Optional[str] = Field(
        default=None,
        description="Path to log file. If None or empty, logs to console only",
    )

    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that the logging level is valid."""
        v_upper = v.upper()
        if v_upper not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )
        return v_upper


class CommitMessageConfig(BaseModel):
    """Configuration for commit message generation."""

    max_line_length: int = Field(
        default=80,
        ge=50,
        le=100,
        description="Maximum line length for commit messages",
    )


class LangfuseConfig(BaseModel):
    """Configuration for Langfuse tracing."""

    enabled: bool = Field(
        default=False,
        description="Whether to enable Langfuse tracing",
    )
    public_key: str = Field(
        default="",
        description="Langfuse public key",
    )
    secret_key: str = Field(
        default="",
        description="Langfuse secret key",
    )
    host: str = Field(
        default="https://cloud.langfuse.com",
        description="Langfuse host URL",
    )


class GeneratorConfig(BaseModel):
    """Top-level configuration for the commit message generator."""

    ai: AIModelConfig = Field(
        default=AIModelConfig(model_name="gpt-4"), description="AI model configuration"
    )
    commit: CommitMessageConfig = Field(
        default=CommitMessageConfig(),
        description="Commit message generation settings",
    )
    langfuse: LangfuseConfig = Field(
        default=LangfuseConfig(),
        description="Langfuse tracing configuration",
    )
    logging: LoggingConfig = Field(
        default=LoggingConfig(),
        description="Logging configuration",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "ai": {
                    "model_name": "gpt-4o-mini",
                    "temperature": 0.2,
                    "max_tokens": 500,
                    "top_p": 1.0,
                },
                "commit": {
                    "max_line_length": 80,
                },
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "file": "commit_gen.log",
                },
            }
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
    logger = logging.getLogger(__name__)
    path = Path(file_path)
    logger.debug(f"Loading config from: {path.absolute()}")

    if not path.exists():
        logger.warning(f"Config file not found: {path.absolute()}")
        return None

    # Load the config file
    try:
        if path.suffix.lower() in (".yaml", ".yml"):
            import yaml

            with open(path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
                logger.debug(f"Loaded YAML config: {config_data}")
        elif path.suffix.lower() == ".json":
            import json

            with open(path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                logger.debug(f"Loaded JSON config: {config_data}")
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

        if not config_data:
            logger.warning(f"Empty config file: {path.absolute()}")
            return None

        logger.debug(f"Raw config data: {config_data}")

        # Ensure all sections exist in the config data
        if "langfuse" in config_data:
            logger.debug(f"Langfuse config found: {config_data['langfuse']}")
        else:
            logger.debug("No Langfuse config found in file")

        # Convert the config data to a GeneratorConfig object
        config = GeneratorConfig(**config_data)
        logger.debug(f"Successfully loaded config: {config}")
        return config

    except Exception as e:
        logger.error(f"Error loading config file {file_path}: {str(e)}", exc_info=True)
        raise ValueError(f"Error loading config file {file_path}: {str(e)}")
