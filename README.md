# College Management FastAPI App

This project shows a clean, modular FastAPI folder structure for a small college API.
It uses **SQLite** with **SQLAlchemy** so students, courses, and enrollments are saved
in a local `college.db` database file.

## Project Structure

```text
app/
  main.py
  database.py
  models.py
  api/
    v1/
      router.py
      routers/
        students.py
        courses.py
        enrollments.py
  schemas/
    auth.py
    student.py
    course.py
    enrollment.py
  services/
    auth_service.py
    student_service.py
    course_service.py
    enrollment_service.py
requirements.txt
```

## Database

The app uses SQLite:

```text
sqlite:///./college.db
```

The database tables are created automatically when the FastAPI app starts.

### Tables

```text
students
- id
- name
- email
- age

courses
- id
- name
- description
- duration

enrollments
- id
- student_id
- course_id

users
- id
- email
- full_name
- hashed_password
- role
```

### Constraints

- Student email must be unique.
- Course name must be unique.
- A student cannot be enrolled in the same course more than once.
- If a duplicate student email is used, the API returns `409 Conflict`.
- If a duplicate course name is used, the API returns `409 Conflict`.
- If a requested student or course does not exist, the API returns `404 Not Found`.

## Authentication and Authorization

The API uses bearer tokens for authentication. Register a user, log in, and send the
returned token in the `Authorization` header:

```text
Authorization: Bearer <access_token>
```

Roles:

- `admin` can create, update, and delete students and courses, and can create enrollments.
- `student` can access authenticated read routes.

Passwords are stored as PBKDF2 hashes. Tokens are signed with HS256 in the service
layer; change `SECRET_KEY` in `app/services/auth_service.py` before using this beyond
local development.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the docs at:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

- `POST /api/v1/auth/register` registers a user.
- `POST /api/v1/auth/login` logs a user in and returns a bearer token.
- `GET /api/v1/auth/me` gets the authenticated user's profile.
- `POST /api/v1/students/` registers a student.
- `GET /api/v1/students/` lists students.
- `GET /api/v1/students/{student_id}` gets one student.
- `PUT /api/v1/students/{student_id}` updates one student.
- `DELETE /api/v1/students/{student_id}` deletes one student.
- `POST /api/v1/courses/` registers a course.
- `GET /api/v1/courses/` lists courses.
- `GET /api/v1/courses/{course_id}` gets one course.
- `PUT /api/v1/courses/{course_id}` updates one course.
- `DELETE /api/v1/courses/{course_id}` deletes one course.
- `POST /api/v1/enrollments/` enrolls a student in a course.
- `GET /api/v1/enrollments/students/{student_id}` lists course IDs for a student.
- `GET /api/v1/enrollments/courses/{course_id}` lists student IDs for a course.
