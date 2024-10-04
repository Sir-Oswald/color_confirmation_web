import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

allowed_colors = {
    "Red": (255, 0, 0),
    "Orange": (255, 165, 0),
    "Yellow": (255, 255, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Purple": (128, 0, 128),
    "Pink": (255, 192, 203),
    "Brown": (150, 75, 0),
    "Black": (0, 0, 0),
    "Gray": (128, 128, 128),
    "White": (255, 255, 255),
    "Beige": (245, 245, 220),
    "Gold": (255, 215, 0),
    "Silver": (192, 192, 192),
    "Bronze": (205, 127, 50),
    "Copper": (184, 115, 51),
    "Rose Gold": (183, 110, 121)
}

def find_main_colors(image_path, num_colors=2):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    image = cv2.resize(image, (300, 100))
    pixels = image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=num_colors, n_init='auto')
    kmeans.fit(pixels)
    main_colors = kmeans.cluster_centers_
    main_colors = cv2.cvtColor(np.uint8(main_colors[np.newaxis, :, :]), cv2.COLOR_LAB2RGB)[0]
    return main_colors

def snap_to_allowed_colors(main_colors):
    color_names = list(allowed_colors.keys())
    color_values = np.array(list(allowed_colors.values()))
    closest_indices, _ = pairwise_distances_argmin_min(main_colors, color_values)
    snapped_colors = [color_names[idx] for idx in closest_indices]
    return snapped_colors