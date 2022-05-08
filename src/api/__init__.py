from flask_restx import Api

from src.api.ping import ping_namespace
from src.api.users.views import users_namespace

api = Api(version="1.0", title="Users Api", doc="/doc")


api.add_namespace(ping_namespace, "/ping")
api.add_namespace(users_namespace, "/users")
