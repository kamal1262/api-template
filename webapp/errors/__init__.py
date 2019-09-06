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
        logger.info("sdfsfssdsfds")
        _log_to_segment(e, 404)
        return {"message": str(e)}, 404

    @api.errorhandler(HTTPException)
    def handle_http_exception(e):
        logger.error(e, exc_info=True)
        _log_to_segment(e)
        return {"message": str(e)}, e.code

    @api.errorhandler(Exception)
    @app.errorhandler(Exception)
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        logger.error(e, exc_info=True)
        _log_to_segment(e, 500)
        return {"message": str(e)}, 500

    def _log_to_segment(e, code=None):
        current_segment = xray_recorder.current_segment()
        stack = traceback.extract_stack(limit=10)
        current_segment.add_exception(Exception(str(e)), stack)
        status_code = e.code if not code else code
        current_segment.apply_status_code(status_code)
