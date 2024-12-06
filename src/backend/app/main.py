import os
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import shutil
from fastapi.middleware.cors import CORSMiddleware

# Define the base for SQLAlchemy models
Base = declarative_base()

# Define the AlbumImage model
class AlbumImage(Base):
    __tablename__ = 'album_images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)

# Get the current directory (where main.py is located)
BASE_DIR = os.path.dirname(__file__)

# Set the relative path to store uploaded images (within app folder)
UPLOAD_DIR = os.path.join(BASE_DIR, 'album_images')  # Path relatif untuk folder gambar
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Setup Database URL and create engine (store DB in the same app folder)
DATABASE_URL = os.path.join(BASE_DIR, 'album_images.db')  # Path relatif untuk database
engine = create_engine(f'sqlite:///{DATABASE_URL}', echo=True)
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI App Setup
app = FastAPI()

# Enable CORS for cross-origin requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with the allowed frontend URLs if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory to serve images
app.mount("/album_images", StaticFiles(directory=UPLOAD_DIR), name="album_images")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create API route to upload images
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save image information in the database
    new_image = AlbumImage(name=file.filename, path=file_path)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return {"message": "Image uploaded successfully", "file_path": file_path}

# API route to fetch all albums (image data)
@app.get("/albums")
async def get_albums(db: Session = Depends(get_db)):
    albums = db.query(AlbumImage).all()
    return [{"id": album.id, "name": album.name, "path": album.path} for album in albums]

# API route for the root (check if the server is running)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Music Album API!"}

# Populate database with existing images (on app startup)
@app.on_event("startup")
async def populate_database():
    db = SessionLocal()
    try:
        # Check if the database is already populated
        existing_images = db.query(AlbumImage).all()
        if not existing_images:
            # If no images in DB, populate from the image folder
            for image_file in os.listdir(UPLOAD_DIR):
                if image_file.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(UPLOAD_DIR, image_file)
                    new_image = AlbumImage(name=image_file, path=image_path)
                    db.add(new_image)
            db.commit()
            print("Database populated with existing images.")
        else:
            print("Database already populated.")
    finally:
        db.close()
