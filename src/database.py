"""
Database management for the ICT PD Array Scanner
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize database manager with configuration"""
        self.config = config
        self.db_type = config.get("type", "sqlite")
        self.connection = None
        
    async def connect(self) -> None:
        """Connect to the database"""
        try:
            if self.db_type == "sqlite":
                await self._connect_sqlite()
            elif self.db_type == "postgresql":
                await self._connect_postgresql()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
                
            logger.info(f"Connected to {self.db_type} database")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
            
    async def _connect_sqlite(self) -> None:
        """Connect to SQLite database"""
        import aiosqlite
        
        db_path = self.config.get("path", "data/scanner.db")
        self.connection = await aiosqlite.connect(db_path)
        
        # Create tables if they don't exist
        await self._create_tables()
        
    async def _connect_postgresql(self) -> None:
        """Connect to PostgreSQL database"""
        # Implementation for PostgreSQL connection
        # This would use asyncpg or similar
        pass
        
    async def _create_tables(self) -> None:
        """Create database tables if they don't exist"""
        if not self.connection:
            return
            
        # Create patterns table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                direction TEXT NOT NULL,
                mean_threshold REAL NOT NULL,
                upper_bound REAL NOT NULL,
                lower_bound REAL NOT NULL,
                status TEXT NOT NULL,
                confidence REAL NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create alerts table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                message TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pattern_id) REFERENCES patterns (pattern_id)
            )
        """)
        
        await self.connection.commit()
        
    async def save_pattern(self, pattern_data: Dict[str, Any]) -> bool:
        """Save pattern to database"""
        try:
            if not self.connection:
                return False
                
            await self.connection.execute("""
                INSERT OR REPLACE INTO patterns 
                (pattern_id, symbol, timeframe, pattern_type, direction, 
                 mean_threshold, upper_bound, lower_bound, status, confidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_data["pattern_id"],
                pattern_data["symbol"],
                pattern_data["timeframe"],
                pattern_data["pattern_type"],
                pattern_data["direction"],
                pattern_data["mean_threshold"],
                pattern_data["upper_bound"],
                pattern_data["lower_bound"],
                pattern_data["status"],
                pattern_data["confidence"],
                str(pattern_data.get("metadata", ""))
            ))
            
            await self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save pattern: {str(e)}")
            return False
            
    async def get_patterns(self, symbol: Optional[str] = None, 
                          pattern_type: Optional[str] = None) -> list:
        """Get patterns from database"""
        try:
            if not self.connection:
                return []
                
            query = "SELECT * FROM patterns WHERE 1=1"
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
                
            if pattern_type:
                query += " AND pattern_type = ?"
                params.append(pattern_type)
                
            query += " ORDER BY created_at DESC"
            
            cursor = await self.connection.execute(query, params)
            rows = await cursor.fetchall()
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in rows]
                   
        except Exception as e:
            logger.error(f"Failed to get patterns: {str(e)}")
            return []
            
    async def close(self) -> None:
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            logger.info("Database connection closed") 