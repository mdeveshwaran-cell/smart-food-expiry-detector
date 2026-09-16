from datetime import date, timedelta, datetime
from models import db, User, FoodItem, WasteLog

def init_db(app):
    """Initializes the database and creates tables if they don't already exist."""
    with app.app_context():
        db.create_all()
        print("[Database] Tables verified and created successfully.")

def seed_demo_data(app):
    """
    Seeds initial realistic sample food items and demo user for evaluation/presentation.
    """
    with app.app_context():
        # Check if demo user already exists
        demo_user = User.query.filter_by(email='demo@smartfood.com').first()
        if demo_user:
            return  # Already seeded

        # Create demo account
        demo_user = User(
            name="Alex Student",
            email="demo@smartfood.com"
        )
        demo_user.set_password("demo123")
        db.session.add(demo_user)
        db.session.commit()

        today = date.today()

        sample_foods = [
            # Expiring Soon items (1 to 3 days remaining)
            FoodItem(
                user_id=demo_user.id,
                name="Organic Whole Milk",
                category="Dairy",
                purchase_date=today - timedelta(days=5),
                expiry_date=today + timedelta(days=2),
                quantity=1.0,
                unit="L",
                storage_location="Refrigerator",
                notes="Keep chilled at 4°C"
            ),
            FoodItem(
                user_id=demo_user.id,
                name="Whole Wheat Bread",
                category="Bakery",
                purchase_date=today - timedelta(days=4),
                expiry_date=today + timedelta(days=1),
                quantity=1.0,
                unit="packet",
                storage_location="Pantry",
                notes="Consider making French toast or freezing"
            ),
            FoodItem(
                user_id=demo_user.id,
                name="Baby Spinach Leaves",
                category="Vegetables",
                purchase_date=today - timedelta(days=3),
                expiry_date=today + timedelta(days=3),
                quantity=250.0,
                unit="g",
                storage_location="Refrigerator",
                notes="Check crisper drawer"
            ),
            # Fresh items (> 3 days remaining)
            FoodItem(
                user_id=demo_user.id,
                name="Greek Yogurt",
                category="Dairy",
                purchase_date=today - timedelta(days=2),
                expiry_date=today + timedelta(days=14),
                quantity=2.0,
                unit="cups",
                storage_location="Refrigerator",
                notes="Sealed container"
            ),
            FoodItem(
                user_id=demo_user.id,
                name="Ripe Yellow Bananas",
                category="Fruits",
                purchase_date=today - timedelta(days=1),
                expiry_date=today + timedelta(days=5),
                quantity=6.0,
                unit="pcs",
                storage_location="Countertop",
                notes="Keep away from apples"
            ),
            FoodItem(
                user_id=demo_user.id,
                name="Basmati Rice",
                category="Grains & Cereals",
                purchase_date=today - timedelta(days=20),
                expiry_date=today + timedelta(days=180),
                quantity=5.0,
                unit="kg",
                storage_location="Pantry",
                notes="Airtight container"
            ),
            # Expired item (< 0 days remaining)
            FoodItem(
                user_id=demo_user.id,
                name="Cheddar Cheese Block",
                category="Dairy",
                purchase_date=today - timedelta(days=25),
                expiry_date=today - timedelta(days=2),
                quantity=1.0,
                unit="block",
                storage_location="Refrigerator",
                notes="Expired 2 days ago"
            ),
        ]

        for food in sample_foods:
            db.session.add(food)

        # Seed sample waste logs for analytics demonstration
        logs = [
            WasteLog(user_id=demo_user.id, food_name="Tomatoes", category="Vegetables", quantity=500.0, unit="g", action="CONSUMED"),
            WasteLog(user_id=demo_user.id, food_name="Eggs", category="Dairy", quantity=6.0, unit="pcs", action="CONSUMED"),
            WasteLog(user_id=demo_user.id, food_name="Stale Croissant", category="Bakery", quantity=1.0, unit="pcs", action="WASTED"),
            WasteLog(user_id=demo_user.id, food_name="Strawberries", category="Fruits", quantity=1.0, unit="box", action="CONSUMED")
        ]
        for log in logs:
            db.session.add(log)

        db.session.commit()
        print("[Database] Seeded realistic demo food items and waste logs.")
