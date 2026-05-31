import os
import time
from datetime import date

import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor


app = Flask(__name__)


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "database": os.getenv("DB_NAME", "library_db"),
    "user": os.getenv("DB_USER", "library_user"),
    "password": os.getenv("DB_PASSWORD", "library_password"),
    "port": int(os.getenv("DB_PORT", "5432")),
}


def get_connection(retries=10, delay=2):
    last_error = None
    for _ in range(retries):
        try:
            return psycopg2.connect(**DB_CONFIG)
        except psycopg2.OperationalError as exc:
            last_error = exc
            time.sleep(delay)
    raise last_error


def row_to_dict(row):
    result = dict(row)
    for key, value in result.items():
        if isinstance(value, date):
            result[key] = value.isoformat()
    return result


def rows_to_json(rows):
    return [row_to_dict(row) for row in rows]


def error_response(message, status_code):
    return jsonify({"error": message}), status_code


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running", "service": "Library Management API"})


@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True) or {}
    required_fields = ["title", "author", "isbn", "total_copies"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", 400)

    try:
        total_copies = int(data["total_copies"])
    except (TypeError, ValueError):
        return error_response("total_copies must be a number", 400)

    if total_copies < 1:
        return error_response("total_copies must be at least 1", 400)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO books (title, author, isbn, total_copies, available_copies)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (data["title"], data["author"], data["isbn"], total_copies, total_copies),
            )
            book = cur.fetchone()
    return jsonify(row_to_dict(book)), 201


@app.route("/books", methods=["GET"])
def list_books():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM books ORDER BY id")
            books = cur.fetchall()
    return jsonify(rows_to_json(books))


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            book = cur.fetchone()
    if not book:
        return error_response("Book not found", 404)
    return jsonify(row_to_dict(book))


