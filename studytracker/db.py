"""
Database module for Study Tracker.
Provides a Database class to handle SQLite connections and operations.
"""

import sqlite3
from typing import List, Tuple, Optional


class Database:
    """
    A simple database wrapper for SQLite operations.
    Handles connection, queries, and transactions.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish a connection to the database."""
        self.connection = sqlite3.connect(self.db_path)
        # Enable foreign key support
        self.connection.execute("PRAGMA foreign_keys = ON")
        # Return rows as dictionaries for easier access
        self.connection.row_factory = sqlite3.Row
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """
        Execute a single SQL query.
        
        Args:
            query: SQL query string
            params: Parameters to bind to the query
            
        Returns:
            Cursor object with the results
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a query and fetch all results.
        
        Args:
            query: SQL query string
            params: Parameters to bind to the query
            
        Returns:
            List of row objects
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """
        Execute a query and fetch one result.
        
        Args:
            query: SQL query string
            params: Parameters to bind to the query
            
        Returns:
            Single row object or None
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def initialize_schema(self, schema_path: str):
        """
        Initialize the database schema from a SQL file.
        
        Args:
            schema_path: Path to the schema.sql file
        """
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        self.connection.executescript(schema_sql)
        self.connection.commit()
        print(f"Database schema initialized from {schema_path}")
