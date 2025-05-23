# official lightweight python image
FROM python:3.11-slim

#setting up working dir inside container
WORKDIR /app

#copying only requirements first to ensure Docker Layer Caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#installing python dependencies
COPY . .

#exposing port 80 for http traffic
EXPOSE 80

#defining the default command to run the app with uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
