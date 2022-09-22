import os
import shutil
import unittest
from app import app
from pathlib import Path
from services import cloud_storage


class BaseCase(unittest.TestCase):
    rootpath = os.path.basename(
        os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    )

    def setUp(self):
        self.app = app.test_client()
        self.cloud_storage = cloud_storage

    def tearDown(self):
        if "test" in os.environ["CLOUD_BUCKET_PREFIX"]:
            self.cloud_storage.batch_delete(os.environ["CLOUD_BUCKET_PREFIX"])
        try:
            shutil.rmtree(Path(os.environ["RESULT_PATH"]))
        except:
            pass
