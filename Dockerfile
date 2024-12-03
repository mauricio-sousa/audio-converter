FROM python:3.13.0

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*


CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
