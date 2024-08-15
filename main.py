from __future__ import unicode_literals

import yt_dlp
import os
import time
import threading
import random

from typing import Annotated

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

templates = Jinja2Templates(directory="templates")

filenames = {}
proxies = []

if not os.path.exists("proxies.txt"):
    print("please provide a list of proxies separated by newlines in proxies.txt")
    exit(0)

with open("proxies.txt", "r") as file:
    lines = file.readlines()
    for proxy in lines:
        proxy = proxy.strip()
        original = proxy

        if proxy.startswith("https://"):
            proxy = proxy.strip("https://")
        elif proxy.startswith("http://"):
            proxy = proxy.strip("http://")
        else:  # proxy must be a url
            continue

        try:
            username_password, ip_port = proxy.split("@")
            if not len(username_password.split(":")) == 2:
                continue
            if not len(ip_port.split(":")) == 2:
                continue
        except:
            continue

        proxies.insert(0, original)


def filename_hook(d):
    if d['status'] == "finished":
        video_id = d['info_dict']['id']
        if not video_id in filenames:
            # in case the hook fires before the info is sanitized
            filenames[video_id] = None
        filenames[video_id] = d['filename']
        print(filenames[video_id])


def delete_file(filename):
    time.sleep(10*60)
    os.remove("templates/static/"+filename)


def yt_dlp_download_video(url: str, opts: dict) -> str:
    video_id = ""
    opts['progress_hooks'] = [filename_hook]
    if len(proxies) > 0:
        opts['proxy'] = proxies[random.randint(0, len(proxies))]
    with yt_dlp.YoutubeDL(opts) as ydl:
        res = ydl.extract_info(url, download=True)

        data = ydl.sanitize_info(res)
        video_id = data['id']

        # only set none if the key doesn't exist
        # protects it from overwriting already downloaded vids
        if not video_id in filenames:
            filenames[video_id] = None

    filename = filenames[video_id]
    del filenames[video_id]

    return filename


@app.get("/", response_class=HTMLResponse)
async def ytdl(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/submit")
async def download_video(
    request: Request,
    url: Annotated[str, Form()],
    mp4: Annotated[str, Form()],
):
    if not os.path.exists("templates/static"):
        os.mkdir("templates/static")

    if mp4 == "mp4":
        ytdl_opts = {
            'format': "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            'paths': {
                "home": "templates/static"
            }
        }
        filename = yt_dlp_download_video(url, ytdl_opts)
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
        filename = yt_dlp_download_video(url, ytdl_opts)

    print(filename)

    raw = os.path.basename(filename)
    split = os.path.splitext(raw)

    # perform 2 splits, since when converting to mp4 it becomes xxxx.f140.m4a
    if mp4 == "mp4":
        split = os.path.splitext(split[0])

    download_url = f"/static/{split[0]}.{mp4}"

    thread = threading.Thread(target=delete_file, args=(f"{split[0]}.{mp4}",))
    thread.start()

    return templates.TemplateResponse(
        request=request,
        name="download.html",
        context={'url': download_url}
    )
