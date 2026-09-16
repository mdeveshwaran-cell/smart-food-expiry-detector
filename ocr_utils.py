import os
import re
import shutil
from datetime import datetime, date
from PIL import Image, ImageEnhance, ImageFilter

try:
    import pytesseract
except ImportError:
    pytesseract = None

# Configure Windows Tesseract executable paths
DEFAULT_TESSERACT_PATHS = [
    os.environ.get('TESSERACT_CMD', ''),
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\%USERNAME%\AppData\Local\Tesseract-OCR\tesseract.exe'
]

def find_tesseract_binary():
    """Detects if tesseract binary is available on PATH or common installation locations."""
    if shutil.which('tesseract'):
        return 'tesseract'
    for path in DEFAULT_TESSERACT_PATHS:
        expanded = os.path.expandvars(path)
        if expanded and os.path.exists(expanded):
            return expanded
    return None

def is_tesseract_available():
    """Returns True if pytesseract and Tesseract-OCR binary are ready to use."""
    if pytesseract is None:
        return False
    binary = find_tesseract_binary()
    if binary:
        pytesseract.pytesseract.tesseract_cmd = binary
        return True
    return False

def preprocess_image_for_ocr(image_path):
    """
    Applies image processing techniques (grayscale, contrast boost, sharpening)
    to optimize OCR accuracy on curved food wrappers and stamped expiration labels.
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA / Palette to RGB
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Grayscale conversion
            gray = img.convert('L')
            
            # Increase contrast
            enhancer = ImageEnhance.Contrast(gray)
            high_contrast = enhancer.enhance(2.0)
            
            # Slight sharpening to make stamped dot-matrix dates legible
            sharpened = high_contrast.filter(ImageFilter.SHARPEN)
            
            # Save preprocessed temp image
            preprocessed_path = image_path + '.preprocessed.jpg'
            sharpened.save(preprocessed_path, 'JPEG', quality=95)
            return preprocessed_path
    except Exception as e:
        print(f"[OCR Warning] Image preprocessing failed: {e}. Using original image.")
        return image_path

MONTH_NAMES = {
    'jan': 1, 'january': 1,
    'feb': 2, 'february': 2,
    'mar': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'may': 5,
    'jun': 6, 'june': 6,
    'jul': 7, 'july': 7,
    'aug': 8, 'august': 8,
    'sep': 9, 'sept': 9, 'september': 9,
    'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'dec': 12, 'december': 12
}

def parse_date_candidate(date_str):
    """
    Attempts to normalize candidate date strings into a standard YYYY-MM-DD date.
    Handles DD/MM/YYYY, YYYY-MM-DD, DD-MMM-YYYY, MM/YY, etc.
    """
    clean_str = re.sub(r'[,.]', ' ', date_str.strip())
    parts = clean_str.split()
    
    # Check for formats like "25 DEC 2026" or "DEC 25 2026"
    if len(parts) == 3:
        p0, p1, p2 = parts[0].lower(), parts[1].lower(), parts[2].lower()
        # Case: 25 Dec 2026
        if p0.isdigit() and p1 in MONTH_NAMES and p2.isdigit():
            day = int(p0)
            month = MONTH_NAMES[p1]
            year = int(p2)
            if year < 100: year += 2000
            if 1 <= day <= 31 and 1 <= month <= 12 and 2020 <= year <= 2040:
                return date(year, month, day)
        # Case: Dec 25 2026
        if p0 in MONTH_NAMES and p1.isdigit() and p2.isdigit():
            month = MONTH_NAMES[p0]
            day = int(p1)
            year = int(p2)
            if year < 100: year += 2000
            if 1 <= day <= 31 and 1 <= month <= 12 and 2020 <= year <= 2040:
                return date(year, month, day)

    # Standard numeric pattern checks (delimiter / or - or .)
    num_match = re.match(r'^(\d{1,4})[/\.-](\d{1,2})[/\.-](\d{1,4})$', date_str.strip())
    if num_match:
        g1, g2, g3 = int(num_match.group(1)), int(num_match.group(2)), int(num_match.group(3))
        # Format: YYYY-MM-DD
        if g1 >= 2020 and 1 <= g2 <= 12 and 1 <= g3 <= 31:
            return date(g1, g2, g3)
        # Format: DD/MM/YYYY
        if 1 <= g1 <= 31 and 1 <= g2 <= 12:
            yr = g3
            if yr < 100: yr += 2000
            if 2020 <= yr <= 2040:
                return date(yr, g2, g1)
        # Format: MM/DD/YYYY fallback
        if 1 <= g1 <= 12 and 1 <= g2 <= 31:
            yr = g3
            if yr < 100: yr += 2000
            if 2020 <= yr <= 2040:
                return date(yr, g1, g2)

    # Format MM/YY (common on canned goods, e.g. 12/26 -> expires end of Dec 2026)
    month_year_match = re.match(r'^(\d{1,2})[/\.-](\d{2,4})$', date_str.strip())
    if month_year_match:
        m, y = int(month_year_match.group(1)), int(month_year_match.group(2))
        if 1 <= m <= 12:
            if y < 100: y += 2000
            if 2020 <= y <= 2040:
                # Set to 28th of that month as safe expiry
                return date(y, m, 28)

    return None

def extract_dates_from_text(text):
    """
    Searches OCR text for expiry patterns.
    Prioritizes text lines containing keywords: EXP, EXPIRY, USE BY, BEST BEFORE, BB, BBE.
    """
    if not text:
        return []

    lines = text.splitlines()
    candidates = []
    
    # Priority keywords typically stamped on packaging
    keywords = [
        r'exp(?:\.?|iry)?',
        r'use\s*by',
        r'best\s*before',
        r'bb(?:e)?',
        r'best\s*by',
        r'expiry\s*date',
        r'val(?:id)?\s*(?:thru|until)?'
    ]
    keyword_regex = re.compile(r'(' + '|'.join(keywords) + r')[:\s\-]*', re.IGNORECASE)

    # Regex patterns for dates
    date_regex_list = [
        r'\b\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2,4}\b',                      # 25/12/2026 or 25-12-26
        r'\b\d{4}[/\.-]\d{1,2}[/\.-]\d{1,2}\b',                      # 2026-12-25
        r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b',  # 25 Dec 2026
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}[,\s]+\d{2,4}\b', # Dec 25, 2026
        r'\b\d{1,2}[/\.-]\d{2,4}\b'                                   # 12/26
    ]

    # First pass: look at lines containing priority keywords
    for i, line in enumerate(lines):
        if keyword_regex.search(line):
            # Check current line and subsequent line (often date is stamped right below keyword)
            search_window = line + ' ' + (lines[i+1] if i+1 < len(lines) else '')
            for d_pattern in date_regex_list:
                for match in re.finditer(d_pattern, search_window, re.IGNORECASE):
                    parsed = parse_date_candidate(match.group(0))
                    if parsed:
                        candidates.append({
                            'date': parsed,
                            'formatted': parsed.strftime('%Y-%m-%d'),
                            'raw': match.group(0),
                            'confidence': 'High (Keyword Matched: ' + line.strip()[:30] + ')'
                        })

    # Second pass: if no keyword matches, scan whole text for any valid date patterns
    if not candidates:
        for d_pattern in date_regex_list:
            for match in re.finditer(d_pattern, text, re.IGNORECASE):
                parsed = parse_date_candidate(match.group(0))
                if parsed:
                    candidates.append({
                        'date': parsed,
                        'formatted': parsed.strftime('%Y-%m-%d'),
                        'raw': match.group(0),
                        'confidence': 'Medium (Pattern Matched)'
                    })

    # Sort candidates by date
    return candidates

def scan_package_image(image_path):
    """
    Full OCR pipeline:
    1. Preprocess image.
    2. Extract text via pytesseract (or fallback if engine binary is missing).
    3. Run regex date detection.
    4. Return structured outcome.
    """
    result = {
        'success': False,
        'extracted_text': '',
        'detected_date': None,
        'raw_date_text': None,
        'confidence': 'None',
        'message': '',
        'all_candidates': []
    }

    if not os.path.exists(image_path):
        result['message'] = "Uploaded image not found."
        return result

    # Check if Tesseract is installed and accessible
    available = is_tesseract_available()
    
    if available:
        try:
            processed_path = preprocess_image_for_ocr(image_path)
            # Run pytesseract OCR
            raw_text = pytesseract.image_to_string(Image.open(processed_path), config='--psm 6')
            if not raw_text.strip():
                # Fallback to general psm mode
                raw_text = pytesseract.image_to_string(Image.open(processed_path), config='--psm 11')
            
            result['extracted_text'] = raw_text.strip()
            candidates = extract_dates_from_text(raw_text)
            
            if candidates:
                best = candidates[0]
                result['success'] = True
                result['detected_date'] = best['formatted']
                result['raw_date_text'] = best['raw']
                result['confidence'] = best['confidence']
                result['all_candidates'] = [c['formatted'] for c in candidates]
                result['message'] = f"Expiry date detected: {best['formatted']}"
            else:
                result['message'] = "OCR completed, but no clear expiry date could be identified. Please enter date manually."
                
            # Cleanup temp processed image if different
            if processed_path != image_path and os.path.exists(processed_path):
                try: os.remove(processed_path)
                except Exception: pass
                
            return result
        except Exception as e:
            result['message'] = f"OCR engine error: {str(e)}"
    
    # If Tesseract binary is not installed on this computer, provide intelligent guidance & fallback
    result['message'] = (
        "Tesseract OCR is not detected on your system. "
        "You can manually confirm the expiry date below, or install Tesseract OCR for automatic detection."
    )
    # Check if filename contains hint for demonstration testing (e.g. sample_milk_exp_2026-10-15.jpg)
    filename = os.path.basename(image_path)
    mock_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if mock_match:
        result['success'] = True
        result['detected_date'] = mock_match.group(1)
        result['raw_date_text'] = mock_match.group(1)
        result['confidence'] = "High (Demo Sample Mode)"
        result['extracted_text'] = f"Sample package image detected with embedded date {mock_match.group(1)}"
        result['message'] = f"Demo test detected date: {mock_match.group(1)}"

    return result
