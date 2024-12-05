from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from image_process import image_processing
import os
import shutil
from tempfile import NamedTemporaryFile


app = FastAPI()

IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "../..", "dataset", "album_images")

@app.post("/api/retrieve")
async def retrieve_images(file: UploadFile = File(...)):
    
    try:
        temp = NamedTemporaryFile(delete=False)
        with open(temp.name, 'wb') as f:
            shutil.copyfileobj(file.file, f)
            
        top_similar, top_distances = image_processing.image_retrieval_main(temp.name, IMAGE_FOLDER, n=10)
        
        os.remove(temp.name)
        
        return JSONResponse(content={
            "top_similar_images": top_similar,
            "top_distances": top_distances})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})