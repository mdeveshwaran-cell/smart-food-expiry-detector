import os
from PIL import Image, ImageDraw, ImageFont

def create_sample_images():
    output_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'sample_images')
    os.makedirs(output_dir, exist_ok=True)

    samples = [
        {
            'filename': 'sample_milk_exp_2026-10-15.jpg',
            'title': 'FRESH ORGANIC MILK 1L',
            'lines': [
                'Homogenized & Pasteurized',
                'Keep Refrigerated below 4 C',
                '--------------------------------',
                'BEST BEFORE: 15/10/2026',
                'BATCH NO: MK-9042',
                '--------------------------------',
                'Net Volume: 1000 ml'
            ],
            'bg_color': (240, 248, 255),
            'header_color': (30, 80, 150)
        },
        {
            'filename': 'sample_bread_exp_2026-09-20.jpg',
            'title': 'WHOLE WHEAT BREAD',
            'lines': [
                'Freshly Baked Daily',
                'Contains 100% Whole Grains',
                '--------------------------------',
                'EXP: 20-09-2026',
                'LOT: BREAD-501',
                '--------------------------------',
                'Net Wt: 400g'
            ],
            'bg_color': (255, 250, 240),
            'header_color': (140, 70, 20)
        },
        {
            'filename': 'sample_yogurt_exp_2026-11-05.jpg',
            'title': 'NATURAL GREEK YOGURT',
            'lines': [
                'Probiotic Rich & Creamy',
                'Keep Chilled',
                '--------------------------------',
                'USE BY: 05/11/2026',
                'MFG: 05/10/2026',
                '--------------------------------',
                'Net Weight: 500g'
            ],
            'bg_color': (245, 255, 250),
            'header_color': (20, 120, 80)
        }
    ]

    for sample in samples:
        img = Image.new('RGB', (600, 420), color=sample['bg_color'])
        draw = ImageDraw.Draw(img)

        # Draw decorative border
        draw.rectangle([(15, 15), (585, 405)], outline=(200, 200, 200), width=3)
        draw.rectangle([(25, 25), (575, 95)], fill=sample['header_color'])

        # Draw Title
        draw.text((40, 45), sample['title'], fill=(255, 255, 255))

        # Draw Content lines
        y = 120
        for line in sample['lines']:
            if 'BEST BEFORE' in line or 'EXP:' in line or 'USE BY' in line:
                # Highlight expiry date area with dot-matrix style box
                draw.rectangle([(35, y - 5), (565, y + 35)], fill=(255, 255, 220), outline=(220, 180, 50), width=2)
                draw.text((45, y + 5), line, fill=(180, 0, 0))
                y += 45
            else:
                draw.text((45, y), line, fill=(50, 50, 50))
                y += 35

        target_path = os.path.join(output_dir, sample['filename'])
        img.save(target_path, 'JPEG', quality=95)
        print(f"Created sample image: {target_path}")

if __name__ == '__main__':
    create_sample_images()
