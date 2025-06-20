FROM python:latest

WORKDIR /app

COPY vm-info-app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY vm-info-app .

CMD ["python", "app.py"]
