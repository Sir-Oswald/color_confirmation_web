import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"

def test_index():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, "Index page failed to load"
    print("Index page test passed")

def test_confirm_colors():
    response = requests.get(f"{BASE_URL}/confirm_colors")
    assert response.status_code == 200, "Confirm colors page failed to load"
    print("Confirm colors page test passed")

def test_get_pattern_folders():
    response = requests.get(f"{BASE_URL}/get_pattern_folders")
    assert response.status_code == 200, "Failed to get pattern folders"
    data = response.json()
    assert "pattern_folders" in data, "Pattern folders data not found in response"
    print("Get pattern folders test passed")
    return data["pattern_folders"]

def test_get_images(folder):
    response = requests.get(f"{BASE_URL}/get_images", params={"folder": folder})
    assert response.status_code == 200, f"Failed to get images for folder {folder}"
    data = response.json()
    assert "images" in data, "Images data not found in response"
    print(f"Get images test passed for folder {folder}")
    return data["images"]

def test_pattern_image(folder, image):
    response = requests.get(f"{BASE_URL}/pattern_image/{folder}/{image}")
    assert response.status_code == 200, f"Failed to get image {image} from folder {folder}"
    print(f"Pattern image test passed for {folder}/{image}")

def test_get_image_colors(folder, image):
    data = {
        "pattern_folder": folder,
        "image_name": image
    }
    response = requests.post(f"{BASE_URL}/get_image_colors", json=data)
    assert response.status_code == 200, f"Failed to get colors for image {image} from folder {folder}"
    colors = response.json()
    assert "colors" in colors, "Colors data not found in response"
    assert len(colors["colors"]) == 2, "Expected 2 colors in response"
    print(f"Get image colors test passed for {folder}/{image}")
    return colors["colors"]

def test_save_colors(folder, image, colors):
    data = {
        "pattern_folder": folder,
        "file_name": image,
        "colors": colors
    }
    response = requests.post(f"{BASE_URL}/save_colors", json=data)
    if response.status_code != 200:
        print(f"Error response content: {response.text}")
        print(f"Request data: {data}")
    assert response.status_code == 200, f"Failed to save colors for image {image} from folder {folder}. Status code: {response.status_code}"
    print(f"Save colors test passed for {folder}/{image}")

def test_download_results():
    response = requests.get(f"{BASE_URL}/download_results")
    assert response.status_code == 200, "Failed to download results"
    assert response.headers["Content-Type"] == "application/json", "Expected JSON content type for results"
    print("Download results test passed")

def test_delete_results():
    response = requests.post(f"{BASE_URL}/delete_results")
    assert response.status_code == 200, "Failed to delete results"
    print("Delete results test passed")

def run_all_tests():
    test_index()
    test_confirm_colors()
    
    pattern_folders = test_get_pattern_folders()
    
    for folder in pattern_folders:
        images = test_get_images(folder)
        
        for image in images:
            test_pattern_image(folder, image)
            colors = test_get_image_colors(folder, image)
            test_save_colors(folder, image, colors)
    
    test_download_results()
    test_delete_results()

if __name__ == "__main__":
    run_all_tests()
    print("All tests completed successfully!")