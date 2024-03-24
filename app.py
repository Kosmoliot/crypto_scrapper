import os
import pyodbc, struct
from azure import identity

from typing import Union

# FastAPI web framework for building APIs with Python. Uses Swagger UI to generate 
# interactive API documentation that lets your users try out the API calls directly 
# in the browser
from fastapi import FastAPI

#FastAPI uses Pydantic models for request and response validation. It automatically 
# validates request data against the defined data models and raises validation errors
# if data doesn't match the expected schema
from pydantic import BaseModel

# Uses load_dotenv to load a connection string from .env file
from dotenv import load_dotenv

class Person(BaseModel):
    first_name: str
    # Using 'Union' type hint from Python's typing module to specify that 'last_name' can either be a string
    #('str') or 'None'
    last_name: Union[str, None] = None  

load_dotenv()
connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]

app = FastAPI()

@app.get("/")
def root():
    print("Root of Person API")
    try:
        conn = get_conn()
        cursor = conn.cursor()

        # Table should be created ahead of time in production app.
        cursor.execute("""
            CREATE TABLE Persons (
                ID int NOT NULL PRIMARY KEY IDENTITY,
                FirstName varchar(255),
                LastName varchar(255)
            );
        """)

        conn.commit()
    except Exception as e:
        # Table may already exist
        print(e)
    return "Person API"

@app.get("/all")
def get_persons():
    rows = []
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Persons")

        for row in cursor.fetchall():
            print(row.FirstName, row.LastName)
            rows.append(f"{row.ID}, {row.FirstName}, {row.LastName}")
    return rows

@app.get("/person/{person_id}")
def get_person(person_id: int):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Persons WHERE ID = ?", person_id)

        row = cursor.fetchone()
        return f"{row.ID}, {row.FirstName}, {row.LastName}"

@app.post("/person")
def create_person(item: Person):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO Persons (FirstName, LastName) VALUES (?, ?)", item.first_name, item.last_name)
        conn.commit()

    return item

# def get_conn():
#     credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=True)
#     token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
#     token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
#     SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
#     conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
#     return conn

def get_conn():
    conn = pyodbc.connect(connection_string)
    return conn
