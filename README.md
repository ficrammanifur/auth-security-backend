# Backend - Hybrid Authentication Security Lab

Flask-based JWT authentication API for educational security lab. Demonstrates common security vulnerabilities in intentionally insecure code for learning purposes.

## Overview

This backend provides a simple JWT-based authentication system with 4 endpoints. It's designed to be educational, including intentional security vulnerabilities that are documented and explained.

**Demo Credentials**: `admin` / `password123` or `user` / `password123`

## Files

- `app.py` - Main Flask application with all routes and logic
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration for Railway
- `railway.json` - Railway.app deployment configuration
- `.env.example` - Environment variables template

## Features

🔐 **JWT Authentication**
- Generate tokens on login
- Validate tokens on protected endpoints
- Token expiration handling (24 hours default)
- Bearer token scheme (Authorization: Bearer <token>)

📡 **RESTful API**
- 4 endpoints with proper HTTP methods
- JSON request/response format
- CORS-enabled for cross-origin requests
- Detailed error messages

📊 **Logging**
- Request/response logging with timestamps
- User activity tracking
- Error logging to stderr
- Debug information in console

🚀 **Production Ready**
- Gunicorn WSGI server
- Docker containerization
- Health check endpoint
- Environment variable configuration

## Setup

### Local Development

1. **Clone and Navigate**
```bash
cd auth-security-backend
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env if needed (optional for local dev)
```

5. **Run Server**
```bash
python app.py
```

Server starts on `http://localhost:5000`

### Docker Deployment

1. **Build Image**
```bash
docker build -t auth-lab-backend .
```

2. **Run Container**
```bash
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  auth-lab-backend
```

### Railway Deployment

1. **Connect GitHub Repository**
   - Link your GitHub account to Railway
   - Select this repository

2. **Configure Environment**
   - Set `SECRET_KEY` in Railway dashboard
   - Set `FLASK_ENV=production`
   - Optional: `JWT_EXPIRATION_HOURS`

3. **Deploy**
   - Railway automatically deploys on git push
   - Uses Dockerfile and railway.json

4. **Get URL**
   - Copy your Railway deployment URL (e.g., `https://xxxx.up.railway.app`)
   - Update frontend `API_BASE_URL` with this URL

## API Endpoints

### 1. Health Check
```
GET /health
```

Check if backend is running.

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Authentication Lab Backend is running",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### 2. Login
```
POST /login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

Authenticate user and receive JWT token.

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "admin",
  "expiresIn": 86400
}
```

**Error** (401 Unauthorized):
```json
{
  "success": false,
  "message": "Invalid username or password"
}
```

### 3. Protected Endpoint
```
GET /protected
Authorization: Bearer <token>
```

Access protected resource with valid JWT.

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Access granted to protected endpoint",
  "username": "admin",
  "timestamp": "2024-01-15T10:30:50.654321"
}
```

**Error** (401 Unauthorized):
```json
{
  "success": false,
  "message": "Token expired or invalid"
}
```

### 4. Verify Token
```
POST /verify
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Verify if a token is valid (optional endpoint).

**Response** (200 OK):
```json
{
  "success": true,
  "valid": true,
  "username": "admin",
  "iat": 1705318245,
  "exp": 1705404645
}
```

## Security Analysis

⚠️ **Intentional Vulnerabilities** (Educational Purpose)

### 1. Hardcoded Secret Key
```python
SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-change-in-production')
```
**Issue**: Default key is exposed in code  
**Impact**: Anyone with code access can forge tokens  
**Fix**: Use strong, random secrets from environment only

### 2. Plaintext Password Storage
```python
USERS = {
    "admin": {"password": "password123"}  # NOT HASHED!
}
```
**Issue**: Passwords stored in plaintext  
**Impact**: Database breach = immediate compromise  
**Fix**: Use bcrypt/Argon2 to hash passwords

