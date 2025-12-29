import sqlite3
from typing import List, Tuple, Optional


class Database:
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign key support
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Return rows as dictionaries for easier access
            self.connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to connect to database: {e}")
    
    def close(self):
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except sqlite3.Error as e:
                print(f"Warning: Error closing database connection: {e}")
    
    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Database integrity error: {e}")
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {e}")
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database query error: {e}")
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database query error: {e}")
    
    def initialize_schema(self, schema_path: str):
        try:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute the schema
            self.connection.executescript(schema_sql)
            self.connection.commit()
            print(f"Database schema initialized from {schema_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to initialize schema: {e}")
