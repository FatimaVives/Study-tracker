from typing import List, Optional
from studytracker.db import Database


class CourseService:
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_course(self, name: str, teacher: str, credits: int) -> int:
        query = """
            INSERT INTO courses (name, teacher, credits)
            VALUES (?, ?, ?)
        """
        cursor = self.db.execute(query, (name, teacher, credits))
        course_id = cursor.lastrowid
        print(f"Course added successfully! ID: {course_id}")
        return course_id
    
    def get_all_courses(self) -> List[dict]:
        query = "SELECT * FROM courses ORDER BY name"
        rows = self.db.fetch_all(query)
        courses = []
        for row in rows:
            courses.append({
                'id': row['id'],
                'name': row['name'],
                'teacher': row['teacher'],
                'credits': row['credits']
            })
        
        return courses
    
    def get_course_by_id(self, course_id: int) -> Optional[dict]:
        query = "SELECT * FROM courses WHERE id = ?"
        row = self.db.fetch_one(query, (course_id,))
        
        if row:
            return {
                'id': row['id'],
                'name': row['name'],
                'teacher': row['teacher'],
                'credits': row['credits']
            }
        return None
    
    def delete_course(self, course_id: int) -> bool:
        query = "DELETE FROM courses WHERE id = ?"
        cursor = self.db.execute(query, (course_id,))
        
        if cursor.rowcount > 0:
            print(f"Course {course_id} deleted successfully!")
            return True
        else:
            print(f"Course {course_id} not found.")
            return False
