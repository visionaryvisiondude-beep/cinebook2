#!/usr/bin/env bash
# ============================================================
# CineBook — Full API test script
# Usage: bash test_api.sh
# Requires: curl, jq  (brew install jq / apt install jq)
# Server must be running at http://localhost:8000
# Run seed_demo first: python manage.py seed_demo
# ============================================================

BASE="http://localhost:8000/api"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

sep() { echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }
ok()  { echo -e "${GREEN}✓ $1${NC}"; }
hdr() { sep; echo -e "${YELLOW}▶ $1${NC}"; }

# ─── 1. REGISTER ────────────────────────────────────────────
hdr "1. Register new user"
REGISTER=$(curl -s -X POST "$BASE/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@cinebook.com",
    "phone": "9876543210",
    "password": "TestPass@123",
    "password2": "TestPass@123"
  }')
echo "$REGISTER" | jq .
ACCESS=$(echo "$REGISTER" | jq -r '.access')
REFRESH=$(echo "$REGISTER" | jq -r '.refresh')
ok "Registered. Access token acquired."

# ─── 2. LOGIN ───────────────────────────────────────────────
hdr "2. Login"
LOGIN=$(curl -s -X POST "$BASE/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@cinebook.com", "password": "TestPass@123"}')
echo "$LOGIN" | jq .
ACCESS=$(echo "$LOGIN" | jq -r '.access')
REFRESH=$(echo "$LOGIN" | jq -r '.refresh')
ok "Login successful."

AUTH="-H \"Authorization: Bearer $ACCESS\""

# ─── 3. GET PROFILE ─────────────────────────────────────────
hdr "3. Get profile"
curl -s "$BASE/auth/profile/" \
  -H "Authorization: Bearer $ACCESS" | jq .

# ─── 4. UPDATE PROFILE ──────────────────────────────────────
hdr "4. Patch profile"
curl -s -X PATCH "$BASE/auth/profile/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"phone": "9999999999"}' | jq .

# ─── 5. REFRESH TOKEN ───────────────────────────────────────
hdr "5. Refresh access token"
NEW_ACCESS=$(curl -s -X POST "$BASE/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH\"}" | jq -r '.access')
[ -n "$NEW_ACCESS" ] && ok "Token refreshed." || echo "Refresh failed"

# ══════════════════════════════════════════════════════════════
# MOVIES
# ══════════════════════════════════════════════════════════════

# ─── 6. LIST GENRES ─────────────────────────────────────────
hdr "6. List genres"
curl -s "$BASE/movies/genres/" | jq .

# ─── 7. LIST MOVIES ─────────────────────────────────────────
hdr "7. List all movies"
curl -s "$BASE/movies/" | jq .

# ─── 8. SEARCH MOVIES ───────────────────────────────────────
hdr "8. Search movies (?search=galactic)"
curl -s "$BASE/movies/?search=galactic" | jq .

# ─── 9. FILTER BY LANGUAGE ──────────────────────────────────
hdr "9. Filter movies by language=HI"
curl -s "$BASE/movies/?language=HI" | jq .

# ─── 10. MOVIE DETAIL ───────────────────────────────────────
hdr "10. Movie detail (id=1)"
curl -s "$BASE/movies/1/" | jq .

# ─── 11. SHOWTIMES FOR A MOVIE ──────────────────────────────
hdr "11. Showtimes for movie id=1"
SHOWTIMES=$(curl -s "$BASE/movies/1/showtimes/")
echo "$SHOWTIMES" | jq .
SHOWTIME_ID=$(echo "$SHOWTIMES" | jq -r '.results[0].id // .[0].id // 1')
ok "Using showtime id=$SHOWTIME_ID"

# ─── 12. ALL SHOWTIMES ──────────────────────────────────────
hdr "12. All showtimes"
curl -s "$BASE/movies/showtimes/" | jq '.results[:2]'

