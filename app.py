import os
import csv
import io
from functools import wraps
from datetime import date, datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, Response
)
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, FoodItem, WasteLog
from database import init_db, seed_demo_data
from ocr_utils import scan_package_image
from recipe_engine import get_recipes_for_items, get_storage_advice

# Create Flask Application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
db.init_app(app)

# Ensure upload and sample directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['BASE_DIR'], 'static', 'sample_images'), exist_ok=True)

# ---------------------------------------------------------
# Authentication Decorator
# ---------------------------------------------------------
def login_required(f):
    """Protects routes so only logged-in users can access them."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# Context Processor (Global Template Variables)
# ---------------------------------------------------------
@app.context_processor
def inject_global_data():
    """Injects user badges and today's date into every Jinja template."""
    data = {'today': date.today().strftime('%Y-%m-%d')}
    if 'user_id' in session:
        user_id = session['user_id']
        # Count active items expiring in 0-3 days
        user = db.session.get(User, user_id)
        if user:
            expiring_count = sum(
                1 for item in user.food_items 
                if not item.is_consumed and not item.is_wasted and 0 <= item.days_remaining <= 3
            )
            data['expiring_soon_count'] = expiring_count
            data['current_user'] = user
    return data

def allowed_file(filename):
    """Validates uploaded image file extensions."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ---------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------
@app.route('/')
def index():
    """Root route redirects to dashboard if logged in, else login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with validation and password hashing."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic validations
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        # Check existing email
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route with secure hash verification and session creation."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clears user session."""
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('login'))

