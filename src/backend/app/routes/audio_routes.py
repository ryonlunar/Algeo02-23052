from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import os
import shutil
from tempfile import NamedTemporaryFile
import time
import traceback
from .audio import audio_retrieval_main
import asyncio
from concurrent.futures import ThreadPoolExecutor
import signal

router = APIRouter(tags=["audio-retrieval"])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AUDIO_FOLDER = os.path.join(BASE_DIR, "music_audios")

executor = ThreadPoolExecutor()

@router.get("/music_audios/{filename}")
async def serve_midi_file(filename: str):
    file_path = os.path.join(AUDIO_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/midi")
    else:
        raise HTTPException(status_code=404, detail="MIDI file not found")

@router.post("/audio-search")
async def search_similar_audio(file: UploadFile = File(...)):
    temp = None
    task = None
    
    try:
        if not file.content_type.startswith('audio/'):
            return JSONResponse(
                status_code=400,
                content={"error": "File must be an audio file"}
            )
        
        start_time = time.time()
        
        temp = NamedTemporaryFile(delete=False)
        temp_path = temp.name
        temp.close()
        
        with open(temp_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        loop = asyncio.get_event_loop()
        task = loop.run_in_executor(executor, audio_retrieval_main, temp_path, AUDIO_FOLDER)

        try:
            top_similar, distances = await asyncio.wait_for(task, timeout=None)
            
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000

            return JSONResponse(content={
                "similar_audios": [os.path.basename(p) for p in top_similar],
                "similarity_scores": distances.tolist(),
                "execution_time": execution_time
            })
            
        except asyncio.CancelledError:
            if task:
                task.cancel()
            return JSONResponse(
                status_code=499,
                content={"error": "Operation cancelled"}
            )
            
    except Exception as e:
        print(f"Error in search_similar_audio: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
        
    finally:
        try:
            if temp and os.path.exists(temp.name):
                os.unlink(temp.name)
            if task and not task.done():
                task.cancel()
        except Exception as cleanup_error:
            print(f"Warning: Error during cleanup: {cleanup_error}")