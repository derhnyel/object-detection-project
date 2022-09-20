import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.curdir)


class Config(object):
    # SECRET_KEY = os.environ.get("SECRET_KEY", "default sekret")
    PROJECT_REGION = os.environ.get("PROJECT_REGION")
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    PROJECT_ID = os.environ.get("PROJECT_ID")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    TO_ADDR = os.environ.get("TO_ADDR")
    FROM_ADDR = os.environ.get("FROM_ADDR")
    RESULT_PATH = os.environ.get("RESULT_PATH", "results/detect")
    CLOUD_BUCKET_PREFIX = os.environ.get("ClOUD_BUCKET_PREFIX", "results")
    MAX_CONTENT_LENGTH = 6097152  # (2*1024*1024) 2MB
