FROM python:3.11.9-alpine

WORKDIR /app

RUN apk add ffmpeg

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]