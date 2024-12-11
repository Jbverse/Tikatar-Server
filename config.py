from decouple import config


class BaseConfig:
    FLASK_SECRET_KEY = config("FLASK_SECRET_KEY")
    
class DevConfig(BaseConfig):
    DEBUG = config("DEBUG", cast=bool)
    
    
class ProdConfig(BaseConfig):
    pass