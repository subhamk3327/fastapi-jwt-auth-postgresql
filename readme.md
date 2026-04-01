# Inventory Management API
An API for managing inventory items secured with Jwt Authentication

## Features
- User Registration and Login with password hashing
- Full CRUD operation on items
- JWT based authentication(15 minutes expiry)
- Postgresql for data storage
- deployed on railway

## Tech stack
- Fastapi (python)
- bcrypt (password hashing)
- python-jose (JWT authentication)
- Postgresql (for database)

## Setup

### Requirements
- Python 3.12 and above
- Postgresql installed and running

### Installation
1. clone the Repository
```bash
git clone https://github.com/subhamk3327/fastapi-jwt-auth-postgresql.git
cd fastapi-jwt-auth-postgresql
```
(clones the code onto your pc and then switches the terminal to current code folder)

2. Install dependencies:
```bash
python -m pip install -r requirements.txt
```
(Installs required dependencies to run the code)

3. Create a '.env' file with:
```
SECRET_KEY = insert_your_secret_key_here
DATABASE_URL = postgresql://postgres:your_password@localhost:5432/itemsdb
```
(create a file with extension of .env and edit it with notepad/editor with the above lines. change the phrase according to your secret key and postgres password pls)

4.Create database tables with the following:
``` sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
```
(Sets-up the database)

5. Run server with the following command: 
```bash
python -m uvicorn pg_main:app --reload
```
(starts local server with the url - `http://127.0.0.1:8000`)

## Deployment

Deployed on Railway: [https://web-production-5ad5.up.railway.app/](https://web-production-5ad5.up.railway.app/)

### Deploy Your Own

1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Add PostgreSQL service on Railway
4. Set environment variables in Railway dashboard
5. Railway auto-deploys on every push