# ─── 13. LIST THEATRES ──────────────────────────────────────
hdr "13. List theatres"
curl -s "$BASE/movies/theatres/" | jq .

# ─── 14. THEATRE DETAIL ─────────────────────────────────────
hdr "14. Theatre detail (id=1)"
curl -s "$BASE/movies/theatres/1/" | jq .

# ══════════════════════════════════════════════════════════════
# SEATS
# ══════════════════════════════════════════════════════════════

# ─── 15. SEAT MAP ───────────────────────────────────────────
hdr "15. Seat map for showtime id=$SHOWTIME_ID"
SEAT_MAP=$(curl -s "$BASE/seats/showtime/$SHOWTIME_ID/")
echo "$SEAT_MAP" | jq '{showtime_id, movie, start_time, price_regular, price_premium}'
# Pick first two available seat ids from row A
SEAT1=$(echo "$SEAT_MAP" | jq -r '.rows.A[0].seat.id')
SEAT2=$(echo "$SEAT_MAP" | jq -r '.rows.A[1].seat.id')
ok "Will use seat ids: $SEAT1, $SEAT2"

# ─── 16. LOCK SEATS ─────────────────────────────────────────
hdr "16. Lock seats $SEAT1 and $SEAT2"
LOCK=$(curl -s -X POST "$BASE/seats/showtime/$SHOWTIME_ID/lock/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"seat_ids\": [$SEAT1, $SEAT2]}")
echo "$LOCK" | jq .
ok "Seats locked for 5 minutes."

# ─── 17. SEAT MAP AFTER LOCK ────────────────────────────────
hdr "17. Seat map after locking (is_locked_by_me should be true)"
curl -s "$BASE/seats/showtime/$SHOWTIME_ID/" \
  -H "Authorization: Bearer $ACCESS" | jq '.rows.A[:2]'

# ══════════════════════════════════════════════════════════════
# BOOKINGS
# ══════════════════════════════════════════════════════════════

# ─── 18. CREATE BOOKING ─────────────────────────────────────
hdr "18. Create booking"
BOOKING=$(curl -s -X POST "$BASE/bookings/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"showtime_id\": $SHOWTIME_ID, \"seat_ids\": [$SEAT1, $SEAT2]}")
echo "$BOOKING" | jq .
BOOKING_REF=$(echo "$BOOKING" | jq -r '.booking_ref')
ok "Booking ref: $BOOKING_REF"

# ─── 19. MY BOOKINGS ────────────────────────────────────────
hdr "19. My bookings"
curl -s "$BASE/bookings/my/" \
  -H "Authorization: Bearer $ACCESS" | jq .

# ─── 20. BOOKING DETAIL ─────────────────────────────────────
hdr "20. Booking detail"
curl -s "$BASE/bookings/$BOOKING_REF/" \
  -H "Authorization: Bearer $ACCESS" | jq .

# ══════════════════════════════════════════════════════════════
# PAYMENTS
# ══════════════════════════════════════════════════════════════

# ─── 21. INITIATE PAYMENT ───────────────────────────────────
hdr "21. Initiate payment"
PAYMENT=$(curl -s -X POST "$BASE/payments/initiate/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"booking_ref\": \"$BOOKING_REF\"}")
echo "$PAYMENT" | jq .
PAYMENT_ID=$(echo "$PAYMENT" | jq -r '.payment_id')
ok "Payment initiated: $PAYMENT_ID"

# ─── 22. CONFIRM PAYMENT ────────────────────────────────────
hdr "22. Confirm payment (mock)"
CONFIRM=$(curl -s -X POST "$BASE/payments/confirm/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{
    \"payment_id\": \"$PAYMENT_ID\",
    \"gateway_payment_id\": \"pay_mock_$(date +%s)\",
    \"gateway_signature\": \"sig_mock\"
  }")
echo "$CONFIRM" | jq .
ok "Booking should now be CONFIRMED."

