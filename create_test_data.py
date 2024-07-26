import os
import requests
import csv
import time
import pandas as pd
import re

UNSPLASH_ACCESS_KEY = 'DmZt9QqGCyENPsalI-W32pPtr2-gUtup5lJk6k43i0Q'

def fetch_image_urls(total_images):
    """Fetch image URLs from Unsplash."""
    base_url = "https://api.unsplash.com/photos/random"
    params = {
        "client_id": UNSPLASH_ACCESS_KEY,
        "count": 20, 
        "orientation": "squarish",
    }

    image_urls = []
    downloaded_images_count = 0

    while downloaded_images_count < total_images:
        response = requests.get(base_url, params=params)
        images_data = response.json()

        for image_data in images_data:
            if downloaded_images_count >= total_images:
                break  # Stop fetching once we reach the desired number of images

            image_url = image_data['urls']['full']
            image_urls.append(image_url)
            downloaded_images_count += 1

            time.sleep(2) 

        print(f"Fetched {downloaded_images_count} out of {total_images} image URLs")

    return image_urls

def generate_product_data(num_products, image_urls):
    """Generate product data with 3 image URLs per product."""
    data = []

    for i in range(1, num_products + 1):
        product_name = f"SKU{i}"
        start_index = (i - 1) * 3
        assigned_image_urls = ", ".join(image_urls[start_index:start_index + 3])
        data.append([i, product_name, assigned_image_urls])

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Serial Number", "Product Name", "Input Image Urls"])
    return df

if __name__ == "__main__":
    num_products = 10  # Adjust this to the number of products you want
    total_images = num_products * 3

    image_urls = fetch_image_urls(total_images)
    product_data_df = generate_product_data(num_products, image_urls)

    # Save to CSV
    os.makedirs("csv", exist_ok=True)
    csv_file_path = os.path.join("csv", "product_data.csv")
    product_data_df.to_csv(csv_file_path, index=False)

    print(f"Product data saved to {csv_file_path}")
