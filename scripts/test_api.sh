#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:5000}"

echo "1. Health check"
curl -s "$BASE_URL/health"
echo

echo "2. Add a book"
curl -s -X POST "$BASE_URL/books" \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"Robert C. Martin","isbn":"9780132350884-extra","total_copies":5}'
echo

echo "3. List books"
curl -s "$BASE_URL/books"
echo

echo "4. Register a user"
curl -s -X POST "$BASE_URL/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ali Karimov","email":"ali.test@example.com"}'
echo

echo "5. List users"
curl -s "$BASE_URL/users"
echo

echo "6. Borrow a book"
curl -s -X POST "$BASE_URL/loans" \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"user_id":1,"due_date":"2026-06-15"}'
echo

echo "7. List loans"
curl -s "$BASE_URL/loans"
echo

echo "8. Return first loan"
curl -s -X PUT "$BASE_URL/loans/1/return"
echo

echo "9. Check overdue loans"
curl -s "$BASE_URL/loans/overdue"
echo

echo "10. Check user history"
curl -s "$BASE_URL/users/1/history"
echo