# ─── 23. PAYMENT STATUS ─────────────────────────────────────
hdr "23. Payment status"
curl -s "$BASE/payments/status/$PAYMENT_ID/" \
  -H "Authorization: Bearer $ACCESS" | jq .

# ─── 24. BOOKING DETAIL AFTER PAYMENT ───────────────────────
hdr "24. Booking detail after payment (status=confirmed)"
curl -s "$BASE/bookings/$BOOKING_REF/" \
  -H "Authorization: Bearer $ACCESS" | jq '{booking_ref, status, total_amount}'

# ══════════════════════════════════════════════════════════════
# CANCEL FLOW (second booking)
# ══════════════════════════════════════════════════════════════

hdr "25. Lock different seats for a second booking"
SEAT3=$(curl -s "$BASE/seats/showtime/$SHOWTIME_ID/" | jq -r '.rows.B[0].seat.id')
SEAT4=$(curl -s "$BASE/seats/showtime/$SHOWTIME_ID/" | jq -r '.rows.B[1].seat.id')
curl -s -X POST "$BASE/seats/showtime/$SHOWTIME_ID/lock/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"seat_ids\": [$SEAT3, $SEAT4]}" | jq .

hdr "26. Create second booking (to test cancellation)"
BOOKING2=$(curl -s -X POST "$BASE/bookings/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"showtime_id\": $SHOWTIME_ID, \"seat_ids\": [$SEAT3, $SEAT4]}")
echo "$BOOKING2" | jq .
BOOKING_REF2=$(echo "$BOOKING2" | jq -r '.booking_ref')

hdr "27. Cancel second booking"
curl -s -X POST "$BASE/bookings/$BOOKING_REF2/cancel/" \
  -H "Authorization: Bearer $ACCESS" | jq .
ok "Seats freed, cancellation email queued."

# ─── 28. UNLOCK SEATS (cart-abandon demo) ───────────────────
hdr "28. Unlock seats explicitly (cart abandon)"
curl -s -X POST "$BASE/seats/showtime/$SHOWTIME_ID/unlock/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"seat_ids\": [$SEAT1]}" | jq .

# ─── 29. LOGOUT ─────────────────────────────────────────────
hdr "29. Logout (blacklist refresh token)"
curl -s -X POST "$BASE/auth/logout/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH\"}" | jq .

sep
echo -e "${GREEN}All endpoints tested successfully!${NC}"
echo ""
echo "Full endpoint list:"
echo "  POST   $BASE/auth/register/"
echo "  POST   $BASE/auth/login/"
echo "  POST   $BASE/auth/logout/"
echo "  POST   $BASE/auth/token/refresh/"
echo "  GET    $BASE/auth/profile/"
echo "  PATCH  $BASE/auth/profile/"
echo "  POST   $BASE/auth/change-password/"
echo "  GET    $BASE/movies/"
echo "  GET    $BASE/movies/{id}/"
echo "  GET    $BASE/movies/?search=&language=&genres="
echo "  GET    $BASE/movies/{id}/showtimes/"
echo "  GET    $BASE/movies/showtimes/"
echo "  GET    $BASE/movies/showtimes/{id}/"
echo "  GET    $BASE/movies/genres/"
echo "  GET    $BASE/movies/theatres/"
echo "  GET    $BASE/movies/theatres/{id}/"
echo "  GET    $BASE/seats/showtime/{id}/"
echo "  POST   $BASE/seats/showtime/{id}/lock/"
echo "  POST   $BASE/seats/showtime/{id}/unlock/"
echo "  POST   $BASE/bookings/"
echo "  GET    $BASE/bookings/my/"
echo "  GET    $BASE/bookings/{ref}/"
echo "  POST   $BASE/bookings/{ref}/cancel/"
echo "  POST   $BASE/payments/initiate/"
echo "  POST   $BASE/payments/confirm/"
echo "  GET    $BASE/payments/status/{id}/"