@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json(silent=True) or {}
    required_fields = ["title", "author", "isbn", "total_copies"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", 400)

    try:
        new_total = int(data["total_copies"])
    except (TypeError, ValueError):
        return error_response("total_copies must be a number", 400)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT total_copies, available_copies
                FROM books
                WHERE id = %s
                FOR UPDATE
                """,
                (book_id,),
            )
            book = cur.fetchone()
            if not book:
                return error_response("Book not found", 404)

            borrowed_count = book["total_copies"] - book["available_copies"]
            if new_total < borrowed_count:
                return error_response(
                    "total_copies cannot be lower than the number of borrowed copies",
                    400,
                )

            new_available = new_total - borrowed_count
            cur.execute(
                """
                UPDATE books
                SET title = %s,
                    author = %s,
                    isbn = %s,
                    total_copies = %s,
                    available_copies = %s
                WHERE id = %s
                RETURNING *
                """,
                (
                    data["title"],
                    data["author"],
                    data["isbn"],
                    new_total,
                    new_available,
                    book_id,
                ),
            )
            updated = cur.fetchone()
    return jsonify(row_to_dict(updated))


@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS active_loans
                FROM loans
                WHERE book_id = %s AND status = 'borrowed'
                """,
                (book_id,),
            )
            if cur.fetchone()["active_loans"] > 0:
                return error_response("Cannot delete a book with active borrowed loans", 409)

            cur.execute("DELETE FROM books WHERE id = %s RETURNING id", (book_id,))
            deleted = cur.fetchone()
    if not deleted:
        return error_response("Book not found", 404)
    return jsonify({"message": "Book deleted", "book_id": book_id})


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    required_fields = ["name", "email"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", 400)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (data["email"],))
            if cur.fetchone():
                return error_response("A user with this email already exists", 409)

            cur.execute(
                """
                INSERT INTO users (name, email)
                VALUES (%s, %s)
                RETURNING *
                """,
                (data["name"], data["email"]),
            )
            user = cur.fetchone()
    return jsonify(row_to_dict(user)), 201


@app.route("/users", methods=["GET"])
def list_users():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users ORDER BY id")
            users = cur.fetchall()
    return jsonify(rows_to_json(users))


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
    if not user:
        return error_response("User not found", 404)
    return jsonify(row_to_dict(user))


@app.route("/users/<int:user_id>/history", methods=["GET"])
def user_history(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cur.fetchone():
                return error_response("User not found", 404)

            cur.execute(
                """
                SELECT
                    b.title AS book_title,
                    l.loan_date,
                    l.due_date,
                    l.return_date,
                    CASE
                        WHEN l.return_date IS NULL AND l.due_date < CURRENT_DATE THEN 'overdue'
                        ELSE l.status
                    END AS status
                FROM loans l
                JOIN books b ON b.id = l.book_id
                WHERE l.user_id = %s
                ORDER BY l.loan_date DESC, l.id DESC
                """,
                (user_id,),
            )
            history = cur.fetchall()
    return jsonify(rows_to_json(history))


@app.route("/loans", methods=["POST"])
def create_loan():
    data = request.get_json(silent=True) or {}
    required_fields = ["book_id", "user_id", "due_date"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", 400)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM books WHERE id = %s FOR UPDATE",
                (data["book_id"],),
            )
            book = cur.fetchone()
            if not book:
                return error_response("Book not found", 404)
            if book["available_copies"] <= 0:
                return error_response("No available copies for this book", 409)

            cur.execute("SELECT id FROM users WHERE id = %s", (data["user_id"],))
            if not cur.fetchone():
                return error_response("User not found", 404)

            cur.execute(
                """
                INSERT INTO loans (book_id, user_id, due_date, status)
                VALUES (%s, %s, %s, 'borrowed')
                RETURNING *
                """,
                (data["book_id"], data["user_id"], data["due_date"]),
            )
            loan = cur.fetchone()

            cur.execute(
                """
                UPDATE books
                SET available_copies = available_copies - 1
                WHERE id = %s
                """,
                (data["book_id"],),
            )
    return jsonify(row_to_dict(loan)), 201


@app.route("/loans", methods=["GET"])
def list_loans():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    l.*,
                    b.title AS book_title,
                    u.name AS user_name,
                    u.email AS user_email
                FROM loans l
                JOIN books b ON b.id = l.book_id
                JOIN users u ON u.id = l.user_id
                ORDER BY l.id
                """
            )
            loans = cur.fetchall()
    return jsonify(rows_to_json(loans))


@app.route("/loans/<int:loan_id>/return", methods=["PUT"])
def return_book(loan_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM loans WHERE id = %s FOR UPDATE",
                (loan_id,),
            )
            loan = cur.fetchone()
            if not loan:
                return error_response("Loan not found", 404)
            if loan["return_date"] is not None or loan["status"] == "returned":
                return error_response("This loan has already been returned", 409)

            cur.execute(
                """
                UPDATE loans
                SET return_date = CURRENT_DATE,
                    status = 'returned'
                WHERE id = %s
                RETURNING *
                """,
                (loan_id,),
            )
            returned_loan = cur.fetchone()

            cur.execute(
                """
                UPDATE books
                SET available_copies = available_copies + 1
                WHERE id = %s
                """,
                (loan["book_id"],),
            )
    return jsonify({"message": "Book returned", "loan": row_to_dict(returned_loan)})


@app.route("/loans/overdue", methods=["GET"])
def overdue_loans():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE loans
                SET status = 'overdue'
                WHERE return_date IS NULL
                  AND due_date < CURRENT_DATE
                  AND status = 'borrowed'
                """
            )
            cur.execute(
                """
                SELECT
                    l.id AS loan_id,
                    b.title AS book_title,
                    u.name AS user_name,
                    u.email AS user_email,
                    l.due_date,
                    l.status
                FROM loans l
                JOIN books b ON b.id = l.book_id
                JOIN users u ON u.id = l.user_id
                WHERE l.return_date IS NULL
                  AND l.due_date < CURRENT_DATE
                ORDER BY l.due_date
                """
            )
            overdue = cur.fetchall()
    return jsonify(rows_to_json(overdue))


@app.errorhandler(psycopg2.Error)
def handle_database_error(exc):
    return error_response(f"Database error: {exc.pgerror or exc}", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
