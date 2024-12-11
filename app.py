from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource
from config import DevConfig

# Initialize the flask app
app = Flask(__name__)

# Load environments
app.config.from_object(DevConfig)

# Enable Cors
CORS(app)

# Initialize Api
api = Api(app)

# Class That represent our CRUD
class BaseAPI(Resource):
    def get(self):
        return {'message': "Tikatar base api"}

# Endpoints
api.add_resource(BaseAPI, '/')

# Running our flask server
if __name__ == '__main__':
    app.run()