FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
# Copy only the requirements files first
COPY requirements-base.txt requirements-base.txt


# Install ML dependencies in a separate layer
RUN pip install -r requirements.txt
# Install base requirements first (this layer gets cached)
RUN pip install -r requirements-base.txt



# Copy the rest of the application
COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
