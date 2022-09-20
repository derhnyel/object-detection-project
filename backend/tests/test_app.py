from pathlib import Path
from app import predict_url_prefix
from tests.test_base import BaseCase


class PredictTest(BaseCase):
    def test_successful_prediction(self):
        files = {"image": open(Path(self.rootpath, "files", "validimage.jpg"), "rb")}
        response = self.app.post(predict_url_prefix, data=files)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.json.get("results"))

    def test_invalid_payload(self):
        files = {"image": open(Path(self.rootpath, "files", "invalidfile.pdf"), "rb")}
        response = self.app.post(predict_url_prefix, data=files)
        self.assertEqual(415, response.status_code)

    def test_maximum_payload_items(self):
        files = {
            "image": [
                open(Path(self.rootpath, "files", "validimage3.jfif"), "rb"),
                open(Path(self.rootpath, "files", "validimage4.jfif"), "rb"),
                open(Path(self.rootpath, "files", "validimage5.jfif"), "rb"),
            ],
        }
        response = self.app.post(predict_url_prefix, data=files)
        self.assertIsNone(response.json.get("results"))
        self.assertEqual(413, response.status_code)

    def predict_batch_items(self):
        files = {
            "image": [
                open(Path(self.rootpath, "files", "validimage.jpg"), "rb"),
                open(Path(self.rootpath, "files", "validimage2.jpg"), "rb"),
            ]
        }
        response = self.app.post(predict_url_prefix, data=files)
        self.assertEqual(len(response.json.get("results")), len(files["image"]))

    def test_maximum_payload_item_size(self):
        files = {
            "image": open(Path(self.rootpath, "files", "largesizeimage.jpg"), "rb")
        }
        response = self.app.post(predict_url_prefix, data=files)
        self.assertEqual(415, response.status_code)

    def test_invalid_url_path(self):
        response = self.app.post("/test")
        self.assertEqual(404, response.status_code)

    def test_invalid_request_method(self):
        response = self.app.get(predict_url_prefix)
        self.assertEqual(405, response.status_code)

    def test_empty_payload(self):
        response = self.app.post(predict_url_prefix)
        self.assertEqual(400, response.status_code)

    def test_wrong_payload_name(self):
        files = {"test": open(Path(self.rootpath, "files", "validimage.jpg"), "rb")}
        response = self.app.post(predict_url_prefix, data=files)
        self.assertEqual(400, response.status_code)
