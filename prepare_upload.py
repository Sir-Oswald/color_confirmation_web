import os
from PIL import Image
import io

def convert_and_compress_image(image_path, quality=85):
    with Image.open(image_path) as img:
        # Convert to RGB mode if it's not already (in case of PNGs with transparency)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else img.split()[1])  # 3 is the alpha channel
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG', quality=quality, optimize=True)
    return img_buffer.getvalue()

def prepare_patterns_for_web_app(source_folder, destination_folder, max_size_mb=512):
    max_size_bytes = max_size_mb * 1024 * 1024
    current_size = 0

    for root, dirs, files in os.walk(source_folder):
        pattern_name = os.path.basename(root)
        png_files = [f for f in files if f.lower().endswith('.png') and 'Etsy Tile Image Asset' not in f]
        
        if png_files:
            main_png = png_files[0]  # Take the first PNG file in the folder
            file_path = os.path.join(root, main_png)
            compressed_data = convert_and_compress_image(file_path)
            
            # Check if adding this file would exceed the size limit
            if current_size + len(compressed_data) > max_size_bytes:
                print(f"Reached size limit. Stopping at {pattern_name}")
                return
            
            # Save compressed file to destination directory as JPG
            jpg_filename = os.path.splitext(main_png)[0] + '.jpg'
            dest_file_path = os.path.join(destination_folder, pattern_name, jpg_filename)
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
            with open(dest_file_path, 'wb') as f:
                f.write(compressed_data)
            
            current_size += len(compressed_data)
            print(f"Processed: {dest_file_path}")
            print(f"Size: {len(compressed_data) / 1024:.2f} KB")

    print(f"Compressed patterns saved to {destination_folder}")
    print(f"Total size: {current_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    source_folder = r"C:\Users\davii\Photoshop Action Creation\Finished Assets - Tile"
    destination_folder = r"C:\GitHub\color_confirmation_web\data\patterns"
    prepare_patterns_for_web_app(source_folder, destination_folder)