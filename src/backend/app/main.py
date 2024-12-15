import os
import uuid
import shutil
import time
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from routes.image import router as image_router
from routes.audio_routes import router as audio_router

# Database ORM setup
Base = declarative_base()

class AlbumImage(Base):
    __tablename__ = 'album_images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)

class MusicAudio(Base):
    __tablename__ = 'music_audios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)

# Directory paths
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, 'album_images')
AUDIO_DIR = os.path.join(BASE_DIR, 'music_audios')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Database setup
DATABASE_URL = os.path.join(BASE_DIR, 'database.db')
engine = create_engine(f'sqlite:///{DATABASE_URL}', echo=True)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI app setup
app = FastAPI(title="Music Album API")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/album_images", StaticFiles(directory=UPLOAD_DIR), name="album_images")
app.mount("/music_audios", StaticFiles(directory=AUDIO_DIR), name="music_audios")
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")

# Include image routes for retrieval functionality
app.include_router(image_router, prefix="/api")
app.include_router(audio_router, prefix="/api")

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        new_image = AlbumImage(name=unique_filename, path=file_path)
        db.add(new_image)
        db.commit()
        db.refresh(new_image)

        return {"message": "Image uploaded successfully", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(AUDIO_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        new_audio = MusicAudio(name=unique_filename, path=file_path)
        db.add(new_audio)
        db.commit()
        db.refresh(new_audio)

        return {"message": "Audio uploaded successfully", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading audio: {str(e)}")

@app.post("/submit-all")
async def submit_all(
    images: list[UploadFile] = File(default=[]),
    audios: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    responses = []
    
    try:
        # Process images
        if images:
            for image in images:
                if not image.content_type.startswith('image/'):
                    raise HTTPException(400, detail=f"File {image.filename} must be an image")
                
                unique_filename = f"{uuid.uuid4()}_{image.filename}"
                file_path = os.path.join(UPLOAD_DIR, unique_filename)
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                new_image = AlbumImage(name=unique_filename, path=file_path)
                db.add(new_image)
                responses.append({
                    "file": unique_filename,
                    "type": "image",
                    "path": file_path
                })

        # Process audios
        if audios:
            for audio in audios:
                if not audio.content_type.startswith('audio/'):
                    raise HTTPException(400, detail=f"File {audio.filename} must be an audio file")
                
                unique_filename = f"{uuid.uuid4()}_{audio.filename}"
                file_path = os.path.join(AUDIO_DIR, unique_filename)
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(audio.file, buffer)
                
                new_audio = MusicAudio(name=unique_filename, path=file_path)
                db.add(new_audio)
                responses.append({
                    "file": unique_filename,
                    "type": "audio",
                    "path": file_path
                })

        # Commit all changes to database
        db.commit()
        
        return {
            "message": "All files submitted successfully",
            "files": responses
        }
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve all albums
@app.get("/albums")
async def get_albums(db: Session = Depends(get_db)):
    albums = db.query(AlbumImage).all()
    return [{"id": album.id, "name": album.name, "path": album.path} for album in albums]

# Retrieve all audios
@app.get("/audios")
async def get_audios(db: Session = Depends(get_db)):
    audios = db.query(MusicAudio).all()
    return [{"id": audio.id, "name": audio.name, "path": audio.path} for audio in audios]

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Music Album API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)