# ---------------------------------------------------------
# Dashboard Route
# ---------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard displaying:
    - Status counts (Fresh, Expiring Soon, Expired)
    - Waste diversion analytics
    - Chart data for Chart.js
    - Urgent items requiring immediate action
    - Recently added foods
    """
    user_id = session['user_id']
    user = db.session.get(User, user_id)

    # Active food items
    active_items = [
        item for item in user.food_items 
        if not item.is_consumed and not item.is_wasted
    ]

    total_items = len(active_items)
    fresh_count = sum(1 for item in active_items if item.status == 'Fresh')
    expiring_count = sum(1 for item in active_items if item.status == 'Expiring Soon')
    expired_count = sum(1 for item in active_items if item.status == 'Expired')

    # Urgent items: expiring in 0-3 days, sorted by days remaining
    urgent_items = sorted(
        [item for item in active_items if item.status == 'Expiring Soon'],
        key=lambda x: x.days_remaining
    )

    # Recently added (last 5)
    recent_items = sorted(active_items, key=lambda x: x.created_at, reverse=True)[:5]

    # Category distribution for Bar Chart
    category_counts_dict = {}
    for item in active_items:
        category_counts_dict[item.category] = category_counts_dict.get(item.category, 0) + 1

    category_labels = list(category_counts_dict.keys())
    category_counts = list(category_counts_dict.values())

    # Waste statistics from WasteLog
    consumed_logs = WasteLog.query.filter_by(user_id=user_id, action='CONSUMED').all()
    wasted_logs = WasteLog.query.filter_by(user_id=user_id, action='WASTED').all()
    total_consumed = len(consumed_logs)
    total_wasted = len(wasted_logs)
    total_diverted = total_consumed + total_wasted

    if total_diverted > 0:
        waste_diversion_rate = round((total_consumed / total_diverted) * 100, 1)
    else:
        waste_diversion_rate = 100.0 if total_items > 0 else 0.0

    return render_template(
        'dashboard.html',
        total_items=total_items,
        fresh_count=fresh_count,
        expiring_count=expiring_count,
        expired_count=expired_count,
        urgent_items=urgent_items,
        recent_items=recent_items,
        category_labels=category_labels,
        category_counts=category_counts,
        total_consumed=total_consumed,
        total_wasted=total_wasted,
        waste_diversion_rate=waste_diversion_rate
    )

# ---------------------------------------------------------
# Food Inventory CRUD Routes
# ---------------------------------------------------------
@app.route('/inventory')
@login_required
def inventory():
    """
    Displays full food inventory with search, multi-filter, and sorting.
    """
    user_id = session['user_id']
    query = FoodItem.query.filter_by(user_id=user_id, is_consumed=False, is_wasted=False)

    # Search keyword
    search_query = request.args.get('search', '').strip()
    if search_query:
        query = query.filter(FoodItem.name.ilike(f'%{search_query}%'))

    # Category filter
    selected_category = request.args.get('category', '').strip()
    if selected_category:
        query = query.filter_by(category=selected_category)

    # Storage filter
    selected_storage = request.args.get('storage', '').strip()
    if selected_storage:
        query = query.filter_by(storage_location=selected_storage)

    items = query.all()

    # Status filter (computed dynamically based on expiry_date)
    selected_status = request.args.get('status', '').strip()
    if selected_status:
        items = [i for i in items if i.status == selected_status]

    # Sorting
    selected_sort = request.args.get('sort', 'expiry_asc').strip()
    if selected_sort == 'expiry_asc':
        items = sorted(items, key=lambda x: x.expiry_date)
    elif selected_sort == 'expiry_desc':
        items = sorted(items, key=lambda x: x.expiry_date, reverse=True)
    elif selected_sort == 'name_asc':
        items = sorted(items, key=lambda x: x.name.lower())
    elif selected_sort == 'date_added':
        items = sorted(items, key=lambda x: x.created_at, reverse=True)

    return render_template(
        'inventory.html',
        items=items,
        search_query=search_query,
        selected_category=selected_category,
        selected_status=selected_status,
        selected_storage=selected_storage,
        selected_sort=selected_sort
    )

@app.route('/add-food', methods=['GET', 'POST'])
@login_required
def add_food():
    """Manual food item entry with image upload."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        purchase_date_str = request.form.get('purchase_date')
        expiry_date_str = request.form.get('expiry_date')
        quantity_str = request.form.get('quantity', '1.0')
        unit = request.form.get('unit', 'pcs')
        storage_location = request.form.get('storage_location', 'Refrigerator')
        notes = request.form.get('notes', '').strip()

        if not name or not expiry_date_str:
            flash('Food name and expiry date are required.', 'danger')
            return render_template('add_food.html')

        try:
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date() if purchase_date_str else date.today()
            quantity = float(quantity_str)
        except ValueError:
            flash('Invalid date or quantity format.', 'danger')
            return render_template('add_food.html')

        # Handle optional image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = f"user_{session['user_id']}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
                save_dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_dest)
                image_path = f"/static/uploads/{filename}"

        food_item = FoodItem(
            user_id=session['user_id'],
            name=name,
            category=category,
            purchase_date=purchase_date,
            expiry_date=expiry_date,
            quantity=quantity,
            unit=unit,
            storage_location=storage_location,
            notes=notes,
            image_path=image_path
        )
        db.session.add(food_item)
        db.session.commit()

        flash(f'"{name}" successfully added to your inventory!', 'success')
        return redirect(url_for('inventory'))

    return render_template('add_food.html')

@app.route('/edit-food/<int:food_id>', methods=['GET', 'POST'])
@login_required
def edit_food(food_id):
    """Edit existing food item."""
    food = db.session.get(FoodItem, food_id)
    if not food or food.user_id != session['user_id']:
        flash('Food item not found.', 'danger')
        return redirect(url_for('inventory'))

    if request.method == 'POST':
        food.name = request.form.get('name', '').strip()
        food.category = request.form.get('category', '').strip()
        food.storage_location = request.form.get('storage_location', '').strip()
        food.unit = request.form.get('unit', 'pcs')
        food.notes = request.form.get('notes', '').strip()

        try:
            food.quantity = float(request.form.get('quantity', '1.0'))
            food.purchase_date = datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date()
            food.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date or number values provided.', 'danger')
            return render_template('edit_food.html', food=food)

        # Handle replacement image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = f"user_{session['user_id']}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
                save_dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_dest)
                food.image_path = f"/static/uploads/{filename}"

        db.session.commit()
        flash(f'Updated "{food.name}" successfully!', 'success')
        return redirect(url_for('food_details', food_id=food.id))

    return render_template('edit_food.html', food=food)

