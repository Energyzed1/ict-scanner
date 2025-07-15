"""
Data source factory module
"""

from typing import Dict, Any
from .base import DataSource
from .interactive_brokers import IBDataSource

def get_data_source(config: Dict[str, Any]) -> DataSource:
    """
    Factory function to create a data source instance
    
    Args:
        config: Data source configuration
        
    Returns:
        DataSource instance
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = config.get("provider", "").lower()
    
    if provider == "interactive_brokers":
        return IBDataSource(config)
    else:
        raise ValueError(f"Unsupported data provider: {provider}")
        
__all__ = ["get_data_source", "DataSource", "IBDataSource"] 