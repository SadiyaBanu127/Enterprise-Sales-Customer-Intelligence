import pytest
from app import create_app
from config import TestingConfig
from database.db import db
from models.user import User

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Seed test admin & analyst
        admin = User(username='test_admin', email='admin@test.com', full_name='Admin Test', role='admin', is_active=True)
        admin.set_password('Admin@123')
        analyst = User(username='test_analyst', email='analyst@test.com', full_name='Analyst Test', role='analyst', is_active=True)
        analyst.set_password('Analyst@123')
        db.session.add_all([admin, analyst])
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_success(client):
    res = client.post('/api/auth/login', json={'username': 'test_admin', 'password': 'Admin@123'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['role'] == 'admin'

def test_login_form_authenticates_and_redirects_to_dashboard(client):
    res = client.post('/login', data={'username': 'test_admin', 'password': 'Admin@123'})
    assert res.status_code == 302
    assert res.headers['Location'].endswith('/dashboard')

    dashboard = client.get('/dashboard')
    assert dashboard.status_code == 200

def test_login_page_serves_logo_asset(client):
    res = client.get('/static/images/logo.svg')
    assert res.status_code == 200
    assert res.mimetype == 'image/svg+xml'

def test_login_invalid_password(client):
    res = client.post('/api/auth/login', json={'username': 'test_admin', 'password': 'WrongPassword'})
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False

def test_user_registration(client):
    res = client.post('/register', data={
        'full_name': 'New User',
        'username': 'newuser',
        'email': 'newuser@enterprise.com',
        'role': 'analyst',
        'password': 'SecurePassword@123'
    }, follow_redirects=True)
    assert res.status_code == 200
