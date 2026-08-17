from datetime import datetime
from database.db import db

class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False, index=True)
    rep_id = db.Column(db.Integer, db.ForeignKey('sales_reps.rep_id', ondelete='SET NULL'), nullable=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.region_id', ondelete='RESTRICT'), nullable=False, index=True)
    order_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(30), default='Completed', nullable=False, index=True) # Completed, Shipped, Cancelled, Returned
    payment_method = db.Column(db.String(50), default='Credit Card')
    shipping_cost = db.Column(db.Numeric(10, 2), default=0.00)
    subtotal_amount = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    discount_amount = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    total_cost = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    net_profit = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    profit_margin_pct = db.Column(db.Numeric(5, 2), default=0.00)
    is_returned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.customer_name if self.customer else None,
            'rep_id': self.rep_id,
            'rep_name': self.sales_rep.rep_name if self.sales_rep else None,
            'region_id': self.region_id,
            'region_name': self.region.region_name if self.region else None,
            'order_date': self.order_date.strftime('%Y-%m-%d') if self.order_date else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'subtotal_amount': float(self.subtotal_amount) if self.subtotal_amount is not None else 0.0,
            'discount_amount': float(self.discount_amount) if self.discount_amount is not None else 0.0,
            'total_amount': float(self.total_amount) if self.total_amount is not None else 0.0,
            'total_cost': float(self.total_cost) if self.total_cost is not None else 0.0,
            'net_profit': float(self.net_profit) if self.net_profit is not None else 0.0,
            'profit_margin_pct': float(self.profit_margin_pct) if self.profit_margin_pct is not None else 0.0,
            'is_returned': self.is_returned
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    discount_pct = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    item_total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    item_total_cost = db.Column(db.Numeric(12, 2), nullable=False)
    item_profit = db.Column(db.Numeric(12, 2), nullable=False)
    item_margin_pct = db.Column(db.Numeric(5, 2), nullable=False)
    is_returned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'category_name': self.product.category.category_name if (self.product and self.product.category) else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price is not None else 0.0,
            'unit_cost': float(self.unit_cost) if self.unit_cost is not None else 0.0,
            'discount_pct': float(self.discount_pct) if self.discount_pct is not None else 0.0,
            'item_total_amount': float(self.item_total_amount) if self.item_total_amount is not None else 0.0,
            'item_total_cost': float(self.item_total_cost) if self.item_total_cost is not None else 0.0,
            'item_profit': float(self.item_profit) if self.item_profit is not None else 0.0,
            'item_margin_pct': float(self.item_margin_pct) if self.item_margin_pct is not None else 0.0,
            'is_returned': self.is_returned
        }
