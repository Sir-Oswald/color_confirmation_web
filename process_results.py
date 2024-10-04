import os
import json

def process_results(json_file_path, target_folder):
    with open(json_file_path, 'r') as f:
        results = json.load(f)
    
    for pattern_folder, data in results.items():
        target_pattern_folder = os.path.join(target_folder, pattern_folder)
        os.makedirs(target_pattern_folder, exist_ok=True)
        
        target_file_path = os.path.join(target_pattern_folder, f"{pattern_folder}_data.json")
        with open(target_file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    print(f"Results processed and saved to {target_folder}")

if __name__ == '__main__':
    json_file_path = 'color_confirmation_results.json'
    target_folder = r'C:\Users\davii\Photoshop Action Creation\Finished Assets - Tile'
    process_results(json_file_path, target_folder)