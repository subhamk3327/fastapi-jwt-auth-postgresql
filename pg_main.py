import psycopg2
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from urllib.parse import urlparse


load_dotenv()


s_key = os.getenv("SECRET_KEY")
algo = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

app = FastAPI()

def get_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("database url not set")
    conn = psycopg2.connect(db_url)
    return conn

class item_c(BaseModel):
    name: str

class user_c(BaseModel):
    username : str
    password : str

@app.get("/items")
def get_items(token : str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,s_key,algorithms=[algo])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401,detail="invalid token")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from items")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": x[0], "name": x[1]} for x in rows]

@app.post("/items")
def post_items(new_item: item_c):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("insert into items(name) values (%s)", (new_item.name,))
    conn.commit()
    conn.close()
    return {"message": "success"}

@app.delete("/items/{old_item}")
def delete_item(old_item: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from items where name = %s", (old_item,))
    value = cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404, detail="item not found")
    cursor.execute("delete from items where name = %s", (old_item,))
    conn.commit()
    conn.close()
    return {"message": "success"}

@app.put("/items/{old_item}")
def put_items(old_item: str, new_item: item_c):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from items where name = %s", (old_item,))
    value = cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404, detail="item not found")
    index = value[0]
    cursor.execute("update items set name = %s where id = %s", (new_item.name, index))
    conn.commit()
    conn.close()
    return {"message": "success"}

@app.post("/register")
def register(new_user : user_c):
    conn = get_db()
    cursor = conn.cursor()
    new_user.password=pwd_context.hash(new_user.password)
    cursor.execute("insert into users(username,password) values(%s,%s)",(new_user.username,new_user.password))
    conn.commit()
    conn.close()
    return{"message": "success"}

@app.post("/login")
def login(old_user : user_c):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from users where username = %s",(old_user.username,))
    fetch_user = cursor.fetchone()
    if fetch_user is None:
        raise HTTPException(status_code=401,detail="invalid user or password")
    validation=pwd_context.verify(old_user.password, fetch_user[2])
    if not validation:
        raise HTTPException(status_code=401,detail="invalid user or password")
    token = jwt.encode({"sub": old_user.username, "exp" : datetime.now(timezone.utc) + timedelta(minutes=15)}, s_key, algorithm=algo)
    return {"token": token}