### 3. Hardcoded User Database
```python
USERS = {...}  # In-memory dictionary
```
**Issue**: Users are hardcoded in source code  
**Impact**: Can't add/remove users without code changes  
**Fix**: Use real database (PostgreSQL, MongoDB, etc.)

### 4. No Input Validation
```python
username = data.get('username', '').strip()  # Only basic cleaning
```
**Issue**: Missing length checks, special character validation  
**Impact**: Potential injection attacks  
**Fix**: Use schema validation (Pydantic, JSONSchema)

### 5. CORS Allows All Origins
```python
CORS(app, origins=["*"])
```
**Issue**: Any website can make requests to this API  
**Impact**: CSRF attacks possible  
**Fix**: Whitelist specific origins in production

### 6. No Rate Limiting
**Issue**: No protection against brute force attacks  
**Impact**: Easy password guessing  
**Fix**: Implement rate limiting per IP/user

### 7. No HTTPS Enforcement
**Issue**: Tokens sent over plaintext HTTP  
**Impact**: Man-in-the-middle attacks  
**Fix**: Enforce HTTPS in production

### 8. Tokens Never Expire (in localStorage)
**Issue**: Frontend stores tokens indefinitely  
**Impact**: Compromised token never expires client-side  
**Fix**: Implement token refresh mechanism

### 9. No Logging/Auditing
**Issue**: Limited request logging  
**Impact**: Can't detect attacks  
**Fix**: Add comprehensive audit logging

### 10. Missing Security Headers
**Issue**: No X-Frame-Options, X-Content-Type-Options, etc.  
**Impact**: Vulnerable to framing, MIME sniffing attacks  
**Fix**: Add security headers middleware

## Production Roadmap

### Phase 1: Basic Security (Week 1)
- [ ] Use environment-only secrets
- [ ] Add HTTPS enforcement
- [ ] Implement password hashing (bcrypt)
- [ ] Add request validation (Pydantic)

### Phase 2: Data Security (Week 2)
- [ ] Integrate real database (PostgreSQL)
- [ ] Add email verification
- [ ] Implement refresh tokens
- [ ] Add password reset flow

### Phase 3: Advanced Security (Week 3)
- [ ] Rate limiting per IP/user
- [ ] Add security headers
- [ ] Implement audit logging
- [ ] Add 2FA support

### Phase 4: Hardening (Week 4)
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF tokens
- [ ] API key authentication

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `PORT` | `5000` | Server port |
| `SECRET_KEY` | `super-secret...` | JWT signing key |
| `JWT_EXPIRATION_HOURS` | `24` | Token expiration time |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

## Testing

### Test Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

### Test Protected Endpoint
```bash
# Use token from login response
curl -X GET http://localhost:5000/protected \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Health
```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Import Error: flask_cors not found
```bash
pip install -r requirements.txt
```

### Port 5000 Already in Use
```bash
# Change PORT env var
PORT=5001 python app.py

# Or kill the process using port 5000
# On Unix: lsof -i :5000 | kill -9 <PID>
```

### CORS Errors from Frontend
Check that `CORS_ORIGINS` includes your frontend URL, or set `origins=["*"]` for testing.

### Token Invalid After Deployment
Ensure `SECRET_KEY` environment variable is set the same across all deployments. Different keys invalidate tokens.

## Performance

- Flask development server: ~50 req/s
- Gunicorn production: ~1000 req/s
- Typical response time: <50ms
- JWT validation: <5ms per request

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework |
| Flask-CORS | 4.0.0 | CORS support |
| PyJWT | 2.8.1 | JWT encoding/decoding |
| Gunicorn | 21.2.0 | WSGI server |
| python-dotenv | 1.0.0 | Environment loading |

## Related

- Frontend: `/auth-security-frontend/README.md`
- Main Project: `/README.md`
- Security Analysis: `/SECURITY.md`
- Deployment Guide: `/DEPLOYMENT.md`

## License

Educational purpose only. Use for learning authentication concepts.
