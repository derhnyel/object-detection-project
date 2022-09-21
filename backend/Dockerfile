# Use Python39
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy full project directory
COPY . /backend
# Set the WORKDIR to be the folder
WORKDIR /backend

# Copy requirements.txt to the docker image and install packages
RUN pip install -r requirements.txt
RUN pip install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html

# Set environmental file
RUN export ENV_FILE_LOCATION=./.env

# Expose port 5000
EXPOSE 5000
ENV PORT 5000

# Use gunicorn as the entrypoint
CMD exec gunicorn --bind :$PORT main:app --workers 1 --threads 8 --timeout 0