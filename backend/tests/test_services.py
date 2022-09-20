import os
from pathlib import Path
from app import predict_url_prefix
from tests.test_base import BaseCase


class GcpTest(BaseCase):
    def test_upload_blob(self):
        files = {"image": open(Path(self.rootpath, "files", "validimage.jpg"), "rb")}
        response = self.app.post(predict_url_prefix, data=files)
        data = response.json.get("results")[0]
        path = f"{data['prefix']}/{data['id']}/{data['filename']}"
        self.assertEqual(self.cloud_storage.blob_exists(path), True)

    def test_download_blob(self):
        files = {"image": open(Path(self.rootpath, "files", "validimage.jpg"), "rb")}
        response = self.app.post(predict_url_prefix, data=files)
        data = response.json.get("results")[0]
        path = f"{data['prefix']}/{data['id']}/{data['filename']}"
        local_file_path = Path(
            os.environ["RESULT_PATH"],
            f"{data['filename']}",
        )
        self.cloud_storage.download_blob(path, local_file_path, write_method="wb")
        self.assertEqual(os.path.exists(local_file_path), True)
