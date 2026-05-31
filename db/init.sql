CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(50) UNIQUE NOT NULL,
    total_copies INTEGER NOT NULL CHECK (total_copies >= 0),
    available_copies INTEGER NOT NULL CHECK (available_copies >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (available_copies <= total_copies)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'borrowed',
    CHECK (status IN ('borrowed', 'returned', 'overdue'))
);

INSERT INTO books (title, author, isbn, total_copies, available_copies)
VALUES
    ('Clean Code', 'Robert C. Martin', '9780132350884', 5, 5),
    ('Database Systems', 'Thomas Connolly', '9780132943260', 3, 3),
    ('Flask Web Development', 'Miguel Grinberg', '9781491991732', 4, 4)
ON CONFLICT (isbn) DO NOTHING;

INSERT INTO users (name, email)
VALUES
    ('Ali Karimov', 'ali@example.com'),
    ('Sara Lee', 'sara@example.com')
ON CONFLICT (email) DO NOTHING;
