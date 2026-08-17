from datetime import datetime
from database.db import db

class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    target_margin = db.Column(db.Numeric(5, 2), default=25.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'description': self.description,
            'target_margin': float(self.target_margin) if self.target_margin is not None else 0.0,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_sku = db.Column(db.String(30), unique=True, nullable=False, index=True)
    product_name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='CASCADE'), nullable=False, index=True)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    target_margin_pct = db.Column(db.Numeric(5, 2), nullable=True)
    stock_quantity = db.Column(db.Integer, default=100, nullable=False)
    is_discontinued = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    @property
    def margin_pct(self):
        if self.unit_price and float(self.unit_price) > 0:
            return round(((float(self.unit_price) - float(self.unit_cost)) / float(self.unit_price)) * 100, 2)
        return 0.0

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_sku': self.product_sku,
            'product_name': self.product_name,
            'category_id': self.category_id,
            'category_name': self.category.category_name if self.category else None,
            'unit_cost': float(self.unit_cost) if self.unit_cost is not None else 0.0,
            'unit_price': float(self.unit_price) if self.unit_price is not None else 0.0,
            'margin_pct': self.margin_pct,
            'stock_quantity': self.stock_quantity,
            'is_discontinued': self.is_discontinued
        }
