# Smart Food Expiry Detection and Food Waste Reduction System

> **A Full-Stack College-Level CSE Academic Project**  
> Built with **Python, Flask, SQLite/MySQL, Tesseract OCR, Bootstrap 5, and Chart.js**

---

## 1. Project Abstract & Overview

Household and commercial food waste contributes significantly to global greenhouse gas emissions and financial losses. A primary driver of preventable food waste is the lack of systematic inventory visibility and forgotten expiration dates on packaged groceries.

The **Smart Food Expiry Detection and Food Waste Reduction System** is an intelligent web application designed to track food inventory, automatically extract expiry dates from packaging using **Optical Character Recognition (OCR)**, dynamically classify food shelf life into actionable status levels (**Fresh**, **Expiring Soon**, **Expired**), alert users to items nearing expiration, recommend zero-waste recipes, and quantify food waste diversion metrics.

---

## 2. Problem Statement & Objectives

### Problem Statement
Most individuals store food in refrigerators and pantries without keeping track of expiration dates. Food packages have diverse, faint, or dot-matrix expiration formats (e.g., `EXP 15/10/26`, `BEST BEFORE 20-09-2026`, `USE BY 05/11/26`), which are easily overlooked. As a result, edible items expire unnoticed, leading to financial loss, unnecessary grocery spending, and municipal food waste burdens.

### Core Objectives
1. **Automated Expiry Capture:** Allow users to scan food packaging images and automatically extract expiry dates using OCR and regex pattern recognition.
2. **Dynamic Shelf-Life Classification:**
   - 🟢 **Fresh:** More than 3 days remaining (`> 3 days`).
   - 🟡 **Expiring Soon ("Use Soon"):** 0 to 3 days remaining (`0 to 3 days`).
   - 🔴 **Expired:** Expiry date has passed (`< 0 days`).
3. **Food Waste Prevention & Recipe Recommendation:** Deliver intelligent recipe suggestions matched with expiring ingredients to encourage immediate utilization.
4. **Interactive Visualization:** Present inventory health and waste reduction statistics (items consumed vs. discarded, waste diversion score) via Chart.js graphs.
5. **Robust Inventory Management:** Provide multi-criteria search, categorization, storage location tracking, sorting, and CSV backup export.

---

## 3. Existing System vs. Proposed System

| Feature / Metric | Existing System (Manual / Traditional) | Proposed Smart Food System |
| :--- | :--- | :--- |
| **Expiry Tracking** | Manual handwritten notes or memory; frequently forgotten | Automated digital inventory with countdown alerts |
| **Data Entry** | Tedious manual typing of every date | Instant OCR package scanning with auto-date extraction |
| **Status Classification** | Subjective visual guess | Mathematically computed real-time status badges |
| **Waste Mitigation** | Food thrown away once spoiled | "Use Soon" priority alerts & tailored recipe ideas |
| **Waste Analytics** | None | Real-time waste reduction rate (%) and consumption logs |
| **Storage Optimization** | Generic knowledge | Tailored scientific storage advice per food category |
| **Data Portability** | None | One-click CSV inventory export |

---

## 4. System Architecture & Data Flow

```
[User Browser / Mobile]
         │
         ▼
[Frontend UI Layer (Bootstrap 5.3 + Chart.js)]
         │  HTTP / Multipart Form Uploads
         ▼
[Flask Application Controller (app.py)]
    ├── [Session Auth & Werkzeug Hash Security]
    ├── [Expiry Date Calculation Math Engine]
    ├── [OCR Pipeline (Pillow Preprocessing + Pytesseract + Regex)]
    └── [Smart Recipe & Storage Recommendation Engine]
         │
         ▼
[Flask-SQLAlchemy ORM Layer]
         │
   ┌─────┴────────────────┐
   ▼                      ▼
[SQLite DB]        [MySQL DB (Optional)]
(food_inventory.db) (via PyMySQL)
```

---

## 5. Database Schema & ER Design

### Table 1: `users`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| `name` | VARCHAR(100) | NOT NULL | User's full name |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE, INDEX | Login email |
| `password_hash` | VARCHAR(255) | NOT NULL | Salted Werkzeug password hash |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

