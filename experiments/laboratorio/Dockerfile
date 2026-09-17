FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV GAMA=alta HF_HUB_CACHE=/models/hf
ENTRYPOINT ["python", "main.py"]
CMD ["--wav", "/data/llamada.wav", "--salida", "/app/artifacts/corrida.json"]
