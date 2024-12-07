# Multi-Backend Application

## Database Structure
- accounts table
- services table
- reviews table
- media folder
- hashtags table

## Features
- Account management
- Service listings
- Reviews and ratings
- Hashtag system
- Search functionality

## Backend Implementations
This application has three equivalent backend implementations:

### FastAPI Backend (Python)
```bash
# Start PostgreSQL
systemctl start postgresql.service

# Start FastAPI backend
cd backend-fastapi
source bin/activate
PYTHONPATH=$PWD uvicorn src.main:app --host localhost --port 8000 --reload
```

### Go Backend
```bash
# Start PostgreSQL
systemctl start postgresql.service

# Start Go backend
cd backend-go
go mod download
go run src/main.go
```

### Node.js Backend
```bash
# Start PostgreSQL
systemctl start postgresql.service

# Start Node.js backend
cd backend-node
npm install
npm run dev
```

## Frontend
```bash
cd frontend
npm start
```

## Environment Variables
Create a `.env` file in each backend directory with:
```
DB_NAME=testdb
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Notes
- All backends connect to the same PostgreSQL database
- Each backend implements identical API endpoints
- The frontend can work with any of the backends interchangeably
- Default port for all backends is 8000

## TODO
- Verify account functionality
- Flag user system
- Payment system integration
- Recurring payments
- Fix registration error (404)
- Fix connection to expo go