### Table 2: `food_items`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique food item ID |
| `user_id` | INTEGER | FOREIGN KEY (`users.id`) | Owner reference |
| `name` | VARCHAR(120) | NOT NULL | Name of food item |
| `category` | VARCHAR(50) | NOT NULL | Dairy, Fruits, Vegetables, Bakery, etc. |
| `purchase_date` | DATE | NOT NULL | Date bought or recorded |
| `expiry_date` | DATE | NOT NULL | Stamped expiration date |
| `quantity` | FLOAT | NOT NULL, DEFAULT 1.0 | Quantity amount |
| `unit` | VARCHAR(20) | NOT NULL, DEFAULT 'pcs' | pcs, kg, g, L, ml, packet, etc. |
| `storage_location`| VARCHAR(50) | NOT NULL | Refrigerator, Freezer, Pantry, Countertop |
| `image_path` | VARCHAR(255) | NULLABLE | Uploaded product photo path |
| `is_consumed` | BOOLEAN | DEFAULT FALSE | Marked when eaten |
| `is_wasted` | BOOLEAN | DEFAULT FALSE | Marked when discarded |
| `notes` | VARCHAR(255) | NULLABLE | Storage notes or reminders |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record created timestamp |

### Table 3: `waste_logs`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Log entry ID |
| `user_id` | INTEGER | FOREIGN KEY (`users.id`) | User reference |
| `food_name` | VARCHAR(120) | NOT NULL | Name of food logged |
| `category` | VARCHAR(50) | NULLABLE | Food category |
| `quantity` | FLOAT | DEFAULT 1.0 | Quantity |
| `unit` | VARCHAR(20) | DEFAULT 'pcs' | Unit |
| `action` | VARCHAR(20) | NOT NULL | `CONSUMED` or `WASTED` |
| `logged_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Action timestamp |

---

## 6. Technologies Used

- **Backend:** Python 3.13, Flask 3.0.3, Flask-SQLAlchemy 3.1.1, Werkzeug 3.0.3
- **Database:** SQLite (default for development), MySQL (production/XAMPP compatible)
- **OCR & Computer Vision:** Tesseract OCR, `pytesseract` 0.3.10, Pillow (PIL) 10.4.0
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons 1.11.3
- **Visualization:** Chart.js 4.4.3
- **Testing:** Pytest 8.2.2

---

## 7. Project Folder Structure

```
project ai/
├── app.py                      # Main Flask application and REST routes
├── config.py                   # App configuration (DB URI, upload limits, thresholds)
├── models.py                   # SQLAlchemy database models (User, FoodItem, WasteLog)
├── database.py                 # Database initialization and sample demo data seeder
├── ocr_utils.py                # Image preprocessing, Tesseract runner, and regex date parsing
├── recipe_engine.py            # Waste-reduction recipe database and storage advisor
├── requirements.txt            # Python dependencies
├── create_sample_images.py     # Script to generate sample package photos for testing
├── food_inventory.db           # SQLite database file (created automatically)
├── static/
│   ├── css/
│   │   └── style.css           # Modern custom styling, cards, status badges, dropzone
│   ├── js/
│   │   ├── main.js             # Live date calculator, image previewer, view toggler
│   │   └── ocr_scanner.js      # Drag-and-drop file upload, AJAX OCR, confirmation modal
│   ├── sample_images/          # Demo food package images for instant OCR evaluation
│   └── uploads/                # Directory for user-uploaded product and scan images
├── templates/
│   ├── base.html               # Master layout with responsive navbar, notifications, and footer
│   ├── login.html              # Login page with demo credentials quick-fill button
│   ├── register.html           # User registration page with client validation
│   ├── dashboard.html          # Stats cards, Chart.js graphs, urgent actions, waste stats
│   ├── inventory.html          # Food inventory with search, multi-filter, sort, table/card toggle
│   ├── add_food.html           # Manual food entry with live countdown badge
│   ├── scan_ocr.html           # OCR scan page: upload, auto-extract date, confirm & save
│   ├── expiring_soon.html      # "Use Soon" section with countdown and matched recipes
│   ├── expired_items.html      # Expired foods section with waste logging and safety tips
│   ├── food_details.html       # Full detail view with scientific preservation tips and recipes
│   ├── edit_food.html          # Edit food item details
│   └── profile.html            # Profile overview, password change, CSV export
└── tests/
    ├── test_app.py             # Unit tests for expiry math, auth, OCR regex, recipes
    └── test_routes.py          # Integration tests for all web endpoints & CSV export
