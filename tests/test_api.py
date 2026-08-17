import pytest
from app import create_app
from config import TestingConfig
from database.db import db
from models.user import User

@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        admin = User(username='admin', email='admin@test.com', full_name='Admin Test', role='admin', is_active=True)
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()

        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user_id'] = admin.user_id
            sess['username'] = admin.username
            sess['role'] = admin.role

        yield client
        db.drop_all()

def test_api_dashboard(client):
    res = client.get('/api/dashboard')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'kpis' in data

def test_api_what_if_simulation(client):
    res = client.get('/api/what-if?price_change_pct=5&discount_change_pct=-2&quantity_change_pct=10&marketing_spend=10000')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'scenario' in data
    assert 'variance' in data['scenario']
