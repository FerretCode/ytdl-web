# ytdl-web
a website for downloading youtube videos

## usage
- install dependencies
```
pip install -r requirements.txt
```
- configure residential proxies
  - create a file called `proxies.txt` in the project directory
  - place newline separated proxy URLs (formatted: `http://username:password@ip:port`
- run the application using fastapi, uvicorn, etc.
### uvicorn
```
uvicorn main:app --host 0.0.0.0 --port 80
```
### fastapi
```
fastapi run main.py
```
