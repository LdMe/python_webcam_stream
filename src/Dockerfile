FROM python:3

WORKDIR /usr/src/app
RUN apt update
RUN apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "/usr/src/app/client.py"  ]