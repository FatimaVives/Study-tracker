# Study Tracker

A simple command-line application for tracking courses and assignments, built with Python and SQLite.

## Features

- Add and manage courses
- Add and manage assignments
- Track assignment grades
- Export reports to CSV and Excel formats
- Simple command-line interface

## Requirements

- Python 3.6+
- SQLite3 (included with Python)
- openpyxl (for Excel export)

## Installation

1. Clone or download this repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example settings file:
   ```bash
   copy config\settings.example.ini config\settings.ini
   ```

4. Initialize the database:
   ```bash
   python cli.py init
   ```

## Usage

### Initialize Database

```bash
python cli.py init
```

### Course Management

**Add a course:**
```bash
python cli.py add-course --name "Python Programming" --teacher "Dr. Smith" --credits 3
```

**List all courses:**
```bash
python cli.py list-courses
```

### Assignment Management

**Add an assignment:**
```bash
python cli.py add-assignment --course-id 1 --title "Homework 1" --due-date 2025-02-15
```

**Add an assignment with a grade:**
```bash
python cli.py add-assignment --course-id 1 --title "Homework 2" --due-date 2025-02-20 --grade 88.5
```

**List all assignments:**
```bash
python cli.py list-assignments
```

**List assignments for a specific course:**
```bash
python cli.py list-assignments --course-id 1
```

**Update an assignment grade:**
```bash
python cli.py update-grade --assignment-id 1 --grade 95.5
```

### Export Reports

**Export all data to CSV:**
```bash
python cli.py export --type full --format csv --output report.csv
```

**Export courses to Excel:**
```bash
python cli.py export --type courses --format excel --output courses.xlsx
```

**Export assignments to CSV:**
```bash
python cli.py export --type assignments --format csv --output assignments.csv
```

### Plotting

**Plot average grades per course (PNG):**
```bash
python cli.py plot-grades --output grade_plot.png
```

## Project Structure

```
study-tracker/
├── cli.py                          # Main CLI entry point
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── config/
│   └── settings.example.ini        # Example configuration file
├── database/
│   ├── schema.sql                  # Database schema
│   └── sample.db                   # SQLite database (created on init)
├── studytracker/
│   ├── __init__.py                 # Package initialization
│   ├── db.py                       # Database access layer
│   ├── course_service.py           # Course business logic
│   ├── assignment_service.py       # Assignment business logic
│   └── reports.py                  # Report generation
```

## Database Schema

### Courses Table
- `id` - Primary key
- `name` - Course name
- `teacher` - Teacher name
- `credits` - Number of credits

### Assignments Table
- `id` - Primary key
- `course_id` - Foreign key to courses
- `title` - Assignment title
- `due_date` - Due date (YYYY-MM-DD)
- `grade` - Grade (can be NULL)

## Configuration

Edit `config/settings.ini` to change the database path:

```ini
[database]
db_path = database/sample.db
```

## Example Workflow

```bash
# 1. Initialize the database
python cli.py init

# 2. Add some courses
python cli.py add-course --name "Data Structures" --teacher "Prof. Johnson" --credits 4
python cli.py add-course --name "Web Development" --teacher "Dr. Lee" --credits 3

# 3. View courses
python cli.py list-courses

# 4. Add assignments
python cli.py add-assignment --course-id 1 --title "Binary Trees Assignment" --due-date 2025-03-01
python cli.py add-assignment --course-id 2 --title "Build a Website" --due-date 2025-03-15

# 5. Update grades
python cli.py update-grade --assignment-id 1 --grade 92.0

# 6. Export a report
python cli.py export --type full --format excel --output my_studies.xlsx
```
## Virtual Environment

This project was developed using a Python virtual environment.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

## License

This is a school assignment project. Feel free to use and modify as needed for educational purposes.
