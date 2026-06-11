# ⚡ PyBridge Pro — Full Stack with Database

Python FastAPI backend + SQLite database + HTML/CSS/JS frontend.

## 🚀 Quick Start

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Open `frontend/index.html` in your browser → Click **Connect**.

## 📁 Structure

```
fullstack-db/
├── backend/
│   ├── main.py              ← FastAPI + SQLite
│   ├── requirements.txt
│   └── pybridge.db          ← SQLite DB (auto-created)
├── frontend/
│   └── index.html
└── README.md
```

## 🗄️ Database Tables

| Table       | Purpose                        |
|-------------|-------------------------------|
| notes       | Create / read / delete notes  |
| todos       | Task manager with priorities  |
| short_urls  | URL shortener with click count|
| api_logs    | Auto-logs every API call      |

## 🛠 API Endpoints

| Method | Endpoint              | Description              |
|--------|-----------------------|--------------------------|
| GET    | /ping                 | Health check             |
| GET    | /server-time          | Server date & time       |
| POST   | /reverse-text         | Reverse a string         |
| POST   | /word-stats           | Text analysis            |
| POST   | /sqrt                 | Square root calculator   |
| POST   | /bmi                  | BMI calculator           |
| POST   | /age-calculator       | Age + birthday countdown |
| POST   | /generate-password    | Secure password          |
| GET    | /random-quote         | Dev quote                |
| GET    | /notes                | Get all notes            |
| POST   | /notes                | Create note              |
| DELETE | /notes/{id}           | Delete note              |
| GET    | /todos                | Get all todos            |
| POST   | /todos                | Create todo              |
| PATCH  | /todos/{id}/toggle    | Toggle complete          |
| DELETE | /todos/{id}           | Delete todo              |
| POST   | /shorten-url          | Shorten a URL            |
| GET    | /urls                 | Get all short URLs       |
| GET    | /analytics            | DB stats + top endpoints |

## 🔗 API Docs
Visit: http://localhost:8000/docs
