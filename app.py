from flask import Flask
from sqlite_session import SqliteSessionInterface

app = Flask(__name__)
app.config.from_pyfile('aemvl-backend.config')
app.session_interface=SqliteSessionInterface(app.config['SQLITE_SESSION_DIRECTORY'])
