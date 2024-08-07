# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure the model file is also copied
COPY resnet.pth .

# Expose the port FastAPI will run on
EXPOSE 8080

# Command to run the FastAPI app
CMD ["uvicorn", "serverResnet:app", "--host", "0.0.0.0", "--port", "8080"]
