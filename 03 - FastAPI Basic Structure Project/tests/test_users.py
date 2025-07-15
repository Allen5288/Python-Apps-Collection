import pytest
from fastapi.testclient import TestClient


class TestUserEndpoints:
    """Test user endpoints"""
    
    def test_register_user(self, client: TestClient, test_user_data):
        """Test user registration"""
        response = client.post("/api/v1/users/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(self, client: TestClient, test_user_data):
        """Test registration with duplicate email"""
        # First registration
        response = client.post("/api/v1/users/register", json=test_user_data)
        assert response.status_code == 201
        
        # Second registration with same email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "different_username"
        response = client.post("/api/v1/users/register", json=duplicate_data)
        assert response.status_code == 409
    
    def test_register_duplicate_username(self, client: TestClient, test_user_data):
        """Test registration with duplicate username"""
        # First registration
        response = client.post("/api/v1/users/register", json=test_user_data)
        assert response.status_code == 201
        
        # Second registration with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/api/v1/users/register", json=duplicate_data)
        assert response.status_code == 409
    
    def test_login_user(self, client: TestClient, test_user_data):
        """Test user login"""
        # Register user first
        client.post("/api/v1/users/register", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/users/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, test_user_data):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/api/v1/users/register", json=test_user_data)
        
        # Login with wrong password
        login_data = {
            "username": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/users/login", data=login_data)
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, test_user_headers):
        """Test getting current user info"""
        response = client.get("/api/v1/users/me", headers=test_user_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data
        assert "hashed_password" not in data
    
    def test_update_current_user(self, client: TestClient, test_user_headers):
        """Test updating current user"""
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
        response = client.put("/api/v1/users/me", json=update_data, headers=test_user_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "Updated bio"
    
    def test_get_users_list(self, client: TestClient, test_user_headers):
        """Test getting users list"""
        response = client.get("/api/v1/users/", headers=test_user_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data
        assert isinstance(data["users"], list)
    
    def test_get_users_pagination(self, client: TestClient, test_user_headers):
        """Test users list pagination"""
        response = client.get("/api/v1/users/?skip=0&limit=5", headers=test_user_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["per_page"] == 5
        assert len(data["users"]) <= 5
    
    def test_unauthorized_access(self, client: TestClient):
        """Test accessing protected endpoints without authentication"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
        
        response = client.get("/api/v1/users/")
        assert response.status_code == 401


class TestUserValidation:
    """Test user input validation"""
    
    def test_invalid_email_format(self, client: TestClient):
        """Test registration with invalid email format"""
        invalid_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/users/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_short_password(self, client: TestClient):
        """Test registration with short password"""
        invalid_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "short"
        }
        response = client.post("/api/v1/users/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_invalid_username(self, client: TestClient):
        """Test registration with invalid username"""
        invalid_data = {
            "email": "test@example.com",
            "username": "ab",  # Too short
            "password": "testpassword123"
        }
        response = client.post("/api/v1/users/register", json=invalid_data)
        assert response.status_code == 422


class TestHealthCheck:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
