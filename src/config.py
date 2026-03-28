"""
HorseClaw Configuration Module
HorseClaw 配置模块

Configuration management for HorseClaw.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


DEFAULT_CONFIG = {
    "language": "en",
    "state_file": "horseclaw_state.json",
    "auto_save": True,
    "log_level": "INFO",
    "pricing": {
        "claude_tokens_per_dollar": 20000,
        "kimi_tokens_per_dollar": 40000
    },
    "allocation": {
        "reserve_percent": 0.10,
        "max_allocation_percent": 0.30,
        "max_allocation_high_priority": 0.50
    },
    "limits": {
        "max_tokens_per_request": 10000000,
        "min_tokens_per_request": 100
    }
}


class Config:
    """Configuration manager for HorseClaw."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file (JSON)
        """
        self._config = DEFAULT_CONFIG.copy()
        self._config_path = config_path
        
        # Load from file if provided
        if config_path and Path(config_path).exists():
            self.load(config_path)
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "HORSECLAW_LANGUAGE": ("language", str),
            "HORSECLAW_STATE_FILE": ("state_file", str),
            "HORSECLAW_AUTO_SAVE": ("auto_save", lambda x: x.lower() == "true"),
            "HORSECLAW_LOG_LEVEL": ("log_level", str),
        }
        
        for env_var, (key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._config[key] = converter(value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def load(self, path: str):
        """Load configuration from file."""
        with open(path, 'r') as f:
            loaded = json.load(f)
            self._config.update(loaded)
        self._config_path = path
    
    def save(self, path: Optional[str] = None):
        """Save configuration to file."""
        save_path = path or self._config_path
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(self._config, f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return self._config.copy()
    
    @property
    def language(self) -> str:
        return self._config["language"]
    
    @property
    def state_file(self) -> str:
        return self._config["state_file"]
    
    @property
    def auto_save(self) -> bool:
        return self._config["auto_save"]
