#!/usr/bin/env python3
"""
Configuration Loader for Code Duplication Analysis Skill

Handles loading configuration from multiple sources with proper precedence:
1. Command-line arguments (highest priority)
2. Configuration file (.duplication-config.json)
3. Default values (lowest priority)

Supports:
- JSON configuration files
- Configuration file discovery
- Schema validation
- Precedence merging
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import asdict, replace

from models import Config


class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""
    pass


def find_config_file(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Search for .duplication-config.json starting from current directory
    and walking up to root.

    Args:
        start_path: Starting directory (defaults to current directory)

    Returns:
        Path to config file if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Walk up the directory tree
    while True:
        config_file = current / ".duplication-config.json"
        if config_file.exists() and config_file.is_file():
            return config_file

        # Stop at root
        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


def load_config_file(config_path: Path) -> Dict[str, Any]:
    """
    Load and validate configuration from JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Dictionary of configuration values

    Raises:
        ConfigurationError: If file is invalid or malformed
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigurationError(
            f"Invalid JSON in configuration file {config_path}: {e}"
        )
    except IOError as e:
        raise ConfigurationError(
            f"Cannot read configuration file {config_path}: {e}"
        )

    if not isinstance(config_data, dict):
        raise ConfigurationError(
            f"Configuration file {config_path} must contain a JSON object"
        )

    return config_data


def validate_config_schema(config_data: Dict[str, Any]) -> None:
    """
    Validate configuration data against schema.

    Args:
        config_data: Configuration dictionary to validate

    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Validate types
    if "min_lines" in config_data:
        if not isinstance(config_data["min_lines"], int):
            raise ConfigurationError("min_lines must be an integer")
        if config_data["min_lines"] < 1:
            raise ConfigurationError("min_lines must be at least 1")

    if "similarity_threshold" in config_data:
        if not isinstance(config_data["similarity_threshold"], (int, float)):
            raise ConfigurationError("similarity_threshold must be a number")
        if not 0.0 <= config_data["similarity_threshold"] <= 1.0:
            raise ConfigurationError("similarity_threshold must be between 0.0 and 1.0")

    if "exclude_patterns" in config_data:
        if not isinstance(config_data["exclude_patterns"], list):
            raise ConfigurationError("exclude_patterns must be a list")
        if not all(isinstance(p, str) for p in config_data["exclude_patterns"]):
            raise ConfigurationError("exclude_patterns must contain only strings")

    if "include_patterns" in config_data:
        if not isinstance(config_data["include_patterns"], list):
            raise ConfigurationError("include_patterns must be a list")
        if not all(isinstance(p, str) for p in config_data["include_patterns"]):
            raise ConfigurationError("include_patterns must contain only strings")

    if "languages" in config_data:
        if not isinstance(config_data["languages"], list):
            raise ConfigurationError("languages must be a list")
        if not all(isinstance(lang, str) for lang in config_data["languages"]):
            raise ConfigurationError("languages must contain only strings")

    if "ignore_comments" in config_data:
        if not isinstance(config_data["ignore_comments"], bool):
            raise ConfigurationError("ignore_comments must be a boolean")

    if "ignore_whitespace" in config_data:
        if not isinstance(config_data["ignore_whitespace"], bool):
            raise ConfigurationError("ignore_whitespace must be a boolean")

    if "incremental_mode" in config_data:
        if not isinstance(config_data["incremental_mode"], bool):
            raise ConfigurationError("incremental_mode must be a boolean")

    if "output_format" in config_data:
        if config_data["output_format"] not in ["markdown", "json"]:
            raise ConfigurationError("output_format must be 'markdown' or 'json'")

    if "output_path" in config_data:
        if not isinstance(config_data["output_path"], str):
            raise ConfigurationError("output_path must be a string")

    if "verbose" in config_data:
        if not isinstance(config_data["verbose"], bool):
            raise ConfigurationError("verbose must be a boolean")

    if "max_file_size_kb" in config_data:
        if not isinstance(config_data["max_file_size_kb"], int):
            raise ConfigurationError("max_file_size_kb must be an integer")
        if config_data["max_file_size_kb"] < 1:
            raise ConfigurationError("max_file_size_kb must be at least 1")

    if "parallel_processing" in config_data:
        if not isinstance(config_data["parallel_processing"], bool):
            raise ConfigurationError("parallel_processing must be a boolean")


def merge_configs(base: Config, overrides: Dict[str, Any]) -> Config:
    """
    Merge configuration overrides into base configuration.

    Args:
        base: Base configuration (lower priority)
        overrides: Configuration overrides (higher priority)

    Returns:
        New Config instance with merged values
    """
    # Convert base config to dict
    base_dict = asdict(base)

    # Merge overrides (special handling for Path objects)
    for key, value in overrides.items():
        if key in base_dict:
            # Convert string paths to Path objects
            if key == "output_path" and isinstance(value, str):
                value = Path(value)
            base_dict[key] = value

    # Create new Config from merged dict
    return Config(**base_dict)


def load_configuration(
    config_file_path: Optional[Path] = None,
    cli_overrides: Optional[Dict[str, Any]] = None,
    project_root: Optional[Path] = None
) -> Config:
    """
    Load configuration from multiple sources with proper precedence.

    Precedence (highest to lowest):
    1. CLI overrides (passed as arguments)
    2. Configuration file (.duplication-config.json)
    3. Default values (from Config dataclass)

    Args:
        config_file_path: Explicit path to config file (optional)
        cli_overrides: Dictionary of CLI argument overrides (optional)
        project_root: Project root directory for config file discovery (optional)

    Returns:
        Merged Config instance

    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Start with defaults
    config = Config()

    # Step 1: Load from config file if available
    if config_file_path is None:
        # Auto-discover config file
        config_file_path = find_config_file(project_root)

    if config_file_path is not None:
        file_config = load_config_file(config_file_path)
        validate_config_schema(file_config)
        config = merge_configs(config, file_config)

    # Step 2: Apply CLI overrides (highest priority)
    if cli_overrides:
        validate_config_schema(cli_overrides)
        config = merge_configs(config, cli_overrides)

    return config


def create_example_config() -> str:
    """
    Generate example configuration file content.

    Returns:
        JSON string with example configuration
    """
    example = {
        "min_lines": 7,
        "similarity_threshold": 0.85,
        "exclude_patterns": [
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.git/**",
            "**/venv/**",
            "**/dist/**",
            "**/build/**",
            "**/test_*.py",
            "**/*_test.go",
            "**/*.spec.ts"
        ],
        "include_patterns": [],
        "languages": [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "cpp"
        ],
        "ignore_comments": True,
        "ignore_whitespace": True,
        "incremental_mode": False,
        "output_format": "markdown",
        "output_path": "./duplication-report.md",
        "verbose": False,
        "max_file_size_kb": 1024,
        "parallel_processing": True
    }

    return json.dumps(example, indent=2)


def save_example_config(output_path: Path) -> None:
    """
    Save example configuration to file.

    Args:
        output_path: Where to save the example config
    """
    example_content = create_example_config()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(example_content)


# Export public API
__all__ = [
    "ConfigurationError",
    "find_config_file",
    "load_config_file",
    "validate_config_schema",
    "merge_configs",
    "load_configuration",
    "create_example_config",
    "save_example_config",
]
