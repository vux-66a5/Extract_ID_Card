from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from pathlib import Path
import subprocess
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directory for uploaded images
app.mount("/public", StaticFiles(directory="public"), name="public")


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        with open(f"../../BE/images/{file.filename}", "wb") as buffer:
            buffer.write(file.file.read())
        subprocess.run(["python", "../../BE/final.py"])
        return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Error uploading file: {str(e)}"}, status_code=500)

@app.get("/api/download")
def download_output():
    output_path = Path("../../BE/output.csv")

    if not output_path.is_file():
        return {"error": "File not found"}

    return FileResponse(output_path, filename="output.csv")
