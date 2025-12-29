"""
Plotting utilities for Study Tracker using matplotlib.
"""

from typing import Optional

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:  # pragma: no cover - handled at runtime
    MATPLOTLIB_AVAILABLE = False

from studytracker.db import Database


def plot_average_grade_per_course(db: Database, filename: str) -> Optional[str]:
    """Generate a bar chart of average graded assignments per course."""
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

    # Color intensity hints at number of graded assignments per course.
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
