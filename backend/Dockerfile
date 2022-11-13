# Use Python39
FROM python:3.9

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy requirements.txt to the docker image and install packages
RUN python3 -m pip install --upgrade pip
RUN pip3 install torch==1.8.1 torchvision==0.9.1 torchaudio===0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
#pip install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio===0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy full project directory
COPY . /backend

# Set the WORKDIR to be the folder
WORKDIR /backend

# Set environmental file
RUN export ENV_FILE_LOCATION=./.env

# Expose port 5000
EXPOSE 5000
ENV PORT 5000

# Use gunicorn as the entrypoint
CMD exec gunicorn --bind :$PORT main:app --workers 1 --threads 8 --timeout 0