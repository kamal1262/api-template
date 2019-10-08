import logging
import traceback

from aws_xray_sdk.core import xray_recorder
from flask import current_app
from flask_restplus.errors import HTTPException

from ..common.errors import UserNotFoundException


def create_module(api, **kwargs):
    app = kwargs.get("app")
    logger: logging.Logger = current_app.logger

    @api.errorhandler(UserNotFoundException)
    def handle_user_not_found(e):
        logger.error(e, exc_info=True)
        _log_to_segment(e, 404)
        return {"message": str(e)}, 404

    @api.errorhandler(HTTPException)
    @app.errorhandler(Exception)
    def handle_http_exception(e):
        logger.error(e, exc_info=True)
        _log_to_segment(e, e.code)
        return {"message": str(e)}, e.code

    def _log_to_segment(e, code=None):
        current_segment = xray_recorder.current_segment()
        stack = traceback.extract_stack(limit=10)
        current_segment.add_exception(Exception(str(e)), stack)
        status_code = e.code if not code else code
        current_segment.apply_status_code(status_code)
