from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import os
import shutil
from tempfile import NamedTemporaryFile
import time
import traceback
from .audio import audio_retrieval_main

router = APIRouter(tags=["audio-retrieval"])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AUDIO_FOLDER = os.path.join(BASE_DIR, "music_audios")

print(f"Audio Route - BASE_DIR: {BASE_DIR}")
print(f"Audio Route - AUDIO_FOLDER: {AUDIO_FOLDER}")

@router.post("/audio-search")
async def search_similar_audio(file: UploadFile = File(...)):
    temp = None
    try:
        print("Starting audio search process...")
        
        if not file.content_type.startswith('audio/'):
            return JSONResponse(
                status_code=400,
                content={"error": "File must be an audio file"}
            )
        
        start_time = time.time()
        
        print("Creating temporary file...")
        temp = NamedTemporaryFile(delete=False)
        temp_path = temp.name
        temp.close()
        
        with open(temp_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
            
        print(f"Temporary file created at: {temp_path}")
        print(f"Audio folder path: {AUDIO_FOLDER}")
        
        print("Starting audio retrieval main function...")
        top_similar, distances = audio_retrieval_main(temp_path, AUDIO_FOLDER)
        
        print("Processing results...")
        relative_paths = [os.path.basename(path) for path in top_similar]
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"Search completed in {execution_time}ms")
        print(f"Found {len(relative_paths)} similar songs")
        
        return JSONResponse(content={
            "similar_audios": relative_paths,
            "similarity_scores": distances,
            "execution_time": execution_time
        })
        
    except Exception as e:
        error_message = f"Error in search_similar_audio: {str(e)}"
        print(error_message)
        print(f"Error type: {type(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )
        
    finally:
        print("Cleaning up temporary file...")
        try:
            if temp is not None:
                file.file.close()
                if os.path.exists(temp.name):
                    os.unlink(temp.name)
        except Exception as cleanup_error:
            print(f"Warning: Error during cleanup: {cleanup_error}")