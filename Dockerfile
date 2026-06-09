FROM python:3.14-alpine
LABEL authors="Raven"
WORKDIR /app
COPY requirements.txt .
RUN pip install -i https://mirror-pypi.runflare.com/simple --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_DEBUG=0
ENV FLASK_APP=app.py
ENV SECRET_KEY=deba3950f8781edda01879ed6f6a4d95e9d8178359e71c3d
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]