# Student Grade Evaluation API

A Flask-based REST API for managing student records with CRUD operations and analytics.

---

## Project Structure

```
YourFullName/
├── app.py              ← Main Flask application
├── requirements.txt    ← Python dependencies
├── Procfile            ← Render deployment config
├── runtime.txt         ← Python version
├── schema.sql          ← Database structure
└── README.md
```

---

## API Endpoints

| Method | Route                    | Description              |
|--------|--------------------------|--------------------------|
| GET    | `/students`              | View all students (HTML) |
| GET    | `/api/students`          | Get all students (JSON)  |
| GET    | `/student/<id>`          | Get one student (JSON)   |
| GET    | `/add_student_form`      | Add student form         |
| POST   | `/add_student`           | Add new student          |
| GET    | `/edit_student/<id>`     | Edit student form        |
| POST   | `/edit_student/<id>`     | Update student           |
| GET    | `/delete_student/<id>`   | Delete student           |
| GET    | `/summary`               | Analytics summary (JSON) |

---

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Visit: http://127.0.0.1:5000

---

## Deploy to Render

1. Push this repo to GitHub (repo name = your full name)
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click **Deploy**

---

## Sample Summary Response

```json
{
  "total_students": 3,
  "average_grade": 81.67,
  "highest_grade": 90,
  "lowest_grade": 70,
  "passed": 2,
  "failed": 1,
  "pass_rate": "66.7%"
}
```
