import logging
import os
from typing import List

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydub import AudioSegment

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s:%(name)s:%(message)s"
)


def convert_to_opus(file_path: str) -> str:
    audio = AudioSegment.from_file(file_path, format="mp3")
    opus_filename = f"converted_{os.path.splitext(os.path.basename(file_path))[0]}.opus"
    opus_path = f"uploads/{opus_filename}"
    audio.export(opus_path, format="opus")
    return opus_filename


@app.get("/")
async def read_root(request: Request):
    files = os.listdir("uploads")
    file_info_list = []
    for filename in files:
        original_filename = os.path.splitext(filename)[0].replace("converted_", "")
        file_info = {
            "original_filename": original_filename,
            "converted_filename": filename,
        }
        file_info_list.append(file_info)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "file_info_list": file_info_list},
    )


@app.post("/upload/")
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    for file in files:
        logger.info(f"File uploading: {file.filename}")
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

    convert_url = request.url_for("convert_files")
    return RedirectResponse(url=convert_url)


@app.post("/convert/")
async def convert_files():
    files = os.listdir("uploads")
    for filename in files:
        if filename.endswith(".mp3"):
            file_path = f"uploads/{filename}"
            converted_filename = convert_to_opus(file_path)
            logger.info(f"File converted: {converted_filename}")
            os.remove(file_path)
    return RedirectResponse(url="/", status_code=301)


@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = f"uploads/{file_name}"
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=file_name
    )
