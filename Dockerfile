FROM python:3.9

WORKDIR /app
COPY . /app
COPY html_files /app/html_files

RUN pip install fastapi uvicorn requests

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
