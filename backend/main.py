import os, json, sqlite3, hmac, hashlib, secrets, time
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH=os.getenv("BIOLEARN_DB","biolearn.db")
SECRET=os.getenv("BIOLEARN_SECRET","CHANGE_ME_TO_A_LONG_RANDOM_SECRET")
TOKEN_TTL=int(os.getenv("TOKEN_TTL_SECONDS","86400"))
app=FastAPI(title="BioLearn Plus API",version="1.0.0",description="REST API for accessible Biology lessons, quiz bank and learner progress.")
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("CORS_ORIGINS","*").split(","),allow_credentials=False,allow_methods=["*"],allow_headers=["*"])

def db():
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con
def init():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'student', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS lessons(id TEXT PRIMARY KEY, grade TEXT NOT NULL, theme TEXT NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL, objectives TEXT NOT NULL, simple TEXT NOT NULL, content TEXT NOT NULL, keyPoints TEXT NOT NULL, altText TEXT NOT NULL, quiz TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS progress(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, lesson_id TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE, completed INTEGER NOT NULL DEFAULT 0, quiz_score INTEGER, quiz_total INTEGER, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id,lesson_id));
        CREATE TABLE IF NOT EXISTS quiz_attempts(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, grade TEXT, score INTEGER NOT NULL, total INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
    admin=os.getenv("BIOLEARN_ADMIN_USERNAME"); pw=os.getenv("BIOLEARN_ADMIN_PASSWORD")
    if admin and pw:
        with db() as c:
            if not c.execute("SELECT 1 FROM users WHERE username=?",(admin,)).fetchone():
                c.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",(admin,hashpw(pw),"admin"))
def hashpw(pw):
    salt=secrets.token_hex(16); digest=hashlib.pbkdf2_hmac("sha256",pw.encode(),salt.encode(),180000).hex()
    return salt+"$"+digest
def verify(pw,stored):
    try:
        salt,d=stored.split("$"); return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256",pw.encode(),salt.encode(),180000).hex(),d)
    except Exception:return False
def token(user):
    payload=f"{user['id']}:{user['role']}:{int(time.time())+TOKEN_TTL}:{secrets.token_hex(8)}"
    sig=hmac.new(SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest()
    return payload+"."+sig
def current(authorization:Optional[str]=Header(None)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401,"Bearer token required")
    raw=authorization[7:]
    try:
        payload,sig=raw.rsplit(".",1)
        if not hmac.compare_digest(hmac.new(SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest(),sig): raise ValueError()
        uid,role,exp,_=payload.split(":")
        if int(exp)<int(time.time()): raise ValueError()
        with db() as c: u=c.execute("SELECT id,username,role FROM users WHERE id=?",(uid,)).fetchone()
        if not u: raise ValueError()
        return dict(u)
    except Exception: raise HTTPException(401,"Invalid or expired token")
def admin(user=Depends(current)):
    if user["role"]!="admin": raise HTTPException(403,"Administrator access required")
    return user

class Register(BaseModel):
    username:str=Field(min_length=3,max_length=50)
    password:str=Field(min_length=8,max_length=128)
class Login(Register): pass
class Lesson(BaseModel):
    id:str=Field(min_length=1,max_length=100)
    grade:str
    theme:str
    title:str
    summary:str
    objectives:list[str]=[]
    simple:str=""
    content:str
    keyPoints:list[str]=[]
    altText:str=""
    quiz:list[dict]=[]
class ProgressInput(BaseModel):
    lesson_id:str
    completed:bool=False
    quiz_score:Optional[int]=None
    quiz_total:Optional[int]=None
class Attempt(BaseModel):
    grade:Optional[str]=None
    score:int=Field(ge=0)
    total:int=Field(gt=0)

@app.on_event("startup")
def startup(): init()
@app.get("/health")
def health():
    with db() as c: n=c.execute("SELECT COUNT(*) n FROM lessons").fetchone()["n"]
    return {"status":"ok","lesson_count":n}
@app.post("/auth/register")
def register(data:Register):
    with db() as c:
        if c.execute("SELECT 1 FROM users WHERE username=?",(data.username,)).fetchone(): raise HTTPException(409,"Username already exists")
        c.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",(data.username,hashpw(data.password),"student"))
        u=c.execute("SELECT id,username,role FROM users WHERE username=?",(data.username,)).fetchone()
    return {"access_token":token(u),"token_type":"bearer","user":dict(u)}
@app.post("/auth/login")
def login(data:Login):
    with db() as c: u=c.execute("SELECT id,username,role,password_hash FROM users WHERE username=?",(data.username,)).fetchone()
    if not u or not verify(data.password,u["password_hash"]): raise HTTPException(401,"Incorrect username or password")
    return {"access_token":token(u),"token_type":"bearer","user":{"id":u["id"],"username":u["username"],"role":u["role"]}}
@app.get("/auth/me")
def me(user=Depends(current)): return user
def serialize(row):
    d=dict(row)
    for k in ["objectives","keyPoints","quiz"]: d[k]=json.loads(d[k])
    return d
@app.get("/lessons")
def list_lessons(grade:Optional[str]=None,theme:Optional[str]=None,q:Optional[str]=None,limit:int=500,offset:int=0):
    limit=max(1,min(limit,1000)); offset=max(0,offset)
    sql="SELECT * FROM lessons WHERE 1=1"; args=[]
    if grade: sql+=" AND grade=?"; args.append(grade)
    if theme: sql+=" AND theme=?"; args.append(theme)
    if q: sql+=" AND (title LIKE ? OR summary LIKE ?)"; args.extend([f"%{q}%",f"%{q}%"])
    sql+=" ORDER BY grade,theme,title LIMIT ? OFFSET ?"; args.extend([limit,offset])
    with db() as c: rows=c.execute(sql,args).fetchall()
    return [serialize(r) for r in rows]
@app.get("/lessons/{lesson_id}")
def get_lesson(lesson_id:str):
    with db() as c:r=c.execute("SELECT * FROM lessons WHERE id=?",(lesson_id,)).fetchone()
    if not r: raise HTTPException(404,"Lesson not found")
    return serialize(r)
@app.post("/admin/lessons",status_code=201)
def create_lesson(data:Lesson,user=Depends(admin)):
    with db() as c:
        if c.execute("SELECT 1 FROM lessons WHERE id=?",(data.id,)).fetchone(): raise HTTPException(409,"Lesson id already exists")
        save_lesson(c,data,False)
    return {"message":"Lesson created","id":data.id}
@app.put("/admin/lessons/{lesson_id}")
def update_lesson(lesson_id:str,data:Lesson,user=Depends(admin)):
    if lesson_id!=data.id: raise HTTPException(400,"URL id and lesson id must match")
    with db() as c:
        if not c.execute("SELECT 1 FROM lessons WHERE id=?",(lesson_id,)).fetchone(): raise HTTPException(404,"Lesson not found")
        save_lesson(c,data,True)
    return {"message":"Lesson updated"}
def save_lesson(c,data,update):
    values=(data.grade,data.theme,data.title,data.summary,json.dumps(data.objectives),data.simple,data.content,json.dumps(data.keyPoints),data.altText,json.dumps(data.quiz))
    if update:c.execute("UPDATE lessons SET grade=?,theme=?,title=?,summary=?,objectives=?,simple=?,content=?,keyPoints=?,altText=?,quiz=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",values+(data.id,))
    else:c.execute("INSERT INTO lessons(grade,theme,title,summary,objectives,simple,content,keyPoints,altText,quiz,id) VALUES(?,?,?,?,?,?,?,?,?,?,?)",values+(data.id,))
@app.delete("/admin/lessons/{lesson_id}")
def delete_lesson(lesson_id:str,user=Depends(admin)):
    with db() as c:
        cur=c.execute("DELETE FROM lessons WHERE id=?",(lesson_id,))
        if not cur.rowcount: raise HTTPException(404,"Lesson not found")
    return {"message":"Lesson deleted"}
@app.post("/admin/import")
def import_lessons(payload:list[Lesson],user=Depends(admin)):
    added=0; updated=0
    with db() as c:
        for item in payload:
            exists=c.execute("SELECT 1 FROM lessons WHERE id=?",(item.id,)).fetchone()
            save_lesson(c,item,bool(exists))
            if exists:updated+=1
            else:added+=1
    return {"added":added,"updated":updated,"total":len(payload)}
@app.get("/admin/summary")
def summary(user=Depends(admin)):
    with db() as c:
        counts={g:c.execute("SELECT COUNT(*) n FROM lessons WHERE grade=?",(g,)).fetchone()["n"] for g in ["SS1","SS2","SS3"]}
        users=c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
        attempts=c.execute("SELECT COUNT(*) n FROM quiz_attempts").fetchone()["n"]
    return {"lessons_by_grade":counts,"users":users,"quiz_attempts":attempts}
@app.post("/progress")
def save_progress(data:ProgressInput,user=Depends(current)):
    with db() as c:
        if not c.execute("SELECT 1 FROM lessons WHERE id=?",(data.lesson_id,)).fetchone(): raise HTTPException(404,"Lesson not found")
        c.execute("""INSERT INTO progress(user_id,lesson_id,completed,quiz_score,quiz_total) VALUES(?,?,?,?,?)
        ON CONFLICT(user_id,lesson_id) DO UPDATE SET completed=excluded.completed,quiz_score=excluded.quiz_score,quiz_total=excluded.quiz_total,updated_at=CURRENT_TIMESTAMP""",(user["id"],data.lesson_id,int(data.completed),data.quiz_score,data.quiz_total))
    return {"message":"Progress saved"}
@app.get("/progress")
def get_progress(user=Depends(current)):
    with db() as c: rows=c.execute("SELECT lesson_id,completed,quiz_score,quiz_total,updated_at FROM progress WHERE user_id=? ORDER BY updated_at DESC",(user["id"],)).fetchall()
    return [dict(r) for r in rows]
@app.post("/quiz-attempts")
def record_attempt(data:Attempt,user=Depends(current)):
    if data.score>data.total: raise HTTPException(400,"Score cannot exceed total")
    with db() as c:c.execute("INSERT INTO quiz_attempts(user_id,grade,score,total) VALUES(?,?,?,?)",(user["id"],data.grade,data.score,data.total))
    return {"message":"Attempt recorded","percentage":round(data.score/data.total*100,1)}
