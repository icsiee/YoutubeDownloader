from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import yt_dlp
import uuid
import tempfile
import os

app = FastAPI()

@app.get("/download")
def download_video(
    url: str = Query(..., description="YouTube video URL"),
    option: str = Query("video", description="Download option: video or audio"),
    quality: str = Query("best", description="Video quality: best, 720p, 480p, etc.")
):
    temp_dir = tempfile.gettempdir()
    base_filename = os.path.join(temp_dir, str(uuid.uuid4()))

    if option == "audio":
        ext = "mp3"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": base_filename,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }
            ]
        }
    else:
        ext = "mp4"
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        elif quality == "720p":
            fmt = "bestvideo[height<=720]+bestaudio/best"
        elif quality == "480p":
            fmt = "bestvideo[height<=480]+bestaudio/best"
        else:
            fmt = "bestvideo+bestaudio/best"

        ydl_opts = {
            "format": fmt,
            "outtmpl": base_filename,
            "merge_output_format": "mp4",
            "postprocessor_args": [
                "-c:v", "copy",   # videoya dokunma
                "-c:a", "aac",    # sesi AAC'ye çevir
                "-b:a", "192k"
            ]
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    final_path = f"{base_filename}.{ext}"

    return FileResponse(
        path=final_path,
        filename=f"video.{ext}",
        media_type="audio/mpeg" if option == "audio" else "video/mp4",
        background=BackgroundTask(lambda: os.remove(final_path))
    )
