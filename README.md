# Library Service API

A web-based library management system that allows users to borrow books and make payments online.

## Features

- 📚 Books inventory management
- 👤 User authentication with JWT
- 📖 Book borrowing system
- 💳 Payment tracking
- 📄 API documentation with Swagger

## Technologies

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- Docker
- JWT Authentication (SimpleJWT)
- Swagger (drf-spectacular)

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
```bash
  git clone https://github.com/ArturDrzazga/LibraryServiceAPI.git
  cd LibraryServiceAPI
```

2. Create `.env` file based on `.env.sample`:
```bash
  cp .env.sample .env
```

3. Fill in the `.env` file with your values

4. Run the application:
```bash
  docker-compose up --build
```

5. Access the API documentation at:
   http://localhost:8000/api/doc/


## API Endpoints

### Books
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | api/books/ | List all books | Anyone |
| POST | api/books/ | Create a book | Admin only |
| GET | api/books/{id}/ | Get book details | Anyone |
| PUT/PATCH | api/books/{id}/ | Update a book | Admin only |
| DELETE | api/books/{id}/ | Delete a book | Admin only |

### Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | api/users/register/ | Register a new user | Anyone |
| POST | api/users/token/ | Get JWT tokens | Anyone |
| POST | api/users/token/refresh/ | Refresh JWT token | Anyone |
| GET | api/users/me/ | Get my profile | Authenticated |
| PUT/PATCH | api/users/me/ | Update my profile | Authenticated |

### Borrowings
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | api/borrowings/ | List borrowings | Authenticated |
| POST | api/borrowings/ | Create borrowing | Authenticated |
| GET | api/borrowings/{id}/ | Get borrowing details | Authenticated |
| POST | api/borrowings/{id}/return/ | Return a book | Authenticated |

#### Borrowings filters:
- `?is_active=true` — show only active borrowings
- `?is_active=false` — show only returned borrowings
- `?user_id={id}` — filter by user (admin only)

### Payments
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | api/payments/ | List payments | Authenticated |
| GET | api/payments/{id}/ | Get payment details | Authenticated |

## Environment Variables

```env
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## Running Tests

```bash
  python manage.py test
```

## Coming Soon

- 🔔 Telegram notifications for new borrowings and overdue alerts
- 💳 Stripe payment integration
- 💰 Fine system for overdue returns
- ⏰ Daily overdue check with Celery
- 🐳 Full Docker setup with Redis and Celery
- ⭐ GitHub Actions CI/CD pipeline
