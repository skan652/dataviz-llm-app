FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD sh -c "uvicorn dataviz_backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"
