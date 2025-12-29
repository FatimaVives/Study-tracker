from typing import List, Optional
from studytracker.db import Database


class AssignmentService:
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_assignment(self, course_id: int, title: str, due_date: str, grade: Optional[float] = None) -> int:
        query = """
            INSERT INTO assignments (course_id, title, due_date, grade)
            VALUES (?, ?, ?, ?)
        """
        cursor = self.db.execute(query, (course_id, title, due_date, grade))
        assignment_id = cursor.lastrowid
        print(f"Assignment added successfully! ID: {assignment_id}")
        return assignment_id
    
    def update_grade(self, assignment_id: int, grade: float) -> bool:
        query = "UPDATE assignments SET grade = ? WHERE id = ?"
        cursor = self.db.execute(query, (grade, assignment_id))
        
        if cursor.rowcount > 0:
            print(f"Assignment {assignment_id} grade updated to {grade}")
            return True
        else:
            print(f"Assignment {assignment_id} not found.")
            return False
    
    def get_all_assignments(self) -> List[dict]:
        query = """
            SELECT 
                a.id,
                a.course_id,
                c.name as course_name,
                a.title,
                a.due_date,
                a.grade
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            ORDER BY a.due_date
        """
        rows = self.db.fetch_all(query)
        
        assignments = []
        for row in rows:
            assignments.append({
                'id': row['id'],
                'course_id': row['course_id'],
                'course_name': row['course_name'],
                'title': row['title'],
                'due_date': row['due_date'],
                'grade': row['grade']
            })
        
        return assignments
    
    def get_assignments_by_course(self, course_id: int) -> List[dict]:
        query = """
            SELECT id, course_id, title, due_date, grade
            FROM assignments
            WHERE course_id = ?
            ORDER BY due_date
        """
        rows = self.db.fetch_all(query, (course_id,))
        
        assignments = []
        for row in rows:
            assignments.append({
                'id': row['id'],
                'course_id': row['course_id'],
                'title': row['title'],
                'due_date': row['due_date'],
                'grade': row['grade']
            })
        
        return assignments
    
    def get_assignment_by_id(self, assignment_id: int) -> Optional[dict]:
        query = """
            SELECT 
                a.id,
                a.course_id,
                c.name as course_name,
                a.title,
                a.due_date,
                a.grade
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            WHERE a.id = ?
        """
        row = self.db.fetch_one(query, (assignment_id,))
        
        if row:
            return {
                'id': row['id'],
                'course_id': row['course_id'],
                'course_name': row['course_name'],
                'title': row['title'],
                'due_date': row['due_date'],
                'grade': row['grade']
            }
        return None
