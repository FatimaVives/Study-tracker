import csv
from typing import List, Dict
from studytracker.db import Database

try:
    from openpyxl import Workbook
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class ReportGenerator:
    
    def __init__(self, db: Database):
        self.db = db
    
    def export_courses_to_csv(self, filename: str):
        query = "SELECT id, name, teacher, credits FROM courses ORDER BY name"
        rows = self.db.fetch_all(query)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Course Name', 'Teacher', 'Credits'])
            for row in rows:
                writer.writerow([row['id'], row['name'], row['teacher'], row['credits']])
        
        print(f"Courses exported to {filename}")
    
    def export_assignments_to_csv(self, filename: str):
        query = """
            SELECT 
                a.id,
                c.name as course_name,
                a.title,
                a.due_date,
                a.grade
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            ORDER BY a.due_date
        """
        rows = self.db.fetch_all(query)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Course', 'Assignment', 'Due Date', 'Grade'])
            for row in rows:
                grade = row['grade'] if row['grade'] is not None else 'Not graded'
                writer.writerow([row['id'], row['course_name'], row['title'], 
                               row['due_date'], grade])
        
        print(f"Assignments exported to {filename}")
    
    def export_full_report_to_csv(self, filename: str):
        query = """
            SELECT 
                c.name as course_name,
                c.teacher,
                c.credits,
                a.title as assignment_title,
                a.due_date,
                a.grade
            FROM courses c
            LEFT JOIN assignments a ON c.id = a.course_id
            ORDER BY c.name, a.due_date
        """
        rows = self.db.fetch_all(query)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Course', 'Teacher', 'Credits', 'Assignment', 'Due Date', 'Grade'])
            for row in rows:
                grade = row['grade'] if row['grade'] is not None else 'Not graded'
                assignment = row['assignment_title'] if row['assignment_title'] else 'No assignments'
                due_date = row['due_date'] if row['due_date'] else ''
                writer.writerow([row['course_name'], row['teacher'], row['credits'],
                               assignment, due_date, grade])
        
        print(f"Full report exported to {filename}")
    
    def export_courses_to_excel(self, filename: str):
        if not EXCEL_AVAILABLE:
            print("Error: openpyxl library is not installed. Run: pip install openpyxl")
            return
        
        query = "SELECT id, name, teacher, credits FROM courses ORDER BY name"
        rows = self.db.fetch_all(query)
        
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Courses"
        
        ws.append(['ID', 'Course Name', 'Teacher', 'Credits'])
        for row in rows:
            ws.append([row['id'], row['name'], row['teacher'], row['credits']])
        
        wb.save(filename)
        print(f"Courses exported to {filename}")
    
    def export_assignments_to_excel(self, filename: str):
        if not EXCEL_AVAILABLE:
            print("Error: openpyxl library is not installed. Run: pip install openpyxl")
            return
        
        query = """
            SELECT 
                a.id,
                c.name as course_name,
                a.title,
                a.due_date,
                a.grade
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            ORDER BY a.due_date
        """
        rows = self.db.fetch_all(query)
        
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Assignments"
        
        # Write header
        ws.append(['ID', 'Course', 'Assignment', 'Due Date', 'Grade'])
        
        # Write data
        for row in rows:
            grade = row['grade'] if row['grade'] is not None else 'Not graded'
            ws.append([row['id'], row['course_name'], row['title'], 
                      row['due_date'], grade])
        
        # Save the workbook
        wb.save(filename)
        print(f"Assignments exported to {filename}")
    
    def export_full_report_to_excel(self, filename: str):
        if not EXCEL_AVAILABLE:
            print("Error: openpyxl library is not installed. Run: pip install openpyxl")
            return
        
        # Create workbook
        wb = Workbook()
        
        # Sheet 1: Courses
        ws_courses = wb.active
        ws_courses.title = "Courses"
        courses_query = "SELECT id, name, teacher, credits FROM courses ORDER BY name"
        courses = self.db.fetch_all(courses_query)
        ws_courses.append(['ID', 'Course Name', 'Teacher', 'Credits'])
        for row in courses:
            ws_courses.append([row['id'], row['name'], row['teacher'], row['credits']])
        
        # Sheet 2: Assignments
        ws_assignments = wb.create_sheet("Assignments")
        assignments_query = """
            SELECT 
                a.id,
                c.name as course_name,
                a.title,
                a.due_date,
                a.grade
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            ORDER BY a.due_date
        """
        assignments = self.db.fetch_all(assignments_query)
        ws_assignments.append(['ID', 'Course', 'Assignment', 'Due Date', 'Grade'])
        for row in assignments:
            grade = row['grade'] if row['grade'] is not None else 'Not graded'
            ws_assignments.append([row['id'], row['course_name'], row['title'],
                                  row['due_date'], grade])
        
        # Save the workbook
        wb.save(filename)
        print(f"Full report exported to {filename}")
