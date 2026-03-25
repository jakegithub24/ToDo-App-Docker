FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN python -m venv myvenv && myvenv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["myvenv/bin/python", "app.py"]
