import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load OpenAI API key from .env file
load_dotenv()
client = OpenAI()

app = FastAPI()

class MessageRequest(BaseModel):
    message: str
    db_path: str = "databases/sleep.db"

class QueryRequest(BaseModel):
    db_path: str
    query: str
    offset: int = 0
    limit: int = 10

def generate_sql(natural_language: str, schema: str) -> str:
    """Converts natural language to SQL using gpt-4o-mini"""
    prompt = f"""
    Convert this natural language query into a **safe** SQL SELECT statement for SQLite.
    Use the following schema:
    {schema}
    
    Query: {natural_language}
    SQL: 
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a SQL expert. Return only SQL code in text. \
             Don't return in code snippet,\
             Handle case sensitive in where using LOWER in every conditions"},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def get_schema(db_path: str) -> str:
    """Fetches SQLite schema as text for processing."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema = []
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema.append(f"Table {table_name}:\n" + "\n".join(
                [f"- {col[1]} ({col[2]})" for col in columns]))
        return "\n\n".join(schema)
    finally:
        conn.close()

@app.post("/send_message")
async def process_nl_query(request: MessageRequest):
    """Processes a natural language query and executes the generated SQL."""
    try:
        schema = get_schema(request.db_path)
        generated_sql = generate_sql(request.message, schema)
        
        print(f"Debug: Generated SQL = {generated_sql}")
        # Ensure the generated SQL is a SELECT statement (security check)
        if not generated_sql.lower().strip().startswith("select"):
            raise HTTPException(status_code=400, detail="Generated SQL is not a SELECT query.")

        # Execute generated SQL
        conn = sqlite3.connect(request.db_path)
        cursor = conn.cursor()
        cursor.execute(generated_sql)
        results = cursor.fetchall()
        conn.close()
        
        return {
            "generated_sql": generated_sql,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute_query")
async def execute_direct_query(request: QueryRequest):
    """Executes a user-provided SQL query."""
    try:
        if not os.path.exists(request.db_path):
            raise HTTPException(status_code=404, detail="Database not found")
            
        conn = sqlite3.connect(request.db_path)
        cursor = conn.cursor()
        cursor.execute(f"{request.query} LIMIT {request.limit} OFFSET {request.offset}")
        results = cursor.fetchall()
        conn.close()
        
        return {
            "query": request.query,
            "results": results
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
