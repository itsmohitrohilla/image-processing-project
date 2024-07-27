import csv
import requests
from PIL import Image
from io import BytesIO
from celery import Celery
from celeryconfig import settings
from sqlalchemy.orm import Session
import boto3
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

# AWS S3 configuration
S3_ENDPOINT_URL = "https://adfwsgumljhsejglhnxn.supabase.co/storage/v1/s3"
S3_REGION = "ap-south-1"
S3_ACCESS_KEY = "2d5ac726150ae5b64793989ae292a149"
S3_SECRET_KEY = "a786a549eb97c9092bcc58f39b7d4be6d96df768855e2ec527de15fab38b2b35"

# Initialize S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT_URL,
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

BUCKET_NAME = "test-bucket"

def upload_to_s3(file_content, s3_path):
    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_path, Body=file_content)
        return f"{S3_ENDPOINT_URL}/{BUCKET_NAME}/{s3_path}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise

@celery.task(bind=True, name='Process CSV')
def process_csv(self, file_path, task_uuid):
    db: Session = next(get_db())
    try:
        task = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).first()

        if not task:
            raise ValueError(f"Task with UUID {task_uuid} not found")

        task.status = 'In Progress'
        db.commit()

        # Define S3 folders and output CSV name
        input_folder = 'input/'
        output_folder = 'output/'
        output_csv_name = f'output_{task_uuid}.csv'

        # Track download progress
        total_rows = 0
        output_rows = []

        try:
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Skip header row if there is one
                headers.append('Output Images URLS')
                total_rows = sum(1 for row in reader)  # Count total rows for progress tracking

                file.seek(0)  # Reset file pointer to start
                next(reader)  # Skip header row again

                for row_index, row in enumerate(reader):
                    output_urls = []
                    urls = row[2].split(',')  # Assuming URLs are in the 3rd column and comma-separated
                    for col_index, url in enumerate(urls):
                        url = url.strip()
                        if url:
                            try:
                                response = requests.get(url)
                                response.raise_for_status()  # Raise an error for bad responses

                                # Upload the original image to S3
                                original_image_name = f'Image{row_index + 1}.{col_index + 1}.jpg'
                                original_url = upload_to_s3(BytesIO(response.content), f'{input_folder}{original_image_name}')

                                # Compress the image
                                image = Image.open(BytesIO(response.content))
                                compressed_image_name = f'compressed_Image{row_index + 1}.{col_index + 1}.jpg'
                                compressed_io = BytesIO()
                                image.save(compressed_io, 'JPEG', quality=50)
                                compressed_io.seek(0)

                                # Upload the compressed image to S3
                                compressed_url = upload_to_s3(compressed_io, f'{output_folder}{compressed_image_name}')

                                output_urls.append(compressed_url)
                            except requests.RequestException as e:
                                self.retry(exc=e)
                            except Exception as e:
                                self.retry(exc=e)

                    row.append(','.join(output_urls))
                    output_rows.append(row)
                    self.update_state(state='PROGRESS', meta={'current': row_index + 1, 'total': total_rows})

        except Exception as e:
            raise self.retry(exc=e)

        # Write the new CSV file with the added column for output image URLs
        output_csv_path = f'/tmp/{output_csv_name}'  # Temporary path for local file creation
        with open(output_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(output_rows)

        # Upload the output CSV file to S3
        with open(output_csv_path, 'rb') as file:
            output_csv_url = upload_to_s3(file, f'{output_folder}{output_csv_name}')

        # Update the task's output_csv_path
        task.output_csv_path = f"https://adfwsgumljhsejglhnxn.supabase.co/storage/v1/object/public/{BUCKET_NAME}/{output_folder}{output_csv_name}"

        # Update task status to 'Completed'
        task.status = 'Completed'
        db.commit()

    except Exception as e:
        if task is not None:
            task.status = 'Failed'
            db.commit()

    finally:
        db.close()

    return {'status': 'Output CSV generated and uploaded successfully'}



#https://adfwsgumljhsejglhnxn.supabase.co/storage/v1/object/public/test-bucket/output/output_7148ca83-69c3-4ce8-afc3-49b3cc6415a5.csv