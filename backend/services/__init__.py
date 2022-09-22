import os
from dotenv import load_dotenv

load_dotenv()


"""
Initialize various third party 
services to be returned on import 
"""
service = os.environ["CLOUD_SERVICE"]


def __init_gcp():
    """
    Initialize Google Cloud
    With environment credentials
    """
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        if os.environ.get("SERVICE_KEY_PATH"):
            service_key_path = os.environ["SERVICE_KEY_PATH"]
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_key_path
    from services import gcp

    storage = gcp.Storage(
        os.environ["PROJECT_ID"],
        os.environ["BUCKET_NAME"],
        os.environ["PROJECT_REGION"],
    )
    return gcp, storage


cloud, cloud_storage = __init_gcp() if (service == "gcp") else __init_gcp()
__all__ = ["cloud", "cloud_storage"]
