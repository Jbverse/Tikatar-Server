from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource, marshal_with, fields
from config import DevConfig
from database import db
# import models class to create the tables below
# from models import User

# Initialize the flask app
app = Flask(__name__)

# Load environments
app.config.from_object(DevConfig)

# Initialize database
db.init_app(app)

# Enable Cors
CORS(app)

# Initialize Api
api = Api(app)


# This one will create the tables in the databaes but first you must import the models class
# to this files in order for sqlalchemy to know about theme
with app.app_context():
    db.create_all()

# Class That represent our CRUD
class BaseAPI(Resource):
    def get(self):
        return {'message': "Tikatar base api"}

# Example of User endpoint with simple get request it will create a user in databse with the name User
# class UserEndpoint(Resource):
#     #the marshal_with lets us return an instance with the fields that we want to return without serializing  
#     @marshal_with({"id": fields.Integer, "username": fields.String})
#     def get(self):
#         user = User()
#         user.set_username("User")
#         db.session.add(user)
#         db.session.commit()
#         return user
        
# Endpoints
api.add_resource(BaseAPI, '/')
# api.add_resource(UserEndpoint, '/users')

# Running our flask server
if __name__ == '__main__':
    app.run()