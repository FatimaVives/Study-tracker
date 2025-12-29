#!/usr/bin/env python3
"""
Study Tracker CLI
Command-line interface for managing courses and assignments.
"""

import argparse
import configparser
import sys
import os
from studytracker.db import Database
from studytracker.course_service import CourseService
from studytracker.assignment_service import AssignmentService
from studytracker.reports import ReportGenerator
from studytracker import plotting


def load_config():
    """
    Load configuration from settings.ini file.
    
    Returns:
        Database path from config file
    """
    config = configparser.ConfigParser()
    config_path = 'config/settings.ini'
    
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found!")
        print("Please copy config/settings.example.ini to config/settings.ini")
        sys.exit(1)
    
    config.read(config_path)
    return config['database']['db_path']


def init_database(args):
    """Initialize the database schema."""
    db_path = load_config()
    db = Database(db_path)
    db.connect()
    
    schema_path = 'database/schema.sql'
    if not os.path.exists(schema_path):
        print(f"Error: {schema_path} not found!")
        sys.exit(1)
    
    db.initialize_schema(schema_path)
    db.close()


def add_course(args):
    """Add a new course."""
    db_path = load_config()
    db = Database(db_path)
    db.connect()
    
    course_service = CourseService(db)
    course_service.add_course(args.name, args.teacher, args.credits)
    
    db.close()


def list_courses(args):
    """List all courses."""
    db_path = load_config()
    db = Database(db_path)
    db.connect()
    
    course_service = CourseService(db)
    courses = course_service.get_all_courses()
    
    if not courses:
        print("No courses found.")
    else:
        print("\n=== All Courses ===")
        for course in courses:
            print(f"ID: {course['id']}")
            print(f"  Name: {course['name']}")
            print(f"  Teacher: {course['teacher']}")
            print(f"  Credits: {course['credits']}")
            print()
    
    db.close()


def add_assignment(args):
    """Add a new assignment."""
    db_path = load_config()
    db = Database(db_path)
    db.connect()
    
    assignment_service = AssignmentService(db)
    grade = args.grade if args.grade is not None else None
    assignment_service.add_assignment(args.course_id, args.title, args.due_date, grade)
    
    db.close()


def list_assignments(args):
    """List all assignments."""
    db_path = load_config()
    db = Database(db_path)
    db.connect()
    
    assignment_service = AssignmentService(db)
    
    if args.course_id:
        assignments = assignment_service.get_assignments_by_course(args.course_id)
        print(f"\n=== Assignments for Course {args.course_id} ===")
    else:
        assignments = assignment_service.get_all_assignments()
        print("\n=== All Assignments ===")
    
    if not assignments:
        print("No assignments found.")
    else:
        for assignment in assignments:
            print(f"ID: {assignment['id']}")
            if 'course_name' in assignment:
                print(f"  Course: {assignment['course_name']}")
            print(f"  Title: {assignment['title']}")
            print(f"  Due Date: {assignment['due_date']}")
            grade = assignment['grade'] if assignment['grade'] is not None else 'Not graded'
            print(f"  Grade: {grade}")
            print()
    
    db.close()


def update_grade(args):
    """Update an assignment grade."""
    db_path = load_config()
    db = Database(db_path)
    db.connect()
    
    assignment_service = AssignmentService(db)
    assignment_service.update_grade(args.assignment_id, args.grade)
    
    db.close()


def export_report(args):
    """Export data to CSV or Excel."""
    db_path = load_config()
    db = Database(db_path)
    db.connect()
    
    report_gen = ReportGenerator(db)
    
    # Determine report type and format
    if args.type == 'courses':
        if args.format == 'csv':
            report_gen.export_courses_to_csv(args.output)
        else:
            report_gen.export_courses_to_excel(args.output)
    elif args.type == 'assignments':
        if args.format == 'csv':
            report_gen.export_assignments_to_csv(args.output)
        else:
            report_gen.export_assignments_to_excel(args.output)
    else:  # full
        if args.format == 'csv':
            report_gen.export_full_report_to_csv(args.output)
        else:
            report_gen.export_full_report_to_excel(args.output)
    
    db.close()


def plot_grades(args):
    """Create a matplotlib plot of average grades per course."""
    db_path = load_config()
    db = Database(db_path)
    db.connect()

    plotting.plot_average_grade_per_course(db, args.output)

    db.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Study Tracker - Manage your courses and assignments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize the database
  python cli.py init

  # Add a course
  python cli.py add-course --name "Python Programming" --teacher "Dr. Smith" --credits 3

  # List all courses
  python cli.py list-courses

  # Add an assignment
  python cli.py add-assignment --course-id 1 --title "Homework 1" --due-date 2025-02-15

  # Update a grade
  python cli.py update-grade --assignment-id 1 --grade 95.5

  # List all assignments
  python cli.py list-assignments

  # Export to CSV
  python cli.py export --type full --format csv --output report.csv

  # Export to Excel
  python cli.py export --type full --format excel --output report.xlsx
        """
    )
    
    subparsers = parser.add_subparsers(title='commands', dest='command', help='Available commands')
    
    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize the database schema')
    parser_init.set_defaults(func=init_database)
    
    # Add course command
    parser_add_course = subparsers.add_parser('add-course', help='Add a new course')
    parser_add_course.add_argument('--name', required=True, help='Course name')
    parser_add_course.add_argument('--teacher', required=True, help='Teacher name')
    parser_add_course.add_argument('--credits', type=int, required=True, help='Number of credits')
    parser_add_course.set_defaults(func=add_course)
    
    # List courses command
    parser_list_courses = subparsers.add_parser('list-courses', help='List all courses')
    parser_list_courses.set_defaults(func=list_courses)
    
    # Add assignment command
    parser_add_assignment = subparsers.add_parser('add-assignment', help='Add a new assignment')
    parser_add_assignment.add_argument('--course-id', type=int, required=True, help='Course ID')
    parser_add_assignment.add_argument('--title', required=True, help='Assignment title')
    parser_add_assignment.add_argument('--due-date', required=True, help='Due date (YYYY-MM-DD)')
    parser_add_assignment.add_argument('--grade', type=float, help='Grade (optional)')
    parser_add_assignment.set_defaults(func=add_assignment)
    
    # List assignments command
    parser_list_assignments = subparsers.add_parser('list-assignments', help='List assignments')
    parser_list_assignments.add_argument('--course-id', type=int, help='Filter by course ID')
    parser_list_assignments.set_defaults(func=list_assignments)
    
    # Update grade command
    parser_update_grade = subparsers.add_parser('update-grade', help='Update assignment grade')
    parser_update_grade.add_argument('--assignment-id', type=int, required=True, help='Assignment ID')
    parser_update_grade.add_argument('--grade', type=float, required=True, help='New grade')
    parser_update_grade.set_defaults(func=update_grade)
    
    # Export command
    parser_export = subparsers.add_parser('export', help='Export data to CSV or Excel')
    parser_export.add_argument('--type', choices=['courses', 'assignments', 'full'], 
                               default='full', help='Type of report')
    parser_export.add_argument('--format', choices=['csv', 'excel'], 
                               default='csv', help='Output format')
    parser_export.add_argument('--output', required=True, help='Output file path')
    parser_export.set_defaults(func=export_report)

    # Plot command
    parser_plot = subparsers.add_parser('plot-grades', help='Plot average grades per course')
    parser_plot.add_argument('--output', default='grade_plot.png', help='Output image file path')
    parser_plot.set_defaults(func=plot_grades)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate function
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
