"""Security tests for SkillTrack API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User
from app.security import hash_password

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(client):
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(
        name="Test User",
        email="test@example.com",
        reg_no="TEST123",
        password_hash=hash_password("TestPassword123!"),
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


class TestPasswordValidation:
    """Test password strength validation."""

    def test_register_with_weak_password_too_short(self, client):
        """Test registration with password too short."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "reg_no": "REG123",
                "password": "Short1!",  # Only 7 chars
                "department": "CS",
            },
        )
        assert response.status_code == 422
        assert "at least 8 characters" in response.json()["detail"][0]["msg"].lower()

    def test_register_with_weak_password_no_uppercase(self, client):
        """Test registration with no uppercase letter."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "reg_no": "REG123",
                "password": "password123!",  # No uppercase
                "department": "CS",
            },
        )
        assert response.status_code == 422
        assert "uppercase" in response.json()["detail"][0]["msg"].lower()

    def test_register_with_weak_password_no_special_char(self, client):
        """Test registration with no special character."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "reg_no": "REG123",
                "password": "Password123",  # No special char
                "department": "CS",
            },
        )
        assert response.status_code == 422
        assert "special character" in response.json()["detail"][0]["msg"].lower()

    def test_register_with_common_password(self, client):
        """Test registration with common password pattern."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "reg_no": "REG123",
                "password": "Password123!",  # Contains "password"
                "department": "CS",
            },
        )
        assert response.status_code == 422
        assert "common pattern" in response.json()["detail"][0]["msg"].lower()

    def test_register_with_strong_password(self, client):
        """Test registration with strong password."""
        response = client.post(
            "/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "reg_no": "REG123",
                "password": "MySecur3P@ssw0rd",  # Strong password
                "department": "CS",
            },
        )
        assert response.status_code == 201
        assert "access_token" in response.json()


class TestAuthenticationSecurity:
    """Test authentication security features."""

    def test_login_with_invalid_credentials(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "WrongPassword123!"},
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_rate_limiting(self, client, test_user):
        """Test rate limiting on failed login attempts."""
        # Make 11 failed login attempts (limit is 10)
        for i in range(11):
            response = client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": f"Wrong{i}!"},
            )

        # 11th attempt should be rate limited
        assert response.status_code == 429
        assert "Too many failed sign-in attempts" in response.json()["detail"]

    def test_jwt_token_validation(self, client, test_user):
        """Test JWT token validation."""
        # Login to get token
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123!"},
        )
        token = response.json()["access_token"]

        # Test with valid token
        response = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # Test with invalid token
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

        # Test without token
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestSecurityHeaders:
    """Test security headers are present."""

    def test_security_headers_present(self, client):
        """Test that security headers are added to responses."""
        response = client.get("/health")

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "X-XSS-Protection" in response.headers
        assert "Content-Security-Policy" in response.headers

    def test_server_header_removed(self, client):
        """Test that server header is removed."""
        response = client.get("/health")
        assert "Server" not in response.headers or response.headers.get("Server") == ""


class TestInputSanitization:
    """Test input sanitization."""

    def test_sql_injection_attempt(self, client):
        """Test that SQL injection attempts are handled."""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com' OR '1'='1",
                "password": "anything",
            },
        )
        # Should not cause SQL injection, just invalid credentials
        assert response.status_code in [401, 422]

    def test_xss_attempt_in_registration(self, client):
        """Test XSS attempt in registration."""
        response = client.post(
            "/auth/register",
            json={
                "name": "<script>alert('XSS')</script>",
                "email": "test@example.com",
                "reg_no": "TEST123",
                "password": "SecureP@ss123",
                "department": "CS",
            },
        )
        # Should sanitize the input
        if response.status_code == 201:
            user_data = response.json()["user"]
            assert "<script>" not in user_data["name"]


class TestRequestSizeLimits:
    """Test request size limits."""

    def test_large_request_rejected(self, client):
        """Test that very large requests are rejected."""
        # Create a large payload (>10MB)
        large_data = "x" * (11 * 1024 * 1024)  # 11MB
        response = client.post(
            "/auth/register",
            json={
                "name": large_data,
                "email": "test@example.com",
                "reg_no": "TEST123",
                "password": "SecureP@ss123",
                "department": "CS",
            },
        )
        # Should be rejected (either 413 or 422 for validation)
        assert response.status_code in [413, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
