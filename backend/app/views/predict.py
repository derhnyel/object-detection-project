import io
import os
from pathlib import Path
from app.mocks import apimock
from datetime import datetime
from resources import load_model
from services import cloud_storage
from flask import jsonify, current_app
from flask_restful import reqparse, abort
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage
from utilities.utility import ValidateFile, BaseHttpException, Helpers

model = load_model()


class PredictApiView(apimock.Base):
    max_payload_content_lenght = 2
    max_payload_object_size = 2097152

    def __init__(self):
        super().__init__()

    def setup(self) -> None:
        """
        Setup PredictViewApi specific
        dependencies and logic
        """
        self.validatefile = ValidateFile(
            max_lenght=self.max_payload_object_size
        )  # Initialize Validate on Payload files
        self.model = model
        self.cloud_bucket = cloud_storage
        self.cloud_bucket_prefix = current_app.config["CLOUD_BUCKET_PREFIX"]
        self.result_path = Path(current_app.config["RESULT_PATH"])

    def define_parser(self):
        """
        Define Request Payload
        Argument Parser
        """
        post_parser = reqparse.RequestParser()
        post_parser.add_argument(
            "image",
            dest="image",
            required=True,
            help="Upload image as payload",
            action="append",
            location="files",
            type=FileStorage,
        )
        return post_parser

    def pushtobucket(self, filename, id):
        """
        Upload Image to Cloud and
        generate download link
        """
        local_image_filepath = Path(self.result_path, id, filename)
        cloudbucket_path = f"{self.cloud_bucket_prefix}/{id}/{filename}"
        return self.cloud_bucket.upload_blob(cloudbucket_path, local_image_filepath)

    def post(self):
        """
        A  `POST` request to
        Make Predictions Using
        Loaded Model on Image Uploaded
        and Return a Json Response with
        Image Details including a Download Link
        To the Detected Image File in a Cloud Bucket
        """
        images = list()
        args = self.parser.parse_args()  # Parse Request Payload Argument
        if not self.validatefile.isvalid_lenght(
            args.image, self.max_payload_content_lenght
        ):
            message, status_code = BaseHttpException.handle_payload_too_large(Exception)
            abort(status_code, message=message)
        for index, imageObject in enumerate(args.image):
            # Preprocessing Images
            self.validatefile.file = imageObject
            file_lenght = Helpers.get_file_size(imageObject)
            if self.validatefile.isvalid("image", file_lenght):
                filename = os.path.basename(imageObject.filename)
                id = Helpers.generate_uuid(
                    source="cloud",
                    base_path=self.result_path,
                    prefix=self.cloud_bucket_prefix,
                    cloud=self.cloud_bucket,
                )
                with imageObject.stream as imageFile:
                    try:
                        image = Image.open(io.BytesIO(imageFile.read()))  # base64
                    except UnidentifiedImageError:
                        message, status_code = BaseHttpException.handle_invalid_media(
                            Exception
                        )
                        abort(status_code, message=message)
                image.filename = filename
                # Predict and Save Image
                result = self.model(image, size=320)  # speed 320 , Accuracy 640
                records = result.pandas().xyxy[0].to_json(orient="records")
                if len(records) == 2:
                    images.append(
                        dict(
                            prefix=None,
                            id=None,
                            index=index,
                            result=records,
                            filename=filename,
                            downloadlink=None,
                            filelenght=file_lenght,
                        )
                    )
                    continue
                result.save(save_dir=Path(self.result_path, id))
                downloadlink = self.pushtobucket(filename, id)
                images.append(
                    dict(
                        prefix=self.cloud_bucket_prefix,
                        id=id,
                        index=index,
                        result=records,
                        filename=filename,
                        downloadlink=downloadlink,
                        filelength=file_lenght,
                    )
                )
            else:
                message, status_code = BaseHttpException.handle_invalid_media(Exception)
                abort(status_code, message=message)
        return jsonify({"results": images, "createdAt": str(datetime.now().utcnow())})
