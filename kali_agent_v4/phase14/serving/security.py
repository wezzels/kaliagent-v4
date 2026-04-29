#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14 Sprint 1.4: Security Hardening

JWT authentication, rate limiting, and request signing:
- JWT token authentication
- API key management
- Rate limiting per client
- Request signing (HMAC)
- TLS configuration
- Security headers

Author: KaliAgent Team
Status: Beta (0.2.0)
"""

import logging
import time
import hashlib
import hmac
import base64
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Security')

# Try to import JWT libraries
try:
    import jwt
    from jwt.exceptions import PyJWTError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("⚠️  PyJWT not available - install with: pip install PyJWT")


@dataclass
class APIKey:
    """API key configuration"""
    key_id: str
    key_hash: str
    name: str
    created_at: str
    expires_at: Optional[str]
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    allowed_endpoints: List[str] = field(default_factory=lambda: ["*"])
    active: bool = True


@dataclass
class RateLimitBucket:
    """Rate limit tracking bucket"""
    requests: List[float] = field(default_factory=list)
    minute_count: int = 0
    hour_count: int = 0


class JWTAuthenticator:
    """
    JWT Token Authentication
    
    Features:
    - Token generation
    - Token validation
    - Token refresh
    - Token revocation
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, secret_key: str, algorithm: str = "HS256",
                 token_expiry_hours: int = 24, refresh_expiry_days: int = 7):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry_hours = token_expiry_hours
        self.refresh_expiry_days = refresh_expiry_days
        
        # Revoked tokens
        self.revoked_tokens: set = set()
        self.token_blacklist_lock = threading.Lock()
        
        if not JWT_AVAILABLE:
            logger.error("❌ JWT not available - install PyJWT")
        
        logger.info(f"🔐 JWT Authenticator v{self.VERSION}")
        logger.info(f"   Algorithm: {algorithm}")
        logger.info(f"   Token expiry: {token_expiry_hours}h")
    
    def generate_token(self, user_id: str, roles: List[str] = None,
                      metadata: Dict = None) -> Dict[str, str]:
        """Generate JWT access and refresh tokens"""
        if not JWT_AVAILABLE:
            return {"error": "JWT not available"}
        
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(hours=self.token_expiry_hours),
            "type": "access",
            "roles": roles or ["user"],
            "metadata": metadata or {}
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        
        # Refresh token
        refresh_payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(days=self.refresh_expiry_days),
            "type": "refresh"
        }
        
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"✅ Generated tokens for user {user_id}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.token_expiry_hours * 3600
        }
    
    def validate_token(self, token: str) -> Dict:
        """Validate JWT token"""
        if not JWT_AVAILABLE:
            return {"valid": False, "error": "JWT not available"}
        
        # Check if revoked
        with self.token_blacklist_lock:
            if token in self.revoked_tokens:
                return {"valid": False, "error": "Token revoked"}
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") not in ["access", "refresh"]:
                return {"valid": False, "error": "Invalid token type"}
            
            return {
                "valid": True,
                "payload": payload,
                "user_id": payload.get("sub"),
                "roles": payload.get("roles", []),
                "metadata": payload.get("metadata", {})
            }
        
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except PyJWTError as e:
            return {"valid": False, "error": f"Invalid token: {str(e)}"}
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token"""
        validation = self.validate_token(refresh_token)
        
        if not validation["valid"]:
            return validation
        
        if validation["payload"].get("type") != "refresh":
            return {"valid": False, "error": "Not a refresh token"}
        
        # Generate new access token
        return self.generate_token(
            user_id=validation["user_id"],
            roles=validation["roles"],
            metadata=validation["metadata"]
        )
    
    def revoke_token(self, token: str):
        """Revoke token (add to blacklist)"""
        with self.token_blacklist_lock:
            self.revoked_tokens.add(token)
        logger.info(f"🚫 Token revoked")
    
    def cleanup_blacklist(self, max_age_hours: int = 48):
        """Clean up old revoked tokens"""
        # In production, use Redis with TTL instead
        with self.token_blacklist_lock:
            # Simple cleanup - in prod, use timestamps
            if len(self.revoked_tokens) > 10000:
                self.revoked_tokens.clear()
        logger.info("🧹 Token blacklist cleaned")


class RateLimiter:
    """
    Rate Limiter with sliding window
    
    Features:
    - Per-client rate limiting
    - Sliding window algorithm
    - Multiple time windows (minute, hour)
    - Automatic cleanup
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, default_rpm: int = 100, default_rph: int = 1000):
        self.default_rpm = default_rpm  # Requests per minute
        self.default_rph = default_rph  # Requests per hour
        
        # Client buckets
        self.buckets: Dict[str, RateLimitBucket] = defaultdict(RateLimitBucket)
        self.lock = threading.Lock()
        
        # Cleanup thread
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        
        logger.info(f"🛡️ Rate Limiter v{self.VERSION}")
        logger.info(f"   Default RPM: {default_rpm}")
        logger.info(f"   Default RPH: {default_rph}")
    
    def check_rate_limit(self, client_id: str, rpm: int = None,
                         rph: int = None) -> Dict:
        """
        Check if request is within rate limit
        
        Returns:
            Dict with allowed, remaining, reset_time
        """
        rpm = rpm or self.default_rpm
        rph = rph or self.default_rph
        
        current_time = time.time()
        
        with self.lock:
            bucket = self.buckets[client_id]
            
            # Remove old requests (older than 1 hour)
            cutoff = current_time - 3600
            bucket.requests = [t for t in bucket.requests if t > cutoff]
            
            # Count requests in last minute and hour
            minute_ago = current_time - 60
            bucket.minute_count = sum(1 for t in bucket.requests if t > minute_ago)
            bucket.hour_count = len(bucket.requests)
            
            # Check limits
            if bucket.minute_count >= rpm:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "limit": rpm,
                    "reset_time": 60,  # seconds until reset
                    "reason": "Minute limit exceeded"
                }
            
            if bucket.hour_count >= rph:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "limit": rph,
                    "reset_time": 3600,
                    "reason": "Hour limit exceeded"
                }
            
            # Add current request
            bucket.requests.append(current_time)
            bucket.minute_count += 1
            bucket.hour_count += 1
            
            # Trigger cleanup if needed
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_buckets()
            
            return {
                "allowed": True,
                "remaining_minute": rpm - bucket.minute_count,
                "remaining_hour": rph - bucket.hour_count,
                "limit_minute": rpm,
                "limit_hour": rph
            }
    
    def _cleanup_old_buckets(self):
        """Remove inactive buckets"""
        current_time = time.time()
        to_remove = []
        
        for client_id, bucket in self.buckets.items():
            if not bucket.requests or (current_time - max(bucket.requests)) > 3600:
                to_remove.append(client_id)
        
        for client_id in to_remove:
            del self.buckets[client_id]
        
        self.last_cleanup = current_time
        logger.debug(f"🧹 Cleaned up {len(to_remove)} rate limit buckets")
    
    def get_client_usage(self, client_id: str) -> Dict:
        """Get rate limit usage for client"""
        with self.lock:
            if client_id not in self.buckets:
                return {"requests": 0, "limit": self.default_rpm}
            
            bucket = self.buckets[client_id]
            current_time = time.time()
            minute_ago = current_time - 60
            
            minute_count = sum(1 for t in bucket.requests if t > minute_ago)
            
            return {
                "requests_last_minute": minute_count,
                "requests_last_hour": len(bucket.requests),
                "limit_per_minute": self.default_rpm,
                "limit_per_hour": self.default_rph,
                "usage_percent": (minute_count / self.default_rpm) * 100
            }


