import os
import sys
import pytest
from fastapi.testclient import TestClient
from pydub.generators import Sine

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    yield
    # Teardown: Remove all files in uploads directory after each test
    for file in os.listdir("uploads"):
        file_path = os.path.join("uploads", file)
        if os.path.isfile(file_path):
            os.unlink(file_path)

def create_test_mp3(file_path):
    # Cria um arquivo .mp3 válido usando um gerador de onda senoidal
    sine_wave = Sine(440).to_audio_segment(duration=1000)  # 1 segundo de onda senoidal a 440 Hz
    sine_wave.export(file_path, format="mp3")

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_upload_files():
    file_path = "test.mp3"
    create_test_mp3(file_path)

    with open(file_path, "rb") as f:
        response = client.post("/upload/", files={"files": f})

    assert response.status_code == 200  # Verifica se o upload foi bem-sucedido

    # Cleanup
    os.remove(file_path)

def test_convert_files():
    file_path = "uploads/test.mp3"
    create_test_mp3(file_path)

    response = client.post("/convert/")
    assert response.status_code == 200  # Verifica se a conversão foi bem-sucedida

    converted_files = os.listdir("uploads")
    assert any(file.endswith(".ogg") for file in converted_files)

def test_download_file():
    file_path = "uploads/test.mp3"
    create_test_mp3(file_path)  # Cria um arquivo .mp3 válido

    # Converte o arquivo para .ogg
    response = client.post("/convert/")
    assert response.status_code == 200  # Verifica se a conversão foi bem-sucedida

    converted_file_path = "uploads/converted_test.ogg"
    assert os.path.exists(converted_file_path)  # Verifica se o arquivo convertido existe

    response = client.get(f"/download/{os.path.basename(converted_file_path)}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"