```

---

## 8. Installation & Setup Instructions (Windows)

### Step 1: Open Terminal / PowerShell
Navigate to the project root directory:
```powershell
cd "c:\Users\user\Desktop\project ai"
```

### Step 2: Install Python Dependencies
Install all required libraries using `pip`:
```powershell
pip install -r requirements.txt
```

### Step 3 (Optional for Full OCR): Install Tesseract OCR on Windows
The application includes a built-in fallback parser and demo test package images so you can evaluate the OCR workflow immediately even without Tesseract installed.

To enable full OCR on live external photos:
1. Download the Windows installer from: [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
   - Installer name: `tesseract-ocr-w64-setup-5.3.x.exe`
2. Run the installer and keep the default installation path:
   `C:\Program Files\Tesseract-OCR`
3. Add `C:\Program Files\Tesseract-OCR` to your Windows System `PATH` environment variable.
4. Restart your PowerShell terminal.

---

## 9. Running the Application

Start the Flask development server:
```powershell
python app.py
```

Open your web browser and visit:
```
http://127.0.0.1:5000
```

### Quick Evaluation Login
A realistic demo dataset is pre-seeded on startup:
- **Email:** `demo@smartfood.com`
- **Password:** `demo123`
*(A quick autofill button is provided directly on the login page for convenience during evaluation).*

---

## 10. Database Migration to MySQL (XAMPP / MySQL Server)

The application uses **Flask-SQLAlchemy**, which makes database switching effortless without altering application code.

To switch from SQLite to MySQL:

1. Start **Apache** and **MySQL** in the **XAMPP Control Panel**.
2. Open phpMyAdmin (`http://localhost/phpmyadmin`) and create a new database:
   ```sql
   CREATE DATABASE food_inventory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Install the MySQL driver:
   ```powershell
   pip install pymysql cryptography
   ```
4. Open [config.py](file:///c:/Users/user/Desktop/project%20ai/config.py) and change the database URI:
   ```python
   # Replace the SQLite line with:
   SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/food_inventory_db"
   ```
   *(Add your MySQL password after the colon if you have one configured, e.g., `root:mypassword@localhost:3306`).*
5. Restart `python app.py`. Tables and demo records will be created automatically in MySQL!

---

## 11. Automated Testing

Run the automated test suite using `pytest`:
```powershell
python -m pytest tests/ -v
```

**What the tests verify:**
- ✅ Password hashing and authentication security
- ✅ Expiry calculation logic (`Fresh`, `Expiring Soon`, `Expired`)
- ✅ OCR regex pattern recognition across varied packaging date formats
- ✅ Recipe recommendation engine keyword matching
- ✅ Category storage advice retrieval
- ✅ All 10 web routes and CSV data export functionality

---

## 12. Advantages & Current Limitations

### Advantages
1. **Reduces Household Food Waste:** Active visual alerts prevent edible foods from spoiling unnoticed.
2. **Saves Grocery Costs:** Prioritizes items nearing expiration and offers actionable recipe ideas.
3. **Automated Data Entry:** OCR eliminates tedious manual date typing for packaged groceries.
4. **Environmentally Conscious:** Logs waste diversion rates to cultivate sustainable habits.
5. **Beginner-Friendly & Modular:** Clean separation of concerns (MVC architecture) with readable Python code.

### Limitations
1. **Complex Fonts / Damaged Labels:** Dot-matrix stamped dates on heavily wrinkled wrappers can sometimes require manual user confirmation.
2. **Barcode Catalog Dependency:** Initial version relies on OCR text extraction rather than a global UPC/EAN product barcode database.

---

## 13. Future Scope & Roadmap

- **Barcode & QR Code Scanning:** Integrate ZXing or QuaggaJS to instantly lookup food names and nutrition info by barcode.
- **WhatsApp & SMS Alerts:** Connect Twilio API to send daily morning reminders of items expiring today.
- **Computer Vision Freshness Detection:** Integrate a Convolutional Neural Network (CNN) model to visually detect spoilage/brown spots on unpackaged fruits and vegetables.
- **Family / Shared Household Inventory:** Allow multiple family members or roommates to share and sync a single refrigerator inventory.
- **Food Donation Integration:** Connect local surplus food charities to donate unopened items expiring in 2-3 days.

---

## 14. College Viva Questions & Answers (Academic Guide)

### Q1: What is the main problem your project solves?
**Answer:** It addresses consumer food waste caused by forgotten expiration dates. By combining automated OCR date capture, real-time expiry countdowns, and recipe suggestions for items nearing expiration, it helps households consume food before it spoils.

### Q2: What architecture is used in this project?
**Answer:** The project follows the **Model-View-Controller (MVC)** architectural pattern:
- **Model:** Defined in `models.py` using Flask-SQLAlchemy (`User`, `FoodItem`, `WasteLog`).
- **View:** Rendered through Jinja2 HTML templates in `templates/` styled with Bootstrap 5 and Chart.js.
- **Controller:** Implemented in `app.py` as Flask route handlers and business logic modules (`ocr_utils.py`, `recipe_engine.py`).

### Q3: How does the OCR date extraction feature work?
**Answer:**
1. The user uploads a food packaging photo.
2. `Pillow` converts the image to grayscale, enhances contrast, and applies sharpening to make stamped text distinct.
3. `pytesseract` extracts raw text from the processed image.
4. Regular expressions (`re`) look for indicator keywords (`EXP`, `USE BY`, `BEST BEFORE`, `BB`) and extract adjacent date strings across multiple international formats (`DD/MM/YYYY`, `DD-MM-YYYY`, `YYYY-MM-DD`, `DD MMM YYYY`).
5. The extracted candidate is presented to the user for one-click confirmation before database persistence.

### Q4: How is food shelf-life status classified?
**Answer:**
Status is dynamically computed by calculating the difference in days between `expiry_date` and `date.today()`:
- **🟢 Fresh:** Remaining days $> 3$
- **🟡 Expiring Soon:** Remaining days $\in [0, 3]$
- **🔴 Expired:** Remaining days $< 0$

### Q5: Why did you choose SQLite initially and how easy is it to migrate to MySQL?
**Answer:** SQLite is a serverless, zero-configuration, file-based relational database ideal for rapid development and demonstration. Because we implemented Flask-SQLAlchemy (an Object-Relational Mapper), the SQL queries are abstracted; migrating to MySQL requires changing only the `SQLALCHEMY_DATABASE_URI` connection string in `config.py`.

### Q6: How is user authentication secured?
**Answer:** We avoid storing plaintext passwords. Using `werkzeug.security`, passwords are encrypted with `generate_password_hash` using salted PBKDF2 with SHA-256 before storage. During login, `check_password_hash` verifies the hash. Session cookies store authentication state across requests.

### Q7: How does the Recipe Recommendation Engine work?
**Answer:** It utilizes a rule-based matching algorithm in `recipe_engine.py`. It inspects the names and categories of food items expiring within 3 days and matches them against recipe ingredient keywords (e.g., matching milk to smoothies or paneer, and bread to French toast or croutons).

### Q8: How is the Food Waste Reduction Score calculated?
**Answer:** Whenever a user consumes or discards an item, an entry is recorded in `WasteLog`. The waste diversion rate is computed as:
$$\text{Waste Diversion Rate (\%)} = \left( \frac{\text{Total Consumed Items}}{\text{Total Consumed Items} + \text{Total Discarded Items}} \right) \times 100$$
This offers users tangible feedback on their waste prevention habits.

### Q9: What happens if the OCR engine fails to detect a date?
**Answer:** The system follows graceful degradation. If text extraction is indistinct, the UI notifies the user and provides a clean date picker allowing manual date entry. The application never crashes due to OCR ambiguity.

### Q10: What HTTP methods are used and why?
**Answer:**
- `GET`: For idempotent read operations (retrieving the dashboard, viewing inventory, filtering, exporting CSV).
- `POST`: For state-modifying actions (user login, registration, adding food items, editing records, deleting items, marking items as consumed/wasted).
