import os
import shutil

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


def run_final_script():
    try:
        # os.chdir("C:/Users/vuxxw/PycharmProjects/ExtractID/Extract_ID_Card/BE")
        # os.chdir("../../BE")
        subprocess.run(["python3", "final.py"])
        return {"message": "final.py executed successfully"}
    except Exception as e:
        return {"error": f"Error executing final.py: {str(e)}"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    current_directory = Path.cwd()
    be_directory = current_directory.parent / "BE"
    os.chdir(be_directory)
    try:
        os.makedirs("images", exist_ok=True)
        with open(f"images/{file.filename}", "wb") as buffer:
            buffer.write(file.file.read())

        # Execute final.py after successful file upload
        run_final_script()

        return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Error uploading file: {str(e)}"}, status_code=500)


@app.get("/api/download")
def download_output():
    current_directory = Path.cwd()
    be_directory = current_directory.parent / "BE"
    os.chdir(be_directory)
    output_path = Path("output.csv")

    if not output_path.is_file():
        return {"error": "File not found"}

    return FileResponse(output_path, filename="output.csv")