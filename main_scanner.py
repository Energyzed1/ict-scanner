#!/usr/bin/env python3
"""
ICT PD Array Scanner - Main Entry Point
Monitors MES and MNQ futures for ICT price delivery array patterns
"""

import asyncio
import argparse
import yaml
from pathlib import Path
from loguru import logger
from typing import Dict, List, Optional

from src.config import load_config
from src.data_sources import get_data_source
from src.patterns import PatternManager
from src.alerts import AlertManager
from src.database import DatabaseManager
from src.utils.logging import setup_logging

class Scanner:
    def __init__(self, config_path: str):
        """Initialize the scanner with configuration"""
        self.config = load_config(config_path)
        self.setup_components()
        
    def setup_components(self):
        """Initialize all system components"""
        # Setup logging
        setup_logging(self.config["logging"])
        
        # Initialize database
        env = "production" if self.config.get("environment") == "production" else "development"
        self.db = DatabaseManager(self.config["database"][env])
        
        # Initialize data source
        self.data_source = get_data_source(self.config["data_source"])
        
        # Initialize pattern detection
        self.pattern_manager = PatternManager(self.config["patterns"])
        
        # Initialize alerting system
        self.alert_manager = AlertManager(self.config["alerts"])
        
    async def start(self, instruments: Optional[List[str]] = None, 
                   patterns: Optional[List[str]] = None,
                   timeframes: Optional[List[str]] = None):
        """Start the scanner with optional filters"""
        try:
            # Filter instruments if specified
            if instruments:
                configured_instruments = [
                    instr for instr in self.config["instruments"]
                    if instr["symbol"] in instruments
                ]
            else:
                configured_instruments = self.config["instruments"]
                
            # Connect to data source
            await self.data_source.connect()
            
            # Subscribe to market data
            for instrument in configured_instruments:
                symbol = instrument["symbol"]
                tfs = timeframes or instrument["timeframes"]
                
                logger.info(f"Subscribing to {symbol} on timeframes: {tfs}")
                await self.data_source.subscribe(symbol, tfs)
                
            # Start pattern detection
            await self.pattern_manager.start(
                instruments=configured_instruments,
                patterns=patterns
            )
            
            # Keep the scanner running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down scanner...")
        except Exception as e:
            logger.error(f"Error in scanner: {str(e)}")
            raise
        finally:
            await self.cleanup()
            
    async def cleanup(self):
        """Cleanup resources"""
        await self.data_source.disconnect()
        await self.db.close()
        await self.alert_manager.close()

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="ICT PD Array Scanner")
    parser.add_argument("--config", type=str, default="config.yaml",
                       help="Path to configuration file")
    parser.add_argument("--instruments", type=str, nargs="+",
                       help="Specific instruments to monitor (e.g. MES MNQ)")
    parser.add_argument("--patterns", type=str, nargs="+",
                       help="Specific patterns to detect (e.g. FVG OrderBlock)")
    parser.add_argument("--timeframes", type=str, nargs="+",
                       help="Specific timeframes to monitor (e.g. 5m 15m)")
    return parser.parse_args()

async def main():
    """Main entry point"""
    args = parse_args()
    
    # Ensure config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        if Path("config.template.yaml").exists():
            logger.error(
                "Configuration file not found. Please copy config.template.yaml "
                "to config.yaml and update with your settings."
            )
        else:
            logger.error("Configuration file not found.")
        return 1
        
    # Start the scanner
    scanner = Scanner(str(config_path))
    await scanner.start(
        instruments=args.instruments,
        patterns=args.patterns,
        timeframes=args.timeframes
    )
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 