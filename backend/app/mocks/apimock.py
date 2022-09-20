import os
from flask_restful import Resource
from abc import ABCMeta, abstractmethod


class Base(Resource):

    __metaclass__ = ABCMeta

    basepath = os.path.basename(
        os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    )
    route = "/"  # Application Url Route

    max_payload_content_lenght = 1  # Maximum Items Payload can Have
    max_payload_object_size = 0  # Maximum file/object size in payload

    def __init__(self):
        self.setup()
        self.parser = self.define_parser()

    @abstractmethod
    def setup(self):
        """
        Setup Api resource and
        Specific dependencies
        """
        raise NotImplementedError()

    @abstractmethod
    def define_parser(self):
        """Define Request Parser"""
        raise NotImplementedError()
