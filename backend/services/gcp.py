import datetime
from google.cloud import storage
from utilities.utility import Logging

log = Logging().logging


class Storage:
    """Handle GCP Cloud Storage"""

    def __init__(self, project_id, bucket_name, region=None):
        self.storage_client = storage.Client(project=project_id)
        self.bucket_name = bucket_name
        try:
            self.bucket = self.storage_client.get_bucket(bucket_name)
            log.info("Bucket {} exists.".format(self.bucket.name))
        except Exception as e:
            log.warning(f"This exception occured while Getting bucket: {e}")
            self.bucket = self.storage_client.create_bucket(bucket_name, region)
            log.info(
                "Attempting to Create Bucket.....Bucket {} created.".format(
                    self.bucket.name
                )
            )

    def download_blob(self, filename, filepath, write_method="w"):
        """Download from cloud bucket."""
        blob = storage.Blob(filename, self.bucket)
        with open(filepath, write_method) as file_obj:
            self.storage_client.download_blob_to_file(blob, file_obj)
        log.info(f"File {filename} downloaded to {filepath} .")

    def blob_exists(self, filename):
        """Check if blob Exists."""
        blob = self.bucket.blob(filename)
        check = blob.exists()
        log.info(f"Blob exists in Cloud Bucket {check}")
        return check

    def upload_blob(self, filename, filepath, public=True):
        """Uploads a file from local Path to the bucket."""
        blob = self.bucket.blob(filename)
        blob.upload_from_filename(filepath)
        log.info(
            "File {} uploaded to {} blob in cloud bucket.".format(filepath, filename)
        )
        return self.make_blob_public(filename) if public else None

    def upload_from_stream(
        self, blobpath, file, content_type=None, read=True, filename=None, public=True
    ):
        """Upload A file stream from memory to cloud bucket"""
        blob = self.bucket.blob(blobpath)
        blob.upload_from_string(
            file.read() if read else file,
            content_type=content_type if content_type else file.content_type,
        )
        log.info(
            "File {} uploaded to {} blob in cloud bucket.".format(
                filename if filename else file.filename, blobpath
            )
        )
        return self.make_blob_public(blobpath) if public else None

    def make_blob_public(self, blob_name):
        """Makes a blob publicly accessible."""
        blob = self.bucket.blob(blob_name)
        blob.make_public()
        log.info(f"Blob {blob.name} is publicly accessible at {blob.public_url}")
        return blob.public_url

    def generate_uri(self, blob_name):
        url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
        log.info(f"Generated  URL for {blob_name} is : {url}")
        return url

    def generate_download_signed_url(self, filename, minutes=15):
        """Generates a v4 signed URL for downloading a blob."""
        blob = self.bucket.blob(filename)
        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for `minutes` minutes
            expiration=datetime.timedelta(minutes=minutes),
            # Allow GET requests using this URL.
            method="GET",
        )
        log.info(f"Generated GET signed URL for {filename} is : {url}")
        return url

    def delete(self, filename):
        """Delete a file from bucket"""
        blob = self.bucket.blob(filename)
        blob.delete()
        log.info(f"Deleted blob {filename}")

    def batch_delete(self, prefix):
        """Delete Files in Directory"""
        blobs = self.bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            blob.delete()
        log.info(f"Deleted blob {blobs}")
