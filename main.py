"""
# Run the app using: uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import requests

app = FastAPI()

# Change this to the actual machine's address where HTML pages are stored
# REMOTE_SERVER = "http://<YOUR-SERVER-IP>:8080"
HTML_DIRECTORY = Path("/app/html_files")
# HTML_DIRECTORY = Path("html_files")


@app.get("/fetch/{page_name}")
def fetch_html(page_name: str):
    # url = f"{REMOTE_SERVER}/{page_name}"
    file_path = HTML_DIRECTORY / page_name
    try:
        # response = requests.get(url)
        # response.raise_for_status()

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Page not found")

        html_content = file_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content, status_code=200)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
