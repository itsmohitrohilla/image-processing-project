""" 

:Description: This script generates a CSV file with the following columns:
:Columns: Serial Number, Product Name, Input Image Urls
:Data: The script generates 50 products and assigns 3 images to each product. The image URLs are assumed to be named as Input_image_n.jpg.
:Output: The generated CSV file is saved to the 'csv/input_csv' directory with the name 'input.csv'.
:Usage: Run the script to generate the CSV file.
:Note: This script assumes that the images have been downloaded using the 'download_images.py' script.
:Note: The 'download_images.py' script is not included in this snippet. You can find the complete script in the 'download_images.py' file in the 'scripts' directory.
:Note: The 'download_images.py' script downloads images from Unsplash using the Unsplash API. You need to provide your Unsplash access key in the script to download images.
:Note: The 'download_images.py' script downloads images to the 'csv/original_images' directory.
:Note: The 'download_images.py' script downloads a total of 100 images. The 'create_input_csv.py' script assigns 3 images to each of the 50 products.

"""


import os
import pandas as pd

image_folder = 'csv/original_images'

num_images = 100 #number of images you want to use in the csv
num_products = 50 #NUMBER OF ROWS

image_urls = [f"{image_folder}/Input_image_{i}.jpg" for i in range(1, num_images + 1)]
data = []

# Generate product data
for i in range(1, num_products + 1):
    product_name = f"SKU{i}"
    start_index = (i - 1) * 2
    assigned_image_urls = ", ".join(image_urls[start_index:start_index + 3])
    data.append([i, product_name, assigned_image_urls])

# Create DataFrame
df = pd.DataFrame(data, columns=["Serial Number", "Product Name", "Input Image Urls"])

# Save DataFrame to CSV
csv_file_path = 'csv/input_csv/input.csv'
df.to_csv(csv_file_path, index=False)

print(f"CSV file '{csv_file_path}' generated successfully.")
