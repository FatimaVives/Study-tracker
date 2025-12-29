from typing import Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

try:
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from studytracker.db import Database


def plot_average_grade_per_course(db: Database, filename: str) -> Optional[str]:
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib is not installed. Run: pip install matplotlib")
        return None

    query = """
        SELECT c.name AS course_name,
               AVG(a.grade) AS avg_grade,
               COUNT(a.id) AS graded_count
        FROM courses c
        LEFT JOIN assignments a ON a.course_id = c.id
        WHERE a.grade IS NOT NULL
        GROUP BY c.id
        HAVING graded_count > 0
        ORDER BY avg_grade DESC
    """

    rows = db.fetch_all(query)
    if not rows:
        print("No graded assignments found to plot.")
        return None

    course_names = [row["course_name"] for row in rows]
    avg_grades = [row["avg_grade"] for row in rows]
    counts = [row["graded_count"] for row in rows]
    max_count = max(counts)
    colors = [count / max_count for count in counts]

    plt.figure(figsize=(8, 4.5))
    bars = plt.bar(course_names, avg_grades, color=plt.cm.Blues(colors))
    plt.title("Average Grade per Course")
    plt.ylabel("Average Grade")
    plt.ylim(0, 100)
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    for bar, avg, count in zip(bars, avg_grades, counts):
        plt.text(bar.get_x() + bar.get_width() / 2,
                 avg + 1.0,
                 f"{avg:.1f}\n({count} graded)",
                 ha="center",
                 va="bottom",
                 fontsize=8)

    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()
    print(f"Plot saved to {filename}")
    return filename


