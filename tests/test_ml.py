import pytest
from app import create_app
from config import TestingConfig
from database.db import db
from services.what_if import simulate_business_scenario

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_what_if_simulation_logic(app):
    with app.app_context():
        res = simulate_business_scenario(
            price_change_pct=10.0,
            discount_change_pct=-5.0,
            quantity_change_pct=5.0,
            marketing_spend=20000.0
        )
        assert 'baseline' in res
        assert 'simulated' in res
        assert 'variance' in res
        assert res['simulated']['revenue'] > 0
