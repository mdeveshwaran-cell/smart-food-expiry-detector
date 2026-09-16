from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """
    User model storing registered credentials and profile information.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    food_items = db.relationship('FoodItem', backref='owner', cascade='all, delete-orphan', lazy=True)
    waste_logs = db.relationship('WasteLog', backref='user', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        """Hashes the user's password securely using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies candidate password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class FoodItem(db.Model):
    """
    FoodItem model representing stored food inventory items.
    """
    __tablename__ = 'food_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), nullable=False, default='pcs')
    storage_location = db.Column(db.String(50), nullable=False, default='Refrigerator')
    image_path = db.Column(db.String(255), nullable=True)
    
    # State tracking
    is_consumed = db.Column(db.Boolean, default=False)
    is_wasted = db.Column(db.Boolean, default=False)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def days_remaining(self):
        """
        Calculates days remaining until expiry.
        Positive: days left.
        Zero: expires today.
        Negative: expired N days ago.
        """
        if not self.expiry_date:
            return 0
        today = date.today()
        delta = (self.expiry_date - today).days
        return delta

    @property
    def status(self):
        """
        Classifies status:
        🟢 Fresh — more than 3 days remaining (> 3 days)
        🟡 Expiring Soon — 0 to 3 days remaining (0 to 3 days)
        🔴 Expired — expiry date has passed (< 0 days)
        """
        if self.is_consumed:
            return 'Consumed'
        if self.is_wasted:
            return 'Discarded'
            
        remaining = self.days_remaining
        if remaining > 3:
            return 'Fresh'
        elif remaining >= 0:
            return 'Expiring Soon'
        else:
            return 'Expired'

    @property
    def status_badge_class(self):
        """Bootstrap 5 CSS badge class for status styling."""
        s = self.status
        if s == 'Fresh':
            return 'bg-success'
        elif s == 'Expiring Soon':
            return 'bg-warning text-dark'
        elif s == 'Expired':
            return 'bg-danger'
        elif s == 'Consumed':
            return 'bg-primary'
        else:
            return 'bg-secondary'

    @property
    def status_indicator(self):
        """Visual emoji indicator for the status."""
        s = self.status
        if s == 'Fresh':
            return '🟢 Fresh'
        elif s == 'Expiring Soon':
            return '🟡 Expiring Soon'
        elif s == 'Expired':
            return '🔴 Expired'
        elif s == 'Consumed':
            return '✅ Consumed'
        else:
            return '🗑️ Discarded'

    def to_dict(self):
        """Serialize food item data for JSON responses or API consumption."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'purchase_date': self.purchase_date.strftime('%Y-%m-%d') if self.purchase_date else None,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
            'days_remaining': self.days_remaining,
            'status': self.status,
            'quantity': self.quantity,
            'unit': self.unit,
            'storage_location': self.storage_location,
            'image_path': self.image_path,
            'is_consumed': self.is_consumed,
            'is_wasted': self.is_wasted
        }

    def __repr__(self):
        return f'<FoodItem {self.name} (Exp: {self.expiry_date})>'


class WasteLog(db.Model):
    """
    Tracks food consumption and waste actions to generate
    food waste reduction statistics and sustainability metrics.
    """
    __tablename__ = 'waste_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    food_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Float, default=1.0)
    unit = db.Column(db.String(20), default='pcs')
    action = db.Column(db.String(20), nullable=False)  # 'CONSUMED' or 'WASTED'
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WasteLog {self.food_name}: {self.action}>'
