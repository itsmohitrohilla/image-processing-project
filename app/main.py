import uuid
import csv
import re
import httpx
import io
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.tasks import process_csv
from app.database import engine, get_db
from app.models import Base, Task as TaskModel
from app.schemas import Task as TaskSchema, TaskCreate
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os



app = FastAPI(
    title="SDE-1-ASSIGNMENT-BACKEND-JULY24",
    description="A backend service for processing and managing CSV files.",
    version="1.0.0",
    contact={
        "name": "Mohit Rohilla",
        "url": "https://www.linkedin.com/in/itsmohitrohilla/",
    }
)

Base.metadata.create_all(bind=engine)

# Your Supabase API Key
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkZndzZ3VtbGpoc2VqZ2xobnhuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjIwMTkxNTUsImV4cCI6MjAzNzU5NTE1NX0.d3X7KrqmPTfUDcizREKxte43GUkqazMJcLCgPsz00H8"

@app.get("/download-input-csv", response_class=StreamingResponse)
async def download_csv():
    url = "https://adfwsgumljhsejglhnxn.supabase.co/storage/v1/object/public/image-processing/input.csv?t=2024-07-27T07%3A09%3A18.151Z"
    #url = "https://adfwsgumljhsejglhnxn.supabase.co/storage/v1/object/public/test-bucket/output/output_c420cf64-6599-4329-864e-9982da6e5df4.csv"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="File not found or could not be downloaded")
        
        # Create a file-like object from the response content
        file_like_object = io.BytesIO(response.content)
        
        # Return the file as StreamingResponse with Content-Disposition header for filename
        return StreamingResponse(
            file_like_object, 
            media_type='application/octet-stream',
            headers={"Content-Disposition": "attachment; filename=input.csv"}
        )



@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
    
    # Save the uploaded file
    file_location = f"csv/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    # Generate a UUID for the task
    task_uuid = str(uuid.uuid4()) 
    
    # Create a new task in the database
    task = TaskModel(uuid=task_uuid, status='Pending')
    db.add(task)
    db.commit()
    db.refresh(task)
    
    process_csv.apply_async(args=[file_location, task_uuid])
    
    return JSONResponse(content={"task_id": task_uuid})

@app.get("/check-status/{task_id}", response_model=TaskSchema)
async def check_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.uuid == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/download-output-csv/{task_uuid}", response_class=StreamingResponse)
async def download_csv(task_uuid: str, db: Session = Depends(get_db)):
    # Retrieve the task from the database using the UUID
    task = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Retrieve the output CSV file URL from the task
    output_csv_url = task.output_csv_path
    print(output_csv_url)

    async with httpx.AsyncClient() as client:
        response = await client.get(output_csv_url)
        print(response)
        
        if response.status_code != 200:
             raise HTTPException(status_code=response.status_code, detail="File found, but can not be downloaded. it is saved at the location.")
        
        # Create a file-like object from the response content
        file_like_object = io.BytesIO(response.content)
        
        # Return the file as StreamingResponse with Content-Disposition header for filename
        return StreamingResponse(
            file_like_object, 
            media_type='application/octet-stream',
            headers={"Content-Disposition": "attachment; filename=output.csv"}
        )   




#https://adfwsgumljhsejglhnxn.supabase.co/storage/v1/object/public/test-bucket/output/output_7148ca83-69c3-4ce8-afc3-49b3cc6415a5.csv?
# t=2024-07-27T08%3A37%3A47.010Z

#https://adfwsgumljhsejglhnxn.supabase.co/storage/v1/s3/test-bucket/output/output_7148ca83-69c3-4ce8-afc3-49b3cc6415a5.csv