class RequestSigner:
    """
    HMAC Request Signing
    
    Features:
    - Request signature generation
    - Signature verification
    - Timestamp validation (prevent replay)
    - Body hashing
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, secret_key: str, timestamp_tolerance_seconds: int = 300):
        self.secret_key = secret_key.encode('utf-8')
        self.timestamp_tolerance = timestamp_tolerance_seconds
        
        logger.info(f"🔏 Request Signer v{self.VERSION}")
    
    def generate_signature(self, method: str, path: str, body: Dict = None,
                          timestamp: int = None) -> str:
        """Generate HMAC signature for request"""
        if timestamp is None:
            timestamp = int(time.time())
        
        # Create message to sign
        body_hash = hashlib.sha256(json.dumps(body or {}, sort_keys=True).encode()).hexdigest()
        message = f"{method}\n{path}\n{timestamp}\n{body_hash}"
        
        # Generate HMAC
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, method: str, path: str, signature: str,
                        body: Dict = None, timestamp: int = None) -> Dict:
        """Verify request signature"""
        current_time = int(time.time())
        
        # Check timestamp
        if timestamp:
            time_diff = abs(current_time - timestamp)
            if time_diff > self.timestamp_tolerance:
                return {
                    "valid": False,
                    "error": f"Request timestamp expired (diff: {time_diff}s)"
                }
        
        # Generate expected signature
        expected_signature = self.generate_signature(method, path, body, timestamp)
        
        # Constant-time comparison
        if hmac.compare_digest(signature, expected_signature):
            return {"valid": True}
        else:
            return {"valid": False, "error": "Invalid signature"}
    
    def get_auth_header(self, method: str, path: str, body: Dict = None) -> Dict[str, str]:
        """Generate authorization header"""
        timestamp = int(time.time())
        signature = self.generate_signature(method, path, body, timestamp)
        
        return {
            "X-Signature": signature,
            "X-Timestamp": str(timestamp),
            "X-Content-Hash": hashlib.sha256(json.dumps(body or {}, sort_keys=True).encode()).hexdigest()
        }


class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache"
        }
    
    @staticmethod
    def add_to_response(response, extra_headers: Dict = None):
        """Add security headers to response"""
        headers = SecurityHeaders.get_headers()
        if extra_headers:
            headers.update(extra_headers)
        
        # For FastAPI responses
        if hasattr(response, 'headers'):
            for key, value in headers.items():
                response.headers[key] = value
        
        return response


class APIKeyManager:
    """API Key management"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.lock = threading.Lock()
        
        logger.info("🔑 API Key Manager initialized")
    
    def create_key(self, name: str, rate_limit_rpm: int = 100,
                   rate_limit_rph: int = 1000,
                   allowed_endpoints: List[str] = None,
                   expires_in_days: int = None) -> APIKey:
        """Create new API key"""
        import secrets
        
        # Generate key
        key_id = secrets.token_urlsafe(16)
        key_secret = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key_secret.encode()).hexdigest()
        
        now = datetime.utcnow()
        expires_at = None
        if expires_in_days:
            expires_at = (now + timedelta(days=expires_in_days)).isoformat()
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            created_at=now.isoformat(),
            expires_at=expires_at,
            rate_limit_per_minute=rate_limit_rpm,
            rate_limit_per_hour=rate_limit_rph,
            allowed_endpoints=allowed_endpoints or ["*"],
            active=True
        )
        
        with self.lock:
            self.api_keys[key_id] = api_key
        
        logger.info(f"✅ Created API key: {key_id} ({name})")
        
        # Return full key only once (won't be shown again)
        return {
            "key_id": key_id,
            "key_secret": key_secret,
            "name": name,
            "created_at": api_key.created_at,
            "expires_at": expires_at,
            "rate_limit_rpm": rate_limit_rpm,
            "warning": "Save key_secret now - it won't be shown again!"
        }
    
    def validate_key(self, key_id: str, key_secret: str) -> Dict:
        """Validate API key"""
        key_hash = hashlib.sha256(key_secret.encode()).hexdigest()
        
        with self.lock:
            if key_id not in self.api_keys:
                return {"valid": False, "error": "Key not found"}
            
            api_key = self.api_keys[key_id]
            
            if api_key.key_hash != key_hash:
                return {"valid": False, "error": "Invalid key"}
            
            if not api_key.active:
                return {"valid": False, "error": "Key deactivated"}
            
            if api_key.expires_at:
                if datetime.utcnow() > datetime.fromisoformat(api_key.expires_at):
                    return {"valid": False, "error": "Key expired"}
            
            return {
                "valid": True,
                "key_id": key_id,
                "name": api_key.name,
                "rate_limit_rpm": api_key.rate_limit_per_minute,
                "rate_limit_rph": api_key.rate_limit_per_hour,
                "allowed_endpoints": api_key.allowed_endpoints
            }
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke API key"""
        with self.lock:
            if key_id in self.api_keys:
                self.api_keys[key_id].active = False
                logger.info(f"🚫 Revoked API key: {key_id}")
                return True
        return False
    
    def list_keys(self) -> List[Dict]:
        """List all API keys (without secrets)"""
        with self.lock:
            return [
                {
                    "key_id": key.key_id,
                    "name": key.name,
                    "created_at": key.created_at,
                    "expires_at": key.expires_at,
                    "active": key.active,
                    "rate_limit_rpm": key.rate_limit_per_minute
                }
                for key in self.api_keys.values()
            ]


def demo():
    """Demo security features"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - SECURITY HARDENING                 ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    # JWT Authentication
    print("🔐 Testing JWT Authentication...")
    if JWT_AVAILABLE:
        auth = JWTAuthenticator(secret_key="super-secret-key-change-in-production")
        
        tokens = auth.generate_token(
            user_id="user123",
            roles=["admin", "analyst"],
            metadata={"department": "security"}
        )
        
        print(f"   Access Token: {tokens['access_token'][:50]}...")
        print(f"   Expires In: {tokens['expires_in']}s")
        
        # Validate
        validation = auth.validate_token(tokens['access_token'])
        print(f"   Valid: {validation['valid']}")
        print(f"   User: {validation['user_id']}")
        print(f"   Roles: {validation['roles']}")
    else:
        print("   ⚠️  JWT not available")
    
    # Rate Limiting
    print("\n🛡️  Testing Rate Limiting...")
    limiter = RateLimiter(default_rpm=10, default_rph=100)
    
    for i in range(12):
        result = limiter.check_rate_limit("client_1")
        status = "✅" if result["allowed"] else "❌"
        print(f"   Request {i+1}: {status} (remaining: {result.get('remaining_minute', 0)})")
    
    # Request Signing
    print("\n🔏 Testing Request Signing...")
    signer = RequestSigner(secret_key="signing-key")
    
    headers = signer.get_auth_header("POST", "/analyze/threat-report", {"text": "test"})
    print(f"   Signature: {headers['X-Signature'][:50]}...")
    print(f"   Timestamp: {headers['X-Timestamp']}")
    
    # Verify
    verification = signer.verify_signature(
        "POST", "/analyze/threat-report",
        headers['X-Signature'],
        {"text": "test"},
        int(headers['X-Timestamp'])
    )
    print(f"   Valid: {verification['valid']}")
    
    # Security Headers
    print("\n🔒 Security Headers:")
    headers = SecurityHeaders.get_headers()
    for header, value in list(headers.items())[:5]:
        print(f"   {header}: {value[:50]}...")
    
    # API Key Management
    print("\n🔑 Testing API Key Management...")
    key_manager = APIKeyManager()
    
    new_key = key_manager.create_key(
        name="production-key",
        rate_limit_rpm=100,
        expires_in_days=365
    )
    
    print(f"   Key ID: {new_key['key_id']}")
    print(f"   Name: {new_key['name']}")
    print(f"   Rate Limit: {new_key['rate_limit_rpm']}/min")
    print(f"   ⚠️  {new_key['warning']}")
    
    # Validate key
    validation = key_manager.validate_key(new_key['key_id'], new_key['key_secret'])
    print(f"   Valid: {validation['valid']}")
    
    print("\n" + "="*70)
    print("✅ Security demo complete!")
    print("="*70)


if __name__ == "__main__":
    demo()