@app.route('/delete-food/<int:food_id>', methods=['POST'])
@login_required
def delete_food(food_id):
    """Deletes a food item and removes associated image file if any."""
    food = db.session.get(FoodItem, food_id)
    if food and food.user_id == session['user_id']:
        # Remove uploaded file if local
        if food.image_path and food.image_path.startswith('/static/uploads/'):
            fname = os.path.basename(food.image_path)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            if os.path.exists(full_path):
                try: os.remove(full_path)
                except Exception: pass

        name = food.name
        db.session.delete(food)
        db.session.commit()
        flash(f'Deleted "{name}" from inventory.', 'info')
    return redirect(request.referrer or url_for('inventory'))

@app.route('/mark-consumed/<int:food_id>', methods=['POST'])
@login_required
def mark_consumed(food_id):
    """
    Marks a food item as consumed/eaten.
    Logs into WasteLog to increase the food waste reduction score.
    """
    food = db.session.get(FoodItem, food_id)
    if food and food.user_id == session['user_id']:
        food.is_consumed = True
        log = WasteLog(
            user_id=food.user_id,
            food_name=food.name,
            category=food.category,
            quantity=food.quantity,
            unit=food.unit,
            action='CONSUMED'
        )
        db.session.add(log)
        db.session.commit()
        flash(f'Great job! "{food.name}" consumed and logged. Food waste prevented!', 'success')
    return redirect(request.referrer or url_for('inventory'))

@app.route('/mark-wasted/<int:food_id>', methods=['POST'])
@login_required
def mark_wasted(food_id):
    """
    Marks an expired food item as discarded/wasted.
    Logs into WasteLog to record waste metrics.
    """
    food = db.session.get(FoodItem, food_id)
    if food and food.user_id == session['user_id']:
        food.is_wasted = True
        log = WasteLog(
            user_id=food.user_id,
            food_name=food.name,
            category=food.category,
            quantity=food.quantity,
            unit=food.unit,
            action='WASTED'
        )
        db.session.add(log)
        db.session.commit()
        flash(f'Logged "{food.name}" as discarded. Track your "Use Soon" alerts to prevent this!', 'warning')
    return redirect(request.referrer or url_for('expired_items'))

# ---------------------------------------------------------
# OCR Scan Routes
# ---------------------------------------------------------
@app.route('/scan-ocr')
@login_required
def scan_ocr():
    """OCR Package scanning interface page."""
    return render_template('scan_ocr.html')

@app.route('/api/scan-ocr', methods=['POST'])
@login_required
def api_scan_ocr():
    """
    API endpoint accepting an uploaded food packaging image,
    running the OCR text extraction and regex date parser, and returning JSON.
    """
    if 'package_image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file uploaded.'}), 400

    file = request.files['package_image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected image file.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file format. Please upload JPG, PNG, or WEBP.'}), 400

    # Save image to upload folder
    filename = f"scan_{session['user_id']}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    # Run OCR scanning engine
    ocr_result = scan_package_image(save_path)
    ocr_result['saved_image_url'] = f"/static/uploads/{filename}"

    return jsonify(ocr_result)

@app.route('/confirm-ocr-food', methods=['POST'])
@login_required
def confirm_ocr_food():
    """
    Saves the user-confirmed OCR detected expiry date and details
    into the database inventory.
    """
    name = request.form.get('name', '').strip()
    category = request.form.get('category', 'Dairy')
    expiry_date_str = request.form.get('expiry_date')
    quantity = float(request.form.get('quantity', '1.0'))
    unit = request.form.get('unit', 'pcs')
    storage_location = request.form.get('storage_location', 'Refrigerator')
    notes = request.form.get('notes', 'Scanned via OCR')
    image_path = request.form.get('image_path')

    if not name or not expiry_date_str:
        flash('Food name and expiry date are required.', 'danger')
        return redirect(url_for('scan_ocr'))

    try:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('scan_ocr'))

    new_item = FoodItem(
        user_id=session['user_id'],
        name=name,
        category=category,
        purchase_date=date.today(),
        expiry_date=expiry_date,
        quantity=quantity,
        unit=unit,
        storage_location=storage_location,
        notes=notes,
        image_path=image_path if image_path else None
    )
    db.session.add(new_item)
    db.session.commit()

    flash(f'Successfully added "{name}" with detected expiry date {expiry_date}!', 'success')
    return redirect(url_for('inventory'))

