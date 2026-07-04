# Bazna slika — Python 3.12 na Alpinu (mali, brz)
FROM python:3.12-alpine

# Radni folder unutar kontejnera
WORKDIR /app

# Kopiraj fajlove u kontejner
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Port koji aplikacija koristi
EXPOSE 5000

# Komanda za pokretanje
CMD ["python3", "app.py"]
