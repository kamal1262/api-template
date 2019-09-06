import logging
import traceback

import jwt.exceptions as jwt_exception
from flask import current_app
from flask_jwt_extended import exceptions as jwt_extended_exception
from flask_jwt_extended import get_jwt_identity
from aws_xray_sdk.core import xray_recorder
from flask_restplus.errors import HTTPException
from ..common.errors import UserNotFoundException


def create_module(api, **kwargs):
    app = kwargs.get("app")
    logger: logging.Logger = current_app.logger

    @api.errorhandler(jwt_extended_exception.NoAuthorizationError)
    def handle_no_authorization_error(e):
        return {"message": str(e)}, 401

    @api.errorhandler(jwt_extended_exception.CSRFError)
    def handle_auth_error(e):
        return {"message": str(e)}, 401

    @api.errorhandler(jwt_exception.ExpiredSignatureError)
    def handle_expired_error(e):
        return {"message": "Token has expired"}, 401

    @api.errorhandler(jwt_extended_exception.InvalidHeaderError)
    def handle_invalid_header_error(e):
        return {"message": str(e)}, 422

    @api.errorhandler(jwt_exception.InvalidTokenError)
    def handle_invalid_token_error(e):
        return {"message": str(e)}, 422

    @api.errorhandler(jwt_extended_exception.JWTDecodeError)
    def handle_jwt_decode_error(e):
        return {"message": str(e)}, 422

    @api.errorhandler(jwt_extended_exception.WrongTokenError)
    def handle_wrong_token_error(e):
        return {"message": str(e)}, 422

    @api.errorhandler(jwt_extended_exception.RevokedTokenError)
    def handle_revoked_token_error(e):
        return {"message": "Token has been revoked"}, 401

    @api.errorhandler(jwt_extended_exception.FreshTokenRequired)
    def handle_fresh_token_required(e):
        return {"message": "Fresh token required"}, 401

    @api.errorhandler(jwt_extended_exception.UserLoadError)
    def handler_user_load_error(e):
        # The identity is already saved before this exception was raised,
        # otherwise a different exception would be raised, which is why we
        # can safely call get_jwt_identity() here
        identity = get_jwt_identity()
        return {"message": "Error loading the user {}".format(identity)}, 401

    @api.errorhandler(jwt_extended_exception.UserClaimsVerificationError)
    def handle_failed_user_claims_verification(e):
        return {"message": "User claims verification failed"}, 400

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
