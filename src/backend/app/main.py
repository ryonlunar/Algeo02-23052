import os
import uuid
import shutil
import zipfile
import traceback
import re
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from routes.image import router as image_router
from routes.audio_routes import router as audio_router
from routes.mic.microphone import record_audio
from routes.mic.audiomic_router import router as audiomic_router
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'album_images')
AUDIO_DIR = os.path.join(BASE_DIR, 'music_audios')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

print(f"Current working directory: {os.getcwd()}")
print(f"BASE_DIR: {BASE_DIR}")
print(f"UPLOAD_DIR: {UPLOAD_DIR}")
print(f"AUDIO_DIR: {AUDIO_DIR}")

DATABASE_URL = os.path.join(BASE_DIR, 'database.db')
engine = create_engine(f'sqlite:///{DATABASE_URL}', echo=True)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Music Album API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def sanitize_filename(filename: str) -> str:
    base_name = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    sanitized_base = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name.replace(' ', '_'))
    return f"{sanitized_base}{extension}"

def is_valid_audio_file(filename: str) -> bool:
    return filename.lower().endswith(('.mid', '.midi'))

def is_valid_image_file(filename: str) -> bool:
    return filename.lower().endswith(('.jpg', '.jpeg', '.png'))

def validate_mapper_line(line: str) -> tuple[bool, str, str]:
    try:
        if not line.strip():
            return False, "", ""
            
        audio_file, image_file = line.strip().split('\t')
        if is_valid_audio_file(audio_file) and is_valid_image_file(image_file):
            return True, audio_file, image_file
            
        return False, "", ""
    except ValueError:
        return False, "", ""

def sync_folder_to_db(db: Session):
    print("Starting database sync...")
    
    # Clear existing data
    db.query(AlbumImage).delete()
    db.query(MusicAudio).delete()
    
    # Sync images
    for filename in os.listdir(UPLOAD_DIR):
        if not filename.lower().endswith('.zip'):
            file_path = os.path.join(UPLOAD_DIR, filename)
            db_path = f"/album_images/{filename}"
            if os.path.isfile(file_path):
                new_image = AlbumImage(name=filename, path=db_path)
                db.add(new_image)
                print(f"Added new image to DB: {filename}")

    # Sync audio files
    for filename in os.listdir(AUDIO_DIR):
        if filename.lower().endswith(('.mid', '.midi')):
            file_path = os.path.join(AUDIO_DIR, filename)
            db_path = f"/music_audios/{filename}"
            if os.path.isfile(file_path):
                new_audio = MusicAudio(name=filename, path=db_path)
                db.add(new_audio)
                print(f"Added new audio to DB: {filename}")

    try:
        db.commit()
        print("Database sync completed successfully")
    except Exception as e:
        db.rollback()
        print(f"Error syncing database: {str(e)}")
        raise

def process_extracted_file(file_path: str, original_filename: str, db: Session):
    print(f"Processing extracted file: {original_filename}")
    
    if original_filename.lower().endswith('.zip'):
        return None

    file_ext = os.path.splitext(original_filename)[1].lower()
    sanitized_name = sanitize_filename(original_filename)
    
    if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
        destination_dir = UPLOAD_DIR
        destination_path = os.path.join(destination_dir, sanitized_name)
        db_path = f"/album_images/{sanitized_name}"
        model = AlbumImage
        file_type = "image"
    elif file_ext in ['.mid', '.midi']:
        destination_dir = AUDIO_DIR
        destination_path = os.path.join(destination_dir, sanitized_name)
        db_path = f"/music_audios/{sanitized_name}"
        model = MusicAudio
        file_type = "audio"
    else:
        return None

    print(f"Copying file to: {destination_path}")
    try:
        shutil.copy2(file_path, destination_path)
        print(f"File copied successfully")
        
        # Check if entry already exists
        existing = db.query(model).filter_by(name=sanitized_name).first()
        if existing:
            print(f"Updating existing entry: {sanitized_name}")
            existing.path = db_path
        else:
            print(f"Creating new entry: {sanitized_name}")
            db_entry = model(name=sanitized_name, path=db_path)
            db.add(db_entry)
        
        return {
            "original_name": original_filename,
            "stored_name": sanitized_name,
            "type": file_type,
            "path": db_path
        }
    except Exception as e:
        print(f"Error processing file {original_filename}: {str(e)}")
        traceback.print_exc()
        return None

@app.on_event("startup")
async def on_startup():
    print("Starting application...")
    try:
        db = SessionLocal()
        try:
            sync_folder_to_db(db)
        finally:
            db.close()
        print("Startup completed successfully")
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/album_images", StaticFiles(directory=UPLOAD_DIR), name="album_images")
app.mount("/music_audios", StaticFiles(directory=AUDIO_DIR), name="music_audios")
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")

app.include_router(image_router, prefix="/api")
app.include_router(audio_router, prefix="/api")
app.include_router(audiomic_router, prefix="/api")

