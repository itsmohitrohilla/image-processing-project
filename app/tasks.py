import os
import csv
import requests
from PIL import Image
from io import BytesIO
from celery import Celery
from celeryconfig import settings
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Task as TaskModel

celery = Celery(
    "SDE-1-ASSIGNMENT-BACKEND-JULY24",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@celery.task(bind=True, name='Process CSV')
def process_csv(self, file_path, task_uuid):
    # Create a new session for database operations
    db: Session = next(get_db())
    try:
        # Retrieve the task from the database using the UUID
        task = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).first()

        if not task:
            raise ValueError(f"Task with UUID {task_uuid} not found")

        # Update task status to 'In Progress'
        task.status = 'In Progress'
        db.commit()

        # Define directories for original and compressed images
        original_dir = 'csv/original_images'
        compressed_dir = 'csv/compressed_images'
        output_csv_path = 'csv/output.csv'
        os.makedirs(original_dir, exist_ok=True)
        os.makedirs(compressed_dir, exist_ok=True)

        # Track download progress
        total_rows = 0
        downloaded_images = 0
        output_rows = []

        try:
            # Open and read the CSV file
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Skip header row if there is one
                headers.append('Output Images URLS')
                total_rows = sum(1 for row in reader)  # Count total rows for progress tracking

                file.seek(0)  # Reset file pointer to start
                next(reader)  # Skip header row again

                for row_index, row in enumerate(reader):
                    output_urls = []
                    # Assuming URLs are in the 3rd column and comma-separated
                    urls = row[2].split(',')  # Split the comma-separated URLs
                    for col_index, url in enumerate(urls):
                        url = url.strip()
                        if url:
                            try:
                                response = requests.get(url)
                                response.raise_for_status()  # Raise an error for bad responses

                                # Determine file names and paths
                                original_image_name = f'Image{row_index + 1}.{col_index + 1}.jpg'
                                original_file_path = os.path.join(original_dir, original_image_name)
                                compressed_image_name = f'compressed_Image{row_index + 1}.{col_index + 1}.jpg'
                                compressed_file_path = os.path.join(compressed_dir, compressed_image_name)

                                # Save the original image
                                with open(original_file_path, 'wb') as img_file:
                                    img_file.write(response.content)

                                # Compress the image and save it
                                image = Image.open(BytesIO(response.content))
                                # Compress by saving at a reduced quality
                                image.save(compressed_file_path, 'JPEG', quality=50)
                                
                                output_urls.append(compressed_file_path)
                                downloaded_images += 1
                            except requests.RequestException as e:
                                self.retry(exc=e)
                            except Exception as e:
                                self.retry(exc=e)

                    row.append(','.join(output_urls))
                    output_rows.append(row)
                    self.update_state(state='PROGRESS', meta={'current': row_index + 1, 'total': total_rows})

        except Exception as e:
            # Handle exceptions during file processing
            raise self.retry(exc=e)

        # Write the new CSV file with the added column for output image URLs
        with open(output_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(output_rows)
            
        
        # Update the task's output_csv_path
        task.output_csv_path = output_csv_path
            

        # Update task status to 'Completed'
        task.status = 'Completed'
        db.commit()

    except Exception as e:
        # If an error occurs, update task status to 'Failed'
        if task is not None:
            task.status = 'Failed'
            db.commit()

    finally:
        # Close the database session
        db.close()

    return {'status': 'Output CSV genertated Success fully Completed'}




#celery -A app.tasks worker --loglevel=info
#uvicorn app.main:app --reload