FROM python:3.14-alpine
LABEL authors="Raven"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_DEBUG=0
ENV FLASK_APP=app.py
# SECRET_KEY must be provided at runtime.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]