@app.get("/mapper.txt")
async def get_mapper():
    MAPPER_PATH = os.path.join(BASE_DIR, 'mapper.txt')
    if os.path.exists(MAPPER_PATH):
        return FileResponse(MAPPER_PATH)
    else:
        raise HTTPException(status_code=404, detail="Mapper file not found")

@app.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")

    temp_dir = os.path.join(TEMP_DIR, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Created temp directory: {temp_dir}")

    try:
        # Save ZIP to temp directory
        zip_path = os.path.join(temp_dir, file.filename)
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if not zipfile.is_zipfile(zip_path):
            raise HTTPException(status_code=400, detail="Invalid ZIP archive")

        processed_files = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract to temp directory
            zip_ref.extractall(temp_dir)
            
            # Process files from extracted content
            for root, _, files in os.walk(temp_dir):
                for filename in files:
                    # Skip the original ZIP file itself
                    if filename == file.filename:
                        continue
                        
                    file_path = os.path.join(root, filename)
                    
                    # Process image files
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        destination_path = os.path.join(UPLOAD_DIR, filename)
                        shutil.copy2(file_path, destination_path)
                        db_path = f"/album_images/{filename}"
                        new_image = AlbumImage(name=filename, path=db_path)
                        db.add(new_image)
                        processed_files.append({
                            "filename": filename,
                            "type": "image",
                            "path": db_path
                        })
                    
                    # Process audio files
                    elif filename.lower().endswith(('.mid', '.midi')):
                        destination_path = os.path.join(AUDIO_DIR, filename)
                        shutil.copy2(file_path, destination_path)
                        db_path = f"/music_audios/{filename}"
                        new_audio = MusicAudio(name=filename, path=db_path)
                        db.add(new_audio)
                        processed_files.append({
                            "filename": filename,
                            "type": "audio",
                            "path": db_path
                        })

        # Commit changes to database
        db.commit()
        print(f"Processed {len(processed_files)} files successfully")
        return {
            "message": "ZIP archive processed successfully",
            "processed_files": processed_files
        }
    
    except Exception as e:
        db.rollback()
        print(f"Error processing ZIP: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing ZIP archive: {str(e)}")
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

async def append_to_mapper(file: UploadFile):
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="Mapper file must be a .txt file"
        )
    
    MAPPER_PATH = os.path.join(BASE_DIR, 'mapper.txt')
    
    if not os.path.exists(MAPPER_PATH):
        with open(MAPPER_PATH, 'w', encoding='utf-8') as f:
            pass
    
    content = await file.read()
    content_str = content.decode('utf-8')
    
    if not content_str.endswith('\n'):
        content_str += '\n'
    
    with open(MAPPER_PATH, 'a', encoding='utf-8') as mapper_file:
        mapper_file.write(content_str)
    
    return {"message": "Mapper content appended successfully"}

