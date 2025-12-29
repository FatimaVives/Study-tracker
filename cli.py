#!/usr/bin/env python3
import argparse
import configparser
import sys
import os
from studytracker.db import Database
from studytracker.course_service import CourseService
from studytracker.assignment_service import AssignmentService
from studytracker.study_session_service import StudySessionService
from studytracker.reports import ReportGenerator
from studytracker import plotting


def load_config():
    config = configparser.ConfigParser()
    config_path = 'config/settings.ini'
    
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found!")
        print("Please copy config/settings.example.ini to config/settings.ini")
        sys.exit(1)
    
    config.read(config_path)
    return config['database']['db_path']


def init_database(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()
        
        schema_path = 'database/schema.sql'
        if not os.path.exists(schema_path):
            print(f"Error: {schema_path} not found!")
            sys.exit(1)
        
        db.initialize_schema(schema_path)
        db.close()
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


def add_course(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()
        
        course_service = CourseService(db)
        course_service.add_course(args.name, args.teacher, args.credits)
        
        db.close()
    except ValueError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error adding course: {e}")
        sys.exit(1)


def list_courses(args):
    try:
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
    except Exception as e:
        print(f"Error listing courses: {e}")
        sys.exit(1)


def add_assignment(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()
        
        assignment_service = AssignmentService(db)
        grade = args.grade if args.grade is not None else None
        assignment_service.add_assignment(args.course_id, args.title, args.due_date, grade)
        
        db.close()
    except ValueError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error adding assignment: {e}")
        sys.exit(1)


def list_assignments(args):
    try:
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
    except Exception as e:
        print(f"Error listing assignments: {e}")
        sys.exit(1)


def update_grade(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()
        
        assignment_service = AssignmentService(db)
        assignment_service.update_grade(args.assignment_id, args.grade)
        
        db.close()
    except ValueError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error updating grade: {e}")
        sys.exit(1)


def export_report(args):
    try:
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
    except Exception as e:
        print(f"Error exporting report: {e}")
        sys.exit(1)


def export_report_pandas(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()

        report_gen = ReportGenerator(db)
        report_gen.export_full_report_with_pandas(args.output, args.format)

        db.close()
    except Exception as e:
        print(f"Error exporting report with pandas: {e}")
        sys.exit(1)


def final_grade(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()

        report_gen = ReportGenerator(db)
        grade = report_gen.calculate_weighted_final_grade()
        if grade == 0.0:
            print("No graded assignments available to calculate final grade.")
        else:
            print(f"Weighted final grade: {grade}")

        db.close()
    except Exception as e:
        print(f"Error calculating final grade: {e}")
        sys.exit(1)


def plot_grades(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()

        plotting.plot_average_grade_per_course(db, args.output)

        db.close()
    except Exception as e:
        print(f"Error plotting grades: {e}")
        sys.exit(1)


def plot_timeline(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()

        plotting.plot_assignment_timeline(db, args.output)

        db.close()
    except Exception as e:
        print(f"Error plotting timeline: {e}")
        sys.exit(1)


def add_session(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()
        
        session_service = StudySessionService(db)
        session_service.add_session(
            args.course_id, 
            args.date, 
            args.duration, 
            args.assignment_id if hasattr(args, 'assignment_id') else None,
            args.notes if hasattr(args, 'notes') else None
        )
        
        db.close()
    except ValueError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error adding study session: {e}")
        sys.exit(1)


def list_sessions(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()
        
        session_service = StudySessionService(db)
        
        if args.course_id:
            sessions = session_service.get_sessions_by_course(args.course_id)
            print(f"\n=== Study Sessions for Course {args.course_id} ===")
        else:
            sessions = session_service.get_all_sessions()
            print("\n=== All Study Sessions ===")
        
        if not sessions:
            print("No study sessions found.")
        else:
            for session in sessions:
                print(f"ID: {session['id']}")
                if 'course_name' in session:
                    print(f"  Course: {session['course_name']}")
                if session['assignment_title']:
                    print(f"  Assignment: {session['assignment_title']}")
                print(f"  Date: {session['date']}")
                hours = session['duration_minutes'] // 60
                minutes = session['duration_minutes'] % 60
                print(f"  Duration: {hours}h {minutes}m")
                if session['notes']:
                    print(f"  Notes: {session['notes']}")
                print()
        
        db.close()
    except Exception as e:
        print(f"Error listing study sessions: {e}")
        sys.exit(1)


def session_report(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()
        
        session_service = StudySessionService(db)
        summaries = session_service.get_study_summary_by_course()
        
        if not summaries:
            print("No study sessions recorded yet.")
        else:
            print("\n=== Study Time Summary by Course ===")
            print()
            total_hours = 0
            for summary in summaries:
                print(f"{summary['course_name']}")
                print(f"  Sessions: {summary['session_count']}")
                print(f"  Total Time: {summary['total_hours']} hours")
                print()
                total_hours += summary['total_hours']
            
            print(f"Total Study Time: {total_hours} hours")
        
        db.close()
    except Exception as e:
        print(f"Error generating session report: {e}")
        sys.exit(1)


def plot_study_time(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()

        plotting.plot_study_time_per_course(db, args.output)

        db.close()
    except Exception as e:
        print(f"Error plotting study time: {e}")
        sys.exit(1)


def plot_efficiency(args):
    try:
        db_path = load_config()
        db = Database(db_path)
        db.connect()

        plotting.plot_study_efficiency(db, args.output)

        db.close()
    except Exception as e:
        print(f"Error plotting study efficiency: {e}")
        sys.exit(1)


def main():
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

    # Export using pandas
    parser_export_pd = subparsers.add_parser('export-pandas', help='Export full report using pandas')
    parser_export_pd.add_argument('--format', choices=['csv', 'excel'], default='csv', help='Output format')
    parser_export_pd.add_argument('--output', required=True, help='Output file path')
    parser_export_pd.set_defaults(func=export_report_pandas)

    # Final grade command
    parser_final = subparsers.add_parser('final-grade', help='Calculate weighted final grade across courses')
    parser_final.set_defaults(func=final_grade)

    # Plot command
    parser_plot = subparsers.add_parser('plot-grades', help='Plot average grades per course')
    parser_plot.add_argument('--output', default='grade_plot.png', help='Output image file path')
    parser_plot.set_defaults(func=plot_grades)

    # Plot timeline command
    parser_plot_timeline = subparsers.add_parser('plot-timeline', help='Plot assignment timeline and workload')
    parser_plot_timeline.add_argument('--output', default='assignment_timeline.png', help='Output image file path')
    parser_plot_timeline.set_defaults(func=plot_timeline)
    
    # Add study session command
    parser_add_session = subparsers.add_parser('add-session', help='Add a study session')
    parser_add_session.add_argument('--course-id', type=int, required=True, help='Course ID')
    parser_add_session.add_argument('--date', required=True, help='Study date (YYYY-MM-DD)')
    parser_add_session.add_argument('--duration', type=int, required=True, help='Duration in minutes')
    parser_add_session.add_argument('--assignment-id', type=int, help='Related assignment ID (optional)')
    parser_add_session.add_argument('--notes', help='Session notes (optional)')
    parser_add_session.set_defaults(func=add_session)
    
    # List study sessions command
    parser_list_sessions = subparsers.add_parser('list-sessions', help='List study sessions')
    parser_list_sessions.add_argument('--course-id', type=int, help='Filter by course ID')
    parser_list_sessions.set_defaults(func=list_sessions)
    
    # Study session report command
    parser_session_report = subparsers.add_parser('session-report', help='Show study time summary by course')
    parser_session_report.set_defaults(func=session_report)
    
    # Plot study time command
    parser_plot_study = subparsers.add_parser('plot-study-time', help='Plot study time per course')
    parser_plot_study.add_argument('--output', default='study_time_plot.png', help='Output image file path')
    parser_plot_study.set_defaults(func=plot_study_time)
    
    # Plot study efficiency command
    parser_plot_efficiency = subparsers.add_parser('plot-study-efficiency', help='Plot study time vs grades to identify areas needing more study')
    parser_plot_efficiency.add_argument('--output', default='study_efficiency_plot.png', help='Output image file path')
    parser_plot_efficiency.set_defaults(func=plot_efficiency)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate function
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
