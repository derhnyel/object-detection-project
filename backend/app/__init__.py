from flask import Flask
from config import Config
from flask_restful import Api

app = Flask(__name__)
app.config.from_object(Config)


from app.views import PredictApiView

predict_api = Api(app, catch_all_404s=True)
predict_url_prefix = PredictApiView.route
predict_api.add_resource(PredictApiView, predict_url_prefix)

__all__ = ["mocks"]
