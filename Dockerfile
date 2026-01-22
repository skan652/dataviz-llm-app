FROM python:3.11

WORKDIR /app

# 1️⃣ Copier uniquement les fichiers de deps (cache intelligent)
COPY pyproject.toml uv.lock ./

RUN pip install --upgrade pip
RUN pip install uv

# 2️⃣ Installer les dépendances (uvicorn inclus)
RUN uv sync --no-cache

# 3️⃣ Copier le reste du code
COPY . .

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "dataviz_backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
