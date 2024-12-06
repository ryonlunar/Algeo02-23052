import os
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import shutil
from fastapi.middleware.cors import CORSMiddleware

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

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, 'album_images')
AUDIO_DIR = os.path.join(BASE_DIR, 'music_audios')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

DATABASE_URL = os.path.join(BASE_DIR, 'album_images.db')
engine = create_engine(f'sqlite:///{DATABASE_URL}', echo=True)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/album_images", StaticFiles(directory=UPLOAD_DIR), name="album_images")
app.mount("/music_audios", StaticFiles(directory=AUDIO_DIR), name="music_audios")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    new_image = AlbumImage(name=file.filename, path=file_path)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    
    return {"message": "Image uploaded successfully", "file_path": file_path}

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(AUDIO_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    new_audio = MusicAudio(name=file.filename, path=file_path)
    db.add(new_audio)
    db.commit()
    db.refresh(new_audio)
    
    return {"message": "Audio uploaded successfully", "file_path": file_path}

@app.get("/albums")
async def get_albums(db: Session = Depends(get_db)):
    albums = db.query(AlbumImage).all()
    return [{"id": album.id, "name": album.name, "path": album.path} for album in albums]

@app.get("/audios")
async def get_audios(db: Session = Depends(get_db)):
    audios = db.query(MusicAudio).all()
    return [{"id": audio.id, "name": audio.name, "path": audio.path} for audio in audios]

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Music Album API!"}

@app.on_event("startup")
async def populate_database():
    db = SessionLocal()
    try:
        # Populate images
        existing_images = db.query(AlbumImage).all()
        if not existing_images:
            for image_file in os.listdir(UPLOAD_DIR):
                if image_file.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(UPLOAD_DIR, image_file)
                    new_image = AlbumImage(name=image_file, path=image_path)
                    db.add(new_image)
        
        # Populate audio files
        existing_audios = db.query(MusicAudio).all()
        if not existing_audios:
            for audio_file in os.listdir(AUDIO_DIR):
                if audio_file.endswith(('.mp3', '.wav')):
                    audio_path = os.path.join(AUDIO_DIR, audio_file)
                    new_audio = MusicAudio(name=audio_file, path=audio_path)
                    db.add(new_audio)
        
        db.commit()
    finally:
        db.close()