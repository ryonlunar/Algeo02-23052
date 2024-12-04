import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from shutil import copyfile
import shutil

# Define the base for the SQLAlchemy model
Base = declarative_base()

# Define the AlbumImage model
class AlbumImage(Base):
    __tablename__ = 'album_images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)

# Connect to the SQLite database (or create it if it doesn't exist)
DATABASE_URL = 'sqlite:///album_images.db'
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)

# Create a session
SessionLocal = sessionmaker(bind=engine)

# Create FastAPI app
app = FastAPI()

# Path to the directory containing the images
UPLOAD_DIR = 'album_images'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static directory for serving images
app.mount("/album_images", StaticFiles(directory=UPLOAD_DIR), name="album_images")

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def populate_database():
    db = SessionLocal()
    try:
        # Check if the database already has data to prevent duplicate entries
        existing_images = db.query(AlbumImage).all()
        if not existing_images:
            # Populate the database with images from the existing folder
            for image_file in os.listdir(UPLOAD_DIR):
                if image_file.endswith(('.jpg', '.jpeg', '.png')):  # Filter only image files
                    image_path = os.path.join(UPLOAD_DIR, image_file)
                    new_image = AlbumImage(name=image_file, path=image_path)
                    db.add(new_image)
            db.commit()
            print("Database populated with existing images.")
        else:
            print("Database already has data.")
    finally:
        db.close()

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Generate the file path to store the uploaded image
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file to the disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save the path to the database
    new_image = AlbumImage(name=file.filename, path=file_path)
    db.add(new_image)
    db.commit()
    
     # Debug log to confirm commit
    print(f"Image '{file.filename}' uploaded and committed to the database.")
    print("Number of images in the database:", db.query(AlbumImage).count())

    return {"message": "Image uploaded successfully", "file_path": file_path}

@app.get("/albums")
async def get_albums(db: Session = Depends(get_db)):
    albums = db.query(AlbumImage).all()
    return [{"id": album.id, "name": album.name, "path": album.path} for album in albums]