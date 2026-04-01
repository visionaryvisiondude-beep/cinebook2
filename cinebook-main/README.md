# CineBook — Cinema Booking Backend

Django REST Framework backend for a full-stack cinema booking system.

## Tech Stack
- **Django 4.2** + Django REST Framework
- **JWT Auth** via `djangorestframework-simplejwt`
- **PostgreSQL** (SQLite for local dev)
- **Redis** — seat locking cache + Celery broker
- **Celery** — async email notifications
- **Docker + docker-compose**

---

## Quick Start (Local Dev — no Docker)

```bash
# 1. Clone and set up venv
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — for local dev leave DB as SQLite (default), comment out DB_* lines

# 3. Run migrations
python manage.py migrate

# 4. Create superuser (for Django admin)
python manage.py createsuperuser

# 5. Seed demo data (movies, theatres, showtimes)
python manage.py seed_demo

# 6. Start dev server
python manage.py runserver
```

API available at: `http://localhost:8000/api/`
Admin panel: `http://localhost:8000/admin/`

---

## Quick Start (Docker — full stack with PostgreSQL + Redis)

```bash
cp .env.example .env
docker-compose up --build

# In a new terminal:
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py seed_demo
```

---

## API Reference

### Auth
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Register new user |
| POST | `/api/auth/login/` | No | Login → JWT tokens |
| POST | `/api/auth/logout/` | Yes | Blacklist refresh token |
| POST | `/api/auth/token/refresh/` | No | Refresh access token |
| GET/PUT | `/api/auth/profile/` | Yes | Get or update profile |
| POST | `/api/auth/change-password/` | Yes | Change password |

### Movies
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/movies/` | No | List movies (search, filter by genre/language) |
| GET | `/api/movies/{id}/` | No | Movie detail |
| GET | `/api/movies/{id}/showtimes/` | No | Showtimes for a movie |
| GET | `/api/movies/showtimes/` | No | All showtimes (filter by movie, theatre) |
| GET | `/api/movies/theatres/` | No | List theatres |
| GET | `/api/movies/genres/` | No | List genres |

### Seats
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/seats/showtime/{id}/` | No | Full seat map with availability |
| POST | `/api/seats/showtime/{id}/lock/` | Yes | Lock seats (5 min Redis TTL) |
| POST | `/api/seats/showtime/{id}/unlock/` | Yes | Release locks on cart abandon |

### Bookings
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/bookings/` | Yes | Create booking (from locked seats) |
| GET | `/api/bookings/my/` | Yes | User's booking history |
| GET | `/api/bookings/{ref}/` | Yes | Single booking detail |
| POST | `/api/bookings/{ref}/cancel/` | Yes | Cancel booking |

### Payments
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/payments/initiate/` | Yes | Initiate payment (mock/Razorpay) |
| POST | `/api/payments/confirm/` | Yes | Confirm payment + confirm booking |
| GET | `/api/payments/status/{id}/` | Yes | Payment status |

---

## Booking Flow

```
1. Browse movies → GET /api/movies/
2. Choose showtime → GET /api/movies/{id}/showtimes/
3. View seat map → GET /api/seats/showtime/{id}/
4. Lock seats → POST /api/seats/showtime/{id}/lock/   (5-min timer starts)
5. Create booking → POST /api/bookings/
6. Initiate payment → POST /api/payments/initiate/
7. Confirm payment → POST /api/payments/confirm/
8. Get confirmation email (via Celery async task)
```

---

## Project Structure

```
cinebook/
├── cinebook/          # Project config (settings, urls, celery)
├── users/             # Custom user model, JWT auth
├── movies/            # Movie, Theatre, Screen, Showtime models
├── seats/             # Seat map, Redis locking
├── bookings/          # Atomic booking creation, Celery tasks
├── payments/          # Mock/Razorpay payment flow
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Resume Highlights
- **Redis seat locking** — prevents double-booking with atomic TTL-based locks
- **Celery async tasks** — non-blocking email confirmations
- **JWT authentication** — stateless auth with refresh token rotation
- **Atomic DB transactions** — booking + seat status update in single transaction
- **Dockerised** — full stack in one `docker-compose up`
- **Django admin** — full management UI out of the box
