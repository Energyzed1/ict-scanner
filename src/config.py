"""
Configuration management for the ICT PD Array Scanner
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable interpolation
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing the configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    # Environment variable interpolation
    _interpolate_env_vars(config)
    
    return config
    
def _interpolate_env_vars(config: Dict[str, Any]) -> None:
    """
    Recursively interpolate environment variables in configuration values
    Format: ${ENV_VAR} or ${ENV_VAR:default_value}
    """
    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, (dict, list)):
                _interpolate_env_vars(value)
            elif isinstance(value, str) and '${' in value:
                config[key] = _resolve_env_var(value)
    elif isinstance(config, list):
        for i, value in enumerate(config):
            if isinstance(value, (dict, list)):
                _interpolate_env_vars(value)
            elif isinstance(value, str) and '${' in value:
                config[i] = _resolve_env_var(value)
                
def _resolve_env_var(value: str) -> str:
    """
    Resolve environment variable references in a string
    
    Args:
        value: String containing environment variable references
        
    Returns:
        String with environment variables replaced with their values
    """
    # Handle ${VAR:default} format
    if ':' in value:
        env_var, default = value[2:-1].split(':', 1)
        return os.environ.get(env_var, default)
    
    # Handle ${VAR} format
    env_var = value[2:-1]
    env_value = os.environ.get(env_var)
    if env_value is None:
        raise ValueError(f"Environment variable not set: {env_var}")
    return env_value 