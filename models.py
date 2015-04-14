from flask.ext.mongoengine import MongoEngine
from imgmining import app
import datetime

app.config["MONGODB_SETTINGS"] = {'DB': "ImageMining"}
app.config["SECRET_KEY"] = "Iwantthistobesecret"

db = MongoEngine(app)
"""
class Regiser_User(db.Document):
    email = db.StringField(required=True)
    alias = db.StringField(required=True)
    reg_date = db.DateTimeField(default=datetime.datetime.now())
    password = db.StringField(required=True)
"""