def plot_assignment_timeline(db: Database, filename: str) -> Optional[str]:

    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib is not installed. Run: pip install matplotlib")
        return None
    
    query = """
        SELECT 
            c.name AS course_name,
            a.title,
            a.due_date,
            a.grade,
            c.id AS course_id
        FROM assignments a
        JOIN courses c ON a.course_id = c.id
        ORDER BY a.due_date ASC
    """

    rows = db.fetch_all(query)
    if not rows:
        print("No assignments found to plot.")
        return None

    assignments = []
    for row in rows:
        due_date = datetime.strptime(row["due_date"], "%Y-%m-%d")
        assignments.append({
            'date': due_date,
            'title': row["title"],
            'course': row["course_name"],
            'grade': row["grade"],
            'course_id': row["course_id"]
        })

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    dates = [a['date'] for a in assignments]
    grades = [a['grade'] if a['grade'] is not None else 0 for a in assignments]
    course_ids = [a['course_id'] for a in assignments]
    
    colors = plt.cm.Set3([(cid - 1) % 12 for cid in course_ids])
    sizes = [200 if g > 0 else 100 for g in grades]
    
    scatter = ax1.scatter(dates, [1]*len(dates), s=sizes, c=course_ids, cmap='Set3', 
                         alpha=0.7, edgecolors='black', linewidth=1.5)
    
    # Add assignment labels
    for i, (date, assign) in enumerate(zip(dates, assignments)):
        ax1.annotate(f"{assign['title'][:15]}\n({assign['course'][:12]})", 
                    xy=(date, 1), xytext=(0, 20 if i % 2 == 0 else -20),
                    textcoords='offset points', ha='center', fontsize=7,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=0.5))
    
    ax1.set_ylim(0.5, 1.5)
    ax1.set_yticks([])
    ax1.set_xlabel('Due Date', fontsize=10)
    ax1.set_title('Assignment Timeline - Track Your Deadlines', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', linestyle='--', alpha=0.3)
    ax1.set_ylabel('')
    
    if assignments:
        min_date = min(dates)
        max_date = max(dates)
        weeks = {}
        current = min_date
        week_num = 0
        while current <= max_date:
            week_start = current
            week_end = current + timedelta(days=6)
            week_key = f"Week {week_num + 1}\n({week_start.strftime('%m/%d')})"
            
            count = sum(1 for a in assignments if week_start <= a['date'] <= week_end)
            graded = sum(1 for a in assignments if week_start <= a['date'] <= week_end and a['grade'] is not None)
            
            if count > 0:
                weeks[week_key] = {'total': count, 'graded': graded}
            
            current = week_end + timedelta(days=1)
            week_num += 1
        
        if weeks:
            week_labels = list(weeks.keys())
            totals = [weeks[w]['total'] for w in week_labels]
            gradeds = [weeks[w]['graded'] for w in week_labels]
            ungraded = [t - g for t, g in zip(totals, gradeds)]
            
            x_pos = range(len(week_labels))
            ax2.bar(x_pos, gradeds, label='Graded', color='#2ecc71', alpha=0.8)
            ax2.bar(x_pos, ungraded, bottom=gradeds, label='Not Graded', color='#e74c3c', alpha=0.8)
            
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(week_labels, fontsize=8)
            ax2.set_ylabel('Number of Assignments', fontsize=10)
            ax2.set_title('Weekly Workload - Plan Your Time', fontsize=12, fontweight='bold')
            ax2.legend(loc='upper left', fontsize=9)
            ax2.grid(axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {filename}")
    return filename


def plot_study_time_per_course(db: Database, filename: str) -> Optional[str]:
    """Plot total study time per course as a horizontal bar chart"""
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib is not installed. Run: pip install matplotlib")
        return None
    
    query = """
        SELECT 
            c.name AS course_name,
            COUNT(s.id) AS session_count,
            SUM(s.duration_minutes) AS total_minutes,
            ROUND(SUM(s.duration_minutes) / 60.0, 2) AS total_hours
        FROM courses c
        LEFT JOIN study_sessions s ON c.id = s.course_id
        GROUP BY c.id, c.name
        HAVING total_minutes > 0
        ORDER BY total_hours DESC
    """
    
    rows = db.fetch_all(query)
    if not rows:
        print("No study sessions found to plot.")
        return None
    
    course_names = [row["course_name"] for row in rows]
    total_hours = [row["total_hours"] for row in rows]
    session_counts = [row["session_count"] for row in rows]
    
    # Create color gradient
    max_hours = max(total_hours)
    colors = plt.cm.Greens([h / max_hours for h in total_hours])
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(course_names, total_hours, color=colors, edgecolor='black', linewidth=1)
    
    plt.xlabel('Total Study Time (hours)', fontsize=11)
    plt.title('Study Time per Course', fontsize=13, fontweight='bold')
    plt.grid(axis='x', linestyle='--', alpha=0.4)
    
    # Add value labels
    for i, (bar, hours, count) in enumerate(zip(bars, total_hours, session_counts)):
        plt.text(hours + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{hours}h ({count} sessions)",
                va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()
    print(f"Plot saved to {filename}")
    return filename


def plot_study_efficiency(db: Database, filename: str) -> Optional[str]:
    """Plot study time vs average grade per course to identify where more studying is needed"""
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib is not installed. Run: pip install matplotlib")
        return None
    
    query = """
        SELECT 
            c.id,
            c.name AS course_name,
            COALESCE(ROUND(SUM(s.duration_minutes) / 60.0, 2), 0) AS total_hours,
            COALESCE(AVG(a.grade), 0) AS avg_grade,
            COUNT(a.id) AS assignment_count
        FROM courses c
        LEFT JOIN study_sessions s ON c.id = s.course_id
        LEFT JOIN assignments a ON c.id = a.course_id AND a.grade IS NOT NULL
        GROUP BY c.id, c.name
        ORDER BY c.name
    """
    
    rows = db.fetch_all(query)
    if not rows:
        print("No data found to plot.")
        return None
    
    course_names = [row["course_name"] for row in rows]
    study_hours = [row["total_hours"] for row in rows]
    avg_grades = [row["avg_grade"] for row in rows]
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # ===== LEFT PLOT: Study Hours =====
    x_pos = range(len(course_names))
    bars1 = axes[0].bar(x_pos, study_hours, color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_ylabel('Study Time (hours)', fontsize=11, fontweight='bold')
    axes[0].set_xlabel('Courses', fontsize=11, fontweight='bold')
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(course_names, rotation=30, ha='right')
    axes[0].set_title('Total Study Time per Course', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', linestyle='--', alpha=0.3)
    
    # Add value labels for study hours
    for bar, hours in zip(bars1, study_hours):
        height = bar.get_height()
        if height > 0:
            axes[0].text(bar.get_x() + bar.get_width() / 2., height,
                        f'{hours}h', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # ===== RIGHT PLOT: Average Grades =====
    bars2 = axes[1].bar(x_pos, avg_grades, color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_ylabel('Average Grade', fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Courses', fontsize=11, fontweight='bold')
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(course_names, rotation=30, ha='right')
    axes[1].set_ylim(0, 100)
    axes[1].set_title('Average Performance per Course', fontsize=12, fontweight='bold')
    axes[1].grid(axis='y', linestyle='--', alpha=0.3)
    
    # Add value labels for grades
    for bar, grade in zip(bars2, avg_grades):
        height = bar.get_height()
        if height > 0:
            axes[1].text(bar.get_x() + bar.get_width() / 2., height,
                        f'{grade:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        else:
            axes[1].text(bar.get_x() + bar.get_width() / 2., 5,
                        'No grades', ha='center', va='bottom', fontsize=9, style='italic', color='gray')
    
    plt.suptitle('Study Time vs Performance Analysis - Where Do You Need to Study More?', 
                fontsize=13, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {filename}")
    return filename
