from flask import request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, Response
import requests
from datetime import datetime
from time import strptime
from pymongo import MongoClient
from bson.objectid import ObjectId
from imgmining import app
import os
import json
import glob
from uuid import uuid4
from fhl import *
import base64

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

@app.route('/r',methods=['GET','POST'])
def newpage():
    return render_template("res.html")

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


@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    print request.form
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "imgmining/static/uploads/{}".format(upload_key)
    try:
        os.mkdir(target)
    except:
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)

    print "=== Form Data ==="
    for key, value in form.items():
        print key, "=>", value

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print "Accept incoming file:", filename
        print "Save it to:", destination
        upload.save(destination)

    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        if('upform1' in form):
            return redirect(url_for("find_similar_imgs", uuid=upload_key))
        elif('upform2' in form):
            return redirect(url_for("form_img_cluster", uuid=upload_key))
        elif('upload-form3' in form):
            return redirect(url_for("form_img_cluster", uuid=upload_key))

@app.route("/similar_images/<uuid>")
def find_similar_imgs(uuid):
    root = "imgmining/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    img_file = root+'/' + os.listdir(root)[0]
    b_value = ''
    with open(img_file,'rb') as imgfile:
        b_value = base64.b64encode(imgfile.read())
    
    items = query_image(img_file)
    return render_template('res.html',cmp_b64=b_value,items=items)

@app.route("/cluster_images/<uuid>")
def form_img_cluster(uuid):
    root = "imgmining/static/uploads/{}".format(uuid)
    #print root
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    fea , ims = create_features(root)
    res = result(fea,ims)
    
    return render_template('res1.html',cmp_b64=res)


@app.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "imgmining/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = os.listdir(root)
    #for file in glob.glob("{}/*.*".format(root)):
    #    fname = file.split("/")[-1]
    #    files.append(fname)

    print files

    return render_template("files.html",
        uuid=uuid,
        files=files,
    )


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))
