"""Configuration models for the commit message generator."""

from enum import Enum
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
        "gpt-4-turbo-preview", description="Name of the AI model to use"
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
    custom_prompts: Dict[str, str] = Field(
        default_factory=dict, description="Custom prompts for different commit types"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ai": {
                    "model_name": "gpt-4-turbo-preview",
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
                "custom_prompts": {
                    "FEATURE": "You are adding a new feature...",
                    "BUGFIX": "You are fixing a bug...",
                },
            }
        }


def load_config_from_file(file_path: str) -> Optional[GeneratorConfig]:
    """Load configuration from a YAML or JSON file.

    Args:
        file_path: Path to the configuration file.

    Returns:
        Loaded configuration or None if the file doesn't exist.

    Raises:
        ValueError: If the file has an unsupported extension or is invalid.

    """
    import json
    from pathlib import Path

    import yaml

    path = Path(file_path)
    if not path.exists():
        return None

    content = path.read_text(encoding="utf-8")

    try:
        if path.suffix.lower() in (".yaml", ".yml"):
            config_dict = yaml.safe_load(content)
        elif path.suffix.lower() == ".json":
            config_dict = json.loads(content)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

        return GeneratorConfig(**config_dict)

    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid configuration file {file_path}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error loading configuration from {file_path}: {str(e)}")
