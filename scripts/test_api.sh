#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:5000}"

echo "1. Health check"
curl -s "$BASE_URL/health"
echo
echo

echo "2. Add a new book"
curl -s -X POST "$BASE_URL/books" \
  -H "Content-Type: application/json" \
  -d '{"title":"Python for Data Analysis","author":"Wes McKinney","isbn":"9781491957660-test","total_copies":3}'
echo
echo

echo "3. List books"
curl -s "$BASE_URL/books"
echo
echo

echo "4. Register a new user"
curl -s -X POST "$BASE_URL/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Student","email":"test.student@example.com"}'
echo
echo

echo "5. List users"
curl -s "$BASE_URL/users"
echo
echo

echo "6. Borrow a book with future due date"
curl -s -X POST "$BASE_URL/loans" \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"user_id":1,"due_date":"2026-06-15"}'
echo
echo

echo "7. Borrow a book with past due date for overdue test"
curl -s -X POST "$BASE_URL/loans" \
  -H "Content-Type: application/json" \
  -d '{"book_id":2,"user_id":2,"due_date":"2024-01-01"}'
echo
echo

echo "8. List all loans"
curl -s "$BASE_URL/loans"
echo
echo

echo "9. Check overdue loans"
curl -s "$BASE_URL/loans/overdue"
echo
echo

echo "10. Check user history"
curl -s "$BASE_URL/users/1/history"
echo
echo
