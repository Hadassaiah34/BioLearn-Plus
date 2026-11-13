import os,json,sqlite3
DB=os.getenv("BIOLEARN_DB","biolearn.db")
DATA=os.path.join(os.path.dirname(__file__),"..","content","biology-sss1-sss3.json")
c=sqlite3.connect(DB)
c.execute("PRAGMA foreign_keys=ON")
# Initialize schema via main module first: `python -c "import main; main.init()"`
with open(DATA,encoding="utf-8") as f: lessons=json.load(f)
for x in lessons:
    values=(x["grade"],x["theme"],x["title"],x["summary"],json.dumps(x["objectives"]),x["simple"],x["content"],json.dumps(x["keyPoints"]),x["altText"],json.dumps(x["quiz"]),x["id"])
    c.execute("""INSERT INTO lessons(grade,theme,title,summary,objectives,simple,content,keyPoints,altText,quiz,id)
    VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET grade=excluded.grade,theme=excluded.theme,title=excluded.title,summary=excluded.summary,objectives=excluded.objectives,simple=excluded.simple,content=excluded.content,keyPoints=excluded.keyPoints,altText=excluded.altText,quiz=excluded.quiz,updated_at=CURRENT_TIMESTAMP""",values)
c.commit(); print(f"Seeded/updated {len(lessons)} lessons and {sum(len(x['quiz']) for x in lessons)} quiz questions."); c.close()
