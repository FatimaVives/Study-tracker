from typing import List, Optional
from studytracker.db import Database
from datetime import datetime


class StudySessionService:
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_session(self, course_id: int, date: str, duration_minutes: int, 
                    assignment_id: Optional[int] = None, notes: Optional[str] = None) -> int:
        # Validate inputs
        if duration_minutes <= 0:
            raise ValueError("Duration must be a positive number of minutes")
        
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Check if course exists
        course_query = "SELECT id FROM courses WHERE id = ?"
        course = self.db.fetch_one(course_query, (course_id,))
        if not course:
            raise ValueError(f"Course with ID {course_id} does not exist")
        
        # Check if assignment exists (if provided)
        if assignment_id is not None:
            assignment_query = "SELECT id FROM assignments WHERE id = ?"
            assignment = self.db.fetch_one(assignment_query, (assignment_id,))
            if not assignment:
                raise ValueError(f"Assignment with ID {assignment_id} does not exist")
        
        query = """
            INSERT INTO study_sessions (course_id, assignment_id, date, duration_minutes, notes)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(query, (course_id, assignment_id, date, duration_minutes, notes))
        session_id = cursor.lastrowid
        print(f"Study session added successfully! ID: {session_id}")
        return session_id
    
    def get_all_sessions(self) -> List[dict]:
        query = """
            SELECT 
                s.id,
                s.course_id,
                c.name as course_name,
                s.assignment_id,
                a.title as assignment_title,
                s.date,
                s.duration_minutes,
                s.notes
            FROM study_sessions s
            JOIN courses c ON s.course_id = c.id
            LEFT JOIN assignments a ON s.assignment_id = a.id
            ORDER BY s.date DESC
        """
        rows = self.db.fetch_all(query)
        
        sessions = []
        for row in rows:
            sessions.append({
                'id': row['id'],
                'course_id': row['course_id'],
                'course_name': row['course_name'],
                'assignment_id': row['assignment_id'],
                'assignment_title': row['assignment_title'],
                'date': row['date'],
                'duration_minutes': row['duration_minutes'],
                'notes': row['notes']
            })
        
        return sessions
    
    def get_sessions_by_course(self, course_id: int) -> List[dict]:
        query = """
            SELECT 
                s.id,
                s.course_id,
                s.assignment_id,
                a.title as assignment_title,
                s.date,
                s.duration_minutes,
                s.notes
            FROM study_sessions s
            LEFT JOIN assignments a ON s.assignment_id = a.id
            WHERE s.course_id = ?
            ORDER BY s.date DESC
        """
        rows = self.db.fetch_all(query, (course_id,))
        
        sessions = []
        for row in rows:
            sessions.append({
                'id': row['id'],
                'course_id': row['course_id'],
                'assignment_id': row['assignment_id'],
                'assignment_title': row['assignment_title'],
                'date': row['date'],
                'duration_minutes': row['duration_minutes'],
                'notes': row['notes']
            })
        
        return sessions
    
    def get_study_summary_by_course(self) -> List[dict]:
        """Get total study time per course"""
        query = """
            SELECT 
                c.id,
                c.name,
                COUNT(s.id) as session_count,
                SUM(s.duration_minutes) as total_minutes,
                ROUND(SUM(s.duration_minutes) / 60.0, 2) as total_hours
            FROM courses c
            LEFT JOIN study_sessions s ON c.id = s.course_id
            GROUP BY c.id, c.name
            HAVING total_minutes > 0
            ORDER BY total_minutes DESC
        """
        rows = self.db.fetch_all(query)
        
        summaries = []
        for row in rows:
            summaries.append({
                'course_id': row['id'],
                'course_name': row['name'],
                'session_count': row['session_count'],
                'total_minutes': row['total_minutes'],
                'total_hours': row['total_hours']
            })
        
        return summaries
    
    def delete_session(self, session_id: int) -> bool:
        query = "DELETE FROM study_sessions WHERE id = ?"
        cursor = self.db.execute(query, (session_id,))
        
        if cursor.rowcount > 0:
            print(f"Study session {session_id} deleted successfully!")
            return True
        else:
            print(f"Study session {session_id} not found.")
            return False
