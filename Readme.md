
# README for Image Processing Service

---

### Project Overview

**Project Name**: SDE-1-ASSIGNMENT-BACKEND-JULY24  
**Hosted on AWS EC2**: [Swagger UI](http://13.233.153.137:8000/docs)  
**Repository**: [GitHub Repository](https://github.com/itsmohitrohilla/image-processing.git)

**Description**:  
This project provides a backend service for processing and managing CSV files containing image URLs. The service downloads the images, compresses them, and uploads them to an AWS S3 bucket. The project uses FastAPI for the web framework, Celery for background tasks, Redis as a message broker, and Supabase for database management.

### Features

1. **Download Input CSV**: Download a sample input CSV file for testing.
2. **Upload CSV**: Upload a CSV file with image URLs for processing.
3. **Check Status**: Check the processing status of your uploaded CSV using a unique task ID.
4. **Download Output CSV**: Download the processed CSV file with URLs to the compressed images.

### Getting Started

#### Prerequisites

- Python 3.8+
- FastAPI
- Celery
- Redis
- AWS S3
- Supabase

#### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/itsmohitrohilla/image-processing.git
   cd image-processing
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Run Celery worker**:
   ```bash
   celery -A app.tasks worker --loglevel=info
   ```

### API Endpoints

1. **GET /download-input-csv**: Download a sample input CSV.
2. **POST /upload-csv**: Upload a CSV file for processing. The file should be structured with columns `Serial Number`, `Product Name`, and `Input Image URLs`.
3. **GET /check-status/{task_id}**: Check the status of a processing task using the task ID.
4. **GET /download-output-csv/{task_uuid}**: Download the processed CSV file using the task UUID.

### Project Structure

- `app/`: Contains the FastAPI application
  - `main.py`: The main application file where the FastAPI app is created.
  - `tasks.py`: Contains Celery tasks for processing images.
  - `models.py`: Defines the database models using SQLAlchemy.
  - `schemas.py`: Defines Pydantic models for request and response schemas.
  - `utils.py`: Utility functions for image processing and S3 interactions.
- `requirements.txt`: List of dependencies.
- `Dockerfile`: Docker configuration for containerizing the application.
- `docker-compose.yml`: Configuration for setting up the application with Docker Compose.

### Database Schema

- **Task**: Stores information about each processing task.
  - `id`: Primary key.
  - `uuid`: Unique identifier for the task.
  - `status`: Status of the task (e.g., pending, processing, completed).
  - `output_csv_path`: Path to the output CSV file.

### How It Works

1. **Upload CSV**: User uploads a CSV file containing image URLs.
2. **Processing**: Celery worker downloads images, compresses them by 50%, and uploads them to S3.
3. **Status Check**: User can check the status of the processing task.
4. **Download Output**: User can download the processed CSV file containing URLs to the compressed images.

### Example Input and Output

**Input CSV Format**:
```csv
Serial Number, Product Name, Input Image Urls
1, SKU1, https://example.com/image1.jpg,https://example.com/image2.jpg,https://example.com/image3.jpg
2, SKU2, https://example.com/image4.jpg,https://example.com/image5.jpg,https://example.com/image6.jpg
```

**Output CSV Format**:
```csv
Serial Number, Product Name, Input Image Urls, Output Image Urls
1, SKU1, https://example.com/image1.jpg,https://example.com/image2.jpg,https://example.com/image3.jpg,https://s3.amazonaws.com/your-bucket/compressed_image1.1.jpg,https://s3.amazonaws.com/your-bucket/compressed_image1.2.jpg,https://s3.amazonaws.com/your-bucket/compressed_image1.3.jpg
2, SKU2, https://example.com/image4.jpg,https://example.com/image5.jpg,https://example.com/image6.jpg,https://s3.amazonaws.com/your-bucket/compressed_image2.1.jpg,https://s3.amazonaws.com/your-bucket/compressed_image2.2.jpg,https://s3.amazonaws.com/your-bucket/compressed_image2.3.jpg
```

### Detailed Explanation of Each File

1. **app/main.py**: The entry point for the FastAPI application. It includes the route definitions for all the API endpoints.
2. **app/tasks.py**: Contains Celery tasks that handle the background processing of images.
3. **app/models.py**: Defines the SQLAlchemy models for the database.
4. **app/schemas.py**: Defines Pydantic models used for data validation and serialization.
5. **app/utils.py**: Contains utility functions for handling image download, compression, and S3 interactions.
6. **Dockerfile**: Configuration file for Docker to build the application image.
7. **docker-compose.yml**: Configuration for Docker Compose to run the application with its dependencies.

### Database Model

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    status = Column(String, index=True)
    output_csv_path = Column(String)
```

### if you want to create test input data so run -> python3 create_test_data.py 
    it will take like 5 minute to create teh text input file as per teh requirment of the tasks

### If you wanna run this code so clone the repository and update redis s3 and database credintials and the run -> ./setup.sh one time and then every time you want to use the code then  use  - > ./run.sh

