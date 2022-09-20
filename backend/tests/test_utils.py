import os
from pathlib import Path
from tests.test_base import BaseCase
from utilities.utility import Helpers


class UtilsTest(BaseCase):
    def test_generate_directory_unique_uuid(self):
        id = Helpers.generate_uuid(
            source="dir", base_path=Path(os.environ["RESULT_PATH"])
        )
        self.assertEqual(os.path.exists(Path(os.environ["RESULT_PATH"], id)), False)

    def test_generate_cloud_unique_uuid(self):
        id = Helpers.generate_uuid(
            source="cloud",
            base_path=os.environ["RESULT_PATH"],
            prefix=os.environ["CLOUD_BUCKET_PREFIX"],
            cloud=self.cloud_storage,
        )
        self.assertEqual(
            self.cloud_storage.blob_exists(f"{os.environ['CLOUD_BUCKET_PREFIX']}/{id}"),
            False,
        )
