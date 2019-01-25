import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from flask import Flask, jsonify
import config

app = Flask(__name__)
app.config.from_object(config.Config())
app.logger.setLevel(int(app.config["LOG_LEVEL"]))

def get_http_exception_handler(app):
    """Overrides the default http exception handler to return JSON."""
    handle_http_exception = app.handle_http_exception

    @wraps(handle_http_exception)
    def ret_val(exception):
        exc = handle_http_exception(exception)
        return (
            jsonify(
                {"response": "ERROR", "http_code": exc.code, "message": exc.description}
            ),
            exc.code,
        )

    return ret_val


# Override the HTTP exception handler.
app.handle_http_exception = get_http_exception_handler(app)


@app.errorhandler(500)
def internal_error(exception):
    return (
        jsonify({"response": "ERROR", "http_code": 500, "message": str(exception)}),
        500,
    )
