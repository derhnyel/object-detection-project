# Use Python39
FROM python:3.9

# Set the WORKDIR to be the folder
WORKDIR /backend

# Copy requirements.txt to the docker image and install packages
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html

# Copy full project directory
COPY . .

# Set environmental file
RUN export ENV_FILE_LOCATION=./.env

# Expose port 5000
EXPOSE 5000
ENV PORT 5000

# Use gunicorn as the entrypoint
CMD exec gunicorn --bind :$PORT main:app --workers 3 --threads 3 --timeout 30