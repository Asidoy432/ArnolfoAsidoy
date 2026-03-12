from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB = "/tmp/students.db"

BASE_STYLE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GradeTrack — Student Portal</title>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #0b0f1a;
      --surface:   #111827;
      --card:      #161d2e;
      --border:    #1e2d45;
      --accent:    #00e5a0;
      --accent2:   #00bfff;
      --danger:    #ff4d6d;
      --warn:      #ffb830;
      --text:      #e8edf5;
      --muted:     #5a6a82;
      --pass:      #00e5a0;
      --fail:      #ff4d6d;
    }

    html, body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      min-height: 100vh;
      font-size: 15px;
    }

    /* ── NAV ── */
    nav {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 32px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(12px);
    }
    .nav-brand {
      font-family: 'Syne', sans-serif;
      font-weight: 800;
      font-size: 18px;
      color: var(--text);
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .nav-brand span {
      color: var(--accent);
    }
    .nav-dot {
      width: 8px; height: 8px;
      background: var(--accent);
      border-radius: 50%;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.8); }
    }
    .nav-links { display: flex; gap: 6px; }
    .nav-link {
      color: var(--muted);
      text-decoration: none;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.2s;
    }
    .nav-link:hover { color: var(--text); background: var(--card); }
    .nav-link.active { color: var(--accent); background: rgba(0,229,160,0.08); }

    /* ── LAYOUT ── */
    .page { max-width: 1100px; margin: 0 auto; padding: 36px 24px; }

    /* ── PAGE HEADER ── */
    .page-header {
      margin-bottom: 32px;
      animation: fadeUp 0.4s ease both;
    }
    .page-header h1 {
      font-family: 'Syne', sans-serif;
      font-size: 28px;
      font-weight: 800;
      color: var(--text);
    }
    .page-header p {
      color: var(--muted);
      font-size: 14px;
      margin-top: 4px;
    }
    .header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }

    /* ── STAT CARDS ── */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
      animation: fadeUp 0.5s ease 0.1s both;
    }
    .stat-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
      position: relative;
      overflow: hidden;
    }
    .stat-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 2px;
      background: var(--accent);
    }
    .stat-card.danger::before { background: var(--danger); }
    .stat-card.warn::before { background: var(--warn); }
    .stat-card.blue::before { background: var(--accent2); }
    .stat-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .stat-value { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 500; color: var(--text); }
    .stat-value.green { color: var(--accent); }
    .stat-value.red { color: var(--danger); }

    /* ── TABLE ── */
    .table-wrap {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      animation: fadeUp 0.5s ease 0.2s both;
    }
    .table-top {
      padding: 18px 24px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .table-title {
      font-family: 'Syne', sans-serif;
      font-weight: 700;
      font-size: 15px;
    }
    table { width: 100%; border-collapse: collapse; }
    thead tr { background: rgba(255,255,255,0.02); }
    th {
      text-align: left;
      padding: 12px 20px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--muted);
      font-weight: 500;
      border-bottom: 1px solid var(--border);
    }
    td {
      padding: 14px 20px;
      border-bottom: 1px solid rgba(30,45,69,0.5);
      font-size: 14px;
      vertical-align: middle;
    }
    tbody tr:last-child td { border-bottom: none; }
    tbody tr { transition: background 0.15s; }
    tbody tr:hover { background: rgba(255,255,255,0.02); }

    .grade-cell {
      font-family: 'DM Mono', monospace;
      font-size: 15px;
      font-weight: 500;
    }
    .badge {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    .badge-pass { background: rgba(0,229,160,0.12); color: var(--pass); }
    .badge-fail { background: rgba(255,77,109,0.12); color: var(--fail); }

    .action-links { display: flex; gap: 8px; }
    .action-btn {
      padding: 5px 12px;
      border-radius: 7px;
      font-size: 12px;
      font-weight: 500;
      text-decoration: none;
      transition: all 0.15s;
      border: 1px solid transparent;
    }
    .action-btn.edit {
      color: var(--accent2);
      border-color: rgba(0,191,255,0.25);
      background: rgba(0,191,255,0.06);
    }
    .action-btn.edit:hover { background: rgba(0,191,255,0.15); }
    .action-btn.delete {
      color: var(--danger);
      border-color: rgba(255,77,109,0.25);
      background: rgba(255,77,109,0.06);
    }
    .action-btn.delete:hover { background: rgba(255,77,109,0.15); }

    /* ── BUTTONS ── */
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 20px;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 500;
      font-family: 'DM Sans', sans-serif;
      text-decoration: none;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
    }
    .btn-primary {
      background: var(--accent);
      color: #0b0f1a;
      font-weight: 600;
    }
    .btn-primary:hover { background: #00ffb3; transform: translateY(-1px); box-shadow: 0 4px 20px rgba(0,229,160,0.3); }
    .btn-secondary {
      background: var(--card);
      color: var(--text);
      border: 1px solid var(--border);
    }
    .btn-secondary:hover { background: var(--border); }
    .btn-danger {
      background: rgba(255,77,109,0.1);
      color: var(--danger);
      border: 1px solid rgba(255,77,109,0.3);
    }
    .btn-danger:hover { background: rgba(255,77,109,0.2); }

    /* ── FORM ── */
    .form-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 32px;
      max-width: 520px;
      animation: fadeUp 0.4s ease both;
    }
    .form-group { margin-bottom: 20px; }
    .form-label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }
    .form-input {
      width: 100%;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px 16px;
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-size: 15px;
      transition: border-color 0.2s, box-shadow 0.2s;
      outline: none;
    }
    .form-input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(0,229,160,0.1);
    }
    .form-actions { display: flex; gap: 12px; margin-top: 28px; }

    /* ── EMPTY STATE ── */
    .empty {
      text-align: center;
      padding: 60px 20px;
      color: var(--muted);
    }
    .empty-icon { font-size: 48px; margin-bottom: 12px; }
    .empty h3 { font-family: 'Syne', sans-serif; color: var(--text); margin-bottom: 6px; }

    /* ── SUMMARY ── */
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      animation: fadeUp 0.4s ease both;
    }
    .summary-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 28px 24px;
      text-align: center;
    }
    .summary-num {
      font-family: 'Syne', sans-serif;
      font-size: 42px;
      font-weight: 800;
      color: var(--accent);
      line-height: 1;
    }
    .summary-num.red { color: var(--danger); }
    .summary-num.blue { color: var(--accent2); }
    .summary-num.warn { color: var(--warn); }
    .summary-label { color: var(--muted); font-size: 13px; margin-top: 8px; }

    /* ── ANIMATIONS ── */
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(16px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* ── RESPONSIVE ── */
    @media (max-width: 600px) {
      nav { padding: 0 16px; }
      .page { padding: 24px 16px; }
      .nav-links { display: none; }
      td, th { padding: 10px 12px; }
    }
  </style>
</head>
<body>
<nav>
  <a class="nav-brand" href="/"><div class="nav-dot"></div>Grade<span>Track</span></a>
  <div class="nav-links">
    <a class="nav-link" href="/students">Students</a>
    <a class="nav-link" href="/add_student_form">Add Student</a>
    <a class="nav-link" href="/summary">Summary</a>
  </div>
</nav>
"""

CLOSE_HTML = "</body></html>"


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

    total = len(rows)
    passed = sum(1 for r in rows if r["grade"] >= 75)
    failed = total - passed
    avg = round(sum(r["grade"] for r in rows) / total, 1) if total else 0

    html = BASE_STYLE + """
<div class="page">
  <div class="page-header">
    <div class="header-row">
      <div>
        <h1>Student Records</h1>
        <p>Manage and track student grades and performance</p>
      </div>
      <a href="/add_student_form" class="btn btn-primary">＋ Add Student</a>
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">Total Students</div>
      <div class="stat-value">{{ total }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Average Grade</div>
      <div class="stat-value">{{ avg }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Passed</div>
      <div class="stat-value green">{{ passed }}</div>
    </div>
    <div class="stat-card danger">
      <div class="stat-label">Failed</div>
      <div class="stat-value red">{{ failed }}</div>
    </div>
  </div>

  <div class="table-wrap">
    <div class="table-top">
      <span class="table-title">All Students</span>
      <a href="/summary" class="btn btn-secondary" style="padding:7px 14px;font-size:13px;">View Analytics →</a>
    </div>
    {% if students %}
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>Section</th>
          <th>Grade</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for s in students %}
        <tr>
          <td style="color:var(--muted);font-family:'DM Mono',monospace;font-size:13px;">{{ s['id'] }}</td>
          <td style="font-weight:500;">{{ s['name'] }}</td>
          <td style="color:var(--muted);">{{ s['section'] }}</td>
          <td class="grade-cell">{{ s['grade'] }}</td>
          <td>
            {% if s['grade'] >= 75 %}
            <span class="badge badge-pass">PASSED</span>
            {% else %}
            <span class="badge badge-fail">FAILED</span>
            {% endif %}
          </td>
          <td>
            <div class="action-links">
              <a href="/edit_student/{{ s['id'] }}" class="action-btn edit">Edit</a>
              <a href="/delete_student/{{ s['id'] }}" class="action-btn delete"
                 onclick="return confirm('Delete {{ s[\'name\'] }}?')">Delete</a>
            </div>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div class="empty">
      <div class="empty-icon">📭</div>
      <h3>No students yet</h3>
      <p>Add your first student to get started</p>
    </div>
    {% endif %}
  </div>
</div>
""" + CLOSE_HTML
    return render_template_string(html, students=rows, total=total, passed=passed, failed=failed, avg=avg)


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
    html = BASE_STYLE + """
<div class="page">
  <div class="page-header">
    <div class="header-row">
      <div>
        <h1>Add Student</h1>
        <p>Enter new student information below</p>
      </div>
      <a href="/students" class="btn btn-secondary">← Back</a>
    </div>
  </div>
  <div class="form-card">
    <form action="/add_student" method="POST">
      <div class="form-group">
        <label class="form-label">Full Name</label>
        <input class="form-input" type="text" name="name" placeholder="e.g. Juan dela Cruz" required autofocus>
      </div>
      <div class="form-group">
        <label class="form-label">Grade (0–100)</label>
        <input class="form-input" type="number" name="grade" placeholder="e.g. 88" required min="0" max="100">
      </div>
      <div class="form-group">
        <label class="form-label">Section</label>
        <input class="form-input" type="text" name="section" placeholder="e.g. Stallman" required>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary">Save Student</button>
        <a href="/students" class="btn btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
""" + CLOSE_HTML
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
    html = BASE_STYLE + """
<div class="page">
  <div class="page-header">
    <div class="header-row">
      <div>
        <h1>Edit Student</h1>
        <p>Update information for <strong style="color:var(--accent)">{{ s['name'] }}</strong></p>
      </div>
      <a href="/students" class="btn btn-secondary">← Back</a>
    </div>
  </div>
  <div class="form-card">
    <form method="POST">
      <div class="form-group">
        <label class="form-label">Full Name</label>
        <input class="form-input" type="text" name="name" value="{{ s['name'] }}" required>
      </div>
      <div class="form-group">
        <label class="form-label">Grade (0–100)</label>
        <input class="form-input" type="number" name="grade" value="{{ s['grade'] }}" required min="0" max="100">
      </div>
      <div class="form-group">
        <label class="form-label">Section</label>
        <input class="form-input" type="text" name="section" value="{{ s['section'] }}" required>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary">Update Student</button>
        <a href="/students" class="btn btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
""" + CLOSE_HTML
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
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    if not rows:
        return redirect(url_for("list_students"))

    grades = [r["grade"] for r in rows]
    passed = len([g for g in grades if g >= 75])
    failed = len(grades) - passed
    average = round(sum(grades) / len(grades), 2)
    highest = max(grades)
    lowest = min(grades)
    pass_rate = round((passed / len(grades)) * 100, 1)

    html = BASE_STYLE + """
<div class="page">
  <div class="page-header">
    <div class="header-row">
      <div>
        <h1>Analytics Summary</h1>
        <p>Performance overview across all students</p>
      </div>
      <a href="/students" class="btn btn-secondary">← Back to Students</a>
    </div>
  </div>

  <div class="summary-grid">
    <div class="summary-card">
      <div class="summary-num">{{ total }}</div>
      <div class="summary-label">Total Students</div>
    </div>
    <div class="summary-card">
      <div class="summary-num blue">{{ average }}</div>
      <div class="summary-label">Average Grade</div>
    </div>
    <div class="summary-card">
      <div class="summary-num">{{ highest }}</div>
      <div class="summary-label">Highest Grade</div>
    </div>
    <div class="summary-card">
      <div class="summary-num warn">{{ lowest }}</div>
      <div class="summary-label">Lowest Grade</div>
    </div>
    <div class="summary-card">
      <div class="summary-num">{{ passed }}</div>
      <div class="summary-label">Passed</div>
    </div>
    <div class="summary-card">
      <div class="summary-num red">{{ failed }}</div>
      <div class="summary-label">Failed</div>
    </div>
    <div class="summary-card">
      <div class="summary-num" style="font-size:32px;">{{ pass_rate }}%</div>
      <div class="summary-label">Pass Rate</div>
    </div>
  </div>
</div>
""" + CLOSE_HTML
    return render_template_string(
        html,
        total=len(grades),
        average=average,
        highest=highest,
        lowest=lowest,
        passed=passed,
        failed=failed,
        pass_rate=pass_rate,
    )


init_db()

if __name__ == "__main__":
    app.run(debug=True)
