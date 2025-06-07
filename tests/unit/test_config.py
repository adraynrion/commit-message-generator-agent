"""Tests for the configuration module."""

from pathlib import Path

from commit_message_generator.config import (
    AIModelConfig,
    CommitMessageConfig,
    CommitType,
    GeneratorConfig,
    SeverityLevel,
    load_config_from_file,
)


def test_ai_model_config_defaults() -> None:
    """Test AIModelConfig with default values."""
    config = AIModelConfig()
    assert config.model_name == "gpt-4o-mini"
    assert config.temperature == 0.3
    assert config.max_tokens == 500
    assert config.top_p == 1.0


def test_commit_message_config_defaults() -> None:
    """Test CommitMessageConfig with default values."""
    config = CommitMessageConfig()
    assert config.max_line_length == 70


def test_generator_config_defaults() -> None:
    """Test GeneratorConfig with default values."""
    config = GeneratorConfig()
    assert isinstance(config.ai, AIModelConfig)
    assert isinstance(config.commit, CommitMessageConfig)


def test_load_config_from_file_yaml(tmp_path) -> None:
    """Test loading configuration from a YAML file."""
    config_content = """
    ai:
      model_name: test-model
      temperature: 0.5
    commit:
      max_line_length: 80
    """

    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    config = load_config_from_file(config_file)

    assert config.ai.model_name == "test-model"
    assert config.ai.temperature == 0.5
    assert config.commit.max_line_length == 80


def test_load_config_from_file_json(tmp_path) -> None:
    """Test loading configuration from a JSON file."""
    config_content = """
    {
        "ai": {
            "model_name": "test-model",
            "temperature": 0.5
        },
        "commit": {
            "max_line_length": 80
        }
    }
    """

    config_file = tmp_path / "config.json"
    config_file.write_text(config_content)

    config = load_config_from_file(config_file)

    assert config.ai.model_name == "test-model"
    assert config.ai.temperature == 0.5
    assert config.commit.max_line_length == 80


def test_load_config_from_nonexistent_file() -> None:
    """Test loading configuration from a non-existent file returns None."""
    assert load_config_from_file(Path("/nonexistent/file.yaml")) is None
    assert load_config_from_file(Path("/nonexistent/file.json")) is None


def test_commit_type_enum_values() -> None:
    """Test CommitType enum values."""
    assert CommitType.FEATURE.value == "FEATURE"
    assert CommitType.IMPROVE.value == "IMPROVE"
    assert CommitType.BUGFIX.value == "BUGFIX"
    assert CommitType.REFACTO.value == "REFACTO"
    assert CommitType.CORE.value == "CORE"
    assert CommitType.TEST.value == "TEST"
    assert CommitType.DOC.value == "DOC"


def test_severity_level_enum_values() -> None:
    """Test SeverityLevel enum values."""
    assert SeverityLevel.MAJOR.value == "MAJOR"
    assert SeverityLevel.MEDIUM.value == "MEDIUM"
    assert SeverityLevel.MINOR.value == "MINOR"
