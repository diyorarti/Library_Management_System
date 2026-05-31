# Library Management System

## 1. Project Description

The Library Management System is a small academic library application built with Flask, PostgreSQL, Adminer, and Docker Compose. It provides a REST API for managing books, registered library users, book loans, overdue books, and user borrowing history.

## 2. Real-life Application

This project can be used by a university or school library to automate book registration, student registration, book borrowing, book returning, and overdue loan tracking.

## 3. Technologies Used

- Python 3.12
- Flask
- PostgreSQL
- Adminer
- Docker
- Docker Compose
- Bash and curl for API testing

## 4. Architecture

```text
+-------------------+
|  User / Postman   |
|  curl / Browser   |
+---------+---------+
          |
          v
+-------------------+
|   Flask REST API  |
|   Container       |
|   Port: 5000      |
+---------+---------+
          |
          | Docker network
          v
+-------------------+
|   PostgreSQL DB   |
|   Container       |
|   Port: 5432      |
+---------+---------+
          |
          v
+-------------------+
| Docker Volume     |
| Persistent Data   |
+-------------------+

+-------------------+
| Adminer GUI       |
| Port: 8080        |
| Manages DB        |
+-------------------+
```

## 5. Containers

| Container | Service | Description | Port |
| --- | --- | --- | --- |
| `library_api` | `flask-api` | Custom Flask REST API built from `app/Dockerfile` | `5000` |
| `library_db` | `db` | PostgreSQL database with persistent storage | `5432` |
| `library_adminer` | `adminer` | Browser-based database management GUI | `8080` |

## 6. Database Schema

### books

Stores book information.

| Column | Description |
| --- | --- |
| `id` | Primary key |
| `title` | Book title |
| `author` | Book author |
| `isbn` | Unique ISBN |
| `total_copies` | Total copies owned by library |
| `available_copies` | Copies currently available |
| `created_at` | Creation timestamp |

### users

Stores library users or students.

| Column | Description |
| --- | --- |
| `id` | Primary key |
| `name` | User name |
| `email` | Unique user email |
| `created_at` | Creation timestamp |

### loans

Stores borrowing records.

| Column | Description |
| --- | --- |
| `id` | Primary key |
| `book_id` | Borrowed book |
| `user_id` | Borrowing user |
| `loan_date` | Borrow date |
| `due_date` | Due date |
| `return_date` | Return date, if returned |
| `status` | `borrowed`, `returned`, or `overdue` |

## 7. API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Check API status |
| `POST` | `/books` | Add a new book |
| `GET` | `/books` | List all books |
| `GET` | `/books/<id>` | Get one book |
| `PUT` | `/books/<id>` | Update a book |
| `DELETE` | `/books/<id>` | Delete a book if it has no active loans |
| `POST` | `/users` | Register a new user |
| `GET` | `/users` | List all users |
| `GET` | `/users/<id>` | Get one user |
| `GET` | `/users/<id>/history` | View user borrowing history |
| `POST` | `/loans` | Borrow a book |
| `GET` | `/loans` | List all loans |
| `PUT` | `/loans/<id>/return` | Return a borrowed book |
| `GET` | `/loans/overdue` | List overdue loans |

## 8. How to Run the Project

Build and start all services:

```bash
docker compose up --build
```

The services will be available at:

- Flask API: <http://localhost:5000>
- Adminer: <http://localhost:8080>
- PostgreSQL: `localhost:5432`

Check running containers:

```bash
docker ps
```

Expected container names:

- `library_api`
- `library_db`
- `library_adminer`

Stop the project:

```bash
docker compose down
```

Stop the project and remove database volume:

```bash
docker compose down -v
```

## 9. How to Test the API

Health check:

```bash
curl http://localhost:5000/health
```

Add a book:

```bash
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"Robert C. Martin","isbn":"9780132350884","total_copies":5}'
```

List books:

```bash
curl http://localhost:5000/books
```

Register a user:

```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Ali Karimov","email":"ali@example.com"}'
```

List users:

```bash
curl http://localhost:5000/users
```

Borrow a book:

```bash
curl -X POST http://localhost:5000/loans \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"user_id":1,"due_date":"2026-06-15"}'
```

List loans:

```bash
curl http://localhost:5000/loans
```

Return a book:

```bash
curl -X PUT http://localhost:5000/loans/1/return
```

Check overdue books:

```bash
curl http://localhost:5000/loans/overdue
```

Check user history:

```bash
curl http://localhost:5000/users/1/history
```

You can also run the included test script:

```bash
bash scripts/test_api.sh
```

## 10. How to Use Adminer

Open Adminer in a browser:

```text
http://localhost:8080
```

Login details:

| Field | Value |
| --- | --- |
| System | `PostgreSQL` |
| Server | `db` |
| Username | `library_user` |
| Password | `library_password` |
| Database | `library_db` |

In Adminer, you can view the `books`, `users`, and `loans` tables, inspect sample data, and confirm that loan operations update `available_copies`.

## 11. Screenshots

Recommended screenshots for submission:

1. `docker compose up --build` running successfully
2. `docker ps` showing all three containers
3. `/health` endpoint response
4. `POST /books` response
5. `POST /users` response
6. `POST /loans` response
7. Adminer login page
8. Adminer showing `books`, `users`, and `loans`
9. `GET /users/1/history` response
10. `GET /loans/overdue` response

Save screenshots in the `screenshots/` folder.

## 12. Final Checklist Before Submission

Run these commands and make sure they work:

```bash
docker compose up --build
docker ps
curl http://localhost:5000/health
curl http://localhost:5000/books
bash scripts/test_api.sh
```

Open Adminer:

```text
http://localhost:8080
```

Login details:

| Field | Value |
| --- | --- |
| System | `PostgreSQL` |
| Server | `db` |
| Username | `library_user` |
| Password | `library_password` |
| Database | `library_db` |

After logging in, confirm these tables exist:

- `books`
- `users`
- `loans`

## 13. Author

Prepared as a Docker Compose final project for an academic library management use case.
