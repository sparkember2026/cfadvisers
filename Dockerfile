# API + web app. Data is baked in from data/; mount your own over /app/data to change it without rebuilding.
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
# Set CFA_API_TOKEN to require a bearer token on the API and data (the page asks for it once).
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/v1/health')"
CMD ["python", "-m", "cfadvisers", "serve", "--host", "0.0.0.0", "--port", "8000"]
