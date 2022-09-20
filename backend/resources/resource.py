import os
import torch
from pathlib import Path


def load_model(
    github_link="ultralytics/yolov5",
    model_name="yolov5s",
    verbose=False,
    path="resources/cache/models",
):
    """
    setting pytorch default hub folder to '{path}'
    in project directory and loading cached model if it exists
    or downloading and caching the model.
    """
    base_path = Path(os.path.dirname(os.path.abspath(__file__)))
    torch.hub.set_dir(Path(base_path.parent, path))
    model = torch.hub.load(github_link, model_name, _verbose=verbose)
    return model
