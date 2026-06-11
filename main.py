from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import random, math, string, secrets, sqlite3, os

app = FastAPI(title="PyBridge Pro API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Database Setup ────────────────────────────────────────────────────────────

DB_PATH = "pybridge.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Notes table
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Todo table
    c.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'Medium',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # URL shortener table
    c.execute("""
        CREATE TABLE IF NOT EXISTS short_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # API usage log table
    c.execute("""
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            called_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ─── Logging Middleware ────────────────────────────────────────────────────────

@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    if request.url.path not in ["/", "/docs", "/openapi.json", "/favicon.ico"]:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO api_logs (endpoint, method) VALUES (?, ?)",
                     (request.url.path, request.method))
        conn.commit()
        conn.close()
    return response

# ─── Models ───────────────────────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str

class NumberInput(BaseModel):
    number: float

class PasswordInput(BaseModel):
    length: int = 12

class NoteCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = "General"

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class TodoCreate(BaseModel):
    task: str
    priority: Optional[str] = "Medium"

class UrlInput(BaseModel):
    url: str

class BMIInput(BaseModel):
    weight_kg: float
    height_cm: float

class AgeInput(BaseModel):
    birth_year: int
    birth_month: int
    birth_day: int

class CurrencyInput(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

# ─── Root ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "PyBridge Pro API v2.0 is running!", "timestamp": datetime.now().isoformat()}

@app.get("/ping")
def ping():
    return {"status": "pong", "time": datetime.now().strftime("%H:%M:%S")}

@app.get("/server-time")
def server_time():
    now = datetime.now()
    return {
        "date": now.strftime("%B %d, %Y"),
        "time": now.strftime("%H:%M:%S"),
        "day": now.strftime("%A"),
        "timestamp": now.isoformat(),
        "unix": int(now.timestamp())
    }

# ─── Text Tools ───────────────────────────────────────────────────────────────

@app.post("/reverse-text")
def reverse_text(body: TextInput):
    return {"original": body.text, "reversed": body.text[::-1], "length": len(body.text)}

@app.post("/word-stats")
def word_stats(body: TextInput):
    text = body.text
    words = text.split()
    return {
        "characters": len(text),
        "characters_no_spaces": len(text.replace(" ", "")),
        "words": len(words),
        "sentences": text.count('.') + text.count('!') + text.count('?'),
        "unique_words": len(set(w.lower().strip(".,!?") for w in words)),
        "longest_word": max(words, key=len) if words else "",
    }

# ─── Math Tools ───────────────────────────────────────────────────────────────

@app.post("/sqrt")
def square_root(body: NumberInput):
    if body.number < 0:
        return {"error": "Cannot compute square root of a negative number"}
    return {
        "input": body.number,
        "sqrt": round(math.sqrt(body.number), 6),
        "squared": body.number ** 2,
        "is_perfect_square": math.sqrt(body.number) == int(math.sqrt(body.number))
    }

@app.post("/bmi")
def calculate_bmi(body: BMIInput):
    h = body.height_cm / 100
    bmi = round(body.weight_kg / (h * h), 2)
    if bmi < 18.5: category = "Underweight"
    elif bmi < 25: category = "Normal weight"
    elif bmi < 30: category = "Overweight"
    else: category = "Obese"
    return {"bmi": bmi, "category": category, "weight_kg": body.weight_kg, "height_cm": body.height_cm}

@app.post("/age-calculator")
def calculate_age(body: AgeInput):
    today = datetime.today()
    birth = datetime(body.birth_year, body.birth_month, body.birth_day)
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    next_birthday = datetime(today.year, birth.month, birth.day)
    if next_birthday < today:
        next_birthday = datetime(today.year + 1, birth.month, birth.day)
    days_until = (next_birthday - today).days
    return {
        "age_years": age,
        "age_months": age * 12 + (today.month - birth.month),
        "days_until_birthday": days_until,
        "day_of_birth": birth.strftime("%A")
    }

# ─── Password & Security ──────────────────────────────────────────────────────

@app.post("/generate-password")
def generate_password(body: PasswordInput):
    length = max(8, min(body.length, 64))
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    strength = "Weak" if length < 10 else "Medium" if length < 16 else "Strong"
    return {"password": password, "length": length, "strength": strength}

@app.get("/random-quote")
def random_quote():
    quotes = [
        {"quote": "Code is like humor. When you have to explain it, it's bad.", "author": "Cory House"},
        {"quote": "First, solve the problem. Then, write the code.", "author": "John Johnson"},
        {"quote": "Any fool can write code that a computer can understand.", "author": "Martin Fowler"},
        {"quote": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
        {"quote": "Make it work, make it right, make it fast.", "author": "Kent Beck"},
        {"quote": "The best error message is the one that never shows up.", "author": "Thomas Fuchs"},
    ]
    return random.choice(quotes)

# ─── Notes CRUD ───────────────────────────────────────────────────────────────

@app.get("/notes")
def get_all_notes(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT * FROM notes ORDER BY created_at DESC").fetchall()
    return {"notes": [dict(r) for r in rows], "count": len(rows)}

@app.post("/notes")
def create_note(body: NoteCreate, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute(
        "INSERT INTO notes (title, content, category) VALUES (?, ?, ?)",
        (body.title, body.content, body.category)
    )
    db.commit()
    note = db.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return {"message": "Note created!", "note": dict(note)}

@app.put("/notes/{note_id}")
def update_note(note_id: int, body: NoteUpdate, db: sqlite3.Connection = Depends(get_db)):
    note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    updates = {k: v for k, v in body.dict().items() if v is not None}
    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    db.execute(f"UPDATE notes SET {set_clause} WHERE id = ?", (*updates.values(), note_id))
    db.commit()
    updated = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return {"message": "Note updated!", "note": dict(updated)}

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: sqlite3.Connection = Depends(get_db)):
    note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    return {"message": f"Note {note_id} deleted!"}

# ─── Todo CRUD ────────────────────────────────────────────────────────────────

@app.get("/todos")
def get_todos(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT * FROM todos ORDER BY created_at DESC").fetchall()
    todos = [dict(r) for r in rows]
    return {
        "todos": todos,
        "total": len(todos),
        "completed": sum(1 for t in todos if t["completed"]),
        "pending": sum(1 for t in todos if not t["completed"])
    }

@app.post("/todos")
def create_todo(body: TodoCreate, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("INSERT INTO todos (task, priority) VALUES (?, ?)", (body.task, body.priority))
    db.commit()
    todo = db.execute("SELECT * FROM todos WHERE id = ?", (cur.lastrowid,)).fetchone()
    return {"message": "Todo created!", "todo": dict(todo)}

@app.patch("/todos/{todo_id}/toggle")
def toggle_todo(todo_id: int, db: sqlite3.Connection = Depends(get_db)):
    todo = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    new_status = 0 if todo["completed"] else 1
    db.execute("UPDATE todos SET completed = ? WHERE id = ?", (new_status, todo_id))
    db.commit()
    updated = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return {"message": "Toggled!", "todo": dict(updated)}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: sqlite3.Connection = Depends(get_db)):
    db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    db.commit()
    return {"message": f"Todo {todo_id} deleted!"}

# ─── URL Shortener ────────────────────────────────────────────────────────────

@app.post("/shorten-url")
def shorten_url(body: UrlInput, db: sqlite3.Connection = Depends(get_db)):
    existing = db.execute("SELECT * FROM short_urls WHERE original_url = ?", (body.url,)).fetchone()
    if existing:
        return {"short_code": existing["short_code"], "original_url": existing["original_url"], "clicks": existing["clicks"], "already_existed": True}
    code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))
    db.execute("INSERT INTO short_urls (original_url, short_code) VALUES (?, ?)", (body.url, code))
    db.commit()
    return {"short_code": code, "original_url": body.url, "clicks": 0, "already_existed": False}

@app.get("/urls")
def get_all_urls(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT * FROM short_urls ORDER BY created_at DESC").fetchall()
    return {"urls": [dict(r) for r in rows], "count": len(rows)}

# ─── Analytics ────────────────────────────────────────────────────────────────

@app.get("/analytics")
def get_analytics(db: sqlite3.Connection = Depends(get_db)):
    total_calls = db.execute("SELECT COUNT(*) as c FROM api_logs").fetchone()["c"]
    top_endpoints = db.execute(
        "SELECT endpoint, COUNT(*) as hits FROM api_logs GROUP BY endpoint ORDER BY hits DESC LIMIT 5"
    ).fetchall()
    notes_count = db.execute("SELECT COUNT(*) as c FROM notes").fetchone()["c"]
    todos_count = db.execute("SELECT COUNT(*) as c FROM todos").fetchone()["c"]
    urls_count = db.execute("SELECT COUNT(*) as c FROM short_urls").fetchone()["c"]
    return {
        "total_api_calls": total_calls,
        "top_endpoints": [dict(r) for r in top_endpoints],
        "total_notes": notes_count,
        "total_todos": todos_count,
        "total_short_urls": urls_count
    }
