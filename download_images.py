import os
import requests
from io import BytesIO
from PIL import Image
import time

UNSPLASH_ACCESS_KEY = 'DmZt9QqGCyENPsalI-W32pPtr2-gUtup5lJk6k43i0Q'

def download_and_save_image(image_url, save_path):
    
    """Download an image from a given URL and save it to the specified path."""
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img.save(save_path)

def fetch_and_download_images(total_images):
    """Fetch and download a total number of images from Unsplash."""
    base_url = "https://api.unsplash.com/photos/random"
    params = {
        "client_id": UNSPLASH_ACCESS_KEY,
        "count": 20, 
        "orientation": "squarish",
    }

    # Ensure the target directory exists
    os.makedirs("csv/original_images", exist_ok=True)

    downloaded_images_count = 0
    while downloaded_images_count < total_images:
        response = requests.get(base_url, params=params)
        images_data = response.json()

        for i, image_data in enumerate(images_data, start=downloaded_images_count + 1):
            if i > total_images:
                break  # Stop downloading once we reach the desired number of images
            
            image_url = image_data['urls']['full']
            save_path = os.path.join("csv/original_images", f"Input_image_{i}.jpg")
            download_and_save_image(image_url, save_path)
            
            time.sleep(2) 
        
        downloaded_images_count += len(images_data)
        print(f"Downloaded {downloaded_images_count} out of {total_images}")

if __name__ == "__main__":
    fetch_and_download_images(100) 
