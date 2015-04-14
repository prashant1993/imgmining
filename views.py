from flask import request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, Response
import requests
from datetime import datetime
from time import strptime
from pymongo import MongoClient
from bson.objectid import ObjectId
from imgmining import app
#from games.models import Regiser_User

@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
def homepage():
    #if(request.method=='POST'):
    #    if 'signin' in request.form:
    #        print 'Trying to sign-in'
    #        print request.form
    #    elif 'Email' in request.form:
    #        print 'Trying to Register'
    #        print request.form
    return render_template("index.html")
"""
@app.route('/spacegame')
def spacegame():
    return render_template("SpaceGame.html")

@app.route('/flipgame')
def flipgame():
    return render_template("Flip Game.html")

@app.route('/floodit')
def floodit():
    return render_template("floodit.html")
"""