@app.post("/submit-all")
async def submit_all(
    images: list[UploadFile] = File(default=[]),
    audios: list[UploadFile] = File(default=[]),
    mapper: UploadFile = File(default=None),
    db: Session = Depends(get_db)
):
    print(f"Received {len(images)} images, {len(audios)} audios")
    responses = []
    
    try:
        # Process images
        for image in images:
            print(f"Processing image: {image.filename}")
            
            # Handle ZIP files
            if image.filename.lower().endswith('.zip'):
                print("Processing image ZIP file")
                temp_dir = os.path.join(TEMP_DIR, str(uuid.uuid4()))
                os.makedirs(temp_dir, exist_ok=True)
                
                try:
                    # Save and extract ZIP
                    zip_path = os.path.join(temp_dir, image.filename)
                    with open(zip_path, "wb") as buffer:
                        shutil.copyfileobj(image.file, buffer)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Process extracted files
                    for root, _, files in os.walk(temp_dir):
                        for filename in files:
                            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                                file_path = os.path.join(root, filename)
                                sanitized_name = sanitize_filename(filename)
                                destination_path = os.path.join(UPLOAD_DIR, sanitized_name)
                                db_path = f"/album_images/{sanitized_name}"
                                
                                # Copy file to destination
                                shutil.copy2(file_path, destination_path)
                                
                                # Add to database
                                new_image = AlbumImage(name=sanitized_name, path=db_path)
                                db.add(new_image)
                                responses.append({
                                    "file": sanitized_name,
                                    "type": "image",
                                    "path": db_path
                                })
                                print(f"Processed extracted image: {sanitized_name}")
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
            # Handle regular image files
            elif image.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                sanitized_name = sanitize_filename(image.filename)
                file_path = os.path.join(UPLOAD_DIR, sanitized_name)
                db_path = f"/album_images/{sanitized_name}"
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                new_image = AlbumImage(name=sanitized_name, path=db_path)
                db.add(new_image)
                responses.append({
                    "file": sanitized_name,
                    "type": "image",
                    "path": db_path
                })
                print(f"Processed single image: {sanitized_name}")

        # Process audio files
        for audio in audios:
            print(f"Processing audio: {audio.filename}")
            
            # Handle ZIP files containing audio
            if audio.filename.lower().endswith('.zip'):
                print("Processing audio ZIP file")
                temp_dir = os.path.join(TEMP_DIR, str(uuid.uuid4()))
                os.makedirs(temp_dir, exist_ok=True)
                
                try:
                    # Save and extract ZIP
                    zip_path = os.path.join(temp_dir, audio.filename)
                    with open(zip_path, "wb") as buffer:
                        shutil.copyfileobj(audio.file, buffer)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Process extracted files
                    for root, _, files in os.walk(temp_dir):
                        for filename in files:
                            if filename.lower().endswith(('.mid', '.midi')):
                                file_path = os.path.join(root, filename)
                                sanitized_name = sanitize_filename(filename)
                                destination_path = os.path.join(AUDIO_DIR, sanitized_name)
                                db_path = f"/music_audios/{sanitized_name}"
                                
                                # Copy file to destination
                                shutil.copy2(file_path, destination_path)
                                
                                # Add to database
                                new_audio = MusicAudio(name=sanitized_name, path=db_path)
                                db.add(new_audio)
                                responses.append({
                                    "file": sanitized_name,
                                    "type": "audio",
                                    "path": db_path
                                })
                                print(f"Processed extracted audio: {sanitized_name}")
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Handle regular audio files
            elif audio.filename.lower().endswith(('.mid', '.midi')):
                sanitized_name = sanitize_filename(audio.filename)
                file_path = os.path.join(AUDIO_DIR, sanitized_name)
                db_path = f"/music_audios/{sanitized_name}"
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(audio.file, buffer)
                
                new_audio = MusicAudio(name=sanitized_name, path=db_path)
                db.add(new_audio)
                responses.append({
                    "file": sanitized_name,
                    "type": "audio",
                    "path": db_path
                })
                print(f"Processed single audio: {sanitized_name}")

        # Process mapper file
        if mapper:
            print(f"Processing mapper: {mapper.filename}")
            await append_to_mapper(mapper)
            responses.append({
                "file": mapper.filename,
                "type": "mapper",
                "status": "appended"
            })

        db.commit()
        print("All files processed successfully")
        return {
            "message": "All files submitted successfully",
            "files": responses
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error in submit_all: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
    
@app.post("/sync-database")
async def force_sync_database(db: Session = Depends(get_db)):
    try:
        sync_folder_to_db(db)
        return {"message": "Database synchronized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/albums")
async def get_albums(db: Session = Depends(get_db)):
    print("Fetching albums...")
    try:
        albums = db.query(AlbumImage).all()
        print(f"Found {len(albums)} albums")
        return [{
            "id": album.id,
            "name": album.name,
            "path": album.path
        } for album in albums]
    except Exception as e:
        print(f"Error getting albums: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting albums: {str(e)}")

@app.get("/audios")
async def get_audios(db: Session = Depends(get_db)):
    print("Fetching audios...")
    try:
        audios = db.query(MusicAudio).all()
        print(f"Found {len(audios)} audios")
        return [{
            "id": audio.id,
            "name": audio.name,
            "path": audio.path
        } for audio in audios]
    except Exception as e:
        print(f"Error getting audios: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting audios: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Music Album API!"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Absolute path to the script directory
INPUT_DIR = os.path.join(BASE_DIR, "routes/mic/recorded_input")
OUTPUT_DIR = os.path.join(BASE_DIR, "routes/mic/recorded_output")

@app.post("/start-recording")
async def start_record(bg_task: BackgroundTasks):
    """Endpoint to start audio recording"""
    bg_task.add_task(record_audio)  # Start recording in the background
    return {"message": "Recording started..."}

@app.post("/get-midi-file")
async def get_midi_file():
    """Fetch list of MIDI files from the output directory"""
    try:
        midi_files = [file for file in os.listdir(OUTPUT_DIR) if file.endswith('.mid')]
        if not midi_files:
            raise HTTPException(status_code=404, detail="No MIDI files found")
        return {"midi_files": midi_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving MIDI files: {str(e)}")

@app.get("/get-recorded-audio/")
async def get_recorded_audio():
    """Return the most recent recorded MIDI file"""
    try:
        # Debugging: Print the contents of the OUTPUT_DIR
        print("Checking the files in OUTPUT_DIR:", OUTPUT_DIR)
        midi_files = [file for file in os.listdir(OUTPUT_DIR) if file.endswith('.mid')]
        
        # Debugging: Print the list of .mid files found
        print("MIDI files found:", midi_files)
        
        if midi_files:
            # Sort the MIDI files and get the most recent one by name
            latest_midi = sorted(midi_files)[-1]
            file_path = os.path.join(OUTPUT_DIR, latest_midi)
            
            # Debugging: Print the file path being returned
            print("Returning MIDI file:", file_path)
            
            # Return the MIDI file as a response
            return FileResponse(path=file_path, media_type='audio/midi')
        else:
            raise HTTPException(status_code=404, detail="No recorded MIDI found")
    except Exception as e:
        # Debugging: Print the error message for troubleshooting
        print(f"Error retrieving recorded MIDI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving recorded MIDI: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)