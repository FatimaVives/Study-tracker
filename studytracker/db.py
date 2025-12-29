import sqlite3
from typing import List, Tuple, Optional


class Database:
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        # Enable foreign key support
        self.connection.execute("PRAGMA foreign_keys = ON")
        # Return rows as dictionaries for easier access
        self.connection.row_factory = sqlite3.Row
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def initialize_schema(self, schema_path: str):
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        self.connection.executescript(schema_sql)
        self.connection.commit()
        print(f"Database schema initialized from {schema_path}")
