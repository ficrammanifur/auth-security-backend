# """
# Hybrid Authentication Security Lab - Flask Backend
# JWT-based authentication API for educational security lab
# """

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import json
from datetime import datetime, timedelta
from functools import wraps
import os
import sys

# ===== CONFIGURATION =====
app = Flask(__name__)

# Secret key for JWT - HARDCODED FOR DEMO (Security Issue!)
SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-change-in-production')
JWT_EXPIRATION_HOURS = 24

# Enable CORS for GitHub Pages frontend
CORS(app, 
     origins=["*"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# ===== DUMMY USER DATABASE =====
# In production, this would be a real database
USERS = {
    "admin": {
        "username": "admin",
        "password": "password123",  # HARDCODED PASSWORD (Security Issue!)
        "email": "admin@example.com"
    },
    "user": {
        "username": "user",
        "password": "password123",  # HARDCODED PASSWORD (Security Issue!)
        "email": "user@example.com"
    }
}

# ===== UTILITY FUNCTIONS =====

def generate_token(username):
    """Generate JWT token with expiration"""
    try:
        payload = {
            'username': username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        print(f"[v0] Token generation error: {str(e)}", file=sys.stderr)
        return None


def verify_token(token):
    """Verify JWT token and extract payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def get_token_from_header():
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    try:
        # Expected format: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            return parts[1]
        return None
    except Exception as e:
        print(f"[v0] Token extraction error: {str(e)}", file=sys.stderr)
        return None


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Missing or invalid authorization header'
            }), 401
        
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'message': 'Token expired or invalid'
            }), 401
        
        # Pass username to the route handler
        request.username = payload.get('username')
        return f(*args, **kwargs)
    
    return decorated


# ===== LOGGING =====

def log_request(endpoint, method, username=None, status_code=None):
    """Simple request logging"""
    timestamp = datetime.utcnow().isoformat()
    log_msg = f"[{timestamp}] {method} {endpoint}"
    if username:
        log_msg += f" | User: {username}"
    if status_code:
        log_msg += f" | Status: {status_code}"
    print(f"[v0] {log_msg}", file=sys.stderr)


# ===== ROUTES =====

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Authentication Lab Backend is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """
    Login endpoint
    POST /login
    Body: { "username": "admin", "password": "password123" }
    Returns: { "token": "jwt_token", "username": "admin" }
    """
    
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Parse JSON body
        data = request.get_json()
        
        if not data:
            log_request('/login', 'POST', status_code=400)
            return jsonify({
                'success': False,
                'message': 'Request body must be JSON'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not password:
            log_request('/login', 'POST', username=username, status_code=400)
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # User lookup
        user = USERS.get(username)
        
        if not user or user['password'] != password:
            log_request('/login', 'POST', username=username, status_code=401)
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        # Generate token
        token = generate_token(username)
        
        if not token:
            log_request('/login', 'POST', username=username, status_code=500)
            return jsonify({
                'success': False,
                'message': 'Failed to generate token'
            }), 500
        
        log_request('/login', 'POST', username=username, status_code=200)
        return jsonify({
            'success': True,
            'message': f'Login successful',
            'token': token,
            'username': username,
            'expiresIn': JWT_EXPIRATION_HOURS * 3600
        }), 200
    
    except Exception as e:
        print(f"[v0] Login error: {str(e)}", file=sys.stderr)
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@app.route('/protected', methods=['GET', 'OPTIONS'])
@token_required
def protected():
    """
    Protected endpoint - requires valid JWT
    GET /protected
    Headers: Authorization: Bearer <token>
    Returns: { "message": "...", "username": "..." }
    """
    
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        username = request.username
        log_request('/protected', 'GET', username=username, status_code=200)
        
        return jsonify({
            'success': True,
            'message': f'Access granted to protected endpoint',
            'username': username,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        print(f"[v0] Protected endpoint error: {str(e)}", file=sys.stderr)
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@app.route('/verify', methods=['POST', 'OPTIONS'])
def verify():
    """
    Token verification endpoint (optional)
    POST /verify
    Body: { "token": "jwt_token" }
    Returns: { "valid": true/false, "username": "..." }
    """
    
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Token is required'
            }), 400
        
        token = data['token']
        payload = verify_token(token)
        
        if payload:
            log_request('/verify', 'POST', username=payload.get('username'), status_code=200)
            return jsonify({
                'success': True,
                'valid': True,
                'username': payload.get('username'),
                'iat': payload.get('iat'),
                'exp': payload.get('exp')
            }), 200
        else:
            log_request('/verify', 'POST', status_code=401)
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Token is invalid or expired'
            }), 401
    
    except Exception as e:
        print(f"[v0] Verify error: {str(e)}", file=sys.stderr)
        return jsonify({
            'success': False,
            'valid': False,
            'message': 'Internal server error'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


# ===== MAIN =====

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Hybrid Authentication Security Lab - Flask Backend      ║
    ║   Educational Purpose Only                                ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"[v0] Starting server with SECRET_KEY: {SECRET_KEY[:10]}...")
    print(f"[v0] Available endpoints:")
    print(f"[v0]   GET  /health       - Health check")
    print(f"[v0]   POST /login        - Authentication")
    print(f"[v0]   GET  /protected    - Protected resource (requires token)")
    print(f"[v0]   POST /verify       - Token verification")
    print()
    
    # Run on 0.0.0.0:5000 for Railway deployment
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
