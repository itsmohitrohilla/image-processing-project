import uuid
import csv
import re
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
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


@app.get("/download-input-csv", response_class=FileResponse)
def download_csv():
    file_path = os.path.join("csv/", "input.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='application/octet-stream', filename="input.csv")


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


@app.get("/download-output-csv/{task_uuid}", response_class=FileResponse)
def download_csv(task_uuid: str, db: Session = Depends(get_db)):
    # Retrieve the task from the database using the UUID
    task = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Retrieve the output CSV file path from the task
    output_csv_path = task.output_csv_path

    # Check if the file exists
    if not output_csv_path or not os.path.isfile(output_csv_path):
        raise HTTPException(status_code=404, detail="Output CSV file not found")

    # Return the file response
    return FileResponse(path=output_csv_path, filename=os.path.basename(output_csv_path))
