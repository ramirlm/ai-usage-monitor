#!/usr/bin/env python3
"""Database module for AI Usage Monitor."""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class Database:
    """Handles all database operations for AI usage monitoring."""
    
    def __init__(self, db_path: str = "ai-usage.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def init_schema(self):
        """Initialize database schema with all required tables."""
        cursor = self.conn.cursor()
        
        # Usage snapshots table - stores individual usage records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                service TEXT NOT NULL,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                cost REAL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily summaries table - aggregated daily data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                service TEXT NOT NULL,
                model TEXT,
                total_input_tokens INTEGER,
                total_output_tokens INTEGER,
                total_tokens INTEGER,
                total_cost REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, service, model)
            )
        ''')
        
        # Alerts table - stores alert history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Budget settings table - stores budget configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT,
                monthly_budget REAL NOT NULL,
                alert_threshold REAL DEFAULT 0.8,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service)
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp 
            ON usage_snapshots(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_snapshots_service 
            ON usage_snapshots(service)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_summaries_date 
            ON daily_summaries(date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
            ON alerts(timestamp)
        ''')
        
        self.conn.commit()
        
    def add_usage_snapshot(self, service: str, model: Optional[str], 
                          input_tokens: int, output_tokens: int, 
                          cost: float, metadata: Optional[str] = None) -> int:
        """Add a usage snapshot record.
        
        Args:
            service: Name of the AI service
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Cost in dollars
            metadata: Optional JSON metadata
            
        Returns:
            ID of inserted record
        """
        cursor = self.conn.cursor()
        total_tokens = input_tokens + output_tokens
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO usage_snapshots 
            (timestamp, service, model, input_tokens, output_tokens, total_tokens, cost, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, service, model, input_tokens, output_tokens, total_tokens, cost, metadata))
        
        self.conn.commit()
        return cursor.lastrowid
        
    def update_daily_summary(self, date: str, service: str, model: Optional[str],
                            input_tokens: int, output_tokens: int, cost: float):
        """Update or insert daily summary.
        
        Args:
            date: Date in YYYY-MM-DD format
            service: Name of the AI service
            model: Model name
            input_tokens: Input tokens to add
            output_tokens: Output tokens to add
            cost: Cost to add
        """
        cursor = self.conn.cursor()
        total_tokens = input_tokens + output_tokens
        
        cursor.execute('''
            INSERT INTO daily_summaries 
            (date, service, model, total_input_tokens, total_output_tokens, total_tokens, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date, service, model) DO UPDATE SET
                total_input_tokens = total_input_tokens + excluded.total_input_tokens,
                total_output_tokens = total_output_tokens + excluded.total_output_tokens,
                total_tokens = total_tokens + excluded.total_tokens,
                total_cost = total_cost + excluded.total_cost
        ''', (date, service, model, input_tokens, output_tokens, total_tokens, cost))
        
        self.conn.commit()
        
    def add_alert(self, alert_type: str, severity: str, message: str, 
                  details: Optional[str] = None) -> int:
        """Add an alert record.
        
        Args:
            alert_type: Type of alert (budget_threshold, anomaly, etc.)
            severity: Alert severity (info, warning, error, critical)
            message: Alert message
            details: Optional detailed information
            
        Returns:
            ID of inserted record
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO alerts (timestamp, type, severity, message, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, alert_type, severity, message, details))
        
        self.conn.commit()
        return cursor.lastrowid
        
    def get_monthly_cost(self, year: int, month: int, service: Optional[str] = None) -> float:
        """Get total cost for a specific month.
        
        Args:
            year: Year
            month: Month (1-12)
            service: Optional service filter
            
        Returns:
            Total cost
        """
        cursor = self.conn.cursor()
        date_start = f"{year}-{month:02d}-01"
        
        # Calculate last day of month
        if month == 12:
            date_end = f"{year + 1}-01-01"
        else:
            date_end = f"{year}-{month + 1:02d}-01"
        
        if service:
            cursor.execute('''
                SELECT COALESCE(SUM(cost), 0) as total
                FROM usage_snapshots
                WHERE timestamp >= ? AND timestamp < ? AND service = ?
            ''', (date_start, date_end, service))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(cost), 0) as total
                FROM usage_snapshots
                WHERE timestamp >= ? AND timestamp < ?
            ''', (date_start, date_end))
        
        result = cursor.fetchone()
        return result['total'] if result else 0.0
        
    def get_service_breakdown(self, year: int, month: int) -> List[Dict]:
        """Get cost breakdown by service for a month.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            List of service cost breakdowns
        """
        cursor = self.conn.cursor()
        date_start = f"{year}-{month:02d}-01"
        
        if month == 12:
            date_end = f"{year + 1}-01-01"
        else:
            date_end = f"{year}-{month + 1:02d}-01"
        
        cursor.execute('''
            SELECT 
                service,
                COALESCE(SUM(cost), 0) as total_cost,
                COALESCE(SUM(total_tokens), 0) as total_tokens,
                COALESCE(SUM(input_tokens), 0) as input_tokens,
                COALESCE(SUM(output_tokens), 0) as output_tokens
            FROM usage_snapshots
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY service
            ORDER BY total_cost DESC
        ''', (date_start, date_end))
        
        return [dict(row) for row in cursor.fetchall()]
        
    def get_budget(self, service: Optional[str] = None) -> Optional[Dict]:
        """Get budget settings.
        
        Args:
            service: Optional service name (None for global budget)
            
        Returns:
            Budget settings dict or None
        """
        cursor = self.conn.cursor()
        
        if service:
            cursor.execute('''
                SELECT * FROM budget_settings WHERE service = ?
            ''', (service,))
        else:
            cursor.execute('''
                SELECT * FROM budget_settings WHERE service IS NULL
            ''')
        
        result = cursor.fetchone()
        return dict(result) if result else None
        
    def set_budget(self, monthly_budget: float, service: Optional[str] = None, 
                   alert_threshold: float = 0.8):
        """Set budget for a service or global.
        
        Args:
            monthly_budget: Monthly budget in dollars
            service: Optional service name (None for global)
            alert_threshold: Threshold percentage for alerts (0.0-1.0)
        """
        cursor = self.conn.cursor()
        updated_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO budget_settings (service, monthly_budget, alert_threshold, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(service) DO UPDATE SET
                monthly_budget = excluded.monthly_budget,
                alert_threshold = excluded.alert_threshold,
                updated_at = excluded.updated_at
        ''', (service, monthly_budget, alert_threshold, updated_at))
        
        self.conn.commit()
        
    def get_recent_alerts(self, limit: int = 10, unacknowledged_only: bool = False) -> List[Dict]:
        """Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            unacknowledged_only: Only return unacknowledged alerts
            
        Returns:
            List of alert dicts
        """
        cursor = self.conn.cursor()
        
        if unacknowledged_only:
            cursor.execute('''
                SELECT * FROM alerts 
                WHERE acknowledged = 0
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT * FROM alerts 
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
        
    def acknowledge_alert(self, alert_id: int):
        """Mark an alert as acknowledged.
        
        Args:
            alert_id: ID of the alert to acknowledge
        """
        cursor = self.conn.cursor()
        acknowledged_at = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE alerts 
            SET acknowledged = 1, acknowledged_at = ?
            WHERE id = ?
        ''', (acknowledged_at, alert_id))
        
        self.conn.commit()
        
    def get_daily_costs(self, days: int = 30) -> List[Dict]:
        """Get daily cost data for the last N days.
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of daily cost dicts
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                date,
                SUM(total_cost) as total_cost
            FROM daily_summaries
            WHERE date >= date('now', '-' || ? || ' days')
            GROUP BY date
            ORDER BY date ASC
        ''', (days,))
        
        return [dict(row) for row in cursor.fetchall()]


if __name__ == '__main__':
    # Initialize database when run directly
    db = Database()
    db.connect()
    db.init_schema()
    print("Database initialized successfully!")
    db.close()
