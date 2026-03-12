from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB = "/tmp/students.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            section TEXT NOT NULL
        )
    """
    )
    if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO students (name, grade, section) VALUES (?, ?, ?)",
            [
                ("Juan", 85, "Stallman"),
                ("Maria", 90, "Stallman"),
                ("Pedro", 70, "Zechariah"),
            ],
        )
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect(url_for("list_students"))


@app.route("/students")
def list_students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
    conn.close()
    html = """
<h2>Student List</h2>
<a href="/add_student_form"><button>+ Add Student</button></a>
&nbsp;
<a href="/summary"><button>View Summary</button></a>
<br><br>
<table border="1" cellpadding="8" cellspacing="0">
  <tr>
    <th>ID</th><th>Name</th><th>Grade</th><th>Section</th><th>Remark</th><th>Actions</th>
  </tr>
  {% for s in students %}
  <tr>
    <td>{{ s['id'] }}</td>
    <td>{{ s['name'] }}</td>
    <td>{{ s['grade'] }}</td>
    <td>{{ s['section'] }}</td>
    <td>{{ 'PASSED' if s['grade'] >= 75 else 'FAILED' }}</td>
    <td>
      <a href="/edit_student/{{ s['id'] }}">Edit</a> |
      <a href="/delete_student/{{ s['id'] }}" onclick="return confirm('Delete?')">Delete</a>
    </td>
  </tr>
  {% endfor %}
</table>
"""
    return render_template_string(html, students=rows)


@app.route("/student/<int:id>")
def get_student(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(row))


@app.route("/api/students")
def api_get_students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/add_student_form")
def add_student_form():
    html = """
<h2>Add New Student</h2>
<form action="/add_student" method="POST">
  Name: <input type="text" name="name" required autofocus><br><br>
  Grade: <input type="number" name="grade" required min="0" max="100"><br><br>
  Section: <input type="text" name="section" required><br><br>
  <input type="submit" value="Add Student">
</form>
<br><a href="/students">Back to List</a>
"""
    return render_template_string(html)


@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    section = request.form.get("section", "").strip()
    raw_grade = request.form.get("grade", "")
    if not name or not section:
        return jsonify({"error": "Name and section are required"}), 400
    try:
        grade = int(raw_grade)
    except ValueError:
        return jsonify({"error": "Grade must be a number"}), 400
    if grade < 0 or grade > 100:
        return jsonify({"error": "Grade must be between 0 and 100"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO students (name, grade, section) VALUES (?, ?, ?)",
        (name, grade, section),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("list_students"))


@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        section = request.form.get("section", "").strip()
        raw_grade = request.form.get("grade", "")
        if not name or not section:
            conn.close()
            return jsonify({"error": "Name and section are required"}), 400
        try:
            grade = int(raw_grade)
        except ValueError:
            conn.close()
            return jsonify({"error": "Grade must be a number"}), 400
        if grade < 0 or grade > 100:
            conn.close()
            return jsonify({"error": "Grade must be between 0 and 100"}), 400
        conn.execute(
            "UPDATE students SET name=?, grade=?, section=? WHERE id=?",
            (name, grade, section, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("list_students"))
    conn.close()
    html = """
<h2>Edit Student</h2>
<form method="POST">
  Name: <input type="text" name="name" value="{{ s['name'] }}" required><br><br>
  Grade: <input type="number" name="grade" value="{{ s['grade'] }}" required min="0" max="100"><br><br>
  Section: <input type="text" name="section" value="{{ s['section'] }}" required><br><br>
  <button type="submit">Update</button>
</form>
<br><a href="/students">Back to List</a>
"""
    return render_template_string(html, s=student)


@app.route("/delete_student/<int:id>")
def delete_student(id):
    conn = get_db()
    result = conn.execute("SELECT id FROM students WHERE id = ?", (id,)).fetchone()
    if not result:
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("list_students"))


@app.route("/summary")
def summary():
    conn = get_db()
    rows = conn.execute("SELECT grade FROM students").fetchall()
    conn.close()
    if not rows:
        return jsonify({"message": "No students found"}), 404
    grades = [r["grade"] for r in rows]
    passed = len([g for g in grades if g >= 75])
    failed = len(grades) - passed
    average = round(sum(grades) / len(grades), 2)
    return jsonify({
        "total_students": len(grades),
        "average_grade": average,
        "highest_grade": max(grades),
        "lowest_grade": min(grades),
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{round((passed / len(grades)) * 100, 1)}%",
    })


init_db()

if __name__ == "__main__":
    app.run(debug=True)
