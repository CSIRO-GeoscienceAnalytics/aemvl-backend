from functools import wraps
from flask import Flask, jsonify

app = Flask(__name__)
app.config.from_pyfile('aemvl-backend.config')


def get_http_exception_handler(app):
    """Overrides the default http exception handler to return JSON."""
    handle_http_exception = app.handle_http_exception

    @wraps(handle_http_exception)
    def ret_val(exception):
        exc = handle_http_exception(exception)
        return jsonify({
            'response': 'ERROR',
            'http_code': exc.code,
            'message': exc.description}), exc.code

    return ret_val

# Override the HTTP exception handler.
app.handle_http_exception = get_http_exception_handler(app)
