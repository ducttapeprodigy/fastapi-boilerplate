from auth import pwd_context

# Mock database (replace with real database in production)
fake_users_db = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("testpassword"),
        "is_active": True
    }
}

fake_items_db = []