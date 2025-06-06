from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
import traceback
from datetime import datetime

from config import UPLOAD_DIR
from rag_agent import classify_file_with_llm

from database import SessionLocal, engine, Base
from models import UploadedFile

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/upload", StaticFiles(directory=UPLOAD_DIR), name="upload")


# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/classify/")
async def classify_file_endpoint(
    file: UploadFile = File(...),
    uploaded_by: str = Form(...),
    db: Session = Depends(get_db),
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to save file", "details": str(e)},
        )

    try:
        result = classify_file_with_llm(file_path, uploaded_by)
        lines = result.splitlines()
        category = lines[0].split(":", 1)[1].strip()
        tag = lines[1].split(":", 1)[1].strip()
        date_uploaded_str = lines[3].split(":", 1)[1].strip()
        date_uploaded = datetime.strptime(date_uploaded_str, "%d-%b-%Y")
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "Classification failed", "details": str(e)},
        )

    existing = db.query(UploadedFile).filter(UploadedFile.filename == file.filename).first()
    if existing:
        existing.category = category
        existing.tag = tag
        existing.uploaded_by = uploaded_by
        existing.date_uploaded = date_uploaded
    else:
        new_file = UploadedFile(
            filename=file.filename,
            category=category,
            tag=tag,
            uploaded_by=uploaded_by,
            date_uploaded=date_uploaded,
        )
        db.add(new_file)

    db.commit()

    return JSONResponse({
        "category": category,
        "tag": tag,
        "uploaded_by": uploaded_by,
        "date_uploaded": date_uploaded_str,
    })


@app.get("/list-files")
async def list_files(db: Session = Depends(get_db)):
    try:
        files = []
        db_files = db.query(UploadedFile).order_by(UploadedFile.date_uploaded.desc()).all()
        for f in db_files:
            files.append({
                "name": f.filename,
                "path": f"/upload/{f.filename}",
                "category": f.category,
                "tag": f.tag,
                "uploaded_by": f.uploaded_by,
                "uploaded_at": f.date_uploaded.strftime("%Y-%m-%d %H:%M:%S")
            })
        return JSONResponse(content={"files": files})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to list files", "details": str(e)},
        )


@app.put("/update-file/{filename}")
async def update_file(
    filename: str,
    category: str = Form(None),
    tag: str = Form(None),
    db: Session = Depends(get_db),
):
    file = db.query(UploadedFile).filter(UploadedFile.filename == filename).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if category is not None:
        file.category = category
    if tag is not None:
        file.tag = tag
    db.commit()
    return {"message": "File updated"}
