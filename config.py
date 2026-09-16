import os

class Config:
    """
    Application Configuration
    -------------------------
    Supports SQLite for development / demo and provides a plug-and-play
    connection string for MySQL migration.
    """
    # Secret key for session management and CSRF security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-food-waste-secret-key-cse-2026')

    # Base directory of the project
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # SQLite Database Configuration (Default)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'food_inventory.db')}"
    )

    # To migrate to MySQL, simply uncomment the following line and update credentials:
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:yourpassword@localhost:3306/food_inventory_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads Configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Megabytes max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}

    # Expiry Classification Thresholds (in days)
    # > 3 days -> Fresh (Green)
    # 0 to 3 days -> Expiring Soon (Yellow/Amber)
    # < 0 days -> Expired (Red)
    EXPIRING_SOON_DAYS = 3

    # Optional Tesseract OCR Path configuration for Windows
    # If installed in default 64-bit path, pytesseract can use this directly
    TESSERACT_CMD = os.environ.get(
        'TESSERACT_CMD',
        r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    )
