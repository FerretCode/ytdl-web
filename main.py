from __future__ import unicode_literals

import yt_dlp
import json

from typing import Union, Annotated

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import youtube_dl.YoutubeDL

app = FastAPI()

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def ytdl(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/submit")
async def download_video(
    url: Annotated[str, Form()],
    mp4: Annotated[str, Form()],
):

    if mp4 == "mp4":
        ytdl_opts = {
            'paths': {
                "home": "templates/static"
            }
        }
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            ydl.download([url])
    else:
        ytdl_opts = {
            'paths': {
                "home": "templates/static"
            },
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            res = ydl.extract_info(url, download=True)

            data = ydl.sanitize_info(res)

            print(data['filename'])