# ---------------------------------------------------------
# Food Waste Reduction ("Use Soon") Section
# ---------------------------------------------------------
@app.route('/expiring-soon')
@login_required
def expiring_soon():
    """
    "Use Soon" Section:
    Displays items with 0 to 3 days shelf-life remaining,
    suggested immediate actions, and matched recipe recommendations.
    """
    user_id = session['user_id']
    user = db.session.get(User, user_id)

    # Filter items expiring in 0-3 days
    urgent_items = [
        item for item in user.food_items
        if not item.is_consumed and not item.is_wasted and 0 <= item.days_remaining <= 3
    ]
    urgent_items = sorted(urgent_items, key=lambda x: x.days_remaining)

    # Get tailored recipe recommendations
    recipes = get_recipes_for_items(urgent_items)

    return render_template('expiring_soon.html', items=urgent_items, recipes=recipes)

# ---------------------------------------------------------
# Expired Food Items Section
# ---------------------------------------------------------
@app.route('/expired')
@login_required
def expired_items():
    """
    Dedicated section displaying all expired food items (days_remaining < 0)
    with disposal guidelines and waste logging actions.
    """
    user_id = session['user_id']
    user = db.session.get(User, user_id)

    expired_list = [
        item for item in user.food_items
        if not item.is_consumed and not item.is_wasted and item.days_remaining < 0
    ]
    expired_list = sorted(expired_list, key=lambda x: x.expiry_date)

    return render_template('expired_items.html', items=expired_list)

# ---------------------------------------------------------
# Food Details Route
# ---------------------------------------------------------
@app.route('/food/<int:food_id>')
@login_required
def food_details(food_id):
    """Detailed view for a single food item with storage tips and recipes."""
    food = db.session.get(FoodItem, food_id)
    if not food or food.user_id != session['user_id']:
        flash('Food item not found.', 'danger')
        return redirect(url_for('inventory'))

    storage_advice = get_storage_advice(food.category, food.name)
    matched_recipes = get_recipes_for_items([food])

    return render_template(
        'food_details.html',
        food=food,
        storage_advice=storage_advice,
        matched_recipes=matched_recipes
    )

# ---------------------------------------------------------
# User Profile & Data Export
# ---------------------------------------------------------
@app.route('/profile')
@login_required
def profile():
    """User profile overview and management."""
    user = db.session.get(User, session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Secure password update."""
    user = db.session.get(User, session['user_id'])
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_new_password = request.form.get('confirm_new_password', '')

    if not user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))

    if new_password != confirm_new_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('profile'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('profile'))

    user.set_password(new_password)
    db.session.commit()
    flash('Password updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/export-csv')
@login_required
def export_csv():
    """Exports all user's food inventory to a downloadable CSV file."""
    user = db.session.get(User, session['user_id'])
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV Header
    writer.writerow([
        'ID', 'Name', 'Category', 'Quantity', 'Unit', 
        'Storage Location', 'Purchase Date', 'Expiry Date', 
        'Days Remaining', 'Status', 'Notes'
    ])

    for item in user.food_items:
        if not item.is_consumed and not item.is_wasted:
            writer.writerow([
                item.id,
                item.name,
                item.category,
                item.quantity,
                item.unit,
                item.storage_location,
                item.purchase_date.strftime('%Y-%m-%d') if item.purchase_date else '',
                item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else '',
                item.days_remaining,
                item.status,
                item.notes or ''
            ])

    output.seek(0)
    filename = f"food_inventory_backup_{date.today().strftime('%Y%m%d')}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

# ---------------------------------------------------------
# Application Initialization & Runner
# ---------------------------------------------------------
def setup_app():
    """Initializes tables and seeds demo data."""
    init_db(app)
    seed_demo_data(app)

if __name__ == '__main__':
    setup_app()
    print("==================================================================")
    print(" Smart Food Expiry Detection & Food Waste Reduction System")
    print(" Running at: http://127.0.0.1:5000")
    print(" Evaluation demo user: demo@smartfood.com / demo123")
    print("==================================================================")
    app.run(debug=True, port=5000)
