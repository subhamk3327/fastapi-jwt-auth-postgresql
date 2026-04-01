"""
Inventory Management API with JWT Authentication
FastAPI + PostgreSQL + JWT tokens
"""

import psycopg2
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

# reads secret key from env variables(keeps secrets out of the code)

s_key = os.getenv("SECRET_KEY")
algo = "HS256"

#hashing password for safety with Bcrypt
#Password hashing uses salt which cant be reversed even if breached
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

app = FastAPI()

#connects to Postgresql using Database_url from environment
#workd for both local dev(.env) and production(railway)
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

#Gets all the items from database after verification of token
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

#Add a new item in the database protected by jwt auth
@app.post("/items")
def post_items(new_item: item_c,token : str=Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,s_key,algorithms=[algo])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401,detail="unauthorised")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("insert into items(name) values (%s)", (new_item.name,))
    conn.commit()
    conn.close()
    return {"message": "success"}

#delete an item in the database protected by jwt auth
@app.delete("/items/{old_item}")
def delete_item(old_item: str, token:str=Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,s_key,algorithms=[algo])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="unauthorised")
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

#replace an existing item protected by jwt auth
@app.put("/items/{old_item}")
def put_items(old_item: str, new_item: item_c, token: str=Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,s_key,algorithms=[algo])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="unauthorised")
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

#Register new User for Fastapi app
#uses bcrypt to hash the password
@app.post("/register")
def register(new_user : user_c):
    conn = get_db()
    cursor = conn.cursor()
    new_user.password=pwd_context.hash(new_user.password)
    cursor.execute("insert into users(username,password) values(%s,%s)",(new_user.username,new_user.password))
    conn.commit()
    conn.close()
    return{"message": "success"}

#Login for already registered users
#15 minute jwt auth expiry if token breached
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