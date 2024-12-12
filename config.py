import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class BaseConfig:
    FLASK_SECRET_KEY = config("FLASK_SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = config("SQLALCHEMY_TRACK_MODIFICATIONS", cast=bool)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1000 * 1000
    
class DevConfig(BaseConfig):
    DEBUG = config("DEBUG", cast=bool)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, 'dev.db')}'
    SQLALCHEMY_ECHO=True
    
    
class ProdConfig(BaseConfig):
    pass