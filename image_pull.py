import os
import re
import cv2
import numpy as np
from PIL import Image
from rembg import remove
import config

def process_raw_folder(input_folder=config.raw_photos, output_folder=config.edited_photos, bridge_gap=15):
    # Loops through the raw folder, extracts individual flower objects, 
    # discards elements cut off by the borders, and preserves original file names.
    
    os.makedirs(output_folder, exist_ok=True)
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.heic')
    
    def natural_keys(text):
        return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]
        
    raw_files = [f for f in os.listdir(input_folder) if f.lower().endswith(valid_extensions)]
    raw_files.sort(key=natural_keys)
    
    if not raw_files:
        print(f"[image_pull] No images found in '{input_folder}/'. Please add some photos!")
        return 0

    print(f"[image_pull] Found {len(raw_files)} photos to process.")
    saved_assets_count = 0

    for file_name in raw_files:
        input_path = os.path.join(input_folder, file_name)
        print(f" Processing image: {file_name}")
        
        # Get the exact filename without the extension (e.g., "flowers21" from "flowers21.jpeg")
        base_name = os.path.splitext(file_name)[0]
        
        input_img = Image.open(input_path)
        rgba_img = remove(input_img).convert("RGBA")
        
        cv_img = cv2.cvtColor(np.array(rgba_img), cv2.COLOR_RGBA2BGRA)
        img_h, img_w = cv_img.shape[:2]
        
        alpha_channel = cv_img[:, :, 3]
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (bridge_gap, bridge_gap))
        grouped_mask = cv2.morphologyEx(alpha_channel, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(grouped_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        contour_idx = 1
        for contour in contours:
            if cv2.contourArea(contour) < 2000: 
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            
            buffer_pixels = 2
            if x <= buffer_pixels or y <= buffer_pixels or (x + w) >= (img_w - buffer_pixels) or (y + h) >= (img_h - buffer_pixels):
                continue
            
            cropped_flower = rgba_img.crop((x, y, x + w, y + h))
            
            # Use original base name. Append suffix only if photo splits into multiple valid shapes
            if len(contours) > 1 and contour_idx > 1:
                output_name = f"{base_name}_{contour_idx}.png"
            else:
                output_name = f"{base_name}.png"
                
            output_path = os.path.join(output_folder, output_name)
            cropped_flower.save(output_path, "PNG")
            
            contour_idx += 1
            saved_assets_count += 1
            
    print(f"[image_pull] Extraction Complete. Generated {saved_assets_count} clear flower assets in '{output_folder}/'")
    
    return output_folder
