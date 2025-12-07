import cv2
import pytesseract
import re
import numpy as np
from PIL import Image

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    
    # 1. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Resize 2x
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # 3. Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # 4. Thresholding (Otsu)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return img, gray, binary

def find_curp_region(img, text_data):
    # Try to find "CURP" keyword and crop region to the right
    n_boxes = len(text_data['text'])
    for i in range(n_boxes):
        if 'CURP' in text_data['text'][i].upper():
            (x, y, w, h) = (text_data['left'][i], text_data['top'][i], text_data['width'][i], text_data['height'][i])
            
            # Define ROI relative to "CURP" label
            # Usually CURP is to the right or below. In INE types, it's often to the right.
            # Let's try a box to the right
            roi_x = x + w + 10
            roi_y = y - 10
            roi_w = 400 # Adjust based on expected width of CURP at 2x scale
            roi_h = h + 20
            
            return (roi_x, roi_y, roi_w, roi_h)
    return None

def test_ocr(image_path):
    print(f"Testing OCR on {image_path}")
    
    img, gray, binary = preprocess_image(image_path)
    
    configs = [
        '--oem 3 --psm 3 -l spa',
        '--oem 3 --psm 6 -l spa',
        '--oem 3 --psm 11 -l spa'
    ]
    
    print("\n--- Full Image OCR ---")
    for config in configs:
        text = pytesseract.image_to_string(binary, config=config)
        curps = re.findall(r'[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d', text)
        print(f"Config {config}: Found {curps}")
        if curps:
            print(f"   Full Text snippet: {text[:100]}...")

    print("\n--- ROI Extraction Strategy ---")
    # Get verbose data to find coordinates
    d = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT)
    
    roi_coords = find_curp_region(img, d)
    if roi_coords:
        x, y, w, h = roi_coords
        print(f"Found CURP label at. Cropping ROI: {x},{y} {w}x{h}")
        
        # Ensure within bounds
        h_img, w_img = binary.shape
        x = max(0, x)
        y = max(0, y)
        w = min(w, w_img - x)
        h = min(h, h_img - y)
        
        roi = binary[y:y+h, x:x+w]
        
        # Save ROI for inspection
        cv2.imwrite('debug_roi.jpg', roi)
        
        # OCR on ROI with PSM 7 (Single line)
        roi_config = '--oem 3 --psm 7 -l spa'
        roi_text = pytesseract.image_to_string(roi, config=roi_config).strip()
        print(f"ROI OCR Text: '{roi_text}'")
        
        # Clean up common OCR errors in CURP
        cleaned = roi_text.replace(' ', '').upper()
        print(f"Cleaned ROI: '{cleaned}'")
        
    else:
        print("Could not find 'CURP' label to anchor ROI.")

if __name__ == "__main__":
    test_ocr("test_ine.jpg")
