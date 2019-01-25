import os
from dotenv import load_dotenv

debug = False
ver = "Development"

class Config:
	if os.environ.get("DOCKER") is None:
		debug = True
		basedir = os.path.abspath(os.path.dirname(__file__))
		load_dotenv(os.path.join(basedir, ".env"))
		# repo = git.Repo(search_parent_directories=True)
		# ver = repo.git.describe()

	DEBUG = debug
	MAX_CONTENT_LENGTH = 32 * 1024 * 1024
	PORT = os.environ.get("PORT") or "8080"
	VERSION = os.environ.get("VERSION") or str(ver)
	# SESSION_TYPE = os.environ.get("SESSION_TYPE") or "filesystem"
	#10 = Debug and 20 = Info
	LOG_LEVEL = os.environ.get("LOG_LEVEL") or "10"
	SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
	UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./uploads")
	DOWNLOAD_FOLDER = os.environ.get("DOWNLOAD_FOLDER", "./downloads")

	# Other Config variables go here
