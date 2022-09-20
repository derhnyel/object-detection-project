import os
import uuid
import logging
from pathlib import Path
from enum import Enum, unique
from logging.config import dictConfig
from logging.handlers import SMTPHandler
from flask.logging import default_handler
from flask import has_request_context, request


@unique
class LogLevels(Enum):
    info = logging.INFO
    debug = logging.DEBUG
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL


class Logging:
    def __init__(
        self,
        level="info",
        format="%(asctime)s :: %(levelname)s :: %(message)s",
        mail=False,
        **kwargs,
    ):
        self.logging = logging
        self.file = kwargs.get("file")
        self.formatter = format
        self.logging.basicConfig(
            level=LogLevels[level].value, file=self.file, format=format
        ) if self.file else self.logging.basicConfig(
            level=LogLevels[level].value, format=format
        )
        self.mail = mail
        self.mail_handler = None
        if self.mail:
            try:
                self.mailhost = kwargs["mailhost"]
                self.fromaddr = kwargs["fromaddr"]
                self.toaddrs = kwargs["toaddrs"]
                self.mail_handler = self.setup_mail_handler()
            except Exception as e:
                self.mail = False
                self.logging.error(e)

    def set_level(self, logger=None, level="info"):
        logger = logger if logger else self.logging
        logger.setLevel(LogLevels[level].value)

    def set_handler_formater(
        self, handler, logger=None, format="%(asctime)s :: %(levelname)s :: %(message)s"
    ):
        logger = logger if logger else self.logging
        formatter = logger.Formatter(format)
        handler.setFormatter(formatter)

    def set_file_handler(
        self, file, logger=None, format="%(asctime)s :: %(levelname)s :: %(message)s"
    ):
        logger = logger if logger else self.logging
        file_handler = logger.FileHandler(file)
        self.set_handler_formater(file_handler, logger, format)

    @staticmethod
    def configure_flask_logging():
        dictConfig(
            {
                "version": 1,
                "formatters": {
                    "default": {
                        "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                    }
                },
                "handlers": {
                    "wsgi": {
                        "class": "logging.StreamHandler",
                        "stream": "ext://flask.logging.wsgi_errors_stream",
                        "formatter": "default",
                    }
                },
                "root": {"level": "INFO", "handlers": ["wsgi"]},
            }
        )

    def setup_mail_handler(
        self,
        subject="Application Error",
        level="error",
        format=None,
        logger=None,
        **kwargs,
    ):
        logger = logger if logger else self.logging
        if not self.mail:
            self.logging.warning()
            try:
                self.mailhost = kwargs["mailhost"]
                self.fromaddr = kwargs["fromaddr"]
                self.toaddrs = kwargs["toaddrs"]
                self.mail = True
            except Exception as e:
                self.logging.error(e)
                return
        if kwargs.get("override_details"):
            self.mailhost = (
                kwargs.get("mailhost") if kwargs.get("mailhost") else self.mailhost
            )
            self.fromaddr = (
                kwargs.get("fromaddr") if kwargs.get("fromaddr") else self.fromaddr
            )
            self.toaddrs = (
                kwargs.get("toaddrs") if kwargs.get("toaddrs") else self.toaddrs
            )
        mail_handler = SMTPHandler(
            mailhost=self.mailhost,
            fromaddr=self.fromaddr,
            toaddrs=self.toaddrs,
            subject=subject,
        )
        mail_handler.setLevel(level=LogLevels[level].value)
        mail_handler.setFormatter(
            logger.Formatter(self.formatter if not format else format)
        )
        self.add_handler(logger, mail_handler)
        return mail_handler

    def inject_flask_request_handler(self, handler):
        class RequestFormatter(self.logging.Formatter):
            def format(self, record):
                if has_request_context():
                    record.url = request.url
                    record.remote_addr = request.remote_addr
                else:
                    record.url = None
                    record.remote_addr = None
                return super().format(record)

        formatter = RequestFormatter(
            "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
            "%(levelname)s in %(module)s: %(message)s"
        )
        handler.setFormatter(formatter)

    def get_logger(self, name=None):
        return self.logging.getLogger(name)

    def add_handler(self, logger=None, handler=None):
        handler = handler if handler else default_handler
        self.logging.addHandler(handler) if not logger else logger.addHandler(handler)


class BaseHttpException:
    @staticmethod
    def handle_bad_request(e: Exception) -> tuple:
        return "bad request!", 400

    @staticmethod
    def handle_method_not_allowed(e: Exception) -> tuple:
        return "method not allowed! ", 405

    @staticmethod
    def handle_payload_too_large(e: Exception) -> tuple:
        return "payload too large!", 413

    @staticmethod
    def handle_invalid_media(e: Exception) -> tuple:
        return "unsupported media type!", 415

    @staticmethod
    def handle_internal_server_error(e: Exception) -> tuple:
        return "internal server error!", 500


class ValidateFile:
    def __init__(self, file=None, max_lenght=0) -> None:
        self.file = file
        self.max_lenght = max_lenght

    def _isvalid_filetype(self, type_) -> bool:
        try:
            return (
                True
                if (type_ in self.file.content_type or type_ in self.file.mimetype)
                else False
            )
        except AttributeError:
            return True if (type_ in self.file.content_type) else False

    def _isvalid_size(self, content_length=None) -> bool:
        try:
            content_length = (
                content_length if content_length else self.file.content_length
            )
            return True if content_length <= self.max_lenght else False
        except AttributeError:
            content_length = (
                content_length if content_length else self.file.spool_max_size
            )
            return True if content_length <= self.max_lenght else False

    def isvalid(self, type_, content_length=None) -> bool:
        if not self.file:
            return False
        return (
            True
            if (self._isvalid_filetype(type_) and self._isvalid_size(content_length))
            else False
        )

    @staticmethod
    def isvalid_lenght(object: list or dict or str, default_lenght: int) -> bool:
        return True if len(object) <= default_lenght else False


class Helpers:
    @staticmethod
    def generate_uuid(source="dir", **kwargs) -> str:
        """
        Generate Unique Id's Based on thier availability
        from either a local path or cloud bucket
        """
        id = str(uuid.uuid1()).replace("-", "_")
        path = Path(kwargs.get("base_path"), id)
        while os.path.exists(path):
            id = str(uuid.uuid1()).replace("-", "_")
            path = Path(kwargs.get("base_path"), id)
        if source == "cloud":
            prefix = kwargs.pop("prefix")
            bucket = kwargs.pop("cloud")
            while bucket.blob_exists(f"{prefix}/{id}"):
                id = str(uuid.uuid1()).replace("-", "_")
            return id
        elif source == "dir":
            return id

    @staticmethod
    def get_file_size(file):
        """
        Seek to the End of A file
        and back to get the file lenght
        """
        file_length = file.seek(0, os.SEEK_END)
        file.seek(0, os.SEEK_SET)
        return file_length
