
# Project Title
This is a simple yet efficient ToDo API built using FastAPI, designed for managing tasks with authentication and CRUD functionalities.The API allows users to register, log in, create, update, delete, and retrieve tasks securely. It leverages FastAPI’s speed and automatic documentation while integrating authentication mechanisms for user-based task management.

&nbsp; 
# 🚀 Features

✅ User Authentication (JWT-based)

✅ Task Management (Create, Read, Update, Delete tasks)

✅ Secure Password Hashing (Passlib with bcrypt)

✅ MongoDB Integration (Async operations using Motor)

✅ Automatic API Documentation (Swagger)

&nbsp; 
# 🛠 Tech Stack 

- FastAPI - Web framework for high-performance APIs

- Motor - Async MongoDB driver      

- JWT (JSON Web Tokens) - Secure authentication

- Passlib - Password hashing with bcrypt

- Uvicorn - ASGI server for running FastAPI

- Pydantic - Data validation and serialization








&nbsp; 
# 📦 Installation


All required dependencies are listed in requirements.txt,


To install them, run:

~~~cmd
  pip install -r requirements.txt
~~~

To start the FastAPI server, use:
~~~
  uvicorn main:app --reload
~~~

&nbsp; 
# 📌 API Endpoints

🔑 Authentication

| Method | Endpoint       | Description                      |
|--------|---------------|----------------------------------|
| **POST** | `/register`   | Register a new user            |
| **POST** | `/token`      | Log in and receive an access token |

✅ **Task Management**

| Method   | Endpoint         | Description            |
|----------|-----------------|------------------------|
| **POST**   | `/tasks/`        | Create a new task     |
| **GET**    | `/tasks/`        | Retrieve all tasks    |
| **PUT**    | `/tasks/{task_id}` | Update an existing task |
| **DELETE** | `/tasks/{task_id}` | Delete a task        |
