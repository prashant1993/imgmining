from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)

import imgmining.views
